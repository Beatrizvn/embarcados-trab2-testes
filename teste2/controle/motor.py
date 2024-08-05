import RPi.GPIO as GPIO

class Motor():
    def __init__(self, id) -> None:
        self.id = id
        self.DIR1_PIN = 20 if id == 1 else 19
        self.DIR2_PIN = 21 if id == 1 else 26
        self.PWM_PIN = 12 if id == 1 else 13
        self.duty_cycle = 0
        self.__status = 'Livre'
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        GPIO.setup(self.DIR1_PIN, GPIO.OUT)
        GPIO.setup(self.DIR2_PIN, GPIO.OUT)
        GPIO.setup(self.PWM_PIN, GPIO.OUT)
        
        self.pwm = GPIO.PWM(self.PWM_PIN, 1000)  # 1000 Hz de frequência inicial
        self.pwm.start(0)  # duty cycle inicial de 0%
        self.status = 'Livre'
      
    def subirElevador(self):
        GPIO.output(self.DIR1_PIN, GPIO.HIGH)
        GPIO.output(self.DIR2_PIN, GPIO.LOW)
    
    def descerElevador(self):
        GPIO.output(self.DIR1_PIN, GPIO.LOW)
        GPIO.output(self.DIR2_PIN, GPIO.HIGH)
    
    def breakElevador(self):
        GPIO.output(self.DIR1_PIN, GPIO.HIGH)
        GPIO.output(self.DIR2_PIN, GPIO.HIGH)
    
    def getStatus(self):
        return self.status
    
    def setStatus(self, estado):
        self.status = estado
    
    def setDutyCycle(self, valor):
        self.pwm.ChangeDutyCycle(valor)
        
    def moveMotor(self, valor):
        self.setDutyCycle(abs(valor))
        if valor > 0:
            self.subirElevador()
        elif valor < 0:
            self.descerElevador()
        else:
            self.breakElevador()
            self.setStatus('Parado')
