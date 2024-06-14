import pygame
import os
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
print(f"Location: {city}, {region}, {country}")

# Split the text into two lines
player_name = os.environ.get('USERNAME')  # Replace with actual player name variable
line1 = f"I see you {player_name}"
line2 = f"How is it in {city}, {region}, {country}"

pygame.init()

# Create the screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Create the font
font = pygame.font.Font(None, 36)  # You can change the font size as needed

WHITE = (255, 255, 255)

# Render each line separately
line1_text = font.render(line1, True, WHITE)
line2_text = font.render(line2, True, WHITE)

# Get the rectangles for each line of text
line1_rect = line1_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
line2_rect = line2_text.get_rect(center=(WIDTH // 2, HEIGHT // 4 + 30))  # Adjust the second line's y position

# Draw the text on the screen
screen.fill((0, 0, 0))  # Fill the screen with black before drawing text
screen.blit(line1_text, line1_rect)
screen.blit(line2_text, line2_rect)

# Update the display
pygame.display.flip()

# Pause for a moment to view the result
pygame.time.wait(3000)

# Quit pygame
pygame.quit()