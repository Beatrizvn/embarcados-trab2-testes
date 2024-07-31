from comunicacao.Uart import Uart
from comunicacao.CodigoModbus import getCodigo
from modelo.Motor import Motor
from modelo.Pid import PID
from modelo.Sensor import Sensor
from modelo.Elevador import Elevador
from i2c.Bmp280 import bmp280_device
from i2c.Oled import oled_display
import time
import struct
import threading

# Instanciação dos objetos
motor = Motor()
sensor = Sensor()
uart = Uart()
pid = PID()
bmp280 = bmp280_device()
display_oled = oled_display()  # Usando display OLED SSD1306
elevador = Elevador()

# Variáveis Globais
uart_lock = threading.Lock()  # Lock para garantir segurança em operações UART
running = True  # Indica se o sistema está em execução
elevador_movendo = False  # Indica se o elevador está se movendo
andares = ['ST', 'S1', 'S2', 'S3']  # Lista de andares
elevador_pos = {}  # Dicionário para armazenar as posições dos andares

def main():
    """
    Função principal que inicializa o sensor, executa a calibração e inicia a leitura dos registradores.
    """
    try:
        sensor.start()
        threading.Thread(target=displayStatus).start()  # Inicia a thread para atualizar o display
        global elevador_pos
        elevador_pos = calibracao()
        recebeRegistrador()
    except Exception as e:
        print(f'Erro: {e}')
        encerra()
    except KeyboardInterrupt:
        encerra()

def recebeRegistrador():
    """
    Função para ler os registradores continuamente e tratar comandos do elevador.
    """
    global running
    while running:
        elevador.setRegistrador(comando('le_registrador'))  # Lê os registradores do elevador
        elevador.trataRegistrador()
        
        if 'emergency' in elevador.getFila():
            botaoEmergencia()
        elif elevador.getFila() and not elevador_movendo:
            andar = elevador.getFila()[0]
            threading.Thread(target=moveElevador, args=(andar,)).start()
        time.sleep(0.05)

def moveElevador(andar):
    """
    Função para mover o elevador até o andar especificado.
    """
    global elevador_movendo
    elevador_movendo = True
    pos_atual = comando('solicita_encoder')

    if pos_atual - elevador_pos[andar] > 0:
        motor.setStatus('Descendo')
    elif pos_atual - elevador_pos[andar] < 0:
        motor.setStatus('Subindo')

    referencia = elevador_pos[andar]
    pid.atualiza_referencia(referencia)
    print(f'Indo para {andar}')

    while abs(pos_atual - referencia) > 3 and running:
        pos_atual = comando('solicita_encoder')
        potencia = pid.controle(pos_atual)
        motor.moveMotor(potencia)
        comando('sinal_PWM', int(abs(potencia)))
        time.sleep(0.2)

    if running:
        motor.setStatus('Parado')
        motor.moveMotor(0)
        desligaBotao(andar)
        elevador.removeFila()
        print('Porta aberta')
        contagemPorta()  # Aguarda 3 segundos para fechar a porta
        elevador_movendo = False

def desligaBotao(andar):
    """
    Função para desligar o botão do andar especificado.
    """
    for botao in elevador.getAndarBotao()[andar]:
        comando('escreve_registrador', botao=botao)

def comando(mensagem, valor=0, botao=None):
    """
    Função para enviar comandos UART e ler respostas.
    """
    if not running:
        return
    with uart_lock:
        cmd = getCodigo(mensagem, valor, botao)
        uart.escreverEncoder(cmd, len(cmd))
        
        if mensagem in ['solicita_encoder', 'le_registrador']:
            response = uart.lerEncoder(15, True) if mensagem == 'le_registrador' else uart.lerEncoder()
            return struct.unpack('i', response)[0] if mensagem == 'solicita_encoder' else response

def displayStatus():
    """
    Função para atualizar o display OLED com a temperatura e status do elevador.
    """
    global running
    print('Display iniciado...')
    
    while running:
        display_oled.clear()  # Limpa o display
        try:
            temperatura = bmp280.get_temp()
        except:
            temperatura = 'N/A'

        if elevador.getFila():
            andar = elevador.getFila()[0].replace('S', 'A')
            display_oled.display(f'{motor.getStatus()}: {andar}', 1)
        display_oled.display(f'Temp: {temperatura} C', 0)

        comando('temperatura', temperatura)
        time.sleep(1)

    display_oled.clear()  # Limpa o display ao finalizar

def calibracao():
    """
    Função para calibrar o elevador encontrando as posições dos andares.
    """
    print('Calibrando...')
    motor.setStatus('Calibrando...')
    pos = {}
    resp = comando('solicita_encoder')  # Solicita a posição atual do encoder
    pid.atualiza_referencia(25000)

    motor.moveMotor(100 if 25000 - resp < resp else -100)
    while (resp < 25000 if 25000 - resp < resp else resp > 0):
        resp = comando('solicita_encoder')
    motor.moveMotor(0)
    time.sleep(1)

    motor.moveMotor(-5 if 25000 - resp < resp else 5)
    print('Procurando posições...')
    
    while not all(key in pos for key in andares):
        andar_detectado = sensor.active_sensor
        if andar_detectado in andares and andar_detectado not in pos:
            resp_list = []
            while sensor.active_sensor == andar_detectado:
                resp_list.append(comando('solicita_encoder'))
            pos[andar_detectado] = sum(resp_list) // len(resp_list) if resp_list else 0
            print(f'Andar {andar_detectado}: {pos[andar_detectado]}')

    motor.moveMotor(0)
    print('Calibração finalizada')
    return pos

def botaoEmergencia():
    """
    Função para tratar o acionamento do botão de emergência.
    """
    print('Botão de emergência pressionado')
    for andar in andares:
        desligaBotao(andar)
    encerra()

def contagemPorta():
    """
    Função para realizar a contagem regressiva de 3 segundos para fechar a porta.
    """
    for i in range(3, 0, -1):
        print(i, end=' ', flush=True)
        time.sleep(1)
    print('Porta fechada')

def encerra():
    """
    Função para encerrar o sistema.
    """
    global running
    running = False
    uart.desconectar()
    motor.moveMotor(0)
    sensor.stop()
    sensor.join()

if __name__ == "__main__":
    main()
