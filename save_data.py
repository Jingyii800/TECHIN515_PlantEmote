import serial
import time

# Configuration parameters
port = 'COM4'  # Update with the correct COM port
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

# Process the data to find the starting point
start_up_index = data.find(b'StartUp!') + 10
data = data[start_up_index:] if start_up_index >= 10 else data

# Convert to integer values and save to file
result = []
i = 0
while i < len(data) - 1:
    int_out = ((data[i] & 127) << 7) + data[i+1]
    result.append(int_out)
    i += 2

# Save data to a file
with open('data.txt', 'w') as f:
    for value in result:
        f.write(f"{value}\n")
