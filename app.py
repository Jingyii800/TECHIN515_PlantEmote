import pygame
import pyaudio
import numpy as np
from scipy.signal import butter, lfilter
import RPi.GPIO as GPIO
from azure.iot.device import IoTHubDeviceClient, Message
import json
import threading
from queue import Queue

# Initialize Pygame
pygame.init()

# Set the display size
display_width = 1920
display_height = 1100
screen = pygame.display.set_mode((display_width, display_height))

# Load icons or graphics
dry_icon = pygame.image.load('dry.png')
wet_icon = pygame.image.load('wet.png')
# Communication queue
display_queue = Queue()

# Scale icons to match screen size
dry_icon = pygame.transform.scale(dry_icon, (display_width, display_height))
wet_icon = pygame.transform.scale(wet_icon, (display_width, display_height))

def update_display():
    while not display_queue.empty():
        is_dry = display_queue.get()
        screen.fill((255, 255, 255))  # Clear the screen with white background
        if is_dry:
             screen.blit(dry_icon, (0, 0))
        else:
            screen.blit(wet_icon, (0, 0))  
        pygame.display.update()


# Azure IoT Hub Configuration
CONNECTION_STRING = "HostName=PlantEmot.azure-devices.net;DeviceId=IoTDevice1;SharedAccessKey=qa8Fn6cRYs+CfBleDLRhdLB1t/LmUF/1BAIoTFqnrmA="

# Soil Moisture Sensor Configuration
GPIO.setmode(GPIO.BCM)
MOISTURE_SENSOR_PIN = 14  # Assuming GPIO17
GPIO.setup(MOISTURE_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Audio Configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100  # Sample rate
CHUNK = 1024  # Samples per frame

def butter_highpass(cutoff, fs, order=5):
    """ Create a highpass filter """
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def apply_filter(data, cutoff, fs, order=5):
    """ Apply a highpass filter to the data """
    b, a = butter_highpass(cutoff, fs, order)
    filtered_data = lfilter(b, a, data)
    return filtered_data

def send_data_to_azure(filtered_data, soil_status):
    """ Send filtered audio data and soil status to Azure IoT Hub """
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    data_json = json.dumps({'audio_data': filtered_data.tolist(), 'soil_moisture': soil_status})
    message = Message(data_json)
    message.content_encoding = "utf-8"
    message.content_type = "application/json"
    client.send_message(message)
    print("Data sent to Azure IoT Hub")
    client.disconnect()
    
def data_processing():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True,
                    frames_per_buffer=CHUNK, input_device_index=2)
    try:
        while True:
            # Handle Pygame events to keep the display responsive
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
            
            try:
                frames = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
            except IOError as e:
                if e.errno == pyaudio.paInputOverflowed:
                    print("Input overflow, skipping this chunk.")
                    continue

            filtered_data = apply_filter(frames, cutoff=200, fs=RATE, order=2)

            # Read soil moisture sensor
            is_dry = GPIO.input(MOISTURE_SENSOR_PIN)

            # Update display
            display_queue.put(is_dry)

            # Send data to Azure IoT Hub
            send_data_to_azure(filtered_data, 'dry' if is_dry else 'wet')
    finally:
        stream.close()
        p.terminate()
        
# Start the background thread
thread = threading.Thread(target=data_processing)
thread.start()

# Main thread for Pygame
try:
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        update_display()
finally:
    pygame.quit()
    GPIO.cleanup()
    thread.join()
