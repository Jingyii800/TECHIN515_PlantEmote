import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pyaudio
import threading
from scipy.signal import butter, lfilter

# Audio Configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 9600  # Sample rate
CHUNK = 1024  # Samples per frame
DISPLAY_SIZE = RATE * 20  # 20 seconds of data

# Initialize PyAudio
p = pyaudio.PyAudio()

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

def handle_data(data):
    """ Process incoming data """
    global audio_buffer
    # Apply high-pass filter to remove low-frequency drift
    filtered_data = apply_filter(data, cutoff=200, fs=RATE, type='high', order=2)
    # Update the audio buffer with new filtered data
    audio_buffer = np.roll(audio_buffer, -len(filtered_data))
    audio_buffer[-len(filtered_data):] = filtered_data

def update_plot(frame):
    """ Update the plot with new audio data """
    line.set_ydata(audio_buffer)
    return line,

def read_from_stream():
    """ Continuously read from audio stream """
    while True:
        frames = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
        handle_data(frames)

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

