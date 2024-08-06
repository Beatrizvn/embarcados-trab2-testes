# uart.py
import serial
from comunicacao.utils import calcula_crc

class Uart:
    def __init__(self, port="/dev/serial0", baudrate=115200, timeout=0.5):
        self.serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=timeout
        )
        self.connected = False
        print("UART Inicializada")

    def conectar(self):
        """Abre a conexão UART se não estiver aberta."""
        if not self.serial.is_open:
            self.serial.open()
        self.connected = True

    def desconectar(self):
        """Fecha a conexão UART se estiver aberta."""
        if self.serial.is_open:
            self.serial.close()
        self.connected = False

    def validate_crc(self, data):
        """
        Valida o CRC dos dados recebidos.

        Parâmetros:
            data (bytes): Dados recebidos com CRC.

        Retorna:
            bool: True se o CRC for válido, False caso contrário.
        """
        if len(data) < 2:
            return False

        received_crc = data[-2:]
        calculated_crc = calcula_crc(data[:-2], len(data) - 2).to_bytes(2, 'little')
        return received_crc == calculated_crc

    def ler_encoder(self, tam=9, botao=False):
        """
        Lê dados do encoder via UART.

        Parâmetros:
            tam (int): Número de bytes a serem lidos.
            botao (bool): Indica se a leitura é de um botão.

        Retorna:
            bytes: Dados lidos ou uma string vazia em caso de erro.
        """
        try:
            self.conectar()

            if not self.serial.is_open:
                raise ConnectionError('Erro: UART não está aberta.')

            buffer = self.serial.read(tam)
            if not buffer:
                raise TimeoutError("Nenhum dado recebido, possivelmente timeout.")

            dados = buffer[3:-2] if not botao else buffer[2:-2]

            if self.validate_crc(buffer):
                return dados
            else:
                raise ValueError(f'Dados incorretos: {buffer}')

        except (ConnectionError, TimeoutError, ValueError) as e:
            print(f'Erro na leitura: {e}')
            return b''

        finally:
            self.desconectar()

    def escrever_encoder(self, msg, tam, skip_resp=False):
        """
        Envia dados para o encoder via UART.

        Parâmetros:
            msg (bytes): Mensagem a ser enviada.
            tam (int): Tamanho dos dados esperados na resposta.
            skip_resp (bool): Se True, ignora a resposta após o envio.

        Retorna:
            None
        """
        try:
            msg_crc = calcula_crc(msg, len(msg)).to_bytes(2, 'little')
            msg_final = msg + msg_crc

            self.conectar()
            self.serial.write(msg_final)

            if not skip_resp:
                resposta = self.serial.read(tam)
                if not resposta:
                    raise TimeoutError("Nenhuma resposta recebida.")
                # Opcional: Processar a resposta aqui, se necessário

        except (serial.SerialException, TimeoutError) as e:
            print(f'Erro ao escrever: {e}')

        finally:
            self.desconectar()
