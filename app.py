# app.py
import streamlit as st
from auth.login_ui import login
from auth.auth import logout
from ui.nurse_interface import nurse_interface
from ui.manager_interface import manager_interface
from ui.karyawan_interface import karyawan_interface
from ui.master_interface import master_interface  # ✅ added Master interface
from config.settings import APP_TITLE
from app_router import handle_qr_landing  # ✅ no changes needed

st.set_page_config(page_title=APP_TITLE, layout="wide")

def main():
    # -------------------------------
    # 1️⃣ Handle QR code landing first
    # -------------------------------
    handle_qr_landing()

    # -------------------------------
    # 2️⃣ If logged in, show interface
    # -------------------------------
    if "user_role" in st.session_state:
        # Clear any login success flags to prevent loops
        if "show_login_success" in st.session_state:
            st.session_state.pop("show_login_success")
            st.session_state.pop("login_role", None)
        
        role = st.session_state["user_role"]
        uid = st.session_state.get("employee_uid")  # ✅ renamed to uid
        is_qr_access = st.session_state.get("qr_access", False)

        # Show logout only for non-QR access or non-karyawan
        if not is_qr_access or role != "Karyawan":
            logout()

        # -------------------------------
        # 3️⃣ Route based on role
        # -------------------------------
        if role == "Manager":
            manager_interface()
        elif role == "Tenaga Kesehatan":
            nurse_interface()
        elif role == "Karyawan":
            if is_qr_access and uid:
                st.sidebar.info("🔒 Akses via QR Code - Terbatas")
                # ✅ Pass UID to Karyawan interface for QR access
                karyawan_interface(uid=uid)
            else:
                # Standard login access (uid from session)
                karyawan_interface(uid=uid)
        elif role == "Master":  # ✅ Master role
            master_interface()
        else:
            st.error("❌ Role tidak dikenal, hubungi administrator.")

    else:
        # -------------------------------
        # 4️⃣ Not logged in → show login
        # -------------------------------
        login()
        
        # If login was successful, let the login function handle the transition
        if st.session_state.get("login_success"):
            st.session_state.pop("login_success")
            # No need for additional rerun here, login function handles it

if __name__ == "__main__":
    main()
