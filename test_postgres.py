import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
password = os.getenv("POSTGRES_PASSWORD")

try:
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="cricket_dashboard",
        user="postgres",
        password=password
    )
    print("Connected to PostgreSQL successfully!")

    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print("PostgreSQL version:", version[0])

    cur.close()
    conn.close()
    print("Connection closed cleanly.")

except Exception as e:
    print("Connection failed:", e)