# Diagnostic Center Management System

A Diagnostic Center management system built with Flask + MySQL + Bootstrap + HTMX.

## Features
- Patient CRUD (Create, Read, Update, Delete)
- Live Search without page reload (HTMX)
- Test Catalog (CBC, X-ray, Urine, etc.)
- Create Reports (multiple tests per report)
- Test Result entry
- PDF report download (WeasyPrint)
- Auto status: pending to ready when all results are filled

## Tech Stack
| Layer | Technology |
|---|---|
| Backend | Flask (Python) |
| Database | MySQL (raw SQL, no ORM) |
| Frontend | Bootstrap 5, HTMX |
| PDF | WeasyPrint |

## Setup

### 1. Prerequisites
- Python 3.10+
- MySQL (XAMPP)

### 2. Clone
git clone <REPO_URL>
cd hospital_app

### 3. Virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

### 4. Create database
Open phpMyAdmin, go to SQL tab, paste contents of db/schema.sql, click Go.
Or CLI: sudo mysql < db/schema.sql

### 5. Start MySQL
sudo /opt/lampp/lampp start

### 6. Update DB_CONFIG in app.py
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "diagnostic_db"
}

### 7. Run
python app.py
Open http://127.0.0.1:5000 in a browser.

## Author
(Your Name) — (Your College)
