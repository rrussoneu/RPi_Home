from luma.core.interface.serial import spi, noop
from luma.oled.device import sh1106
from PIL import Image, ImageDraw, ImageFont
import time

# SPI config
serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25, gpio_CS=8)
device = sh1106(serial, width=128, height=64)

# Clear display
device.clear()
device.show()

# Blank image to draw on
width = device.width
height = device.height
image = Image.new("1", (width, height))
draw = ImageDraw.Draw(image)

# Default font
font = ImageFont.load_default()

# Black box to clear
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Add some text and a horizontal line
draw.text((0, 0), "Hello world!", font=font, fill=255)
draw.line((0, height//2, width, height//2), fill=255)

# Display image and wait a few seconds
device.display(image)

time.sleep(5)

# Clear display
draw.rectangle((0, 0, width, height), outline=0, fill=0)
device.display(image)
