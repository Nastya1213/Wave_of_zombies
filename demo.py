import os
import sys
import pygame as pg
from pygame import time


def load_image(name):
    """Функция загрузки изображения из файла"""
    filename = os.path.join('data', name)
    try:
        image = pg.image.load(filename)
    except pg.error as error:
        print('Не могу загрузить изображение:', name)
        raise SystemExit(error)
    return image


def start_screen():
    """Стартовое окно"""
    start_screen_background = load_image('fon1.jpeg')
    screen.blit(start_screen_background, (0, 0))

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            elif event.type == pg.KEYDOWN or event.type == pg.MOUSEBUTTONDOWN:
                return
        pg.display.flip()


def terminate():
    """Выход из игры"""
    pg.quit()
    sys.exit()


if __name__ == '__main__':
    pg.init()
    pg.display.set_caption('Wave of Zombies')
    icon = load_image('mozg.png')
    pg.display.set_icon(icon)
    size = width, height = 1280, 720
    screen = pg.display.set_mode(size)

    start_screen()

    pg.key.set_repeat(200, 70)

    fps = 60
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        screen.fill(pg.Color('black'))
        menu = load_image('menu.png')
        screen.blit(menu, (0, 0))
        pg.display.flip()
        time.Clock().tick(fps)
    terminate()
