"""
Resume Generator Streamlit App
- Horizontal tab navigation
- ATS score panel with colored progress bar
- Clean white UI
- JD Insights page with emerging skills
- Bullet performance tracking
- HTML preview
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime
from collections import Counter

src_path = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(src_path.parent))

from src import db
from src.generator import generate_resume, generate_cover_letter, generate_cv, get_output_dir
from src.scoring import extract_keywords, detect_emerging_keywords

if not hasattr(st, "rerun"):
    st.rerun = getattr(st, "experimental_rerun", lambda: None)

ST_VERSION = tuple(int(x) for x in st.__version__.split(".")[:2])
HAS_TABS = ST_VERSION >= (1, 11)

st.set_page_config(
    page_title="Resume Generator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    .main .block-container { padding-top: 1rem; max-width: 1200px; }
    .status-generated { background-color: #94a3b8; color: white; padding: 2px 8px; border-radius: 4px; }
    .status-applied { background-color: #3b82f6; color: white; padding: 2px 8px; border-radius: 4px; }
    .status-interview { background-color: #eab308; color: white; padding: 2px 8px; border-radius: 4px; }
    .status-offer { background-color: #22c55e; color: white; padding: 2px 8px; border-radius: 4px; }
    .status-rejected { background-color: #6b7280; color: white; padding: 2px 8px; border-radius: 4px; }
    .keyword-matched { 
        background-color: #dcfce7; color: #166534; 
        padding: 2px 8px; border-radius: 12px; margin: 2px; display: inline-block;
    }
    .keyword-missing { 
        background-color: #fee2e2; color: #991b1b; 
        padding: 2px 8px; border-radius: 12px; margin: 2px; display: inline-block;
    }
    .keyword-emerging {
        background-color: #fef3c7; color: #92400e;
        padding: 2px 8px; border-radius: 12px; margin: 2px; display: inline-block;
    }
    .ats-score-container { 
        padding: 20px; background-color: #f8fafc; border-radius: 8px; margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


def page_generator():
    st.header("Generate")
    tab1, tab2, tab3 = st.tabs(["📄 Resume", "✉️ Cover Letter", "📋 CV"])

    with tab1:
        _tab_resume()
    with tab2:
        _tab_cover_letter()
    with tab3:
        _tab_cv()


def _tab_resume():
    st.subheader("Resume Generator")
    col1, col2 = st.columns([3, 1])
    with col1:
        jd_text = st.text_area(
            "Paste Job Description",
            height=200,
            placeholder="Paste the full job description here...",
            key="jd_input"
        )
    with col2:
        st.markdown("**Job Details** (for tracking)")
        company_name = st.text_input("Company", key="track_company")
        job_title = st.text_input("Job Title", key="track_title")
        st.markdown("---")
        bullets_per_job = st.number_input("Bullets per job", 3, 10, 5)
    
    if st.button("🚀 Generate Resume"):
        if not jd_text.strip():
            st.warning("Please paste a job description.")
            return
        
        if not company_name.strip() or not job_title.strip():
            st.warning("Please enter company name and job title for tracking.")
            return
        
        try:
            with st.spinner("Generating resume..."):
                result = generate_resume(
                    job_description=jd_text,
                    top_n=bullets_per_job,
                )
            
            st.session_state["last_result"] = result
            st.session_state["last_jd"] = jd_text
            
            db.add_job_application(
                company=company_name.strip(),
                job_title=job_title.strip(),
                job_description=jd_text,
                resume_file=result["path"],
                ats_score=result["ats_score"],
                role_type=result.get("role_type", ""),
                bullets_used=result.get("bullets_used", ""),
            )
            st.success(f"✓ Resume generated! Role detected: **{result.get('role_type', 'Other')}**")
            
        except Exception as e:
            st.error(f"Error: {e}")
            return
    
    if "last_result" in st.session_state:
        result = st.session_state["last_result"]
        
        st.markdown("---")
        st.subheader("ATS Score Analysis")
        
        score = result["ats_score"]
        if score >= 75:
            color = "#22c55e"
            status = "Excellent"
        elif score >= 50:
            color = "#eab308"
            status = "Good"
        else:
            color = "#ef4444"
            status = "Needs Improvement"
        
        st.markdown(f"""
        <div class="ats-score-container">
            <h2 style="margin:0; color:{color};">{score:.0f}% — {status}</h2>
            <div style="background:#e5e7eb; border-radius:4px; height:20px; margin-top:10px;">
                <div style="background:{color}; width:{min(score, 100)}%; height:100%; border-radius:4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Matched Keywords**")
            matched = result.get("matched_keywords", [])
            if matched:
                chips = " ".join([f'<span class="keyword-matched">{kw}</span>' for kw in matched[:20]])
                st.markdown(chips, unsafe_allow_html=True)
            else:
                st.info("No matches found")
        
        with col2:
            st.markdown("**Missing Keywords** (gaps to address)")
            missing = result.get("missing_keywords", [])
            if missing:
                chips = " ".join([f'<span class="keyword-missing">{kw}</span>' for kw in missing[:20]])
                st.markdown(chips, unsafe_allow_html=True)
            else:
                st.success("No significant gaps!")

        ats_score = result.get("ats_score", 0)
        missing_keywords = result.get("missing_keywords", [])
        if ats_score >= 75:
            st.success("Strong match. Apply with confidence.")
        elif ats_score >= 50:
            top_missing = missing_keywords[:3]
            st.warning(f"Good foundation. Consider adding these to your skills section before applying: {', '.join(top_missing)}")
        else:
            top_missing = missing_keywords[:5]
            st.error(f"Significant gaps. Top missing keywords: {', '.join(top_missing)}")

        st.caption(f"Role classified as: {result.get('role_type', 'Unknown')}")
        
        with st.expander("Score Breakdown"):
            section_scores = result.get("section_scores", {})
            st.markdown(f"""
            - **Experience Match**: {section_scores.get('experience', 0):.1f}%
            - **Projects Match**: {section_scores.get('projects', 0):.1f}%
            - **Skills Match**: {section_scores.get('skills', 0):.1f}%
            """)
            
            st.markdown("**Top Selected Bullets:**")
            top_bullets = result.get("top_bullets", [])
            for i, item in enumerate(top_bullets[:5], 1):
                if len(item) >= 2:
                    text, score_val = item[0], item[1]
                    st.markdown(f"{i}. *{text}...* — Score: {score_val:.3f}")
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            resume_path = Path(result["path"])
            if resume_path.exists():
                with open(resume_path, "rb") as f:
                    st.download_button(
                        "📥 Download DOCX",
                        f,
                        file_name=resume_path.name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )
        
        with col2:
            html_path = Path(result.get("html_path", ""))
            if html_path.exists():
                with open(html_path, "r", encoding="utf-8") as f:
                    st.download_button(
                        "📥 Download HTML",
                        f.read(),
                        file_name=html_path.name,
                        mime="text/html",
                    )
        
        with col3:
            html_path = Path(result.get("html_path", ""))
            if html_path.exists():
                if st.button("🌐 Preview HTML"):
                    st.session_state["show_html_preview"] = True
        
        if st.session_state.get("show_html_preview") and html_path.exists():
            st.markdown("---")
            st.subheader("HTML Preview")
            html_content = html_path.read_text(encoding="utf-8")
            st.components.v1.html(html_content, height=800, scrolling=True)


def _tab_cover_letter():
    st.subheader("Cover Letter Generator")
    cl_jd = st.text_area("Paste job description", height=150, key="cl_jd")
    col1, col2, col3 = st.columns(3)
    with col1:
        cl_company = st.text_input("Company name *", key="cl_company")
    with col2:
        cl_title = st.text_input("Job title *", key="cl_title")
    with col3:
        cl_manager = st.text_input("Hiring manager (optional)", key="cl_manager")

    if st.button("Generate Cover Letter"):
        if not cl_company or not cl_title:
            st.error("Company name and job title are required.")
        else:
            try:
                with st.spinner("Generating cover letter..."):
                    result = generate_cover_letter(
                        cl_jd, cl_company, cl_title,
                        cl_manager or "Hiring Manager", db_path=None
                    )
                st.session_state["last_cl"] = result
                st.success("Cover letter generated.")
            except Exception as e:
                st.error(f"Error: {e}")

    if "last_cl" in st.session_state:
        cl = st.session_state["last_cl"]
        st.text_area("Preview", value=cl["content"], height=300, disabled=True)
        col1, col2 = st.columns(2)
        with col1:
            cl_path = Path(cl["path"])
            if cl_path.exists():
                with open(cl_path, "rb") as f:
                    st.download_button(
                        "Download DOCX",
                        f.read(),
                        file_name=cl_path.name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )
        with col2:
            html_path = Path(cl["html_path"])
            if html_path.exists():
                with open(html_path, "rb") as f:
                    st.download_button(
                        "Download HTML",
                        f.read(),
                        file_name=html_path.name,
                        mime="text/html",
                    )


def _tab_cv():
    st.subheader("CV Generator")
    st.caption("Includes all experience, projects, and skills. Not filtered by job description.")
    if st.button("Generate CV"):
        try:
            with st.spinner("Generating CV..."):
                result = generate_cv(db_path=None)
            st.session_state["last_cv"] = result
            st.success("CV generated.")
        except Exception as e:
            st.error(f"Error: {e}")

    if "last_cv" in st.session_state:
        cv = st.session_state["last_cv"]
        col1, col2 = st.columns(2)
        with col1:
            cv_path = Path(cv["path"])
            if cv_path.exists():
                with open(cv_path, "rb") as f:
                    st.download_button(
                        "Download CV (DOCX)",
                        f.read(),
                        file_name=cv_path.name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )
        with col2:
            html_path = Path(cv["html_path"])
            if html_path.exists():
                with open(html_path, "rb") as f:
                    st.download_button(
                        "Download CV (HTML)",
                        f.read(),
                        file_name=html_path.name,
                        mime="text/html",
                    )


def _profile_personal_info():
    info = db.get_personal_info() or {}
    with st.form("personal_form"):
        name = st.text_input("Name", info.get("name", ""))
        email = st.text_input("Email", info.get("email", ""))
        phone = st.text_input("Phone", info.get("phone", ""))
        location = st.text_input("Location", info.get("location", ""))
        linkedin = st.text_input("LinkedIn", info.get("linkedin", ""))
        github = st.text_input("GitHub", info.get("github", ""))
        portfolio = st.text_input("Portfolio", info.get("portfolio", ""))
        
        if st.form_submit_button("Save Personal Info"):
            db.upsert_personal_info(name, email, phone, linkedin, github, portfolio, location)
            st.success("Saved!")
            st.rerun()


def _profile_work_experience():
    jobs = db.get_work_experience()
    if jobs:
        for job in jobs:
            with st.expander(f"{job['company']} — {job['job_title']}"):
                st.write(f"**Period:** {job['start_date']} - {job['end_date'] or 'Present'}")
                bullets = db.get_bullets_for_job(job["id"])
                for b in bullets:
                    st.markdown(f"• {b['bullet_text']}")
                if st.button(f"Delete", key=f"del_job_{job['id']}"):
                    db.delete_work_experience(job["id"])
                    st.rerun()
    
    with st.form("add_job_form"):
        st.subheader("Add Work Experience")
        new_title = st.text_input("Job Title")
        new_company = st.text_input("Company")
        new_start = st.text_input("Start Date (YYYY-MM)")
        new_end = st.text_input("End Date (YYYY-MM or leave blank)")
        new_location = st.text_input("Location")
        
        if st.form_submit_button("Add Job"):
            if new_title and new_company and new_start:
                db.add_work_experience(new_title, new_company, new_start, new_end, new_location)
                st.success("Added!")
                st.rerun()


def _profile_projects():
    projects = db.get_projects()
    if projects:
        for proj in projects:
            with st.expander(proj["project_name"]):
                if proj.get("github_url"):
                    st.write(f"**GitHub:** {proj['github_url']}")
                bullets = db.get_bullets_for_project(proj["id"])
                for b in bullets:
                    st.markdown(f"• {b['bullet_text']}")
                if st.button(f"Delete", key=f"del_proj_{proj['id']}"):
                    db.delete_project(proj["id"])
                    st.rerun()
    
    with st.form("add_project_form"):
        st.subheader("Add Project")
        new_proj_name = st.text_input("Project Name")
        new_proj_url = st.text_input("GitHub URL")
        
        if st.form_submit_button("Add Project"):
            if new_proj_name:
                db.add_project(new_proj_name, github_url=new_proj_url)
                st.success("Added!")
                st.rerun()


def _profile_skills():
    skills = db.get_skills()
    if skills:
        df = pd.DataFrame(skills)[["skill_name", "category", "proficiency"]]
        st.dataframe(df)
    
    with st.form("add_skill_form"):
        st.subheader("Add Skill")
        new_skill = st.text_input("Skill Name")
        new_category = st.selectbox("Category", [
            "Languages", "Databases", "BI & Analytics", "ML & AI",
            "Frameworks & APIs", "Cloud & DevOps", "Tools", "Other"
        ])
        new_prof = st.selectbox("Proficiency", ["Beginner", "Intermediate", "Advanced"])
        
        if st.form_submit_button("Add Skill"):
            if new_skill:
                db.add_skill(new_skill, new_category, new_prof)
                st.success("Added!")
                st.rerun()


def _profile_education():
    education = db.get_education()
    if education:
        for edu in education:
            st.markdown(f"**{edu['degree']}** — {edu['institution']} ({edu.get('year', '')})")
    
    with st.form("add_edu_form"):
        st.subheader("Add Education")
        new_degree = st.text_input("Degree")
        new_field = st.text_input("Field of Study")
        new_inst = st.text_input("Institution")
        new_year = st.text_input("Graduation Year (YYYY-MM)")
        new_gpa = st.text_input("GPA")
        
        if st.form_submit_button("Add Education"):
            if new_degree and new_inst:
                db.add_education(new_degree, new_inst, new_field, "", new_gpa, new_year)
                st.success("Added!")
                st.rerun()


def _profile_certifications():
    certs = db.get_certifications()
    if certs:
        for cert in certs:
            st.markdown(f"**{cert['name']}** — {cert['issuer']} ({cert.get('issued', '')})")
    
    with st.form("add_cert_form"):
        st.subheader("Add Certification")
        new_cert_name = st.text_input("Certification Name")
        new_issuer = st.text_input("Issuer")
        new_issued = st.text_input("Issued Date (YYYY-MM)")
        new_expires = st.text_input("Expires (YYYY-MM)")
        new_cred_id = st.text_input("Credential ID")
        
        if st.form_submit_button("Add Certification"):
            if new_cert_name and new_issuer:
                db.add_certification(new_cert_name, new_issuer, new_issued, new_expires, new_cred_id)
                st.success("Added!")
                st.rerun()


def page_profile():
    st.header("Profile Management")
    
    sections = ["Personal Info", "Work Experience", "Projects", "Skills", "Education", "Certifications"]
    section_funcs = [_profile_personal_info, _profile_work_experience, _profile_projects, 
                     _profile_skills, _profile_education, _profile_certifications]
    
    if HAS_TABS:
        tabs = st.tabs(sections)
        for tab, func in zip(tabs, section_funcs):
            with tab:
                func()
    else:
        section = st.selectbox("Section", sections)
        idx = sections.index(section)
        section_funcs[idx]()


def page_applications():
    st.header("Applications Tracker")
    st.caption("Generating a resume does not mean you applied. Only mark as Applied when you actually submit.")

    all_apps = db.get_job_applications()
    applied_apps = [a for a in all_apps if a.get("applied") == 1 or a.get("outcome") in ["Applied", "Interview", "Offer", "Rejected"]]
    draft_apps = [a for a in all_apps if a.get("applied") == 0 and a.get("outcome") == "Generated"]
    
    status_colors = {
        "Generated": "status-generated",
        "Applied": "status-applied",
        "Interview": "status-interview",
        "Offer": "status-offer",
        "Rejected": "status-rejected",
    }
    
    if applied_apps:
        st.subheader(f"📋 Applied Applications ({len(applied_apps)})")
        
        for app in applied_apps:
            col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1, 1, 2, 1])
            
            with col1:
                st.write(f"**{app['company']}**")
            with col2:
                st.write(app["job_title"])
            with col3:
                score = app.get("ats_score")
                st.write(f"{score:.0f}%" if score else "N/A")
            with col4:
                status_class = status_colors.get(app["outcome"], "status-applied")
                st.markdown(f'<span class="{status_class}">{app["outcome"]}</span>', unsafe_allow_html=True)
            with col5:
                new_status = st.selectbox(
                    "Status",
                    ["Applied", "Interview", "Offer", "Rejected"],
                    index=["Applied", "Interview", "Offer", "Rejected"].index(app["outcome"]) if app["outcome"] in ["Applied", "Interview", "Offer", "Rejected"] else 0,
                    key=f"status_{app['id']}"
                )
                if new_status != app["outcome"]:
                    db.update_job_application_outcome(app["id"], new_status)
                    if new_status in ["Interview", "Offer"]:
                        db.boost_bullets_for_outcome(app["id"], new_status)
                    st.rerun()
            with col6:
                if st.button("🗑️", key=f"del_app_{app['id']}"):
                    st.session_state[f"confirm_delete_{app['id']}"] = True
            
            if st.session_state.get(f"confirm_delete_{app['id']}"):
                st.warning(f"Delete application to {app['company']}?")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("Yes, delete", key=f"confirm_yes_{app['id']}"):
                        db.delete_job_application(app["id"])
                        del st.session_state[f"confirm_delete_{app['id']}"]
                        st.rerun()
                with col_no:
                    if st.button("Cancel", key=f"confirm_no_{app['id']}"):
                        del st.session_state[f"confirm_delete_{app['id']}"]
                        st.rerun()
            
            st.markdown("---")
    
    if draft_apps:
        st.markdown("---")
        st.subheader(f"📝 Draft Resumes ({len(draft_apps)})")
        st.caption("These resumes were generated but not marked as applied yet.")
        
        for app in draft_apps:
            col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 2, 1])
            
            with col1:
                st.write(f"**{app['company']}**")
            with col2:
                st.write(app["job_title"])
            with col3:
                score = app.get("ats_score")
                st.write(f"{score:.0f}%" if score else "N/A")
            with col4:
                if st.button("✓ Mark as Applied", key=f"apply_{app['id']}"):
                    db.mark_application_applied(app["id"], True)
                    st.rerun()
            with col5:
                if st.button("🗑️", key=f"del_draft_{app['id']}"):
                    db.delete_job_application(app["id"])
                    st.rerun()
            
            st.markdown("---")
    
    if not all_apps:
        st.info("No applications tracked yet. Generate a resume to get started!")


def _cluster_jds_by_role(apps):
    role_keywords = {
        "BI Developer": {"power bi", "dashboard", "dax", "semantic model", "reporting", "kpi", "bi"},
        "Data Analyst": {"data analysis", "sql", "excel", "visualization", "analytics", "statistical"},
        "Data Engineer": {"etl", "pipeline", "data pipeline", "airflow", "spark", "data warehouse", "ingestion"},
        "Finance Analyst": {"financial", "budget", "forecasting", "ap/ar", "accounting", "variance", "reconciliation"},
        "ML Engineer": {"machine learning", "ml", "pytorch", "tensorflow", "model", "nlp", "training"},
        "Software Engineer": {"api", "backend", "frontend", "rest", "flask", "javascript", "software"},
    }
    
    clusters = {role: [] for role in role_keywords}
    clusters["Other"] = []
    
    for app in apps:
        jd = (app.get("job_description") or app.get("jd_text") or "").lower()
        best_role = app.get("role_type") or "Other"
        if best_role == "Other":
            best_score = 0
            for role, keywords in role_keywords.items():
                score = sum(1 for kw in keywords if kw in jd)
                if score > best_score:
                    best_score = score
                    best_role = role
        clusters[best_role].append(app)
    
    return {k: v for k, v in clusters.items() if v}


def page_insights():
    st.header("JD Insights & Analytics")
    
    apps = db.get_job_applications(applied_only=True)
    top_keywords = db.get_top_keywords(30)
    
    if not apps and not top_keywords:
        st.info("No job descriptions analyzed yet. Generate and apply to some jobs first!")
        return
    
    recent_kw = db.get_recent_keywords(7)
    old_kw = db.get_old_keywords(30)
    emerging = detect_emerging_keywords(recent_kw, old_kw)
    
    if emerging:
        st.subheader("🚀 Emerging Skills (trending this week)")
        chips = " ".join([f'<span class="keyword-emerging">📈 {kw["keyword"]} (new!)</span>' for kw in emerging[:8]])
        st.markdown(chips, unsafe_allow_html=True)
        st.caption("These keywords appeared in recent JDs but weren't common before. The market is shifting!")
        st.markdown("---")
    
    st.subheader("📊 Keyword Frequency Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Top 20 Keywords Across All JDs**")
        if top_keywords:
            df = pd.DataFrame(top_keywords[:20])
            df.columns = ["Keyword", "Frequency", "Last Seen", "First Seen"]
            st.bar_chart(df.set_index("Keyword")["Frequency"])
        else:
            st.info("No keyword data yet.")
    
    with col2:
        st.markdown("**Word Cloud** (sized by frequency)")
        if top_keywords:
            max_count = max(kw["jd_count"] for kw in top_keywords)
            word_cloud_html = '<div style="text-align:center; line-height:2.5; padding:20px; background:#f8fafc; border-radius:8px;">'
            for kw in top_keywords[:25]:
                size = 12 + int((kw["jd_count"] / max_count) * 24)
                opacity = 0.5 + (kw["jd_count"] / max_count) * 0.5
                word_cloud_html += f'<span style="font-size:{size}px; opacity:{opacity}; margin:0 8px; color:#1e40af;">{kw["keyword"]}</span> '
            word_cloud_html += '</div>'
            st.markdown(word_cloud_html, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🎯 Gap Analysis: Keywords to Add")
    
    all_bullets = db.get_all_bullets()
    bullet_text = " ".join([b["bullet_text"] + " " + (b.get("keywords") or "") for b in all_bullets]).lower()
    
    missing_high_value = []
    for kw_data in top_keywords[:20]:
        kw = kw_data["keyword"]
        if kw.lower() not in bullet_text and kw_data["jd_count"] >= 1:
            missing_high_value.append((kw, kw_data["jd_count"]))
    
    if missing_high_value:
        st.warning(f"**{len(missing_high_value)} high-frequency JD keywords** are missing from your resume:")
        chips = " ".join([f'<span class="keyword-missing">{kw} ({count})</span>' for kw, count in missing_high_value[:15]])
        st.markdown(chips, unsafe_allow_html=True)
    else:
        st.success("Your resume covers the most common keywords!")
    
    st.markdown("---")
    st.subheader("📁 Applications by Role Type")
    
    if apps:
        clusters = _cluster_jds_by_role(apps)
        
        if clusters:
            cluster_data = [{"Role": role, "Count": len(jobs)} for role, jobs in clusters.items()]
            df_clusters = pd.DataFrame(cluster_data)
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.bar_chart(df_clusters.set_index("Role")["Count"])
            with col2:
                st.markdown("**Role Distribution:**")
                for role, jobs in clusters.items():
                    companies = ", ".join([j["company"] for j in jobs[:3]])
                    if len(jobs) > 3:
                        companies += f" +{len(jobs)-3} more"
                    st.markdown(f"- **{role}** ({len(jobs)}): {companies}")
    
    st.markdown("---")
    st.subheader("📋 Application History")
    
    if apps:
        app_data = []
        for app in apps:
            app_data.append({
                "Date": app["date_applied"],
                "Company": app["company"],
                "Title": app["job_title"],
                "Role": app.get("role_type", "Other"),
                "ATS Score": f"{app['ats_score']:.0f}%" if app.get("ats_score") else "N/A",
                "Status": app["outcome"],
            })
        df = pd.DataFrame(app_data)
        st.dataframe(df)
        
        st.markdown(f"**Total Applied:** {len(apps)}")
        avg_score = [a["ats_score"] for a in apps if a.get("ats_score")]
        if avg_score:
            st.markdown(f"**Average ATS Score:** {sum(avg_score)/len(avg_score):.1f}%")
        
        interviews = sum(1 for a in apps if a["outcome"] == "Interview")
        offers = sum(1 for a in apps if a["outcome"] == "Offer")
        if interviews or offers:
            st.markdown(f"**Success:** {interviews} interviews, {offers} offers")


def page_settings():
    st.header("Settings")
    
    st.subheader("Data Management")
    
    if st.button("Reload Data from gopi_data.py"):
        try:
            from gopi_data import PERSONAL_INFO
            db.clear_all_data()
            import subprocess
            result = subprocess.run(
                [sys.executable, "main.py", "load-gopi"],
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).parent)
            )
            if result.returncode == 0:
                st.success("Data reloaded!")
                st.rerun()
            else:
                st.error(f"Error: {result.stderr}")
        except Exception as e:
            st.error(f"Error: {e}")
    
    st.markdown("---")
    st.subheader("Database Info")
    
    info = db.get_personal_info()
    jobs = db.get_work_experience()
    skills = db.get_skills()
    projects = db.get_projects()
    bullets = db.get_all_bullets()
    apps = db.get_job_applications()
    
    st.markdown(f"""
    - **Personal Info**: {'✓' if info else '✗'}
    - **Work Experience**: {len(jobs)} jobs
    - **Projects**: {len(projects)} projects
    - **Skills**: {len(skills)} skills
    - **Bullets**: {len(bullets)} total
    - **Applications**: {len(apps)} tracked
    """)
    
    st.markdown("---")
    st.subheader("Bullet Performance")
    
    perf = db.get_all_bullet_performance()
    if perf:
        st.markdown("**Top Performing Bullets** (by interview/offer success):")
        for p in perf[:5]:
            text = p.get("bullet_text", "")[:60]
            st.markdown(f"- *{text}...* — {p['times_selected']} uses, {p['times_in_interview']} interviews, {p['times_in_offer']} offers")
    else:
        st.info("Generate more resumes and track outcomes to see bullet performance data.")


def main():
    st.title("📄 Resume Generator")
    
    if HAS_TABS:
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Generator", "Profile", "Applications", "Insights", "Settings"
        ])
        
        with tab1:
            page_generator()
        with tab2:
            page_profile()
        with tab3:
            page_applications()
        with tab4:
            page_insights()
        with tab5:
            page_settings()
    else:
        page = st.sidebar.radio(
            "Navigate",
            ["Generator", "Profile", "Applications", "Insights", "Settings"]
        )
        
        if page == "Generator":
            page_generator()
        elif page == "Profile":
            page_profile()
        elif page == "Applications":
            page_applications()
        elif page == "Insights":
            page_insights()
        elif page == "Settings":
            page_settings()


if __name__ == "__main__":
    main()
