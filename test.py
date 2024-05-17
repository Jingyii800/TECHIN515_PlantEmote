import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter

# Audio Configuration
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 9600  # Sample rate
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

def audio_stream():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, input_device_index=1)

    # Initialize Matplotlib for real-time plotting
    plt.ion()
    fig, ax = plt.subplots()
    x = np.arange(0, CHUNK)
    line_left, = ax.plot(x, np.random.rand(CHUNK), label='Left Channel')
    line_right, = ax.plot(x, np.random.rand(CHUNK), label='Right Channel')
    ax.set_ylim(-9600, 9600)
    ax.set_xlim(0, CHUNK)
    ax.legend()
    fig.show()

    try:
        while True:
            frames = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
            frames = frames.reshape(-1, 2)  # Reshape to (CHUNK, CHANNELS)
            left_channel = frames[:, 0]
            right_channel = frames[:, 1]
            
            filtered_left = apply_filter(left_channel, cutoff=200, fs=RATE, order=2)
            filtered_right = apply_filter(right_channel, cutoff=200, fs=RATE, order=2)
            
            # Update Matplotlib plot
            line_left.set_ydata(filtered_left)
            line_right.set_ydata(filtered_right)
            fig.canvas.draw()
            fig.canvas.flush_events()
    except KeyboardInterrupt:
        print("Interrupted")
    finally:
        stream.close()
        p.terminate()

if __name__ == "__main__":
    audio_stream()


