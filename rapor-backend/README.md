# Rapor Backend API

Backend API untuk aplikasi pengelolaan nilai menggunakan **FastAPI**, **SQLite**, dan **SQLAlchemy**. Backend ini dirancang untuk digunakan oleh frontend **Streamlit**.

## 1. Ringkasan Sistem

Aplikasi ini digunakan untuk mengelola tabel nilai per mata pelajaran.

Fitur utama:

- Autentikasi admin dan teacher.
- Admin mengelola akun teacher.
- Teacher mengelola grade table miliknya sendiri.
- Admin dapat mengakses dan mengedit semua grade table.
- Grade table berisi students, assessment components, dan scores.
- Sistem menghitung final grade otomatis berdasarkan bobot komponen.
- Sistem menyediakan analytics.
- Sistem mendukung Excel export dan Excel import strict.

## 2. Arsitektur

Arsitektur project:

```text
Streamlit Frontend
        ↓ HTTP
FastAPI Backend
        ↓ SQLAlchemy ORM
SQLite Database
```

Jenis arsitektur:

```text
Client-Server + Layered Backend + Modular Monolith
```

Backend dibagi menjadi:

```text
routers/       → endpoint HTTP
schemas/       → validasi request/response Pydantic
services/      → business logic
models/        → SQLAlchemy ORM models
dependencies/  → dependency auth/database
core/          → config dan security
database/      → database session dan Base
```

## 3. Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- JWT
- passlib bcrypt
- openpyxl
- uv

## 4. Setup Project

### 4.1 Install dependency

```bash
uv sync
```

Jika ada dependency yang belum masuk:

```bash
uv add fastapi uvicorn sqlalchemy pydantic pydantic-settings python-jose passlib[bcrypt] python-multipart openpyxl
```

### 4.2 Buat file `.env`

Copy dari `.env.example`:

```bash
cp .env.example .env
```

PowerShell:

```powershell
Copy-Item .env.example .env
```

Isi `.env`:

```env
SECRET_KEY=rapor-development-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

DEFAULT_ADMIN_NIP=admin
DEFAULT_ADMIN_NAME=Administrator
DEFAULT_ADMIN_PASSWORD=admin123
```

### 4.3 Jalankan server

```bash
uv run uvicorn main:app --reload
```

Server berjalan di:

```text
http://127.0.0.1:8000
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

## 5. Akun Default Admin

Saat server pertama kali berjalan, sistem membuat default admin jika belum ada admin.

```text
NIP      : admin
Password : admin123
```

Nilai ini bisa diubah melalui `.env`.

## 6. Authentication

Login menggunakan **NIP dan password**.

Endpoint login memakai `OAuth2PasswordRequestForm`, sehingga body dikirim sebagai **form-encoded**, bukan JSON.

Walaupun field Swagger bernama `username`, nilainya diisi dengan NIP.

### Login

```http
POST /auth/login
```

Form data:

```text
username=admin
password=admin123
```

Response:

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

Untuk endpoint yang membutuhkan login, kirim header:

```http
Authorization: Bearer <access_token>
```

### Current user

```http
GET /auth/me
```

Response:

```json
{
  "id": 1,
  "nip": "admin",
  "name": "Administrator",
  "role": "admin",
  "is_active": true
}
```

## 7. Role dan Access Control

Sistem memiliki dua role:

```text
admin
teacher
```

Aturan akses:

| Role | Hak Akses |
|---|---|
| admin | Mengelola teacher |
| admin | Mengakses dan mengedit semua grade table |
| teacher | Membuat grade table miliknya sendiri |
| teacher | Mengakses dan mengedit grade table miliknya sendiri |
| teacher | Tidak dapat mengakses data teacher lain |

Sistem ini menggunakan:

```text
RBAC + ownership check
```

Artinya:

- RBAC membedakan role `admin` dan `teacher`.
- Ownership check memastikan teacher hanya dapat mengakses `grade_table.teacher_id == current_user.id`.

## 8. Aturan Data Utama

### Grade Table

- Satu grade table mewakili satu mata pelajaran.
- Grade table dimiliki oleh satu teacher.
- Admin dapat membuat grade table untuk teacher tertentu.
- Teacher hanya dapat membuat grade table untuk dirinya sendiri.

### Student

- Student hanya tersimpan di dalam satu grade table.
- Jika student yang sama ada di mata pelajaran lain, ia dibuat sebagai student record baru.
- `student_number` optional.
- `student_number` yang terisi tidak boleh duplikat dalam grade table yang sama.

### Component

- Component adalah komponen nilai seperti `Tugas`, `UTS`, `UAS`.
- `weight` harus lebih besar dari 0.
- `max_score` selalu 100.
- `order_index` digunakan untuk urutan tampilan/grafik.
- Nama component tidak boleh duplikat dalam grade table yang sama.

### Score

- Score berada pada rentang 0 sampai 100.
- Satu student hanya boleh punya satu score untuk satu component.
- Student dan component harus berasal dari grade table yang sama.

### Missing Score

Missing score adalah score yang belum diisi.

Aturan:

| Fitur | Missing Score |
|---|---|
| Result/final grade | Dihitung sebagai 0 |
| Analytics summary | Dihitung sebagai 0 |
| Analytics distribution | Dihitung sebagai 0 |
| Student progress | Ditampilkan sebagai 0 dengan `is_complete = false` |
| Student comparison | Ditampilkan sebagai 0 dengan `is_complete = false` |
| Excel export sheet Scores | Dikosongkan, bukan ditulis 0 |
| Excel import blank score | Dianggap missing score |

## 9. Format Error Umum

FastAPI mengembalikan error dalam format:

```json
{
  "detail": "Error message"
}
```

Status code umum:

| Status | Arti |
|---:|---|
| 400 | Request invalid / data melanggar aturan |
| 401 | Token/login tidak valid |
| 403 | Akses ditolak |
| 404 | Data tidak ditemukan |
| 422 | Validasi request Pydantic gagal |

## 10. Endpoint Auth

### 10.1 Login

```http
POST /auth/login
```

Form data:

```text
username=admin
password=admin123
```

Larangan/error:

| Kondisi | Status | Message |
|---|---:|---|
| NIP/password salah | 401 | `Invalid NIP or password` |
| User inactive | 403 | `User account is inactive` |

### 10.2 Current user

```http
GET /auth/me
```

Header:

```http
Authorization: Bearer <token>
```

Larangan/error:

| Kondisi | Status | Message |
|---|---:|---|
| Token invalid/hilang | 401 | `Could not validate credentials` |
| User inactive | 403 | `User account is inactive` |

## 11. Endpoint Admin: Teacher Management

Semua endpoint admin membutuhkan role `admin`.

### 11.1 List teachers

```http
GET /admin/teachers
```

Response:

```json
[
  {
    "id": 2,
    "nip": "T001",
    "name": "Budi Santoso",
    "role": "teacher",
    "is_active": true
  }
]
```

Larangan/error:

| Kondisi | Status | Message |
|---|---:|---|
| User bukan admin | 403 | `Admin access required` |

### 11.2 Create teacher

```http
POST /admin/teachers
```

Body:

```json
{
  "nip": "T001",
  "name": "Budi Santoso",
  "password": "teacher123"
}
```

Response:

```json
{
  "id": 2,
  "nip": "T001",
  "name": "Budi Santoso",
  "role": "teacher",
  "is_active": true
}
```

Larangan/error:

| Kondisi | Status | Message |
|---|---:|---|
| User bukan admin | 403 | `Admin access required` |
| NIP sudah dipakai | 400 | `NIP already registered` |

### 11.3 Update teacher

```http
PATCH /admin/teachers/{teacher_id}
```

Body partial:

```json
{
  "name": "Budi Updated"
}
```

atau:

```json
{
  "password": "newpassword123"
}
```

atau:

```json
{
  "is_active": false
}
```

Larangan/error:

| Kondisi | Status | Message |
|---|---:|---|
| User bukan admin | 403 | `Admin access required` |
| Teacher tidak ditemukan | 404 | `Teacher not found` |
| NIP sudah dipakai | 400 | `NIP already registered` |

### 11.4 Delete teacher

```http
DELETE /admin/teachers/{teacher_id}
```

Catatan:

- Delete bersifat permanent.
- Menghapus teacher akan menghapus semua grade table milik teacher tersebut.

Larangan/error:

| Kondisi | Status | Message |
|---|---:|---|
| User bukan admin | 403 | `Admin access required` |
| Teacher tidak ditemukan | 404 | `Teacher not found` |

## 12. Endpoint Grade Tables

### 12.1 List grade tables

```http
GET /grade-tables/
```

Aturan:

- Admin melihat semua grade table.
- Teacher hanya melihat grade table miliknya.

Response:

```json
[
  {
    "id": 1,
    "subject_name": "Matematika",
    "description": "Kelas 8A",
    "teacher_id": 2
  }
]
```

### 12.2 Create grade table

```http
POST /grade-tables/
```

Sebagai teacher:

```json
{
  "subject_name": "Matematika",
  "description": "Kelas 8A"
}
```

Sebagai admin:

```json
{
  "subject_name": "Matematika",
  "description": "Kelas 8A",
  "teacher_id": 2
}
```

Larangan/error:

| Kondisi | Status | Message |
|---|---:|---|
| Admin tidak mengirim `teacher_id` | 400 | `teacher_id is required when admin creates a grade table` |
| Teacher mengirim `teacher_id` | 403 | `Teacher cannot assign grade table owner` |
| Teacher target tidak ditemukan | 404 | `Teacher not found` |

### 12.3 Get grade table detail

```http
GET /grade-tables/{grade_table_id}
```

Larangan/error:

| Kondisi | Status | Message |
|---|---:|---|
| Grade table tidak ditemukan | 404 | `Grade table not found` |
| Teacher mengakses milik teacher lain | 403 | `You do not have access to this grade table` |

### 12.4 Update grade table

```http
PATCH /grade-tables/{grade_table_id}
```

Body partial:

```json
{
  "subject_name": "Fisika"
}
```

Larangan/error sama seperti detail grade table.

### 12.5 Delete grade table

```http
DELETE /grade-tables/{grade_table_id}
```

Catatan:

- Delete permanent.
- Menghapus grade table juga menghapus students, components, dan scores terkait.

Larangan/error sama seperti detail grade table.

## 13. Endpoint Components

### 13.1 List components

```http
GET /grade-tables/{grade_table_id}/components
```

### 13.2 Create component

```http
POST /grade-tables/{grade_table_id}/components
```

Body:

```json
{
  "name": "UTS",
  "weight": 2,
  "order_index": 1
}
```

Response:

```json
{
  "id": 1,
  "name": "UTS",
  "weight": 2,
  "max_score": 100,
  "order_index": 1,
  "grade_table_id": 1
}
```

Larangan/error:

| Kondisi | Status | Message |
|---|---:|---|
| Weight <= 0 | 422/400 | `weight` validation / `Weight must be greater than 0` |
| Nama component duplikat dalam grade table | 400 | `Component name already exists in this grade table` |
| Grade table tidak boleh diakses | 403 | `You do not have access to this grade table` |

### 13.3 Get component detail

```http
GET /grade-components/{component_id}
```

### 13.4 Update component

```http
PATCH /grade-components/{component_id}
```

Body partial:

```json
{
  "weight": 3
}
```

Larangan/error:

| Kondisi | Status | Message |
|---|---:|---|
| Component tidak ditemukan | 404 | `Grade component not found` |
| Nama component duplikat | 400 | `Component name already exists in this grade table` |
| User tidak punya akses ke grade table component | 403 | `You do not have access to this grade table` |

### 13.5 Delete component

```http
DELETE /grade-components/{component_id}
```

Catatan:

- Delete permanent.
- Menghapus component juga menghapus scores terkait component tersebut.

## 14. Endpoint Students

### 14.1 List students

```http
GET /grade-tables/{grade_table_id}/students
```

### 14.2 Create student

```http
POST /grade-tables/{grade_table_id}/students
```

Body:

```json
{
  "name": "Andi",
  "student_number": "001"
}
```

`student_number` optional:

```json
{
  "name": "Siti"
}
```

Larangan/error:

| Kondisi | Status | Message |
|---|---:|---|
| Student number duplikat dalam grade table | 400 | `Student number already exists in this grade table` |
| Grade table tidak boleh diakses | 403 | `You do not have access to this grade table` |

### 14.3 Get student detail

```http
GET /students/{student_id}
```

### 14.4 Update student

```http
PATCH /students/{student_id}
```

Body partial:

```json
{
  "name": "Andi Pratama"
}
```

Untuk mengosongkan kembali student number:

```json
{
  "student_number": null
}
```

Larangan/error:

| Kondisi | Status | Message |
|---|---:|---|
| Student tidak ditemukan | 404 | `Student not found` |
| Student number duplikat | 400 | `Student number already exists in this grade table` |
| User tidak punya akses ke grade table student | 403 | `You do not have access to this grade table` |

### 14.5 Delete student

```http
DELETE /students/{student_id}
```

Catatan:

- Delete permanent.
- Menghapus student juga menghapus scores milik student tersebut.

## 15. Endpoint Scores

### 15.1 List scores

```http
GET /grade-tables/{grade_table_id}/scores
```

### 15.2 Create score

```http
POST /grade-tables/{grade_table_id}/scores
```

Body:

```json
{
  "student_id": 1,
  "component_id": 1,
  "score": 85
}
```

Larangan/error:

| Kondisi | Status | Message |
|---|---:|---|
| Score < 0 atau > 100 | 422/400 | `score` validation / `must be between 0 and 100` |
| Student tidak ada di grade table tersebut | 404 | `Student not found in this grade table` |
| Component tidak ada di grade table tersebut | 404 | `Component not found in this grade table` |
| Score student-component sudah ada | 400 | `Score for this student and component already exists` |

### 15.3 Get score detail

```http
GET /scores/{score_id}
```

### 15.4 Update score

```http
PATCH /scores/{score_id}
```

Body:

```json
{
  "score": 90
}
```

Larangan/error:

| Kondisi | Status | Message |
|---|---:|---|
| Score tidak ditemukan | 404 | `Score not found` |
| Score < 0 atau > 100 | 422/400 | `score` validation |
| User tidak punya akses ke grade table score | 403 | `You do not have access to this grade table` |

### 15.5 Delete score

```http
DELETE /scores/{score_id}
```

## 16. Endpoint Results

### 16.1 Get final results

```http
GET /grade-tables/{grade_table_id}/results
```

Response:

```json
{
  "grade_table_id": 1,
  "subject_name": "Matematika",
  "teacher_id": 2,
  "teacher_name": "Budi Santoso",
  "total_weight": 6,
  "results": [
    {
      "student_id": 1,
      "student_name": "Andi",
      "student_number": "001",
      "component_scores": [
        {
          "component_id": 1,
          "component_name": "Tugas",
          "weight": 1,
          "score": 80
        }
      ],
      "final_grade": 78.33,
      "is_complete": true,
      "missing_components": []
    }
  ]
}
```

Formula:

```text
final_grade = sum(score × weight) / total_weight
```

Missing score dihitung sebagai 0.

Larangan/error:

| Kondisi | Status | Message |
|---|---:|---|
| Grade table tidak punya components | 400 | `Grade table has no components` |
| Total weight <= 0 | 400 | `Total component weight must be greater than 0` |
| User tidak punya akses | 403 | `You do not have access to this grade table` |

## 17. Endpoint Analytics

### 17.1 Analytics summary

```http
GET /grade-tables/{grade_table_id}/analytics/summary
```

Berisi:

- Rata-rata final grade.
- Final grade tertinggi.
- Final grade terendah.
- Rata-rata tiap component.
- Score tertinggi tiap component.
- Score terendah tiap component.
- Jumlah missing score tiap component.

Missing score dihitung sebagai 0, tetapi `is_complete` menunjukkan apakah nilai asli tersedia.

Larangan/error:

| Kondisi | Status | Message |
|---|---:|---|
| Grade table tidak punya components | 400 | `Grade table has no components` |
| Grade table tidak punya students | 400 | `Grade table has no students` |

### 17.2 Analytics distribution

```http
POST /grade-tables/{grade_table_id}/analytics/distribution
```

Untuk distribusi final grade:

```json
{
  "target": "final_grade",
  "component_id": null,
  "ranges": [
    { "label": "0-60", "min": 0, "max": 60 },
    { "label": "60-70", "min": 60, "max": 70 },
    { "label": "70-80", "min": 70, "max": 80 },
    { "label": "80-90", "min": 80, "max": 90 },
    { "label": "90-100", "min": 90, "max": 100 }
  ]
}
```

Untuk distribusi component:

```json
{
  "target": "component",
  "component_id": 2,
  "ranges": [
    { "label": "0-60", "min": 0, "max": 60 },
    { "label": "60-70", "min": 60, "max": 70 },
    { "label": "70-80", "min": 70, "max": 80 },
    { "label": "80-90", "min": 80, "max": 90 },
    { "label": "90-100", "min": 90, "max": 100 }
  ]
}
```

Aturan ranges:

- Jumlah range 1 sampai 10.
- Label harus unik.
- Range pertama harus mulai dari 0.
- Range terakhir harus berakhir di 100.
- `min < max`.
- `max` range saat ini harus sama dengan `min` range berikutnya.
- Interval menggunakan `min <= value < max`, kecuali range terakhir menggunakan `min <= value <= max`.

Larangan/error:

| Kondisi | Status | Message |
|---|---:|---|
| `target=component` tanpa `component_id` | 422 | `component_id is required when target is component` |
| `target=final_grade` tetapi ada `component_id` | 422 | `component_id must be null when target is final_grade` |
| Label range duplikat | 422 | `Range labels must be unique` |
| Range pertama tidak mulai dari 0 | 422 | `First range must start from 0` |
| Range terakhir tidak berakhir di 100 | 422 | `Last range must end at 100` |
| Range tidak continuous | 422 | `Ranges must be continuous and non-overlapping` |
| Component tidak ditemukan | 404 | `Component not found in this grade table` |

### 17.3 Student progress

```http
GET /grade-tables/{grade_table_id}/analytics/students/{student_id}/progress
```

Response:

```json
{
  "grade_table_id": 1,
  "subject_name": "Matematika",
  "student_id": 1,
  "student_name": "Andi",
  "student_number": "001",
  "is_complete": false,
  "missing_components": ["UAS"],
  "progress": [
    {
      "component_id": 1,
      "component_name": "Tugas",
      "weight": 1,
      "order_index": 1,
      "score": 80,
      "is_complete": true
    },
    {
      "component_id": 3,
      "component_name": "UAS",
      "weight": 3,
      "order_index": 3,
      "score": 0,
      "is_complete": false
    }
  ]
}
```

Larangan/error:

| Kondisi | Status | Message |
|---|---:|---|
| Student tidak ada di grade table tersebut | 404 | `Student not found in this grade table` |
| Grade table tidak punya components | 400 | `Grade table has no components` |

### 17.4 Student comparison

```http
POST /grade-tables/{grade_table_id}/analytics/student-comparison
```

Compare final grade:

```json
{
  "student_ids": [1, 2, 3]
}
```

Compare component tertentu:

```json
{
  "student_ids": [1, 2, 3],
  "component_id": 2
}
```

Aturan:

- Minimal 2 students.
- Maksimal 5 students.
- Student ID tidak boleh duplikat.
- Missing score ditampilkan sebagai 0 dengan `is_complete = false`.

Larangan/error:

| Kondisi | Status | Message |
|---|---:|---|
| Student kurang dari 2 / lebih dari 5 | 422 | Pydantic validation |
| Student ID duplikat | 400 | `Duplicate student IDs are not allowed` |
| Student tidak ada di grade table tersebut | 404 | `One or more students were not found in this grade table` |
| Component tidak ditemukan | 404 | `Component not found in this grade table` |

## 18. Endpoint Excel

### 18.1 Export Excel

```http
GET /grade-tables/{grade_table_id}/export/excel
```

Menghasilkan file `.xlsx`.

Sheets:

```text
Metadata
Components
Scores
Results
```

Catatan:

- Sheet `Scores` menampilkan missing score sebagai blank.
- Sheet `Results` menampilkan final grade statis dari backend.
- Excel tidak menggunakan formula.
- Backend tetap menjadi sumber perhitungan utama.

Larangan/error:

| Kondisi | Status | Message |
|---|---:|---|
| User tidak punya akses ke grade table | 403 | `You do not have access to this grade table` |
| Total weight <= 0 | 400 | `Total component weight must be greater than 0` |

### 18.2 Import Excel

```http
POST /grade-tables/import/excel
```

Form data:

```text
file=<file.xlsx>
```

Admin wajib memakai query:

```http
POST /grade-tables/import/excel?teacher_id=2
```

Teacher tidak boleh mengirim `teacher_id`.

Import selalu membuat grade table baru.

Sheet wajib:

```text
Metadata
Components
Scores
```

Sheet `Results` diabaikan.

#### Metadata sheet

Header wajib:

```text
Field
Value
```

Field wajib:

```text
Subject Name
```

Field optional:

```text
Description
```

Field lain yang diperbolehkan dan diabaikan:

```text
Grade Table ID
Teacher ID
Teacher NIP
Teacher Name
Exported At
```

Larangan/error:

| Kondisi | Status | Message |
|---|---:|---|
| Metadata sheet hilang | 400 | `Missing required sheets: Metadata` |
| Header tidak sesuai | 400 | `Metadata sheet missing required headers: ...` |
| Unknown field | 400 | `Metadata row X: Unknown metadata field '...'` |
| Duplicate field | 400 | `Metadata sheet contains duplicate field: Subject Name` |
| Subject Name kosong | 400 | `Metadata sheet must contain non-empty Subject Name` |

#### Components sheet

Header wajib:

```text
Component Name
Weight
Max Score
Order Index
```

Header optional:

```text
Component ID
```

Aturan:

- Component Name wajib.
- Component Name tidak boleh duplikat.
- Weight harus angka dan > 0.
- Max Score harus 100.
- Order Index harus integer.
- Max Score hanya untuk validasi template. Backend tetap menyimpan `max_score = 100`.

Larangan/error:

| Kondisi | Status | Message |
|---|---:|---|
| Components sheet hilang | 400 | `Missing required sheets: Components` |
| Unknown header | 400 | `Components sheet has unknown headers: ...` |
| Duplicate component | 400 | `Components sheet contains duplicate component name: UTS` |
| Weight bukan angka | 400 | `Components row X: Weight must be numeric` |
| Weight <= 0 | 400 | `Components row X: Weight must be greater than 0` |
| Max Score bukan 100 | 400 | `Components row X: Max Score must be 100` |
| Order Index bukan integer | 400 | `Components row X: Order Index must be an integer` |
| Tidak ada component | 400 | `Components sheet must contain at least one component` |

#### Scores sheet

Header wajib:

```text
Student Number
Student Name
```

Header optional:

```text
Student ID
```

Kolom component di Scores harus sama persis dengan component name di Components.

Aturan:

- Student Name wajib.
- Student Number optional.
- Student Number kosong boleh berulang.
- Student Number yang terisi tidak boleh duplikat.
- Score boleh kosong.
- Score kosong berarti missing score.
- Score yang diisi harus angka 0 sampai 100.
- Extra component column ditolak.
- Missing component column ditolak.

Larangan/error:

| Kondisi | Status | Message |
|---|---:|---|
| Scores sheet hilang | 400 | `Missing required sheets: Scores` |
| Header wajib hilang | 400 | `Scores sheet missing required headers: ...` |
| Header extra | 400 | `Scores sheet has unknown headers: ...` |
| Student Name kosong | 400 | `Scores row X: Student Name is required` |
| Student Number duplikat | 400 | `Scores row X: Duplicate student number '001'` |
| Score bukan angka | 400 | `Scores row X: UTS must be numeric` |
| Score di luar 0-100 | 400 | `Scores row X: UTS must be between 0 and 100` |
| Tidak ada student | 400 | `Scores sheet must contain at least one student` |

#### Import response

```json
{
  "grade_table_id": 5,
  "subject_name": "Matematika",
  "teacher_id": 2,
  "imported_components": 3,
  "imported_students": 30,
  "imported_scores": 85
}
```

## 19. Full Manual Testing Flow

Recommended manual test lewat Swagger:

```text
1. Login admin.
2. Admin create teacher.
3. Login teacher.
4. Teacher create grade table.
5. Teacher create components.
6. Teacher create students.
7. Teacher create scores.
8. GET results.
9. GET analytics summary.
10. POST analytics distribution.
11. POST student comparison.
12. Export Excel.
13. Import Excel.
14. Login teacher lain.
15. Pastikan teacher lain tidak bisa akses grade table tersebut.
16. Login admin.
17. Pastikan admin bisa akses grade table tersebut.
```

## 20. Catatan Development

### Hapus database development

Jika model berubah dan belum memakai migration:

```powershell
Remove-Item rapor.db
```

atau:

```bash
rm rapor.db
```

### Compile check

```bash
uv run python -m compileall .
```

### Run server

```bash
uv run uvicorn main:app --reload
```

## 21. Catatan Keamanan

- Jangan commit `.env`.
- Commit `.env.example`.
- Gunakan `SECRET_KEY` yang kuat.
- Password disimpan sebagai hash.
- Logout dilakukan di frontend dengan menghapus token.
- Backend belum menggunakan token blacklist.
