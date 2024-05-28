import threading
import serial
import time
import numpy as np
from azure.iot.device import IoTHubDeviceClient, Message, exceptions
import json
import pygame
import RPi.GPIO as GPIO
from queue import Queue
import requests
from io import BytesIO

# Initialize Pygame
pygame.init()

# Set the display size
# Set the display to full screen with specified size
display_width, display_height = 1920, 1100
screen = pygame.display.set_mode((display_width, display_height))

# Load and scale icons
dry_icon = pygame.image.load('dry.png')
wet_icon = pygame.image.load('wet.png')
dry_icon = pygame.transform.scale(dry_icon, (display_width, display_height))
wet_icon = pygame.transform.scale(wet_icon, (display_width, display_height))
initial_text = "Touch me to help me painting"
painting_text = "Wait! I am painting"

# Communication queue for display updates
display_queue = Queue()

# Configuration parameters
port = '/dev/ttyACM0'  # Update with the correct serial port
baud_rate = 230400  # Set baud rate
duration = 10  # Duration to read data in seconds

# Azure IoT Hub Configuration
CONNECTION_STRING = "HostName=PlantEmot.azure-devices.net;DeviceId=IoTDevice1;SharedAccessKey=qa8Fn6cRYs+CfBleDLRhdLB1t/LmUF/1BAIoTFqnrmA="

# Soil Moisture Sensor Configuration
GPIO.setmode(GPIO.BCM)
MOISTURE_SENSOR_PIN = 14
GPIO.setup(MOISTURE_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def read_serial_data(port, baud_rate, duration=10):
    """Read data from the serial port."""
    try:
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
    
    except serial.SerialException as e:
        print(f"Error reading from serial port: {e}")
        return np.array([])

def update_display():
    while True:
        is_dry = GPIO.input(MOISTURE_SENSOR_PIN)
        display_queue.put(('dry' if is_dry else 'wet', None))
        time.sleep(1)  # Update every second

def data_processing():
    """Background thread for data processing."""
    while True:
        # Read soil moisture sensor once
        is_dry = GPIO.input(MOISTURE_SENSOR_PIN)

        # Read serial data
        signal_data = read_serial_data(port, baud_rate)

        # Send data to Azure IoT Hub
        send_data_to_azure(signal_data, 'dry' if is_dry else 'wet')        
        
        # Rest for 1 minute
        time.sleep(60)

def handle_display():
    image_display_end_time = None
    current_image = None

    current_text = initial_text
    font = pygame.font.SysFont(None, 48)
    
    while True:
        current_time = time.time()

        # Check if there's a new image to display
        if not display_queue.empty():
            status, image = display_queue.get()
            screen.fill((255, 255, 255))  # Clear the screen with white background

            if image:
                current_image = image
                image_display_end_time = current_time + 10  # Set end time for image display
                current_text = initial_text  # Reset to initial text when an image is received
                print(f"Image display start time: {current_time}")
                print(f"Image display end time: {image_display_end_time}")
            else:
                if current_image is None:
                    if status == 'dry':
                        screen.blit(dry_icon, (0, 0))
                    else:
                        screen.blit(wet_icon, (0, 0))
                    pygame.display.update()

        # Continue displaying the current image if the time has not elapsed
        if current_image and image_display_end_time:
            if current_time < image_display_end_time:
                screen.fill((255, 255, 255))  # Clear the screen with white background
                screen.blit(current_image, (0, 0))
                pygame.display.update()
                print(f"Displaying image. Current time: {current_time}")
            else:
                print(f"Time exceeded. Current time: {current_time}")
                current_image = None  # Reset the current image after 60 seconds
                image_display_end_time = None

        # Display the current text if no image is being displayed
        if current_image is None:
            screen.fill((255, 255, 255))  # Clear the screen with white background
            if status == 'dry':
                screen.blit(dry_icon, (0, 0))
            else:
                screen.blit(wet_icon, (0, 0))
            text_surface = font.render(current_text, True, (0, 0, 0))
            screen.blit(text_surface, (10, 10))
            pygame.display.update()

        time.sleep(1)  # Sleep for a short time to reduce CPU usage

def send_data_to_azure(signal_data, soil_moisture, downsample_factor=100):
    """Send signal and soil moisture data to Azure IoT Hub in chunks."""
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

    try:
        # Downsample the data
        downsampled_data = signal_data[::downsample_factor]
        data_list = downsampled_data.tolist()
        
        data_json = json.dumps({
            'signal_data': data_list,
            'soil_moisture': soil_moisture
        })
        
        message = Message(data_json)
        message.content_encoding = "utf-8"
        message.content_type = "application/json"

        retries = 0
        max_retries = 5
        retry_delay = 2

        while retries < max_retries:
            try:
                client.send_message(message)
                print("Data sent to Azure IoT Hub")
                display_queue.put((None, painting_text))  # Update the text after sending data
                break  # Exit the retry loop if the message is sent successfully
            except (exceptions.ConnectionDroppedError, exceptions.ClientError) as e:
                retries += 1
                print(f"Connection error: {e}. Retrying ({retries}/{max_retries})...")
                time.sleep(retry_delay)
        else:
            print("Failed to send data after multiple attempts.")
    
    except ValueError as e:
        print(f"Failed to send data: {e}")
    
    finally:
        client.disconnect()


def iot_message_listener():
    """Listener for IoT Hub messages."""
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

    def message_handler(message):
        try:
            # Log received message for debugging
            print(f"Received message: {message.data}")
            
            # Check if the message data is not empty
            if not message.data:
                print("Received empty message.")
                return

            # Strip any leading/trailing whitespace and parse the JSON data
            message_str = message.data.decode('utf-8').strip()
            print(f"Stripped message: {message_str}")
            
            message_data = json.loads(message_str)
            print(f"Parsed message data: {message_data}")

            image_url = message_data.get('image_url')
            if image_url:
                print(f"Fetching image from URL: {image_url}")
                response = requests.get(image_url)
                image = pygame.image.load(BytesIO(response.content))
                image = pygame.transform.scale(image, (display_width, display_height))
                display_queue.put((None, image))
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON from message data: {e}")
        except Exception as e:
            print(f"Failed to process message: {e}")

    client.on_message_received = message_handler

    while True:
        try:
            client.connect()
            print("Client connected to IoT Hub.")
            while True:
                time.sleep(1)  # Keep the thread alive to listen for messages
        except (exceptions.ConnectionDroppedError, exceptions.ClientError) as e:
            print(f"Connection error: {e}. Retrying connection...")
            time.sleep(10)
        except KeyboardInterrupt:
            print("Receiving messages stopped.")
            break
        finally:
            if client.connected:
                client.shutdown()

def main():
    # Start the background thread for data processing
    data_thread = threading.Thread(target=data_processing)
    data_thread.daemon = True  # Ensure the thread exits when the main program exits
    data_thread.start()

    # Start the thread for real-time soil moisture display updates
    display_thread = threading.Thread(target=update_display)
    display_thread.daemon = True
    display_thread.start()

    # Start the thread for IoT message listening
    iot_listener_thread = threading.Thread(target=iot_message_listener)
    iot_listener_thread.daemon = True
    iot_listener_thread.start()

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
