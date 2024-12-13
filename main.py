import pygame
import sys
import sqlite3
import random

# --- Настройки Pygame ---
pygame.init()

# Размеры окна
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arkanoid")

# Частота кадров
FPS = 60
clock = pygame.time.Clock()

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)

# --- Шрифт ---
font = pygame.font.SysFont(None, 40)

# --- Подключение к базе данных SQLite ---
DB_FILE = "arkanoid.db"
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

# --- Работа с базой данных ---
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

# --- Функции для интерфейса ---
def input_text(prompt, screen, font, pos, color=WHITE, password=False):
    """Получение ввода текста. Если password=True, то ввод отображается как звездочки."""
    text = ""
    while True:
        screen.fill(BLACK)
        prompt_surface = font.render(prompt, True, color)
        screen.blit(prompt_surface, pos)

        display_text = text if not password else '*' * len(text)
        input_surface = font.render(display_text, True, color)
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

def draw_button(text, x, y, width, height, color, text_color, font, screen):
    """Отрисовка кнопок."""
    button_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, color, button_rect, border_radius=5)
    text_surface = font.render(text, True, text_color)
    screen.blit(text_surface, (x + (width - text_surface.get_width()) // 2, y + (height - text_surface.get_height()) // 2))
    return button_rect

def pause_menu():
    """Меню паузы."""
    while True:
        screen.fill(BLACK)
        continue_button = draw_button("Continue", WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50, GREEN, WHITE, font, screen)
        exit_button = draw_button("Exit", WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50, RED, WHITE, font, screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if continue_button.collidepoint(mouse_pos):
                    return
                elif exit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

def game_over_menu():
    """Окно Game Over."""
    while True:
        screen.fill(BLACK)
        game_over_text = font.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))

        retry_button = draw_button("Retry", WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 50, GREEN, WHITE, font, screen)
        exit_button = draw_button("Exit", WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50, RED, WHITE, font, screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if retry_button.collidepoint(mouse_pos):
                    return True
                elif exit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

def main_menu():
    """Главное меню."""
    while True:
        screen.fill(BLACK)
        login_button = draw_button("Login", 300, 200, 200, 50, BLUE, WHITE, font, screen)
        register_button = draw_button("Register", 300, 300, 200, 50, GREEN, WHITE, font, screen)
        play_button = draw_button("Play as Guest", 300, 400, 200, 50, WHITE, BLACK, font, screen)
        exit_button = draw_button("Exit", 300, 500, 200, 50, RED, WHITE, font, screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if login_button.collidepoint(mouse_pos):
                    username = input_text("Enter Username:", screen, font, (100, 200))
                    password = input_text("Enter Password:", screen, font, (100, 300), password=True)
                    if authenticate_user(username, password):
                        return username
                elif register_button.collidepoint(mouse_pos):
                    username = input_text("Choose Username:", screen, font, (100, 200))
                    password = input_text("Choose Password:", screen, font, (100, 300), password=True)
                    if register_user(username, password):
                        message = "Registration Successful!"
                    else:
                        message = "Username already exists!"
                    prompt = font.render(message, True, GREEN)
                    screen.blit(prompt, (300, 400))
                    pygame.display.flip()
                    pygame.time.delay(2000)
                elif play_button.collidepoint(mouse_pos):
                    return None
                elif exit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

# --- Основной игровой процесс ---
def reset_game():
    """Сбросить параметры игры."""
    ball_x, ball_y = WIDTH // 2, HEIGHT // 2
    ball_dx, ball_dy = 5, -5
    ball_radius = 10

    paddle_width, paddle_height = 100, 20
    paddle_x, paddle_y = (WIDTH - paddle_width) // 2, HEIGHT - 40
    paddle_speed = 10

    blocks = []
    indestructible_blocks = []
    bonuses = []
    block_width, block_height = 80, 30

    # Генерация блоков
    for row in range(6):
        for col in range(10):
            if random.random() < 0.05: 
                indestructible_blocks.append(pygame.Rect(col * block_width + 10, row * block_height + 10, block_width - 2, block_height - 2))
            else:
                blocks.append(pygame.Rect(col * block_width + 10, row * block_height + 10, block_width - 2, block_height - 2))

    return ball_x, ball_y, ball_dx, ball_dy, blocks, indestructible_blocks, bonuses, paddle_x, paddle_y


def spawn_bonus(block_rect):
    """Создание бонуса, выпадающего из разрушенного блока."""
    if random.random() < 0.3:  # 30% шанс выпадения бонуса
        return pygame.Rect(block_rect.x, block_rect.y, 20, 20)
    return None

def game_loop(username=None):
    """Основной игровой цикл."""
    while True:
        ball_x, ball_y, ball_dx, ball_dy, blocks, indestructible_blocks, bonuses, paddle_x, paddle_y = reset_game()

        paddle_width, paddle_height = 100, 20
        paddle_speed = 10
        ball_radius = 10

        move_left, move_right = False, False
        paused = False

        while True:
            if paused:
                pause_menu()
                paused = False

            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        move_left = True
                    elif event.key == pygame.K_RIGHT:
                        move_right = True
                    elif event.key == pygame.K_ESCAPE:
                        paused = True
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        move_left = False
                    elif event.key == pygame.K_RIGHT:
                        move_right = False

            # Движение платформы
            if move_left and paddle_x > 0:
                paddle_x -= paddle_speed
            if move_right and paddle_x < WIDTH - paddle_width:
                paddle_x += paddle_speed

            # Движение мяча
            ball_x += ball_dx
            ball_y += ball_dy

            # Отражения от стен
            if ball_x - ball_radius <= 0 or ball_x + ball_radius >= WIDTH:
                ball_dx *= -1
            if ball_y - ball_radius <= 0:
                ball_dy *= -1
            if ball_y + ball_radius >= HEIGHT:
                if not game_over_menu():
                    return
                else:
                    break

            # Отражение от платформы
            if paddle_x <= ball_x <= paddle_x + paddle_width and paddle_y <= ball_y + ball_radius <= paddle_y + paddle_height:
                ball_dy *= -1

            # Проверка столкновений с блоками
            for block in blocks[:]:
                if block.collidepoint(ball_x, ball_y - ball_radius) or block.collidepoint(ball_x, ball_y + ball_radius):
                    blocks.remove(block)
                    ball_dy *= -1
                    bonus = spawn_bonus(block)
                    if bonus:
                        bonuses.append(bonus)
                    break
            for block in indestructible_blocks:
                if block.collidepoint(ball_x, ball_y - ball_radius) or block.collidepoint(ball_x, ball_y + ball_radius):
                    ball_dy *= -1
                    break

            # Обработка бонусов
            for bonus in bonuses[:]:
                bonus.y += 5  # Бонус падает вниз
                if bonus.colliderect(pygame.Rect(paddle_x, paddle_y, paddle_width, paddle_height)):
                    bonuses.remove(bonus)
                    paddle_width = min(paddle_width + 20, WIDTH // 2)  # Увеличить платформу
                elif bonus.y > HEIGHT:
                    bonuses.remove(bonus)

            # Проверка, все ли блоки разрушены
            if not blocks and not indestructible_blocks:
                win_menu()
                break

            # Отображение объектов на экране
            screen.fill(BLACK)
            for block in blocks:
                pygame.draw.rect(screen, YELLOW, block)
            for block in indestructible_blocks:
                pygame.draw.rect(screen, BLUE, block)
            for bonus in bonuses:
                pygame.draw.rect(screen, RED, bonus)
            pygame.draw.rect(screen, GREEN, pygame.Rect(paddle_x, paddle_y, paddle_width, paddle_height))
            pygame.draw.circle(screen, WHITE, (ball_x, ball_y), ball_radius)
            pygame.display.flip()
            clock.tick(FPS)

def win_menu():
    """Меню победы."""
    while True:
        screen.fill(BLACK)
        win_text = font.render("YOU WIN!", True, GREEN)
        screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 100))

        retry_button = draw_button("Retry", WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 50, GREEN, WHITE, font, screen)
        exit_button = draw_button("Exit", WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50, RED, WHITE, font, screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if retry_button.collidepoint(mouse_pos):
                    return True
                elif exit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

# --- Создание таблицы пользователей ---
create_users_table()

# --- Главный цикл программы ---
if __name__ == "__main__":
    username = main_menu()
    game_loop(username)
