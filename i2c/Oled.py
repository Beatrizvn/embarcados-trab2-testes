import board
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import adafruit_bmp280

# Configuração do display OLED
OLED_I2C_ADDRESS = 0x3C  # Endereço comum do OLED SSD1306
WIDTH = 128
HEIGHT = 64
BORDER = 5

# Configuração do sensor BMP280
BMP280_I2C_ADDRESS = 0x76  # Endereço do sensor BMP280

# Inicializa o barramento I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Inicializa o sensor BMP280
try:
    bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=BMP280_I2C_ADDRESS)
    print("Sensor BMP280 inicializado com sucesso.")
except ValueError as e:
    print(f"Erro ao inicializar o sensor BMP280: {e}")
    bmp280 = None

# Inicializa o display OLED
try:
    oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=OLED_I2C_ADDRESS)
except ValueError as e:
    print(f"Erro ao inicializar o display OLED: {e}")
    # Tente outro endereço I2C se necessário
    OLED_I2C_ADDRESS = 0x3D  # Outro endereço comum do OLED SSD1306
    try:
        oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=OLED_I2C_ADDRESS)
    except ValueError as e:
        print(f"Erro ao inicializar o display OLED com o endereço alternativo: {e}")
        oled = None

if oled:
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
else:
    print("Display OLED não encontrado.")