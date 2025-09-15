# auth/auth.py
import streamlit as st
import bcrypt
from db.database import init_db
from db.queries import get_user_by_username
from config.settings import SIDEBAR_TITLE

# --- Initialize DB ---
init_db()

def login():
    """Render login form and validate credentials."""
    st.sidebar.header(SIDEBAR_TITLE)
    username = st.sidebar.text_input("Username")
    password_input = st.sidebar.text_input("Password", type="password")
    login_button = st.sidebar.button("Login")

    if login_button:
        result = get_user_by_username(username)
        if result:
            stored_hash = result["password"]   # string from DB
            role = result["role"]

            # bcrypt requires bytes
            if bcrypt.checkpw(password_input.encode("utf-8"), stored_hash.encode("utf-8")):
                # ✅ Session state without NIK
                st.session_state["user_role"] = role
                st.session_state["username"] = username
                st.session_state["qr_access"] = False  # default for manual login
                st.success(f"✅ Logged in as {role}")
                st.rerun()
            else:
                st.error("❌ Username atau password salah!")
        else:
            st.error("❌ Username atau password salah!")

def logout():
    """Clear session and rerun app."""
    if st.sidebar.button("Logout"):
        st.session_state.pop("user_role", None)
        st.session_state.pop("username", None)
        st.session_state.pop("qr_access", None)
        st.rerun()
