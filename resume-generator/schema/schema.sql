-- Resume Generator Database Schema

CREATE TABLE IF NOT EXISTS personal_info (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    linkedin TEXT,
    github TEXT,
    portfolio TEXT,
    location TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS work_experience (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    start_date TEXT NOT NULL,
    end_date TEXT,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,
    description TEXT,
    github_url TEXT,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bullets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bullet_text TEXT NOT NULL,
    keywords TEXT,
    work_experience_id INTEGER,
    project_id INTEGER,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (work_experience_id) REFERENCES work_experience(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL,
    category TEXT,
    proficiency TEXT,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS education (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    degree TEXT NOT NULL,
    field TEXT,
    institution TEXT NOT NULL,
    location TEXT,
    gpa TEXT,
    year TEXT,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS certifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    issuer TEXT NOT NULL,
    issued TEXT,
    expires TEXT,
    credential_id TEXT,
    year TEXT,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS job_applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    job_title TEXT NOT NULL,
    job_description TEXT,
    jd_text TEXT,
    resume_file TEXT,
    generated_resume_path TEXT,
    ats_score REAL,
    role_type TEXT,
    applied INTEGER DEFAULT 0,
    bullets_used TEXT,
    date_applied DATE DEFAULT CURRENT_DATE,
    outcome TEXT DEFAULT 'Generated',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS keyword_frequency (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT UNIQUE NOT NULL,
    jd_count INTEGER DEFAULT 1,
    last_seen DATE DEFAULT CURRENT_DATE,
    first_seen DATE DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS role_keyword_weights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_type TEXT NOT NULL,
    keyword TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    jd_count INTEGER DEFAULT 1,
    UNIQUE(role_type, keyword)
);

CREATE TABLE IF NOT EXISTS bullet_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bullet_id INTEGER UNIQUE,
    times_selected INTEGER DEFAULT 0,
    times_in_high_ats_resume INTEGER DEFAULT 0,
    times_in_interview INTEGER DEFAULT 0,
    times_in_offer INTEGER DEFAULT 0,
    avg_ats_score REAL DEFAULT 0,
    FOREIGN KEY (bullet_id) REFERENCES bullets(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_bullets_work ON bullets(work_experience_id);
CREATE INDEX IF NOT EXISTS idx_bullets_project ON bullets(project_id);
CREATE INDEX IF NOT EXISTS idx_keyword_freq ON keyword_frequency(keyword);
CREATE INDEX IF NOT EXISTS idx_role_kw ON role_keyword_weights(role_type, keyword);
CREATE INDEX IF NOT EXISTS idx_bullet_perf ON bullet_performance(bullet_id);
