import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from azure.iot.device import IoTHubDeviceClient, Message
import json
import pyaudio
import threading
from scipy.signal import butter, lfilter
import pygame
import RPi.GPIO as GPIO

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
DISPLAY_SIZE = RATE * 20  # 20 seconds of data

# Initialize PyAudio
p = pyaudio.PyAudio()

# Initialize Pygame
pygame.init()

# Set the display size
display_width = 480
display_height = 320
screen = pygame.display.set_mode((display_width, display_height), pygame.FULLSCREEN)

# Define colors
black = (0, 0, 0)
white = (255, 255, 255)

# Load icons
dry_icon = pygame.image.load('dry.png')
wet_icon = pygame.image.load('wet.png')

def show_moisture_level(is_dry):
    screen.fill(white)  # Clear the screen
    if is_dry:
        screen.blit(dry_icon, (display_width / 2 - dry_icon.get_width() / 2, 50))
    else:
        screen.blit(wet_icon, (display_width / 2 - wet_icon.get_width() / 2, 50))
    
    pygame.display.update()

# Open audio stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                input_device_index=0)  # Audio device index

# Buffer for audio data
audio_buffer = np.zeros(DISPLAY_SIZE)

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def apply_filter(data, cutoff, fs, type='low', order=5):
    if type == 'low':
        b, a = butter_lowpass(cutoff, fs, order=order)
    elif type == 'high':
        b, a = butter_highpass(cutoff, fs, order=order)
    filtered_data = lfilter(b, a, data)
    return filtered_data

def send_data_to_azure(filtered_data, soil_status):
    """ Send filtered audio data to Azure IoT Hub """
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    data_json = json.dumps({'audio_data': filtered_data.tolist(), 'soil_moisture': soil_status})
    message = Message(data_json)
    message.content_encoding = "utf-8"
    message.content_type = "application/json"
    client.send_message(message)
    print("Data sent to Azure IoT Hub")
    client.disconnect()

def update_plot(frame):
    """ Update the plot with new audio data """
    line.set_ydata(audio_buffer)
    return line,

def read_from_stream():
    """ Continuously read from audio stream and send every 10 seconds """
    audio_buffer = np.zeros(DISPLAY_SIZE)
    while True:
        frames = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
        filtered_data = apply_filter(frames, cutoff=200, fs=RATE, type='high', order=2)
        audio_buffer = np.roll(audio_buffer, -len(filtered_data))
        audio_buffer[-len(filtered_data):] = filtered_data
        # Read soil moisture sensor
        is_dry = GPIO.input(MOISTURE_SENSOR_PIN)
        
        # Display moisture level on screen
        show_moisture_level(is_dry)
        
        # Check for exit condition
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return  # Exit the function
        
        if np.any(audio_buffer):
            send_data_to_azure(audio_buffer, 'dry' if is_dry else 'wet')

# Setup threading for continuous audio reading
thread = threading.Thread(target=read_from_stream)
thread.start()

# Setup matplotlib plot
fig, ax = plt.subplots()
x = np.linspace(-20, 0, num=DISPLAY_SIZE)
line, = ax.plot(x, np.zeros(DISPLAY_SIZE), '-', lw=1)
ax.set_ylim(-700, 700)  # y-axis limits

# Animate plot updates
ani = FuncAnimation(fig, update_plot, blit=True, interval=50, repeat=True)
plt.show()

# Clean up
stream.stop_stream()
stream.close()
p.terminate()
thread.join()

