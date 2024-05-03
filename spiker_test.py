import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pyaudio
import threading
import time
from scipy.signal import butter, lfilter

# Audio Configuration
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100  # Sample rate, adjust if different
CHUNK = 1024  # Samples per frame
DISPLAY_SIZE = 200000  # Display size for the plot

# Initialize PyAudio
p = pyaudio.PyAudio()

# Print the index and name of each audio device found
info = p.get_host_api_info_by_index(0)
num_devices = info.get('deviceCount')

# Loop through all the devices and print their information
for i in range(0, num_devices):
    device_info = p.get_device_info_by_host_api_device_index(0, i)
    if device_info.get('maxInputChannels') > 0:  # Only show devices that can handle input
        print(f"Device ID {i}: {device_info.get('name')} - Max Input Channels: {device_info.get('maxInputChannels')}")

# Terminate the PyAudio connection
p.terminate()
# Open audio stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=1,
                frames_per_buffer=CHUNK)

# Buffer to store audio data
sample_buffer = np.zeros(DISPLAY_SIZE)

def butter_lowpass_filter(data, cutoff=1000, fs=44100, order=5):
    """Apply a Butterworth low-pass filter."""
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return lfilter(b, a, data)

def handle_data(data):
    """Processes chunks of data just acquired."""
    global sample_buffer
    # Filter the data
    filtered_data = butter_lowpass_filter(data)
    # Roll the buffer to discard the oldest chunk
    sample_buffer = np.roll(sample_buffer, -len(filtered_data))
    # Insert the new chunk at the end of the buffer
    sample_buffer[-len(filtered_data):] = filtered_data

def update_plot(frame):
    """Update the plot with new data."""
    line.set_ydata(sample_buffer)
    return line,

def read_from_stream():
    """Thread function to continuously read from the audio stream."""
    while True:
        data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
        handle_data(data)
        time.sleep(0.001)  # Small delay to prevent CPU overuse

# Start the audio reading in a separate thread
thread = threading.Thread(target=read_from_stream)
thread.start()

# Setup the matplotlib plot
fig, ax = plt.subplots()
x = np.linspace(-DISPLAY_SIZE / RATE, 0, num=DISPLAY_SIZE)
line, = ax.plot(x, np.zeros(DISPLAY_SIZE), '-', lw=1)
ax.set_ylim(-32768, 32767)  # Adjust y-limits to fit 16-bit audio range
ax.set_xlim(min(x), max(x))

# Create animation
ani = FuncAnimation(fig, update_plot, blit=True, interval=50, repeat=True)

plt.show()

# Clean up on exit
stream.stop_stream()
stream.close()
p.terminate()
thread.join()


