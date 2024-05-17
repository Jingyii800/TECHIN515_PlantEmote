import serial
import time
import matplotlib.pyplot as plt
import numpy as np
from azure.iot.device import IoTHubDeviceClient, Message
import json
import threading
import matplotlib.animation as animation

# Azure IoT Hub Configuration
CONNECTION_STRING = "HostName=PlantEmote1.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=VZgcYiUWlnRhHr9R5GMW9/GFVnTUU+42yAIoTDqfxsw="

# Serial Configuration for Plant SpikerBox
port_spikerbox = 'COM3'  # Update with the correct COM port for Plant SpikerBox
baud_rate_spikerbox = 230400  # Set baud rate for Plant SpikerBox
duration_spikerbox = 10  # Duration to read data in seconds

# Soil Moisture Sensor Configuration (dummy data generation for example)
def read_soil_moisture_sensor():
    # Replace this with actual code to read from your soil moisture sensor
    return np.random.rand(1000) * 1000  # Generate dummy data

def read_spikerbox_data():
    """ Read data from the Plant SpikerBox """
    ser = serial.Serial(port_spikerbox, baud_rate_spikerbox, timeout=1)
    ser.reset_input_buffer()
    ser.write(b'conf s:10000;c:1;\n')
    time.sleep(0.5)
    
    data = bytearray()
    start_time = time.time()
    
    while time.time() - start_time < duration_spikerbox:
        size = ser.in_waiting
        if size:
            data.extend(ser.read(size))
        time.sleep(0.1)
    
    ser.close()
    
    start_up_index = data.find(b'StartUp!') + 10
    data = data[start_up_index:] if start_up_index >= 10 else data

    result = []
    i = 0
    found_beginning_of_frame = False

    while i < len(data) - 1:
        if not found_beginning_of_frame:
            if data[i] > 127:
                found_beginning_of_frame = True
                int_out = ((data[i] & 127) << 7)
                i += 1
                int_out += data[i]
                result.append(int_out)
        else:
            int_out = ((data[i] & 127) << 7)
            i += 1
            int_out += data[i]
            result.append(int_out)
        i += 1

    return np.array(result)

def send_data_to_azure(spikerbox_data, soil_moisture_data):
    """ Send Plant SpikerBox and soil moisture data to Azure IoT Hub """
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    data_json = json.dumps({
        'spikerbox_data': spikerbox_data.tolist(),
        'soil_moisture_data': soil_moisture_data.tolist()
    })
    message = Message(data_json)
    message.content_encoding = "utf-8"
    message.content_type = "application/json"
    client.send_message(message)
    print("Data sent to Azure IoT Hub")
    client.disconnect()

def data_processing():
    """ Process data from both sensors and send to Azure """
    while True:
        spikerbox_data = read_spikerbox_data()
        soil_moisture_data = read_soil_moisture_sensor()
        send_data_to_azure(spikerbox_data, soil_moisture_data)
        plot_data(spikerbox_data, soil_moisture_data)
        time.sleep(duration_spikerbox)

def plot_data(spikerbox_data, soil_moisture_data):
    """ Plot the data from both sensors """
    plt.figure(figsize=(12, 6))

    # Plot SpikerBox data
    plt.subplot(2, 1, 1)
    plt.plot(spikerbox_data, label='SpikerBox Signal')
    plt.title('Signal from Plant SpikerBox')
    plt.xlabel('Sample Index')
    plt.ylabel('Signal Amplitude')
    plt.ylim(0, 1000)
    plt.legend()

    # Plot Soil Moisture data
    plt.subplot(2, 1, 2)
    plt.plot(soil_moisture_data, label='Soil Moisture Data', color='orange')
    plt.title('Soil Moisture Data')
    plt.xlabel('Sample Index')
    plt.ylabel('Moisture Level')
    plt.ylim(0, 1000)
    plt.legend()

    plt.tight_layout()
    plt.show()

# Start the background thread
thread = threading.Thread(target=data_processing)
thread.start()

# Main thread for Pygame (optional for visualization)
import pygame

# Initialize Pygame
pygame.init()
display_width = 1920
display_height = 1100
screen = pygame.display.set_mode((display_width, display_height))

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
