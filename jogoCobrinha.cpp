#include <iostream>
#include <vector>
#include <cstdlib>
#include <ctime>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <SDL2/SDL.h>

// ioctl commands defined at the PCI driver
#define RD_SWITCHES   24929
#define RD_PBUTTONS   24930
#define WR_L_DISPLAY  24931
#define WR_R_DISPLAY  24932
#define WR_RED_LEDS   24933
#define WR_GREEN_LEDS 24934

const int WIDTH = 600;
const int HEIGHT = 400;
const int BLOCK_SIZE = 20;
const SDL_Color WHITE = {255, 255, 255, 255};
const SDL_Color BLACK = {0, 0, 0, 255};
const SDL_Color RED = {255, 0, 0, 255};
const SDL_Color GREEN = {0, 255, 0, 255};

void message(SDL_Renderer* renderer, TTF_Font* font, const char* msg, SDL_Color color, SDL_Point pos) {
    SDL_Surface* surface = TTF_RenderText_Solid(font, msg, color);
    SDL_Texture* texture = SDL_CreateTextureFromSurface(renderer, surface);
    SDL_Rect dstrect = {pos.x, pos.y, surface->w, surface->h};
    SDL_RenderCopy(renderer, texture, NULL, &dstrect);
    SDL_DestroyTexture(texture);
    SDL_FreeSurface(surface);
}

void draw_snake(SDL_Renderer* renderer, const std::vector<SDL_Point>& snake_body) {
    SDL_SetRenderDrawColor(renderer, GREEN.r, GREEN.g, GREEN.b, GREEN.a);
    for (const auto& block : snake_body) {
        SDL_Rect rect = {block.x, block.y, BLOCK_SIZE, BLOCK_SIZE};
        SDL_RenderFillRect(renderer, &rect);
    }
}

SDL_Point new_food(const std::vector<SDL_Point>& snake_body) {
    SDL_Point food;
    bool valid_position = false;
    while (!valid_position) {
        food.x = (rand() % (WIDTH / BLOCK_SIZE)) * BLOCK_SIZE;
        food.y = (rand() % (HEIGHT / BLOCK_SIZE)) * BLOCK_SIZE;
        valid_position = true;
        for (const auto& block : snake_body) {
            if (block.x == food.x && block.y == food.y) {
                valid_position = false;
                break;
            }
        }
    }
    return food;
}

void game_loop(int fd) {
    SDL_Window* window = SDL_CreateWindow("Snake Game", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, WIDTH, HEIGHT, SDL_WINDOW_SHOWN);
    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    TTF_Font* font = TTF_OpenFont("arial.ttf", 35);

    bool game_over = false;
    bool game_close = false;
    int x = WIDTH / 2;
    int y = HEIGHT / 2;
    int x_change = 0;
    int y_change = 0;
    std::vector<SDL_Point> snake_body;
    int snake_length = 1;
    SDL_Point food = new_food(snake_body);

    while (!game_over) {
        while (game_close) {
            SDL_SetRenderDrawColor(renderer, BLACK.r, BLACK.g, BLACK.b, BLACK.a);
            SDL_RenderClear(renderer);
            message(renderer, font, "You lost! Press C to play or Q to quit", RED, {0, HEIGHT / 2});
            SDL_RenderPresent(renderer);

            ioctl(fd, RD_SWITCHES);
            char switches_char;
            read(fd, &switches_char, 1);
            int switches = static_cast<int>(switches_char);
            
            if (switches & 0x1) {
                game_over = true;
                game_close = false;
            }
            if (switches & 0x2) {
                game_loop(fd);
            }

            SDL_Event event;
            while (SDL_PollEvent(&event)) {
                if (event.type == SDL_QUIT) {
                    game_over = true;
                    game_close = false;
                }
            }
        }

        ioctl(fd, RD_PBUTTONS);
        char buttons_char;
        read(fd, &buttons_char, 1);
        int buttons = static_cast<int>(buttons_char);
        buttons = ~buttons;

        if (buttons & 0x2) {
            x_change = -BLOCK_SIZE;
            y_change = 0;
        } else if (buttons & 0x1) {
            x_change = BLOCK_SIZE;
            y_change = 0;
        } else if (buttons & 0x8) {
            y_change = -BLOCK_SIZE;
            x_change = 0;
        } else if (buttons & 0x4) {
            y_change = BLOCK_SIZE;
            x_change = 0;
        }

        if (x >= WIDTH || x < 0 || y >= HEIGHT || y < 0) {
            game_close = true;
        }
        x += x_change;
        y += y_change;

        SDL_SetRenderDrawColor(renderer, BLACK.r, BLACK.g, BLACK.b, BLACK.a);
        SDL_RenderClear(renderer);
        SDL_SetRenderDrawColor(renderer, RED.r, RED.g, RED.b, RED.a);
        SDL_Rect food_rect = {food.x, food.y, BLOCK_SIZE, BLOCK_SIZE};
        SDL_RenderFillRect(renderer, &food_rect);

        SDL_Point snake_head = {x, y};
        snake_body.push_back(snake_head);
        if (snake_body.size() > snake_length) {
            snake_body.erase(snake_body.begin());
        }

        for (size_t i = 0; i < snake_body.size() - 1; ++i) {
            if (snake_body[i].x == snake_head.x && snake_body[i].y == snake_head.y) {
                game_close = true;
                break;
            }
        }

        draw_snake(renderer, snake_body);
        SDL_RenderPresent(renderer);

        if (x == food.x && y == food.y) {
            food = new_food(snake_body);
            ++snake_length;
        }

        SDL_Delay(200);
    }

    TTF_CloseFont(font);
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Error: expected more command line arguments" << std::endl;
        std::cerr << "Syntax: " << argv[0] << " </dev/device_file>" << std::endl;
        return 1;
    }

    int fd = open(argv[1], O_RDWR);
    if (fd < 0) {
        std::cerr << "Error: could not open device file" << std::endl;
        return 1;
    }

    srand(time(NULL));
    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        std::cerr << "Error: could not initialize SDL" << std::endl;
        return 1;
    }
    if (TTF_Init() == -1) {
        std::cerr << "Error: could not initialize SDL_ttf" << std::endl;
        return 1;
    }

    game_loop(fd);

    close(fd);
    TTF_Quit();
    SDL_Quit();
    return 0;
}
