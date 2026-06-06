CREATE DATABASE IF NOT EXISTS hospital_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE hospital_db;

--  TABLE: patients
CREATE TABLE IF NOT EXISTS patients (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    name           VARCHAR(100)                          NOT NULL,
    age            INT                                   NOT NULL,
    gender         ENUM('Male','Female','Other')         NOT NULL,
    phone          VARCHAR(15)                           NOT NULL,
    email          VARCHAR(100),
    address        TEXT,
    blood_group    VARCHAR(5),
    admission_date DATE                                  DEFAULT (CURRENT_DATE),
    created_at     TIMESTAMP                             DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_patient_age   CHECK (age > 0 AND age < 150),
    CONSTRAINT chk_patient_phone CHECK (phone REGEXP '^[0-9+\\-\\s]{7,15}$')
);
--  TABLE: doctors
CREATE TABLE IF NOT EXISTS doctors (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100)  NOT NULL,
    specialization  VARCHAR(100)  NOT NULL,
    phone           VARCHAR(15)   NOT NULL,
    email           VARCHAR(100),
    experience      INT           DEFAULT 0,
    available       TINYINT(1)    DEFAULT 1,
    created_at      TIMESTAMP     DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_doctor_exp   CHECK (experience >= 0 AND experience < 70),
    CONSTRAINT chk_doctor_phone CHECK (phone REGEXP '^[0-9+\\-\\s]{7,15}$')
);

--  TABLE: appointments
CREATE TABLE IF NOT EXISTS appointments (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    patient_id        INT                                            NOT NULL,
    doctor_id         INT                                            NOT NULL,
    appointment_date  DATE                                           NOT NULL,
    appointment_time  TIME                                           NOT NULL,
    status            ENUM('Scheduled','Completed','Cancelled')      DEFAULT 'Scheduled',
    notes             TEXT,
    created_at        TIMESTAMP                                      DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id)  REFERENCES doctors(id)  ON DELETE CASCADE
);


--  TABLE: medicines
CREATE TABLE IF NOT EXISTS medicines (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(100)    NOT NULL,
    category     VARCHAR(100),
    quantity     INT             DEFAULT 0,
    price        DECIMAL(10,2)   DEFAULT 0.00,
    expiry_date  DATE,
    supplier     VARCHAR(100),
    created_at   TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_med_qty   CHECK (quantity >= 0),
    CONSTRAINT chk_med_price CHECK (price >= 0)
);

--  TABLE: billing
CREATE TABLE IF NOT EXISTS billing (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    patient_id      INT                                  NOT NULL,
    total_amount    DECIMAL(10,2)                        NOT NULL,
    paid_amount     DECIMAL(10,2)                        DEFAULT 0.00,
    payment_status  ENUM('Pending','Partial','Paid')      DEFAULT 'Pending',
    payment_date    DATE,
    description     TEXT,
    created_at      TIMESTAMP                            DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    CONSTRAINT chk_bill_total CHECK (total_amount >= 0),
    CONSTRAINT chk_bill_paid  CHECK (paid_amount >= 0)
);
SHOW TABLES;
