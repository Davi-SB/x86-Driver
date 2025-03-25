#!/usr/bin/python3

import os
import sys
import pygame
import random
from fcntl import ioctl

# Mapeamento dos dígitos para os valores correspondentes no display de 7 segmentos
SEGMENT_MAP = {
    0: 0b11000000,
    1: 0b11111001,
    2: 0b10100100,
    3: 0b10110000,
    4: 0b10011001,
    5: 0b10010010,
    6: 0b10000010,
    7: 0b11111000,
    8: 0b10000000,
    9: 0b10010000
}

def encode_number(num: int, fd):
    high, low = 0, 0

    for i in range(8):
        digit = num % 10  # Obtém o último dígito
        num //= 10  # Remove o último dígito
        
        segment_value = SEGMENT_MAP[digit]  # Obtém o valor para 7 segmentos

        if i == 0:
        	low |= (segment_value << 0)
        elif i < 4:
        	low |= (segment_value << (i * 8))
        else:
        	high |= (segment_value << ((i - 4) * 8)) 
        	
        ioctl(fd, WR_L_DISPLAY)
        retval = os.write(fd, low.to_bytes(4, 'little'))
        ioctl(fd, WR_R_DISPLAY)
        retval = os.write(fd, high.to_bytes(4, 'little'))
        
# ioctl commands defined at the pci driver
RD_SWITCHES   = 24929
RD_PBUTTONS   = 24930
WR_L_DISPLAY  = 24931
WR_R_DISPLAY  = 24932
WR_RED_LEDS   = 24933
WR_GREEN_LEDS = 24934

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

def gameLoop(fd):
    game_over = False
    game_close = False
    x = WIDTH // 2
    y = HEIGHT // 2
    x_change = 0
    y_change = 0
    snake_body = []
    snake_length = 1
    food = new_food(snake_body)
    encode_number(0, fd)

    while not game_over:
        while game_close:
            screen.fill(BLACK)
            message("Você perdeu! Pressione C para jogar ou Q para sair", RED, [0, HEIGHT / 2])
            pygame.display.update()
            ioctl(fd, RD_SWITCHES)
            switches = os.read(fd, 1)
            switches = int.from_bytes(switches, 'little')
            
            #if event.type == pygame.KEYDOWN:
            # sair
            print(switches)
            if switches & 0x1:
                game_over = True
                game_close = False
            if switches & 0x2:
                gameLoop(fd)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False

        # Leitura dos botões
        ioctl(fd, RD_PBUTTONS)
        buttons = os.read(fd, 1)
        buttons = int.from_bytes(buttons, 'little')
		
        buttons = (~buttons)
        print(buttons)
        if ( buttons) & 0x2:  # Botão para esquerda
            x_change = -BLOCK_SIZE
            y_change = 0
        elif ( buttons) & 0x01:  # Botão para direita
            x_change = BLOCK_SIZE
            y_change = 0
        elif ( buttons) & 0x08:  # Botão para cima
            y_change = -BLOCK_SIZE
            x_change = 0
        elif ( buttons) & 0x04:  # Botão para baixo
            y_change = BLOCK_SIZE
            x_change = 0

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

        for block in snake_body[:-1]:
            if block == snake_head:
                game_close = True

        draw_snake(snake_body)
        pygame.display.update()

        if x == food[0] and y == food[1]:
            food = new_food(snake_body)
            snake_length += 1
            # Testando a função
            encode_number(snake_length-1, fd)

        clock.tick(5)

    pygame.quit()
    sys.exit()

def main():
    if len(sys.argv) < 2:
        print("Error: expected more command line arguments")
        print("Syntax: %s </dev/device_file>" % sys.argv[0])
        exit(1)

    fd = os.open(sys.argv[1], os.O_RDWR)
    gameLoop(fd)
    os.close(fd)

if __name__ == '__main__':
    main()
