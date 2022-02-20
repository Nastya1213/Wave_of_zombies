import os
import sys
import numpy as np
import pygame as pg
from pygame import mixer

MONEY = 0


# функция для показа картинки
def return_screen(name):
    start_screen_background = load_image(name)
    screen.blit(start_screen_background, (0, 0))
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            # если нажали пробел, то запускаем игру
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    return  # Начинаем игру
        pg.display.flip()


# функция для прорисовки текста
def draw_text(text, x, y, font=None):
    if font is None:
        font = pg.font.Font('/data/ShadowsIntoLight-Regular.ttf', 20)
        img = font.render(text, True, (255, 79, 0))
        screen.blit(img, (x, y))
    else:
        img = font.render(text, True, (0, 5, 5))
        run.screen.blit(img, (x, y))


def load_image(name):  # Проверка фото на наличие
    filename = os.path.join('data', name)
    try:
        image = pg.image.load(filename)
    except pg.error as error:
        print('Не могу загрузить изображение:', name)
        raise SystemExit(error)
    return image


def move_player(player, movement):  # Движение персонажа
    global levelmap
    global level_y
    x, y = player.pos
    # проверка, можно ли двигаться
    if movement == 'up':
        if y > 0 and levelmap[y - 1, x] == '.':
            player.move(x, y - 1)
    elif movement == 'down':
        if y < level_y - 1 and levelmap[y + 1, x] == '.':
            player.move(x, y + 1)


# функция для загрузки уровня
def load_level(filename):
    filename = os.path.join('data', filename)
    with open(filename, 'r') as mapfile:
        levelmap = np.array([list(i) for i in [line.strip() for line in mapfile]])
    return levelmap


# разрезание листа с картинками на отдельные кадры
def animasprite(sheet, cols, rows):
    frames = []
    rect = pg.Rect(0, 0, sheet.get_width() // cols, sheet.get_height() // rows)
    for j in range(rows):
        for i in range(cols):
            frame_location = (rect.w * i, rect.h * j)
            frames.append(sheet.subsurface(pg.Rect(frame_location, rect.size)))
    return frames


def generate_level(level):
    # элементы игрового поля
    data_lst = list()
    row, col = level.shape
    for y in range(row):
        for x in range(col):
            if level[y, x] == '/':
                data_lst.append(Tile('dirt', x, y))
            elif level[y, x] == '#':
                data_lst.append(Tile('wall', x, y))
            elif level[y, x] == 'p':
                p = Portal(x, y)
                run.portal_group.add(p)
                run.all_sprites.add(p)
            elif level[y, x] == 'c':
                c = Coin(x, y)
                run.all_sprites.add(c)
                run.coin_group.add(c)
            elif level[y, x] == 'l':
                lava_block = Lava(x, y)
                run.lava_group.add(lava_block)
                run.all_sprites.add(lava_block)
            elif level[y, x] == 'f':
                data_lst.append(Tile('lava_fill', x, y))
            elif level[y, x] == 'b':
                bmb = Bomb(x, y)
                run.bombs.add(bmb)
                run.all_sprites.add(bmb)
            elif level[y, x] == 'm':
                m = Man(x, y)
                run.men_group.add(m)
                run.all_sprites.add(m)
            elif level[y, x] == 'a':
                a = Car(x, y)
                run.autos_group.add(a)
                run.all_sprites.add(a)
    return data_lst


class Portal(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        pg.sprite.Sprite.__init__(self)
        self.image = load_image('portal.png')
        self.rect = self.image.get_rect().move(pos_x * run.tile_width,
                                               (pos_y * run.tile_height) - 400)


class Tile(pg.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__()
        self.image = run.tile_images[tile_type]
        self.rect = self.image.get_rect().move(run.tile_width * pos_x,
                                               run.tile_height * pos_y)
        self.abs_pos = (self.rect.x, self.rect.y)
        self.out()

    def out(self):
        return self.abs_pos[0], self.abs_pos[1], 70, 70


class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.x + int(run.width / 2.2)
        y = -target.rect.y + int(run.height / 2.2)
        # лимит
        x = min(0, x)  # лево
        y = min(0, y)  # верх
        self.camera = pg.Rect(x, y, self.width, self.height)


class Player(pg.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.reset(game)

    def reset(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        # спрайт игрока
        self.stand = load_image('stand.png')
        self.image = load_image('stand.png')
        self.rect = pg.rect.Rect((5, 880), (70, 148))
        self.on_ground = False
        # трение
        self.friction = -0.12
        # скорость передвижения игрока
        self.vel = vec(0, 0)
        # ускорение
        self.acc = vec(0, 0)
        # переменные для анимации, списки с кадрами
        self.walking = False
        self.walk_r_lst = animasprite(load_image('walk.png'), 4, 1)
        self.walk_l_lst = list()
        for frame in self.walk_r_lst:
            self.walk_l_lst.append(pg.transform.flip(frame, True, False))
        # счетчик кадров
        self.current_frame = 0
        self.last_update = 0

    def jump(self):
        # проверка, стоит ли игрок на поверхности
        if self.on_ground:
            self.vel.y = -21

    def update(self):
        self.animate()
        self.acc = vec(0, 0.7)
        # считывание нажатий кнопок передвижения
        if self.game.game_over == 0:
            key = pg.key.get_pressed()
            self.acc.x = 0.7
            if key[pg.K_SPACE]:
                if self.on_ground:
                    self.game.jump_fx.play()
                self.jump()
            # обновление координат игрока, применение трения
            self.acc.x += self.vel.x * self.friction
            # выравнивание скорости + инерция
            self.vel.x += self.acc.x
            if abs(self.vel.x) < 0.1:
                self.vel.x = 0
            if not self.on_ground:
                self.vel.y += self.acc.y
            self.on_ground = False
            self.rect.y += self.vel.y + 0.5 * self.acc.y
            self.collide(0, self.vel.y)
            self.rect.x += self.vel.x + 0.5 * self.acc.x
            self.collide(self.vel.x, 0)
        elif self.game.game_over == 1:
            return_screen('overGame.png')

    def collide(self, xvel, yvel):
        for tile in self.game.tiles_group:
            if pg.sprite.collide_rect(self, tile):
                if xvel > 0:
                    self.rect.right = tile.rect.left
                if xvel < 0:
                    self.rect.left = tile.rect.right
                if yvel < 0:
                    self.rect.top = tile.rect.bottom
                    self.vel.y = 0
                if yvel > 0:
                    self.rect.bottom = tile.rect.top
                    self.vel.y = 0
                    self.on_ground = True
                # столкновение с бомбой
                if pg.sprite.spritecollide(self, self.game.bombs, True):
                    # self.game.bomb.kill()
                    self.game.countmozg -= 1
                    self.game.boom_fx.play()
                    if self.game.countmozg == 0:
                        self.game.game_over = 1
                        self.game.game_over_fx.play()
                # столкновение с лавой
                if pg.sprite.spritecollide(self, self.game.lava_group, False):
                    self.game.game_over = 1
                    if self.game.countmozg == 0:
                        self.game.game_over = 1
                        self.game.game_over_fx.play()

    def animate(self):
        current = pg.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False
        # анимация ходьбы
        if self.walking:
            if current - self.last_update > 190:
                self.last_update = current
                self.current_frame = (self.current_frame + 1) % len(self.walk_r_lst)
                if self.vel.x > 0:
                    self.image = self.walk_r_lst[self.current_frame]
                else:
                    self.image = self.walk_l_lst[self.current_frame]
        if not self.walking:
            self.image = self.stand


class Bomb(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        pg.sprite.Sprite.__init__(self)
        self.image = load_image('bomb.png')
        self.rect = self.image.get_rect().move(run.tile_width * pos_x,
                                               (run.tile_height * pos_y) + 20)
        # счетчик кадров
        self.current_frame = 0
        self.last_update = 0


class Coin(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        pg.sprite.Sprite.__init__(self)
        self.image = load_image('coin1.png')
        self.rect = self.image.get_rect().move(run.tile_width * pos_x,
                                               (run.tile_height * pos_y))
        self.animation = animasprite(load_image('coin.png'), 4, 1)
        self.current_frame = 0
        self.last_update = 0

    def update(self):
        current = pg.time.get_ticks()
        if current - self.last_update > 300:
            self.last_update = current
            self.current_frame = (self.current_frame + 1) % len(self.animation)
            self.image = self.animation[self.current_frame]


class Lava(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        pg.sprite.Sprite.__init__(self)
        self.image = load_image('lava.png')
        self.rect = self.image.get_rect().move(run.tile_width * pos_x,
                                               (run.tile_height * pos_y))
        self.animation = animasprite(load_image('lava_move.png'), 2, 1)
        self.current_frame = 0
        self.last_update = 0

    def update(self):
        current = pg.time.get_ticks()
        if current - self.last_update > 1300:
            self.last_update = current
            self.current_frame = (self.current_frame + 1) % len(self.animation)
            self.image = self.animation[self.current_frame]


# вектор
vec = pg.math.Vector2


class Game:
    def __init__(self):
        self.running = True
        pg.init()
        pg.mixer.pre_init(44100, -16, 2, 512)
        mixer.init()
        # параметры для draw_text
        self.font = pg.font.SysFont('Comic Sans', 35)
        pg.display.set_caption('Wave of zombies')
        size = self.width, self.height = 1280, 720
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode(size)
        self.fps = 60
        self.background, self.background_rect = load_image('background.png'), \
                                                load_image('background.png').get_rect()

    def new(self):
        # Тайлы
        self.tile_images = {
            'wall': load_image('grass.png'),
            'dirt': load_image('dark_dirt.png'),
            'lava_fill': load_image('lava_fill.png')}
        # размер тайлов:
        self.tile_width = self.tile_height = 70
        # кнопки
        # self.restart_button = Button('try_unpressed.png', 'try_pressed.png')
        self.restart_check = False
        # Группы:
        self.tiles_group = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group()
        self.lava_group = pg.sprite.Group()
        self.coin_group = pg.sprite.Group()
        self.bombs = pg.sprite.Group()
        self.autos_group = pg.sprite.Group()
        self.men_group = pg.sprite.Group()
        self.portal_group = pg.sprite.Group()
        # музыка
        try:
            # сбор монеток
            self.coin_fx = pg.mixer.Sound('data/coin_pick.mp3')
            # прыжок
            self.jump_fx = pg.mixer.Sound('data/jump.mp3')
            # проигрыш
            self.game_over_fx = pg.mixer.Sound('data/boom.mp3')
            # взрыв бомбы
            self.boom_fx = pg.mixer.Sound('data/boom.mp3')
            # победа
            self.portal_fx = pg.mixer.Sound('data/portal.mp3')
            # фоновая музыка
            pg.mixer.music.load('data/Bowling.mp3')
        except:
            self.coin_fx = pg.mixer.Sound('data/coin_pick.wav')
            self.jump_fx = pg.mixer.Sound('data/jump.wav')
            self.boom_fx = pg.mixer.Sound('data/boom.wav')
            self.game_over_fx = pg.mixer.Sound('data/boom.wav')
            self.portal_fx = pg.mixer.Sound('data/portal.wav')
            pg.mixer.music.load('data/Bowling.wav')
        self.coin_fx.set_volume(0.6)
        self.jump_fx.set_volume(0.05)
        self.game_over_fx.set_volume(0.8)
        self.boom_fx.set_volume(0.3)
        self.portal_fx.set_volume(0.5)
        pg.mixer.music.set_volume(0.4)
        pg.mixer.music.play(-1, 0.0)
        # генерация уровня
        self.levelmap = load_level('level_1.map')
        data_lst = generate_level(self.levelmap)
        # помещение тайлов в группы
        for tile in data_lst:
            self.all_sprites.add(tile)
            self.tiles_group.add(tile)
        # камера
        self.camera = Camera(len(self.levelmap), len(self.levelmap[0]))
        # переменная для проверки проигрыша, счёт
        self.score = 0
        self.countmozg = 1
        self.game_over = 0
        # спавн игрока с референсом к классу Game
        self.player = Player(self)
        self.all_sprites.add(self.player)
        self.run()

    def run(self):
        self.running = True
        while self.running:
            self.playing = True
            while self.playing:
                self.clock.tick(self.fps)
                self.events()
                self.update()
                self.draw()

    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)

    def events(self):
        # цикл с событиями
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                self.restart_check = True
            else:
                self.restart_check = False
            if pg.Rect.colliderect(self.player.rect, (9630, 750, 150, 100)):
                self.playing = False
                self.running = False
                return_screen('end_level.png')
                pg.display.set_caption('Wave of zombies')

    def draw(self):
        # прорисовка всего
        self.screen.blit(self.background, self.background_rect)
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        # проверка столкновенния с монетами, обновление счетчика
        if pg.sprite.spritecollide(self.player, self.coin_group, True):
            self.coin_fx.play()
            self.score += 1
            global MONEY
            MONEY += 1
            # db.set('money', db.get('money') + 1)
        if pg.sprite.spritecollide(self.player, self.autos_group, True):
            if self.countmozg >= 4:
                self.countmozg += 1
        # проверка столкновенния с людьми
        if pg.sprite.spritecollide(self.player, self.men_group, True):
            self.countmozg += 1
            # self.coin_fx.play()
        if pg.sprite.spritecollide(self.player, self.portal_group, False):
            self.portal_fx.play()
            return_screen('win.png')
            return_screen('end.png')

        draw_text(f'zombiecoins:  {self.score}', 12, 10, self.font)
        draw_text(f'brains:  {str(self.countmozg)}', 12, 30, self.font)
        # рестарт
        if self.game_over == 1:
            return_screen('overGame.png')
            key = pg.key.get_pressed()
            if key[pg.K_SPACE]:
                self.player.reset(self)
                self.game_over = 0
        pg.display.flip()


class Car(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        pg.sprite.Sprite.__init__(self)
        self.image = load_image('car.png')
        self.rect = self.image.get_rect().move(run.tile_width * pos_x,
                                               (run.tile_height * pos_y) - 20)


class Man(pg.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        pg.sprite.Sprite.__init__(self)
        self.image = load_image('man.png')
        self.rect = self.image.get_rect().move(run.tile_width * pos_x,
                                               (run.tile_height * pos_y))
        self.animation = animasprite(load_image('men.png'), 4, 1)
        self.current_frame = 0
        self.last_update = 0

    def update(self):
        current = pg.time.get_ticks()
        if current - self.last_update > 1300:
            self.last_update = current
            self.current_frame = (self.current_frame + 1) % len(self.animation)
            self.image = self.animation[self.current_frame]


def terminate():
    pg.quit()
    sys.exit()


if __name__ == '__main__':
    pg.init()
    pg.display.set_caption('Wave of Zombies')
    size = width, height = 1280, 720
    screen = pg.display.set_mode(size)
    # включаем музыку
    pg.mixer.pre_init(44100, -16, 2, 512)
    mixer.init()
    try:
        pg.mixer.music.load('data/Grasswalk.mp3')
    except:
        pg.mixer.music.load('data/Grasswalk.wav')
    pg.mixer.music.set_volume(0.4)
    pg.mixer.music.play(-1, 0.0)
    return_screen('start-screen.png')
    icon = load_image('mozg.png')
    pg.display.set_icon(icon)
    return_screen('story.png')
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            run = Game()
            while run.running:
                run.new()

        pg.display.flip()
    terminate()
