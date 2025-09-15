# config/settings.py
import os
import streamlit as st

APP_TITLE = "🏥 Mini MCU Web App"
SIDEBAR_TITLE = "🔑 Login"

# --- Database configuration -----------------------------------------------

# Fallback SQLite for quick local testing (optional)
DB_FILE = "med_check.db"

# Flag to choose backend
USE_POSTGRES = True  # Set False if you want local SQLite

# Pull Postgres URL from Streamlit Secrets first, then environment variable,
# finally fallback to the hard-coded local default (for dev only).
POSTGRES_URL = (
    st.secrets.get("POSTGRES_URL")
    or os.getenv("POSTGRES_URL")
    or "postgresql+psycopg2://mini_mcu_user:new_password@localhost:5432/mini_mcu"
)

# --- Default users (used if DB has no users) --------------------------------
DEFAULT_USERS = [
    ("manager", "manager123", "Manager"),
    ("nurse", "nurse123", "Tenaga Kesehatan"),
    ("karyawan1", "karyawan123", "Karyawan"),
]

# --- File export configs ----------------------------------------------------
CSV_FILENAME = "medical_checkup_data.csv"
EXCEL_FILENAME = "medical_checkup_data.xlsx"
