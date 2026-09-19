-- ============================================================
-- SmartHire AI - MySQL schema
-- ============================================================
-- The FastAPI app also creates these tables automatically through
-- SQLAlchemy (Base.metadata.create_all). This file is provided so the
-- schema can be shown in the project report and created manually if needed.
--
-- Usage:
--   mysql -u root -p < database/schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS smarthire_ai
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smarthire_ai;

-- ------------------------------------------------------------
-- 1. users  (one row per account, whatever the role)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  name           VARCHAR(120) NOT NULL,
  email          VARCHAR(160) NOT NULL UNIQUE,
  password_hash  VARCHAR(255) NOT NULL,
  role           ENUM('candidate','employer','admin') NOT NULL DEFAULT 'candidate',
  phone          VARCHAR(20),
  is_active      TINYINT NOT NULL DEFAULT 1,
  created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at     DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX ix_users_role (role)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 2. candidate_profiles  (1:1 with users where role = candidate)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS candidate_profiles (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  user_id        INT NOT NULL UNIQUE,
  education      VARCHAR(255),
  location       VARCHAR(120),
  skills         TEXT,
  experience     FLOAT DEFAULT 0,
  certifications TEXT,
  bio            TEXT,
  resume_file    VARCHAR(255),
  resume_score   FLOAT,
  created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at     DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_profile_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 3. companies  (1:1 with users where role = employer)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS companies (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  user_id      INT NOT NULL UNIQUE,
  company_name VARCHAR(160) NOT NULL,
  description  TEXT,
  website      VARCHAR(200),
  location     VARCHAR(120),
  industry     VARCHAR(120),
  created_at   DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_company_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 4. jobs  (N:1 with companies)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS jobs (
  id                  INT AUTO_INCREMENT PRIMARY KEY,
  company_id          INT NOT NULL,
  title               VARCHAR(160) NOT NULL,
  description         TEXT NOT NULL,
  required_skills     TEXT NOT NULL,
  preferred_skills    TEXT,
  experience_required FLOAT DEFAULT 0,
  education_required  VARCHAR(120),
  location            VARCHAR(120),
  employment_type     VARCHAR(60) DEFAULT 'Full-time',
  salary              VARCHAR(80),
  deadline            DATETIME,
  is_active           TINYINT NOT NULL DEFAULT 1,
  created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_job_company FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
  INDEX ix_jobs_title_location (title, location)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 5. applications  (N:1 job, N:1 candidate, unique together)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS applications (
  id                 INT AUTO_INCREMENT PRIMARY KEY,
  job_id             INT NOT NULL,
  candidate_id       INT NOT NULL,
  resume_file        VARCHAR(255),
  match_score        FLOAT,
  application_status ENUM('Applied','Under Review','Shortlisted','Interview','Rejected','Selected')
                     NOT NULL DEFAULT 'Applied',
  cover_note         TEXT,
  applied_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at         DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_app_job       FOREIGN KEY (job_id)       REFERENCES jobs(id) ON DELETE CASCADE,
  CONSTRAINT fk_app_candidate FOREIGN KEY (candidate_id) REFERENCES candidate_profiles(id) ON DELETE CASCADE,
  CONSTRAINT uq_job_candidate UNIQUE (job_id, candidate_id)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 6. resume_analysis  (history of every AI screening run)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS resume_analysis (
  id               INT AUTO_INCREMENT PRIMARY KEY,
  candidate_id     INT NOT NULL,
  resume_score     FLOAT NOT NULL,
  extracted_skills TEXT,
  education_score  FLOAT DEFAULT 0,
  experience_score FLOAT DEFAULT 0,
  keyword_score    FLOAT DEFAULT 0,
  skills_score     FLOAT DEFAULT 0,
  suggestions      TEXT,
  raw_text_preview TEXT,
  analyzed_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_analysis_candidate FOREIGN KEY (candidate_id)
    REFERENCES candidate_profiles(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 7. job_recommendations  (cached AI match per candidate/job pair)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS job_recommendations (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  candidate_id    INT NOT NULL,
  job_id          INT NOT NULL,
  match_score     FLOAT NOT NULL,
  matching_skills TEXT,
  missing_skills  TEXT,
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_rec_candidate FOREIGN KEY (candidate_id)
    REFERENCES candidate_profiles(id) ON DELETE CASCADE,
  CONSTRAINT fk_rec_job FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
  CONSTRAINT uq_candidate_job_rec UNIQUE (candidate_id, job_id)
) ENGINE=InnoDB;
