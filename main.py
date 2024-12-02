import pygame
import sys
import sqlite3
import math

# --- Настройки Pygame ---
pygame.init()

# Размеры окна
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Арканоид с Авторизацией и Анимацией")

# Частота кадров
FPS = 60
clock = pygame.time.Clock()

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Шрифт
font = pygame.font.SysFont(None, 55)

# --- Подключение к SQLite ---
DB_FILE = "arkanoid.db"

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

# --- Функции работы с базой данных ---
def create_users_table():
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )
    conn.commit()

def register_user(username, password):
    try:
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def authenticate_user(username, password):
    cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    return cur.fetchone() is not None

# --- Главное меню ---
def main_menu():
    menu_running = True
    while menu_running:
        screen.fill(BLACK)
        draw_pulsating_text("Main Menu", WIDTH // 2, 100, 0.1)
        draw_pulsating_text("Press 'L' to Login", WIDTH // 2, 300, 0.05)
        draw_pulsating_text("Press 'R' to Register", WIDTH // 2, 400, 0.05)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:  # Авторизация
                    username = input_text("Enter Username:", screen, font, (100, 200))
                    password = input_text("Enter Password:", screen, font, (100, 300))
                    if authenticate_user(username, password):
                        return True
                elif event.key == pygame.K_r:  # Регистрация
                    username = input_text("Choose Username:", screen, font, (100, 200))
                    password = input_text("Choose Password:", screen, font, (100, 300))
                    register_user(username, password)
    return False

# --- Ввод текста ---
def input_text(prompt, screen, font, pos, color=pygame.Color("white")):
    text = ""
    while True:
        screen.fill(BLACK)
        prompt_surface = font.render(prompt, True, color)
        screen.blit(prompt_surface, pos)
        input_surface = font.render(text, True, color)
        screen.blit(input_surface, (pos[0], pos[1] + 50))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return text
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

# --- Анимация текста ---
def draw_pulsating_text(text, x, y, scale, color=WHITE):
    time = pygame.time.get_ticks() / 1000
    scale_factor = 1 + math.sin(time * 2) * scale
    text_surface = font.render(text, True, color)
    text_surface = pygame.transform.scale(
        text_surface,
        (int(text_surface.get_width() * scale_factor), int(text_surface.get_height() * scale_factor)),
    )
    screen.blit(text_surface, (x - text_surface.get_width() // 2, y - text_surface.get_height() // 2))

# --- Экран Game Over ---
def game_over_screen():
    while True:
        screen.fill(BLACK)
        draw_pulsating_text("Game Over", WIDTH // 2, HEIGHT // 2 - 50, 0.1, RED)
        draw_pulsating_text("Press 'R' to Restart", WIDTH // 2, HEIGHT // 2 + 50, 0.05, WHITE)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                return  # Вернуться в игровой цикл

# --- Основной игровой цикл ---
def game_loop():
    paddle_width = 100
    paddle_height = 20
    paddle_x = (WIDTH - paddle_width) // 2
    paddle_y = HEIGHT - 30
    paddle_speed = 10

    ball_radius = 10
    ball_x = WIDTH // 2
    ball_y = HEIGHT // 2
    ball_dx = 5
    ball_dy = -5

    blocks = []
    block_width = 80
    block_height = 30
    for row in range(5):
        for col in range(10):
            blocks.append(pygame.Rect(col * block_width + 10, row * block_height + 10, block_width - 2, block_height - 2))

    running = True
    move_left = False
    move_right = False

    while running:
        screen.fill(BLACK)

        # Рисуем платформу
        pygame.draw.rect(screen, WHITE, (paddle_x, paddle_y, paddle_width, paddle_height))

        # Рисуем мяч
        pygame.draw.circle(screen, RED, (ball_x, ball_y), ball_radius)

        # Рисуем блоки
        for block in blocks:
            pygame.draw.rect(screen, GREEN, block)

        # Обновляем мяч
        ball_x += ball_dx
        ball_y += ball_dy

        # Проверка столкновений
        if ball_x - ball_radius <= 0 or ball_x + ball_radius >= WIDTH:
            ball_dx *= -1
        if ball_y - ball_radius <= 0:
            ball_dy *= -1
        if ball_y + ball_radius >= HEIGHT:
            game_over_screen()
            return  # Завершить текущий игровой цикл

        # Столкновение с платформой
        if paddle_x <= ball_x <= paddle_x + paddle_width and paddle_y <= ball_y + ball_radius <= paddle_y + paddle_height:
            ball_dy *= -1

        # Столкновение с блоками
        for block in blocks[:]:
            if block.collidepoint(ball_x, ball_y):
                blocks.remove(block)
                ball_dy *= -1
                break

        # Управление платформой
        if move_left and paddle_x > 0:
            paddle_x -= paddle_speed
        if move_right and paddle_x < WIDTH - paddle_width:
            paddle_x += paddle_speed

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    move_left = True
                if event.key == pygame.K_RIGHT:
                    move_right = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    move_left = False
                if event.key == pygame.K_RIGHT:
                    move_right = False

        pygame.display.flip()
        clock.tick(FPS)

# --- Создание таблицы пользователей и запуск ---
create_users_table()
if main_menu():  # Авторизация происходит только один раз
    while True:  # Игровой цикл с возможностью перезапуска
        game_loop()

pygame.quit()
sys.exit()
