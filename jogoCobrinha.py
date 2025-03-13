import pygame
import random
import sys

# Inicialização do pygame
pygame.init()

# Configurações da tela
WIDTH, HEIGHT = 600, 400
BLOCK_SIZE = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Jogo da Cobrinha')

# Definição de cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)

clock = pygame.time.Clock()

# Fonte para mensagens
font_style = pygame.font.SysFont(None, 35)

def message(msg, color, pos):
    mesg = font_style.render(msg, True, color)
    screen.blit(mesg, pos)

def draw_snake(snake_body):
    for block in snake_body:
        pygame.draw.rect(screen, GREEN, [block[0], block[1], BLOCK_SIZE, BLOCK_SIZE])

def new_food(snake_body):
    while True:
        x = random.randrange(0, WIDTH, BLOCK_SIZE)
        y = random.randrange(0, HEIGHT, BLOCK_SIZE)
        if [x, y] not in snake_body:
            return [x, y]

def gameLoop():
    game_over = False
    game_close = False

    # Posição inicial da cobra (centro da tela)
    x = WIDTH // 2
    y = HEIGHT // 2
    x_change = 0
    y_change = 0

    snake_body = []
    snake_length = 1

    food = new_food(snake_body)

    while not game_over:
        # Tela de fim de jogo
        while game_close:
            screen.fill(BLACK)
            message("Você perdeu! Pressione C para jogar ou Q para sair", RED, [0,HEIGHT/2])
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False

        # Eventos de movimento
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x_change = -BLOCK_SIZE
                    y_change = 0
                elif event.key == pygame.K_RIGHT:
                    x_change = BLOCK_SIZE
                    y_change = 0
                elif event.key == pygame.K_UP:
                    y_change = -BLOCK_SIZE
                    x_change = 0
                elif event.key == pygame.K_DOWN:
                    y_change = BLOCK_SIZE
                    x_change = 0

        # Verifica colisão com as bordas
        if x >= WIDTH or x < 0 or y >= HEIGHT or y < 0:
            game_close = True

        x += x_change
        y += y_change

        screen.fill(BLACK)
        pygame.draw.rect(screen, RED, [food[0], food[1], BLOCK_SIZE, BLOCK_SIZE])
        
        snake_head = [x, y]
        snake_body.append(snake_head)
        if len(snake_body) > snake_length:
            del snake_body[0]

        # Verifica colisão com o próprio corpo
        for block in snake_body[:-1]:
            if block == snake_head:
                game_close = True

        draw_snake(snake_body)
        pygame.display.update()

        # Verifica se a cobra comeu a comida
        if x == food[0] and y == food[1]:
            food = new_food(snake_body)
            snake_length += 1
            print(snake_length-1)
                  

        clock.tick(7)  # Controle da velocidade

    pygame.quit()
    sys.exit()

gameLoop()
