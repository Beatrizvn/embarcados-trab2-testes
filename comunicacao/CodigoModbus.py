import struct

# Digitos da Matrícula
digitos_matricula = bytes([7, 9, 9, 7])  # 190037997

tabela_enderecos = {
    'BTS': 0x00,
    'B1D': 0x01,
    'B1S': 0x02,
    'B2D': 0x03,
    'B2S': 0x04,
    'B3D': 0x05,
    'BEmergencia': 0x06,
    'BT': 0x07,
    'B1': 0x08,
    'B2': 0x09,
    'B3': 0x0A,
    '0': 0
}

def getCodigo(codigo, valor = 0, botao = '0'):
    # Codigos do Protocolo de Comunicacao
    
    # retorna protocolo
    if codigo == 'temperatura':
        return bytes([0x01, 0x16, 0xD1]) + struct.pack("f", valor) + digitos_matricula
    elif codigo == 'solicita_encoder':
        return bytes([0x01, 0x23, 0xC1]) + digitos_matricula
    elif codigo == 'sinal_PWM':
        return bytes([0x01, 0x16, 0xC2]) + valor.to_bytes(4, 'little', signed=True) + digitos_matricula
    elif codigo == 'le_registrador':
        return bytes([0x01, 0x03]) + endereca_botao('BTS', 11) + digitos_matricula
    elif codigo == 'escreve_registrador':
        return bytes([0x01, 0x06]) + endereca_botao(botao, 1) + valor.to_bytes(1, 'little') + digitos_matricula

# Endereco (Tab.2) + Qtd
def endereca_botao(botao, qtd_bytes):
        
    endereco_botao = tabela_enderecos.get(botao)
    sub_codigo = bytes([endereco_botao, qtd_bytes])
    
    return sub_codigo