# config/settings.py
import os
from dotenv import load_dotenv

# --- Load .env file ---
load_dotenv("supa.env")

# --- App UI Titles ---
APP_TITLE = "🏥 Mini MCU Web App"
SIDEBAR_TITLE = "🔑 Login"

# --- Database configuration ---
DB_FILE = "med_check.db"  # fallback SQLite (optional)
USE_POSTGRES = True       # True to use Supabase/Postgres, False for local SQLite

# --- Build Postgres URL from environment variables ---
POSTGRES_URL = (
    f"postgresql://{os.getenv('USER')}:{os.getenv('PASSWORD')}"
    f"@{os.getenv('HOST')}:{os.getenv('PORT')}/{os.getenv('DBNAME')}?sslmode=require"
)

# --- Default users (used if DB has no users) ---
DEFAULT_USERS = [
    ("manager", "manager123", "Manager"),
    ("nurse", "nurse123", "Tenaga Kesehatan"),
    ("karyawan1", "karyawan123", "Karyawan"),
]

# --- File export configs ---
CSV_FILENAME = "medical_checkup_data.csv"
EXCEL_FILENAME = "medical_checkup_data.xlsx"
