from bmp280 import BMP280
import smbus2
from utils.exceptions import SensorError

class BMP280Device:
    def __init__(self, bus_number=1):
        try:
            self.bus = smbus2.SMBus(bus_number)  # Para Raspberry Pi 3
            self.bmp280 = BMP280(i2c_dev=self.bus)
        except Exception as e:
            raise SensorError(f"Erro ao inicializar o BMP280: {e}")
        
    def get_temp(self):
        """Obtém a temperatura do BMP280 ou usa um método de fallback."""
        try:
            return self._read_bmp280_temperature()
        except Exception as e:
            print(f"Erro ao obter a temperatura do BMP280: {e}")
            return self._read_fallback_temperature()

    def _read_bmp280_temperature(self):
        """Lê a temperatura do sensor BMP280."""
        return round(self.bmp280.get_temperature(), 2)

    def _read_fallback_temperature(self):
        """Lê a temperatura usando um método de fallback."""
        TEMPERATURE = "/sys/bus/iio/devices/iio:device0/in_temp_input"
        try:
            with open(TEMPERATURE, 'r') as input_temp:
                temp = int(input_temp.read().strip())
                temperature = (((float(temp) / 1000.0) * 100) + 0.5) / 100
            return round(temperature, 2)
        except Exception as e:
            print(f"Erro ao ler temperatura alternativa: {e}")
            raise SensorError("Falha ao obter a temperatura de backup.")
