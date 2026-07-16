import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
password = os.getenv("POSTGRES_PASSWORD")

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port="5432",
    database="cricket_dashboard",
    user="postgres",
    password=password
)
cur = conn.cursor()

# Create the table if it doesn't already exist
cur.execute("""
    CREATE TABLE IF NOT EXISTS live_matches (
        match_id TEXT PRIMARY KEY,
        match_name TEXT,
        match_type TEXT,
        status TEXT,
        venue TEXT,
        match_date TEXT,
        last_updated TIMESTAMP DEFAULT NOW()
    );
""")

conn.commit()
print("Table 'live_matches' created (or already exists).")

cur.close()
conn.close()