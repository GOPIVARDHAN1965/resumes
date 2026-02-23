"""
Generate .docx and HTML resumes.
Uses enhanced scoring with TF-IDF, role-specific weights, and bullet performance tracking.
"""

import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from .db import (
    get_db_path, get_keyword_frequencies, update_keyword_frequencies,
    get_total_jds_count, update_role_keyword_weights, get_role_keyword_weights,
    update_bullet_selection, get_all_bullet_performance
)
from .scoring import (
    extract_keywords, select_top_bullets, filter_skills_by_relevance,
    calculate_ats_score, get_section_scores, classify_role,
    compute_tfidf_weights
)


def _get_base_path() -> Path:
    return Path(__file__).resolve().parent.parent


def _get_template_js() -> Path:
    return _get_base_path() / "resume_template.js"


def _get_output_dir() -> Path:
    return _get_base_path() / "outputs"


def get_output_dir() -> Path:
    return _get_output_dir()


def _check_node_available() -> None:
    node = shutil.which("node")
    if not node:
        raise RuntimeError(
            "Node.js is not installed or not in PATH. "
            "Install Node.js from https://nodejs.org and ensure 'node' is available."
        )
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            raise RuntimeError("Node.js is not working. Run 'node --version' to verify.")
    except FileNotFoundError:
        raise RuntimeError("Node.js not found. Install from https://nodejs.org.")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Node.js check timed out.")


def _fetch_all_data(db_path: Optional[Path] = None) -> dict:
    import sqlite3

    db_path = db_path or get_db_path()
    if not db_path.exists():
        raise ValueError("Database not initialized. Run: python main.py init")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM personal_info LIMIT 1")
    row = cur.fetchone()
    personal = {}
    if row:
        r = dict(row)
        personal = {
            "name": r.get("name", ""),
            "email": r.get("email", ""),
            "phone": r.get("phone") or "",
            "location": r.get("location") or "",
            "linkedin": r.get("linkedin") or "",
            "github": r.get("github") or "",
            "portfolio": r.get("portfolio") or "",
        }

    cur.execute("SELECT * FROM education ORDER BY display_order, year DESC")
    education = []
    for r in cur.fetchall():
        d = dict(r)
        education.append({
            "degree": d.get("degree", ""),
            "field": d.get("field") or "",
            "institution": d.get("institution", ""),
            "location": d.get("location") or "",
            "gpa": d.get("gpa") or "",
            "end_date": d.get("year") or "",
        })

    cur.execute("SELECT * FROM certifications ORDER BY display_order, issued DESC")
    certifications = []
    for r in cur.fetchall():
        d = dict(r)
        certifications.append({
            "name": d.get("name", ""),
            "issuer": d.get("issuer", ""),
            "credential_id": d.get("credential_id") or "",
            "issued": d.get("issued") or d.get("year") or "",
            "expires": d.get("expires") or "",
        })

    cur.execute("SELECT * FROM work_experience ORDER BY display_order, start_date DESC")
    jobs = []
    for job in cur.fetchall():
        j = dict(job)
        cur.execute(
            "SELECT id, bullet_text, keywords FROM bullets WHERE work_experience_id = ? ORDER BY display_order, id",
            (j["id"],),
        )
        bullets = [{"id": dict(b)["id"], "text": dict(b)["bullet_text"], "keywords": dict(b).get("keywords") or ""} 
                   for b in cur.fetchall()]
        jobs.append({
            "title": j["job_title"],
            "company": j["company"],
            "location": j.get("location") or "",
            "start_date": j["start_date"],
            "end_date": j.get("end_date") or "",
            "bullets": bullets,
        })

    cur.execute("SELECT * FROM projects ORDER BY display_order, id")
    projects = []
    for proj in cur.fetchall():
        p = dict(proj)
        cur.execute(
            "SELECT id, bullet_text, keywords FROM bullets WHERE project_id = ? ORDER BY display_order, id",
            (p["id"],),
        )
        bullets = [{"id": dict(b)["id"], "text": dict(b)["bullet_text"], "keywords": dict(b).get("keywords") or ""} 
                   for b in cur.fetchall()]
        projects.append({
            "id": p["id"],
            "name": p["project_name"],
            "github_url": p.get("github_url") or p.get("description") or "",
            "bullets": bullets,
        })

    cur.execute("SELECT * FROM skills ORDER BY category, display_order")
    skills = [{"name": dict(r)["skill_name"], "category": dict(r).get("category") or "",
               "proficiency": dict(r).get("proficiency") or ""} for r in cur.fetchall()]

    conn.close()
    return {
        "personal": personal,
        "experience": jobs,
        "projects": projects,
        "skills": skills,
        "certifications": certifications,
        "education": education,
    }


PRIORITY_BOLD = [
    "Azure Blob Storage", "Azure", "Power BI", "Power Query", "Power Automate",
    "Python", "SQL", "DAX", "MySQL", "ETL",
    "FLAIR", "FOCUS", "HMGP", "FEMA", "ARIMA", "Prophet",
    "Flask", "MongoDB", "Selenium", "Scikit-learn", "LangChain",
    "Snowflake", "PostgreSQL", "SQL Server", "Spark", "Airflow",
    "Databricks", "GCP", "AWS", "Docker", "REST API", "FastAPI",
]

NEVER_BOLD = frozenset([
    "SHA-256", "KPIs", "SLA", "CSRF", ".NET", "VBA", "Git", "GitHub",
    "SharePoint", "OneDrive", "Windows Task Scheduler", "Excel", "JSON", "CSV", "XML",
])

SKIP_LEADERSHIP_STARTS = (
    "Collaborated", "Onboarded", "Trained", "Presented", "Authored",
    "Led a", "Worked with", "Partnered",
)


def _bold_technical_terms_html(text: str, matched_keywords: list, max_bolds: int = 2) -> str:
    """
    Wrap priority technical terms in <strong>. Same rules as DOCX:
    - PRIORITY_BOLD only, max 2 per bullet
    - First half of bullet only
    - Never bold NEVER_BOLD terms
    - Skip bullets starting with leadership phrases
    """
    if not text:
        return ""
    text_trimmed = text.strip()
    for prefix in SKIP_LEADERSHIP_STARTS:
        if text_trimmed.startswith(prefix):
            return text

    terms_to_check = [
        t for t in PRIORITY_BOLD
        if t not in NEVER_BOLD
        and (not matched_keywords or any(
            kw.lower() in t.lower() or t.lower() in kw.lower()
            for kw in matched_keywords
        ))
    ]
    terms_to_check.sort(key=len, reverse=True)

    midpoint = len(text) // 2
    text_lower = text.lower()
    candidates = []
    for term in terms_to_check:
        idx = text_lower.find(term.lower())
        if idx >= 0 and idx < midpoint:
            candidates.append((idx, term))
    candidates.sort(key=lambda x: x[0])
    to_bold = [term for _, term in candidates[:max_bolds]]

    result = text
    offset = 0
    for term in to_bold:
        idx = result.lower().find(term.lower())
        if idx >= 0:
            before = result[:idx]
            match = result[idx : idx + len(term)]
            after = result[idx + len(term) :]
            result = before + "<strong>" + match + "</strong>" + after
    return result


def _format_date(date_str: str) -> str:
    if not date_str:
        return "Present"
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    parts = date_str.split("-")
    if len(parts) >= 2:
        year = parts[0]
        month_idx = int(parts[1]) - 1
        if 0 <= month_idx < 12:
            return f"{months[month_idx]} {year}"
    return date_str


def generate_resume_html(data: dict, output_path: Path) -> str:
    """Generate HTML version of the resume."""
    personal = data.get("personal", {})
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{personal.get("name", "Resume")}</title>
    <style>
        @media print {{
            body {{ margin: 0; padding: 0.5in; }}
            .page-break {{ page-break-before: always; }}
        }}
        body {{
            font-family: Calibri, Arial, sans-serif;
            font-size: 10pt;
            line-height: 1.4;
            max-width: 8.5in;
            margin: 0 auto;
            padding: 0.5in;
            color: #333;
        }}
        .header {{
            text-align: center;
            margin-bottom: 12px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 18pt;
            font-weight: bold;
        }}
        .contact {{
            font-size: 10pt;
            margin: 4px 0;
        }}
        .contact a {{
            color: #0066cc;
            text-decoration: none;
        }}
        .section {{
            margin-top: 16px;
        }}
        .section-title {{
            font-size: 12pt;
            font-weight: bold;
            text-transform: uppercase;
            border-bottom: 1px solid #333;
            padding-bottom: 2px;
            margin-bottom: 8px;
        }}
        .job-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 4px;
        }}
        .job-title {{
            font-weight: bold;
        }}
        .job-date {{
            font-style: normal;
        }}
        .job-location {{
            font-style: italic;
            font-size: 9pt;
            margin-bottom: 4px;
        }}
        ul {{
            margin: 4px 0 8px 20px;
            padding: 0;
        }}
        li {{
            margin-bottom: 4px;
        }}
        .skills-row {{
            margin-bottom: 4px;
        }}
        .skills-category {{
            font-weight: bold;
        }}
        .project-title {{
            font-weight: bold;
        }}
        .project-link {{
            color: #0066cc;
            text-decoration: none;
            font-size: 9pt;
        }}
        .cert-item, .edu-item {{
            margin-bottom: 6px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{personal.get("name", "")}</h1>
        <div class="contact">
            {" | ".join(filter(None, [personal.get("location"), personal.get("phone"), personal.get("email")]))}
        </div>
        <div class="contact">
            {" | ".join(filter(None, [
                f'<a href="https://{personal.get("linkedin")}">{personal.get("linkedin")}</a>' if personal.get("linkedin") else "",
                f'<a href="https://{personal.get("github")}">{personal.get("github")}</a>' if personal.get("github") else "",
                f'<a href="https://{personal.get("portfolio")}">{personal.get("portfolio")}</a>' if personal.get("portfolio") else ""
            ]))}
        </div>
    </div>
'''
    
    if data.get("is_cv") and data.get("summary"):
        html += '    <div class="section">\n        <div class="section-title">Professional Summary</div>\n'
        html += f'        <p style="margin: 0 0 8px 0;">{data["summary"]}</p>\n    </div>\n'

    if data.get("experience"):
        html += '    <div class="section">\n        <div class="section-title">Professional Experience</div>\n'
        for job in data["experience"]:
            start = _format_date(job.get("start_date", ""))
            end = _format_date(job.get("end_date", ""))
            html += f'''        <div class="job-header">
            <span class="job-title">{job.get("company", "")}, {job.get("title", "")}</span>
            <span class="job-date">{start} – {end}</span>
        </div>\n'''
            if job.get("location"):
                html += f'        <div class="job-location">{job.get("location")}</div>\n'
            if job.get("bullets"):
                html += '        <ul>\n'
                for b in job["bullets"]:
                    text = b.get("text", "") if isinstance(b, dict) else b
                    mk = b.get("matched_keywords", []) if isinstance(b, dict) else []
                    html += f'            <li>{_bold_technical_terms_html(text, mk)}</li>\n'
                html += '        </ul>\n'
        html += '    </div>\n'
    
    if data.get("projects"):
        html += '    <div class="section">\n        <div class="section-title">Projects</div>\n'
        projects_to_show = data["projects"] if data.get("is_cv") else data["projects"][:3]
        for proj in projects_to_show:
            github = proj.get("github_url", "")
            link_html = f' — <a class="project-link" href="{github}">GitHub</a>' if github.startswith("http") else ""
            html += f'        <div class="project-title">{proj.get("name", "")}{link_html}</div>\n'
            if proj.get("bullets"):
                html += '        <ul>\n'
                for b in proj["bullets"]:
                    text = b.get("text", "") if isinstance(b, dict) else b
                    mk = b.get("matched_keywords", []) if isinstance(b, dict) else []
                    html += f'            <li>{_bold_technical_terms_html(text, mk)}</li>\n'
                html += '        </ul>\n'
        html += '    </div>\n'
    
    if data.get("skills"):
        html += '    <div class="section">\n        <div class="section-title">Technical Skills</div>\n'
        by_cat = {}
        for s in data["skills"]:
            cat = s.get("category") or "Other"
            by_cat.setdefault(cat, []).append(s["name"])
        for cat, names in by_cat.items():
            html += f'        <div class="skills-row"><span class="skills-category">{cat}:</span> {", ".join(names)}</div>\n'
        html += '    </div>\n'
    
    if data.get("certifications"):
        html += '    <div class="section">\n        <div class="section-title">Certifications</div>\n'
        for cert in data["certifications"]:
            parts = [cert.get("name", "")]
            if cert.get("issuer"):
                parts.append(cert["issuer"])
            if cert.get("issued"):
                parts.append(_format_date(cert["issued"]))
            html += f'        <div class="cert-item">{" — ".join(parts)}</div>\n'
        html += '    </div>\n'
    
    if data.get("education"):
        html += '    <div class="section">\n        <div class="section-title">Education</div>\n'
        for edu in data["education"]:
            degree = f'{edu.get("degree", "")} in {edu.get("field", "")}' if edu.get("field") else edu.get("degree", "")
            date_gpa = []
            if edu.get("end_date"):
                date_gpa.append(_format_date(edu["end_date"]))
            if edu.get("gpa"):
                date_gpa.append(f'GPA: {edu["gpa"]}')
            html += f'        <div class="edu-item"><strong>{degree}</strong> | {" | ".join(date_gpa)}<br><em>{edu.get("institution", "")}</em></div>\n'
        html += '    </div>\n'
    
    html += '</body>\n</html>'
    
    output_path.write_text(html, encoding="utf-8")
    return str(output_path)


def generate_resume(
    job_description: str = "",
    top_n: int = 5,
    output_filename: Optional[str] = None,
    db_path: Optional[Path] = None,
    track_keywords: bool = True,
) -> dict:
    """
    Generate resume .docx and HTML via Node.js.
    Uses TF-IDF weighting, role-specific scoring, and bullet performance tracking.
    """
    _check_node_available()
    template_js = _get_template_js()
    if not template_js.exists():
        raise FileNotFoundError(
            f"resume_template.js not found at {template_js}. "
            "Ensure it exists in the project root."
        )

    out_dir = _get_output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if output_filename is None:
        output_filename = f"resume_{timestamp}.docx"
    if not output_filename.endswith(".docx"):
        output_filename += ".docx"
    output_path = out_dir / output_filename
    html_path = out_dir / output_filename.replace(".docx", ".html")

    data = _fetch_all_data(db_path)
    if not data.get("personal") or not data["personal"].get("name"):
        raise ValueError("No personal info in database. Add personal info first.")

    jd_keywords = extract_keywords(job_description) if job_description.strip() else {
        "unigrams": set(), "bigrams": set(), "trigrams": set(), "all": set()
    }
    
    role_type = classify_role(job_description) if job_description.strip() else "Other"
    
    tfidf_weights = None
    role_weights = None
    perf_map = None
    
    if track_keywords and job_description.strip():
        freqs = get_keyword_frequencies(db_path)
        freq_map = {f["keyword"]: f["jd_count"] for f in freqs}
        total_jds = get_total_jds_count(db_path) or 1
        tfidf_weights = compute_tfidf_weights(freq_map, total_jds)
        
        update_keyword_frequencies(list(jd_keywords["unigrams"]), db_path)
        update_role_keyword_weights(role_type, list(jd_keywords["unigrams"]), db_path)
        
        role_kw = get_role_keyword_weights(role_type, db_path)
        role_weights = {r["keyword"]: r["jd_count"] for r in role_kw}
        
        perf_data = get_all_bullet_performance(db_path)
        perf_map = {p["bullet_id"]: p for p in perf_data}

    all_matched = set()
    selected_bullets_info = []
    all_bullet_ids = []

    if jd_keywords["all"]:
        data["experience"], exp_ids = select_top_bullets(
            data["experience"], jd_keywords, top_n, tfidf_weights, role_weights, perf_map
        )
        all_bullet_ids.extend(exp_ids)
        
        data["projects"], proj_ids = select_top_bullets(
            data["projects"], jd_keywords, top_n=3, tfidf_weights=tfidf_weights, 
            role_weights=role_weights, perf_map=perf_map
        )
        all_bullet_ids.extend(proj_ids)
        
        data["projects"] = data["projects"][:3]
        
        data["skills"] = filter_skills_by_relevance(data["skills"], jd_keywords)
        
        for job in data["experience"]:
            for info in job.get("selected_scores", []):
                all_matched.update(info[2])
                selected_bullets_info.append(info)
        for proj in data["projects"]:
            for info in proj.get("selected_scores", []):
                all_matched.update(info[2])
        
        for skill in data["skills"]:
            skill_lower = skill["name"].lower()
            if skill_lower in jd_keywords["all"]:
                all_matched.add(skill_lower)
    else:
        for job in data["experience"]:
            job["bullets"] = job.get("bullets", [])[:top_n]
        data["projects"] = data["projects"][:3]
        for proj in data["projects"]:
            proj["bullets"] = proj.get("bullets", [])[:3]

    ats_result = calculate_ats_score(jd_keywords, data)

    if track_keywords and all_bullet_ids:
        update_bullet_selection(all_bullet_ids, ats_result["score"], db_path)
    
    skills_matched = sum(1 for s in data["skills"] if s["name"].lower() in all_matched)
    section_scores = get_section_scores(
        selected_bullets_info[:10] if selected_bullets_info else [],
        [],
        skills_matched,
        len(data["skills"])
    )

    for job in data["experience"]:
        scores = job.get("selected_scores", [])
        for i, b in enumerate(job.get("bullets", [])):
            if isinstance(b, dict) and i < len(scores):
                b["matched_keywords"] = scores[i][2] if len(scores[i]) > 2 else []
        job.pop("selected_scores", None)
    for proj in data["projects"]:
        scores = proj.get("selected_scores", [])
        for i, b in enumerate(proj.get("bullets", [])):
            if isinstance(b, dict) and i < len(scores):
                b["matched_keywords"] = scores[i][2] if len(scores[i]) > 2 else []
        proj.pop("selected_scores", None)
        proj.pop("id", None)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as tmp:
        json.dump(data, tmp, ensure_ascii=False, indent=2)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            ["node", str(template_js), tmp_path, str(output_path)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(_get_base_path()),
        )
        if result.returncode != 0:
            raise RuntimeError(f"resume_template.js failed:\n{result.stderr or result.stdout}")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    generate_resume_html(data, html_path)

    return {
        "path": str(output_path),
        "html_path": str(html_path),
        "ats_score": ats_result["score"],
        "matched_keywords": ats_result["matched"],
        "missing_keywords": ats_result["missing"],
        "section_scores": section_scores,
        "top_bullets": selected_bullets_info[:5],
        "role_type": role_type,
        "bullets_used": ",".join(str(bid) for bid in all_bullet_ids),
    }


def build_resume(
    job_description: str,
    bullets_per_job: int = 3,
    output_filename: Optional[str] = None,
    db_path=None,
) -> Path:
    """Alias for generate_resume for backwards compatibility."""
    result = generate_resume(
        job_description=job_description,
        top_n=bullets_per_job,
        output_filename=output_filename,
        db_path=db_path,
    )
    return Path(result["path"])


def _generate_cover_letter_html(data: dict, output_path: Path) -> str:
    personal = data["personal"]
    content = data["content"].replace("\n\n", "</p><p>").replace("\n", "<br>")
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: Calibri, Arial, sans-serif; font-size: 11pt;
         max-width: 7.5in; margin: 1in auto; color: #222; line-height: 1.6; }}
  .header {{ text-align: center; margin-bottom: 30px; }}
  .header h1 {{ margin: 0; font-size: 16pt; }}
  .header p {{ margin: 4px 0; font-size: 10pt; }}
  p {{ margin: 0 0 14px 0; }}
  @media print {{ body {{ margin: 0.75in; }} }}
</style>
</head>
<body>
  <div class="header">
    <h1>{personal.get("name", "")}</h1>
    <p>{personal.get("location", "")} | {personal.get("phone", "")} | {personal.get("email", "")}</p>
  </div>
  <p>{data.get("date", "")}</p>
  <p>{content}</p>
</body>
</html>"""
    output_path.write_text(html, encoding="utf-8")
    return str(output_path)


def generate_cover_letter(
    job_description: str,
    company_name: str,
    job_title: str,
    hiring_manager: str = "Hiring Manager",
    db_path: Optional[Path] = None,
) -> dict:
    """Generate cover letter DOCX and HTML from template. No AI, no API."""
    _check_node_available()
    from datetime import date

    data = _fetch_all_data(db_path)
    personal = data["personal"]
    if not personal or not personal.get("name"):
        raise ValueError("No personal info in database. Add personal info first.")

    current_job = data["experience"][0] if data["experience"] else {}
    jd_keywords = extract_keywords(job_description)
    scored_experience, _ = select_top_bullets(
        data["experience"], jd_keywords, top_n=2
    )

    top_bullets = []
    for job in scored_experience[:1]:
        for b in job.get("bullets", [])[:2]:
            top_bullets.append(b.get("text", "") if isinstance(b, dict) else b)

    jd_text = job_description.lower()
    matching_skills = [
        s["name"] for s in data["skills"]
        if s["name"].lower() in jd_text
    ][:3]
    skills_str = ", ".join(matching_skills) if matching_skills else "data engineering, Python, and SQL"

    today = date.today().strftime("%B %d, %Y")

    bullet1 = top_bullets[0] if len(top_bullets) > 0 else ""
    bullet2 = top_bullets[1] if len(top_bullets) > 1 else ""

    bullet1_trim = (bullet1[:200] + "...") if len(bullet1) > 200 else bullet1
    bullet2_trim = (bullet2[:200] + "...") if len(bullet2) > 200 else bullet2

    body = f"""Dear {hiring_manager},

I am applying for the {job_title} role at {company_name}. With a Master's in Data Science from Florida State University and hands-on experience building production data systems for Florida's Division of Emergency Management, I bring the technical depth and domain expertise this role requires.

In my current role, I {bullet1_trim} Additionally, {bullet2_trim}

My core technical stack — {skills_str} — maps directly to what {company_name} is looking for. I have built and owned these systems end to end in a high-stakes government environment with no dedicated support team, which means I know how to deliver reliably under pressure.

I would welcome the opportunity to discuss how my experience translates to this role. Thank you for your consideration.

Sincerely,
{personal["name"]}
{personal["email"]} | {personal["phone"]}"""

    cover_letter_data = {
        "personal": personal,
        "content": body,
        "company": company_name,
        "jobTitle": job_title,
        "hiringManager": hiring_manager,
        "date": today,
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_company = "".join(c if c.isalnum() or c == "_" else "_" for c in company_name).strip("_").lower()[:30]
    docx_filename = f"cover_letter_{safe_company}_{timestamp}.docx"
    html_filename = f"cover_letter_{safe_company}_{timestamp}.html"

    out_dir = _get_output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    docx_path = out_dir / docx_filename
    html_path = out_dir / html_filename

    template_js = _get_template_js()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as tmp:
        json.dump(cover_letter_data, tmp, ensure_ascii=False)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            ["node", str(template_js), "--type", "coverletter", tmp_path, str(docx_path)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(_get_base_path()),
        )
        if result.returncode != 0:
            raise RuntimeError(f"Cover letter DOCX failed: {result.stderr or result.stdout}")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    _generate_cover_letter_html(cover_letter_data, html_path)

    return {
        "path": str(docx_path),
        "html_path": str(html_path),
        "content": body,
    }


def generate_cv(db_path: Optional[Path] = None, output_filename: Optional[str] = None) -> dict:
    """Generate full CV with ALL bullets, projects, skills. No filtering."""
    _check_node_available()
    data = _fetch_all_data(db_path)
    if not data.get("personal") or not data["personal"].get("name"):
        raise ValueError("No personal info in database. Add personal info first.")

    current = data["experience"][0] if data["experience"] else {}
    all_skills_str = ", ".join(s["name"] for s in data["skills"][:8])

    summary = (
        f"{data['personal']['name']} is a Data Analyst and Data Engineer with experience "
        f"in federal grant management, financial data systems, and enterprise reporting. "
        f"Currently at {current.get('company', '')}, managing data operations across 150+ "
        f"federal grants using Python, Azure Blob Storage, SQL, and Power BI. "
        f"Holds an MS in Data Science from Florida State University (GPA 3.93) and "
        f"certifications in AWS and Florida Contract Management."
    )

    data["summary"] = summary
    data["is_cv"] = True

    out_dir = _get_output_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = output_filename or f"cv_{timestamp}.docx"
    output_path = out_dir / filename
    html_path = out_dir / filename.replace(".docx", ".html")

    template_js = _get_template_js()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as tmp:
        json.dump(data, tmp, ensure_ascii=False, indent=2)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            ["node", str(template_js), "--type", "cv", tmp_path, str(output_path)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(_get_base_path()),
        )
        if result.returncode != 0:
            raise RuntimeError(f"CV generation failed: {result.stderr or result.stdout}")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    generate_resume_html(data, html_path)

    return {
        "path": str(output_path),
        "html_path": str(html_path),
    }
