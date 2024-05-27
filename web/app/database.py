import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def get_db_connection():
    return psycopg2.connect(
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),        
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_DATABASE'),
        port=os.getenv('DB_PORT'),
    )

