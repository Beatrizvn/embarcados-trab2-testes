import RPi.GPIO as GPIO

class Sensor:
    def __init__(self, id) -> None:
        self.id = id
        # Mapeamento dos pinos dos sensores com base no ID
        self.pins = {
            'ST': 18 if id == 1 else 17,
            'S1': 23 if id == 1 else 27,
            'S2': 24 if id == 1 else 22,
            'S3': 25 if id == 1 else 6
        }

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Configura todos os pinos como entradas
        for pin in self.pins.values():
            GPIO.setup(pin, GPIO.IN)

        self.active_sensor = None

    def start(self):
        # Configura a detecção de eventos para todos os sensores
        for sensor, pin in self.pins.items():
            GPIO.add_event_detect(pin, GPIO.RISING, callback=self.sensor_callback, bouncetime=200)

    def stop(self):
        # Remove a detecção de eventos para todos os sensores
        for pin in self.pins.values():
            GPIO.remove_event_detect(pin)
            
    def sensor_callback(self, channel):
        # Identifica qual sensor foi ativado com base no pino
        self.active_sensor = next((sensor for sensor, pin in self.pins.items() if pin == channel), None)
        print(f"Sensor {self.active_sensor} ativado no pino {channel}")

    def cleanup(self):
        self.stop()  # Garante que a detecção de eventos seja parada antes da limpeza
        GPIO.cleanup()
