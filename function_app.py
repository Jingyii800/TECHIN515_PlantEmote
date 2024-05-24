import os
import azure.functions as func
import logging
import json
import numpy as np
import matplotlib.pyplot as plt
import io
from azure.storage.blob import BlobServiceClient, BlobClient
import psycopg2
from datetime import datetime
from azure.iot.device import IoTHubDeviceClient, Message

app = func.FunctionApp()

@app.event_hub_message_trigger(arg_name="azeventhub", event_hub_name="plantemot",
                               connection="IOTHUB_CONNECTION_STRING")
def dataProcess(azeventhub: func.EventHubEvent):
    logging.info('Python EventHub trigger processed an event: %s',
                 azeventhub.get_body().decode('utf-8'))

    # Decode the message and convert from JSON
    message_body = azeventhub.get_body().decode('utf-8')
    data = json.loads(message_body)
    signal_data = np.array(data['signal_data'])
    soil_moisture = data['soil_moisture']
    sample_rate = data.get('sample_rate', 1000)
    index = data.get('index', datetime.now().strftime("%Y%m%d%H%M%S"))

    # Azure Blob Storage setup
    connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connect_str:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING is not set or is empty.")
    container_name = "plantemot"
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Generate and upload the standard plot
    plot_buffer = generate_plot(signal_data, sample_rate)
    plot_blob_name = f'{index}_standard_plot.png'
    standard_plot_url = upload_blob(blob_service_client, container_name, plot_blob_name, plot_buffer)

    # Generate and upload the artistic image
    art_buffer = generate_artistic_image(signal_data)
    art_blob_name = f'{index}_artistic_image.png'
    artistic_image_url = upload_blob(blob_service_client, container_name, art_blob_name, art_buffer)

    # Store data in PostgreSQL
    store_in_postgresql(index, signal_data, soil_moisture, standard_plot_url, artistic_image_url)

    # Send the artistic image URL to the Raspberry Pi via IoT Hub
    send_image_to_raspberry_pi(artistic_image_url)

def generate_plot(data, sample_rate):
    time_vector = np.linspace(0, 10, num=len(data))
    plt.figure()
    plt.plot(time_vector, data)
    plt.title('Standard Signal Plot')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Amplitude')
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    return buffer

def generate_artistic_image(data):
    plt.figure()
    plt.scatter(range(len(data)), data, c=data, cmap='viridis', alpha=0.5)
    plt.colorbar()
    plt.title('Artistic Signal Representation')
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    return buffer

def upload_blob(blob_service_client, container_name, blob_name, buffer):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_client.upload_blob(buffer.getvalue(), overwrite=True)
    buffer.close()
    blob_url = blob_client.url
    logging.info(f"{blob_name} uploaded to Azure Blob Storage.")
    return blob_url

def store_in_postgresql(index, signal_data, soil_moisture, standard_plot_url, artistic_image_url):
    connection_string = os.getenv("DATABASE_URL")
    if not connection_string:
        raise ValueError("DATABASE_URL is not set or is empty.")
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    signal_data_json = json.dumps(signal_data.tolist())
    cursor.execute("INSERT INTO telemetry_data (index, signal_data, soil_moisture, standard_plot_url, artistic_image_url) VALUES (%s, %s, %s, %s, %s)",
                   (index, signal_data_json, soil_moisture, standard_plot_url, artistic_image_url))
    conn.commit()
    cursor.close()
    conn.close()
    logging.info("Data and URLs stored in PostgreSQL database.")

def send_image_to_raspberry_pi(image_url):
    IOTHUB_CONNECTION_STRING = os.getenv("IOT_SEND_DATA_CONNECTION_STRING")

    if not IOTHUB_CONNECTION_STRING:
        raise ValueError("IOTHUB_CONNECTION_STRING is not set or is empty.")

    try:
        # Create the IoT Hub client
        client = IoTHubDeviceClient.create_from_connection_string(IOTHUB_CONNECTION_STRING)
        
        # Connect the client
        client.connect()
        logging.info("Client connected to IoT Hub.")

        # Create the message
        message = Message(json.dumps({'image_url': image_url}))
        message.content_encoding = "utf-8"
        message.content_type = "application/json"

        # Send the message
        logging.info(f"Sending message: {message}")
        client.send_message(message)
        logging.info("Message successfully sent to IoT Hub")

    except Exception as e:
        logging.error(f"Failed to send image URL to Raspberry Pi: {e}")

    finally:
        # Ensure the client is disconnected properly
        if client.connected:
            client.disconnect()
            logging.info("Client disconnected from IoT Hub")
