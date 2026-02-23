"""Database operations for the resume generator."""

import sqlite3
from pathlib import Path
from typing import Any, Optional
from datetime import date


def get_db_path() -> Path:
    base = Path(__file__).resolve().parent.parent
    return base / "data" / "resume.db"


def get_schema_path() -> Path:
    base = Path(__file__).resolve().parent.parent
    return base / "schema" / "schema.sql"


def init_db(db_path: Optional[Path] = None) -> Path:
    db_path = db_path or get_db_path()
    schema_path = get_schema_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with open(schema_path) as f:
        schema = f.read()
    conn = sqlite3.connect(db_path)
    conn.executescript(schema)
    conn.commit()
    conn.close()
    return db_path


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    db_path = db_path or get_db_path()
    if not db_path.exists():
        init_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def execute_query(query: str, params: tuple = (), db_path: Optional[Path] = None) -> list:
    conn = get_connection(db_path)
    cur = conn.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def execute_write(query: str, params: tuple = (), db_path: Optional[Path] = None) -> int:
    conn = get_connection(db_path)
    cur = conn.execute(query, params)
    conn.commit()
    row_id = cur.lastrowid or 0
    conn.close()
    return row_id


def clear_all_data(db_path: Optional[Path] = None) -> None:
    conn = get_connection(db_path)
    for table in ["bullets", "work_experience", "projects", "skills", "education", 
                  "certifications", "job_applications", "keyword_frequency", "personal_info"]:
        conn.execute(f"DELETE FROM {table}")
    conn.commit()
    conn.close()


# --- Personal Info ---
def get_personal_info(db_path: Optional[Path] = None) -> Optional[dict]:
    rows = execute_query("SELECT * FROM personal_info LIMIT 1", db_path=db_path)
    return rows[0] if rows else None


def upsert_personal_info(name: str, email: str, phone: str = "", linkedin: str = "",
                         github: str = "", portfolio: str = "", location: str = "",
                         db_path: Optional[Path] = None) -> int:
    conn = get_connection(db_path)
    conn.execute("""INSERT INTO personal_info (id, name, email, phone, linkedin, github, portfolio, location)
                    VALUES (1, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET name=?, email=?, phone=?, linkedin=?, github=?, portfolio=?, location=?""",
                 (name, email, phone, linkedin, github, portfolio, location,
                  name, email, phone, linkedin, github, portfolio, location))
    conn.commit()
    conn.close()
    return 1


# --- Work Experience ---
def get_work_experience(db_path: Optional[Path] = None) -> list:
    return execute_query("SELECT * FROM work_experience ORDER BY display_order, start_date DESC", db_path=db_path)


def add_work_experience(job_title: str, company: str, start_date: str, end_date: str = None,
                        location: str = "", display_order: int = 0, db_path: Optional[Path] = None) -> int:
    return execute_write(
        "INSERT INTO work_experience (job_title, company, start_date, end_date, location, display_order) VALUES (?, ?, ?, ?, ?, ?)",
        (job_title, company, start_date, end_date or "", location, display_order), db_path)


def delete_work_experience(wid: int, db_path: Optional[Path] = None) -> None:
    execute_write("DELETE FROM bullets WHERE work_experience_id = ?", (wid,), db_path)
    execute_write("DELETE FROM work_experience WHERE id = ?", (wid,), db_path)


# --- Bullets ---
def get_all_bullets(db_path: Optional[Path] = None) -> list:
    return execute_query("""SELECT b.*, w.company, w.job_title, p.project_name
                            FROM bullets b
                            LEFT JOIN work_experience w ON b.work_experience_id = w.id
                            LEFT JOIN projects p ON b.project_id = p.id
                            ORDER BY b.display_order""", db_path=db_path)


def get_bullets_for_job(work_id: int, db_path: Optional[Path] = None) -> list:
    return execute_query("SELECT * FROM bullets WHERE work_experience_id = ? ORDER BY display_order", (work_id,), db_path)


def get_bullets_for_project(project_id: int, db_path: Optional[Path] = None) -> list:
    return execute_query("SELECT * FROM bullets WHERE project_id = ? ORDER BY display_order", (project_id,), db_path)


def add_bullet(bullet_text: str, keywords: str = "", work_experience_id: int = None,
               project_id: int = None, display_order: int = 0, db_path: Optional[Path] = None) -> int:
    return execute_write(
        "INSERT INTO bullets (bullet_text, keywords, work_experience_id, project_id, display_order) VALUES (?, ?, ?, ?, ?)",
        (bullet_text, keywords, work_experience_id, project_id, display_order), db_path)


def delete_bullet(bid: int, db_path: Optional[Path] = None) -> None:
    execute_write("DELETE FROM bullets WHERE id = ?", (bid,), db_path)


# --- Skills ---
def get_skills(db_path: Optional[Path] = None) -> list:
    return execute_query("SELECT * FROM skills ORDER BY category, display_order", db_path=db_path)


def add_skill(skill_name: str, category: str = "", proficiency: str = "",
              display_order: int = 0, db_path: Optional[Path] = None) -> int:
    return execute_write(
        "INSERT INTO skills (skill_name, category, proficiency, display_order) VALUES (?, ?, ?, ?)",
        (skill_name, category, proficiency, display_order), db_path)


def delete_skill(sid: int, db_path: Optional[Path] = None) -> None:
    execute_write("DELETE FROM skills WHERE id = ?", (sid,), db_path)


# --- Projects ---
def get_projects(db_path: Optional[Path] = None) -> list:
    return execute_query("SELECT * FROM projects ORDER BY display_order", db_path=db_path)


def add_project(project_name: str, description: str = "", github_url: str = "",
                display_order: int = 0, db_path: Optional[Path] = None) -> int:
    return execute_write(
        "INSERT INTO projects (project_name, description, github_url, display_order) VALUES (?, ?, ?, ?)",
        (project_name, description, github_url, display_order), db_path)


def delete_project(pid: int, db_path: Optional[Path] = None) -> None:
    execute_write("DELETE FROM bullets WHERE project_id = ?", (pid,), db_path)
    execute_write("DELETE FROM projects WHERE id = ?", (pid,), db_path)


# --- Education ---
def get_education(db_path: Optional[Path] = None) -> list:
    return execute_query("SELECT * FROM education ORDER BY display_order, year DESC", db_path=db_path)


def add_education(degree: str, institution: str, field: str = "", location: str = "",
                  gpa: str = "", year: str = "", display_order: int = 0, db_path: Optional[Path] = None) -> int:
    return execute_write(
        "INSERT INTO education (degree, institution, field, location, gpa, year, display_order) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (degree, institution, field, location, gpa, year, display_order), db_path)


def delete_education(eid: int, db_path: Optional[Path] = None) -> None:
    execute_write("DELETE FROM education WHERE id = ?", (eid,), db_path)


# --- Certifications ---
def get_certifications(db_path: Optional[Path] = None) -> list:
    return execute_query("SELECT * FROM certifications ORDER BY display_order, issued DESC", db_path=db_path)


def add_certification(name: str, issuer: str, issued: str = "", expires: str = "",
                      credential_id: str = "", display_order: int = 0, db_path: Optional[Path] = None) -> int:
    return execute_write(
        "INSERT INTO certifications (name, issuer, issued, expires, credential_id, display_order) VALUES (?, ?, ?, ?, ?, ?)",
        (name, issuer, issued, expires, credential_id, display_order), db_path)


def delete_certification(cid: int, db_path: Optional[Path] = None) -> None:
    execute_write("DELETE FROM certifications WHERE id = ?", (cid,), db_path)


# --- Job Applications ---
def get_job_applications(db_path: Optional[Path] = None, applied_only: bool = False) -> list:
    if applied_only:
        return execute_query("SELECT * FROM job_applications WHERE applied = 1 ORDER BY date_applied DESC", db_path=db_path)
    return execute_query("SELECT * FROM job_applications ORDER BY date_applied DESC", db_path=db_path)


def get_draft_applications(db_path: Optional[Path] = None) -> list:
    return execute_query("SELECT * FROM job_applications WHERE applied = 0 ORDER BY date_applied DESC", db_path=db_path)


def add_job_application(company: str, job_title: str, job_description: str = "",
                        resume_file: str = "", ats_score: float = None, role_type: str = "",
                        bullets_used: str = "", outcome: str = "Generated", 
                        db_path: Optional[Path] = None) -> int:
    return execute_write(
        """INSERT INTO job_applications (company, job_title, job_description, jd_text, resume_file, 
           generated_resume_path, ats_score, role_type, bullets_used, outcome, applied) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)""",
        (company, job_title, job_description, job_description, resume_file, resume_file, 
         ats_score, role_type, bullets_used, outcome), db_path)


def update_job_application_outcome(app_id: int, outcome: str, db_path: Optional[Path] = None) -> None:
    execute_write("UPDATE job_applications SET outcome = ? WHERE id = ?", (outcome, app_id), db_path)


def mark_application_applied(app_id: int, applied: bool = True, db_path: Optional[Path] = None) -> None:
    execute_write("UPDATE job_applications SET applied = ?, outcome = ? WHERE id = ?", 
                  (1 if applied else 0, "Applied" if applied else "Generated", app_id), db_path)


def delete_job_application(app_id: int, db_path: Optional[Path] = None) -> None:
    execute_write("DELETE FROM job_applications WHERE id = ?", (app_id,), db_path)


def get_application_by_id(app_id: int, db_path: Optional[Path] = None) -> dict:
    rows = execute_query("SELECT * FROM job_applications WHERE id = ?", (app_id,), db_path)
    return rows[0] if rows else None


# --- Keyword Frequency ---
def get_keyword_frequencies(db_path: Optional[Path] = None) -> list:
    return execute_query("SELECT * FROM keyword_frequency ORDER BY jd_count DESC", db_path=db_path)


def get_total_jds_count(db_path: Optional[Path] = None) -> int:
    rows = execute_query("SELECT COUNT(*) as cnt FROM job_applications WHERE applied = 1", db_path=db_path)
    return rows[0]["cnt"] if rows else 0


def update_keyword_frequencies(keywords: list, db_path: Optional[Path] = None) -> None:
    conn = get_connection(db_path)
    today = date.today().isoformat()
    for kw in keywords:
        kw_lower = kw.lower().strip()
        if len(kw_lower) < 2:
            continue
        conn.execute("""INSERT INTO keyword_frequency (keyword, jd_count, last_seen, first_seen) VALUES (?, 1, ?, ?)
                        ON CONFLICT(keyword) DO UPDATE SET jd_count = jd_count + 1, last_seen = ?""",
                     (kw_lower, today, today, today))
    conn.commit()
    conn.close()


def get_top_keywords(limit: int = 20, db_path: Optional[Path] = None) -> list:
    return execute_query(f"SELECT keyword, jd_count, last_seen, first_seen FROM keyword_frequency ORDER BY jd_count DESC LIMIT {limit}", db_path=db_path)


def get_recent_keywords(days: int = 7, db_path: Optional[Path] = None) -> list:
    return execute_query(
        f"SELECT keyword, jd_count, first_seen FROM keyword_frequency WHERE first_seen >= date('now', '-{days} days') ORDER BY jd_count DESC",
        db_path=db_path)


def get_old_keywords(days: int = 30, db_path: Optional[Path] = None) -> list:
    return execute_query(
        f"SELECT keyword, jd_count FROM keyword_frequency WHERE first_seen < date('now', '-{days} days') ORDER BY jd_count DESC LIMIT 20",
        db_path=db_path)


# --- Role Keyword Weights ---
def update_role_keyword_weights(role_type: str, keywords: list, db_path: Optional[Path] = None) -> None:
    conn = get_connection(db_path)
    for kw in keywords:
        kw_lower = kw.lower().strip()
        if len(kw_lower) < 2:
            continue
        conn.execute("""INSERT INTO role_keyword_weights (role_type, keyword, weight, jd_count) VALUES (?, ?, 1.0, 1)
                        ON CONFLICT(role_type, keyword) DO UPDATE SET jd_count = jd_count + 1""",
                     (role_type, kw_lower))
    conn.commit()
    conn.close()


def get_role_keyword_weights(role_type: str, db_path: Optional[Path] = None) -> list:
    return execute_query(
        "SELECT keyword, jd_count, weight FROM role_keyword_weights WHERE role_type = ? ORDER BY jd_count DESC",
        (role_type,), db_path)


# --- Bullet Performance ---
def get_bullet_performance(bullet_id: int, db_path: Optional[Path] = None) -> dict:
    rows = execute_query("SELECT * FROM bullet_performance WHERE bullet_id = ?", (bullet_id,), db_path)
    return rows[0] if rows else None


def update_bullet_selection(bullet_ids: list, ats_score: float, db_path: Optional[Path] = None) -> None:
    conn = get_connection(db_path)
    is_high_ats = 1 if ats_score >= 75 else 0
    for bid in bullet_ids:
        conn.execute("""INSERT INTO bullet_performance (bullet_id, times_selected, times_in_high_ats_resume, avg_ats_score)
                        VALUES (?, 1, ?, ?)
                        ON CONFLICT(bullet_id) DO UPDATE SET 
                            times_selected = times_selected + 1,
                            times_in_high_ats_resume = times_in_high_ats_resume + ?,
                            avg_ats_score = (avg_ats_score * times_selected + ?) / (times_selected + 1)""",
                     (bid, is_high_ats, ats_score, is_high_ats, ats_score))
    conn.commit()
    conn.close()


def boost_bullets_for_outcome(app_id: int, outcome: str, db_path: Optional[Path] = None) -> None:
    app = get_application_by_id(app_id, db_path)
    if not app or not app.get("bullets_used"):
        return
    
    bullet_ids = [int(x) for x in app["bullets_used"].split(",") if x.strip().isdigit()]
    if not bullet_ids:
        return
    
    conn = get_connection(db_path)
    col = "times_in_interview" if outcome == "Interview" else "times_in_offer"
    for bid in bullet_ids:
        conn.execute(f"""INSERT INTO bullet_performance (bullet_id, {col})
                         VALUES (?, 1)
                         ON CONFLICT(bullet_id) DO UPDATE SET {col} = {col} + 1""",
                     (bid,))
    conn.commit()
    conn.close()


def get_all_bullet_performance(db_path: Optional[Path] = None) -> list:
    return execute_query("""SELECT bp.*, b.bullet_text 
                            FROM bullet_performance bp 
                            JOIN bullets b ON bp.bullet_id = b.id 
                            ORDER BY bp.times_in_offer DESC, bp.times_in_interview DESC, bp.times_in_high_ats_resume DESC""",
                         db_path=db_path)
