import threading
import serial
import time
import matplotlib.pyplot as plt 
import numpy as np

global connected
connected = False
port = ''
baud = 230400
global input_buffer
global sample_buffer
global cBufTail
cBufTail = 0
input_buffer = []
sample_rate = 10000
display_size = 200000  # 20 seconds of data
sample_buffer = np.linspace(0,0,display_size)
serial_port = serial.Serial(port, baud, timeout=0)

def checkIfNextByteExist():
    global cBufTail
    global input_buffer
    tempTail = cBufTail + 1
    if tempTail == len(input_buffer): 
        return False
    return True

def checkIfHaveWholeFrame():
    global cBufTail
    global input_buffer
    tempTail = cBufTail + 1
    while tempTail != len(input_buffer): 
        nextByte  = input_buffer[tempTail] & 0xFF
        if nextByte > 127:
            return True
        tempTail = tempTail + 1
    return False

def areWeAtTheEndOfFrame():
    global cBufTail
    global input_buffer
    tempTail = cBufTail + 1
    nextByte  = input_buffer[tempTail] & 0xFF
    if nextByte > 127:
        return True
    return False

def numberOfChannels():
    return 1

def handle_data(data):
    global input_buffer
    global cBufTail
    global sample_buffer    
    if len(data) > 0:
        cBufTail = 0
        haveData = True
        weAlreadyProcessedBeginingOfTheFrame = False
        numberOfParsedChannels = 0
        
        while haveData:
            MSB = input_buffer[cBufTail] & 0xFF
            
            if MSB > 127:
                weAlreadyProcessedBeginingOfTheFrame = False
                numberOfParsedChannels = 0
                
                if checkIfHaveWholeFrame():
                    while True:
                        MSB = input_buffer[cBufTail] & 0x7F
                        weAlreadyProcessedBeginingOfTheFrame = True
                        cBufTail += 1
                        LSB = input_buffer[cBufTail] & 0xFF
                        if LSB > 127:
                            break
                        LSB = input_buffer[cBufTail] & 0x7F
                        MSB = MSB << 7
                        writeInteger = LSB | MSB
                        numberOfParsedChannels += 1
                        if numberOfParsedChannels > numberOfChannels():
                            break
                        sample_buffer = np.append(sample_buffer[1:], writeInteger - 512)
                        if areWeAtTheEndOfFrame():
                            break
                        cBufTail += 1
                else:
                    haveData = False
                    break
            cBufTail += 1
            if cBufTail == len(input_buffer):
                haveData = False
                break

def read_from_port(ser):
    global connected
    global input_buffer
    while not connected:
        connected = True
        while True:
            reading = ser.read(1024)
            if len(reading) > 0:
                reading = list(reading)
                input_buffer = reading.copy()
                handle_data(reading)
            time.sleep(0.001)

thread = threading.Thread(target=read_from_port, args=(serial_port,))
thread.start()
xi = np.linspace(-20, 0, num=display_size)
while True:
    plt.ion()
    plt.show(block=False)
    if len(sample_buffer) > 0:
        yi = sample_buffer.copy()
        plt.clf()
        plt.ylim(-550, 550)
        plt.plot(xi, yi, linewidth=1, color='royalblue')
        plt.pause(0.001)
        time.sleep(2)  # Update every 2 seconds

