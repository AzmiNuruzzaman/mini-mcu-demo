# db_test.py
import streamlit as st
import socket
import psycopg2

# --- Load secrets ---
user = st.secrets["USER"]
password = st.secrets["PASSWORD"]
host = st.secrets["HOST"]
port = st.secrets["PORT"]
dbname = st.secrets["DBNAME"]

st.write("Testing database connection...")

# --- 1️⃣ Test hostname resolution ---
try:
    ip = socket.gethostbyname(host)
    st.success(f"✅ Host resolves to {ip}")
except Exception as e:
    st.error(f"❌ Host resolution failed: {e}")

# --- 2️⃣ Test raw psycopg2 connection ---
try:
    conn = psycopg2.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        dbname=dbname,
        sslmode="require"
    )
    st.success("✅ Raw psycopg2 DB connected!")
    conn.close()
except Exception as e:
    st.error(f"❌ Raw psycopg2 connection failed: {e}")
