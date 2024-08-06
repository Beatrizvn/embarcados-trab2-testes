from PIL import Image, ImageDraw, ImageFont
import Adafruit_SSD1306

class OLED:
    def __init__(self):
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)
        self.disp.begin()
        self.clear()

        self.image = Image.new('1', (self.disp.width, self.disp.height))
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.load_default()
        
    def display_string(self, string, line):
        y_position = line * 8
        self.draw.rectangle((0, y_position, self.disp.width, y_position + 8), outline=0, fill=0)
        self.draw.text((0, y_position), string, font=self.font, fill=255)
        self.disp.image(self.image)
        self.disp.display()

    def clear(self):
        self.disp.clear()
        self.disp.display()