# import pyaudio

# # Create a PyAudio object
# p = pyaudio.PyAudio()

# # Print the index and name of each audio device found
# info = p.get_host_api_info_by_index(0)
# num_devices = info.get('deviceCount')

# # Loop through all the devices and print their information
# for i in range(0, num_devices):
#     device_info = p.get_device_info_by_host_api_device_index(0, i)
#     if device_info.get('maxInputChannels') > 0:  # Only show devices that can handle input
#         print(f"Device ID {i}: {device_info.get('name')} - Max Input Channels: {device_info.get('maxInputChannels')}")

# # Terminate the PyAudio connection
# p.terminate()
import serial
import threading

# Setup the serial connection
ser = serial.Serial('COM3', 9600)  # Update 'COM3' to your port number

def read_from_port(ser):
    while True:
        reading = ser.readline().decode().strip()
        print("Read data:", reading)

# Start a thread to read from the USB device
thread = threading.Thread(target=read_from_port, args=(ser,))
thread.start()

# Remember to close the serial port when done

