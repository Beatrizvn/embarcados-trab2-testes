from PIL import Image, ImageDraw, ImageFont
import Adafruit_SSD1306

class OLEDDisplay:
    def __init__(self, rst=None):
        try:
            # Inicializa o display OLED
            self.disp = Adafruit_SSD1306.SSD1306_128_64(rst=rst)
            self.disp.begin()
            self.clear()
            # Cria imagem em modo 1-bit color
            self.image = Image.new('1', (self.disp.width, self.disp.height))
            # Inicializa Draw object
            self.draw = ImageDraw.Draw(self.image)
            # Fonte padrão
            self.font = ImageFont.load_default()
        except Exception as e:
            raise IOError(f"Erro ao inicializar o OLED: {e}")

    def clear(self):
        # Limpa o display
        self.disp.clear()
        self.disp.display()

def display_string(self, string, line):
    """Exibe uma string em uma linha específica do display OLED."""
    try:
        self._draw_text(string, line)
        self.disp.image(self.image)
        self.disp.display()
    except Exception as e:
        raise IOError(f"Erro ao exibir string no OLED: {e}")

def _draw_text(self, text, line):
    """Desenha o texto na linha especificada."""
    y_position = line * 8
    self.draw.rectangle((0, y_position, self.disp.width, y_position + 8), outline=0, fill=0)
    self.draw.text((0, y_position), text, font=self.font, fill=255)
