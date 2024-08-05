import serial
import threading
import time

from .CRC16 import calcula_crc

class Uart:
    def __init__(self):
        self.serial = serial.Serial(
            port="/dev/serial0", 
            baudrate=115200, 
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0.5
        )
        if self.serial is not None:
            print("UART Inicializada")
        self.connected = False

    def conectar(self) -> None:
        if not self.serial.is_open:
            self.serial.open()
            self.connected = True
            # print('Abrindo a UART')

    def desconectar(self) -> None:
        if self.serial.is_open:
            self.serial.close()
            self.connected = False
            # print('Fechando a UART')

    def validate_crc(self, buffer, buffer_size):
        crc_size = 2
        if len(buffer) < crc_size:
            return False
        crc_buf = buffer[-crc_size:]
        crc = calcula_crc(buffer[:-crc_size], buffer_size - crc_size).to_bytes(crc_size, 'little')
        return crc_buf == crc

    def lerEncoder(self, tam=9, botao=False):
        try:
            self.conectar()
            if not self.serial.is_open:
                print('Erro: UART não está aberta.')
                return b''

            buffer = self.serial.read(tam)
            if not buffer:
                print("Nenhum dado recebido, possivelmente timeout.")
                return b''

            dados = buffer[3:-2] if not botao else buffer[2:-2]
            if self.validate_crc(buffer, len(buffer)):
                return dados
            else:
                print('Dados incorretos:', buffer)
                return b''

        except Exception as e:
            print(f'Erro na leitura: {str(e)}')
            return b''

        finally:
            self.desconectar()

    def escreverEncoder(self, msg, tam, skip_resp=False) -> None:
        try:
            msg_crc = calcula_crc(msg, tam).to_bytes(2, 'little')
            msg_final = msg + msg_crc
            self.conectar()
            self.serial.write(msg_final)
            # print("Escrevendo")

            if skip_resp:
                self.serial.read(tam)

        except Exception as e:
            print(f'Erro ao escrever: {str(e)}')

        finally:
            self.desconectar()