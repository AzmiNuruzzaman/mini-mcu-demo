# test_db.py
from db.database import init_postgres_db  # Add this import
from db.queries import load_checkups, save_checkups, add_user, get_users, get_user_by_username
import pandas as pd

def test_checkups():
    print("🔎 Testing checkups table...")
    
    # Initialize PostgreSQL database FIRST
    init_postgres_db()  # Add this line
    
    # Create a dummy dataframe with required schema
    data = {
        "tanggal": ["2025-09-04"],
        "lokasi": ["HO Mentul"],
        "tahun": [2025],
        "nama": ["Budi Santoso"],
        "jabatan": ["Staff"],
        "umur": [30],
        "tanggal_lahir": ["1995-01-01"],
        "tinggi": [170],
        "berat": [70],
        "lingkar_perut": [80],
        "bmi": [24.2],
        "gestational_diabetes": [0],  # Changed from False to 0
        "cholesterol": [200],
        "asam_urat": [5.5],
    }
    df = pd.DataFrame(data)

    # Save to DB
    save_checkups(df)
    print("✅ Inserted 1 checkup row")

    # Load from DB
    df_loaded = load_checkups()
    print("✅ Loaded checkups:")
    print(df_loaded.tail(1))  # show last row

def test_users():
    print("\n🔎 Testing users table...")

    # Add new user
    add_user("tester", "secret123", "manager")
    print("✅ Inserted user 'tester'")

    # Load all users
    df_users = get_users()
    print("✅ Loaded users:")
    print(df_users)

    # Get single user
    user = get_user_by_username("tester")
    print("✅ get_user_by_username('tester'):", user)

if __name__ == "__main__":
    test_checkups()
    test_users()