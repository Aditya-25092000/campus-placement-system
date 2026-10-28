-- ============================================================================
-- Campus Placement & Eligibility Management System
-- Database Schema (MySQL 8+)
-- ============================================================================
-- This file creates the complete database schema with all tables, indexes,
-- foreign keys, and constraints.
-- ============================================================================

-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS campus_placement
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE campus_placement;

-- ============================================================================
-- DROP TABLES in reverse dependency order for clean re-initialization
-- ============================================================================
DROP TABLE IF EXISTS admin_users;
DROP TABLE IF EXISTS offers;
DROP TABLE IF EXISTS interview_rounds;
DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS job_required_skills;
DROP TABLE IF EXISTS job_allowed_departments;
DROP TABLE IF EXISTS job_postings;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS student_skills;
DROP TABLE IF EXISTS skills;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS departments;

-- ============================================================================
-- 1. DEPARTMENTS
-- ============================================================================
CREATE TABLE IF NOT EXISTS departments (
    department_id   INT AUTO_INCREMENT PRIMARY KEY,
    dept_name       VARCHAR(100) NOT NULL UNIQUE,
    dept_code       VARCHAR(10)  NOT NULL UNIQUE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================================
-- 2. STUDENTS
-- ============================================================================
CREATE TABLE IF NOT EXISTS students (
    student_id        INT AUTO_INCREMENT PRIMARY KEY,
    enrollment_no     VARCHAR(20)   NOT NULL UNIQUE,
    full_name         VARCHAR(100)  NOT NULL,
    email             VARCHAR(100)  NOT NULL UNIQUE,
    phone             VARCHAR(15),
    department_id     INT           NOT NULL,
    graduation_year   INT           NOT NULL,
    cgpa              DECIMAL(4,2)  NOT NULL,
    active_backlogs   INT           NOT NULL DEFAULT 0,
    registration_date DATE          NOT NULL DEFAULT (CURRENT_DATE),
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT chk_students_cgpa       CHECK (cgpa >= 0 AND cgpa <= 10),
    CONSTRAINT chk_students_backlogs   CHECK (active_backlogs >= 0),

    -- Foreign Keys
    CONSTRAINT fk_students_department
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE RESTRICT,

    -- Indexes for common queries
    INDEX idx_students_department  (department_id),
    INDEX idx_students_grad_year   (graduation_year),
    INDEX idx_students_cgpa        (cgpa)
) ENGINE=InnoDB;

-- ============================================================================
-- 3. SKILLS
-- ============================================================================
CREATE TABLE IF NOT EXISTS skills (
    skill_id    INT AUTO_INCREMENT PRIMARY KEY,
    skill_name  VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- ============================================================================
-- 4. STUDENT_SKILLS (Junction Table)
-- ============================================================================
CREATE TABLE IF NOT EXISTS student_skills (
    student_id  INT NOT NULL,
    skill_id    INT NOT NULL,

    PRIMARY KEY (student_id, skill_id),

    CONSTRAINT fk_ss_student
        FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_ss_skill
        FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- 5. COMPANIES
-- ============================================================================
CREATE TABLE IF NOT EXISTS companies (
    company_id      INT AUTO_INCREMENT PRIMARY KEY,
    company_name    VARCHAR(100) NOT NULL UNIQUE,
    industry        VARCHAR(50),
    website         VARCHAR(200),
    hr_contact_name VARCHAR(100),
    hr_email        VARCHAR(100),
    contact_number  VARCHAR(15),
    description     TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================================
-- 6. JOB_POSTINGS
-- ============================================================================
CREATE TABLE IF NOT EXISTS job_postings (
    job_id                INT AUTO_INCREMENT PRIMARY KEY,
    company_id            INT           NOT NULL,
    job_title             VARCHAR(100)  NOT NULL,
    job_description       TEXT,
    job_location          VARCHAR(100),
    job_type              ENUM('Full-time','Internship','Part-time','Contract') DEFAULT 'Full-time',
    min_cgpa              DECIMAL(4,2)  DEFAULT 0.00,
    max_backlogs          INT           DEFAULT 0,
    eligible_grad_year    INT,
    application_open_date DATE          NOT NULL,
    application_deadline  DATE          NOT NULL,
    status                ENUM('Active','Closed','Draft') DEFAULT 'Active',
    created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT chk_jp_min_cgpa    CHECK (min_cgpa >= 0 AND min_cgpa <= 10),
    CONSTRAINT chk_jp_backlogs    CHECK (max_backlogs >= 0),

    -- Foreign Keys
    CONSTRAINT fk_jp_company
        FOREIGN KEY (company_id) REFERENCES companies(company_id)
        ON DELETE RESTRICT,

    -- Indexes
    INDEX idx_jp_company   (company_id),
    INDEX idx_jp_status    (status),
    INDEX idx_jp_deadline  (application_deadline)
) ENGINE=InnoDB;

-- ============================================================================
-- 7. JOB_ALLOWED_DEPARTMENTS (Junction Table)
-- ============================================================================
CREATE TABLE IF NOT EXISTS job_allowed_departments (
    job_id        INT NOT NULL,
    department_id INT NOT NULL,

    PRIMARY KEY (job_id, department_id),

    CONSTRAINT fk_jad_job
        FOREIGN KEY (job_id) REFERENCES job_postings(job_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_jad_department
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- 8. JOB_REQUIRED_SKILLS (Junction Table)
-- ============================================================================
CREATE TABLE IF NOT EXISTS job_required_skills (
    job_id    INT NOT NULL,
    skill_id  INT NOT NULL,

    PRIMARY KEY (job_id, skill_id),

    CONSTRAINT fk_jrs_job
        FOREIGN KEY (job_id) REFERENCES job_postings(job_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_jrs_skill
        FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- 9. APPLICATIONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS applications (
    application_id  INT AUTO_INCREMENT PRIMARY KEY,
    student_id      INT NOT NULL,
    job_id          INT NOT NULL,
    status          ENUM('Applied','Shortlisted','Interview','Selected','Rejected','Withdrawn') DEFAULT 'Applied',
    applied_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- A student can apply to a job only once
    UNIQUE KEY unique_student_job (student_id, job_id),

    -- Foreign Keys
    CONSTRAINT fk_app_student
        FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_app_job
        FOREIGN KEY (job_id) REFERENCES job_postings(job_id)
        ON DELETE RESTRICT,

    -- Indexes
    INDEX idx_app_status (status),
    INDEX idx_app_job    (job_id)
) ENGINE=InnoDB;

-- ============================================================================
-- 10. INTERVIEW_ROUNDS
-- ============================================================================
CREATE TABLE IF NOT EXISTS interview_rounds (
    interview_id    INT AUTO_INCREMENT PRIMARY KEY,
    application_id  INT          NOT NULL,
    round_name      VARCHAR(50)  NOT NULL,
    scheduled_date  DATETIME     NOT NULL,
    interview_mode  ENUM('In-Person','Online','Hybrid') DEFAULT 'In-Person',
    location_details VARCHAR(200),
    status          ENUM('Scheduled','Completed','Cancelled') DEFAULT 'Scheduled',
    result          ENUM('Passed','Failed','Pending') DEFAULT 'Pending',
    feedback        TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Each application can have only one round with the same name
    UNIQUE KEY unique_app_round (application_id, round_name),

    -- Foreign Keys
    CONSTRAINT fk_ir_application
        FOREIGN KEY (application_id) REFERENCES applications(application_id)
        ON DELETE CASCADE,

    -- Indexes
    INDEX idx_ir_scheduled (scheduled_date),
    INDEX idx_ir_status    (status)
) ENGINE=InnoDB;

-- ============================================================================
-- 11. OFFERS
-- ============================================================================
CREATE TABLE IF NOT EXISTS offers (
    offer_id        INT AUTO_INCREMENT PRIMARY KEY,
    application_id  INT           NOT NULL,
    student_id      INT           NOT NULL,
    company_id      INT           NOT NULL,
    job_id          INT           NOT NULL,
    offer_date      DATE          NOT NULL,
    ctc_lpa         DECIMAL(10,2) NOT NULL,
    offer_status    ENUM('Pending','Accepted','Declined') DEFAULT 'Pending',
    joining_date    DATE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- One offer per application
    UNIQUE KEY unique_app_offer (application_id),

    -- Foreign Keys
    CONSTRAINT fk_offer_application
        FOREIGN KEY (application_id) REFERENCES applications(application_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_offer_student
        FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_offer_company
        FOREIGN KEY (company_id) REFERENCES companies(company_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_offer_job
        FOREIGN KEY (job_id) REFERENCES job_postings(job_id)
        ON DELETE RESTRICT,

    -- Indexes
    INDEX idx_offer_student (student_id),
    INDEX idx_offer_status  (offer_status)
) ENGINE=InnoDB;

-- ============================================================================
-- 12. ADMIN_USERS
-- ============================================================================
CREATE TABLE IF NOT EXISTS admin_users (
    admin_id      INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(100) NOT NULL,
    email         VARCHAR(100),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================================
-- Schema creation complete.
-- ============================================================================
