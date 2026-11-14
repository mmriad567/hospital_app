CREATE DATABASE IF NOT EXISTS diagnostic_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE diagnostic_db;

CREATE TABLE IF NOT EXISTS patients (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    phone      VARCHAR(20)  NOT NULL,
    gender     ENUM('male','female','other') NOT NULL,
    age        INT NOT NULL,
    address    VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tests (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    test_name    VARCHAR(100) NOT NULL,
    category     VARCHAR(50),
    price        DECIMAL(10,2) NOT NULL DEFAULT 0,
    normal_range VARCHAR(100),
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reports (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    patient_id   INT NOT NULL,
    report_date  DATE NOT NULL,
    status       ENUM('pending','ready','delivered') NOT NULL DEFAULT 'pending',
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS report_items (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    report_id    INT NOT NULL,
    test_id      INT NOT NULL,
    result_value VARCHAR(255),
    price        DECIMAL(10,2) NOT NULL DEFAULT 0,
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE,
    FOREIGN KEY (test_id)   REFERENCES tests(id)
);

INSERT INTO patients (name, phone, gender, age, address) VALUES
('Rahim',  '01712345678', 'male',   35, 'Dhaka'),
('Fatema', '01898765432', 'female', 28, 'Chattogram');

INSERT INTO tests (test_name, category, price, normal_range) VALUES
('CBC',           'Blood', 300.00, 'Hemoglobin: 12-16 g/dL'),
('Blood Sugar',   'Blood', 150.00, 'Fasting: 70-100 mg/dL'),
('Chest X-ray',   'X-ray', 500.00, 'Normal chest'),
('Urine R/E',     'Urine', 200.00, 'Normal'),
('Lipid Profile', 'Blood', 800.00, 'Cholesterol: <200 mg/dL');
