# config/settings.py
import streamlit as st

# --- App UI Titles ---
APP_TITLE = "🏥 Mini MCU Web App"
SIDEBAR_TITLE = "🔑 Login"

# --- Database configuration ---
DB_FILE = "med_check.db"  # fallback SQLite (optional)
USE_POSTGRES = True       # True to use Supabase/Postgres, False for local SQLite

# --- Build Postgres URL from Streamlit secrets ---
# Make sure your secrets.toml has a [postgres] block:
# [postgres]
# host = "db.iqcrkohssyqoggjuwsoh.supabase.co"
# port = "5432"
# database = "postgres"
# username = "postgres"
# password = "HvKt5mtxWsjmaNPA"

postgres = st.secrets["postgres"]
POSTGRES_URL = (
    f"postgresql://{postgres['username']}:{postgres['password']}"
    f"@{postgres['host']}:{postgres['port']}/{postgres['database']}?sslmode=require"
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
