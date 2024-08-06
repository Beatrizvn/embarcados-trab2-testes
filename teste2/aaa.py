from comunicacao.UART import Uart
from comunicacao.ModBus import codigo_E1, codigo_E2
from controle.motor import Motor
from controle.pid import PID 
from controle.sensor import Sensor
from controle.elevador import Elevador
from I2C.bmp280 import bmp280_device
from I2C.OLED import OLED
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
display_oled = OLED()
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
        
        # Start display status thread
        # displayStatus_thread = threading.Thread(target=displayStatus)
        # displayStatus_thread.start()
        
        global elevador1_pos, elevador2_pos
        # elevador1_pos = calibracao(elevador1, motor1, sensor1, pid1)
        # elevador2_pos = calibracao(elevador2, motor2, sensor2, pid2)
        elevador1_pos = {'ST': 1800, 'S1': 5000, 'S2': 13000, 'S3': 19000}
        elevador2_pos = {'ST': 1800, 'S1': 5000, 'S2': 13000, 'S3': 19000}

        # Start the alarm for recebeRegistradorElevador1 and recebeRegistradorElevador2
        set_alarm_display()
        start_alarm_recebeRegistradorElevador1()
        start_alarm_recebeRegistradorElevador2()

    except Exception as e:
        print(traceback.format_exc())
        print('Erro:', e)
        encerra()
    except KeyboardInterrupt:
        encerra()

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
        start_alarm_recebeRegistradorElevador2()

def moveElevador1(andar):
    global running, elevador1_movendo
    elevador1_movendo = True
    pos_atual = comando('solicita_encoder', elevador=elevador1)
    if pos_atual - elevador1_pos[andar] > 0:
        motor1.setStatus('Descendo')
    elif pos_atual - elevador1_pos[andar] < 0:
        motor1.setStatus('Subindo')
    
    referencia = elevador1_pos[andar]
    print("referencia", referencia)
    pid1.atualiza_referencia(referencia)
    print(f'Elevador {elevador1.id} indo para {andar}')
    potencia = pid1.controle(comando('solicita_encoder', elevador=elevador1))
    diff_posicao = 500
    while diff_posicao > 3 and running:
        saida = comando('solicita_encoder', elevador=elevador1)
        potencia = pid1.controle(saida)
        motor1.moveMotor(potencia)
        comando('sinal_PWM', int(abs(potencia)), elevador=elevador1)
        diff_posicao = abs(saida - referencia)
        time.sleep(0.2)
    if running:
        motor1.setStatus('Parado')
        motor1.moveMotor(0)
        desligaBotao(andar, elevador1)
        elevador1.removeFila()
        print('Porta aberta')
        contagemPorta()  # aguarda 3 segundos para fechar a porta
        elevador1_movendo = False

def moveElevador2(andar):
    global running, elevador2_movendo
    elevador2_movendo = True
    pos_atual = comando('solicita_encoder', elevador=elevador2)
    if pos_atual - elevador2_pos[andar] > 0:
        motor2.setStatus('Descendo')
    elif pos_atual - elevador2_pos[andar] < 0:
        motor2.setStatus('Subindo')
    
    referencia = elevador2_pos[andar]
    pid2.atualiza_referencia(referencia)
    print(f'Elevador {elevador2.id} indo para {andar}')
    potencia = pid2.controle(comando('solicita_encoder', elevador=elevador2))
    diff_posicao = 500
    while diff_posicao > 3 and running:
        saida = comando('solicita_encoder', elevador=elevador2)
        potencia = pid2.controle(saida)
        motor2.moveMotor(potencia)
        comando('sinal_PWM', int(abs(potencia)), elevador=elevador2)
        diff_posicao = abs(saida - referencia)
        # time.sleep(0.2)
    if running:
        motor2.setStatus('Parado')
        motor2.moveMotor(0)
        desligaBotao(andar, elevador2)
        elevador2.removeFila()
        print('Porta aberta')
        contagemPorta()  # aguarda 3 segundos para fechar a porta
        elevador2_movendo = False

def desligaBotao(andar, elevador):
    botoes = elevador.getAndarBotao()[andar]
    print("botoes: ", botoes)
    for botao in botoes:
        comando('escreve_registrador', botao=botao, elevador=elevador)

def comando(mensagem, valor=0, botao=None, elevador=None):
    if running:
        if mensagem == 'solicita_encoder':
            with uart_lock:
                cmd = codigo_E1(mensagem) if elevador.id == 1 else codigo_E2(mensagem)
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
                cmd = codigo_E1(mensagem, valor) if elevador.id == 1 else codigo_E2(mensagem, valor)
                uart.escreverEncoder(cmd, len(cmd), skip_resp=True)
                # uart.lerEncoder(5)

        # elif mensagem == 'temperatura':
        #     with uart_lock:
        #         cmd = codigo_E1(mensagem, valor) if elevador.id == 1 else codigo_E2(mensagem, valor)
        #         uart.escreverEncoder(cmd, len(cmd))
        #         uart.lerEncoder(5)
                
        elif mensagem == 'le_registrador':
            with uart_lock:
                cmd = codigo_E1(mensagem) if elevador.id == 1 else codigo_E2(mensagem)
                uart.escreverEncoder(cmd, len(cmd))
                response = uart.lerEncoder(15, True)
                # print(response)
                if isinstance(response, str):
                    response = response.encode('utf-8')
                
                return response
                
        elif mensagem == 'escreve_registrador':
            with uart_lock:
                cmd = codigo_E1(mensagem, valor, botao) if elevador.id == 1 else codigo_E2(mensagem, valor, botao)
                uart.escreverEncoder(cmd, len(cmd))
                uart.lerEncoder(5, True)

def displayStatus():
    global running
    # print('display iniciado...')
    display_oled.clear()
    andar1 = andar2 = -1
    if running:
        display_oled.clear()
        try:
            temperatura1 = bmp280_1.get_temp()
            temperatura2 = bmp280_2.get_temp()
        except:
            temperatura1 = None
            temperatura2 = None

        if len(elevador1.getFila()) != 0:
            andar1 = elevador1.getFila()[0]
            andar1 = andar1.replace('S', 'A')
            display_oled.display_string(f'Elevador 1: {motor1.getStatus()}: {andar1}', 0)
        else:
            display_oled.display_string(f'Elevador 1: {motor1.getStatus()}', 0)
        
        if len(elevador2.getFila()) != 0:
            andar2 = elevador2.getFila()[0]
            andar2 = andar2.replace('S', 'A')
            display_oled.display_string(f'Elevador 2: {motor2.getStatus()}: {andar2}', 2)
        else:
            display_oled.display_string(f'Elevador 2: {motor2.getStatus()}', 2)

        if temperatura1 is not None and temperatura2 is not None:
            display_oled.display_string(f'Temp 1: {temperatura1:.2f} C', 4)
            display_oled.display_string(f'Temp 2: {temperatura2:.2f} C', 6)

            comando('temperatura', temperatura1, elevador=elevador1)
            comando('temperatura', temperatura2, elevador=elevador2)
        
        # time.sleep(1)

        if running:
            set_alarm_display()
        
    display_oled.clear()

def calibracao(elevador, motor, sensor, pid):
    andares = ['ST', 'S1', 'S2', 'S3']
    print(f'Calibrando elevador {elevador.id}')
    motor.setStatus('Calibrando...')
    pos = {}
    resp = comando('solicita_encoder', elevador=elevador)
    
    if resp is None:
        print("Erro: Não foi possível obter a posição do encoder.")
        motor.moveMotor(0)
        return pos
    
    pid.atualiza_referencia(25000)
    
    if 25000 - resp < resp:
        motor.moveMotor(100)
        while resp is not None and resp < 25000:
            resp = comando('solicita_encoder', elevador=elevador)
        motor.moveMotor(0)
        time.sleep(1)
        print('descendo...')
        motor.moveMotor(-5)
    else:
        motor.moveMotor(-100)
        while resp is not None and resp > 0:
            resp = comando('solicita_encoder', elevador=elevador)
        motor.moveMotor(0)
        time.sleep(1)
        print('subindo...')
        motor.moveMotor(5)
    
    print('Procurando posições...')
    print('[')
    
    while not all(key in pos for key in andares):
        andar_detectado = sensor.active_sensor
        if andar_detectado in andares and andar_detectado not in pos:
            resp_list = []
            while sensor.active_sensor == andar_detectado:
                resp = comando('solicita_encoder', elevador=elevador)
                if resp is not None:
                    resp_list.append(resp)
                
            if len(resp_list) != 0:
                pos_media = int(sum(resp_list) / len(resp_list))
                pos[andar_detectado] = pos_media
                print(f'Andar {andar_detectado}: {pos_media}')
    
    print(']\nCalibração finalizada\n')
    motor.moveMotor(0)
    return pos


def botaoEmergencia():
    print('Emergência acionada!')

def contagemPorta():
    print('Porta aberta por 3 segundos...')
    time.sleep(3)
    print('Porta fechada')

def encerra():
    global running
    running = False
    sensor1.stop()
    sensor2.stop()
    display_oled.clear()
    print('Sistema encerrado')

if __name__ == '__main__':
    main()