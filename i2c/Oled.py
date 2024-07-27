import board
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

# Configuração do display OLED
I2C_ADDRESS = 0x3C  # Endereço do OLED SSD1306
WIDTH = 128
HEIGHT = 64
BORDER = 5

# Inicializa o barramento I2C e o display OLED
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=I2C_ADDRESS)

# Limpa o display
oled.fill(0)
oled.show()

# Cria uma imagem em preto e branco
image = Image.new('1', (WIDTH, HEIGHT))
draw = ImageDraw.Draw(image)

# Carrega uma fonte
font = ImageFont.load_default()

def display_elevator_state_and_floor(state, floor):
    """Exibe o estado do elevador e o andar atual no display OLED."""
    draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)
    draw.text((BORDER, BORDER), f"Estado: {state}", font=font, fill=255)
    draw.text((BORDER, 20), f"Andar: {floor}", font=font, fill=255)
    oled.image(image)
    oled.show()

# Exemplos de uso
display_elevator_state_and_floor("Em movimento", "3")

