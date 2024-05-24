from flask import Blueprint, render_template
import psycopg2

main = Blueprint('main', __name__)


@main.route('/')
def index():
    conn = psycopg2.connect(
        user="plant_emot",
        password="techin515#",  # Replace with your actual password
        host="plantemotserver.postgres.database.azure.com",
        port=5432,
        database="plant_emot"
    )
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

