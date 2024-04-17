import os
import pygame
import RPi.GPIO as GPIO
import time

# Initialize Pygame and the display
os.putenv('SDL_FBDEV', '/dev/fb1')
pygame.init()
pygame.display.set_mode((480, 320))  # Adjust the resolution to your specific display

# GPIO setup for the soil moisture sensor
GPIO.setmode(GPIO.BCM)
MOISTURE_SENSOR_PIN = 17  # Change to your connected GPIO pin
GPIO.setup(MOISTURE_SENSOR_PIN, GPIO.IN)

# Load images
wet_img = pygame.image.load('wet_icon.png')  # Ensure this path and file exist
dry_img = pygame.image.load('dry_icon.png')  # Ensure this path and file exist

# Main display loop
screen = pygame.display.get_surface()
try:
    while True:
        # Clear the screen
        screen.fill((0, 0, 0))  # Clear with black

        # Read the sensor
        if GPIO.input(MOISTURE_SENSOR_PIN) == GPIO.LOW:
            # Display the wet image and text
            screen.blit(wet_img, (20, 50))  # Adjust positioning as needed
            font = pygame.font.Font(None, 36)
            text = font.render('Soil is Moist', True, (255, 255, 255))
            screen.blit(text, (150, 250))  # Adjust text positioning as needed
        else:
            # Display the dry image and text
            screen.blit(dry_img, (20, 50))  # Adjust positioning as needed
            font = pygame.font.Font(None, 36)
            text = font.render('Soil is Dry', True, (255, 255, 255))
            screen.blit(text, (150, 250))  # Adjust text positioning as needed

        pygame.display.flip()  # Update the display
        time.sleep(1)  # Refresh rate

except KeyboardInterrupt:
    GPIO.cleanup()  # Clean up GPIO on CTRL+C exit
    pygame.quit()
