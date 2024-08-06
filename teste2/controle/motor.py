import RPi.GPIO as GPIO
from .config import MOTOR_PINS

class Motor:
    def __init__(self, id):
        self.id = id
        self.DIR1_PIN, self.DIR2_PIN, self.PWM_PIN = MOTOR_PINS[id]
        self.duty_cycle = 0
        self.__status = 'Livre'
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.DIR1_PIN, GPIO.OUT)
        GPIO.setup(self.DIR2_PIN, GPIO.OUT)
        GPIO.setup(self.PWM_PIN, GPIO.OUT)

        self.pwm = GPIO.PWM(self.PWM_PIN, 1000)  
        self.pwm.start(0)  
        self.status = 'Livre'
      
    def up_elevador(self):
        GPIO.output(self.DIR1_PIN, GPIO.HIGH)
        GPIO.output(self.DIR2_PIN, GPIO.LOW)
    
    def down_elevador(self):
        GPIO.output(self.DIR1_PIN, GPIO.LOW)
        GPIO.output(self.DIR2_PIN, GPIO.HIGH)
    
    def break_elevador(self):
        GPIO.output(self.DIR1_PIN, GPIO.HIGH)
        GPIO.output(self.DIR2_PIN, GPIO.HIGH)
    
    def set_status(self, estado):
        self.status = estado
    
    def get_status(self):
        return self.status
    
    def set_duty_cycle(self, valor):
        if 0 <= valor <= 100:
            self.pwm.ChangeDutyCycle(valor)
            
    def move_motor(self, valor):
        self.set_duty_cycle(abs(valor))
        if valor == 0:
            self.break_elevador()
            self.set_status('Parado')
        else:
            if valor > 0:
                self.up_elevador()
            else:
                self.down_elevador()

