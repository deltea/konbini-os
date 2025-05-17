DEV = False

import os
import numpy as np
import math
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

# animation
animations = {
    "gear": {
        "folder": "assets/sprites/gear",
        "frames": [tint_image(pg.image.load(os.path.join("assets/sprites/gear", f)).convert_alpha(), ACCENT) for f in sorted(os.listdir("assets/sprites/gear"))],
    },
    "donut": {
        "folder": "assets/sprites/donut",
        "frames": [tint_image(pg.image.load(os.path.join("assets/sprites/donut", f)).convert_alpha(), ACCENT) for f in sorted(os.listdir("assets/sprites/donut"))],
    },
    "monke": {
        "folder": "assets/sprites/monke",
        "frames": [tint_image(pg.image.load(os.path.join("assets/sprites/monke", f)).convert_alpha(), ACCENT) for f in sorted(os.listdir("assets/sprites/monke"))],
    },
    "music": {
        "folder": "assets/sprites/music",
        "frames": [tint_image(pg.image.load(os.path.join("assets/sprites/music", f)).convert_alpha(), ACCENT) for f in sorted(os.listdir("assets/sprites/music"))],
    },
    "shutdown": {
        "folder": "assets/sprites/shutdown",
        "frames": [tint_image(pg.image.load(os.path.join("assets/sprites/shutdown", f)).convert_alpha(), ACCENT) for f in sorted(os.listdir("assets/sprites/shutdown"))],
    }
}

animation_timer = 0
current_frame = 0
animation_speed = 1

clock = pg.time.Clock()
running = True
dt = 0
time = 0
select_index = 0
icon_row_x = 0

def change_select_index(direction):
    global select_index
    select_index = (select_index + direction) % len(apps)

def select_app():
    global running
    print(f"selected app: {apps[select_index]['name']}")
    running = False

apps = [
    {
        "name": "settings",
        "color": pg.Color("red"),
        "animation": "gear",
    },
    {
        "name": "donut",
        "color": pg.Color("red"),
        "animation": "music",
    },
    {
        "name": "movies",
        "color": pg.Color("red"),
        "animation": "monke",
    },
    {
        "name": "music",
        "color": pg.Color("red"),
        "animation": "gear",
    },
    {
        "name": "shutdown",
        "color": pg.Color("red"),
        "animation": "shutdown",
    },
]

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
                select_app()
            elif key == "\x1b[B":
                select_app()
            elif key == "\x1b[D":
                change_select_index(-1)
            elif key == "\x1b[C":
                change_select_index(1)
            else:
                print(f"you pressed: {repr(key)}")

        # update animations
        animation_timer += 1
        if animation_timer >= 1:
            animation_timer = 0
            current_frame = (current_frame + animation_speed) % 101

        # window clear
        screen.fill(BG)

        # draw text
        text = title_font.render(apps[select_index]["name"], False, FG)
        text_rect = text.get_rect(center=(res[0] / 2, res[1] / 6))
        screen.blit(text, text_rect)

        x = math.sin(time * 4) * 4

        bracket_1 = title_font.render("<              ", False, FG)
        bracket_1_rect = bracket_1.get_rect(center=(res[0] / 2 - x - 8, res[1] / 6))
        screen.blit(bracket_1, bracket_1_rect)

        bracket_2 = title_font.render("              >", False, FG)
        bracket_2_rect = bracket_2.get_rect(center=(res[0] / 2 + x + 8, res[1] / 6))
        screen.blit(bracket_2, bracket_2_rect)

        # draw app icon
        x_offset = select_index * 74
        icon_row_x = lerp(icon_row_x, res[0] / 2 - 32 - x_offset, 10 * dt)
        for i, app in enumerate(apps):
            screen.blit(animations[app["animation"]]["frames"][current_frame], (icon_row_x + i * 74, res[1] / 5 * 3 - 32))

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
