class PID:
    def __init__(self, kp=0.009, ki=0.04, kd=0.011, T=0.2):
        self.referencia, self.saida_medida, self.sinal_de_controle = 0.0, 0.0, 0.0
        self.kp = kp  # ganho proporcional
        self.ki = ki  # ganho integral
        self.kd = kd  # ganho derivativo
        self.T = T    # periodo de amostragem (ms)
        self.last_time = 0
        self.erro_total = 0.0
        self.erro_anterior = 0.0
        self.sinal_de_controle_MAX = 100.0
        self.sinal_de_controle_MIN = -100.0
    
    def atualiza_referencia(self, nova_referencia):
        self.referencia = nova_referencia
    
def controle(self, saida_medida):
    erro = self.referencia - saida_medida
    self.erro_total = self.clamp(self.erro_total + erro)
    delta_erro = erro - self.erro_anterior

    # Calcula sinal de controle
    self.sinal_de_controle = (
        self.kp * erro +
        (self.ki * self.T) * self.erro_total +
        (self.kd / self.T) * delta_erro
    )
    self.sinal_de_controle = self.clamp(self.sinal_de_controle)
    self.erro_anterior = erro

    return self.sinal_de_controle

def clamp(self, valor):
    return max(self.sinal_de_controle_MIN, min(valor, self.sinal_de_controle_MAX))

