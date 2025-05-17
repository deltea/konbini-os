import pygame
import spidev
import RPi.GPIO as GPIO
import time
import numpy as np

# === display settings ===
WIDTH = 128
HEIGHT = 128
DC = 25
RST = 27
SPI_SPEED_HZ = 20000000

# === setup GPIO ===
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(DC, GPIO.OUT)
GPIO.setup(RST, GPIO.OUT)

# === reset display ===
GPIO.output(RST, 0)
time.sleep(0.1)
GPIO.output(RST, 1)
time.sleep(0.1)

# === setup SPI ===
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = SPI_SPEED_HZ
spi.mode = 0b00

# === send command/data ===
def write_cmd(cmd):
    GPIO.output(DC, 0)
    spi.writebytes([cmd])

def write_data(data):
    GPIO.output(DC, 1)
    spi.writebytes(data)

# === basic init sequence for SSD1351 ===
def init_display():
    cmds = [
        (0xFD, [0x12]), (0xFD, [0xB1]), (0xAE, []),
        (0xB3, [0xF1]), (0xCA, [0x7F]), (0xA0, [0x74]),
        (0x15, [0x00, WIDTH - 1]), (0x75, [0x00, HEIGHT - 1]),
        (0xA1, [0x00]), (0xA2, [0x00]), (0xB5, [0x00]),
        (0xAB, [0x01]), (0xB1, [0x32]), (0xBE, [0x05]),
        (0xA6, []), (0xC1, [0xC8, 0x80, 0xC8]),
        (0xC7, [0x0F]), (0xB4, [0xA0, 0xB5, 0x55]),
        (0xB6, [0x01]), (0xAF, [])
    ]
    for cmd, data in cmds:
        write_cmd(cmd)
        if data:
            write_data(data)

# === draw a pygame surface ===
def render_surface():
    surf = pygame.Surface((WIDTH, HEIGHT))
    surf.fill((0, 0, 0))  # black bg
    pygame.draw.circle(surf, (255, 0, 0), (tick % 128, 64), 10)
    return surf

# === convert pygame surface -> RGB565 numpy array ===
def surface_to_rgb565(surface):
    arr = pygame.surfarray.array3d(surface)
    r = (arr[:, :, 0] >> 3).astype(np.uint16)
    g = (arr[:, :, 1] >> 2).astype(np.uint16)
    b = (arr[:, :, 2] >> 3).astype(np.uint16)
    rgb565 = (r << 11) | (g << 5) | b
    return rgb565.astype('>u2').tobytes()  # big endian

# === push framebuffer to screen ===
def display_surface(surface):
    write_cmd(0x15)
    write_data([0x00, WIDTH - 1])
    write_cmd(0x75)
    write_data([0x00, HEIGHT - 1])
    write_cmd(0x5C)

    GPIO.output(DC, 1)
    buffer = surface_to_rgb565(surface)

    CHUNK = 4096
    for i in range(0, len(buffer), CHUNK):
        spi.writebytes(buffer[i:i + CHUNK])

# === main loop ===
pygame.init()
init_display()

tick = 0
clock = pygame.time.Clock()

while True:
    surf = render_surface()
    display_surface(surf)
    tick += 6
    clock.tick(60)
