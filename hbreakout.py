import subprocess
import pygame
import sys
import os
import pyautogui
import pygame.mixer
import requests
from geopy.geocoders import Nominatim

def get_ip():
    response = requests.get('https://ipinfo.io')
    data = response.json()
    return data['ip']

def get_location(ip):
    response = requests.get(f'https://ipinfo.io/{ip}/json')
    data = response.json()
    return data['loc'], data['city'], data['region'], data['country']

def get_detailed_location(lat, lon):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.reverse((lat, lon), language='en')
    return location.address

# Get user's IP address
ip = get_ip()
# print(f"IP Address: {ip}")

# Get latitude, longitude, city, region, and country
latlon, city, region, country = get_location(ip)
lat, lon = latlon.split(',')
# print(f"Location: {city}, {region}, {country}")


# get user
Player = os.environ.get('USERNAME')

# Initialize pygame
pygame.init()

# Initialize mixer
pygame.mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Breakout')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RAINBOW_COLORS = [
    (255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (143, 0, 255)
]
COLORS = [RED, GREEN, BLUE, RAINBOW_COLORS]
level_color_index = 0

# Paddle settings
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 10
paddle_speed = 10
paddle = pygame.Rect((WIDTH // 2) - (PADDLE_WIDTH // 2), HEIGHT - 30, PADDLE_WIDTH, PADDLE_HEIGHT)

# Ball settings
BALL_SIZE = 20
ball_speed_x, ball_speed_y = 5, -5
ball = pygame.Rect((WIDTH // 2) - (BALL_SIZE // 2), HEIGHT // 2, BALL_SIZE, BALL_SIZE)

# Brick settings
BRICK_WIDTH, BRICK_HEIGHT = 60, 20
bricks = []
rows, cols = 5, 10

def create_bricks():
    bricks.clear()
    for row in range(rows):
        for col in range(cols):
            brick_x = col * (BRICK_WIDTH + 10) + 35
            brick_y = row * (BRICK_HEIGHT + 10) + 35
            bricks.append(pygame.Rect(brick_x, brick_y, BRICK_WIDTH, BRICK_HEIGHT))

create_bricks()

# Score, lives, and level
score = 0
lives = 5
level = 1
font = pygame.font.Font(None, 36)
game_over = False
game_won = False
bonus_level = False
bonus_screen = False
rainbow_index = 0
rainbow_counter = 0
RAINBOW_DELAY = 5  # Slow down the rainbow animation
BONUS_SCREEN_DELAY = 2000  # 2 seconds delay for the bonus stage screen

# Load sound effects
# pygame.mixer.music.load('sounds/background_music.mp3')
bounce_sound = pygame.mixer.Sound('sounds/bounce.wav')
win_sound = pygame.mixer.Sound('sounds/win.wav')
game_over_sound = pygame.mixer.Sound('sounds/game_over.wav')
bonus_level_sound = pygame.mixer.Sound('sounds/bonus_level.wav')
jumpscare_sound = pygame.mixer.Sound('sounds/jumpscare.wav')

# Function to handle game over and jumpscare
def handle_game_over(player_name):
    # Play jumpscare sound
    jumpscare_sound.play()

    # Capture screenshot of desktop
    screenshot = pyautogui.screenshot()
    screenshot.save('screenshot.png')

    # Display jumpscare image for 5 seconds
    display_image('screenshot.png', 5000)

    # Black out screen and display message
    screen.fill((0, 0, 0))
    game_over_text = font.render(f"I see you {player_name}", True, WHITE)
    line2_text = font.render(f"How is it in {city}, {region}, {country}", True, WHITE)
    text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    line2_rect = line2_text.get_rect(center=(WIDTH // 2, HEIGHT // 4 + 30))
    screen.blit(game_over_text, text_rect)
    screen.blit(line2_text, line2_rect)
    pygame.display.flip()
    pygame.time.wait(5000)  # Wait for 5 seconds
    pygame.quit()
    sys.exit()

def display_image(image_path, duration):
    image = pygame.image.load(image_path)
    screen.blit(image, (0, 0))
    pygame.display.flip()
    pygame.time.wait(duration)

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if game_over:
                if event.key == pygame.K_r:
                    game_over = False
                    score = 0
                    lives = 5
                    level = 1
                    ball.x, ball.y = (WIDTH // 2) - (BALL_SIZE // 2), HEIGHT // 2
                    ball_speed_x, ball_speed_y = 5, -5
                    paddle_speed = 10
                    level_color_index = 0
                    create_bricks()
            elif game_won:
                pass  # Handle next level logic here if needed

    if not game_over and not game_won and not bonus_screen:
        # Paddle movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle.left > 0:
            paddle.x -= paddle_speed
        if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
            paddle.x += paddle_speed

        # Ball movement
        ball.x += ball_speed_x
        ball.y += ball_speed_y

        # Ball collision with walls
        if ball.left <= 0 or ball.right >= WIDTH:
            ball_speed_x = -ball_speed_x
            bounce_sound.play()
        if ball.top <= 0:
            ball_speed_y = -ball_speed_y
            bounce_sound.play()

        # Ball collision with paddle
        if ball.colliderect(paddle):
            ball_speed_y = -ball_speed_y
            bounce_sound.play()

        # Ball collision with bricks
        for brick in bricks[:]:
            if ball.colliderect(brick):
                ball_speed_y = -ball_speed_y
                bricks.remove(brick)
                score += 1
                bounce_sound.play()
                break

        # Ball out of bounds
        if ball.bottom >= HEIGHT:
            lives -= 1
            if lives > 0:
                ball.x, ball.y = (WIDTH // 2) - (BALL_SIZE // 2), HEIGHT // 2
                ball_speed_x, ball_speed_y = 5, -5
            else:
                game_over = True
                game_over_sound.play()

        # Check for win condition
        if not bricks:
            if level % 3 == 0:
                bonus_screen = True
                bonus_level = True
                bonus_screen_start = pygame.time.get_ticks()
                bonus_level_sound.play()
            else:
                game_won = True
                win_sound.play()

        # Drawing everything
        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, paddle)
        pygame.draw.ellipse(screen, WHITE, ball)

        if bonus_level:
            rainbow_counter += 1
            if rainbow_counter % RAINBOW_DELAY == 0:
                rainbow_index += 1
            for brick in bricks:
                pygame.draw.rect(screen, RAINBOW_COLORS[rainbow_index % len(RAINBOW_COLORS)], brick)
        else:
            for brick in bricks:
                pygame.draw.rect(screen, COLORS[level_color_index], brick)

        # Display score, lives, and level
        score_text = font.render(f'Score: {score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        lives_text = font.render(f'Lives: {lives}', True, WHITE)
        screen.blit(lives_text, (WIDTH - 110, 10))
        level_text = font.render(f'Level: {level}', True, WHITE)
        screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, 10))

    elif game_over:
        screen.fill(BLACK)
        game_over_text = font.render('Game Over', True, WHITE)
        restart_text = font.render('Press R to Restart', True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 30))

    elif game_won:
        screen.fill(BLACK)
        win_text = font.render('You Win! Next Level...', True, WHITE)
        screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - win_text.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        game_won = False
        level += 1
        ball.x, ball.y = (WIDTH // 2) - (BALL_SIZE // 2), HEIGHT // 2
        ball_speed_x, ball_speed_y = 5, -5
        level_color_index = (level_color_index + 1) % len(COLORS)
        create_bricks()

    elif bonus_screen:
        screen.fill(BLACK)
        rainbow_counter += 1
        if rainbow_counter % RAINBOW_DELAY == 0:
            rainbow_index += 1
        bonus_text = font.render('Entering Bonus Stage!', True, RAINBOW_COLORS[rainbow_index % len(RAINBOW_COLORS)])
        screen.blit(bonus_text, (WIDTH // 2 - bonus_text.get_width() // 2, HEIGHT // 2 - bonus_text.get_height() // 2))
        if pygame.time.get_ticks() - bonus_screen_start >= BONUS_SCREEN_DELAY:
            bonus_screen = False
            ball.x, ball.y = (WIDTH // 2) - (BALL_SIZE // 2), HEIGHT // 2
            ball_speed_x, ball_speed_y = 5, -5
            create_bricks()
            rainbow_index = 0
            rainbow_counter = 0

    elif bonus_level:
        screen.fill(BLACK)
        bonus_text = font.render('Bonus Level! Destroy All Bricks for Extra Lives!', True, WHITE)
        screen.blit(bonus_text, (WIDTH // 2 - bonus_text.get_width() // 2, HEIGHT // 2 - bonus_text.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        bonus_level = False
        lives += 3  # Give 3 extra lives after completing the bonus level
        ball.x, ball.y = (WIDTH // 2) - (BALL_SIZE // 2), HEIGHT // 2
        ball_speed_x, ball_speed_y = 5, -5
        create_bricks()
        rainbow_index = 0
        rainbow_counter = 0

    pygame.display.flip()
    pygame.time.Clock().tick(60)

    # Speed up ball and paddle by 10% after each bonus level
    if not game_over and not game_won and not bonus_screen and bonus_level:
        ball_speed_x *= 1.1
        ball_speed_y *= 1.1
        paddle_speed *= 1.1
        bonus_level = False

    # Check for game over after first bonus level and trigger jump scare
    if game_over and level > 1:
        handle_game_over(Player)  # Replace "Player" with actual player name retrieval logic if available

# Quit Pygame
pygame.quit()
sys.exit()
