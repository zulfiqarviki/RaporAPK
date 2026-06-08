# Rapor Frontend

Frontend Streamlit untuk aplikasi Rapor/Nilai. Aplikasi ini digunakan untuk mengelola tabel nilai per mata pelajaran, termasuk teacher account management, grade table, students, components, scores, results, analytics, Excel export, dan Excel import.

Frontend ini berkomunikasi dengan backend FastAPI melalui HTTP API. Semua autentikasi, role access, ownership check, perhitungan final grade, analytics, dan validasi Excel strict ditangani oleh backend.

## Tech Stack

* Python 3.12+
* Streamlit
* Requests
* Pandas
* Altair
* python-dotenv
* uv

## Main Features

### Authentication

* Login menggunakan NIP dan password.
* Token disimpan di session state Streamlit.
* Logout dilakukan dengan menghapus token dari session frontend.

### Role-based UI

Aplikasi memiliki dua role:

| Role    | Akses                                                  |
| ------- | ------------------------------------------------------ |
| admin   | Mengelola akun teacher dan mengakses semua grade table |
| teacher | Mengelola grade table miliknya sendiri                 |

### Teacher Management

Admin dapat:

* melihat daftar teacher;
* membuat akun teacher;
* mengedit data teacher;
* mengaktifkan/nonaktifkan teacher;
* menghapus teacher.

### Grade Table Management

Admin dan teacher dapat:

* melihat grade table;
* membuat grade table;
* mengedit grade table;
* menghapus grade table;
* membuka detail grade table.

Perbedaan akses:

* Admin dapat melihat semua grade table.
* Teacher hanya dapat melihat grade table miliknya sendiri.
* Admin memilih teacher saat membuat grade table.
* Teacher otomatis membuat grade table untuk dirinya sendiri.

### Students

Dalam setiap grade table, user dapat:

* melihat daftar student;
* menambah student;
* mengedit student;
* menghapus student.

Catatan:

* Student hanya tersimpan di dalam satu grade table.
* `student_number` bersifat optional.
* `student_number` yang terisi tidak boleh duplikat dalam grade table yang sama.

### Components

Dalam setiap grade table, user dapat:

* melihat daftar component;
* menambah component;
* mengedit component;
* menghapus component.

Catatan:

* Component memiliki `name`, `weight`, `max_score`, dan `order_index`.
* `max_score` selalu bernilai 100 dan ditentukan oleh backend.
* `order_index` digunakan untuk mengatur urutan tampilan dan grafik.

### Scores

Dalam setiap grade table, user dapat:

* melihat matrix score;
* menambah score;
* mengedit score;
* menghapus score.

Catatan:

* Score berada pada rentang 0 sampai 100.
* Satu student hanya boleh memiliki satu score untuk satu component.
* Missing score berarti belum ada record score.
* Missing score akan dihitung sebagai 0 oleh backend untuk results dan analytics.

### Results

Tab Results menampilkan final grade dari backend.

Results menampilkan:

* student;
* component scores;
* final grade;
* status kelengkapan nilai;
* missing components.

Final grade dihitung oleh backend menggunakan formula:

```text
final_grade = sum(score × weight) / total_weight
```

### Analytics

Tab Analytics menyediakan:

* summary;
* distribution;
* student progress;
* student comparison.

Analytics tetap dihitung oleh backend. Frontend hanya menampilkan hasil dan menyediakan input yang dibutuhkan.

### Excel

Frontend mendukung:

* export grade table ke file `.xlsx`;
* import grade table dari file `.xlsx`.

Catatan:

* Export menghasilkan file dari backend.
* Import selalu membuat grade table baru.
* Admin wajib memilih teacher saat import.
* Teacher tidak memilih teacher saat import.
* Validasi format Excel dilakukan secara strict oleh backend.

## Project Structure

```text
rapor-frontend/
├── .env.example
├── README.md
├── app.py
├── pyproject.toml
├── uv.lock
└── src/
    ├── __init__.py
    ├── config.py
    ├── api/
    │   ├── __init__.py
    │   ├── client.py
    │   ├── auth.py
    │   ├── admin.py
    │   ├── grade_tables.py
    │   ├── grade_components.py
    │   ├── students.py
    │   ├── scores.py
    │   ├── results.py
    │   ├── analytics.py
    │   └── excel.py
    ├── auth/
    │   ├── __init__.py
    │   └── session.py
    ├── pages/
    │   ├── __init__.py
    │   ├── login.py
    │   ├── dashboard.py
    │   ├── admin_teachers.py
    │   ├── grade_tables.py
    │   ├── grade_table_detail.py
    │   ├── students.py
    │   ├── grade_components.py
    │   ├── scores.py
    │   ├── results.py
    │   ├── analytics.py
    │   └── excel.py
    └── ui/
        ├── __init__.py
        └── layout.py
```

## Folder Responsibilities

### `app.py`

Entry point utama Streamlit.

Bertanggung jawab untuk:

* inisialisasi session auth;
* auth guard;
* routing halaman;
* menampilkan sidebar berdasarkan role.

### `src/api/`

API client layer untuk berkomunikasi dengan backend FastAPI.

Folder ini tidak berisi UI dan tidak berisi business logic. Setiap file membungkus endpoint backend tertentu.

Contoh:

```text
src/api/students.py
```

berisi fungsi untuk memanggil endpoint students backend.

### `src/auth/`

Mengelola session authentication frontend.

Berisi logic untuk:

* menyimpan access token;
* menyimpan current user;
* login;
* logout;
* auth guard;
* role guard.

### `src/pages/`

Berisi halaman atau tab utama Streamlit.

Setiap file fokus pada tampilan dan interaksi user untuk satu modul aplikasi.

### `src/ui/`

Berisi komponen layout reusable, seperti sidebar.

## Prerequisites

Pastikan sudah menginstall:

* Python 3.12+
* uv

Backend harus berjalan terlebih dahulu sebelum frontend digunakan.

Struktur project yang disarankan:

```text
RapotAPK/
├── rapor-backend/
└── rapor-frontend/
```

## Environment Variables

Buat file `.env` berdasarkan `.env.example`.

```bash
cp .env.example .env
```

Untuk PowerShell:

```powershell
Copy-Item .env.example .env
```

Isi `.env`:

```env
BACKEND_URL=http://127.0.0.1:8000
```

Jika backend dijalankan di host/port lain, sesuaikan nilai `BACKEND_URL`.

## Installation

Masuk ke folder frontend:

```bash
cd rapor-frontend
```

Install dependency:

```bash
uv sync
```

Jika ada dependency yang belum tersedia, tambahkan dengan:

```bash
uv add streamlit requests python-dotenv pandas altair
```

## Running the Application

### 1. Run backend

Dari folder backend:

```bash
cd ../rapor-backend
uv run uvicorn main:app --reload
```

Backend berjalan di:

```text
http://127.0.0.1:8000
```

Swagger docs backend:

```text
http://127.0.0.1:8000/docs
```

### 2. Run frontend

Dari folder frontend:

```bash
cd ../rapor-frontend
uv run streamlit run app.py
```

Frontend berjalan di:

```text
http://localhost:8501
```

## Default Account

Default admin dibuat oleh backend saat server pertama kali dijalankan.

```text
NIP      : admin
Password : admin123
```

Nilai ini dapat berbeda jika konfigurasi `.env` backend sudah diubah.

## Basic Usage Flow

Recommended manual flow:

```text
1. Login sebagai admin.
2. Buat akun teacher.
3. Logout.
4. Login sebagai teacher.
5. Buat grade table.
6. Tambahkan components.
7. Tambahkan students.
8. Input scores.
9. Lihat results.
10. Lihat analytics.
11. Export Excel.
12. Import Excel.
13. Login sebagai admin.
14. Pastikan admin dapat melihat semua grade table.
```

## Development Commands

Compile check:

```bash
uv run python -m compileall app.py src
```

Run Streamlit:

```bash
uv run streamlit run app.py
```

Check installed dependency:

```bash
uv run python -c "import streamlit, requests, dotenv, pandas, altair; print('OK')"
```

## Backend Dependency

Frontend ini membutuhkan backend Rapor API yang menyediakan endpoint untuk:

* authentication;
* teacher management;
* grade tables;
* students;
* components;
* scores;
* results;
* analytics;
* Excel export/import.

Frontend tidak dapat berjalan penuh tanpa backend.

## Notes on Authentication

* Login menggunakan NIP dan password.
* Backend mengembalikan JWT access token.
* Token dikirim ke backend menggunakan header:

```http
Authorization: Bearer <access_token>
```

* Logout hanya menghapus token dari session frontend.
* Backend belum menggunakan token blacklist.

## Notes on Excel Import

Excel import bersifat strict dan divalidasi oleh backend.

Import file harus memiliki sheet:

```text
Metadata
Components
Scores
```

Sheet `Results` akan diabaikan saat import.

Import selalu membuat grade table baru, bukan mengubah grade table yang sedang dibuka.

## Repository Hygiene

File berikut tidak boleh di-commit:

```text
.env
.venv/
__pycache__/
*.pyc
```

Jika `.env` atau `.venv` sudah terlanjur masuk Git, hapus dari tracking:

```bash
git rm --cached .env
git rm -r --cached .venv
```

Lalu pastikan `.gitignore` berisi:

```gitignore
.env
.venv/
__pycache__/
*.pyc
.streamlit/
```

## Troubleshooting

### Backend connection error

Pastikan backend sudah berjalan:

```bash
uv run uvicorn main:app --reload
```

Pastikan `BACKEND_URL` di `.env` frontend benar:

```env
BACKEND_URL=http://127.0.0.1:8000
```

### Login gagal

Cek:

* NIP benar;
* password benar;
* backend berjalan;
* akun user masih aktif;
* default admin backend belum diubah.

### Import Excel gagal

Cek:

* file berformat `.xlsx`;
* sheet wajib tersedia;
* header sesuai template;
* component name di sheet Scores sama dengan sheet Components;
* score berada dalam rentang 0 sampai 100.

Jika format tidak sesuai, backend akan mengembalikan error detail yang ditampilkan di frontend.

## License

This project is intended for educational and development purposes.
