import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
load_dotenv()

def get_connection():
    conn = psycopg.connect(
        host=os.getenv("DB_HOST","localhost"),
        port=os.getenv("DB_PORT","5432"),
        dbname=os.getenv("DB_NAME","context_hub"),
        user=os.getenv("DB_USER","postgres"),
        password=os.getenv("DB_PASSWORD","postgresql")
        ,row_factory=dict_row

    )

    return conn