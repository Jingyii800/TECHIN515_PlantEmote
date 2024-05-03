import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pyaudio
import threading
from scipy.signal import butter, filtfilt

# Audio Configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100  # Sample rate
CHUNK = 1024  # Samples per frame
DISPLAY_SIZE = RATE * 20  # 20 seconds of data at 44100 Hz

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

def butter_highpass_filter(data, cutoff=20, fs=44100, order=5):
    """Apply a Butterworth high-pass filter."""
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return filtfilt(b, a, data)

def normalize_data(data):
    """Normalize data to the range -1 to 1."""
    data_max = np.max(np.abs(data))
    if data_max == 0:
        return data  # Prevent division by zero
    return data / data_max

def handle_data(data):
    """Processes chunks of data just acquired."""
    global sample_buffer
    filtered_data = butter_highpass_filter(data)
    normalized_data = normalize_data(filtered_data)
    # Roll the buffer to discard the oldest chunk
    sample_buffer = np.roll(sample_buffer, -len(normalized_data))
    # Insert the new chunk at the end of the buffer
    sample_buffer[-len(normalized_data):] = normalized_data

def update_plot(frame):
    """Update the plot with new data."""
    line.set_ydata(sample_buffer * 30000)  # Scale up for visibility
    ax.relim()  # Recompute the ax.dataLim
    ax.autoscale_view()  # Update the axis limits
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
ax.set_ylim(-1, 1)  # Start with normalized y-limits

# Create animation
ani = FuncAnimation(fig, update_plot, blit=True, interval=50, repeat=True)

plt.show()

# Clean up on exit
stream.stop_stream()
stream.close()
p.terminate()
thread.join()




