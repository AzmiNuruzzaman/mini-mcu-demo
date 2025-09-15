# ui/manager_interface.py
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
from db.queries import (
    load_checkups, save_uploaded_checkups, get_users, add_user, get_employees,
    get_total_karyawan   # ✅ Added for total karyawan metric
)
from config.settings import CSV_FILENAME, EXCEL_FILENAME
from utils.qr_utils import display_qr_code, save_qr_code_image
import io, zipfile, uuid
import altair as alt

LOKASI_DEFAULT = ["Kantor", "Rig 1", "Rig 2", "Rig 3", "Rig 4"]

# -------------------------
# Manager Interface
# -------------------------
def manager_interface(current_employee_uid=None):
    st.header("📊 Mini MCU - Manager Interface")
    df = load_checkups()
    users_df = get_users()
    employees_df = get_employees()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Dashboard", "User Management", "QR Codes", "Export Data",
        "Upload master data karyawan", "data management"
    ])

    # ---------------- Tab 1: Dashboard ----------------
    with tab1:
        st.subheader("📖 Riwayat Check-Up Karyawan")
        df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
        df['tanggal_lahir'] = pd.to_datetime(df['tanggal_lahir'], errors='coerce')

        if "manager_filter_mode" not in st.session_state:
            st.session_state["manager_filter_mode"] = "month_year"
        if "manager_filter_date_range" not in st.session_state:
            today = datetime.today()
            st.session_state["manager_filter_date_range"] = (today, today)

        df['status'] = 'Well'
        df.loc[
            (df['gestational_diabetes'] > 120) |
            (df['cholesterol'] > 240) |
            (df['asam_urat'] > 7),
            'status'
        ] = 'Unwell'

        df['bulan'] = df['tanggal'].dt.month.fillna(0).astype(int)
        df['tahun'] = df['tanggal'].dt.year.fillna(0).astype(int)

        month_names = ["All","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug",
                       "Sep","Oct","Nov","Dec"]
        lokasi_options = sorted(set(LOKASI_DEFAULT) | set(df['lokasi'].dropna().tolist()))
        status_options = df['status'].dropna().unique().tolist() or ["Well","Unwell"]

        col1, col2, col3, col4 = st.columns([1,1,2,1])
        with col1:
            filter_bulan = st.selectbox(
                "Filter Bulan",
                options=range(0,13),
                index=0,
                format_func=lambda x: month_names[x],
                key="manager_filter_bulan"
            )
        with col2:
            filter_tahun = st.selectbox(
                "Filter Tahun",
                options=[0] + sorted(df["tahun"].unique()),
                index=0,
                format_func=lambda x: "All" if x == 0 else str(x),
                key="manager_filter_tahun"
            )
        with col3:
            filter_lokasi = st.multiselect(
                "Filter Lokasi",
                options=lokasi_options,
                default=lokasi_options,
                key="manager_filter_lokasi"
            )
        with col4:
            filter_status = st.multiselect(
                "Filter Status",
                options=status_options,
                default=status_options,
                key="manager_filter_status"
            )

        if st.session_state["manager_filter_mode"] == "date_picker":
            date_range = st.date_input(
                "Rentang Tanggal",
                value=st.session_state["manager_filter_date_range"],
                key="manager_filter_daterange"
            )
            if isinstance(date_range, tuple):
                start_date, end_date = date_range
            else:
                start_date, end_date = date_range, date_range
            st.session_state["manager_filter_date_range"] = (start_date, end_date)
        else:
            start_date = pd.Timestamp.min
            end_date   = pd.Timestamp.max

        df_filtered = df.copy()
        df_filtered = df_filtered[
            (df_filtered['tanggal'] >= pd.to_datetime(start_date)) &
            (df_filtered['tanggal'] <= pd.to_datetime(end_date))
        ]
        if filter_tahun != 0:
            df_filtered = df_filtered[df_filtered['tahun'] == filter_tahun]
        if filter_bulan != 0:
            df_filtered = df_filtered[df_filtered['bulan'] == filter_bulan]
        if filter_lokasi:
            df_filtered = df_filtered[df_filtered['lokasi'].isin(filter_lokasi)]
        if filter_status:
            df_filtered = df_filtered[df_filtered['status'].isin(filter_status)]

        # ✅ Use database total karyawan metric
        total_karyawan = get_total_karyawan()

        # ⚡ Deduplicate for KPIs: only latest checkup per UID
        df_latest = df_filtered.sort_values('tanggal', ascending=False).drop_duplicates(subset=['uid'], keep='first')

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("👥 Total Karyawan", total_karyawan)
        k2.metric("📝 Total Checkups", len(df_latest))  # only latest per UID
        k3.metric("✅ Well", (df_latest['status'] == "Well").sum())
        k4.metric("⚠️ Unwell", (df_latest['status'] == "Unwell").sum())


        summary = df_filtered.groupby("status").size().reindex(["Well","Unwell"], fill_value=0)
        chart_df = summary.reset_index().rename(columns={'index': 'status'})
        chart_df["count"] = chart_df["status"].map(lambda s: int(summary[s]))
        chart_df["status"] = chart_df["status"].astype(str)

        hbar = alt.Chart(chart_df).mark_bar().encode(
            y=alt.Y('status:N', title='Status'),
            x=alt.X('count:Q', title='Jumlah', axis=alt.Axis(format='d', tickMinStep=1)),
            color=alt.Color('status:N',
                            scale=alt.Scale(domain=['Well','Unwell'],
                                            range=['green','red'])),
            tooltip=['status','count']
        ).properties(height=80)
        st.altair_chart(hbar, use_container_width=True)

        df_filtered[['tinggi','lingkar_perut','bmi']] = (
        df_filtered[['tinggi','lingkar_perut','bmi']].round(2)
    )

    def highlight_unwell(row):
        return ['color: red' if row.status == 'Unwell' else '' for _ in row]

    display_cols = [
        'uid','nama','jabatan',
        'status','tanggal','lokasi','tinggi','lingkar_perut','bmi'
]

    # data frame #
    df_latest = df_filtered.sort_values('tanggal', ascending=False).drop_duplicates(subset=['uid'], keep='first')
    df_to_display = df_latest[display_cols].reset_index(drop=True)  # reset index to make it sequential

    st.dataframe(
        df_to_display.style.format({
            'tinggi': '{:.2f}',
            'lingkar_perut': '{:.2f}',
            'bmi': '{:.2f}'
        }).apply(highlight_unwell, axis=1),
        use_container_width=True
    )

    # ---------------- Tab 2: User Management ----------------
    with tab2:
        st.subheader("👥 User Management")

        manager_count = len(users_df[users_df["role"] == "Manager"])
        nurse_count = len(users_df[users_df["role"] == "Tenaga Kesehatan"])
        karyawan_count = len(users_df[users_df["role"] == "Karyawan"])

        col1, col2, col3 = st.columns(3)
        col1.metric("Manager Users", manager_count)
        col2.metric("Nurse Users", nurse_count)
        col3.metric("Karyawan Users", karyawan_count)

        st.markdown("---")
        st.write("Tambah user baru:")

        # --- Form without rerun ---
        with st.form("add_user_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["Manager", "Tenaga Kesehatan", "Karyawan"])
            add_user_btn = st.form_submit_button("Add User")

            if add_user_btn:
                if new_username and new_password:
                    try:
                        add_user(new_username, new_password, new_role)
                        st.success(f"✅ User '{new_username}' ditambahkan sebagai '{new_role}'!")
                        # Refresh users_df locally
                        users_df = get_users()
                    except Exception as e:
                        if "unique" in str(e).lower():
                            st.error("⚠️ Username sudah ada!")
                        else:
                            st.error(f"❌ Error: {e}")
                else:
                    st.error("❌ Username dan password tidak boleh kosong!")

        # Display updated users table
        st.dataframe(users_df[['username','role']], use_container_width=True)


    # ---------------- Tab 3: QR Code Management ----------------
    with tab3:
        from ui.qr_manager import qr_manager_interface
        qr_manager_interface()

    # ---------------- Tab 4: Export Data ----------------
    with tab4:
        st.subheader("📥 Download Data")
        if df.empty:
            st.warning("⚠️ Tidak ada data untuk di-download.")
        else:
            df_export = df.copy()
            for col in ['tinggi','lingkar_perut','bmi']:
                if col in df_export.columns:
                    df_export[col] = df_export[col].round(2)

            csv = df_export.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", data=csv, file_name=CSV_FILENAME, mime="text/csv")

            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df_export.to_excel(writer, index=False, sheet_name="CheckUp")
            st.download_button("Download Excel", data=output.getvalue(), file_name=EXCEL_FILENAME,
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # ---------------- Tab 5: Upload Master Data Karyawan ----------------
    with tab5:
        st.subheader("upload master data karyawan")
        uploaded_file = st.file_uploader("Pilih file XLS/CSV", type=["xls", "xlsx", "csv"])
        if uploaded_file:
            try:
                df_upload = (
                    pd.read_csv(uploaded_file)
                    if uploaded_file.name.lower().endswith(".csv")
                    else pd.read_excel(uploaded_file)
                )

                from utils.helpers import prepare_uploaded_df, prepare_karyawan_master_df
                from db.queries import save_uploaded_karyawan

                cols_lower = {c.strip().lower() for c in df_upload.columns}
                medical_markers = {
                    "tanggal", "tanggal_lahir", "tinggi", "berat",
                    "lingkar_perut", "bmi", "gestational_diabetes",
                    "cholesterol", "asam_urat", "umur"
                }

                if cols_lower & medical_markers:
                    df_upload = prepare_uploaded_df(df_upload)
                    save_uploaded_checkups(df_upload)
                else:
                    df_upload = prepare_karyawan_master_df(df_upload)
                    save_uploaded_karyawan(df_upload)

                st.success(
                    f"✅ File '{uploaded_file.name}' berhasil di-upload "
                    "dan disimpan ke database!"
                )
                st.rerun()
            except ValueError as ve:
                st.error(f"⚠️ Kolom wajib tidak lengkap: {ve}")
            except Exception as e:
                st.error(f"❌ Error saat meng-upload file: {e}")

    # ---------------- Tab 6: Data Management ----------------
    with tab6:
        st.subheader("🗂️ Data Management – Riwayat Upload Master Karyawan")

        from db.queries import get_upload_history, delete_batch

        history_df = get_upload_history()
        if history_df.empty:
            st.info("Belum ada riwayat upload master karyawan.")
        else:
            st.dataframe(history_df, use_container_width=True)

            batch_to_delete = st.selectbox(
                "Pilih Batch untuk dihapus",
                options=history_df["upload_batch_id"]
            )
            if st.button("🗑️ Hapus Batch Terpilih"):
                try:
                    delete_batch(batch_to_delete)
                    st.success("✅ Batch berhasil dihapus.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Gagal menghapus batch: {e}")
