import struct
from comunicacao.utils import calcula_crc

# Dicionários para endereços E1 e E2
enderecos_E1 = {
    'BTS': 0x00,
    'B1D': 0x01,
    'B1S': 0x02,
    'B2D': 0x03,
    'B2S': 0x04,
    'B3D': 0x05,
    'BE': 0x06,
    'BT': 0x07,
    'B1': 0x08,
    'B2': 0x09,
    'B3': 0x0A
}

enderecos_E2 = {
    'BTS': 0xA0,
    'B1D': 0xA1,
    'B1S': 0xA2,
    'B2D': 0xA3,
    'B2S': 0xA4,
    'B3D': 0xA5,
    'BE': 0xA6,
    'BT': 0xA7,
    'B1': 0xA8,
    'B2': 0xA9,
    'B3': 0xAA
}

digitos_matricula = bytes([1, 6, 2, 8])

# Funções utilitárias
def get_botao(botao, qtd_bytes, tabela):
    endereco_botao = tabela.get(botao)
    return bytes([endereco_botao, qtd_bytes])

def get_codigo(codigo, valor=0, botao='0', e2=False):
    enderecos = enderecos_E2 if e2 else enderecos_E1
    if codigo == 'temperatura':
        return bytes([0x01, 0x16, 0xD1, e2]) + struct.pack("f", valor) + digitos_matricula
    elif codigo == 'solicita_encoder':
        return bytes([0x01, 0x23, 0xC1, e2]) + digitos_matricula
    elif codigo == 'sinal_PWM':
        return bytes([0x01, 0x16, 0xC2, e2]) + valor.to_bytes(4, 'little', signed=True) + digitos_matricula
    elif codigo == 'le_registrador':
        return bytes([0x01, 0x03]) + get_botao('BTS', 11, enderecos) + digitos_matricula
    elif codigo == 'escreve_registrador':
        return bytes([0x01, 0x06]) + get_botao(botao, 1, enderecos) + valor.to_bytes(1, 'little') + digitos_matricula

def getCodigo_E1(codigo, valor=0, botao='0'):
    return get_codigo(codigo, valor, botao, e2=False)

def getCodigo_E2(codigo, valor=0, botao='0'):
    return get_codigo(codigo, valor, botao, e2=True)