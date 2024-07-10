from .config import *
from psycopg2 import connect


def get_connection():
    try:
        return connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return None
