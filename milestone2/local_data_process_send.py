import numpy as np
import pyaudio
import threading
from scipy.signal import butter, lfilter
import pygame
import RPi.GPIO as GPIO
from azure.iot.device import IoTHubDeviceClient, Message
import json

# Azure IoT Hub Configuration
CONNECTION_STRING = "HostName=PlantEmot.azure-devices.net;DeviceId=IoTDevice1;SharedAccessKey=qa8Fn6cRYs+CfBleDLRhdLB1t/LmUF/1BAIoTFqnrmA="

# Soil Moisture Sensor Configuration
GPIO.setmode(GPIO.BCM)
MOISTURE_SENSOR_PIN = 17  # Assuming GPIO17
GPIO.setup(MOISTURE_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Audio Configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 9600  # Sample rate
CHUNK = 1024  # Samples per frame

# Initialize PyAudio
p = pyaudio.PyAudio()

# Initialize Pygame
pygame.init()

# Set the display size
display_width = 480
display_height = 320
screen = pygame.display.set_mode((display_width, display_height), pygame.FULLSCREEN)

# Load icons
dry_icon = pygame.image.load('dry.png')
wet_icon = pygame.image.load('wet.png')

def show_moisture_level(is_dry):
    """ Display the current moisture level on the screen """
    screen.fill((255, 255, 255))  # Clear the screen with white background
    if is_dry:
        screen.blit(dry_icon, ((display_width - dry_icon.get_width()) // 2, 50))
    else:
        screen.blit(wet_icon, ((display_width - wet_icon.get_width()) // 2, 50))
    pygame.display.update()

# Open audio stream
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True,
                frames_per_buffer=CHUNK, input_device_index=0)

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

def read_from_stream():
    """ Continuously read from audio stream and send data """
    while True:
        frames = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
        filtered_data = apply_filter(frames, cutoff=200, fs=RATE, order=2)
        
        # Read soil moisture sensor
        is_dry = GPIO.input(MOISTURE_SENSOR_PIN)
        
        # Display moisture level on screen
        show_moisture_level(is_dry)
        
        # Check for exit condition
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return  # Exit the function
        
        # Send data to Azure IoT Hub
        send_data_to_azure(filtered_data, 'dry' if is_dry else 'wet')

# Setup threading for continuous audio reading
thread = threading.Thread(target=read_from_stream)
thread.start()

# Cleanup
stream.stop_stream()
stream.close()
p.terminate()
thread.join()
pygame.quit()
