import struct

digitos_matricula = bytes([1, 6, 2, 8]) #211031628

tabela_enderecos_E1 = {
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

tabela_enderecos_E2 = {
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

def codigo_E1(codigo, valor=0, botao='0'):
    if codigo == 'temperatura':
        # return bytes([0x01, 0x16, 0xD1]) + struct.pack("f", valor) + digitos_matricula
        return bytes([0x01, 0x16, 0xD1, 0x00]) + struct.pack("f", valor) + digitos_matricula
    elif codigo == 'solicita_encoder':
        return bytes([0x01, 0x23, 0xC1, 0x00]) + digitos_matricula 
    elif codigo == 'sinal_PWM':
        return bytes([0x01, 0x16, 0xC2, 0x00]) + valor.to_bytes(4, 'little', signed=True) + digitos_matricula
    elif codigo == 'le_registrador':
        return bytes([0x01, 0x03]) + get_botao('BTS', 11, tabela_enderecos_E1) + digitos_matricula
    elif codigo == 'escreve_registrador':
        return bytes([0x01, 0x06]) + get_botao(botao, 1, tabela_enderecos_E1) + valor.to_bytes(1, 'little') + digitos_matricula

def codigo_E2(codigo, valor=0, botao='0'):
    if codigo == 'temperatura':
        # return bytes([0x01, 0x16, 0xD1]) + struct.pack("f", valor) + digitos_matricula
        return bytes([0x01, 0x16, 0xD1, 0x01]) + struct.pack("f", valor) + digitos_matricula
    elif codigo == 'solicita_encoder':
        return bytes([0x01, 0x23, 0xC1, 0x01]) + digitos_matricula
    elif codigo == 'sinal_PWM':
        return bytes([0x01, 0x16, 0xC2, 0x01]) + valor.to_bytes(4, 'little', signed=True) + digitos_matricula
    elif codigo == 'le_registrador':
        return bytes([0x01, 0x03]) + get_botao('BTS', 11, tabela_enderecos_E2) + digitos_matricula
    elif codigo == 'escreve_registrador':
        return bytes([0x01, 0x06]) + get_botao(botao, 1, tabela_enderecos_E2) + valor.to_bytes(1, 'little') + digitos_matricula

def get_botao(botao, qtd_bytes, tabela):
    endereco_botao = tabela.get(botao)
    sub_codigo = bytes([endereco_botao, qtd_bytes])
    return sub_codigo