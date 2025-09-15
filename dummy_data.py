# dummy_data.py
from datetime import date
import pandas as pd
from utils.helpers import calculate_age, calculate_bmi

# --- Dummy employee data ---
dummy_employees = [
    {"employee_id": "E001", "nik": "1234567890", "name": "Andi Santoso", "jabatan": "Operator Rig", "lokasi": "Rig 1",
     "hari_lahir": 12, "bulan_lahir": 5, "tahun_lahir": 1985, "unwell": False},
    {"employee_id": "E002", "nik": "1234567891", "name": "Budi Hartono", "jabatan": "Engineer", "lokasi": "Rig 2",
     "hari_lahir": 3, "bulan_lahir": 8, "tahun_lahir": 1990, "unwell": True},
    {"employee_id": "E003", "nik": "1234567892", "name": "Citra Dewi", "jabatan": "Supervisor", "lokasi": "Rig 3",
     "hari_lahir": 22, "bulan_lahir": 11, "tahun_lahir": 1982, "unwell": False},
    {"employee_id": "E004", "nik": "1234567893", "name": "Dedi Prasetyo", "jabatan": "Technician", "lokasi": "Rig 4",
     "hari_lahir": 5, "bulan_lahir": 2, "tahun_lahir": 1988, "unwell": True},
    {"employee_id": "E005", "nik": "1234567894", "name": "Eka Putri", "jabatan": "Admin", "lokasi": "Kantor",
     "hari_lahir": 17, "bulan_lahir": 6, "tahun_lahir": 1992, "unwell": False},
    {"employee_id": "E006", "nik": "1234567895", "name": "Fajar Nugroho", "jabatan": "Operator Rig", "lokasi": "Rig 1",
     "hari_lahir": 28, "bulan_lahir": 9, "tahun_lahir": 1987, "unwell": False},
    {"employee_id": "E007", "nik": "1234567896", "name": "Gita Ramadhani", "jabatan": "Engineer", "lokasi": "Rig 2",
     "hari_lahir": 10, "bulan_lahir": 12, "tahun_lahir": 1991, "unwell": True},
    {"employee_id": "E008", "nik": "1234567897", "name": "Hendra Wijaya", "jabatan": "Supervisor", "lokasi": "Rig 3",
     "hari_lahir": 1, "bulan_lahir": 3, "tahun_lahir": 1983, "unwell": False},
    {"employee_id": "E009", "nik": "1234567898", "name": "Intan Sari", "jabatan": "Technician", "lokasi": "Rig 4",
     "hari_lahir": 14, "bulan_lahir": 7, "tahun_lahir": 1989, "unwell": False},
    {"employee_id": "E010", "nik": "1234567899", "name": "Joko Susanto", "jabatan": "Admin", "lokasi": "Kantor",
     "hari_lahir": 30, "bulan_lahir": 1, "tahun_lahir": 1993, "unwell": False},
]

# --- Add age and dummy medical metrics ---
for emp in dummy_employees:
    dob = date(emp["tahun_lahir"], emp["bulan_lahir"], emp["hari_lahir"])
    emp["umur"] = calculate_age(dob)
    
    # Random-ish but realistic medical metrics for testing
    emp["tinggi"] = 160 + hash(emp["employee_id"]) % 30  # 160-189 cm
    emp["berat"] = 50 + hash(emp["nik"]) % 50           # 50-99 kg
    emp["lingkar_perut"] = 70 + hash(emp["name"]) % 40  # 70-109 cm
    emp["bmi"] = calculate_bmi(emp["berat"], emp["tinggi"])
    emp["gestational_diabetes"] = 80 + hash(emp["nik"]) % 100   # 80-179 mg/dL
    emp["cholesterol"] = 150 + hash(emp["employee_id"]) % 150   # 150-299 mg/dL
    emp["asam_urat"] = 3 + hash(emp["nik"]) % 10               # 3-12 mg/dL

# Convert to DataFrame for easy testing
df_dummy = pd.DataFrame(dummy_employees)

if __name__ == "__main__":
    print(df_dummy)
