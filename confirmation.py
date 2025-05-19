DEV = False

import math
import os
import pygame as pg
import sys, tty, termios, select

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
BG = pg.Color("#000000")

# generic utils
def lerp(a, b, t):
    return a + (b - a) * t

def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))

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

angle = 10  # degrees
speed = 0.5  # pixels per second

text_surface = title_font.render(" DANGER! " * 3, False, BG)
text_width = text_surface.get_width()
text_height = text_surface.get_height()

scroll = 0
padding = 4
select_index = 0

arrow_image = pg.image.load("assets/sprites/arrow.png").convert_alpha()
arrow_y = 0
arrow_x = 0

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
                select_index = (select_index - 1) % 2
            elif key == "\x1b[B":
                select_index = (select_index + 1) % 2
            else:
                print(f"you pressed: {repr(key)}")

        # window clear
        screen.fill(BG)

        # draw text
        confirm_text = title_font.render("are you sure?", False, FG)
        confirm_text_rect = confirm_text.get_rect(center=(res[0] // 2, res[1] // 3))
        screen.blit(confirm_text, confirm_text_rect)

        options = ["yup!", "nah"]
        option_width = 0

        for i in range(2):
            option_text = small_font.render(options[i], False, FG)
            if i == select_index:
                option_width = option_text.get_width()
            option_text_rect = option_text.get_rect(center=(res[0] // 2, res[1] // 2 + i * 16))
            screen.blit(option_text, option_text_rect)

        for i in range(2):
            background = pg.Surface((res[0], text_height))
            background.fill(FG)
            screen.blit(background, (0, res[1] - padding - text_height if i == 1 else padding))

        scroll = (scroll + speed) % text_width
        for j in range(2):
            for i in range(-1, screen.get_width() // text_width + 2):
                x = i * text_width - scroll + (20 if j == 1 else 0)
                screen.blit(text_surface, (x, res[1] - padding - text_height if j == 1 else padding))

        arrow_x = lerp(arrow_x, res[0] // 2 - arrow_image.get_width() // 2 - option_width // 2 - 8, 25 * dt)
        arrow_y = lerp(arrow_y, res[1] // 2 + select_index * 16, 25 * dt)
        screen.blit(arrow_image, (arrow_x, arrow_y))

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
