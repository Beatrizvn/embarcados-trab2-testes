import RPi.GPIO as GPIO
from .config import SENSOR_PINS

class Sensor:
    def __init__(self, id):
        self.id = id
        self.ST_PIN, self.S1_PIN, self.S2_PIN, self.S3_PIN = SENSOR_PINS[id]

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(self.ST_PIN, GPIO.IN)
        GPIO.setup(self.S1_PIN, GPIO.IN)
        GPIO.setup(self.S2_PIN, GPIO.IN)
        GPIO.setup(self.S3_PIN, GPIO.IN)

        self.active_sensor = None

def start(self):
    for pin in [self.ST_PIN, self.S1_PIN, self.S2_PIN, self.S3_PIN]:
        GPIO.add_event_detect(pin, GPIO.RISING, callback=self.sensor_callback, bouncetime=200)

def sensor_callback(self, channel):
    sensor_map = {
        self.ST_PIN: "ST",
        self.S1_PIN: "S1",
        self.S2_PIN: "S2",
        self.S3_PIN: "S3"
    }
    self.active_sensor = sensor_map.get(channel, None)
    if self.active_sensor:
        print(f"Sensor {self.active_sensor} triggered on pin {channel}")

    def stop(self):
        GPIO.remove_event_detect(self.ST_PIN)
        GPIO.remove_event_detect(self.S1_PIN)
        GPIO.remove_event_detect(self.S2_PIN)
        GPIO.remove_event_detect(self.S3_PIN)

    def cleanup(self):
        self.stop()
        GPIO.cleanup()
