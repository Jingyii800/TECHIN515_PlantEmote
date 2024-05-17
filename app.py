import serial
import time
import numpy as np
from azure.iot.device import IoTHubDeviceClient, Message
import json
import pygame
import RPi.GPIO as GPIO

# Initialize Pygame
pygame.init()

# Set the display size
display_width = 1920
display_height = 1100
screen = pygame.display.set_mode((display_width, display_height))

# Load and scale icons
dry_icon = pygame.image.load('dry.png')
wet_icon = pygame.image.load('wet.png')
dry_icon = pygame.transform.scale(dry_icon, (100, 100))
wet_icon = pygame.transform.scale(wet_icon, (100, 100))

# Configuration parameters
port = '/dev/ttyUSB0'  # Update with the correct serial port
baud_rate = 230400  # Set baud rate
duration = 10  # Duration to read data in seconds

# Azure IoT Hub Configuration
CONNECTION_STRING = "HostName=PlantEmot.azure-devices.net;DeviceId=IoTDevice1;SharedAccessKey=your_shared_access_key_here"

# Set up GPIO for soil moisture sensor
GPIO.setmode(GPIO.BCM)
MOISTURE_SENSOR_PIN = 17  # Assuming GPIO17
GPIO.setup(MOISTURE_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Set up serial connection
ser = serial.Serial(port, baud_rate, timeout=1)
ser.reset_input_buffer()

# Send configuration command to the device
ser.write(b'conf s:10000;c:1;\n')  # Adjust as necessary based on device requirements
time.sleep(0.5)  # Give time for the device to respond

data = bytearray()
start_time = time.time()

# Collect data for approximately 10 seconds
while time.time() - start_time < duration:
    size = ser.in_waiting
    if size:
        data.extend(ser.read(size))
    time.sleep(0.1)

# Close the serial port
ser.close()

# Process the data
result = []
i = 0
while i < len(data) - 1:
    if data[i] > 127:
        int_out = ((data[i] & 127) << 7)
        i += 1
        int_out += data[i]
        result.append(int_out)
    i += 1

# Convert result to a numpy array
result_array = np.array(result)

def send_data_to_azure(signal_data, soil_moisture):
    """ Send signal and soil moisture data to Azure IoT Hub """
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    data_json = json.dumps({'signal_data': signal_data.tolist(), 'soil_moisture': soil_moisture})
    message = Message(data_json)
    message.content_encoding = "utf-8"
    message.content_type = "application/json"
    client.send_message(message)
    print("Data sent to Azure IoT Hub")
    client.disconnect()

# Read soil moisture sensor
is_dry = GPIO.input(MOISTURE_SENSOR_PIN)

# Display the appropriate icon
screen.fill((255, 255, 255))  # Clear screen with white
if is_dry:
    screen.blit(dry_icon, (display_width / 2, display_height / 2))
else:
    screen.blit(wet_icon, (display_width / 2, display_height / 2))
pygame.display.update()

# Send data to Azure IoT Hub
send_data_to_azure(result_array, 'dry' if is_dry else 'wet')

# Clean up
pygame.quit()
GPIO.cleanup()

