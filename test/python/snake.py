# Import the necessary libraries
import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 800, 600
SPEED = 10
BLOCK_SIZE = 20

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Set up some colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Set up the snake and food
snake = [(200, 200), (220, 200), (240, 200)]
food = (400, 300)

# Set up the snake direction
direction = 'RIGHT'

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction!= 'DOWN':
                direction = 'UP'
            elif event.key == pygame.K_DOWN and direction!= 'UP':
                direction = 'DOWN'
            elif event.key == pygame.K_LEFT and direction!= 'RIGHT':
                direction = 'LEFT'
            elif event.key == pygame.K_RIGHT and direction!= 'LEFT':
                direction = 'RIGHT'

    # Move the snake
    head = snake[-1]
    if direction == 'UP':
        new_head = (head[0], head[1] - BLOCK_SIZE)
    elif direction == 'DOWN':
        new_head = (head[0], head[1] + BLOCK_SIZE)
    elif direction == 'LEFT':
        new_head = (head[0] - BLOCK_SIZE, head[1])
    elif direction == 'RIGHT':
        new_head = (head[0] + BLOCK_SIZE, head[1])
    snake.append(new_head)

    # Check if the snake has eaten the food
    if snake[-1] == food:
        food = (random.randint(0, WIDTH - BLOCK_SIZE) // BLOCK_SIZE * BLOCK_SIZE, 
                random.randint(0, HEIGHT - BLOCK_SIZE) // BLOCK_SIZE * BLOCK_SIZE)
    else:
        snake.pop(0)

    # Check if the snake has hit the edge or itself
    if (snake[-1][0] < 0 or snake[-1][0] >= WIDTH or 
        snake[-1][1] < 0 or snake[-1][1] >= HEIGHT or 
        snake[-1] in snake[:-1]):
        pygame.quit()
        sys.exit()

    # Draw everything
    screen.fill(BLACK)
    for pos in snake:
        pygame.draw.rect(screen, GREEN, (pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))
    pygame.draw.rect(screen, RED, (food[0], food[1], BLOCK_SIZE, BLOCK_SIZE))
    pygame.display.flip()

    # Cap the frame rate
    pygame.time.Clock().tick(SPEED)