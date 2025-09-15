# ui/karyawan_interface.py
import streamlit as st
import pandas as pd
from db.queries import load_checkups

def karyawan_interface(uid=None):
    """
    Landing page for karyawan to view their medical checkup.
    Accessed via a URL with ?uid=<unique_id> or via QR code session.
    """

    st.header("🏥 Medical Check-Up Result")

    # --- 1️⃣ Get UID from session or query string ---------------------------
    if not uid:
        try:
            uid = st.query_params.get("uid", [None])
            if isinstance(uid, list):
                uid = uid[0]
        except AttributeError:
            uid = st.experimental_get_query_params().get("uid", [None])[0]

    if not uid:
        st.error("❌ UID tidak ditemukan di URL. Silakan scan QR code yang benar.")
        return

    # --- 2️⃣ Load and filter data -------------------------------------------
    df = load_checkups()
    if df.empty:
        st.warning("Belum ada data medical check-up di sistem.")
        return

    # ✅ Coerce UID to string to avoid type mismatch
    karyawan_data = df[df["uid"].astype(str) == str(uid)]

    if karyawan_data.empty:
        st.warning("❌ Data medical check-up tidak ditemukan untuk UID yang diberikan.")
        return

    # --- 3️⃣ Add Unwell Status ----------------------------------------------
    # Simple categorization example (adjust logic as needed)
    def categorize_unwell(row):
        thresholds = {
            "bmi": 30,
            "gestational_diabetes": 120,
            "cholesterol": 240,
            "asam_urat": 7
        }
        for key, limit in thresholds.items():
            if row.get(key, 0) > limit:
                return "Unwell"
        return "Healthy"

    karyawan_data["Status"] = karyawan_data.apply(categorize_unwell, axis=1)

    # --- 4️⃣ Display history -------------------------------------------------
    st.subheader("📋 Riwayat Medical Check-Up")
    karyawan_data = karyawan_data.sort_values("tanggal", ascending=False)
    karyawan_data["tanggal"] = pd.to_datetime(karyawan_data["tanggal"]).dt.strftime("%Y-%m-%d")

    # Highlight unwell rows
    def highlight_unwell(row):
        return ['background-color: #ffcccc' if row.Status == "Unwell" else '' for _ in row]

    st.dataframe(
        karyawan_data[
            [
                "tanggal", "lokasi", "jabatan", "umur",
                "tinggi", "berat", "lingkar_perut", "bmi",
                "gestational_diabetes", "cholesterol", "asam_urat",
                "Status"
            ]
        ].style.apply(highlight_unwell, axis=1),
        use_container_width=True
    )

    # --- 5️⃣ Highlight latest results ---------------------------------------
    latest = karyawan_data.iloc[0]
    st.subheader("📊 Hasil Terbaru")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("BMI", f"{latest['bmi']}")
        st.metric("Berat", f"{latest['berat']} kg")

    with col2:
        st.metric("Tinggi", f"{latest['tinggi']} cm")
        st.metric("Lingkar Perut", f"{latest['lingkar_perut']} cm")

    with col3:
        st.metric("G. Diabetes", f"{latest['gestational_diabetes']} mg/dL")
        st.metric("Cholesterol", f"{latest['cholesterol']} mg/dL")
        st.metric("Asam Urat", f"{latest['asam_urat']} mg/dL")

    # --- 6️⃣ Footer ----------------------------------------------------------
    st.markdown("---")
    st.info("ℹ️ Hubungi tenaga kesehatan jika ada pertanyaan mengenai "
            "hasil medical check-up Anda.")
