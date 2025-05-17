import math
import pygame as pg

pg.init()
pg.font.init()

FG = pg.Color("#e4e4e7")
BG = pg.Color("#18181b")
BORDER = pg.Color("#3f3f46")
ACCENT = pg.Color("#f6b300")

def lerp(a, b, t):
  return a + (b - a) * t

def clamp(value, min_value, max_value):
  return max(min_value, min(value, max_value))

apps = [
  {
    "name": "music",
    "icon": "./assets/sprites/music.png"
  },
  {
    "name": "games",
    "icon": "./assets/sprites/games.png"
  },
  {
    "name": "settings",
    "icon": "./assets/sprites/settings.png"
  },
  {
    "name": "camera",
    "icon": "./assets/sprites/camera.png"
  },
  {
    "name": "roll",
    "icon": "./assets/sprites/roll.png"
  }
]

size = (1200, 720)
window = pg.display.set_mode(size)

mono_font = pg.font.Font("./assets/fonts/SourceCodePro.ttf", 30)

clock = pg.time.Clock()
running = True
dt = 0

square_size = 100
gap = 25
padding = 40
selector_index = [0, 0]
target_pos = [0, 0]
rows = 2
cols = 3
center = False

objects = []
buttons = []

# --------- initialization ---------
for row in range(rows):
  x_offset = 0
  if row == rows - 1:
    x_offset = (cols * rows - len(apps)) * (square_size + gap) / 2

  for col in range(len(apps[math.ceil(len(apps) / rows) * row:math.ceil(len(apps) / rows) * (row + 1)])):
    rect = pg.Rect(col * (square_size + gap) + x_offset, row * (square_size + gap), square_size, square_size)
    objects.append(rect)
    buttons.append(rect)


for app in apps:
  app["image"] = pg.image.load(app["icon"])
  app["image"] = pg.transform.scale(app["image"], (square_size - padding, square_size - padding))

# --------- game loop ---------
while running:
  # input
  for event in pg.event.get():
    if event.type == pg.QUIT:
      running = False

    if event.type == pg.KEYDOWN:
      if event.key == pg.K_UP:
        selector_index[1] = clamp(selector_index[1] - 1, 0, rows - 1)
      if event.key == pg.K_DOWN:
        selector_index[1] = clamp(selector_index[1] + 1, 0, rows - 1)
        selector_index[0] = clamp(selector_index[0], 0, cols - 1 - (rows * cols - len(buttons) if selector_index[1] == rows - 1 else 0))
      if event.key == pg.K_LEFT:
        selector_index[0] = clamp(selector_index[0] - 1, 0, cols - 1)
      if event.key == pg.K_RIGHT:
        selector_index[0] = clamp(selector_index[0] + 1, 0, cols - 1 - (rows * cols - len(buttons) if selector_index[1] == rows - 1 else 0))

  # window clear
  window.fill(BG)

  for i, button in enumerate(buttons):
    pg.draw.rect(window, BORDER, button, width=6, border_radius=12)

  for i, app in enumerate(apps):
    if i < len(buttons):
      window.blit(app["image"], (buttons[i].x + padding // 2, buttons[i].y + padding // 2))

  speed = 20 * dt
  target_pos = [lerp(target_pos[0], selector_index[0] + ((x_offset / (square_size + gap)) if selector_index[1] == rows - 1 else 0), speed), lerp(target_pos[1], selector_index[1], speed)]
  pg.draw.rect(window, ACCENT, (target_pos[0] * (square_size + gap), target_pos[1] * (square_size + gap), square_size, square_size), width=6, border_radius=12)


  # draw text
  # surface = mono_font.render("hello world", True, (255, 255, 255))
  # window.blit(surface, (100, 100))

  pg.display.update()

  dt = clock.tick(60) / 1000

pg.quit()
