# clean_cache.py
import os
import shutil
import streamlit as st

# --- Clear __pycache__ folders ---
for root, dirs, files in os.walk("."):
    for d in dirs:
        if d == "__pycache__":
            full_path = os.path.join(root, d)
            shutil.rmtree(full_path)
            print(f"Removed {full_path}")

# --- Clear Streamlit cache ---
st.cache_data.clear()
st.cache_resource.clear()
print("✅ Streamlit cache cleared.")
