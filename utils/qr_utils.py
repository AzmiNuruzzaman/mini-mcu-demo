# utils/qr_utils.py
import qrcode
import io
import base64
import streamlit as st
from datetime import datetime
import os

def generate_qr_code(data, size=300):
    """
    Generate QR code from data and return as base64 encoded image
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to bytes
    img_buffer = io.BytesIO()
    img.save(img_buffer, format="PNG")
    img_buffer.seek(0)
    
    # Convert to base64 for HTML embedding
    img_str = base64.b64encode(img_buffer.getvalue()).decode()
    
    return img_str

def generate_karyawan_qr(nik):
    """
    Generate QR code for a specific karyawan using NIK
    """
    # Create a unique URL using NIK instead of username
    qr_data = f"mcu://karyawan/{nik}"
    return generate_qr_code(qr_data)

def save_qr_code_image(username, qr_data):
    """
    Save QR code as image file (optional - for downloading)
    """
    # Create qr_codes directory if it doesn't exist
    os.makedirs("qr_codes", exist_ok=True)
    
    # Generate and save QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    filename = f"qr_codes/{username}_qrcode.png"
    img.save(filename)
    
    return filename

def display_qr_code(qr_data, title="QR Code"):
    """
    Display QR code in Streamlit
    """
    img_str = generate_qr_code(qr_data)
    st.subheader(title)
    st.markdown(
        f'<img src="data:image/png;base64,{img_str}" width="200" height="200">',
        unsafe_allow_html=True
    )
    return img_str