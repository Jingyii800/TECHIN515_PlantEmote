import pygame
import RPi.GPIO as GPIO
import time

# Initialize Pygame
pygame.init()

# Set the display size
display_width = 480
display_height = 320
screen = pygame.display.set_mode((display_width, display_height))

# Define colors
black = (0, 0, 0)
white = (255, 255, 255)

# Load icons
dry_icon = pygame.image.load('dry.png')
wet_icon = pygame.image.load('wet.png')

def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()

def message_display(text):
    largeText = pygame.font.Font('freesansbold.ttf', 20)
    TextSurf, TextRect = text_objects(text, largeText)
    TextRect.center = ((display_width/2), (display_height/2 + 50))
    screen.blit(TextSurf, TextRect)
    pygame.display.update()

def show_moisture_level(is_dry):
    screen.fill(white)  # Clear the screen
    if is_dry:
        screen.blit(dry_icon, (display_width/2 - dry_icon.get_width()/2, 50))
        message_display("Soil is dry")
    else:
        screen.blit(wet_icon, (display_width/2 - wet_icon.get_width()/2, 50))
        message_display("Soil is moist")
    
    pygame.display.update()

# Configure the Pi to use the BCM (Broadcom) pin names
GPIO.setmode(GPIO.BCM)

# Pin connected to the sensor's output
MOISTURE_SENSOR_PIN = 12  # Replace with your GPIO pin

# Set up the pin as an input with a pull-up resistor
GPIO.setup(MOISTURE_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        # Read the sensor (True if dry, False if wet)
        is_dry = GPIO.input(MOISTURE_SENSOR_PIN)
        
        # Show the moisture level on the screen
        show_moisture_level(is_dry)
        
        # Wait for 1 second before reading again
        time.sleep(1)

except KeyboardInterrupt:
    print("Program stopped")

finally:
    # Clean up the GPIO to reset the pin states
    GPIO.cleanup()
    pygame.quit()

