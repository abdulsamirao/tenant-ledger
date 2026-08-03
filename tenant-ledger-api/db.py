import psycopg2
from config import app_settings

DATABASE_URL = app_settings.database_url

# prevent error where the URL includes "DATABASE_URL="
if DATABASE_URL and DATABASE_URL.startswith("DATABASE_URL="):
    DATABASE_URL = DATABASE_URL.replace("DATABASE_URL=", "")
# Initialize connection and cursor as None
conn = None
cursor = None

def get_connection():
    # Establish database connection only on demand
    global conn, cursor
    if conn is None:
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable not set")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
    return conn, cursor