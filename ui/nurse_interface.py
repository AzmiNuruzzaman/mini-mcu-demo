# ui/nurse_interface.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid
import io
from db.queries import (
    save_checkups,
    save_uploaded_checkups,
    CHECKUP_COLUMNS,
    get_employees,
    get_employee_by_uid,
    load_checkups
)
from utils.helpers import validate_form, calculate_bmi, calculate_age
import altair as alt

LOKASI_OPTIONS = ["Rig 1", "Rig 2", "Rig 3", "Rig 4", "Kantor"]

def nurse_interface(current_employee_uid=None):
    st.header("📝 Mini MCU - Nurse Interface")

    # --- Session state ---
    if "draft_data" not in st.session_state:
        st.session_state["draft_data"] = pd.DataFrame(columns=CHECKUP_COLUMNS)
    if "tab2_form_counter" not in st.session_state:
        st.session_state["tab2_form_counter"] = 0
    if "selected_emp_uid" not in st.session_state:
        st.session_state["selected_emp_uid"] = None
    if "emp_locked" not in st.session_state:
        st.session_state["emp_locked"] = False

    # --- Tabs ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Pilih Data Karyawan",
        "Riwayat Check-Up",
        "Upload Data (XLS/CSV)",
        "Download data karyawan (xls/csv)",
        "Edit data karyawan",
    ])

    # ----------------------
    # Tab 1: Pilih Data Karyawan (UNCHANGED)
    # ----------------------
    with tab1:
        st.subheader("👥 Pilih Data Karyawan (hanya karyawan yang sudah terdaftar)")

        try:
            employees = get_employees()
        except Exception as e:
            st.error(f"❌ Gagal memuat daftar karyawan: {e}")
            employees = pd.DataFrame()

        def build_uid_name_lists(employees_obj):
            uids = []
            names = []
            if isinstance(employees_obj, pd.DataFrame):
                uid_col = next((c for c in ["employee_uid", "uid", "id", "nik"] if c in employees_obj.columns), None)
                name_col = next((c for c in ["nama", "name"] if c in employees_obj.columns), None)
                if uid_col and name_col:
                    uids = employees_obj[uid_col].astype(str).tolist()
                    names = employees_obj[name_col].astype(str).tolist()
            elif isinstance(employees_obj, (list, tuple)):
                for e in employees_obj:
                    if isinstance(e, dict):
                        uid = e.get("employee_uid") or e.get("uid") or e.get("id") or e.get("nik")
                        name = e.get("nama") or e.get("name")
                        if uid and name:
                            uids.append(str(uid))
                            names.append(str(name))
            return uids, names

        uids, names = build_uid_name_lists(employees)
        display_options = ["-- Pilih Karyawan --"] + names

        col_sel, col_conf, col_res = st.columns([4, 1, 1])
        selected_name = col_sel.selectbox(
            "Pilih Karyawan",
            display_options,
            index=0,
            key=f"tab2_selector_{st.session_state['tab2_form_counter']}"
        )
        confirm = col_conf.button("Konfirmasi Pilihan", use_container_width=True)
        reset = col_res.button("Reset Pilihan", use_container_width=True)

        if confirm:
            if selected_name == "-- Pilih Karyawan --" or selected_name == "":
                st.warning("⚠️ Pilih karyawan terlebih dahulu sebelum konfirmasi!")
            else:
                try:
                    idx = names.index(selected_name)
                    selected_uid = uids[idx]
                    st.session_state["selected_emp_uid"] = selected_uid
                    st.session_state["emp_locked"] = True
                    emp_raw = get_employee_by_uid(selected_uid)
                    emp = emp_raw.to_dict() if hasattr(emp_raw, "to_dict") else emp_raw
                    st.session_state["selected_employee_record"] = emp
                    st.success(f"✅ Karyawan dikunci: {selected_name}")
                except Exception as e:
                    st.error(f"❌ Gagal ambil data karyawan: {e}")

        if reset:
            st.session_state["selected_emp_uid"] = None
            st.session_state["emp_locked"] = False
            if "selected_employee_record" in st.session_state:
                del st.session_state["selected_employee_record"]
            st.session_state["tab2_form_counter"] += 1
            st.info("🔄 Pilihan karyawan dan form direset.")
            st.rerun()

        emp = st.session_state.get("selected_employee_record", {})
        lokasi_val = emp.get("lokasi", "")
        jabatan_val = emp.get("jabatan", "")
        dob_date = None
        umur = None
        try:
            if "tanggal_lahir" in emp:
                dob = pd.to_datetime(emp.get("tanggal_lahir"))
                dob_date = dob.date()
                umur = calculate_age(dob)
        except Exception:
            pass

        st.markdown("**Data Karyawan (otomatis diisi setelah konfirmasi)**")
        tanggal_check_key = f"tab2_tanggal_check_{st.session_state['tab2_form_counter']}"
        tanggal_check = st.date_input("Tanggal Pemeriksaan", datetime.today(), key=tanggal_check_key)

        lokasi_widget = st.text_input("Lokasi Kerja", value=lokasi_val, disabled=True)
        jabatan_widget = st.text_input("Jabatan", value=jabatan_val, disabled=True)

        col_d1, col_d2, col_d3 = st.columns(3)
        col_d1.number_input("Hari Lahir", value=dob_date.day if dob_date else 0, disabled=True)
        col_d2.number_input("Bulan Lahir", value=dob_date.month if dob_date else 0, disabled=True)
        col_d3.number_input("Tahun Lahir", value=dob_date.year if dob_date else 0, disabled=True)

        st.text(f"Umur (otomatis): {umur if umur is not None else 'N/A'} tahun")

        k = st.session_state["tab2_form_counter"]
        tinggi = st.number_input("Tinggi Badan (cm)", min_value=1.0, max_value=300.0, step=0.1, key=f"tab2_tinggi_{k}")
        berat = st.number_input("Berat Badan (kg)", min_value=1.0, max_value=500.0, step=0.1, key=f"tab2_berat_{k}")
        lingkar_perut = st.number_input("Lingkar Perut (cm)", min_value=1.0, max_value=500.0, step=0.1, key=f"tab2_lingkar_{k}")
        bmi_val = calculate_bmi(berat, tinggi) if (berat and tinggi) else None
        st.text(f"BMI (otomatis): {round(bmi_val, 2) if bmi_val is not None else ''}")

        gd = st.number_input("Gula Darah (mg/dL)", min_value=1.0, max_value=2000.0, step=0.1, key=f"tab2_gd_{k}")
        chol = st.number_input("Cholesterol (mg/dL)", min_value=1.0, max_value=2000.0, step=0.1, key=f"tab2_chol_{k}")
        asam_urat = st.number_input("Asam Urat (mg/dL)", min_value=0.1, max_value=100.0, step=0.1, key=f"tab2_au_{k}")

        col_add, col_clear = st.columns([1, 1])
        add_clicked = col_add.button("➕ Tambah ke Draft", use_container_width=True)
        clear_draft_clicked = col_clear.button("🗑️ Clear Draft (hapus semua draft)", use_container_width=True)

        if add_clicked:
            if not st.session_state.get("selected_emp_uid"):
                st.error("⚠️ Silakan konfirmasi karyawan terlebih dahulu sebelum menambah ke draft.")
            else:
                missing = []
                if not tinggi: missing.append("Tinggi")
                if not berat: missing.append("Berat")
                if not lingkar_perut: missing.append("Lingkar Perut")
                if not gd: missing.append("Gula Darah")
                if not chol: missing.append("Cholesterol")
                if not asam_urat: missing.append("Asam Urat")
                if missing:
                    st.error(f"⚠️ Field wajib belum diisi: {', '.join(missing)}")
                else:
                    new_row = pd.DataFrame([{
                        "employee_uid": st.session_state.get("selected_emp_uid"),
                        "tanggal": pd.to_datetime(tanggal_check),
                        "tanggal_lahir": pd.to_datetime(emp.get("tanggal_lahir")) if emp.get("tanggal_lahir") else pd.NaT,
                        "umur": umur,
                        "tinggi": float(tinggi),
                        "berat": float(berat),
                        "lingkar_perut": float(lingkar_perut),
                        "bmi": float(round(bmi_val, 2)) if bmi_val is not None else None,
                        "gestational_diabetes": float(gd),
                        "cholesterol": float(chol),
                        "asam_urat": float(asam_urat),
                        "lokasi": lokasi_val,
                        "nama": emp.get("nama", ""),
                        "jabatan": emp.get("jabatan", "")
                    }])
                    st.session_state["draft_data"] = pd.concat(
                        [st.session_state["draft_data"], new_row], ignore_index=True
                    )
                    st.success(f"✅ Data untuk {emp.get('nama','-')} ditambahkan ke draft!")
                    st.session_state["tab2_form_counter"] += 1
                    st.rerun()

        if clear_draft_clicked:
            st.session_state["draft_data"] = pd.DataFrame(columns=CHECKUP_COLUMNS)
            st.warning("🗑️ Semua draft telah dihapus!")
            st.rerun()

        if not st.session_state["draft_data"].empty:
            st.subheader("📋 Draft Data")
            st.dataframe(st.session_state["draft_data"], use_container_width=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Submit Semua Draft (Karyawan)"):
                    save_checkups(st.session_state["draft_data"])
                    st.session_state["draft_data"] = pd.DataFrame(columns=CHECKUP_COLUMNS)
                    st.success("✅ Semua draft berhasil disimpan ke database.")
                    st.rerun()
            with col2:
                if st.button("Hapus Semua Draft (Karyawan)"):
                    st.session_state["draft_data"] = pd.DataFrame(columns=CHECKUP_COLUMNS)
                    st.warning("⚠️ Semua draft dihapus.")
                    st.rerun()

    # ------------------------- Tab 2: Riwayat Check-Up -------------------------
    with tab2:
        st.subheader("📖 Riwayat Check-Up Karyawan")

        df = load_checkups()
        df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
        df['tanggal_lahir'] = pd.to_datetime(df['tanggal_lahir'], errors='coerce')

    # --- Define default locations locally for now ---
        LOKASI_DEFAULT = ["Kantor", "Rig 1", "Rig 2", "Rig 3", "Rig 4"]

    # --- Inline status assignment logic ---
        df['status'] = 'Well'
        df.loc[
            (df['gestational_diabetes'] > 120) |
            (df['cholesterol'] > 240) |
            (df['asam_urat'] > 7),
            'status'
        ] = 'Unwell'

    # --- Inline add_month_year logic ---
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
                key="nurse_filter_bulan"
            )
        with col2:
            filter_tahun = st.selectbox(
                "Filter Tahun",
                options=[0] + sorted(df["tahun"].unique()),
                index=0,
                format_func=lambda x: "All" if x == 0 else str(x),
                key="nurse_filter_tahun"
            )
        with col3:
            filter_lokasi = st.multiselect(
                "Filter Lokasi",
                options=lokasi_options,
                default=lokasi_options,
                key="nurse_filter_lokasi"
            )
        with col4:
            filter_status = st.multiselect(
                "Filter Status",
                options=status_options,
                default=status_options,
                key="nurse_filter_status"
            )

        df_filtered = df.copy()
        if filter_tahun != 0:
            df_filtered = df_filtered[df_filtered['tahun'] == filter_tahun]
        if filter_bulan != 0:
            df_filtered = df_filtered[df_filtered['bulan'] == filter_bulan]
        if filter_lokasi:
            df_filtered = df_filtered[df_filtered['lokasi'].isin(filter_lokasi)]
        if filter_status:
            df_filtered = df_filtered[df_filtered['status'].isin(filter_status)]

    # Deduplicate for KPIs: only latest checkup per UID
        df_latest = df_filtered.sort_values('tanggal', ascending=False).drop_duplicates(subset=['uid'], keep='first')

    # KPIs
        total_karyawan = len(df['uid'].unique())
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("👥 Total Karyawan", total_karyawan)
        k2.metric("📝 Total Checkups", len(df_latest))
        k3.metric("✅ Well", (df_latest['status'] == "Well").sum())
        k4.metric("⚠️ Unwell", (df_latest['status'] == "Unwell").sum())

    # Highlight Unwell
        def highlight_unwell(row):
            return ['color: red' if row.status == 'Unwell' else '' for _ in row]

        display_cols = ['uid','nama','jabatan','status','tanggal','lokasi','tinggi','lingkar_perut','bmi']

        df_to_display = df_latest[display_cols].sort_values("tanggal", ascending=False).reset_index(drop=True)

        st.dataframe(
            df_to_display.style.format({
                'tinggi': '{:.2f}',
                'lingkar_perut': '{:.2f}',
            '   bmi': '{:.2f}'
            }).apply(highlight_unwell, axis=1),
            use_container_width=True
        )


    # ----------------------
    # Tab 4: Download Data Karyawan
    # ----------------------
    with tab4:
        st.subheader("💾 Download Data Karyawan untuk Update Check-Up")

        try:
            employees = get_employees()  # fetch master karyawan
            if employees.empty:
                st.info("ℹ️ Tidak ada data karyawan untuk diunduh.")
            else:
            # Create template with new columns (without bmi and umur)
                cols = [
                    "uid", "nama", "jabatan", "lokasi", "tanggal_lahir", "tanggal",
                    "tinggi", "berat", "lingkar_perut", "gestational_diabetes",
                    "cholesterol", "asam_urat", "status"
                ]
                df_template = pd.DataFrame(columns=cols)

            # Fill uid, nama, jabatan, lokasi from master
                df_template["uid"] = employees["uid"] if "uid" in employees.columns else ""
                df_template["nama"] = employees["nama"] if "nama" in employees.columns else ""
                df_template["jabatan"] = employees["jabatan"] if "jabatan" in employees.columns else ""
                df_template["lokasi"] = employees["lokasi"] if "lokasi" in employees.columns else ""

            # Other columns stay empty for nurse to fill
                empty_cols = ["tanggal_lahir","tanggal","tinggi","berat","lingkar_perut",
                              "gestational_diabetes","cholesterol","asam_urat"]
                df_template[empty_cols] = ""

            # Write to Excel in-memory
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    df_template.to_excel(writer, index=False)
                data = output.getvalue()

                st.download_button(
                    label="⬇️ Unduh Template Data Karyawan",
                    data=data,
                    file_name="data_karyawan_update.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.error(f"❌ Gagal memuat data karyawan: {e}")


    # ----------------------
    # Tab 5: Edit Data Karyawan
    # ----------------------
    with tab5:
        st.subheader("✏️ Edit Data Karyawan")

        try:
            employees = get_employees()
            if employees.empty:
                st.info("ℹ️ Tidak ada data karyawan untuk diedit.")
            else:
            # Build selector: show name + uid
                display_options = ["-- Pilih Karyawan --"] + [
                    f"{row['nama']} ({row['uid']})" for _, row in employees.iterrows()
                ]
                selected_display = st.selectbox("Pilih Karyawan", display_options, index=0)

                if selected_display != "-- Pilih Karyawan --":
                # Extract uid from selection
                    selected_uid = selected_display.split("(")[-1].replace(")","").strip()

                # Load existing check-ups
                    df_checkups = load_checkups()
                    df_emp = df_checkups[df_checkups["uid"].astype(str) == selected_uid]

                    if df_emp.empty:
                        st.info("ℹ️ Belum ada data check-up untuk karyawan ini.")
                    else:
                        st.markdown("**Klik cell untuk mengedit data.**")
                        edited_df = st.data_editor(   # ✅ updated call
                            df_emp.drop(columns=["id"], errors="ignore"),
                            num_rows="dynamic",
                            use_container_width=True
                        )

                    # Auto calculate BMI and umur
                        if not edited_df.empty:
                            for idx, row in edited_df.iterrows():
                                try:
                                # Recalculate umur
                                    if "tanggal_lahir" in row and pd.notnull(row["tanggal_lahir"]):
                                        dob = pd.to_datetime(row["tanggal_lahir"], dayfirst=True, errors="coerce")
                                        if dob:
                                            edited_df.at[idx, "umur"] = calculate_age(dob)
                                        else:
                                            edited_df.at[idx, "umur"] = None
                                # Recalculate BMI
                                    if "tinggi" in row and "berat" in row:
                                        tinggi = float(row["tinggi"]) if pd.notnull(row["tinggi"]) else None
                                        berat = float(row["berat"]) if pd.notnull(row["berat"]) else None
                                        edited_df.at[idx, "bmi"] = calculate_bmi(berat, tinggi) if (berat and tinggi) else None
                                except Exception:
                                    pass

                    # Save edited data
                        if st.button("💾 Simpan Perubahan"):
                            try:
                                save_uploaded_checkups(edited_df)
                                st.success("✅ Data karyawan berhasil diperbarui.")
                            except Exception as e:
                                st.error(f"❌ Gagal menyimpan perubahan: {e}")

        except Exception as e:
            st.error(f"❌ Gagal memuat data karyawan: {e}")







