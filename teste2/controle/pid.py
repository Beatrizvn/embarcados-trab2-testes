class PID:
    def __init__(self, kp=0.009, ki=0.04, kd=0.011, T=0.2):
    # def __init__(self, kp = 0.05, ki = 0.05, kd = 5, T = 1.0):
        self.referencia, self.saida_medida, self.sinal_de_controle = 0.0, 0.0, 0.0
        self.kp = kp # ganho proporcional
        self.ki = ki # ganho integral
        self.kd = kd # ganho derivativo
        self.T = T # periodo de amostragem (ms)
        self.last_time = 0
        self.erro_total = 0.0
        self.erro_anterior = 0.0
        self.sinal_de_controle_MAX = 100.0
        self.sinal_de_controle_MIN = -100.0
    
    def atualiza_referencia(self, nova_referencia):
        self.referencia = nova_referencia
    
    def controle(self, saida_medida):
        erro = self.referencia - saida_medida
        
        self.erro_total += erro # acumula o erro (termo integral)
        
        if self.erro_total >= self.sinal_de_controle_MAX:
            self.erro_total = self.sinal_de_controle_MAX
        elif self.erro_total<= self.sinal_de_controle_MIN:
            self.erro_total = self.sinal_de_controle_MIN
            
        delta_error = erro - self.erro_anterior # diferenca entre os erros (termo derivativo)
        
        # PID calcula sinal de controle
        self.sinal_de_controle = (
            self.kp * erro + (self.ki * self.T) * self.erro_total + (self.kd / self.T) * delta_error
        )
        
        if self.sinal_de_controle >= self.sinal_de_controle_MAX:
            self.sinal_de_controle = self.sinal_de_controle_MAX
        elif self.sinal_de_controle <= self.sinal_de_controle_MIN:
            self.sinal_de_controle = self.sinal_de_controle_MIN
        
        self.erro_anterior = erro
        
        return self.sinal_de_controle    