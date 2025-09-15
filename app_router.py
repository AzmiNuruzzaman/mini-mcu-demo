# app_router.py
import streamlit as st
from urllib.parse import urlparse
from db.queries import get_user_by_username, get_employee_by_uid  # ✅ updated import

def handle_qr_landing():
    """
    Handle QR code landing if ?qr=... or ?uid=... param is present in the URL.
    
    QR format (old): mcu://karyawan/<username>
    UID format (new): ?uid=<unique_karyawan_uid>
    """
    params = st.query_params

    # --- 1️⃣ Handle old QR (username) ---
    if "qr" in params:
        qr_data = params["qr"][0] if isinstance(params["qr"], list) else params["qr"]
        parsed = urlparse(qr_data)

        if parsed.scheme == "mcu" and parsed.netloc == "karyawan":
            username = parsed.path.lstrip("/")
            user = get_user_by_username(username)
            if user:
                st.session_state["user_role"] = user["role"]
                st.session_state["username"] = username
                st.session_state["qr_access"] = True

        if "qr" in st.query_params:
            del st.query_params["qr"]
        st.rerun()

    # --- 2️⃣ Handle UID access ---
    elif "uid" in params:
        uid = params["uid"][0] if isinstance(params["uid"], list) else params["uid"]
        employee = get_employee_by_uid(uid)  # ✅ replaced function
        if employee:
            st.session_state["user_role"] = "Karyawan"       # fixed role
            st.session_state["username"] = employee["nama"]  # use nama from karyawan table
            st.session_state["employee_uid"] = uid
            st.session_state["qr_access"] = True

        if "uid" in st.query_params:
            del st.query_params["uid"]
        st.rerun()
