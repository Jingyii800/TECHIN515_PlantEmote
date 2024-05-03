import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pyaudio
import threading

# Audio Configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 9600  # Sample rate
CHUNK = 1024  # Samples per frame
DISPLAY_SIZE = RATE * 20  # 20 seconds of data at 9600 Hz

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open audio stream with specified input device
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                input_device_index=0)  # Specify your device index here

# Buffer to store differential audio data
diff_buffer = np.zeros(DISPLAY_SIZE)

def moving_average(data, window_size=50):
    """Compute the moving average of the data."""
    cumsum_vec = np.cumsum(np.insert(data, 0, 0)) 
    ma_vec = (cumsum_vec[window_size:] - cumsum_vec[:-window_size]) / window_size
    return np.concatenate((data[:window_size-1], ma_vec))  # Pad the start with original data

def handle_data(data):
    """Processes chunks of data just acquired and stores the first difference after smoothing."""
    global diff_buffer
    # Apply moving average filter
    smoothed_data = moving_average(data)
    # Compute first difference
    diff_data = np.diff(smoothed_data, prepend=smoothed_data[0])
    # Roll the buffer to discard the oldest chunk
    diff_buffer = np.roll(diff_buffer, -len(diff_data))
    # Insert the new chunk at the end of the buffer
    diff_buffer[-len(diff_data):] = diff_data

def update_plot(frame):
    """Update the plot with new data."""
    line.set_ydata(diff_buffer)
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
ax.set_ylim(-700, 700)  # Adjusted y-limits to focus on typical differential values

# Create animation
ani = FuncAnimation(fig, update_plot, blit=True, interval=50, repeat=True)

plt.show()

# Clean up on exit
stream.stop_stream()
stream.close()
p.terminate()
thread.join()





