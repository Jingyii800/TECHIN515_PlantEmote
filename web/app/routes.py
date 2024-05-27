from flask import Blueprint, render_template
import psycopg2
from .database import get_db_connection

main = Blueprint('main', __name__)

@main.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT soil_moisture, standard_plot_url, artistic_image_url FROM telemetry_data ORDER BY index DESC LIMIT 1;')
    #cur.execute('SELECT * FROM telemetry_data ORDER BY index DESC LIMIT 1;')
    data = cur.fetchone()
    cur.close()
    conn.close()
    if data:
        return render_template('index.html', soil_moisture=data[0], plot_url=data[1], image_url=data[2])
    else:
        return render_template('index.html', soil_moisture='No data', plot_url=None, image_url=None)

