import streamlit as st
from PIL import Image
from pathlib import Path
from auth.auth import get_user_by_username
import bcrypt

def login():
    """Login page with centered logo, welcome text, and input fields using a form."""

    # --- Skip login page if already logged in ---
    if "user_role" in st.session_state:
        st.info("Sudah login. Silakan logout jika ingin masuk dengan akun lain.")
        if st.button("Lanjut ke Aplikasi"):
            st.switch_page("app.py")
        return

    # --- Check if we just successfully logged in and need to show success message ---
    if st.session_state.get("show_login_success"):
        st.success(f"✅ Berhasil login sebagai {st.session_state.get('login_role', 'user')}")
        st.session_state.pop("show_login_success", None)
        st.session_state.pop("login_role", None)
        st.rerun()  # One more rerun to clear the message and proceed
        return

    # --- Page config ---
    st.set_page_config(page_title="Mini-MCU Login", layout="centered")

    # --- Absolute logo path ---
    BASE_DIR = Path(__file__).resolve().parent.parent
    LOGO_PATH = BASE_DIR / "assets" / "logo.png"

    # --- CSS for fixed-width container and min-width ---
    st.markdown(
        """
        <style>
        body { min-width: 600px; }
        .login-container {
            max-width: 400px;
            margin-left: auto;
            margin-right: auto;
            padding-top: 70px;  /* increased for larger logo */
        }
        .login-container .stTextInput>div>div>input {
            width: 100%;
        }
        /* Smooth transitions */
        .element-container {
            transition: opacity 0.3s ease;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="login-container">', unsafe_allow_html=True)

    # Logo
    try:
        logo = Image.open(LOGO_PATH)
        st.image(logo, width=250)  # enlarged logo
    except FileNotFoundError:
        st.warning("⚠️ Logo not found. Please place 'logo.png' in the assets folder.")

    # Welcome text
    st.markdown("### Selamat datang di Mini-MCU")
    st.markdown("<br>", unsafe_allow_html=True)

    # --- Login Form ---
    with st.form("login_form", clear_on_submit=True):
        username = st.text_input("User ID", placeholder="Masukkan ID Anda", key="login_user")
        password = st.text_input("Password", type="password", placeholder="Masukkan Password", key="login_pass")
        st.markdown("<small>Lupa password? (placeholder)</small>", unsafe_allow_html=True)
        submit = st.form_submit_button("Login")

        if submit:
            if username and password:
                result = get_user_by_username(username)
                if result and bcrypt.checkpw(password.encode("utf-8"), result["password"].encode("utf-8")):
                    # --- Update session state ---
                    st.session_state["user_role"] = result["role"]
                    st.session_state["username"] = username
                    st.session_state["qr_access"] = False
                    st.session_state["login_success"] = True
                    st.session_state["show_login_success"] = True
                    st.session_state["login_role"] = result["role"]
                    
                    # Immediate rerun to show success message
                    st.rerun()
                else:
                    st.error("❌ Username atau password salah!")
            else:
                st.warning("⚠️ Harap isi username dan password")

    st.markdown('</div>', unsafe_allow_html=True)
