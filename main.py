from comunicacao.Uart import Uart
from comunicacao.CodigoModbus import getCodigo_E1, getCodigo_E2
from modelo.Motor import Motor
from modelo.Pid import PID
from modelo.Sensor import Sensor
from modelo.Elevador import Elevador
from i2c.Bmp280 import bmp280_device
# from i2c.OLED import OLED
import time
import struct
import threading
import traceback
import os

# Instâncias para o primeiro elevador
motor1 = Motor(1)
sensor1 = Sensor(1)
elevador1 = Elevador(1)
pid1 = PID()

# Instâncias para o segundo elevador
motor2 = Motor(2)
sensor2 = Sensor(2)
elevador2 = Elevador(2)
pid2 = PID()

# Instâncias comuns
uart = Uart()
bmp280_1 = bmp280_device()
bmp280_2 = bmp280_device()
# display_oled = OLED()
uart_lock = threading.Lock()

running = True
elevador1_movendo = False
elevador2_movendo = False

andares = ['ST', 'S1', 'S2', 'S3']

def main():
    try:
        # Start sensor threads (assuming sensor1 and sensor2 are already defined and have a start method)
        sensor1.start()
        sensor2.start()
        
        global elevador1_pos, elevador2_pos

        elevador1_pos = {'ST': 1800, 'S1': 5000, 'S2': 13000, 'S3': 19000}
        elevador2_pos = {'ST': 1800, 'S1': 5000, 'S2': 13000, 'S3': 19000}

        set_alarm_display()
        start_alarm_recebeRegistradorElevador1()
        start_alarm_recebeRegistradorElevador2()

    except Exception as e:
        print(traceback.format_exc())
        print('Erro:', e)
        fechar()
    except KeyboardInterrupt:
        fechar()

def start_alarm_recebeRegistradorElevador1():
    if running:
        threading.Timer(0.5, recebeRegistradorElevador1).start()

def set_alarm_display():
    if running:
        threading.Timer(0.1, displayStatus).start()

def start_alarm_recebeRegistradorElevador2():
    if running:
        threading.Timer(0.5, recebeRegistradorElevador2).start()

def recebeRegistradorElevador1() -> None:
    global running, elevador1_movendo
    try:
        elevador1.setRegistrador(comando('le_registrador', elevador=elevador1))
        elevador1.trataRegistrador()
        
        if 'emergency' in elevador1.getFila():
            botaoEmergencia()
        elif not elevador1_movendo and len(elevador1.getFila()) != 0:
            andar = elevador1.getFila()[0]
            moveElevador_thread = threading.Thread(target=moveElevador1, args=(andar,))
            moveElevador_thread.start()
    except Exception as e:
        print(f"Exception in recebeRegistradorElevador1: {e}")
    
    # Schedule the next call
    if running:
        start_alarm_recebeRegistradorElevador1()


def recebeRegistradorElevador2() -> None:
    global running, elevador2_movendo
    try:
        elevador2.setRegistrador(comando('le_registrador', elevador=elevador2))
        elevador2.trataRegistrador()
        
        if 'emergency' in elevador2.getFila():
            botaoEmergencia()
        elif not elevador2_movendo and len(elevador2.getFila()) != 0:
            andar = elevador2.getFila()[0]
            moveElevador_thread = threading.Thread(target=moveElevador2, args=(andar,))
            moveElevador_thread.start()
    except Exception as e:
        print(f"Exception in recebeRegistradorelevador2: {e}")
    
    # Schedule the next call
    if running:
        start_alarm_recebeRegistradorElevador1()

def move_elevador(elevador, motor, pid, posicoes, andar):
    """Move o elevador para o andar desejado usando controle PID."""
    global running
    elevador_movendo = True
    pos_atual = comando('solicita_encoder', elevador=elevador)
    
    # Define a direção do movimento do motor
    if pos_atual - posicoes[andar] > 0:
        motor.setStatus('Descendo')
    elif pos_atual - posicoes[andar] < 0:
        motor.setStatus('Subindo')
    
    referencia = posicoes[andar]
    print(f'Referência: {referencia}')
    
    pid.atualiza_referencia(referencia)
    print(f'Elevador {elevador.id} indo para {andar}')
    
    # Controla o motor até atingir a posição desejada
    controle_motor(motor, pid, elevador, referencia)

    if running:
        motor.setStatus('Parado')
        motor.moveMotor(0)
        desligaBotao(andar, elevador)
        elevador.removeFila()
        print('Porta aberta')
        contagemPorta() 
        elevador_movendo = False

def controle_motor(motor, pid, elevador, referencia):
    """Controle do motor usando o PID para alcançar a posição desejada."""
    diff_posicao = 500
    while diff_posicao > 3 and running:
        saida = comando('solicita_encoder', elevador=elevador)
        potencia = pid.controle(saida)
        motor.moveMotor(potencia)
        comando('sinal_PWM', int(abs(potencia)), elevador=elevador)
        diff_posicao = abs(saida - referencia)
        time.sleep(0.2)

def moveElevador1(andar):
    """Move o elevador 1 para o andar desejado."""
    move_elevador(elevador1, motor1, pid1, elevador1_pos, andar)

def moveElevador2(andar):
    """Move o elevador 2 para o andar desejado."""
    move_elevador(elevador2, motor2, pid2, elevador2_pos, andar)


def desligaBotao(andar, elevador):
    botoes = elevador.getAndarBotao()[andar]
    print("botoes: ", botoes)
    for botao in botoes:
        comando('escreve_registrador', botao=botao, elevador=elevador)

def comando(mensagem, valor=0, botao=None, elevador=None):
    if running:
        if mensagem == 'solicita_encoder':
            with uart_lock:
                cmd = getCodigo_E1(mensagem) if elevador.id == 1 else getCodigo_E2(mensagem)
                uart.escreverEncoder(cmd, len(cmd))
                response = uart.lerEncoder()
                
                if isinstance(response, str):
                    response = response.encode('utf-8')
                
                if len(response) != 4:
                    print(f'Erro: Esperava 4 bytes, mas recebeu {len(response)} bytes.')
                    return None
                
                response = struct.unpack('i', response)[0]
                return response  

        elif mensagem == 'sinal_PWM' or mensagem == 'temperatura':
            with uart_lock:
                cmd = getCodigo_E1(mensagem, valor) if elevador.id == 1 else getCodigo_E2(mensagem, valor)
                uart.escreverEncoder(cmd, len(cmd), skip_resp=True)

        elif mensagem == 'le_registrador':
            with uart_lock:
                cmd = getCodigo_E1(mensagem) if elevador.id == 1 else getCodigo_E2(mensagem)
                uart.escreverEncoder(cmd, len(cmd))
                response = uart.lerEncoder(15, True)
                if isinstance(response, str):
                    response = response.encode('utf-8')
                
                return response
                
        elif mensagem == 'escreve_registrador':
            with uart_lock:
                cmd = getCodigo_E1(mensagem, valor, botao) if elevador.id == 1 else getCodigo_E2(mensagem, valor, botao)
                uart.escreverEncoder(cmd, len(cmd))
                uart.lerEncoder(5, True)
        
def calibracao(elevador, motor, sensor, pid):
    andares = ['ST', 'S1', 'S2', 'S3']
    print(f'Calibrando elevador {elevador.id}')
    motor.setStatus('Calibrando...')
    pos = {}
    posicao_inicial = obter_posicao_encoder(elevador, motor)
    
    if posicao_inicial is None:
        print("Erro: Não foi possível obter a posição do encoder.")
        motor.moveMotor(0)
        return pos

    pid.atualiza_referencia(25000)
    mover_motor_ate_posicao(motor, posicao_inicial, 25000, elevador)

    print('Procurando posições...')
    pos = obter_posicoes_sensor(sensor, elevador, andares)

    print(']\nCalibração finalizada\n')
    motor.moveMotor(0)
    return pos

def obter_posicao_encoder(elevador, motor):
    """Obtém a posição atual do encoder e ajusta o motor para a posição desejada."""
    resp = comando('solicita_encoder', elevador=elevador)
    if resp is not None:
        return resp
    return None

def mover_motor_ate_posicao(motor, posicao_atual, posicao_desejada, elevador):
    """Move o motor até a posição desejada e ajusta a direção conforme necessário."""
    if posicao_desejada - posicao_atual < posicao_atual:
        motor.moveMotor(100)
        while posicao_atual < posicao_desejada:
            posicao_atual = comando('solicita_encoder', elevador=elevador)
        motor.moveMotor(0)
        time.sleep(1)
        print('Descendo...')
        motor.moveMotor(-5)
    else:
        motor.moveMotor(-100)
        while posicao_atual > 0:
            posicao_atual = comando('solicita_encoder', elevador=elevador)
        motor.moveMotor(0)
        time.sleep(1)
        print('Subindo...')
        motor.moveMotor(5)

def obter_posicoes_sensor(sensor, elevador, andares):
    """Obtém as posições dos andares detectados pelo sensor."""
    pos = {}
    print('[')
    while not all(key in pos for key in andares):
        andar_detectado = sensor.active_sensor
        if andar_detectado in andares and andar_detectado not in pos:
            resp_list = []
            while sensor.active_sensor == andar_detectado:
                resp = comando('solicita_encoder', elevador=elevador)
                if resp is not None:
                    resp_list.append(resp)

            if resp_list:
                pos_media = int(sum(resp_list) / len(resp_list))
                pos[andar_detectado] = pos_media
                print(f'Andar {andar_detectado}: {pos_media}')
    return pos

def displayStatus():
    global running
    andar1 = andar2 = -1
    if running:
        try:
            temperatura1 = bmp280_1.get_temp()
            temperatura2 = bmp280_2.get_temp()
        except:
            temperatura1 = None
            temperatura2 = None

        if len(elevador1.getFila()) != 0:
            andar1 = elevador1.getFila()[0]
            andar1 = andar1.replace('S', 'A')
        
        if len(elevador2.getFila()) != 0:
            andar2 = elevador2.getFila()[0]
            andar2 = andar2.replace('S', 'A')
        if temperatura1 is not None and temperatura2 is not None:
            comando('temperatura', temperatura1, elevador=elevador1)
            comando('temperatura', temperatura2, elevador=elevador2)
        
        if running:
            set_alarm_display()

def botaoEmergencia():
    print('Emergência acionada!')

def contagemPorta():
    print('Porta aberta (3 segundos)')
    time.sleep(3)
    print('Porta fechada')

def fechar():
    global running
    running = False
    sensor1.stop()
    sensor2.stop()
    print('Encerrado')

if __name__ == '__main__':
    main()