# db/queries.py
import pandas as pd
import bcrypt
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from utils.helpers import calculate_age
from dotenv import load_dotenv
import os

# --- Load .env ---
load_dotenv(dotenv_path="supa.env")

# --- Config ---
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DBNAME = os.getenv("DBNAME")

DATABASE_URL = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"
ENGINE = create_engine(DATABASE_URL)

# --- Expected schema for checkups table ---
CHECKUP_COLUMNS = [
    "uid", "tanggal", "tanggal_lahir", "umur",
    "tinggi", "berat", "lingkar_perut",
    "bmi", "gestational_diabetes", "cholesterol", "asam_urat"
]

# --- Connection helper ---
def get_engine():
    return ENGINE

# --- Karyawan ---
def get_employees():
    query = """
        SELECT uid, username AS nama, jabatan, lokasi, tanggal_lahir
        FROM karyawan
        ORDER BY username
    """
    return pd.read_sql(query, get_engine())

def get_employee_by_uid(uid):
    with get_engine().connect() as conn:
        result = conn.execute(
            text(
                "SELECT uid, username AS nama, jabatan, lokasi, tanggal_lahir "
                "FROM karyawan WHERE uid = :uid"
            ),
            {"uid": uid}
        ).fetchone()
    return dict(result._mapping) if result else None

def add_employee_if_missing(username, jabatan, lokasi, tanggal_lahir=None, upload_batch_id=None):
    with get_engine().begin() as conn:
        existing = conn.execute(
            text(
                "SELECT uid FROM karyawan "
                "WHERE username = :username AND jabatan = :jabatan AND lokasi = :lokasi"
            ),
            {"username": username, "jabatan": jabatan, "lokasi": lokasi}
        ).fetchone()
        if existing:
            return existing._mapping["uid"]

        new_uid = str(uuid.uuid4())
        conn.execute(
            text(
                "INSERT INTO karyawan (uid, username, jabatan, lokasi, tanggal_lahir, "
                "uploaded_at, upload_batch_id) "
                "VALUES (:uid, :username, :jabatan, :lokasi, :dob, NOW(), :batch)"
            ),
            {
                "uid": new_uid,
                "username": username,
                "jabatan": jabatan,
                "lokasi": lokasi,
                "dob": tanggal_lahir,
                "batch": upload_batch_id,
            }
        )
        return new_uid

# --- Checkups ---
def load_checkups():
    query = """
        SELECT
            c.uid,
            c.tanggal,
            c.tanggal_lahir,
            c.umur,
            ROUND(c.tinggi::numeric, 2) AS tinggi,
            ROUND(c.berat::numeric, 2) AS berat,
            ROUND(c.lingkar_perut::numeric, 2) AS lingkar_perut,
            ROUND(c.bmi::numeric, 2) AS bmi,
            c.gestational_diabetes,
            c.cholesterol,
            c.asam_urat,
            k.username AS nama,
            k.jabatan,
            k.lokasi
        FROM checkups c
        JOIN karyawan k ON c.uid = k.uid
        ORDER BY c.tanggal DESC
    """
    return pd.read_sql(query, get_engine())

def save_checkups(df):
    missing_cols = [col for col in CHECKUP_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    df = df[CHECKUP_COLUMNS]
    try:
        df.to_sql("checkups", get_engine(), if_exists="append", index=False)
    except SQLAlchemyError as e:
        raise e

def save_uploaded_checkups(df):
    required_cols = ["nama", "jabatan", "lokasi", "tanggal",
                     "tanggal_lahir", "tinggi", "berat", "lingkar_perut",
                     "bmi", "gestational_diabetes", "cholesterol", "asam_urat"]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in uploaded file: {missing_cols}")

    df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce").dt.date
    df["tanggal_lahir"] = pd.to_datetime(df["tanggal_lahir"], errors="coerce").dt.date
    df["umur"] = df["tanggal_lahir"].apply(lambda d: calculate_age(d) if pd.notnull(d) else 0)

    numeric_cols = ["tinggi", "berat", "lingkar_perut", "bmi",
                    "gestational_diabetes", "cholesterol", "asam_urat"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0).round(2)

    batch_id = str(uuid.uuid4())
    uids = []
    for _, row in df.iterrows():
        uid = add_employee_if_missing(
            row["nama"], row["jabatan"], row["lokasi"], row["tanggal_lahir"],
            upload_batch_id=batch_id
        )
        uids.append(uid)
    df["uid"] = uids

    df_to_save = df[CHECKUP_COLUMNS].copy()
    save_checkups(df_to_save)

# --- Users ---
def get_users():
    query = "SELECT username, role FROM users"
    return pd.read_sql(query, get_engine())

def get_user_by_username(username):
    with get_engine().connect() as conn:
        result = conn.execute(
            text("SELECT username, password, role FROM users WHERE username = :username"),
            {"username": username}
        ).fetchone()
    return dict(result._mapping) if result else None

def add_user(username, password, role):
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode("utf-8")
    with get_engine().begin() as conn:
        conn.execute(
            text("INSERT INTO users (username, password, role) VALUES (:u, :p, :r)"),
            {"u": username, "p": hashed_pw, "r": role}
        )

# --- Master User Functions ---
def delete_user(username: str):
    with get_engine().begin() as conn:
        conn.execute(text("DELETE FROM users WHERE username = :username"), {"username": username})

def reset_user_password(username: str, new_password: str):
    hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode("utf-8")
    with get_engine().begin() as conn:
        conn.execute(
            text("UPDATE users SET password = :pw WHERE username = :username"),
            {"pw": hashed_pw, "username": username}
        )

def count_users_by_role(role: str) -> int:
    with get_engine().connect() as conn:
        result = conn.execute(
            text("SELECT COUNT(*) FROM users WHERE role = :role"),
            {"role": role}
        ).scalar()
    return result or 0

# --- Master Karyawan Upload ---
def save_uploaded_karyawan(df: pd.DataFrame) -> None:
    if df.empty:
        return
    batch_id = str(uuid.uuid4())
    with get_engine().begin() as conn:
        for _, row in df.iterrows():
            username = row.get("nama")
            jabatan = row.get("jabatan")
            lokasi  = row.get("lokasi")
            tanggal_lahir = pd.to_datetime(row.get("tanggal_lahir"), errors="coerce")
            tanggal_lahir = tanggal_lahir.date() if pd.notnull(tanggal_lahir) else None
            result = conn.execute(
                text("SELECT uid FROM karyawan WHERE username = :username"),
                {"username": username}
            ).fetchone()
            if result:
                conn.execute(
                    text("""
                        UPDATE karyawan
                        SET jabatan = :jabatan,
                            lokasi = :lokasi,
                            tanggal_lahir = :dob
                        WHERE uid = :uid
                    """),
                    {"jabatan": jabatan, "lokasi": lokasi, "dob": tanggal_lahir, "uid": result._mapping["uid"]},
                )
            else:
                new_uid = str(uuid.uuid4())
                conn.execute(
                    text("""
                        INSERT INTO karyawan (uid, username, jabatan, lokasi,
                                              tanggal_lahir, uploaded_at, upload_batch_id)
                        VALUES (:uid, :username, :jabatan, :lokasi, :dob, NOW(), :batch)
                    """),
                    {"uid": new_uid, "username": username, "jabatan": jabatan,
                     "lokasi": lokasi, "dob": tanggal_lahir, "batch": batch_id},
                )

# --- Karyawan Count ---
def get_total_karyawan() -> int:
    with get_engine().connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM karyawan")).scalar()
    return result or 0

# --- Upload History Helpers ---
def get_upload_history() -> pd.DataFrame:
    query = """
        SELECT
            upload_batch_id,
            MIN(uploaded_at) AS uploaded_at,
            COUNT(*) AS total_rows
        FROM karyawan
        WHERE upload_batch_id IS NOT NULL
        GROUP BY upload_batch_id
        ORDER BY uploaded_at DESC
    """
    return pd.read_sql(query, get_engine())

def delete_batch(batch_id: str) -> None:
    with get_engine().begin() as conn:
        conn.execute(text("DELETE FROM karyawan WHERE upload_batch_id = :bid"), {"bid": batch_id})

# --- Master Delete Helpers ---
def delete_employee_by_uid(uid: str):
    with get_engine().begin() as conn:
        conn.execute(text("DELETE FROM karyawan WHERE uid = :uid"), {"uid": uid})

def delete_all_employees():
    with get_engine().begin() as conn:
        conn.execute(text("DELETE FROM karyawan"))

def delete_checkup_by_id(checkup_id: int):
    with get_engine().begin() as conn:
        conn.execute(text("DELETE FROM checkups WHERE id = :id"), {"id": checkup_id})

def delete_all_checkups():
    with get_engine().begin() as conn:
        conn.execute(text("DELETE FROM checkups"))
