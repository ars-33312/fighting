import pygame
from pygame import *
import os
import random
import sys

pygame.init()
mixer.init()

# ---------- Параметри вікна ----------
win_width = 1730
win_height = 1000
window = display.set_mode((win_width, win_height))
display.set_caption("Menu")
clock = time.Clock()
FPS = 60

# ---------- Завантаження ресурсів ----------
background = transform.scale(image.load("background2.png"), (win_width, win_height))
logo_image = transform.scale(image.load("ui/logo.png"), (600, 400))
play_button_image = transform.scale(image.load("ui/play_button.png"), (300, 120))
exit_button_image = transform.scale(image.load("ui/exit_button.png"), (300, 120))
music_on_image = transform.scale(image.load("ui/music_on.png"), (60, 60))
music_off_image = transform.scale(image.load("ui/music_off.png"), (60, 60))
easy_btn = transform.scale(image.load("ui/easy.jpeg"), (250, 80))
medium_btn = transform.scale(image.load("ui/medium.jpeg"), (250, 80))
hard_btn = transform.scale(image.load("ui/hard.jpeg"), (250, 80))

# ---------- Музика ----------
mixer.music.load("music.mp3")
mixer.music.set_volume(0.3)
mixer.music.play(-1)
music_on = True

# ---------- Класи для кнопок ----------
class Button:
    def __init__(self, image, pos):
        self.image = image
        self.rect = self.image.get_rect(center=pos)

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

# ---------- Створення кнопок ----------
play_button = Button(play_button_image, (win_width // 2, 570))
exit_button = Button(exit_button_image, (win_width // 2, 700))
music_button = Button(music_on_image, (win_width - 80, 20))

easy_button = Button(easy_btn, (win_width // 2, 550))
medium_button = Button(medium_btn, (win_width // 2, 650))
hard_button = Button(hard_btn, (win_width // 2, 750))

# ---------- Стан меню ----------
game_started = False
difficulty_selected = False
difficulty = 1  # 1 - easy, 2 - medium, 3 - hard
def get_difficulty_settings(diff_level):
    if diff_level == 1:  # easy
        return {"player_hp": 150, "player_damage": 20, "enemy_count": 2}
    elif diff_level == 2:  # medium
        return {"player_hp": 100, "player_damage": 15, "enemy_count": 3}
    elif diff_level == 3:  # hard
        return {"player_hp": 70, "player_damage": 10, "enemy_count": 4}

# ---------- Функція меню ----------
def show_main_menu():
    global game_started, music_on
    while not game_started:
        window.blit(background, (0, 0))
        window.blit(logo_image, (win_width // 2 - logo_image.get_width() // 2, 100))
        play_button.draw(window)
        exit_button.draw(window)
        music_button.draw(window)
        display.update()
        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit()
                sys.exit()
            if e.type == MOUSEBUTTONDOWN:
                if play_button.is_clicked(e.pos):
                    return "difficulty"
                if exit_button.is_clicked(e.pos):
                    pygame.quit()
                    sys.exit()
                if music_button.is_clicked(e.pos):
                    music_on = not music_on
                    if music_on:
                        mixer.music.play(-1)
                        music_button.image = music_on_image
                    else:
                        mixer.music.stop()
                        music_button.image = music_off_image
        clock.tick(FPS)

def show_difficulty_menu():
    global difficulty, game_started
    selecting = True
    while selecting:
        window.blit(background, (0, 0))
        window.blit(logo_image, (win_width // 2 - logo_image.get_width() // 2, 100))
        easy_button.draw(window)
        medium_button.draw(window)
        hard_button.draw(window)
        music_button.draw(window)
        display.update()
        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit()
                sys.exit()
            if e.type == MOUSEBUTTONDOWN:
                if easy_button.is_clicked(e.pos):
                    difficulty = 1
                    game_started = True
                    selecting = False
                elif medium_button.is_clicked(e.pos):
                    difficulty = 2
                    game_started = True
                    selecting = False
                elif hard_button.is_clicked(e.pos):
                    difficulty = 3
                    game_started = True
                    selecting = False
                elif music_button.is_clicked(e.pos):
                    global music_on
                    music_on = not music_on
                    if music_on:
                        mixer.music.play(-1)
                        music_button.image = music_on_image
                    else:
                        mixer.music.stop()
                        music_button.image = music_off_image
        clock.tick(FPS)

# ---------- Запуск меню ----------
next_step = show_main_menu()
if next_step == "difficulty":
    show_difficulty_menu()

win_width = 1730
win_height = 1000
window = display.set_mode((win_width, win_height))
display.set_caption("Curse of the Abyss")
background = transform.scale(image.load("background1.png"), (win_width, win_height))
clock = time.Clock()
FPS = 60
game_over = False

# ---------- Звук удару ----------
mixer.init()
hit_sound = mixer.Sound("hit.wav")

# ---------- Додаткові змінні ----------
ground_y = 650
round_number = 1
enemies = []
arrows = []

# ---------- Клас GameSprite ----------
class GameSprite(sprite.Sprite):
    def __init__(self, player_image, size_x, size_y, x, y):
        super().__init__()
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

# ---------- Клас Player ----------
class Player(GameSprite):
    def __init__(self, size_x, size_y, x, y, speed):
        super().__init__("sprites/idle/idle1.png", size_x, size_y, x, y)
        self.speed = speed
        self.direction = "right"
        self.animations = {
            "idle": self.load_animation("idle", 7),
            "walk": self.load_animation("walk", 8),
            "jump": self.load_animation("jump", 6),
            "attack": self.load_animation("attack", 5),
            "dead": self.load_animation("dead", 6),
            "block": self.load_animation("block", 4),
        }
        self.state = "idle"
        self.frame = 0
        self.animation_speed = 0.2
        self.attacking = False
        self.blocking = False
        self.health = 100
        self.max_health = 100
        self.dead = False

    def load_animation(self, folder, count):
        frames = []
        for i in range(1, count + 1):
            path = os.path.join("sprites", folder, f"{folder}{i}.png")
            if os.path.exists(path):
                img = transform.scale(image.load(path), (self.rect.width, self.rect.height))
                frames.append(img)
        return frames

    def set_state(self, new_state):
        if self.dead and new_state != "dead":
            return
        if self.attacking and new_state != "attack":
            return
        if self.blocking and new_state != "block":
            return
        if self.state != new_state:
            self.state = new_state
            self.frame = 0

    def update(self):
        frames = self.animations[self.state]
        if frames:
            if self.state == "dead":
                if self.frame < len(frames) - 1:
                    self.frame += self.animation_speed
                current_frame = frames[int(min(self.frame, len(frames) - 1))]
            else:
                self.frame += self.animation_speed
                if self.frame >= len(frames):
                    self.frame = 0
                    if self.state == "attack":
                        self.attacking = False
                        self.set_state("idle")
                current_frame = frames[int(self.frame)]
            if self.direction == "left":
                self.image = transform.flip(current_frame, True, False)
            else:
                self.image = current_frame

    def draw_health_bar(self):
        bar_width = 400
        bar_height = 35
        x = 20
        y = 20
        fill = (self.health / self.max_health) * bar_width
        outline_rect = Rect(x, y, bar_width, bar_height)
        fill_rect = Rect(x, y, fill, bar_height)
        draw.rect(window, (0, 200, 0), fill_rect)
        draw.rect(window, (255, 255, 255), outline_rect, 3)

# ---------- Клас Enemy ----------
class Enemy(GameSprite):
    def __init__(self, size_x, size_y, x, y, speed):
        super().__init__("sprites/enemy_idle/enemy_idle1.png", size_x, size_y, x, y)
        self.speed = speed
        self.direction = "left"
        self.animations = {
            "idle": self.load_animation("enemy_idle", 7),
            "walk": self.load_animation("enemy_walk", 7),
            "attack": self.load_animation("enemy_attack", 6),
            "dead": self.load_animation("enemy_dead", 4),
        }
        self.state = "idle"
        self.frame = 0
        self.animation_speed = 0.2
        self.health = 100
        self.max_health = 100
        self.dead = False
        self.remove_after_death = False
        self.attack_cooldown = 0

    def load_animation(self, folder, count):
        frames = []
        for i in range(1, count + 1):
            path = os.path.join("sprites", folder, f"{folder}{i}.png")
            if os.path.exists(path):
                img = transform.scale(image.load(path), (self.rect.width, self.rect.height))
                frames.append(img)
        return frames

    def set_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
            self.frame = 0

    def update(self):
        if self.dead and self.remove_after_death:
            return
        frames = self.animations[self.state]
        if frames:
            self.frame += self.animation_speed
            if self.frame >= len(frames):
                if self.state == "dead":
                    self.remove_after_death = True
                    return
                self.frame = 0
            current_frame = frames[int(self.frame)]
            self.image = transform.flip(current_frame, True, False) if self.direction == "left" else current_frame
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def draw_health_bar(self):
        if self.dead:
            return
        bar_width = 200
        bar_height = 20
        fill = (self.health / self.max_health) * bar_width
        outline_rect = Rect(self.rect.x + 20, self.rect.y - 15, bar_width, bar_height)
        fill_rect = Rect(self.rect.x + 20, self.rect.y - 15, fill, bar_height)
        draw.rect(window, (200, 0, 0), fill_rect)
        draw.rect(window, (255, 255, 255), outline_rect, 2)

# ---------- Клас ArcherEnemy ----------
class ArcherEnemy(Enemy):
    def __init__(self, size_x, size_y, x, y, speed):
        super().__init__(size_x, size_y, x, y, speed)
        self.animations = {
            "idle": self.load_animation("archer_idle", 7),
            "walk": self.load_animation("archer_walk", 8),
            "attack": self.load_animation("archer_attack", 15),
            "dead": self.load_animation("archer_dead", 5),
        }
        self.last_shot_frame = -1
        self.shoot_cooldown = 0

    def update(self):
        if self.dead and self.remove_after_death:
            return

        # Визначення напрямку в залежності від положення героя
        if hero.rect.centerx < self.rect.centerx:
            self.direction = "left"
        else:
            self.direction = "right"

        distance = abs(hero.rect.centerx - self.rect.centerx)

        if not self.dead:
            if distance < 800:
                self.set_state("attack")
                if int(self.frame) == 7 and self.last_shot_frame != 7:
                    self.shoot_arrow()
                    self.last_shot_frame = 7
            else:
                self.set_state("walk")
                if self.rect.x > hero.rect.x:
                    self.rect.x -= self.speed
                else:
                    self.rect.x += self.speed

        # Анімація
        frames = self.animations[self.state]
        if frames:
            self.frame += self.animation_speed
            if self.frame >= len(frames):
                if self.state == "dead":
                    self.remove_after_death = True
                    return
                self.frame = 0
                if self.state == "attack":
                    self.last_shot_frame = -1  # Скидаємо після повного циклу атаки

            current_frame = frames[int(self.frame)]
            self.image = transform.flip(current_frame, True, False) if self.direction == "left" else current_frame

    def shoot_arrow(self):
        print("Стріла випущена!")  # ← додай цю строку
        direction = -15 if self.rect.centerx > hero.rect.centerx else 15
        arrow = Arrow(self.rect.centerx, self.rect.y + self.rect.height - 50, direction)
        arrows.append(arrow)

# ---------- Клас Arrow ----------
class Arrow:
    def __init__(self, x, y, speed):
        self.image = transform.scale(image.load("sprites/arrow/arrow.png"), (60, 20))
        if speed < 0:
            self.image = transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.x += self.speed

    def draw(self):
        window.blit(self.image, self.rect.topleft)

# ---------- Функція спавну ворогів ----------

def spawn_enemies(round_num):
    new_enemies = []
    for i in range(settings["enemy_count"]):
        x = random.randint(1000, 1600)
        if i % 2 == 0:
            new_enemies.append(Enemy(300, 300, x, ground_y, 3))
        else:
            new_enemies.append(ArcherEnemy(300, 300, x, ground_y, 2))
    return new_enemies

# ---------- Функція перевірки завершення раунду ----------
def check_round_end():
    global round_number, enemies
    if all(e.dead and e.remove_after_death for e in enemies):
        round_number += 1
        enemies = spawn_enemies(round_number)

def display_message(message):
    font = pygame.font.Font(None, 100)
    text = font.render(message, True, (255, 0, 0))  # Червоний колір
    window.blit(text, (win_width // 2 - text.get_width() // 2, win_height // 2 - text.get_height() // 2))
    display.update()


# ---------- Ігрові об’єкти ----------
hero = Player(300, 300, 100, ground_y, 5)
settings = get_difficulty_settings(difficulty)
hero.health = settings["player_hp"]
hero.max_health = settings["player_hp"]
enemies = spawn_enemies(round_number)

# ---------- Управління ----------
moving_left = False
moving_right = False
velocity_y = 0
gravity = 0.5
jump_strength = -10
on_ground = False
blocking = False

font.init()
game_font = font.Font(None, 70)

# ---------- Ігровий цикл ----------
run = True
while run:
    for i in event.get():
        if i.type == QUIT:
            run = False
        elif i.type == KEYDOWN:
            if i.key == K_SPACE and on_ground and not hero.dead:
                velocity_y = jump_strength
                on_ground = False
            if i.key == K_a and not hero.dead:
                moving_left = True
                hero.direction = "left"
            if i.key == K_d and not hero.dead:
                moving_right = True
                hero.direction = "right"
            if i.key == K_j and not hero.attacking and not hero.dead and not blocking:
                hero.attacking = True
                hero.set_state("attack")
                for enemy in enemies:
                    if enemy.rect.colliderect(hero.rect) and not enemy.dead:
                        enemy.health -= settings["player_damage"]
                        hit_sound.play()
                        if enemy.health <= 0:
                            enemy.set_state("dead")
                            enemy.dead = True
            if i.key == K_f and not hero.dead:
                blocking = True
                hero.set_state("block")
        elif i.type == KEYUP:
            if i.key == K_a:
                moving_left = False
            if i.key == K_d:
                moving_right = False
            if i.key == K_f:
                blocking = False

    # Оновлення гравця
    if not hero.dead:
        if moving_left:
            hero.rect.x -= hero.speed
        if moving_right:
            hero.rect.x += hero.speed
        velocity_y += gravity
        hero.rect.y += velocity_y
        if hero.rect.y >= ground_y:
            hero.rect.y = ground_y
            velocity_y = 0
            on_ground = True
        else:
            on_ground = False

        if not on_ground:
            hero.set_state("jump")
        elif blocking:
            hero.set_state("block")
        elif moving_left or moving_right:
            hero.set_state("walk")
        elif not hero.attacking:
            hero.set_state("idle")

    # Оновлення ворогів
    for enemy in enemies:
        if isinstance(enemy, Enemy) and not isinstance(enemy, ArcherEnemy):
            if not enemy.dead:
                if abs(hero.rect.centerx - enemy.rect.centerx) < 100:
                    enemy.set_state("attack")
                    if 2 <= enemy.frame < 2.5 and enemy.attack_cooldown == 0:
                        if hero.rect.colliderect(enemy.rect):
                            if not blocking:
                                hero.health -= 5
                            enemy.attack_cooldown = 30
                            if hero.health <= 0:
                                hero.set_state("dead")
                                hero.dead = True
                else:
                    enemy.set_state("walk")
                    if enemy.rect.x > hero.rect.x:
                        enemy.rect.x -= enemy.speed
                        enemy.direction = "left"
                    elif enemy.rect.x < hero.rect.x:
                        enemy.rect.x += enemy.speed
                        enemy.direction = "right"
        enemy.update()

    # Оновлення стріл
    for arrow in arrows[:]:
        arrow.update()
        if arrow.rect.colliderect(hero.rect) and not hero.dead:
            if not blocking:
                hero.health -= 7
                hit_sound.play()
                if hero.health <= 0:
                    hero.set_state("dead")
                    hero.dead = True
            arrows.remove(arrow)
        elif arrow.rect.x < 0 or arrow.rect.x > win_width:
            arrows.remove(arrow)

    check_round_end()

    # Перевірка на перемогу (якщо пройдено 5 раундів)
    if round_number > 5 and not game_over:
        game_over = True
        display_message("YOU WIN")
        pygame.time.delay(3000)  # Затримка на 3 секунди
        quit()
        sys.exit()


    # Перевірка на поразку (якщо герой мертвий)
    if hero.dead and not game_over:
        game_over = True
        display_message("YOU LOSE")
        pygame.time.delay(3000)  # Затримка на 3 секунди
        quit()
        sys.exit()


    # Малювання
    window.blit(background, (0, 0))
    hero.update()
    hero.reset()
    hero.draw_health_bar()
    for enemy in enemies:
        if not enemy.remove_after_death:
            enemy.reset()
            enemy.draw_health_bar()
    for arrow in arrows:
        arrow.draw()

    round_text = game_font.render(f"Раунд: {round_number}", True, (240, 240, 240))
    window.blit(round_text, (20, 70))

    display.update()
    clock.tick(FPS)