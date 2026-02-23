#!/usr/bin/env python3
"""
Resume Generator CLI
"""

import argparse
import sys
from pathlib import Path

src_path = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(src_path.parent))

from src import db
from src.generator import generate_resume, get_output_dir


def cmd_init(args):
    """Initialize the database."""
    db_path = db.init_db()
    print(f"Database initialized at {db_path}")
    
    if args.gopi:
        cmd_load_gopi(args)


def cmd_load_gopi(args):
    """Load gopi_data.py into the database."""
    try:
        from gopi_data import (
            PERSONAL_INFO, EDUCATION, CERTIFICATIONS, 
            WORK_EXPERIENCE, PROJECTS, SKILLS, ACHIEVEMENTS
        )
    except ImportError:
        print("Error: gopi_data.py not found in project root.")
        sys.exit(1)
    
    print("Clearing existing data...")
    db.clear_all_data()
    
    print("Loading personal info...")
    db.upsert_personal_info(
        name=PERSONAL_INFO["name"],
        email=PERSONAL_INFO["email"],
        phone=PERSONAL_INFO.get("phone", ""),
        linkedin=PERSONAL_INFO.get("linkedin", ""),
        github=PERSONAL_INFO.get("github", ""),
        portfolio=PERSONAL_INFO.get("portfolio", ""),
        location=PERSONAL_INFO.get("location", ""),
    )
    
    print("Loading education...")
    for i, edu in enumerate(EDUCATION):
        db.add_education(
            degree=f"{edu['degree']} in {edu.get('field', '')}" if edu.get('field') else edu['degree'],
            institution=edu["institution"],
            field=edu.get("field", ""),
            location=edu.get("location", ""),
            gpa=edu.get("gpa", ""),
            year=edu.get("end_date", ""),
            display_order=i,
        )
    
    print("Loading certifications...")
    for i, cert in enumerate(CERTIFICATIONS):
        db.add_certification(
            name=cert["name"],
            issuer=cert["issuer"],
            issued=cert.get("issued", ""),
            expires=cert.get("expires", ""),
            credential_id=cert.get("credential_id", ""),
            display_order=i,
        )
    
    print("Loading work experience and bullets...")
    for i, job in enumerate(WORK_EXPERIENCE):
        job_id = db.add_work_experience(
            job_title=job["title"],
            company=job["company"],
            start_date=job["start_date"],
            end_date=job.get("end_date") or "",
            location=job.get("location", ""),
            display_order=i,
        )
        for j, bullet in enumerate(job.get("bullets", [])):
            db.add_bullet(
                bullet_text=bullet["text"],
                keywords=bullet.get("keywords", ""),
                work_experience_id=job_id,
                display_order=j,
            )
    
    print("Loading projects and bullets...")
    for i, proj in enumerate(PROJECTS):
        proj_id = db.add_project(
            project_name=proj["name"],
            github_url=proj.get("github_url", ""),
            display_order=i,
        )
        for j, bullet in enumerate(proj.get("bullets", [])):
            db.add_bullet(
                bullet_text=bullet["text"],
                keywords=bullet.get("keywords", ""),
                project_id=proj_id,
                display_order=j,
            )
    
    print("Loading skills...")
    for i, skill in enumerate(SKILLS):
        db.add_skill(
            skill_name=skill["name"],
            category=skill.get("category", ""),
            proficiency=skill.get("proficiency", ""),
            display_order=i,
        )
    
    if ACHIEVEMENTS:
        print("Loading achievements as a project...")
        ach_id = db.add_project(
            project_name="Achievements",
            display_order=len(PROJECTS),
        )
        for j, ach in enumerate(ACHIEVEMENTS):
            text = f"{ach['title']}: {ach['description']}"
            db.add_bullet(
                bullet_text=text,
                keywords="achievement, award, recognition",
                project_id=ach_id,
                display_order=j,
            )
    
    print("Done! Data loaded successfully.")


def cmd_generate(args):
    """Generate a resume from a job description."""
    jd = args.job_description or ""
    if args.jd_file:
        jd = Path(args.jd_file).read_text()
    
    try:
        result = generate_resume(
            job_description=jd,
            top_n=args.bullets,
            output_filename=args.output,
        )
        print(f"Resume generated: {result['path']}")
        print(f"ATS Score: {result['ats_score']:.1f}%")
        if result['matched_keywords']:
            print(f"Matched: {', '.join(result['matched_keywords'][:10])}")
        if result['missing_keywords']:
            print(f"Missing: {', '.join(result['missing_keywords'][:10])}")
        
        if args.track:
            db.add_job_application(
                company=args.company or "Unknown",
                job_title=args.title or "Unknown",
                job_description=jd,
                resume_file=result['path'],
                ats_score=result['ats_score'],
            )
            print("Application tracked.")
    except (RuntimeError, ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_list(args):
    """List data in the database."""
    if args.type == "personal":
        info = db.get_personal_info()
        if info:
            for k, v in info.items():
                if v and k not in ("id", "created_at"):
                    print(f"{k}: {v}")
        else:
            print("No personal info found.")
    
    elif args.type == "work":
        jobs = db.get_work_experience()
        for job in jobs:
            print(f"\n{job['company']} - {job['job_title']}")
            print(f"  {job['start_date']} - {job['end_date'] or 'Present'}")
            bullets = db.get_bullets_for_job(job['id'])
            for b in bullets[:3]:
                print(f"  • {b['bullet_text'][:80]}...")
    
    elif args.type == "skills":
        skills = db.get_skills()
        by_cat = {}
        for s in skills:
            cat = s.get("category") or "Other"
            by_cat.setdefault(cat, []).append(s["skill_name"])
        for cat, names in by_cat.items():
            print(f"{cat}: {', '.join(names)}")
    
    elif args.type == "applications":
        apps = db.get_job_applications()
        for app in apps:
            score = f"{app['ats_score']:.0f}%" if app.get('ats_score') else "N/A"
            print(f"{app['date_applied']} | {app['company']} - {app['job_title']} | {app['outcome']} | ATS: {score}")


def main():
    parser = argparse.ArgumentParser(description="Resume Generator CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    init_parser = subparsers.add_parser("init", help="Initialize the database")
    init_parser.add_argument("--gopi", action="store_true", help="Load gopi_data.py after init")
    
    subparsers.add_parser("load-gopi", help="Load gopi_data.py into database")
    
    gen_parser = subparsers.add_parser("generate", help="Generate a resume")
    gen_parser.add_argument("-j", "--job-description", help="Job description text")
    gen_parser.add_argument("-f", "--jd-file", help="Path to job description file")
    gen_parser.add_argument("-o", "--output", help="Output filename")
    gen_parser.add_argument("-b", "--bullets", type=int, default=5, help="Bullets per job")
    gen_parser.add_argument("--track", action="store_true", help="Track this application")
    gen_parser.add_argument("--company", help="Company name for tracking")
    gen_parser.add_argument("--title", help="Job title for tracking")
    
    list_parser = subparsers.add_parser("list", help="List data")
    list_parser.add_argument("type", choices=["personal", "work", "skills", "applications"])
    
    args = parser.parse_args()
    
    if args.command == "init":
        cmd_init(args)
    elif args.command == "load-gopi":
        cmd_load_gopi(args)
    elif args.command == "generate":
        cmd_generate(args)
    elif args.command == "list":
        cmd_list(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
