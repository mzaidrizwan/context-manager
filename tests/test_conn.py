from database import get_connection

try:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()
            print("Connected successfully!")
            print("PostgreSQL Version:", version["version"])
except Exception as e:
    print("Connection failed:", e)