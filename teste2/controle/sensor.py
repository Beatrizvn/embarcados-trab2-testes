import RPi.GPIO as GPIO

class Sensor:
    def __init__(self, id) -> None:
        self.id = id
        self.ST_PIN = 18 if id == 1 else 17
        self.S1_PIN = 23 if id == 1 else 27
        self.S2_PIN = 24 if id == 1 else 22
        self.S3_PIN = 25 if id == 1 else 6

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(self.ST_PIN, GPIO.IN)
        GPIO.setup(self.S1_PIN, GPIO.IN)
        GPIO.setup(self.S2_PIN, GPIO.IN)
        GPIO.setup(self.S3_PIN, GPIO.IN)

        self.active_sensor = None

    def start(self):
        # Setup event detection for all sensors
        GPIO.add_event_detect(self.ST_PIN, GPIO.RISING, callback=self.sensor_callback, bouncetime=200)
        GPIO.add_event_detect(self.S1_PIN, GPIO.RISING, callback=self.sensor_callback, bouncetime=200)
        GPIO.add_event_detect(self.S2_PIN, GPIO.RISING, callback=self.sensor_callback, bouncetime=200)
        GPIO.add_event_detect(self.S3_PIN, GPIO.RISING, callback=self.sensor_callback, bouncetime=200)

    def sensor_callback(self, channel):
        if channel == self.ST_PIN:
            self.active_sensor = "ST"
        elif channel == self.S1_PIN:
            self.active_sensor = "S1"
        elif channel == self.S2_PIN:
            self.active_sensor = "S2"
        elif channel == self.S3_PIN:
            self.active_sensor = "S3"
        print(f"Sensor {self.active_sensor} triggered on pin {channel}")

    def stop(self):
        # Remove event detection for all sensors
        GPIO.remove_event_detect(self.ST_PIN)
        GPIO.remove_event_detect(self.S1_PIN)
        GPIO.remove_event_detect(self.S2_PIN)
        GPIO.remove_event_detect(self.S3_PIN)

    def cleanup(self):
        self.stop()  # Ensure event detection is stopped before cleanup
        GPIO.cleanup()