import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pyaudio
import threading
from scipy.signal import savgol_filter

# Audio Configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 9600  # Sample rate
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

def detect_events(data, threshold=500):
    """Detect significant changes based on a threshold."""
    events = np.abs(data) > threshold
    return events

def handle_data(data):
    """Processes chunks of data just acquired."""
    global sample_buffer
    # Apply Savitzky-Golay filter for smoothing
    smoothed_data = savgol_filter(data, 51, 3)  # Window size 51, polynomial order 3
    # Detect events
    events = detect_events(smoothed_data)
    # Highlight events by setting to a max or min value
    smoothed_data[events] = np.sign(smoothed_data[events]) * 7000
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
ax.set_ylim(-7000, 7000)  # Set fixed y-limits

# Create animation
ani = FuncAnimation(fig, update_plot, blit=True, interval=50, repeat=True)

plt.show()

# Clean up on exit
stream.stop_stream()
stream.close()
p.terminate()
thread.join()






