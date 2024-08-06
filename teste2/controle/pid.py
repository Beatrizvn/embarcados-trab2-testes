class PID:
    def __init__(self, kp=0.009, ki=0.04, kd=0.011, T=0.2):
        self.referencia = 0.0
        self.saida_medida = 0.0
        self.sinal_de_controle = 0.0
        self.kp = kp  # ganho proporcional
        self.kd = kd  # ganho derivativo
        self.ki = ki  # ganho integral
        self.T = T  # periodo de amostragem (ms)
        self.last_time = 0
        self.erro_total = 0.0
        self.erro_anterior = 0.0
        self.sinal_de_controle_MAX = 100.0
        self.sinal_de_controle_MIN = -100.0
    
    def atualiza_referencia(self, nova_referencia):
        self.referencia = nova_referencia
    
    def controle(self, saida_medida):
        erro = self.referencia - saida_medida
        self.erro_total += erro  # acumula o erro (termo integral)
        
        # Limita o erro total ao máximo e mínimo do sinal de controle
        self.erro_total = max(min(self.erro_total, self.sinal_de_controle_MAX), self.sinal_de_controle_MIN)
        
        delta_error = erro - self.erro_anterior  # diferença entre os erros (termo derivativo)
        
        # PID calcula sinal de controle
        self.sinal_de_controle = (
            self.kp * erro +
            (self.ki * self.T) * self.erro_total +
            (self.kd / self.T) * delta_error
        )
        
        # Limita o sinal de controle ao máximo e mínimo
        self.sinal_de_controle = max(min(self.sinal_de_controle, self.sinal_de_controle_MAX), self.sinal_de_controle_MIN)
        
        self.erro_anterior = erro
        
        return self.sinal_de_controle   