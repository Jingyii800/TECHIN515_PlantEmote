from azure.iot.device import IoTHubDeviceClient, Message
import RPi.GPIO as GPIO
import time

# Azure IoT Hub settings
CONNECTION_STRING = "HostName=PlantEmote.azure-devices.net;DeviceId=iotdevice-1;SharedAccessKey=pfJGLHdpm1CRY938KfaME0RDeNLNkZMWiAIoTMu3IJY="
MSG_TXT = '{{"team": "team1", "soil_moisture": {soil_moisture}}}'

# Set up the GPIO with the BCM numbering scheme
GPIO.setmode(GPIO.BCM)
MOISTURE_SENSOR_PIN = 17  # GPIO pin number where sensor is connected
GPIO.setup(MOISTURE_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Create an IoT Hub client
client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

def send_to_iot_hub(soil_moisture):
    try:
        # Format the message data
        message = Message(MSG_TXT.format(soil_moisture=soil_moisture))
        message.content_encoding = "utf-8"
        message.content_type = "application/json"
        
        # Send the message
        print("Sending message: {}".format(message))
        client.send_message(message)
        print("Message successfully sent")

    except Exception as e:
        print("Error sending message to IoT Hub: {}".format(e))

def read_soil_moisture():
    # Check the moisture level
    if GPIO.input(MOISTURE_SENSOR_PIN) == GPIO.LOW:
        print("Soil is moist")
        send_to_iot_hub(1)  # You can change 1 to a sensor-specific value
    else:
        print("Soil is dry")
        send_to_iot_hub(0)  # You can change 0 to a sensor-specific value

    # Wait for a second before the next read
    time.sleep(1)

def main():
    try:
        print("IoT Hub device sending periodic messages, press Ctrl-C to exit")
        client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
        
        while True:
            read_soil_moisture()

    except KeyboardInterrupt:
        print("IoT Hub client stopped")
        
    finally:
        GPIO.cleanup()
        client.disconnect()

if __name__ == '__main__':
    main()
