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
from azure.iot.device import Message
from azure.iot.hub import IoTHubRegistryManager
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import LinearSegmentedColormap

app = func.FunctionApp()

@app.event_hub_message_trigger(arg_name="azeventhub", event_hub_name="plantemot",
                               connection="IOTHUB_CONNECTION_STRING")
def dataProcess(azeventhub: func.EventHubEvent):
    logging.info('Python EventHub trigger processed an event: %s',
                 azeventhub.get_body().decode('utf-8'))

    # Decode the message and convert from JSON
    message_body = azeventhub.get_body().decode('utf-8')
    data = json.loads(message_body)

    # Check if the required keys are present to avoid loops
    if 'signal_data' not in data or 'soil_moisture' not in data:
        logging.warning("The message does not contain required fields 'signal_data' and 'soil_moisture'. Ignoring this message.")
        return
    
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
    plt.plot(time_vector, data, color='darkgreen')
    plt.ylim(0, 1000)  # Set y-axis limits
    plt.xlabel('Time (seconds)')
    plt.ylabel('Sensitivity Strength (Higher means stronger reaction)')
    plt.gca().spines['top'].set_color('none')
    plt.gca().spines['right'].set_color('none')
    plt.gca().spines['left'].set_color('#E4EFE1')
    plt.gca().spines['bottom'].set_color('#E4EFE1')
    plt.gca().patch.set_alpha(0)  # Set background to transparent
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', transparent=True)
    buffer.seek(0)
    return buffer

def generate_artistic_image(data):
    # Normalize data for better color mapping within 400-600 and above 600
    data_normalized = np.zeros_like(data, dtype=float)
    data_normalized[data <= 600] = (data[data <= 600] - 400) / (600 - 400)
    data_normalized[data > 600] = 1 + (data[data > 600] - 600) / (data.max() - 600)

    # Set up the plot with the specified size
    display_width = 1920
    display_height = 1100
    fig, ax = plt.subplots(figsize=(display_width / 100, display_height / 100))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect('equal')

    # Create a custom colormap with lower saturation and more transparent colors
    colors = [(0, "#B3E5FC"), (0.25, "#B2DFDB"), (0.4, "#FFF9C4"), (0.65, "#FFCC80"), (1, "#FFAB91")]
    cmap = LinearSegmentedColormap.from_list("custom_cmap", colors, N=512)

    # Create a gradient background
    gradient = np.linspace(0, 1, 512)
    gradient = np.vstack((gradient, gradient))
    ax.imshow(gradient, aspect='auto', cmap=cmap, extent=[0, 100, 0, 100])

    # Generate random polygons and color them based on normalized data values
    patches = []
    polygon_colors = []
    polygon_alphas = []
    num_polygons = 80  # More polygons for a richer look
    for _ in range(num_polygons):
        num_sides = np.random.randint(3, 10)
        base_radius = 5 + np.random.rand() * 20  # Variable radius for diversity
        position = np.random.rand(2) * 100  # Position on the canvas
        color_index = np.random.randint(0, len(data_normalized))  # Choose a random index
        color_val = data_normalized[color_index]  # Use normalized data value for color
        angles = np.linspace(0, 2 * np.pi, num_sides, endpoint=False)
        radius_noise = base_radius + np.random.rand(num_sides) * 10 - 5  # Add noise to radius
        polygon_points = np.c_[radius_noise * np.cos(angles), radius_noise * np.sin(angles)] + position
        polygon = Polygon(polygon_points, closed=True)
        patches.append(polygon)
        polygon_colors.append(color_val)  # Color mapped by normalized data value
        polygon_alphas.append(0.3 + 0.5 * color_val)  # Alpha value based on normalized data

    # Ensure the alpha values are within the 0-1 range
    polygon_alphas = np.clip(polygon_alphas, 0, 1)

    # Create color mapping using the custom colormap
    colors_rgba = cmap(np.clip(np.array(polygon_colors), 0, 1))

    # Adjust color saturation and alpha to add more richness
    for i in range(len(colors_rgba)):
        color_noise = np.random.rand() * 0.1 - 0.05  # Add small noise to color
        alpha_noise = np.random.rand() * 0.2 - 0.1  # Add small noise to alpha
        colors_rgba[i][:3] = np.clip(colors_rgba[i][:3] + color_noise, 0, 1)  # Adjust color
        colors_rgba[i][-1] = np.clip(polygon_alphas[i] + alpha_noise, 0, 1)  # Adjust alpha

    # Add polygons to the plot
    p = PatchCollection(patches, facecolors=colors_rgba, edgecolors='none')
    ax.add_collection(p)

    # Remove axes for a cleaner look
    ax.set_axis_off()

    # Save plot to buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', transparent=True)
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
    IOTHUB_SEND_CONNECTION_STRING = os.getenv("IOT_SEND_DATA_CONNECTION_STRING")
    DEVICE_ID = "IoTDevice1"  # Make sure to use the correct device ID

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