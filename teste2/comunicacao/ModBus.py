import struct

digitos_matricula = bytes([1, 6, 2, 8])  # 211031628

tabela_enderecos = {
    'E1': {
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
    },
    'E2': {
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
}

def getCodigo(tipo, codigo, valor=0, botao='0'):
    tabela = tabela_enderecos[tipo]
    prefixos = {
        'temperatura': (0x01, 0x16, 0xD1),
        'solicita_encoder': (0x01, 0x23, 0xC1),
        'sinal_PWM': (0x01, 0x16, 0xC2),
        'le_registrador': (0x01, 0x03),
        'escreve_registrador': (0x01, 0x06)
    }
    
    if codigo in prefixos:
        prefix = prefixos[codigo]
        if codigo == 'temperatura':
            return bytes(prefix) + (bytes([0x00]) if tipo == 'E1' else bytes([0x01])) + struct.pack("f", valor) + digitos_matricula
        elif codigo == 'sinal_PWM':
            return bytes(prefix) + bytes(valor.to_bytes(4, 'little', signed=True)) + digitos_matricula
        elif codigo == 'le_registrador':
            return bytes(prefix) + get_botao('BTS', 11, tabela) + digitos_matricula
        elif codigo == 'escreve_registrador':
            return bytes(prefix) + get_botao(botao, 1, tabela) + valor.to_bytes(1, 'little') + digitos_matricula
        elif codigo == 'solicita_encoder':
            return bytes(prefix) + (bytes([0x00]) if tipo == 'E1' else bytes([0x01])) + digitos_matricula

def get_botao(botao, qtd_bytes, tabela):
    endereco_botao = tabela.get(botao)
    return bytes([endereco_botao, qtd_bytes])
