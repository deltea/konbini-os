DEV = False

import os
import numpy as np
import math
import pygame as pg
import sys, tty, termios, select
import vlc

# oled screen setup
if not DEV:
    from luma.core.interface.serial import spi
    from luma.oled.device import ssd1351
    from PIL import Image

    serial = spi(port=0, device=0, gpio_DC=25, gpio_RST=27, bus_speed_hz=20000000)
    oled = ssd1351(serial_interface=serial, width=128, height=128, bgr=True)

pg.init()
pg.font.init()

# terminal input handling setup
fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)
tty.setcbreak(fd)

# colors
FG = pg.Color("#ffffff")
ACCENT = pg.Color("#0000ff")
BG = pg.Color("#000000")

# generic utils
def lerp(a, b, t):
    return a + (b - a) * t

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

# screen utils
def tint_image(image, tint_color):
    tinted = image.copy()
    tint_surface = pg.Surface(image.get_size(), flags=pg.SRCALPHA)
    tint_surface.fill(tint_color)
    tinted.blit(tint_surface, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
    return tinted

# input utils
def is_key_pressed():
    return select.select([sys.stdin], [], [], 0)[0]

def read_key():
    first = sys.stdin.read(1)
    if first == "\x1b":
        second = sys.stdin.read(1)
        third = sys.stdin.read(1)
        return first + second + third
    else:
        return first

# screen setup
res = (128, 128)
screen_scale = 4 if DEV else 1
screen_size = (res[0] * screen_scale, res[1] * screen_scale)
window = pg.display.set_mode(screen_size)
screen = pg.Surface(res)

# fonts
accent_font = pg.font.Font("./assets/fonts/DigitalDisco.ttf", 16)
title_font = pg.font.Font("./assets/fonts/CutePixel.ttf", 16)
small_font = pg.font.Font("./assets/fonts/monogram.ttf", 16)

clock = pg.time.Clock()
running = True
dt = 0
time = 0

# --------- game loop ---------
try:
    while running:
        dt = clock.tick(60) / 1000
        time += dt

        # input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        if is_key_pressed():
            key = read_key()

            if key == "q":
                running = False
            elif key == "\x1b[A":
                pass
            elif key == "\x1b[B":
                pass
            elif key == "\x1b[D":
                pass
            elif key == "\x1b[C":
                pass
            else:
                print(f"you pressed: {repr(key)}")

        # window clear
        screen.fill(BG)

        # draw text
        text = title_font.render("player", False, FG)
        text_rect = text.get_rect(center=(res[0] / 2, res[1] / 6))
        screen.blit(text, text_rect)

        if DEV:
            window.blit(pg.transform.scale(screen, screen_size), (0, 0))
            pg.display.update()
        else:
            raw_str = pg.image.tostring(screen, "RGB", False)
            img = Image.frombytes("RGB", res, raw_str)
            oled.display(img)
finally:
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    pg.quit()
