import requests
from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()
api_key = os.getenv("CRICAPI_KEY")
pg_password = os.getenv("POSTGRES_PASSWORD")


def fetch_matches():
    """Pull current match data from CricAPI."""
    url = "https://api.cricapi.com/v1/currentMatches"
    params = {"apikey": api_key, "offset": 0}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"ERROR: API request failed: {e}")
        return []

    data = response.json()
    if data.get("status") != "success":
        print(f"ERROR: API returned failure: {data.get('reason', 'unknown')}")
        return []

    matches = data.get("data", [])
    print(f"Fetched {len(matches)} matches from CricAPI.")
    return matches


def upsert_matches(matches):
    """Insert new matches or update existing ones in PostgreSQL."""
    if not matches:
        print("No matches to upsert.")
        return

    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port="5432",
        database="cricket_dashboard",
        user="postgres",
        password=pg_password
    )
    cur = conn.cursor()

    upsert_query = """
        INSERT INTO live_matches (match_id, match_name, match_type, status, venue, match_date, last_updated)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
        ON CONFLICT (match_id)
        DO UPDATE SET
            match_name = EXCLUDED.match_name,
            match_type = EXCLUDED.match_type,
            status = EXCLUDED.status,
            venue = EXCLUDED.venue,
            match_date = EXCLUDED.match_date,
            last_updated = NOW();
    """

    for match in matches:
        cur.execute(upsert_query, (
            match.get("id", ""),
            match.get("name", ""),
            match.get("matchType", ""),
            match.get("status", ""),
            match.get("venue", ""),
            match.get("date", ""),
        ))

    conn.commit()
    print(f"Upserted {len(matches)} matches into live_matches.")

    cur.close()
    conn.close()


def refresh():
    matches = fetch_matches()
    upsert_matches(matches)


if __name__ == "__main__":
    refresh()