import os
import logging
from flask import Blueprint, jsonify, render_template, request
from .database import get_db_connection
from openai import OpenAI
from dotenv import load_dotenv

main = Blueprint('main', __name__)
load_dotenv()
client = OpenAI(
api_key=os.getenv("OPENAI_API_KEY"),
base_url="https://openai.ianchen.io/v1",
)

os.environ.get("OPENAI_API_KEY")

# Global variable to store the latest plot URL
latest_plot_url = None
recent_urls = None

@main.route('/')
def index():
    global latest_plot_url 
    global recent_urls
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT soil_moisture, standard_plot_url, artistic_image_url FROM telemetry_data ORDER BY index DESC LIMIT 10;')
    data = cur.fetchall()
    cur.close()
    conn.close()
   
    if data:
        newest_data = data[0]
        recent_urls = [entry[1] for entry in data]
        latest_plot_url = newest_data[1]  # Store the latest plot URL
        previous_art_urls = [entry[2] for entry in data[1:]]
        return render_template('index.html', soil_moisture=newest_data[0], 
                               plot_url=newest_data[1], image_url=newest_data[2], 
                               previous_art_urls=previous_art_urls)
    else:
        return render_template('index.html', 
                               soil_moisture='No data', 
                               plot_url=None, image_url=None)
    
@main.route('/plant-data', methods=['GET'])
def plant_data():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT soil_moisture, standard_plot_url, artistic_image_url FROM telemetry_data ORDER BY index DESC LIMIT 10;')
    data = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(data)

@main.route('/ask_question', methods=['POST'])
def ask_question():
    question = request.json.get('question')
    try:
        if question == "How's your feeling now?":
            if not latest_plot_url:
                return jsonify({'answer': 'Error: No plot available'}), 500
            custom_prompt = (
                f"This is the Mimosa's Electrophysiological Signal in 10 seconds,"
                f"please refer to the plot at {latest_plot_url}, then answer as the perspective "
                f"of the mimosa the question 'what is the feeling now', no more than 20 words. "
                f"Be vivid and cute."
            )
        elif question == "Write a poem for me?":
            if not latest_plot_url:
                return jsonify({'answer': 'Error: No plot available'}), 500
            custom_prompt = (
                f"This is the Mimosa's Electrophysiological Signal in 10 seconds, "
                f"please refer to the plot at {latest_plot_url} and answer as the perspective "
                f"of the mimosa the question 'Write a short poem to describe your feeling', no more than 5 lines. "
                f"Be poetic."
            )
        elif question == "Recently?":
            if not recent_urls:
                return jsonify({'answer': 'Error: No plot available'}), 500
            custom_prompt = (
                f"These are the Mimosa's Electrophysiological Signal in 10 seconds, "
                f"please based on the recent 10 plots at {latest_plot_url} and answer as the perspective "
                f"of the mimosa the question 'What's your feeling recently', no more than 30 words. "
                f"Be vivid and cute."
            )
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": custom_prompt}
            ]
        )
        answer = completion.choices[0].message.content
        return jsonify({'answer': answer})
    except Exception as e:
        logging.error(f"Error occurred: {e}", exc_info=True)
        return jsonify({'answer': 'Error occurred: ' + str(e)}), 500