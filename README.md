# Hospital-Managment-System
A Python + MySQL desktop Hospital Management System with a modern dark UI — manage patients, doctors, appointments, rooms, and billing in one app.
# 🏥 MediCore — Hospital Management System

A full-featured, desktop-based Hospital Management System built with Python and Tkinter, backed by a MySQL database. MediCore provides a clean, modern dark-themed UI to manage patients, doctors, appointments, rooms, medicines, and billing — all from a single application.

---

## ✨ Features

### 📊 Dashboard
- Real-time statistics cards: Total Patients, Doctors, Appointments, Rooms, Bills, and Today's Appointments
- Recent patients table for a quick overview

### 👤 Patients
- Add, update, and delete patient records
- Fields: Name, Age, Gender, Phone, Email, Address, Blood Group, Admission Date
- Live search/filter by name
- Input validation on all fields

### 🩺 Doctors
- Manage doctor profiles with specialization, experience, and availability status
- Search by name or specialization
- Toggle availability (Available / Not Available)

### 📅 Appointments
- Book appointments by linking patients and doctors
- Set date, time, status (Scheduled / Completed / Cancelled), and notes
- Dropdown selection populated from live database records

### 🛏 Rooms
- Manage room inventory: room number, type, floor, capacity, price per day
- Room types: General, Private, ICU, Emergency, Maternity, Pediatric
- Status tracking: Available, Occupied, Under Maintenance
- Assign rooms to patients
- Summary bar showing room availability stats

### 💰 Billing
- Create and manage bills linked to patients
- Track total amount, paid amount, and payment status (Pending / Partial / Paid)
- Live summary showing total billed, collected, and pending amounts

---

## 🖥️ Tech Stack

| Component      | Technology              |
|---------------|--------------------------|
| GUI Framework  | Python Tkinter + ttk    |
| Database       | MySQL (via mysql-connector-python) |
| Validation     | Python `re` (regex)     |
| Styling        | Custom dark theme (Deep Medical Blue + Gold) |

---

## 📋 Prerequisites

- Python 3.9+
- MySQL Server (local or remote)
- MySQL Workbench (recommended for DB setup)

---

## ⚙️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/medicore-hospital.git
cd medicore-hospital
```

### 2. Install Dependencies
```bash
pip install mysql-connector-python
```

### 3. Set Up the Database
Open MySQL Workbench (or any MySQL client) and run the provided SQL script:
```sql
source hospital_db.sql
```
This creates the `hospital_db` database with all required tables:
- `patients`
- `doctors`
- `appointments`
- `medicines`
- `billing`
- `rooms`

### 4. Configure Database Credentials
Open `hospital.py` and update the `DB_CONFIG` block at the top of the file:
```python
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",          # your MySQL username
    "password": "your_password", # your MySQL password
    "database": "hospital_db"
}
```

### 5. Run the Application
```bash
python hospital.py
```

---

## 🗂️ Project Structure

```
medicore-hospital/
├── hospital.py        # Main application (UI + logic)
└── hospital_db.sql    # MySQL database schema
```

---

## 🗃️ Database Schema

| Table          | Key Fields                                              |
|----------------|---------------------------------------------------------|
| `patients`     | id, name, age, gender, phone, email, blood_group, admission_date |
| `doctors`      | id, name, specialization, phone, experience, available  |
| `appointments` | id, patient_id, doctor_id, date, time, status, notes   |
| `medicines`    | id, name, category, quantity, price, expiry_date, supplier |
| `billing`      | id, patient_id, total_amount, paid_amount, payment_status |
| `rooms`        | id, room_number, type, floor, capacity, price_per_day, status |

All foreign keys use `ON DELETE CASCADE` to maintain referential integrity.

---

## ✅ Input Validation

The system validates all form inputs before saving to the database:

- **Names**: Letters, spaces, dots, and hyphens only — no digits
- **Age**: Whole number between 1 and 149
- **Phone**: 7–15 characters, digits with optional `+` and `-`
- **Email**: Optional; validated against standard email format
- **Dates**: Must follow `YYYY-MM-DD` format
- **Times**: Must follow `HH:MM` format
- **Amounts**: Must be non-negative numbers

---

## 🎨 UI Design

- **Theme**: Deep Medical Blue (`#0A0F1E`) with Gold accents (`#FFD700`)
- **Font**: Segoe UI for labels, Consolas for data fields
- **Layout**: Sidebar navigation + split-pane form/table layout per page
- **Interactions**: Hover effects on buttons, placeholder text in inputs, alternating row colors in tables

---

## 🐛 Troubleshooting

**Cannot connect to MySQL**
- Ensure MySQL Server is running
- Verify credentials in `DB_CONFIG`
- Confirm `hospital_db.sql` has been executed first

**Table not found errors**
- Re-run `hospital_db.sql` in MySQL Workbench to recreate missing tables

**Module not found**
- Run `pip install mysql-connector-python` and ensure Python 3.9+ is used

---

## 📄 License

This project is open source. Feel free to use and modify it for personal or educational purposes.

---

## 🙏 Credits

- Built with [Python Tkinter](https://docs.python.org/3/library/tkinter.html)
- Database powered by [MySQL](https://www.mysql.com/)
- Connector via [mysql-connector-python](https://pypi.org/project/mysql-connector-python/)
