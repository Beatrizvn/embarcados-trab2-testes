class PID:
    def __init__(self, kp=0.009, ki=0.04, kd=0.011, T=0.2):
        self.referencia = 0.0
        self.saida_medida = 0.0
        self.sinal_de_controle = 0.0
        self.kp = kp  # ganho proporcional
        self.ki = ki  # ganho integral
        self.kd = kd  # ganho derivativo
        self.T = T  # período de amostragem (s)
        self.erro_total = 0.0
        self.erro_anterior = 0.0
        self.sinal_de_controle_MAX = 100.0
        self.sinal_de_controle_MIN = -100.0

    def atualiza_referencia(self, nova_referencia):
        self.referencia = nova_referencia

    def controle(self, saida_medida):
        erro = self.referencia - saida_medida
        self.erro_total += erro

        # Limita o erro total para evitar integrador windup
        self.erro_total = self.limitar_valor(self.erro_total, self.sinal_de_controle_MIN, self.sinal_de_controle_MAX)
        
        delta_error = erro - self.erro_anterior

        # Calcula o sinal de controle
        self.sinal_de_controle = (
            self.kp * erro + 
            (self.ki * self.T) * self.erro_total + 
            (self.kd / self.T) * delta_error
        )

        # Limita o sinal de controle
        self.sinal_de_controle = self.limitar_valor(self.sinal_de_controle, self.sinal_de_controle_MIN, self.sinal_de_controle_MAX)

        self.erro_anterior = erro
        return self.sinal_de_controle

    def limitar_valor(self, valor, minimo, maximo):
        """Limita o valor dentro do intervalo [minimo, maximo]."""
        return max(min(valor, maximo), minimo)
