# test_connection.py
from dotenv import dotenv_values
import psycopg2

# 1️⃣ Check if env file loads correctly
config = dotenv_values(r"C:\Python Project\mini-mcu\supa.env")
print("Loaded env config:", config)

# 2️⃣ Attempt connection only if config loaded
if config:
    conn = psycopg2.connect(
        user=config["USER"],
        password=config["PASSWORD"],
        host=config["HOST"],
        port=config["PORT"],
        dbname=config["DBNAME"],
        sslmode="require"
    )
    print("✅ Connected successfully!")
    conn.close()
else:
    print("❌ Failed to load env variables.")
