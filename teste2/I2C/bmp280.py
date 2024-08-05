from bmp280 import BMP280
import smbus2

class bmp280_device:
    def __init__(self):
        self.bus = smbus2.SMBus(1) # para rasp 3
        self.bmp280 = BMP280(i2c_dev=self.bus)
        
    def get_temp(self):
        #return round(self.bmp280.get_temperature(), 2)
        try:
            return round(self.bmp280.get_temperature(), 2)
        except:
            TEMPERATURE = "/sys/bus/iio/devices/iio:device0/in_temp_input"
            with open(TEMPERATURE, 'r') as input_temp:
                temp = int(input_temp.read().strip())
                temperature = (((float(temp) / 1000.0) * 100) + 0.5) / 100
            return round(temperature, 2)