# ui/qr_manager.py
import streamlit as st
import pandas as pd
import io, zipfile
from db.queries import load_checkups, get_users
from utils.qr_utils import display_qr_code, save_qr_code_image

def qr_manager_interface():
    st.header("📱 QR Code Management")

    # --- Load data ---
    users_df = get_users()
    checkups_df = load_checkups()

    # --- Merge users with checkups to ensure we have UID ---
    karyawan_data = checkups_df[['uid', 'nama']].drop_duplicates()
    if karyawan_data.empty:
        st.warning("Belum ada data medical untuk karyawan.")
        st.info("Upload data medical karyawan terlebih dahulu.")
        return

    # --- Build display mapping from checkups UID ---
    display_to_uid = {f"{row['nama']} (UID: {row['uid']})": row['uid']
                      for _, row in karyawan_data.iterrows()}

    # --- Dropdown selection ---
    st.subheader("👥 Daftar Karyawan")
    selected_display = st.selectbox("Pilih Karyawan:", options=list(display_to_uid.keys()))
    if not selected_display:
        return

    selected_uid = display_to_uid[selected_display]
    selected_user = karyawan_data[karyawan_data['uid'] == selected_uid].iloc[0]
    selected_name = selected_user['nama']

    # --- Display QR ---
    qr_data = f"mcu://karyawan/{selected_uid}"
    display_qr_code(qr_data, f"QR Code untuk {selected_name}")

    if st.button("📥 Download QR Code"):
        filename = save_qr_code_image(selected_name, qr_data)
        with open(filename, "rb") as f:
            qr_bytes = f.read()
        st.download_button(
            label="Download QR Code Image",
            data=qr_bytes,
            file_name=f"{selected_name}_qrcode.png",
            mime="image/png"
        )

    # --- Bulk QR Generation ---
    st.markdown("---")
    st.subheader("📦 Download Semua QR Codes")
    if st.button("Generate & Download All QR Codes"):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, mode="w") as zf:
            for _, row in karyawan_data.iterrows():
                name = row['nama']
                uid = row['uid']
                qr_path = save_qr_code_image(name, f"mcu://karyawan/{uid}")
                zf.write(qr_path, arcname=f"{name}_qrcode.png")
        st.download_button(
            label="Download ZIP of All QR Codes",
            data=zip_buffer.getvalue(),
            file_name="all_karyawan_qrcodes.zip",
            mime="application/zip"
        )
