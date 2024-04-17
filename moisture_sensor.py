import RPi.GPIO as GPIO
import time

# Configure the Pi to use the BCM (Broadcom) pin names
GPIO.setmode(GPIO.BCM)

# Pin connected to the sensor's output
MOISTURE_SENSOR_PIN = 17  # Replace with your GPIO pin

# Set up the pin as an input with a pull-up resistor
GPIO.setup(MOISTURE_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        # Read the sensor (True if dry, False if wet)
        is_dry = GPIO.input(MOISTURE_SENSOR_PIN)
        
        if is_dry:
            print("Soil is dry")
        else:
            print("Soil is moist")
        
        # Wait for 1 second before reading again
        time.sleep(1)

except KeyboardInterrupt:
    print("Program stopped")

finally:
    # Clean up the GPIO to reset the pin states
    GPIO.cleanup()

# import os
# import pygame
# import RPi.GPIO as GPIO
# import time

# # Initialize Pygame and the display
# os.putenv('SDL_FBDEV', '/dev/fb1')
# pygame.init()
# pygame.display.set_mode((480, 320))  # Adjust the resolution to your specific display

# # GPIO setup for the soil moisture sensor
# GPIO.setmode(GPIO.BCM)
# MOISTURE_SENSOR_PIN = 17  # Change to your connected GPIO pin
# GPIO.setup(MOISTURE_SENSOR_PIN, GPIO.IN)

# # Load images
# wet_img = pygame.image.load('wet_icon.png')  # Ensure this path and file exist
# dry_img = pygame.image.load('dry_icon.png')  # Ensure this path and file exist

# # Main display loop
# screen = pygame.display.get_surface()
# try:
#     while True:
#         # Clear the screen
#         screen.fill((0, 0, 0))  # Clear with black

#         # Read the sensor
#         if GPIO.input(MOISTURE_SENSOR_PIN) == GPIO.LOW:
#             # Display the wet image and text
#             screen.blit(wet_img, (20, 50))  # Adjust positioning as needed
#             font = pygame.font.Font(None, 36)
#             text = font.render('Soil is Moist', True, (255, 255, 255))
#             screen.blit(text, (150, 250))  # Adjust text positioning as needed
#         else:
#             # Display the dry image and text
#             screen.blit(dry_img, (20, 50))  # Adjust positioning as needed
#             font = pygame.font.Font(None, 36)
#             text = font.render('Soil is Dry', True, (255, 255, 255))
#             screen.blit(text, (150, 250))  # Adjust text positioning as needed

#         pygame.display.flip()  # Update the display
#         time.sleep(1)  # Refresh rate

# except KeyboardInterrupt:
#     GPIO.cleanup()  # Clean up GPIO on CTRL+C exit
#     pygame.quit()
