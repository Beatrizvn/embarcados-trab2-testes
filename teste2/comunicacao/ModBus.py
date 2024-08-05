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

codigo_map = {
    'temperatura': lambda endereco, valor: bytes([0x01, 0x16, 0xD1, endereco]) + struct.pack("f", valor) + digitos_matricula,
    'solicita_encoder': lambda endereco, valor: bytes([0x01, 0x23, 0xC1, endereco]) + digitos_matricula,
    'sinal_PWM': lambda endereco, valor: bytes([0x01, 0x16, 0xC2, endereco]) + valor.to_bytes(4, 'little', signed=True) + digitos_matricula,
    'le_registrador': lambda endereco, valor: bytes([0x01, 0x03]) + get_botao('BTS', 11, tabela_enderecos[endereco]) + digitos_matricula,
    'escreve_registrador': lambda endereco, valor, botao: bytes([0x01, 0x06]) + get_botao(botao, 1, tabela_enderecos[endereco]) + valor.to_bytes(1, 'little') + digitos_matricula,
}

def getCodigo(endereco, codigo, valor=0, botao='0'):
    if codigo in ['temperatura', 'solicita_encoder', 'sinal_PWM', 'le_registrador']:
        return codigo_map[codigo](endereco, valor)
    elif codigo == 'escreve_registrador':
        return codigo_map[codigo](endereco, valor, botao)
    else:
        raise ValueError(f"Código {codigo} não reconhecido")

def get_botao(botao, qtd_bytes, tabela):
    endereco_botao = tabela.get(botao)
    if endereco_botao is None:
        raise ValueError(f"Botão {botao} não encontrado na tabela")
    return bytes([endereco_botao, qtd_bytes])
