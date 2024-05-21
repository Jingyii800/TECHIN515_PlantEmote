import azure.functions as func
import logging
import json
import numpy as np
import matplotlib.pyplot as plt
import io
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp()

@app.event_hub_message_trigger(arg_name="azeventhub", event_hub_name="plantemot",
                               connection="IOTHUB_CONNECTION_STRING")
def dataProcess(azeventhub: func.EventHubEvent):
    logging.info('Python EventHub trigger processed an event: %s',
                 azeventhub.get_body().decode('utf-8'))

    # Decode the message and convert from JSON
    message_body = azeventhub.get_body().decode('utf-8')
    data = json.loads(message_body)
    signal_data = np.array(data['signal'])
    sample_rate = data.get('sample_rate', 1000)  # Default sample rate if not provided
    index = data.get('index', datetime.datetime.now().strftime("%Y%m%d%H%M%S"))  # Use current timestamp if index not provided

    # Azure Blob Storage setup
    connect_str = "AZURE_STORAGE_CONNECTION_STRING"
    container_name = "plantemot"
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Generate and upload the standard plot
    plot_buffer = generate_plot(signal_data, sample_rate)
    plot_blob_name = f'{index}_standard_plot.png'
    upload_blob(blob_service_client, container_name, plot_blob_name, plot_buffer)

    # Generate and upload the artistic image
    art_buffer = generate_artistic_image(signal_data)
    art_blob_name = f'{index}_artistic_image.png'
    upload_blob(blob_service_client, container_name, art_blob_name, art_buffer)

def generate_plot(data, sample_rate):
    # Calculate the time vector based on the sample rate
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
    # Create an artistic representation of the data
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
    logging.info(f"{blob_name} uploaded to Azure Blob Storage.")
