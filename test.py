from luma.core.interface.serial import spi
from luma.oled.device import ssd1351
from PIL import Image
import time

serial = spi(device=0, port=0, gpio_DC=25, gpio_RST=27, bus_speed_hz=8000000)
device = ssd1351(serial, width=128, height=128)

colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 0, 0)]

while True:
    for c in colors:
        img = Image.new("RGB", (128, 128), c)
        device.display(img.copy())
        time.sleep(0.5)
