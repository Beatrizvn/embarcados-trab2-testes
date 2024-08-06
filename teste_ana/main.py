from comunicacao.uart import Uart
from comunicacao.modbus import getCodigo_E2, getCodigo_E1
from controle.motor import Motor
from controle.pid import PID
from controle.sensor import Sensor
from controle.elevador import Elevador
from i2c.bmp280_device import bmp280_device
from i2c.oled_display import OLED
import time
import struct
import threading
import traceback
import os


# Configurações iniciais
elevadores = {}
pid_controllers = {}
motores = {}
sensors = {}
bmp280_devices = {}
running = True
elevador_movendo = {}

def initialize_system():
    """Inicializa os componentes do sistema."""
    global elevadores, pid_controllers, motores, sensors, bmp280_devices, elevador_movendo

    for i in range(1, 3):
        motores[i] = Motor(i)
        sensors[i] = Sensor(i)
        elevadores[i] = Elevador(i)
        pid_controllers[i] = PID()
        bmp280_devices[i] = BMP280Device()

    uart = Uart()
    display_oled = OLEDDisplay()
    uart_lock = threading.Lock()

    return uart, display_oled, uart_lock

def main():
    try:
        uart, display_oled, uart_lock = initialize_system()
        start_sensor_threads()
        calibrate_elevadores()
        start_alarms()
    except Exception as e:
        print(traceback.format_exc())
        print('Erro:', e)
        shutdown_system()
    except KeyboardInterrupt:
        shutdown_system()

def start_sensor_threads():
    """Inicia os threads dos sensores."""
    for i in range(1, 3):
        sensors[i].start()

def calibrate_elevadores():
    """Calibra os elevadores e define as posições de referência."""
    global elevador_movendo

    elevador_movendo = {1: False, 2: False}
    for i in range(1, 3):
        elevadores[i].posicoes = calibracao(elevadores[i], motores[i], sensors[i], pid_controllers[i])

def start_alarms():
    """Inicia os alarmes para receber os registradores dos elevadores e atualizar o display."""
    set_alarm_display()
    start_alarm_recebeRegistradorElevador(1)
    start_alarm_recebeRegistradorElevador(2)

def start_alarm_recebeRegistradorElevador(elevador_id):
    """Inicia o alarme para o registrador do elevador específico."""
    if running:
        threading.Timer(0.5, lambda: recebeRegistradorElevador(elevador_id)).start()

def set_alarm_display():
    """Inicia o alarme para atualizar o display OLED."""
    if running:
        threading.Timer(0.1, display_status).start()

def recebeRegistradorElevador(elevador_id):
    """Recebe e processa o registrador do elevador especificado."""
    global elevador_movendo
    try:
        elevador = elevadores[elevador_id]
        elevador.setRegistrador(comando('le_registrador', elevador=elevador))
        elevador.trataRegistrador()
        
        if 'emergency' in elevador.getFila():
            botaoEmergencia()
        elif not elevador_movendo[elevador_id] and elevador.getFila():
            andar = elevador.getFila()[0]
            move_thread = threading.Thread(target=moveElevador, args=(elevador_id, andar))
            move_thread.start()
    except Exception as e:
        print(f"Exception in recebeRegistradorElevador{elevador_id}: {e}")

    if running:
        start_alarm_recebeRegistradorElevador(elevador_id)

def moveElevador(elevador_id, andar):
    """Move o elevador para o andar especificado."""
    global elevador_movendo
    elevador_movendo[elevador_id] = True
    elevador = elevadores[elevador_id]
    motor = motores[elevador_id]
    pid = pid_controllers[elevador_id]
    pos_atual = comando('solicita_encoder', elevador=elevador)
    referencia = elevador.posicoes[andar]
    
    motor.setStatus('Descendo' if pos_atual > referencia else 'Subindo')
    pid.atualiza_referencia(referencia)
    print(f'Elevador {elevador.id} indo para {andar}')
    
    while running:
        saida = comando('solicita_encoder', elevador=elevador)
        potencia = pid.controle(saida)
        motor.moveMotor(potencia)
        comando('sinal_PWM', int(abs(potencia)), elevador=elevador)
        
        if abs(saida - referencia) <= 3:
            break
        
        time.sleep(0.2)
    
    if running:
        motor.setStatus('Parado')
        motor.moveMotor(0)
        desligaBotao(andar, elevador)
        elevador.removeFila()
        print('Porta aberta')
        contagemPorta()  # Aguarda 3 segundos para fechar a porta
        elevador_movendo[elevador_id] = False

def desligaBotao(andar, elevador):
    """Desliga o botão correspondente ao andar especificado."""
    botoes = elevador.getAndarBotao()[andar]
    print("botoes: ", botoes)
    for botao in botoes:
        comando('escreve_registrador', botao=botao, elevador=elevador)

def comando(mensagem, valor=0, botao=None, elevador=None):
    """Envia comandos para o dispositivo especificado via UART."""
    if running:
        with uart_lock:
            if mensagem == 'solicita_encoder':
                cmd = getCodigo_E1(mensagem) if elevador.id == 1 else getCodigo_E2(mensagem)
                uart.escreverEncoder(cmd, len(cmd))
                response = uart.lerEncoder()
                if len(response) != 4:
                    print(f'Erro: Esperava 4 bytes, mas recebeu {len(response)} bytes.')
                    return None
                return struct.unpack('i', response.encode('utf-8'))[0]

            elif mensagem in ['sinal_PWM', 'temperatura']:
                cmd = getCodigo_E1(mensagem, valor) if elevador.id == 1 else getCodigo_E2(mensagem, valor)
                uart.escreverEncoder(cmd, len(cmd), skip_resp=True)

            elif mensagem == 'le_registrador':
                cmd = getCodigo_E1(mensagem) if elevador.id == 1 else getCodigo_E2(mensagem)
                uart.escreverEncoder(cmd, len(cmd))
                return uart.lerEncoder(15, True).encode('utf-8')

            elif mensagem == 'escreve_registrador':
                cmd = getCodigo_E1(mensagem, valor, botao) if elevador.id == 1 else getCodigo_E2(mensagem, valor, botao)
                uart.escreverEncoder(cmd, len(cmd))
                uart.lerEncoder(5, True)

def display_status():
    """Atualiza o status exibido no display OLED."""
    global running
    if running:
        display_oled.clear()
        try:
            temperaturas = [bmp280_devices[i].get_temp() for i in range(1, 3)]
        except:
            temperaturas = [None, None]

        for i in range(1, 3):
            elevador = elevadores[i]
            motor_status = motores[i].getStatus()
            fila_andar = elevador.getFila()
            andar = fila_andar[0].replace('S', 'A') if fila_andar else ''
            display_oled.display_string(f'Elevador {i}: {motor_status}{": " + andar if andar else ""}', 2 * (i - 1))

        if all(temp is not None for temp in temperaturas):
            for i, temp in enumerate(temperaturas, 1):
                display_oled.display_string(f'Temp {i}: {temp:.2f} C', 4 + 2 * (i - 1))
                comando('temperatura', temp, elevador=elevadores[i])
        
        if running:
            set_alarm_display()

def calibracao(elevador, motor, sensor, pid):
    """Calibra o elevador e retorna as posições de referência."""
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
        motor.moveMotor(-5)
    else:
        motor.moveMotor(-100)
        while resp is not None and resp > 0:
             resp = comando('solicita_encoder', elevador=elevador)
        motor.moveMotor(0)
        time.sleep(1)
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
                
            if resp_list:
                pos_media = int(sum(resp_list) / len(resp_list))
                pos[andar_detectado] = pos_media
                print(f'Andar {andar_detectado}: {pos_media}')
    
    print(']\nCalibração finalizada\n')
    motor.moveMotor(0)
    return pos

def botaoEmergencia():
    """Maneja a emergência."""
    print('Emergência acionada!')

def contagemPorta():
    """Gerencia a contagem de tempo da porta aberta."""
    print('Porta aberta por 3 segundos...')
    time.sleep(3)
    print('Porta fechada')

def shutdown_system():
    """Encerra o sistema de forma segura."""
    global running
    running = False
    for i in range(1, 3):
        sensors[i].stop()
    display_oled.clear()
    print('Sistema encerrado')

if __name__ == '__main__':
    main()
