# scripts/seed_dummy_data.py
import pandas as pd
from datetime import datetime, timedelta
from db.queries import save_checkups, get_employees
from sqlalchemy import create_engine
from config.settings import POSTGRES_URL, DB_FILE
from db.queries import get_engine

# --- Dummy employees ---
dummy_employees = [
    {"employee_id": f"E{100+i}", "nik": f"NIK{i+1:03}", "name": f"Employee {i+1}", 
     "jabatan": "Staff", "lokasi": f"Rig {i%4+1}", "hari_lahir": i+1, "bulan_lahir": (i%12)+1, "tahun_lahir": 1990+i}
    for i in range(10)
]

# Optional: print employees
print("Dummy employees to add:")
for emp in dummy_employees:
    print(emp)

# --- Dummy checkups ---
today = datetime.today()
dummy_checkups = []

for i, emp in enumerate(dummy_employees):
    # Random past dates
    for d in range(3):  # 3 checkups each
        date_check = today - timedelta(days=30*d + i)
        gd = 90 + (i*5)%50
        chol = 180 + (i*10)%100
        urat = 5 + (i%5)
        status = "Unwell" if i < 3 else "Well"  # first 3 employees unwell
        dummy_checkups.append({
            "tanggal": date_check,
            "lokasi": emp["lokasi"],
            "tahun": date_check.year,
            "nik": emp["nik"],
            "nama": emp["name"],
            "jabatan": emp["jabatan"],
            "umur": 2025 - emp["tahun_lahir"],
            "tanggal_lahir": datetime(emp["tahun_lahir"], emp["bulan_lahir"], emp["hari_lahir"]),
            "tinggi": 160 + i,
            "berat": 55 + i,
            "lingkar_perut": 80 + i,
            "bmi": (55+i)/((160+i)/100)**2,
            "gestational_diabetes": gd,
            "cholesterol": chol,
            "asam_urat": urat
        })

# Save to database
df_checkups = pd.DataFrame(dummy_checkups)
save_checkups(df_checkups)
print("✅ Dummy checkup data inserted successfully!")
