# db/database.py
import bcrypt
from sqlalchemy import create_engine, text
from config.settings import DEFAULT_USERS
from dotenv import load_dotenv
import os

# --- Load .env ---
load_dotenv(dotenv_path="supa.env")

# --- Connection helper ---
def get_engine():
    """Return SQLAlchemy engine for Supabase PostgreSQL using .env."""
    user = os.getenv("USER")
    password = os.getenv("PASSWORD")
    host = os.getenv("HOST")
    port = os.getenv("PORT")
    dbname = os.getenv("DBNAME")
    
    db_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}?sslmode=require"
    return create_engine(db_url)

# --- Initialize DB ---
def init_db():
    """Initialize PostgreSQL database with required tables and default users."""
    engine = get_engine()
    with engine.connect() as conn:
        # --- Create karyawan table (Manager master XLS) ---
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS karyawan (
                uid UUID PRIMARY KEY,
                username TEXT NOT NULL,
                jabatan TEXT,
                lokasi TEXT,
                tanggal_lahir DATE
            )
        """))

        # --- Create checkups table (Nurse master XLS) ---
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS checkups (
                checkup_id SERIAL PRIMARY KEY,
                uid UUID NOT NULL REFERENCES karyawan(uid) ON DELETE CASCADE,
                tanggal DATE NOT NULL,
                tanggal_lahir DATE,
                umur INTEGER,
                tinggi NUMERIC(5,2),
                berat NUMERIC(5,2),
                lingkar_perut NUMERIC(5,2),
                bmi NUMERIC(5,2),
                gestational_diabetes NUMERIC(5,2),
                cholesterol NUMERIC(5,2),
                asam_urat NUMERIC(5,2),
                status VARCHAR(50)   -- Well/Unwell or any nurse status
            )
        """))

        # --- Create users table ---
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                role VARCHAR(50) NOT NULL,
                password TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))

        # --- Insert default users if table empty ---
        result = conn.execute(text("SELECT COUNT(*) FROM users")).fetchone()
        if result[0] == 0:
            for username, pw, role in DEFAULT_USERS:
                hashed_pw = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
                conn.execute(
                    text(
                        "INSERT INTO users (username, password, role) "
                        "VALUES (:u, :p, :r)"
                    ),
                    {"u": username, "p": hashed_pw, "r": role}
                )

        conn.commit()
