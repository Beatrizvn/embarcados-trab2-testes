import threading
import RPi.GPIO as GPIO 

class Sensor(threading.Thread):
    def __init__(self) -> None:
        super().__init__()
        self.ST_PIN = 18
        self.S1_PIN = 23
        self.S2_PIN = 24
        self.S3_PIN = 25
        self.active_sensor = None
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        GPIO.setup(self.ST_PIN, GPIO.IN)
        GPIO.setup(self.S1_PIN, GPIO.IN)
        GPIO.setup(self.S2_PIN, GPIO.IN)
        GPIO.setup(self.S3_PIN, GPIO.IN)
        
        self.running = True
        
    def detectSensor(self):
        if GPIO.input(self.ST_PIN) == GPIO.HIGH:
            return "ST"
        elif GPIO.input(self.S1_PIN) == GPIO.HIGH:
            return "S1"
        elif GPIO.input(self.S2_PIN) == GPIO.HIGH:
            return "S2"
        elif GPIO.input(self.S3_PIN) == GPIO.HIGH:
            return "S3"
        else:
            return None
        
    def run(self):
        while self.running:
            self.active_sensor = self.detectSensor()
    
    def stop(self):
        self.running = False