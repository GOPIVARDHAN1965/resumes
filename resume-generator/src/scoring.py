"""
Enhanced scoring engine with:
- TF-IDF style keyword weighting
- Role-specific scoring
- Bullet performance tracking
- Phrase matching and synonym expansion
"""

import re
import math
from collections import Counter
from typing import Optional
from pathlib import Path

SYNONYM_MAP = {
    "business intelligence": ["power bi", "bi reporting", "dashboards", "tableau", "data visualization"],
    "federal grants": ["federal funding", "flair", "focus", "grant management", "fema", "disaster recovery"],
    "machine learning": ["ml", "scikit-learn", "pytorch", "tensorflow", "model training", "deep learning"],
    "data warehouse": ["snowflake", "sql server", "redshift", "bigquery", "data mart", "olap"],
    "etl": ["data pipeline", "data ingestion", "data engineering", "airflow", "data extraction"],
    "agile": ["scrum", "sprint", "jira", "iterative", "continuous improvement", "kanban"],
    "api": ["rest api", "flask", "fastapi", "endpoint", "http", "web service", "api development"],
    "visualization": ["power bi", "tableau", "plotly", "dash", "dashboard", "charts", "reporting"],
    "quantitative": ["arima", "prophet", "forecasting", "statistical", "time series", "analytics"],
    "self-service": ["power bi", "reporting", "dashboard", "end-user reporting", "self service"],
    "nlp": ["natural language processing", "text classification", "sentiment analysis", "langchain", "llm"],
    "cloud": ["aws", "azure", "gcp", "cloud computing", "s3", "ec2", "lambda"],
    "database": ["mysql", "postgresql", "sql server", "mongodb", "nosql", "sql", "sqlite"],
    "automation": ["power automate", "selenium", "scheduling", "windows task scheduler", "cron"],
    "financial analysis": ["budgeting", "forecasting", "variance analysis", "financial modeling", "ap/ar"],
    "azure blob storage": ["azure blob", "blob storage", "azure storage", "cloud storage", "data lake"],
    "power bi": ["powerbi", "power-bi", "bi dashboard", "business intelligence dashboard"],
    "flair": ["flair system", "florida accounting", "state financial system"],
    "hmgp": ["hazard mitigation", "hazard mitigation grant program", "fema grant"],
    "grant management": ["federal grants", "grant tracking", "grant reconciliation", "150 grants"],
    "data pipeline": ["etl pipeline", "data ingestion", "automated pipeline", "python pipeline"],
    "reconciliation": ["recon", "data reconciliation", "financial reconciliation", "source to target"],
    "anomaly detection": ["outlier detection", "flag transactions", "transaction monitoring", "misallocation"],
    "azure": ["azure blob storage", "microsoft azure", "azure sql", "azure data"],
    "transfer memo": ["transfer memos", "fund transfer", "grant transfer", "reallocation"],
    "bureau-wide": ["bureau", "division-wide", "agency-wide"],
    "director": ["bureau director", "division head", "executive", "leadership"],
    "governance": ["data governance", "compliance", "audit"],
    "deduplication": ["dedupe", "duplicate removal"],
    "catalog": ["data catalog", "metadata"],
    "fccm": ["certified contract manager", "contract management"],
}

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does",
    "did", "will", "would", "could", "should", "may", "might", "must", "can", "shall",
    "about", "above", "after", "again", "all", "also", "am", "any", "as", "because",
    "before", "below", "between", "both", "by", "come", "day", "down", "during", "each",
    "few", "from", "get", "give", "go", "good", "great", "he", "her", "here", "him",
    "his", "how", "i", "if", "into", "it", "its", "just", "know", "like", "long",
    "look", "make", "many", "me", "more", "most", "my", "new", "no", "not", "now",
    "old", "one", "only", "other", "our", "out", "over", "own", "part", "people",
    "say", "see", "she", "so", "some", "take", "than", "that", "their", "them",
    "then", "there", "these", "they", "thing", "think", "this", "those", "through",
    "time", "too", "two", "under", "up", "us", "use", "very", "want", "way", "we",
    "well", "what", "when", "where", "which", "while", "who", "why", "work", "world",
    "year", "you", "your", "ability", "able", "across", "candidate", "experience",
    "looking", "seeking", "preferred", "required", "responsibilities", "qualifications",
    "join", "team", "role", "position", "opportunity", "company", "strong", "excellent",
}

ROLE_KEYWORDS = {
    "BI Developer": {"power bi", "dashboard", "dax", "semantic model", "reporting", "kpi", "bi", "data visualization"},
    "Data Analyst": {"data analysis", "sql", "excel", "visualization", "analytics", "statistical", "insights"},
    "Data Engineer": {"etl", "pipeline", "data pipeline", "airflow", "spark", "data warehouse", "ingestion", "kafka"},
    "Finance Analyst": {"financial", "budget", "forecasting", "ap/ar", "accounting", "variance", "reconciliation"},
    "ML Engineer": {"machine learning", "ml", "pytorch", "tensorflow", "model", "nlp", "training", "deep learning"},
    "Software Engineer": {"api", "backend", "frontend", "rest", "flask", "javascript", "software", "microservices"},
}

SKILLS_WHITELIST = [
    "azure blob storage", "azure data factory", "azure sql", "azure devops",
    "azure", "aws", "gcp", "s3", "ec2", "lambda",
    "python", "sql", "dax", "vba", "r", "java", "javascript", "c++",
    "power query", "m language",
    "power bi", "tableau", "looker", "qlik", "excel", "plotly", "dash",
    "power automate", "semantic model", "row-level security",
    "mysql", "postgresql", "sql server", "mongodb", "snowflake", "sqlite",
    "redshift", "bigquery", "oracle",
    "etl", "data pipeline", "airflow", "spark", "kafka", "dbt",
    "data ingestion", "data engineering", "data warehouse",
    "flair", "focus", "hmgp", "fema", "sharepoint", "onedrive",
    "flask", "fastapi", "streamlit", "selenium", "pytest", "django",
    "rest api", "api", "langchain", "faiss",
    "arima", "prophet", "scikit-learn", "pytorch", "tensorflow",
    "nlp", "rag", "vector embeddings", "hugging face", "pinecone",
    "time series", "forecasting", "machine learning",
    "data governance", "data modeling", "kpi", "sla", "etl pipeline",
    "data migration", "data catalog", "data quality", "reconciliation",
    "grant management", "federal grants", "budget forecasting",
    "variance analysis", "anomaly detection", "audit trail",
    "ci/cd", "docker", "kubernetes", "git", "github",
    "windows task scheduler", "task scheduler",
    "aws certified", "fccm", "pmp",
    "stakeholder management", "executive reporting", "director level",
    "bureau wide", "bureau-wide", "self-service reporting", "agile", "scrum",
    "transfer memo", "budget incremental", "disaster recovery",
]


def _tokenize(text: str) -> list:
    return re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.\-]{1,}\b", text.lower())


def extract_unigrams(text: str) -> set:
    tokens = _tokenize(text)
    return {t for t in tokens if t not in STOP_WORDS and len(t) > 2}


def extract_bigrams(text: str) -> set:
    tokens = _tokenize(text)
    bigrams = set()
    BIGRAM_STOP = {
        "and", "or", "the", "a", "an", "in", "on", "at", "to", "for",
        "of", "with", "is", "are", "was", "were", "be", "by", "from",
        "as", "its", "our", "their", "this", "that", "will", "can",
        "including", "such", "across", "within", "between", "through",
        "using", "via", "per", "over", "into", "onto", "upon",
    }
    for i in range(len(tokens) - 1):
        t1, t2 = tokens[i], tokens[i + 1]
        if t1 in BIGRAM_STOP or t2 in BIGRAM_STOP:
            continue
        if len(t1) < 3 or len(t2) < 3:
            continue
        bigrams.add(f"{t1} {t2}")
    return bigrams


def extract_trigrams(text: str) -> set:
    tokens = _tokenize(text)
    trigrams = set()
    GRAM_STOP = {
        "and", "or", "the", "a", "an", "in", "on", "at", "to", "for",
        "of", "with", "is", "are", "was", "were", "be", "by", "from",
    }
    for i in range(len(tokens) - 2):
        t1, t2, t3 = tokens[i], tokens[i + 1], tokens[i + 2]
        if t1 in GRAM_STOP or t3 in GRAM_STOP:
            continue
        if len(t1) < 3 or len(t2) < 3 or len(t3) < 3:
            continue
        trigrams.add(f"{t1} {t2} {t3}")
    return trigrams


def _term_in_text(term: str, text: str) -> bool:
    """Match term with word boundaries for short terms to avoid false positives (e.g. 'r' in 'recovery')."""
    if len(term) <= 2:
        return bool(re.search(r"\b" + re.escape(term) + r"\b", text))
    return term in text


def extract_keywords(text: str) -> dict:
    """
    Extract only real skills and tools from JD text by checking against a skills whitelist.
    No garbage bigrams or sentence fragments.
    """
    text_lower = text.lower()
    matched = set()

    for term in sorted(SKILLS_WHITELIST, key=len, reverse=True):
        if _term_in_text(term, text_lower):
            matched.add(term)

    acronyms = set(re.findall(r"\b[A-Z]{2,6}\b", text))
    matched.update(a.lower() for a in acronyms if len(a) >= 2)

    return {
        "unigrams": matched,
        "bigrams": set(),
        "trigrams": set(),
        "all": matched,
    }


def expand_synonyms(keywords: set) -> set:
    """Expand keywords with synonyms."""
    expanded = set(keywords)
    keywords_lower = {k.lower() for k in keywords}
    
    for canonical, synonyms in SYNONYM_MAP.items():
        if canonical.lower() in keywords_lower:
            expanded.update(synonyms)
        for syn in synonyms:
            if syn.lower() in keywords_lower:
                expanded.add(canonical)
                expanded.update(synonyms)
                break
    return expanded


def classify_role(jd_text: str) -> str:
    """Classify a job description into a role type."""
    jd_lower = jd_text.lower()
    best_role = "Other"
    best_score = 0
    
    for role, keywords in ROLE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in jd_lower)
        if score > best_score:
            best_score = score
            best_role = role
    
    return best_role


def compute_tfidf_weights(freq_map: dict, total_jds: int) -> dict:
    """
    Compute TF-IDF style weights for keywords.
    Formula: (jd_count / total_jds) * log(1 + jd_count)
    Keywords appearing in ~60% of JDs are weighted higher than those in 100%.
    """
    if total_jds < 1:
        total_jds = 1
    
    weights = {}
    for kw, count in freq_map.items():
        tf = count / total_jds
        idf_factor = math.log(1 + count)
        uniqueness = 1.0 - (tf * 0.3) if tf > 0.8 else 1.0
        weights[kw] = tf * idf_factor * uniqueness
    
    total_weight = sum(weights.values()) or 1
    return {kw: w / total_weight for kw, w in weights.items()}


def get_keyword_weight(keyword: str, tfidf_weights: dict, role_weights: dict = None) -> float:
    """Get combined weight for a keyword from TF-IDF and role-specific weights."""
    base_weight = tfidf_weights.get(keyword.lower(), 0.01)
    
    if role_weights:
        role_boost = role_weights.get(keyword.lower(), 1.0)
        base_weight *= (1 + role_boost * 0.2)
    
    return base_weight


def get_bullet_performance_multiplier(bullet_id: int, perf_map: dict) -> float:
    """Get performance multiplier based on bullet's historical success."""
    if not perf_map or bullet_id not in perf_map:
        return 1.0
    
    perf = perf_map[bullet_id]
    times_selected = perf.get("times_selected", 0)
    high_ats = perf.get("times_in_high_ats_resume", 0)
    interviews = perf.get("times_in_interview", 0)
    offers = perf.get("times_in_offer", 0)
    
    if times_selected < 2:
        return 1.0
    
    multiplier = 1.0
    
    high_ats_rate = high_ats / times_selected
    multiplier += high_ats_rate * 0.15
    
    if interviews > 0:
        multiplier += 0.10 * min(interviews, 3)
    if offers > 0:
        multiplier += 0.20 * min(offers, 2)
    
    return min(multiplier, 1.5)


def score_bullet(bullet: dict, jd_keywords: dict, recency_mult: float = 1.0,
                 tfidf_weights: Optional[dict] = None, role_weights: Optional[dict] = None,
                 perf_map: Optional[dict] = None) -> dict:
    """
    Score a bullet against JD whitelist skills. Count how many JD skills appear in bullet.
    """
    bullet_text = (bullet.get("text", "") + " " + bullet.get("keywords", "")).lower()
    jd_skills = jd_keywords.get("all", set())
    matched = set()

    for skill in jd_skills:
        if _term_in_text(skill, bullet_text):
            matched.add(skill)
        else:
            for canonical, synonyms in SYNONYM_MAP.items():
                if skill in synonyms or skill == canonical:
                    if _term_in_text(canonical, bullet_text) or any(
                        _term_in_text(s, bullet_text) for s in synonyms
                    ):
                        matched.add(skill)
                        break

    if tfidf_weights and matched:
        weighted_score = sum(get_keyword_weight(kw, tfidf_weights, role_weights) for kw in matched)
        base_score = weighted_score * (len(matched) / max(len(jd_skills), 1))
    else:
        base_score = len(matched) / max(len(jd_skills), 1)

    bullet_id = bullet.get("id")
    perf_mult = get_bullet_performance_multiplier(bullet_id, perf_map) if bullet_id else 1.0
    final_score = base_score * recency_mult * perf_mult

    return {
        "score": round(final_score, 4),
        "matched_keywords": list(matched),
        "bullet": bullet,
        "bullet_id": bullet_id,
    }


def score_all_bullets(jobs: list, jd_keywords: dict, tfidf_weights: Optional[dict] = None,
                      role_weights: Optional[dict] = None, perf_map: Optional[dict] = None) -> list:
    """Score all bullets across all jobs with recency weighting."""
    scored = []
    for i, job in enumerate(jobs):
        if i == 0:
            recency = 1.15
        elif i == 1:
            recency = 1.0
        else:
            recency = 0.85
        
        for bullet in job.get("bullets", []):
            result = score_bullet(bullet, jd_keywords, recency, tfidf_weights, role_weights, perf_map)
            result["job_index"] = i
            result["company"] = job.get("company", "")
            result["title"] = job.get("title", "")
            scored.append(result)
    return sorted(scored, key=lambda x: x["score"], reverse=True)


def select_top_bullets(items: list, jd_keywords: dict, top_n: int = 5,
                       tfidf_weights: Optional[dict] = None, role_weights: Optional[dict] = None,
                       perf_map: Optional[dict] = None) -> tuple:
    """
    Select top N bullets per job/project based on score.
    Returns (items_with_selected_bullets, list_of_selected_bullet_ids).
    """
    result = []
    all_selected_ids = []
    
    for i, item in enumerate(items):
        bullets = item.get("bullets", [])
        if not bullets:
            item_copy = {k: v for k, v in item.items()}
            item_copy["bullets"] = []
            item_copy["selected_scores"] = []
            result.append(item_copy)
            continue
        
        if i == 0:
            recency = 1.15
        elif i == 1:
            recency = 1.0
        else:
            recency = 0.85
        
        scored = []
        for b in bullets:
            score_result = score_bullet(b, jd_keywords, recency, tfidf_weights, role_weights, perf_map)
            scored.append((b, score_result["score"], score_result["matched_keywords"], score_result.get("bullet_id")))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        top_bullets = [s[0] for s in scored[:top_n]]
        top_scores = [(s[0].get("text", "")[:50], s[1], s[2]) for s in scored[:top_n]]
        selected_ids = [s[3] for s in scored[:top_n] if s[3]]
        
        all_selected_ids.extend(selected_ids)
        
        item_copy = {k: v for k, v in item.items() if k != "bullets"}
        item_copy["bullets"] = top_bullets
        item_copy["selected_scores"] = top_scores
        result.append(item_copy)
    
    return result, all_selected_ids


def filter_skills_by_relevance(skills: list, jd_keywords: dict) -> list:
    """Filter skills to show only categories matching JD keywords."""
    jd_all = " ".join(jd_keywords.get("all", set())).lower()
    
    category_keywords = {
        "Languages": ["python", "sql", "java", "javascript", "r", "dax", "vba", "c++"],
        "Databases": ["mysql", "postgresql", "sql server", "mongodb", "snowflake", "sqlite", "database"],
        "BI & Analytics": ["power bi", "dashboard", "reporting", "visualization", "etl", "analytics", "kpi"],
        "ML & AI": ["machine learning", "ml", "nlp", "pytorch", "tensorflow", "scikit", "ai", "model"],
        "Frameworks & APIs": ["flask", "fastapi", "api", "rest", "streamlit", "dash", "next.js"],
        "Cloud & DevOps": ["aws", "azure", "gcp", "docker", "kubernetes", "cloud", "devops", "ci/cd"],
        "Tools": ["git", "selenium", "sharepoint", "automation"],
    }
    
    relevant_categories = set()
    for category, keywords in category_keywords.items():
        for kw in keywords:
            if kw in jd_all:
                relevant_categories.add(category)
                break
    
    if not relevant_categories:
        return skills
    
    relevant_categories.add("Languages")
    
    return [s for s in skills if s.get("category", "") in relevant_categories]


def calculate_ats_score(jd_keywords: dict, resume_data: dict) -> dict:
    """Calculate ATS score: JD whitelist skills vs full resume text."""
    resume_text = ""
    for job in resume_data.get("experience", []):
        for b in job.get("bullets", []):
            text = b.get("text", "") if isinstance(b, dict) else b
            kw = b.get("keywords", "") if isinstance(b, dict) else ""
            resume_text += " " + text + " " + kw
    for proj in resume_data.get("projects", []):
        for b in proj.get("bullets", []):
            text = b.get("text", "") if isinstance(b, dict) else b
            kw = b.get("keywords", "") if isinstance(b, dict) else ""
            resume_text += " " + text + " " + kw
    for skill in resume_data.get("skills", []):
        resume_text += " " + skill.get("name", "")
    resume_text = resume_text.lower()

    jd_skills = jd_keywords.get("all", set())
    matched = set()
    missing = set()

    for skill in jd_skills:
        if _term_in_text(skill, resume_text):
            matched.add(skill)
        else:
            found = False
            for canonical, synonyms in SYNONYM_MAP.items():
                if skill in synonyms or skill == canonical:
                    if _term_in_text(canonical, resume_text) or any(
                        _term_in_text(s, resume_text) for s in synonyms
                    ):
                        matched.add(skill)
                        found = True
                        break
            if not found:
                missing.add(skill)

    total = len(jd_skills)
    score = (len(matched) / total * 100) if total > 0 else 0

    return {
        "score": round(score, 1),
        "matched": sorted(list(matched)),
        "missing": sorted(list(missing)),
        "total_jd": total,
        "total_matched": len(matched),
    }


def get_section_scores(experience_scores: list, project_scores: list, 
                       skills_matched: int, skills_total: int) -> dict:
    """Get match percentages per section."""
    exp_avg = 0
    if experience_scores:
        exp_avg = sum(s[1] for s in experience_scores) / len(experience_scores) * 100
    
    proj_avg = 0
    if project_scores:
        proj_avg = sum(s[1] for s in project_scores) / len(project_scores) * 100
    
    skills_pct = (skills_matched / skills_total * 100) if skills_total > 0 else 0
    
    return {
        "experience": round(exp_avg, 1),
        "projects": round(proj_avg, 1),
        "skills": round(skills_pct, 1)
    }


def detect_emerging_keywords(recent_keywords: list, old_keywords: list) -> list:
    """
    Detect keywords trending up in recent JDs.
    Returns keywords appearing in 3+ recent JDs but not prominent in older ones.
    """
    old_set = {kw["keyword"] for kw in old_keywords}
    emerging = []
    
    for kw in recent_keywords:
        if kw["jd_count"] >= 2 and kw["keyword"] not in old_set:
            emerging.append(kw)
    
    return emerging[:10]
