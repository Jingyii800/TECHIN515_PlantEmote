import pygame
import sys

# Initialize Pygame
pygame.init()

# Set the dimensions of the window
window_size = (1920, 1100)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Pygame Image Display Test")

# Load an image
image_path = "test_image.png"  # Replace this with the path to your image file
image = pygame.image.load(image_path)

# Scale the image to fit the window
image = pygame.transform.scale(image, window_size)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill((0, 0, 0))

    # Draw the image
    screen.blit(image, (0, 0))

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
