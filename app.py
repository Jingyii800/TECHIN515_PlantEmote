import threading
import serial
import time
import numpy as np
from azure.iot.device import IoTHubDeviceClient, Message
import json
import pygame
import RPi.GPIO as GPIO
from queue import Queue

# Initialize Pygame
pygame.init()

# Set the display size
display_width = 1920
display_height = 1100
screen = pygame.display.set_mode((display_width, display_height))

# Load and scale icons
dry_icon = pygame.image.load('dry.png')
wet_icon = pygame.image.load('wet.png')
dry_icon = pygame.transform.scale(dry_icon, (display_width, display_height))
wet_icon = pygame.transform.scale(wet_icon, (display_width, display_height))

# Communication queue for display updates
display_queue = Queue()

# Configuration parameters
port = '/dev/ttyACM0'  # Update with the correct serial port
baud_rate = 230400  # Set baud rate
duration = 10  # Duration to read data in seconds

# Azure IoT Hub Configuration
CONNECTION_STRING = "HostName=PlantEmote1.azure-devices.net;DeviceId=Device1;SharedAccessKey=sC7GZUGp3D7kEqVbyjHb0K45nN6YXWpD6qFjtlRF8HU="

# Soil Moisture Sensor Configuration
GPIO.setmode(GPIO.BCM)
MOISTURE_SENSOR_PIN = 14
GPIO.setup(MOISTURE_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def read_serial_data():
    """Read data from the serial port."""
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

    return result_array

def send_data_to_azure(signal_data, soil_moisture, downsample_factor=10):
    """Send signal and soil moisture data to Azure IoT Hub in chunks."""
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    # Downsample the data
    downsampled_data = signal_data[::downsample_factor]
    data_list = downsampled_data.tolist()
    
    data_json = json.dumps
    ({'signal_data': data_list, 
      'soil_moisture': soil_moisture})
    
    message = Message(data_json)
    message.content_encoding = "utf-8"
    message.content_type = "application/json"
    try:
        client.send_message(message)
        print("Data sent to Azure IoT Hub")
    except ValueError as e:
        print(f"Failed to send data: {e}")
    
    client.disconnect()

def update_display():
    while True:
        is_dry = GPIO.input(MOISTURE_SENSOR_PIN)
        display_queue.put(is_dry)
        time.sleep(1)  # Update every second

def data_processing():
    """Background thread for data processing."""
    while True:
        # Read soil moisture sensor once
        is_dry = GPIO.input(MOISTURE_SENSOR_PIN)

        # Read serial data
        signal_data = read_serial_data()

        # Send data to Azure IoT Hub
        send_data_to_azure(signal_data, 'dry' if is_dry else 'wet')        
        
        # Rest for 1 minute
        time.sleep(60)

def handle_display():
    while True:
        if not display_queue.empty():
            is_dry = display_queue.get()
            screen.fill((255, 255, 255))  # Clear the screen with white background
            if is_dry:
                screen.blit(dry_icon, (0, 0))
            else:
                screen.blit(wet_icon, (0, 0))
            pygame.display.update()

def main():
    # Start the background thread for data processing
    data_thread = threading.Thread(target=data_processing)
    data_thread.daemon = True  # Ensure the thread exits when the main program exits
    data_thread.start()

    # Start the thread for real-time soil moisture display updates
    display_thread = threading.Thread(target=update_display)
    display_thread.daemon = True
    display_thread.start()

    try:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            # Handle Pygame display updates
            handle_display()

    finally:
        pygame.quit()
        GPIO.cleanup()

if __name__ == "__main__":
    main()
