import pygame
import pyaudio
import numpy as np
from scipy.signal import butter, lfilter
from azure.iot.device import IoTHubDeviceClient, Message
import json
import threading

# Initialize Pygame
pygame.init()

# Set the display size
display_width = 1920
display_height = 1100
screen = pygame.display.set_mode((display_width, display_height))

# Azure IoT Hub Configuration
CONNECTION_STRING = "HostName=PlantEmot.azure-devices.net;DeviceId=IoTDevice1;SharedAccessKey=your_shared_access_key_here"

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

def send_data_to_azure(filtered_data):
    """ Send filtered audio data to Azure IoT Hub """
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    data_json = json.dumps({'audio_data': filtered_data.tolist()})
    message = Message(data_json)
    message.content_encoding = "utf-8"
    message.content_type = "application/json"
    client.send_message(message)
    print("Data sent to Azure IoT Hub")
    client.disconnect()

def data_processing():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, input_device_index=2)
    buffer = []
    try:
        while True:
            frames = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
            buffer.append(frames)
            if len(buffer) * CHUNK / RATE >= 10:  # Collect 10 seconds of data
                all_frames = np.concatenate(buffer)
                filtered_data = apply_filter(all_frames, cutoff=200, fs=RATE, order=2)
                send_data_to_azure(filtered_data)
                buffer = []  # Clear buffer after sending
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
finally:
    pygame.quit()
    thread.join()
