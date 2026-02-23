# Resume Generator

A Streamlit app that generates **resumes**, **cover letters**, and **CVs** from your profile data. Fully template-based—no AI, no external APIs.

## Features

### 📄 Resume (JD-targeted)
- Paste a job description; the app selects the most relevant bullets, projects, and skills
- TF-IDF weighting, role-specific scoring, and bullet performance tracking
- ATS score with matched/missing keywords and section breakdown
- Outputs DOCX and HTML

### ✉️ Cover Letter (template-based)
- Paste job description, company name, job title, and optional hiring manager
- Pulls top 2 bullets from your current role and top 3 JD-matching skills
- Professional template with your data slotted in
- Outputs DOCX and HTML

### 📋 CV (full document)
- Complete document with **all** experience, projects, and skills
- No filtering—includes every bullet and project
- Professional summary built from your data
- Outputs DOCX and HTML

### Other
- **Profile** – Edit personal info, work experience, projects, skills, education, certifications
- **Applications** – Track job applications and outcomes (applied, interview, offer, rejected)
- **Insights** – JD insights, emerging keywords, keyword frequency
- **Settings** – Reload data from `gopi_data.py`, view database stats, bullet performance

## Tech Stack

- **Python** – Streamlit, SQLite
- **Node.js** – docx library for DOCX generation
- **Template-based** – No AI or external APIs

## Setup

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm

### Installation

```bash
cd resume-generator
pip install -r requirements.txt
npm install
```

### Run

```bash
streamlit run app.py
```

## Usage

1. **Profile** – Add personal info, experience, projects, skills, education, certifications.
2. **Generator** – Choose tab:
   - **Resume** – Paste JD, enter company/job title, set bullets per job, generate.
   - **Cover Letter** – Paste JD, company, title, optional hiring manager, generate.
   - **CV** – Click Generate (no JD needed).
3. Download DOCX or HTML from each tab.

Outputs are saved in `outputs/`.

## Project Structure

```
resume-generator/
├── app.py              # Streamlit app
├── resume_template.js  # Node.js DOCX generator (resume, cover letter, CV)
├── gopi_data.py        # Seed data (optional)
├── main.py             # CLI for loading data
├── outputs/            # Generated DOCX/HTML files
├── data/               # SQLite database
└── src/
    ├── generator.py    # Resume, cover letter, CV generation
    ├── scoring.py      # Keywords, ATS score, bullet selection
    └── db.py           # SQLite operations
```

## How It Works

### Resume
- Extracts keywords from the job description (unigrams, bigrams, trigrams)
- Scores bullets by JD match, recency, TF-IDF, role weights, and past performance
- Selects top N bullets per job and top 3 projects
- Filters skills by JD relevance
- Calculates ATS score and returns matched/missing keywords

### Cover Letter
- Uses `select_top_bullets()` to pick top 2 bullets from the current job
- Selects top 3 skills that appear in the JD
- Slots data into a professional template
- Generates DOCX via Node.js and HTML in Python

### CV
- Uses full profile data with no filtering
- Builds a professional summary from current job and skills
- Passes `is_cv: true` and `summary` to the template
- Node.js template includes all bullets, all projects, all skills

### DOCX Generation (Node.js)
- `resume_template.js` accepts `--type resume|coverletter|cv`
- For resume: Experience → Projects → Skills → Certifications → Education
- For cover letter: Header, date, body paragraphs
- For CV: Summary → Experience → Projects → Skills → Certifications → Education (all content)

## CLI

```bash
# Load data from gopi_data.py
python main.py load-gopi
```

## License

MIT
