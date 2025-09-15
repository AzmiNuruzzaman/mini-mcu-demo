-- --- Employees table ---
CREATE TABLE employees (
    employee_uid UUID PRIMARY KEY,
    nama VARCHAR(255) NOT NULL,
    jabatan VARCHAR(255) NOT NULL,
    lokasi VARCHAR(255) NOT NULL DEFAULT 'Kantor'
);

-- --- Checkups table ---
CREATE TABLE checkups (
    id SERIAL PRIMARY KEY,
    employee_uid UUID NOT NULL REFERENCES employees(employee_uid) ON DELETE CASCADE,
    tanggal DATE NOT NULL,
    tinggi NUMERIC(5,2),
    berat NUMERIC(5,2),
    lingkar_perut NUMERIC(5,2),
    bmi NUMERIC(5,2),
    gestational_diabetes BOOLEAN,
    cholesterol NUMERIC(6,2),
    asam_urat NUMERIC(6,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- --- Users table (kept as-is) ---
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    nik VARCHAR(50) UNIQUE
);
