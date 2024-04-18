import pygame
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
    # Adjust the y position to be at the bottom of the screen minus padding
    TextRect.center = (display_width/2, display_height - 30)
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

try:
    index = 0
    while True:
        # Use modulo to alternate between dry and wet
        is_dry = index % 2 != 0
        
        # Show the moisture level on the screen
        show_moisture_level(is_dry)
        
        # Increment index to change the condition in the next iteration
        index += 1
        
        # Wait for 2 seconds before updating the condition again
        time.sleep(2)

except KeyboardInterrupt:
    print("Program stopped")

finally:
    # Cleanup pygame
    pygame.quit()

