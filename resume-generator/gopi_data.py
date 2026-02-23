"""
GOPI VARDHAN GUNTA — Resume Generator Seed Data (Enhanced v2)
=============================================================
Instructions for Cursor:
1. Drop this file in the project root as gopi_data.py
2. Run: python main.py load-gopi
   to clear existing data and reload everything fresh.

See CURSOR_PROMPT at the bottom of this file for what to
ask Cursor to build next (ATS scoring, scoring improvements, UI fixes).
"""

# ─────────────────────────────────────────────
# PERSONAL INFO
# ─────────────────────────────────────────────
PERSONAL_INFO = {
    "name": "GopiVardhan Gunta",
    "email": "guntagopivardhan@gmail.com",
    "phone": "+1-234-564-0891",
    "location": "Tallahassee, FL",
    "linkedin": "linkedin.com/in/gopivardhan",
    "github": "github.com/GOPIVARDHAN1965",
    "portfolio": "gopivardhan1965.github.io/Portfoli0",
}

# ─────────────────────────────────────────────
# EDUCATION
# ─────────────────────────────────────────────
EDUCATION = [
    {
        "institution": "Florida State University",
        "location": "Tallahassee, FL",
        "degree": "Master of Science",
        "field": "Data Science",
        "gpa": "3.93",
        "end_date": "2025-05",
    },
    {
        "institution": "Gitam University",
        "location": "Visakhapatnam, India",
        "degree": "Bachelor of Technology",
        "field": "Computer Science",
        "gpa": "8.36",
        "end_date": "2023-05",
    },
]

# ─────────────────────────────────────────────
# CERTIFICATIONS
# ─────────────────────────────────────────────
CERTIFICATIONS = [
    {
        "name": "AWS Certified Cloud Practitioner",
        "issuer": "Amazon Web Services (AWS)",
        "issued": "2025-02",
        "expires": "2028-02",
        "credential_id": "b84a6b62136143cca23c1a034f3797cf",
        "verification_url": "aws.amazon.com/verification",
    },
    {
        "name": "Florida Certified Contract Manager (FCCM)",
        "issuer": "Florida Department of Management Services",
        "issued": "2025-12",
        "expires": "2030-12",
        "credential_id": "013179-25122",
        "verification_url": None,
    },
]

# ─────────────────────────────────────────────
# WORK EXPERIENCE
#
# NOTE: Each job has 15-20 bullets covering different angles.
# The scoring engine picks the best 4-6 per job based on the JD.
# More bullets = better tailoring. Do not cut these down.
# ─────────────────────────────────────────────
WORK_EXPERIENCE = [
    {
        "id": 1,
        "title": "Data Analyst",
        "company": "Florida Division of Emergency Management",
        "location": "Tallahassee, FL",
        "start_date": "2025-05",
        "end_date": None,
        "bullets": [

            # ── Power BI / BI Developer ──
            {
                "text": "Deployed 15+ Power BI semantic models bureau-wide using DAX, calculated columns, row-level security, and Power Query transformations, enabling self-service reporting for 50+ stakeholders without analyst intervention.",
                "keywords": "Power BI, DAX, Power Query, M, semantic model, row-level security, self-service reporting, KPI, BI developer, data visualization, reporting"
            },
            {
                "text": "Built SQL-driven KPI frameworks connecting live financial data sources to Power BI — enabling leadership to monitor multi-billion-dollar program operations, analyze performance, and track progress against objectives in real time.",
                "keywords": "Power BI, SQL, KPI, financial reporting, real-time, operations monitoring, executive reporting, BI reporting, dashboards"
            },
            {
                "text": "Collaborated with program managers and bureau stakeholders to gather reporting requirements, prioritize features, and translate operational needs into scalable Power BI solutions — reducing contract routing delays by 30%.",
                "keywords": "stakeholder management, requirements gathering, program manager, Power BI, agile, reporting, collaboration, BI developer, continuous improvement"
            },
            {
                "text": "Set up automated email alerts and SLA threshold monitoring tied to Power BI dashboards — notified 50+ stakeholders when deadlines were at risk, improving accountability and compliance without manual follow-up.",
                "keywords": "Power Automate, email automation, SLA, compliance, alerting, Power BI, accountability, monitoring, stakeholder management"
            },
            {
                "text": "Authored SOPs and technical documentation for all pipelines, dashboards, and reporting workflows, reviewed by bureau auditors and confirmed accurate and fully traceable across all financial data systems.",
                "keywords": "SOP, documentation, audit, compliance, data governance, traceability, agile, process documentation, reporting, government"
            },

            # ── ETL / Data Pipeline / Data Engineering ──
            {
                "text": "Built and maintained Python-based ETL pipelines ingesting 500K+ rows daily from authenticated .NET web portals, automating login flows and CSRF token handling via Selenium; scheduled via Windows Task Scheduler for zero-touch daily execution.",
                "keywords": "Python, Selenium, ETL, data pipeline, web scraping, automation, Windows Task Scheduler, .NET, CSRF, data ingestion, data engineering"
            },
            {
                "text": "Automated end-to-end ETL delivery of FLAIR and FOCUS financial datasets into SharePoint and OneDrive, cutting reconciliation turnaround from 30 days to under 30 minutes across multi-million dollar state contracts.",
                "keywords": "ETL, FLAIR, FOCUS, SharePoint, OneDrive, automation, reconciliation, financial data, government, data pipeline, data engineering"
            },
            {
                "text": "Wrote Python data validation scripts enforcing null checks, type consistency, date range validations, and source-to-target reconciliation before loading — maintaining data integrity and 99.9% accuracy across all downstream reports.",
                "keywords": "Python, data cleaning, data validation, data quality, deduplication, data integrity, ETL, preprocessing, data engineering, reconciliation"
            },
            {
                "text": "Served as sole technical owner of all pipelines, trackers, and automation systems — monitored for failures, diagnosed root causes, and deployed fixes independently, maintaining 99%+ uptime across critical financial data operations.",
                "keywords": "pipeline ownership, uptime, reliability, incident management, troubleshooting, autonomy, production support, data engineering"
            },

            # ── Database ──
            {
                "text": "Designed and maintained MySQL databases from scratch — defined schemas, primary/foreign keys, and indexes on high-query columns; implemented source-to-target reconciliation checks supporting 2M+ transaction records at 99.9% accuracy.",
                "keywords": "MySQL, database design, schema, indexing, foreign keys, reconciliation, data accuracy, relational database, SQL, data modeling"
            },

            # ── Federal Grants / FEMA / Grant Management ──
            {
                "text": "Tracked and reconciled federal grant expenditures across FEMA-funded disaster recovery programs, ensuring spend data aligned with grant award terms and federal reporting deadlines using FLAIR and FOCUS financial system data.",
                "keywords": "federal grants, FEMA, grant management, FLAIR, FOCUS, disaster recovery, reconciliation, federal funding, compliance, government finance"
            },
            {
                "text": "Built multi-year budget forecast models for federal disaster recovery programs using ARIMA and Prophet, projecting expenditure trajectories against grant award ceilings to help leadership avoid overruns and ensure timely federal fund drawdowns.",
                "keywords": "federal grants, budget forecasting, disaster recovery, FEMA, expenditure analysis, ARIMA, Prophet, grant management, federal funding, financial modeling, quantitative analyst"
            },
            {
                "text": "Developed State Management Cost trackers with burn rate analysis, churn breakdowns, and grant period forecasting — supporting federal reporting compliance and giving leadership real-time visibility into grant utilization across programs.",
                "keywords": "grant management, burn rate, federal grants, compliance reporting, cost tracking, FEMA, financial planning, federal funding, government, quantitative"
            },
            {
                "text": "Reconciled state-managed federal grant data against FLAIR/FOCUS financial records, identifying discrepancies between reimbursement requests and actual expenditures before federal reporting submission deadlines.",
                "keywords": "FLAIR, FOCUS, federal grants, reconciliation, grant compliance, financial data, government reporting, FEMA, audit, federal funding"
            },

            # ── Forecasting / Quantitative ──
            {
                "text": "Developed time-series forecasting models using ARIMA and Prophet to project statewide expenditure trends and disaster recovery costs, delivering quantitative budget estimates to executive leadership for multi-billion-dollar planning cycles.",
                "keywords": "ARIMA, Prophet, time series, forecasting, expenditure analysis, predictive analytics, financial modeling, Python, budget planning, quantitative analyst"
            },
            {
                "text": "Built Excel and VBA-based budget tools including burn rate calculators, churn breakdowns, and multi-year projection models used directly by executive leadership for billion-dollar state program management.",
                "keywords": "Excel, VBA, budget forecasting, burn rate, churn analysis, executive reporting, financial modeling, government finance, quantitative"
            },

            # ── Data Governance / Migration ──
            {
                "text": "Led a 2 TB data migration from network drives to SharePoint — SHA-256 checksum validation confirmed file integrity, deduplication removed 700 GB of redundant content, and a new data catalog and business glossary improved asset discoverability.",
                "keywords": "data migration, SharePoint, SHA-256, checksum, deduplication, data catalog, data governance, data management"
            },
            {
                "text": "Collaborated with finance, IT, and audit teams to document data flows, resolve cross-system discrepancies, and establish shared metric definitions — reducing confusion around financial KPIs across departments.",
                "keywords": "data governance, cross-functional, collaboration, finance, IT, audit, data documentation, business glossary, stakeholder management"
            },

            # ── Contract / Stakeholder ──
            {
                "text": "Built a Contract Routing Tracker that mapped every step of multi-million dollar approval workflows, flagged delays automatically, and gave managers a live bottleneck view — reducing average contract approval time by 30%.",
                "keywords": "contract management, FCCM, workflow tracking, bottleneck detection, process improvement, compliance, Power BI, automation, government contracts"
            },
            {
                "text": "Onboarded and trained 30+ non-technical users across finance, IT, and audit on Power BI dashboards — built reference guides, ran live walkthroughs, and handled follow-up to drive full adoption across the bureau.",
                "keywords": "training, user adoption, Power BI, stakeholder management, non-technical, communication, documentation, change management"
            },

            # ── Additional Federal Grants / Reconciliation / Azure ──
            {
                "text": "Designed and maintain a centralized reconciliation system tracking 150+ active federal grants across HMGP, non-disaster, and disaster recovery programs, validating daily FLAIR/FOCUS expenditures against award terms, funding ceilings, and program eligibility requirements.",
                "keywords": "federal grants, HMGP, grant management, FLAIR, FOCUS, reconciliation, disaster recovery, federal funding, FEMA, grant tracking, expenditure validation, compliance, 150 grants"
            },
            {
                "text": "Built automated transaction monitoring that flags expenditures posted to incorrect grant accounts in near real-time, generates transfer memo documentation, and routes corrections to finance staff before federal reporting deadlines.",
                "keywords": "transaction monitoring, grant misallocation, transfer memo, federal grants, automation, compliance, financial controls, anomaly detection, FLAIR, near real-time"
            },
            {
                "text": "Eliminated manual line-item review across 150+ grant accounts by implementing automated cross-grant anomaly detection, reducing misallocation errors and routing correction documentation to the appropriate teams without human triage.",
                "keywords": "automation, grant management, anomaly detection, financial controls, federal grants, manual process elimination, compliance, reconciliation, 150 grants"
            },
            {
                "text": "Architected a Python and Azure Blob Storage data lake to store and version FLAIR/FOCUS financial extracts, supporting historical reprocessing, audit trail maintenance, and cross-period reconciliation independent of source system availability.",
                "keywords": "Azure Blob Storage, Azure, data lake, Python, FLAIR, FOCUS, data architecture, versioning, audit trail, historical data, cloud storage, data engineering"
            },
            {
                "text": "Engineered end-to-end data pipelines from FLAIR/FOCUS through Azure Blob Storage to Power BI, fully automated and built from scratch on greenfield infrastructure with no prior systems to build on.",
                "keywords": "Azure Blob Storage, Azure, Python, ETL, data pipeline, Power BI, FLAIR, FOCUS, data engineering, cloud, end-to-end, greenfield"
            },
            {
                "text": "Developed the expenditure analysis and variance modeling that bureau leadership used to construct federal budget incremental justification documents, translating multi-grant spending trends into quantitative narratives reviewed by the director and division heads.",
                "keywords": "budget incremental, executive reporting, director, bureau leadership, financial modeling, variance analysis, federal budget, quantitative analysis, expenditure analysis"
            },
            {
                "text": "Regularly presented reconciliation findings, dashboard walkthroughs, and financial summaries directly to the bureau director and division heads, distilling 150+ grant program data into actionable decision support.",
                "keywords": "executive presentation, director, bureau leadership, stakeholder management, communication, dashboard, financial reporting, decision support"
            },
            {
                "text": "Own and operate a live reconciliation dashboard refreshing daily across all active grants, surfacing budget incremental status, flagging transactions routed to incorrect accounts, and identifying transfer memo needs, serving as the bureau's primary financial control instrument.",
                "keywords": "reconciliation dashboard, Power BI, daily refresh, budget incremental, grant management, financial controls, automation, real-time monitoring, FLAIR, FOCUS, 150 grants"
            },
        ]
    },

    {
        "id": 2,
        "title": "Data & Finance Analyst",
        "company": "Aramark",
        "location": "Tallahassee, FL",
        "start_date": "2023-11",
        "end_date": "2025-05",
        "bullets": [
            {
                "text": "Built 10+ Power BI dashboards covering 25+ KPIs across $35M+ in operations — included DAX measures, drill-through pages, and real-time data connections so leadership could analyze financials without waiting on manual reports.",
                "keywords": "Power BI, DAX, KPI, dashboards, financial monitoring, real-time reporting, drill-through, data visualization, BI developer, semantic model"
            },
            {
                "text": "Built Python and SQL ETL pipelines to generate automated sales and revenue reports across $35M+ in annual transactions; trend analysis surfaced key revenue drivers and contributed to a 20% improvement in forecasting accuracy.",
                "keywords": "Python, SQL, ETL, revenue analysis, trend analysis, forecasting, sales reporting, financial analysis, automation, data engineering"
            },
            {
                "text": "Handled weekly financial operations covering $500K+ in AP/AR, invoice processing, and account reconciliations; automated invoice tracking using Power Automate and SQL, cutting processing delays by 30%.",
                "keywords": "AP/AR, invoicing, reconciliation, Power Automate, SQL, cash flow, financial operations, automation, accounts payable"
            },
            {
                "text": "Owned month-end close activities including variance analysis, account reconciliation, and forecast updates — standardized templates and automated repetitive data pulls to reduce close cycle friction.",
                "keywords": "month-end close, variance analysis, reconciliation, financial forecasting, reporting, accounting, automation, financial close"
            },
            {
                "text": "Produced monthly AR aging snapshots surfacing outstanding invoices and collection status, giving finance leadership consistent visibility into receivables across all accounts.",
                "keywords": "accounts receivable, AR aging, invoicing, collections, payment tracking, financial reporting"
            },
            {
                "text": "Replaced manual reconciliation workflows with Excel VBA macros, cutting weekly reconciliation time by 40% and eliminating formula errors that had caused prior reporting discrepancies.",
                "keywords": "Excel, VBA, macros, automation, reconciliation, workflow optimization, manual effort reduction, financial reporting"
            },
            {
                "text": "Built standardized invoice generation templates in Excel that auto-populated line items from source data, reducing manual entry and improving billing turnaround consistency.",
                "keywords": "Excel, invoice automation, billing, templates, automation, efficiency, financial operations"
            },
            {
                "text": "Generated and distributed daily sales variance reports giving operations managers a quantitative view of performance versus plan each morning.",
                "keywords": "sales reporting, daily reporting, variance analysis, operations, revenue tracking, financial analysis, quantitative"
            },
        ]
    },

    {
        "id": 3,
        "title": "Finance Analyst",
        "company": "Sravanthi Engineers",
        "location": "India",
        "start_date": "2021-07",
        "end_date": "2023-06",
        "bullets": [
            {
                "text": "Managed end-to-end AP/AR and invoicing across multiple simultaneous engineering projects — tracked payment milestones, followed up on overdue accounts, and maintained cash flow visibility for project leadership.",
                "keywords": "AP/AR, invoicing, payment tracking, billing, cash flow, project finance, engineering"
            },
            {
                "text": "Performed tender analysis and built detailed cost estimates for work orders, breaking down material, labor, and overhead to produce competitive bids and accurate project budgets.",
                "keywords": "cost estimation, tender analysis, budgeting, pricing, financial planning, work orders, project costing, quantitative"
            },
            {
                "text": "Filed GST returns and maintained compliance records on schedule, ensuring statutory deadlines were met without penalties.",
                "keywords": "GST, tax compliance, statutory reporting, financial compliance, record keeping"
            },
            {
                "text": "Allocated costs across active contracts and produced management reporting with a clear breakdown of spend versus budget on every project.",
                "keywords": "cost allocation, cost tracking, forecasting, project reporting, financial reporting, budget management"
            },
            {
                "text": "Prepared site measurement reports reconciling estimated versus actual material and labor usage — data used to settle contractor disputes and calibrate future cost estimates.",
                "keywords": "reporting, validation, materials management, labor tracking, engineering, cost reconciliation, site reporting"
            },
        ]
    },

    {
        "id": 4,
        "title": "Software Engineering Intern",
        "company": "ZAWN",
        "location": "Ottawa, Canada (Remote)",
        "start_date": "2021-02",
        "end_date": "2021-04",
        "bullets": [
            {
                "text": "Diagnosed and resolved slow MongoDB queries in high-traffic collections — added compound indexes, restructured aggregation pipelines, and rewrote query logic, bringing API response times down by 40%.",
                "keywords": "MongoDB, query optimization, indexing, aggregation pipeline, API performance, database optimization, NoSQL, backend"
            },
            {
                "text": "Built and integrated frontend components including profile avatar upload and dropdown navigation — improvements contributed to a 15% lift in user engagement post-release.",
                "keywords": "UI, frontend, user engagement, UX, JavaScript, product improvement, web development"
            },
            {
                "text": "Traced recurring bugs in alert and complaint submission flows, wrote detailed issue reports with reproduction steps, and worked with the dev team to resolve root causes responsible for 30% of customer complaints.",
                "keywords": "QA, bug tracking, documentation, customer satisfaction, quality assurance, testing, workflow analysis"
            },
            {
                "text": "Wrote automated regression test scripts in Selenium and PyTest, reducing manual testing burden per release and improving release confidence.",
                "keywords": "Selenium, PyTest, automated testing, QA, test automation, software quality, regression testing"
            },
        ]
    },
]

# ─────────────────────────────────────────────
# PROJECTS
# ─────────────────────────────────────────────
PROJECTS = [
    {
        "id": 1,
        "name": "Retrieval-Augmented Generation (RAG) PDF Query System",
        "github_url": "https://github.com/GOPIVARDHAN1965/rag_ollama_project",
        "bullets": [
            {
                "text": "Built a local RAG pipeline using Ollama and vector embeddings — users query large PDFs through a terminal interface and get context-grounded answers retrieved from the most relevant document chunks before generation.",
                "keywords": "RAG, LangChain, vector embeddings, Ollama, semantic search, NLP, LLM, document retrieval, Python, generative AI, AI"
            },
            {
                "text": "Built a Flask REST API wrapper around the RAG pipeline, exposing document query functionality as an HTTP endpoint for integration with frontends and external tools.",
                "keywords": "Flask, REST API, Python, backend, API development, web development, RAG, NLP, LLM integration"
            },
            {
                "text": "Implemented FAISS-based embedding indexing and chunk overlap tuning to keep retrieval fast and accurate on locally run models with no cloud dependency.",
                "keywords": "FAISS, vector embeddings, indexing, document chunking, Python, NLP, information retrieval, local LLM, scalability"
            },
            {
                "text": "Handled PDF preprocessing including text extraction, noise removal, and metadata stripping to improve retrieval accuracy on dense government and technical documents.",
                "keywords": "data preprocessing, PDF processing, Python, NLP, text extraction, document processing"
            },
        ]
    },
    {
        "id": 2,
        "name": "Tally Code Brewers Hackathon — Quiz Platform (Semifinalist)",
        "github_url": "https://github.com/Bidisha28/TallyCode-QuizCreationPlatform",
        "bullets": [
            {
                "text": "Built a full-stack quiz platform in Flask and MongoDB under hackathon time pressure — dynamic question loading, real-time scoring, per-user unique links, and re-attempt blocking; placed semifinalist among 200+ teams.",
                "keywords": "Flask, MongoDB, Python, backend, real-time, security, hackathon, full-stack, web development, scalability"
            },
            {
                "text": "Built and exposed RESTful API endpoints for quiz creation, attempt submission, and score retrieval — consumed by the frontend for real-time updates.",
                "keywords": "REST API, Flask, Python, API development, backend, web development, real-time, endpoints"
            },
            {
                "text": "Designed a flexible MongoDB data model supporting variable point values, time-limited link activation, and per-user access control without hardcoding quiz-specific logic.",
                "keywords": "data modeling, MongoDB, access control, Flask, Python, schema design, security, NoSQL"
            },
            {
                "text": "Stress-tested concurrent quiz submissions and tuned backend query patterns to handle load without score drops or duplicate entries.",
                "keywords": "backend optimization, concurrency, performance, scalability, load testing, MongoDB, system reliability"
            },
        ]
    },
    {
        "id": 3,
        "name": "Shopping Recommendation and Sentiment Analysis Systems",
        "github_url": "https://github.com/GOPIVARDHAN1965/final_sem_project",
        "bullets": [
            {
                "text": "Built a KNN-based product recommendation model on purchase history data — surfaced complementary product suggestions that improved cross-sell opportunity identification by 25%.",
                "keywords": "machine learning, KNN, recommendation system, Scikit-learn, Python, data analysis, e-commerce"
            },
            {
                "text": "Trained a TF-IDF + Scikit-learn text classifier on restaurant review data, reaching 88% accuracy in sentiment labeling with output feeding a reporting layer for service quality trend analysis.",
                "keywords": "NLP, sentiment analysis, TF-IDF, Scikit-learn, machine learning, text classification, Python, accuracy"
            },
            {
                "text": "Wrapped both models in a Flask REST API and built automated reporting generating spend analysis summaries and live sentiment scores on demand for business stakeholders.",
                "keywords": "Flask, REST API, Python, automation, reporting, marketing analytics, business intelligence, API development"
            },
        ]
    },
    {
        "id": 4,
        "name": "Interactive COVID-19 Dashboard",
        "github_url": "https://github.com/GOPIVARDHAN1965",
        "bullets": [
            {
                "text": "Built a Dash + Plotly dashboard pulling live COVID-19 data via public APIs, visualizing case trends, regional breakdowns, and time-series trajectories with interactive filters for country and date range.",
                "keywords": "Dash, Plotly, data visualization, dashboard, Python, real-time, KPI, API integration, time series, public health"
            },
            {
                "text": "Structured the API integration layer to handle upstream schema changes gracefully and automated data refresh to keep the dashboard current without manual updates.",
                "keywords": "API, automation, data pipeline, dynamic updates, Python, data engineering, Dash, ETL"
            },
        ]
    },
]

# ─────────────────────────────────────────────
# SKILLS
# ─────────────────────────────────────────────
SKILLS = [
    # Languages
    {"name": "Python",              "category": "Languages",            "proficiency": "Advanced"},
    {"name": "SQL",                 "category": "Languages",            "proficiency": "Advanced"},
    {"name": "DAX",                 "category": "Languages",            "proficiency": "Advanced"},
    {"name": "M (Power Query)",     "category": "Languages",            "proficiency": "Advanced"},
    {"name": "VBA",                 "category": "Languages",            "proficiency": "Intermediate"},
    {"name": "R",                   "category": "Languages",            "proficiency": "Intermediate"},
    {"name": "Java",                "category": "Languages",            "proficiency": "Intermediate"},
    {"name": "JavaScript",          "category": "Languages",            "proficiency": "Intermediate"},
    {"name": "C++",                 "category": "Languages",            "proficiency": "Intermediate"},

    # Frameworks & APIs
    {"name": "Flask",               "category": "Frameworks & APIs",    "proficiency": "Advanced"},
    {"name": "REST APIs",           "category": "Frameworks & APIs",    "proficiency": "Advanced"},
    {"name": "FastAPI",             "category": "Frameworks & APIs",    "proficiency": "Intermediate"},
    {"name": "Streamlit",           "category": "Frameworks & APIs",    "proficiency": "Intermediate"},
    {"name": "Dash",                "category": "Frameworks & APIs",    "proficiency": "Intermediate"},
    {"name": "Next.js",             "category": "Frameworks & APIs",    "proficiency": "Intermediate"},

    # Databases
    {"name": "MySQL",               "category": "Databases",            "proficiency": "Advanced"},
    {"name": "SQL Server",          "category": "Databases",            "proficiency": "Advanced"},
    {"name": "SQLite",              "category": "Databases",            "proficiency": "Intermediate"},
    {"name": "PostgreSQL",          "category": "Databases",            "proficiency": "Intermediate"},
    {"name": "MongoDB",             "category": "Databases",            "proficiency": "Intermediate"},
    {"name": "Snowflake",           "category": "Databases",            "proficiency": "Intermediate"},

    # BI & Analytics
    {"name": "Power BI",            "category": "BI & Analytics",       "proficiency": "Advanced"},
    {"name": "Power Query",         "category": "BI & Analytics",       "proficiency": "Advanced"},
    {"name": "Power Automate",      "category": "BI & Analytics",       "proficiency": "Advanced"},
    {"name": "Excel",               "category": "BI & Analytics",       "proficiency": "Advanced"},
    {"name": "ETL Pipelines",       "category": "BI & Analytics",       "proficiency": "Advanced"},
    {"name": "Data Modeling",       "category": "BI & Analytics",       "proficiency": "Advanced"},
    {"name": "Semantic Models",     "category": "BI & Analytics",       "proficiency": "Advanced"},
    {"name": "KPI Development",     "category": "BI & Analytics",       "proficiency": "Advanced"},
    {"name": "Plotly",              "category": "BI & Analytics",       "proficiency": "Intermediate"},

    # ML & AI
    {"name": "ARIMA",               "category": "ML & AI",              "proficiency": "Advanced"},
    {"name": "Prophet",             "category": "ML & AI",              "proficiency": "Advanced"},
    {"name": "Scikit-learn",        "category": "ML & AI",              "proficiency": "Intermediate"},
    {"name": "TF-IDF",              "category": "ML & AI",              "proficiency": "Intermediate"},
    {"name": "NLP",                 "category": "ML & AI",              "proficiency": "Intermediate"},
    {"name": "LangChain",           "category": "ML & AI",              "proficiency": "Intermediate"},
    {"name": "RAG",                 "category": "ML & AI",              "proficiency": "Intermediate"},
    {"name": "Vector Embeddings",   "category": "ML & AI",              "proficiency": "Intermediate"},
    {"name": "PyTorch",             "category": "ML & AI",              "proficiency": "Intermediate"},
    {"name": "TensorFlow",          "category": "ML & AI",              "proficiency": "Intermediate"},
    {"name": "Hugging Face",        "category": "ML & AI",              "proficiency": "Intermediate"},
    {"name": "Pinecone",            "category": "ML & AI",              "proficiency": "Intermediate"},

    # Cloud & DevOps
    {"name": "AWS",                 "category": "Cloud & DevOps",       "proficiency": "Intermediate"},
    {"name": "GCP",                 "category": "Cloud & DevOps",       "proficiency": "Intermediate"},
    {"name": "Azure",               "category": "Cloud & DevOps",       "proficiency": "Intermediate"},
    {"name": "Docker",              "category": "Cloud & DevOps",       "proficiency": "Intermediate"},
    {"name": "Kubernetes",          "category": "Cloud & DevOps",       "proficiency": "Intermediate"},
    {"name": "CI/CD",               "category": "Cloud & DevOps",       "proficiency": "Intermediate"},
    {"name": "Terraform",           "category": "Cloud & DevOps",       "proficiency": "Beginner"},

    # Tools
    {"name": "Git",                 "category": "Tools",                "proficiency": "Advanced"},
    {"name": "GitHub",              "category": "Tools",                "proficiency": "Advanced"},
    {"name": "SharePoint",          "category": "Tools",                "proficiency": "Advanced"},
    {"name": "Windows Task Scheduler", "category": "Tools",            "proficiency": "Advanced"},
    {"name": "Selenium",            "category": "Tools",                "proficiency": "Intermediate"},
    {"name": "PyTest",              "category": "Tools",                "proficiency": "Intermediate"},
]

# ─────────────────────────────────────────────
# ACHIEVEMENTS
# ─────────────────────────────────────────────
ACHIEVEMENTS = [
    {"title": "Ranked 1st",     "description": "IIT Madras HackerRank Competition"},
    {"title": "Ranked 3rd",     "description": "Gitam HackerEarth Competition"},
    {"title": "Semifinalist",   "description": "Tally Code Brewers Hackathon — among 200+ participants"},
]


# ═══════════════════════════════════════════════════════════════════════════════
# CURSOR PROMPT
# Copy everything below and paste into Cursor chat.
# ═══════════════════════════════════════════════════════════════════════════════
CURSOR_PROMPT = """
Do all of the following in one go:

─── 1. FIX DATE FORMATTING BUG IN resume_template.js ───
The job title and date are running together with no space
(e.g., "Data AnalystMay 2025 – Present"). Fix the separator so it renders as:
"Florida Division of Emergency Management, Data Analyst | May 2025 – Present"
There must be a space and pipe character between title and date on the same line.

─── 2. UPGRADE THE SCORING ENGINE (src/scoring.py or src/generator.py) ───
The current single-keyword matcher is too basic. Replace it with this:

a) PHRASE MATCHING: extract bigrams and trigrams from the job description
   so "Power BI", "semantic model", "grant management", "federal funding"
   match as phrases, not just individual words.

b) SYNONYM EXPANSION: add a SYNONYM_MAP so related terms score together.
   Use at minimum:
   {
     "business intelligence": ["power bi", "bi reporting", "dashboards", "tableau"],
     "federal grants": ["federal funding", "flair", "focus", "grant management", "fema", "disaster recovery"],
     "machine learning": ["ml", "scikit-learn", "pytorch", "tensorflow", "model training"],
     "data warehouse": ["snowflake", "sql server", "redshift", "bigquery", "data mart"],
     "etl": ["data pipeline", "data ingestion", "data engineering", "airflow"],
     "agile": ["scrum", "sprint", "jira", "iterative", "continuous improvement"],
     "api": ["rest api", "flask", "fastapi", "endpoint", "http", "web service"],
     "visualization": ["power bi", "tableau", "plotly", "dash", "dashboard", "charts"],
     "quantitative": ["arima", "prophet", "forecasting", "statistical", "time series"],
     "self-service": ["power bi", "reporting", "dashboard", "end-user reporting"],
   }

c) RECENCY BONUS: multiply bullet scores by 1.15 for current job, 
   1.0 for previous job, 0.85 for older jobs.

d) SKILL RELEVANCE: filter the skills list to show only categories
   that have keywords matching the job description. If the JD is pure BI,
   don't show the full ML & AI section.

─── 3. ADD ATS SCORE PANEL TO THE STREAMLIT GENERATOR PAGE ───
After the user pastes a JD and clicks Generate:

a) Calculate ATS score = matched_keywords / total_jd_keywords * 100
   Show as a labeled progress bar with color:
   - >= 75%: green
   - 50-74%: yellow / orange  
   - < 50%: red

b) Show two columns below the score:
   LEFT  → "Matched Keywords" as green st.badge / colored chips
   RIGHT → "Missing Keywords" as red chips (these are gaps to address)

c) Add a "Score Breakdown" st.expander showing:
   - Match % per section: Experience, Projects, Skills
   - Top 5 selected bullets with their relevance score shown

─── 4. CLEAN UP THE UI ───
- White background only, remove all dark mode
- Top horizontal tab navigation: Generator | Profile | Applications | Settings
- Generator page layout: centered text area (full width) → Generate button →
  ATS score panel → Download .docx button, in that vertical order
- Profile page: clean simple forms, editable tables, no dashboard clutter
- Applications tracker: clean table with colored status badges
  (Applied=blue, Interview=yellow, Offer=green, Rejected=gray)
"""
