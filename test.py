import os
import logging
import json
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.device import Message

def send_image_to_raspberry_pi(image_url):
    IOTHUB_SEND_CONNECTION_STRING = "HostName=PlantEmot.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=nJD4Sl3l1q4ozB7yW2qFjNprworv8DR0jAIoTOg75ME="
    DEVICE_ID = "IoTDevice1"  # Ensure this is the correct device ID

    if not IOTHUB_SEND_CONNECTION_STRING:
        raise ValueError("IOT_SEND_DATA_CONNECTION_STRING is not set or is empty.")

    try:
        # Create the IoT Hub registry manager
        registry_manager = IoTHubRegistryManager(IOTHUB_SEND_CONNECTION_STRING)

        # Create the message
        message_data = {'image_url': image_url}
        message_json = json.dumps(message_data).strip()  # Ensure JSON is well-formatted
        logging.info(f"Formatted message JSON: {message_json}")
        
        props = {
            "contentType": "application/json"
        }

        # Send the message to the specified device
        logging.info(f"Sending message to device {DEVICE_ID}: {message_json}")
        registry_manager.send_c2d_message(DEVICE_ID, message_json, properties=props)
        logging.info("Message successfully sent to IoT Hub")

    except Exception as e:
        logging.error(f"Failed to send image URL to Raspberry Pi: {e}")

# Example usage for testing
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    test_image_url = "https://plantemot.blob.core.windows.net/plantemot/20240524001138_artistic_image.png"
    send_image_to_raspberry_pi(test_image_url)
