import os
import random
import sys

import pygame

FPS = 60


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def draw_hp(HP, x, x2, y, size=6, colour=(255, 0, 0)):
    lenn = int(((x2[0] - x) / 100) * HP)
    if size > 6:
        pygame.draw.rect(screen, colour, (x, y - size, lenn, size))
    else:
        pygame.draw.rect(screen, colour, (x, y - 10, lenn, size))


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mario.png')
weapon_image = load_image('weapon.png')
enemy_image = load_image('enemy.png')
bonus_images = load_image('heal.png')
enemy_culdown_atak = 180

tile_width = tile_height = 50


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(enemy_group, all_sprites)
        self.image = enemy_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 20, tile_height * pos_y + 20)
        self.direct = -1
        self.speed = 1
        self.HP = 100

    def update(self):
        if self.direct == 1 and not pygame.sprite.spritecollideany(self, walls_group):
            self.rect = self.rect.move(self.speed, 0)
            if pygame.sprite.spritecollideany(self, walls_group):
                self.rect = self.rect.move(-self.speed, 0)
        if self.direct == -1 and not pygame.sprite.spritecollideany(self, walls_group):
            self.rect = self.rect.move(-self.speed, 0)
            if pygame.sprite.spritecollideany(self, walls_group):
                self.rect = self.rect.move(self.speed, 0)
                self.direct = -self.direct
        # не трогать
        self.rect = self.rect.move(0, 1)
        if pygame.sprite.spritecollideany(self, walls_enemy_group):
            self.direct = -self.direct
        self.rect = self.rect.move(0, -1)
        draw_hp(self.HP, self.rect.x, self.rect.midright, self.rect.y)


class Weapon(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(weapon_group)
        self.image = weapon_image
        self.rect = self.image.get_rect().move(
            430, 112)
        self.old_direct = 0
        self.x = 388
        self.y = 188

    def update(self):
        self.revers()
        x = self.x - player.rect.midright[0]
        y = self.y - player.rect.midright[1]
        self.x = player.rect.midright[0]
        self.y = player.rect.midright[1]
        self.rect = self.rect.move(x, y)

    def revers(self):
        direkt = player.get_move_direction()
        if player.get_move_direction() == -1:
            self.image = weapon_image
            self.old_direct = direkt
            self.rect = self.image.get_rect().move(
                405, 100)
        elif player.get_move_direction() == 1:
            if self.old_direct != direkt:
                self.image = pygame.transform.flip(self.image, True, False)
            self.old_direct = direkt
            self.rect = self.image.get_rect().move(
                346, 100)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.move_direktion_left = 0
        self.move_direktion_right = 0
        self.move_direktion_up = 0
        self.move_direktion_down = 0
        self.direct = 0
        self.atak_spisok = self.get_atak()
        self.atak_long = -1
        self.atak_strick = 0
        self.run_spisok = self.get_run()
        self.run_strik = 0
        self.speed = 4
        self.jump = 0
        self.jump_spisok = self.get_jump()
        self.jump_strik = 0
        self.gravity = 1
        self.time_damage = 0
        self.HP = 100

    def update(self, update_typy="None", pos=(0, 0)):
        if update_typy == "heal" and pygame.sprite.spritecollideany(self, bonus_group):
            self.HP += 30
            if self.HP > 100:
                self.HP = self.HP - (self.HP - 100)
            for i in bonus_group:
                use_bonus(i)

        if update_typy == "move_left":
            self.move_direktion_left = 1
        if update_typy == "move_right":
            self.move_direktion_right = 1
        if update_typy == "move_not_right":
            self.move_direktion_right = 0
        if update_typy == "move_not_left":
            self.move_direktion_left = 0
        if self.move_direktion_left == 1 and self.move_direktion_right == 0:
            self.direct = -1
        elif self.move_direktion_left == 0 and self.move_direktion_right == 1:
            self.direct = 1
        if update_typy == "run":
            self.speed *= 2
        if update_typy == "run_not":
            self.speed //= 2
        if (self.move_direktion_right != 1 and self.move_direktion_left == 1) or \
                (self.move_direktion_right == 1 and self.move_direktion_left != 1):
            if self.move_direktion_right == 1 and not pygame.sprite.spritecollideany(self, walls_group) and self.atak_long < 1:
                self.rect = self.rect.move(self.speed, 0)
                if self.jump == 0:
                    if self.run_strik == 30:
                        self.run_strik = 0
                    self.image = self.run_spisok[self.run_strik // 3]
                    self.run_strik += 1
                    self.rect = self.image.get_rect().move(
                        self.rect.x, self.rect.y)
                if pygame.sprite.spritecollideany(self, walls_group):
                    self.rect = self.rect.move(-self.speed, 0)
            if self.move_direktion_left == 1 and not pygame.sprite.spritecollideany(self, walls_group) and self.atak_long < 1:
                if self.run_strik == 30:
                    self.run_strik = 0
                self.rect = self.rect.move(-self.speed, 0)
                self.image = self.run_spisok[self.run_strik // 3]
                self.image = pygame.transform.flip(self.image, True, False)
                self.run_strik += 1
                self.rect = self.image.get_rect().move(
                    self.rect.x, self.rect.y)
                if pygame.sprite.spritecollideany(self, walls_group):
                    self.rect = self.rect.move(self.speed, 0)

        if (update_typy == "ataka" or 0 <= self.atak_long != 20) and self.jump == 0 and self.gravity == 1:
            if update_typy == "ataka" and self.atak_strick != 1:
                self.atak_long = 0
                self.atak_strick = 1
            self.image = self.atak_spisok[self.atak_long // 4]
            if self.direct == -1:
                self.image = pygame.transform.flip(self.image, True, False)
            self.rect = self.image.get_rect().move(400 - (int(self.image.get_size()[0]) // 2), self.rect.y)
            self.atak_long += 1
            if self.atak_long == 20:
                self.atak_long = -1
                self.image = player_image
                if self.direct == -1:
                    self.image = pygame.transform.flip(self.image, True, False)
                self.rect = self.image.get_rect().move(
                    self.rect.x, self.rect.y)
                self.atak_strick = 0
            if self.atak_long == 13:
                for i in enemy_group:
                    enemy_atak(i)

        """if update_typy == "climb_up":
            self.move_direktion_up = 1
        if update_typy == "climb_down":
            self.move_direktion_down = 1
        if update_typy == "climb_not_up":
            self.move_direktion_up = 0
        if update_typy == "climb_not_down":
            self.move_direktion_down = 0
        if self.move_direktion_up == 1 and not pygame.sprite.spritecollideany(self, walls_group):
            self.rect = self.rect.move(0, -2)
            if pygame.sprite.spritecollideany(self, walls_group):
                self.rect = self.rect.move(0, 2)
        if self.move_direktion_down == 1 and not pygame.sprite.spritecollideany(self, walls_group):
            self.rect = self.rect.move(0, 2)
            if pygame.sprite.spritecollideany(self, walls_group):
                self.rect = self.rect.move(0, -2)"""

        if (update_typy == "jump" and self.jump_strik < 2) or self.jump != 0:
            if update_typy == "jump" and self.jump_strik < 2:
                self.jump = 25
                self.jump_strik += 1
                self.gravity = 1
            if self.jump >= 24:
                self.image = self.jump_spisok[0]
            if 24 > self.jump >= 23:
                self.image = self.jump_spisok[1]
            if 23 > self.jump >= 21:
                self.image = self.jump_spisok[2]
            if 21 > self.jump >= 8:
                self.image = self.jump_spisok[3]
            if 8 > self.jump >= 0:
                self.image = self.jump_spisok[4]
            if self.direct == -1:
                self.image = pygame.transform.flip(self.image, True, False)
            self.rect = self.image.get_rect().move(
                self.rect.x, self.rect.y)
            self.rect = self.rect.move(0, -self.jump)
            self.jump -= 1
            if pygame.sprite.spritecollideany(self, walls_group):
                self.jump = 0
                while True:
                    if not pygame.sprite.spritecollideany(self, walls_group):
                        break
                    self.rect = self.rect.move(0, 1)
        if pygame.sprite.spritecollideany(self, walls_group):
            self.jump_strik = 0

        if not pygame.sprite.spritecollideany(self, walls_group):
            if self.jump == 0 and self.gravity > 3:
                self.image = self.jump_spisok[5]
                if self.direct == -1:
                    self.image = pygame.transform.flip(self.image, True, False)
                self.rect = self.image.get_rect().move(
                    self.rect.x, self.rect.y)
            self.rect = self.rect.move(0, self.gravity)
            if self.gravity != 10:
                self.gravity += 1
            if pygame.sprite.spritecollideany(self, walls_group):
                while True:
                    if not pygame.sprite.spritecollideany(self, walls_group):
                        break
                    self.rect = self.rect.move(0, -1)
                self.gravity = 1

        if ((self.move_direktion_left == 0 and self.move_direktion_right == 0) or
            (self.move_direktion_left == 1 and self.move_direktion_right == 1)) and \
                self.run_strik >= 0 and self.atak_strick == 0 and self.jump == 0 and self.gravity == 1:
            self.image = player_image
            self.rect = self.image.get_rect().move(
                self.rect.x, self.rect.y)
            self.run_strik = 0
        while True:
            if not pygame.sprite.spritecollideany(self, walls_group):
                break
            self.rect = self.rect.move(0, -1)

        if pygame.sprite.spritecollideany(self, enemy_group) and self.time_damage == 0 and self.atak_strick == 0:
            self.HP -= 10
            self.time_damage = 180
        draw_hp(100, 0, [400, 1], 400, 20, (123, 200, 123))
        draw_hp(self.HP, 0, [400, 1], 400, 20)
        if self.time_damage > 0:
            self.time_damage -= 1

    def get_move_direction(self):
        return self.direct

    def get_atak(self):
        sp = []
        for i in range(1, 6):
            sp.append(load_image(f"atak_{i}.png"))
        return sp

    def get_jump(self):
        sp = []
        for i in range(1, 7):
            sp.append(load_image(f"jump_{i}.png"))
        return sp

    def get_run(self):
        sp = []
        for i in range(1, 11):
            sp.append(load_image(f"run_{i}.png"))
        return sp


class Wall(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(walls_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Wall_enemy(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(walls_group, walls_enemy_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Empty(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Bonus(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(bonus_group, all_sprites)
        self.image = bonus_images
        self.rect = self.image.get_rect().move(pos_x, pos_y)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - 800 // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - 400 // 2)


camera = Camera()
player = None
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
weapon_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
bonus_group = pygame.sprite.Group()
walls_enemy_group = pygame.sprite.Group()


def enemy_atak(sprite_enemy):
    if pygame.sprite.spritecollideany(sprite_enemy, player_group):
        print(player.direct)
        if player.direct == -1:
            sprite_enemy.rect.x -= 40
        elif player.direct == 1:
            sprite_enemy.rect.x += 40
        sprite_enemy.HP -= 50
    if sprite_enemy.HP < 1:
        if random.randint(0, 3) == 1:
            Bonus(sprite_enemy.rect.x, sprite_enemy.rect.y)
        sprite_enemy.rect.x -= 10000
        sprite_enemy.rect.y -= 10000


def use_bonus(bonus):
    if pygame.sprite.spritecollideany(bonus, player_group):
        bonus.rect.x -= 10000
        bonus.rect.y -= 10000


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Empty('empty', x, y)
            elif level[y][x] == '#':
                Wall('wall', x, y)
            elif level[y][x] == '@':
                Empty('empty', x, y)
                new_player = Player(x, y)
                Weapon()
            elif level[y][x] == '*':
                Empty('empty', x, y)
                Enemy(x, y)
            elif level[y][x] == '_':
                Wall_enemy('wall', x, y)
    return new_player, x, y


player, level_x, level_y = generate_level(load_level('map'))

if __name__ == '__main__':
    clock = pygame.time.Clock()
    pygame.init()
    pygame.display.set_caption('Перетаскивание')
    size = 800, 400
    screen = pygame.display.set_mode(size)
    running, moving = True, False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    player.update('ataka')
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    player.update('heal')
                if event.key == pygame.K_LEFT:
                    player.update('move_left')
                if event.key == pygame.K_RIGHT:
                    player.update('move_right')
                if event.key == pygame.K_UP:
                    player.update('climb_up')
                if event.key == pygame.K_DOWN:
                    player.update('climb_down')
                if event.key == pygame.K_LSHIFT:
                    player.update('run')
                if event.key == pygame.K_SPACE:
                    player.update('jump')
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    player.update('move_not_left')
                if event.key == pygame.K_RIGHT:
                    player.update('move_not_right')
                if event.key == pygame.K_UP:
                    player.update('climb_not_up')
                if event.key == pygame.K_DOWN:
                    player.update('climb_not_down')
                if event.key == pygame.K_LSHIFT:
                    player.update('run_not')
        screen.fill((0, 0, 0))
        camera.update(player)
        for sprite in all_sprites:
            camera.apply(sprite)
        walls_group.draw(screen)
        tiles_group.draw(screen)
        bonus_group.draw(screen)
        enemy_group.update()
        enemy_group.draw(screen)
        weapon_group.update()
        weapon_group.draw(screen)
        player.update()
        player_group.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
