import os
import sys
import numpy as np
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
    # Выводим изображение заставки:
    start_screen_background = load_image('fon1.jpeg')
    screen.blit(start_screen_background, (0, 0))
    # Выводим текст заставки:
    font = pg.font.Font(None, 30)
    text_coord = 10
    # Главный игровой цикл для окна заставки:
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            elif event.type == pg.KEYDOWN or event.type == pg.MOUSEBUTTONDOWN:
                return  # Начинаем игру
        pg.display.flip()



def terminate():
    """Выход из игры"""
    # Определяем отдельную функцию выхода из игры,
    # чтобы ею можно было воспользоваться,
    # как при закрытии игрового окна,
    # так и при закрытии окна заставки:
    pg.quit()
    sys.exit()


class Menu():
    pass


if __name__ == '__main__':
    pg.init()
    pg.display.set_caption('Wave of Zombies')
    img = pg.image.load('/home/nastya/code/waveOfZombies/data/mozg.png')
    pg.display.set_icon(img)
    size = width, height = 1280, 720
    screen = pg.display.set_mode(size)

    # Выводим заставку игры:
    start_screen()

    # Задаём задержку автоповторения нажатой клавиши:
    pg.key.set_repeat(200, 70)

    # Главный игровой цикл:
    fps = 60
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        screen.fill(pg.Color('black'))
        pg.display.flip()
        time.Clock().tick(fps)
    terminate()
