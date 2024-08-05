from PIL import Image, ImageDraw, ImageFont
import Adafruit_SSD1306 

class OLED:
    def __init__(self):
        # Inicializa o display OLED
        self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)
        self.disp.begin()
        self.clear()

        # Cria imagem em modo 1-bit color
        self.image = Image.new('1', (self.disp.width, self.disp.height))

        # Inicializa Draw object
        self.draw = ImageDraw.Draw(self.image)

        # Fonte padrão
        self.font = ImageFont.load_default()

    def clear(self):
        # Limpa o display
        self.disp.clear()
        self.disp.display()

    def display_string(self, string, line):
        # Desenha a string na linha especificada
        self.draw.rectangle((0, line * 8, self.disp.width, (line + 1) * 8), outline=0, fill=0)
        self.draw.text((0, line * 8), string, font=self.font, fill=255)
        self.disp.image(self.image)
        self.disp.display()