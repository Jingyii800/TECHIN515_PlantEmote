import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pyaudio
import threading

# Audio Configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 9600  # Updated sample rate
CHUNK = 1024  # Samples per frame
DISPLAY_SIZE = RATE * 20  # 20 seconds of data at 9600 Hz

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open audio stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=0,
                frames_per_buffer=CHUNK)

# Buffer to store audio data
sample_buffer = np.zeros(DISPLAY_SIZE)

def amplitude_filter(data, threshold=250):
    """Zero out changes that are within the threshold range."""
    filtered_data = np.where((data < threshold) & (data > -threshold), 0, data)
    return filtered_data

def moving_average_filter(data, window_size=50):
    """Smooth data using a moving average filter."""
    cumsum_vec = np.cumsum(np.insert(data, 0, 0)) 
    smoothed = (cumsum_vec[window_size:] - cumsum_vec[:-window_size]) / window_size
    return np.concatenate((data[:window_size-1], smoothed))

def handle_data(data):
    """Processes chunks of data just acquired."""
    global sample_buffer
    differential_data = np.diff(data, prepend=data[0])
    amplitude_filtered = amplitude_filter(differential_data)
    smoothed_data = moving_average_filter(amplitude_filtered)
    # Roll the buffer to discard the oldest chunk
    sample_buffer = np.roll(sample_buffer, -len(smoothed_data))
    # Insert the new chunk at the end of the buffer
    sample_buffer[-len(smoothed_data):] = smoothed_data

def update_plot(frame):
    """Update the plot with new data."""
    line.set_ydata(sample_buffer)
    return line,

def read_from_stream():
    """Thread function to continuously read from the audio stream."""
    while True:
        data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
        handle_data(data)

# Start the audio reading in a separate thread
thread = threading.Thread(target=read_from_stream)
thread.start()

# Setup the matplotlib plot
fig, ax = plt.subplots()
x = np.linspace(-20, 0, num=DISPLAY_SIZE)
line, = ax.plot(x, np.zeros(DISPLAY_SIZE), '-', lw=1)
ax.set_ylim(-750, 750)  # Set fixed y-limits

# Create animation
ani = FuncAnimation(fig, update_plot, blit=True, interval=50, repeat=True)

plt.show()

# Clean up on exit
stream.stop_stream()
stream.close()
p.terminate()
thread.join()





