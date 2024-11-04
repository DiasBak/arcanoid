import pygame
import sys

# Инициализация Pygame
pygame.init()

# Размеры окна
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Арканоид")

# Частота кадров (FPS)
FPS = 60
clock = pygame.time.Clock()

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Параметры платформы
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 20
PADDLE_SPEED = 7

# Параметры мяча
BALL_RADIUS = 10
ball_speed_x = 4
ball_speed_y = -4

# Параметры блоков
BLOCK_WIDTH = 75
BLOCK_HEIGHT = 30
BLOCK_ROWS = 5
BLOCK_COLUMNS = 8
block_padding = 10

def reset_game():
    """Функция для сброса всех игровых параметров при рестарте"""
    global paddle_x, paddle_y, ball_x, ball_y, ball_speed_x, ball_speed_y, blocks, game_over

    # Начальная позиция платформы
    paddle_x = (WIDTH - PADDLE_WIDTH) // 2
    paddle_y = HEIGHT - PADDLE_HEIGHT - 10

    # Начальная позиция мяча
    ball_x = WIDTH // 2
    ball_y = HEIGHT // 2

    # Создаем блоки
    blocks = []
    for row in range(BLOCK_ROWS):
        block_row = []
        for col in range(BLOCK_COLUMNS):
            block_x = col * (BLOCK_WIDTH + block_padding) + block_padding
            block_y = row * (BLOCK_HEIGHT + block_padding) + block_padding
            block = pygame.Rect(block_x, block_y, BLOCK_WIDTH, BLOCK_HEIGHT)
            block_row.append(block)
        blocks.append(block_row)

    # Сброс флага окончания игры
    game_over = False

# Инициализируем начальные параметры
reset_game()

# Флаги состояний игры
game_started = False
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Обрабатываем нажатие клавиш для старта или перезапуска игры
        if not game_started and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:  # Нажатие клавиши "S" для начала игры
                game_started = True
                reset_game()  # Начинаем новую игру

        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # Нажатие клавиши "R" для рестарта
                reset_game()
            elif event.key == pygame.K_s:  # Нажатие клавиши "S" для возврата к стартовому экрану
                game_started = False

    if game_started and not game_over:
        # Получаем нажатые клавиши
        keys = pygame.key.get_pressed()

        # Движение платформы
        if keys[pygame.K_LEFT] and paddle_x > 0:
            paddle_x -= PADDLE_SPEED
        if keys[pygame.K_RIGHT] and paddle_x < WIDTH - PADDLE_WIDTH:
            paddle_x += PADDLE_SPEED

        # Движение мяча
        ball_x += ball_speed_x
        ball_y += ball_speed_y

        # Столкновения мяча с границами экрана
        if ball_x - BALL_RADIUS <= 0 or ball_x + BALL_RADIUS >= WIDTH:
            ball_speed_x = -ball_speed_x
        if ball_y - BALL_RADIUS <= 0:
            ball_speed_y = -ball_speed_y

        # Проверка на выход мяча за пределы экрана (ниже платформы)
        if ball_y + BALL_RADIUS >= HEIGHT:
            game_over = True  # Игра окончена

        # Столкновение мяча с платформой
        if paddle_y < ball_y + BALL_RADIUS < paddle_y + PADDLE_HEIGHT and paddle_x < ball_x < paddle_x + PADDLE_WIDTH:
            ball_speed_y = -ball_speed_y

        # Столкновение мяча с блоками
        for row in blocks:
            for block in row:
                if block.collidepoint(ball_x, ball_y):
                    ball_speed_y = -ball_speed_y  # Мяч отскакивает
                    row.remove(block)  # Удаляем блок
                    break

    # Закрашиваем экран черным цветом
    screen.fill(BLACK)

    if not game_started:
        # Отображение стартового экрана
        font = pygame.font.SysFont(None, 55)
        text = font.render("Press 'S' to Start", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    
    elif game_over:
        # Отображение сообщения после окончания игры
        font = pygame.font.SysFont(None, 55)
        text = font.render("Game Over! Press 'R' to Restart or 'S' for Start Screen", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    
    else:
        # Рисуем платформу
        pygame.draw.rect(screen, WHITE, (paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))

        # Рисуем мяч
        pygame.draw.circle(screen, WHITE, (ball_x, ball_y), BALL_RADIUS)

        # Рисуем блоки
        for row in blocks:
            for block in row:
                pygame.draw.rect(screen, BLUE, block)

    # Обновляем экран
    pygame.display.flip()

    # Ограничиваем частоту кадров
    clock.tick(FPS)

# Завершение работы Pygame
pygame.quit()
sys.exit()
