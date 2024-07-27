import serial
import time
from .Crc16 import calcula_crc

class Uart:
    def __init__(self):
        self.serial = None
        self.connected = False
        
    def conectar(self):
        """
        Conecta à porta serial.
        """
        if self.serial is not None and self.serial.is_open:
            self.serial.close()
            
        try:
            self.serial = serial.Serial("/dev/serial0", 115200)  # Abre a porta serial
            self.connected = True
            print('Conexão UART estabelecida')
        except Exception as e:
            print(f'Erro ao conectar UART: {e}')
            
    def desconectar(self):
        """
        Desconecta da porta serial.
        """
        if self.serial is not None and self.serial.is_open:
            self.serial.close()
            self.connected = False
            print('Desconexão UART')

    def validate_crc(self, buffer, buffer_size):
        """
        Verifica se o valor do CRC no final do buffer corresponde ao CRC calculado dos bytes anteriores no buffer.
        """
        crc_size = 2  # CRC tem 2 bytes
        
        if len(buffer) < crc_size:
            return False  # buffer muito pequeno para conter um CRC válido
        
        # bytes do buffer que contêm o CRC
        crc_buf = buffer[-crc_size:]
        # calcula o valor do CRC para os bytes no buffer, excluindo o CRC
        crc = calcula_crc(buffer[:-crc_size], buffer_size - crc_size).to_bytes(crc_size, 'little')
        
        return crc_buf == crc

    def lerEncoder(self, tam=9, botao=False):
        """
        Realiza a leitura de dados do encoder via conexão serial, valida o CRC e retorna os dados ou mensagens de erro.
        """
        try:
            if not self.connected:
                self.conectar()
            
            buffer = self.serial.read(tam)
            dados = buffer[3:-2] if not botao else buffer[2:-2]
            
            if self.validate_crc(buffer, len(buffer)):
                return dados
            else:
                print('Dados incorretos: ', buffer)
        except Exception as e:
            print(f'Erro na leitura: {str(e)}')
            return None
    
    def escreverEncoder(self, msg, tam):
        """
        Escreve dados no encoder via conexão serial, adicionando o CRC aos dados.
        """
        if not self.connected:
            self.conectar()
        
        try:
            msg_crc = calcula_crc(msg, tam).to_bytes(2, 'little')
            msg_final = msg + msg_crc
            self.serial.write(msg_final)
        except Exception as e:
            print(f'Erro ao escrever: {e}')
