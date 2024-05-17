import serial
import time
import matplotlib.pyplot as plt
import numpy as np

# Configuration parameters
port = 'COM3'  # Update with the correct COM port
baud_rate = 230400  # Set baud rate
duration = 10  # Duration to read data in seconds

# Set up serial connection
ser = serial.Serial(port, baud_rate, timeout=1)
ser.reset_input_buffer()

# Send configuration command to the device
ser.write(b'conf s:10000;c:1;\n')  # Adjust as necessary based on device requirements

time.sleep(0.5)  # Give some time for the device to respond and start sending data

data = bytearray()
start_time = time.time()

# Collect data for approximately 10 seconds
while time.time() - start_time < duration:
    size = ser.in_waiting
    if size:
        data.extend(ser.read(size))
    time.sleep(0.1)  # Short delay to avoid hogging the CPU

# Close the serial port
ser.close()

# Process the data
# Eliminate 'StartUp!' string and new line characters (if present)
start_up_index = data.find(b'StartUp!') + 10
data = data[start_up_index:] if start_up_index >= 10 else data

# Unpack the data from frames
result = []
i = 0
found_beginning_of_frame = False

while i < len(data) - 1:
    if not found_beginning_of_frame:
        # Frame begins with MSB set to 1
        if data[i] > 127:
            found_beginning_of_frame = True
            # Extract one sample from 2 bytes
            int_out = ((data[i] & 127) << 7)
            i += 1
            int_out += data[i]
            result.append(int_out)
    else:
        # Extract one sample from 2 bytes
        int_out = ((data[i] & 127) << 7)
        i += 1
        int_out += data[i]
        result.append(int_out)
    i += 1

# Convert result to a numpy array for better handling
result_array = np.array(result)

# Plot the data
plt.figure(figsize=(10, 5))
plt.plot(result_array, label='EEG or EKG Signal from SpikerShield')
plt.title('Signal from Plant SpikerShield')
plt.xlabel('Sample Index')
plt.ylabel('Signal Amplitude')
plt.ylim(0, 1000)  # Set y-axis range
plt.legend()
plt.show()

