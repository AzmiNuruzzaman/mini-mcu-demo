from datetime import date, datetime
import pandas as pd
import uuid

def validate_form(nama, jabatan, tinggi, berat, bmi):
    """
    Ensure all required fields are filled.
    Returns True if valid, False if any field is missing.
    """
    required_fields = [nama, jabatan, tinggi, berat, bmi]
    return all(field not in [None, "", 0] for field in required_fields)

def calculate_bmi(weight_kg, height_cm):
    """
    Calculate BMI given weight (kg) and height (cm).
    """
    if not weight_kg or not height_cm or height_cm <= 0:
        return 0
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)

def calculate_age(birth_date):
    """
    Calculate age in years given birth_date.
    Accepts datetime.date, datetime.datetime, or pandas.Timestamp.
    Returns 0 if invalid or missing.
    """
    if birth_date is None or pd.isnull(birth_date):
        return 0

    # Normalize to datetime.date
    if isinstance(birth_date, pd.Timestamp):
        birth_date = birth_date.to_pydatetime().date()
    elif isinstance(birth_date, datetime):
        birth_date = birth_date.date()
    elif not isinstance(birth_date, date):
        try:
            birth_date = pd.to_datetime(birth_date).date()
        except Exception:
            return 0

    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


# -------------------- New Helper for Unified Upload Flow -------------------- #

def prepare_uploaded_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and normalize an uploaded DataFrame so it is ready for
    save_uploaded_checkups().

    Steps:
    1. Standardize column names (strip/ lowercase)
    2. Ensure a UID column exists (rename employee_uid → uid if present)
    3. Validate & auto-fill required columns
       - Convert date columns to datetime
       - Compute BMI if missing and weight/height available
       - Compute umur if missing and tanggal_lahir available
    4. Raise ValueError if any required columns remain missing.
    """
    REQUIRED = [
        "uid", "tanggal", "tanggal_lahir", "tinggi", "berat",
        "lingkar_perut", "bmi", "gestational_diabetes", "cholesterol"
    ]

    df_clean = df.copy()

    # --- 1. Standardize column names ---
    df_clean.columns = [c.strip().lower() for c in df_clean.columns]

    # --- 2. UID handling ---
    if "uid" not in df_clean.columns:
        # Rename employee_uid -> uid if present
        if "employee_uid" in df_clean.columns:
            df_clean.rename(columns={"employee_uid": "uid"}, inplace=True)
        else:
            df_clean["uid"] = [str(uuid.uuid4()) for _ in range(len(df_clean))]

    # --- 3. Date parsing ---
    for date_col in ["tanggal", "tanggal_lahir"]:
        if date_col in df_clean.columns:
            df_clean[date_col] = pd.to_datetime(df_clean[date_col], errors="coerce")

    # --- 4. Auto-compute BMI if needed ---
    if "bmi" not in df_clean.columns:
        if {"tinggi", "berat"}.issubset(df_clean.columns):
            df_clean["bmi"] = df_clean.apply(
                lambda r: calculate_bmi(r["berat"], r["tinggi"])
                if pd.notnull(r["berat"]) and pd.notnull(r["tinggi"])
                else 0,
                axis=1,
            )
        else:
            df_clean["bmi"] = 0

    # --- 5. Auto-compute umur if applicable ---
    if "umur" not in df_clean.columns and "tanggal_lahir" in df_clean.columns:
        df_clean["umur"] = df_clean["tanggal_lahir"].apply(
            lambda d: calculate_age(d) if pd.notnull(d) else 0
        )

    # --- 6. Required-column validation ---
    missing = [col for col in REQUIRED if col not in df_clean.columns]
    if missing:
        raise ValueError(
            f"Missing required columns after cleaning: {missing}. "
            "Please update the uploaded file to include these columns."
        )

    return df_clean


# -------------------- New Helper for Manager Karyawan Master Upload -------------------- #

def prepare_karyawan_master_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and normalize a Manager's master Karyawan upload.

    Expected columns: nama, jabatan, lokasi
    - Standardize column names
    - Ensure required columns exist
    - Add uid if missing, generate uuid4 for any missing uid cells
    """
    REQUIRED = ["nama", "jabatan", "lokasi"]

    df_clean = df.copy()
    df_clean.columns = [c.strip().lower() for c in df_clean.columns]

    # validate required columns
    missing = [col for col in REQUIRED if col not in df_clean.columns]
    if missing:
        raise ValueError(
            f"Missing required columns in manager master file: {missing}"
        )

    # ensure uid column exists and fill missing values
    if "uid" not in df_clean.columns:
        df_clean["uid"] = [str(uuid.uuid4()) for _ in range(len(df_clean))]
    else:
        # fill empty or NaN with new uuid
        df_clean["uid"] = df_clean["uid"].apply(
            lambda x: str(uuid.uuid4()) if pd.isnull(x) or x == "" else str(x)
        )

    return df_clean
