DEV = False

import math
import pygame as pg
import colorsys

if not DEV:
    from luma.core.interface.serial import spi
    from luma.oled.device import ssd1351
    from PIL import Image

    # init luma oled
    serial = spi(port=0, device=0, gpio_DC=25, gpio_RST=27, bus_speed_hz=20000000)
    oled = ssd1351(serial_interface=serial, width=128, height=128)

pg.init()
pg.font.init()

FG = pg.Color("#ffffff")
BG = pg.Color("#000000")

res = (128, 128)
if DEV:
    screen_scale = 4
    size = (res[0] * screen_scale, res[1] * screen_scale)
    window = pg.display.set_mode(size)
screen = pg.Surface(res)

title_font = pg.font.Font("./assets/fonts/DigitalDisco.ttf", 16)
main_font = pg.font.Font("./assets/fonts/dogicabold.ttf", 8)
heavy_font = pg.font.Font("./assets/fonts/CutePixel.ttf", 16)

clock = pg.time.Clock()
running = True
dt = 0
time = 0

def draw_rectangle(x, y, width, height, color, rotation=0):
    """Draw a rectangle, centered at x, y.

    Arguments:
      x (int/float):
        The x coordinate of the center of the shape.
      y (int/float):
        The y coordinate of the center of the shape.
      width (int/float):
        The width of the rectangle.
      height (int/float):
        The height of the rectangle.
      color (str):
        Name of the fill color, in HTML format.
    """
    points = []

    # The distance from the center of the rectangle to
    # one of the corners is the same for each corner.
    radius = math.sqrt((height / 2)**2 + (width / 2)**2)

    # Get the angle to one of the corners with respect
    # to the x-axis.
    angle = math.atan2(height / 2, width / 2)

    # Transform that angle to reach each corner of the rectangle.
    angles = [angle, -angle + math.pi, angle + math.pi, -angle]

    # Convert rotation from degrees to radians.
    rot_radians = (math.pi / 180) * rotation

    # Calculate the coordinates of each point.
    for angle in angles:
        y_offset = -1 * radius * math.sin(angle + rot_radians)
        x_offset = radius * math.cos(angle + rot_radians)
        points.append((x + x_offset, y + y_offset))

    pg.draw.polygon(screen, color, points)


# --------- game loop ---------
while running:
    # input
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    # window clear
    screen.fill(BG)

    # draw circle
    shape_size = 40
    pos = (res[0] / 2 + math.cos(time * 8) * 8, res[1] / 3 * 2 + math.sin(time * 8) * 8)
    # pg.draw.rect(screen, FG, (pos[0] - shape_size / 2, pos[1] - shape_size / 2, shape_size, shape_size), width=3, border_radius=4)
    draw_rectangle(pos[0], pos[1], shape_size, shape_size, FG, rotation=time * 100)

    # RAINBOW
    hue = (time * 0.5) % 1.0
    r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
    FG = (int(r * 255), int(g * 255), int(b * 255))

    # draw text
    text = heavy_font.render("helloooo world", False, pg.Color("#ffffff"))
    text_rect = text.get_rect(center=(res[0] / 2 + math.cos(time * 4) * 6, res[1] / 6 + math.sin(time * 4) * 6))
    screen.blit(text, text_rect)

    if DEV:
        window.blit(pg.transform.scale(screen, size), (0, 0))
        pg.display.update()
    else:
        raw_str = pg.image.tostring(screen, "RGB", False)
        img = Image.frombytes("RGB", res, raw_str)
        oled.display(img)

    dt = clock.tick(60) / 1000
    time += dt

pg.quit()
