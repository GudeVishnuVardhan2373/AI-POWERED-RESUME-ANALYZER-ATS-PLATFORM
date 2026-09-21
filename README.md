# AI-Powered Resume Analyzer (Fullstack Application)

An intelligent, fullstack AI Resume Analysis, ATS Compliance, and Recruiter CRM dashboard built with **FastAPI**, **SQLAlchemy ORM (SQLite)**, and a modern **HTML5 / Tailwind CSS / Chart.js** frontend.

---

## Key Features

1. **Resume Ingestion & Parsing**:
   - Accepts **PDF**, **DOCX**, and **TXT** files.
   - Automatically extracts candidate name, contact email, phone number, portfolio/GitHub/LinkedIn links, experience years, and recognized degrees.

2. **500+ Skill Extraction & Categorization**:
   - Automatically parses and categorizes technical skills into:
     - **Programming Languages** (Python, Java, TypeScript, C++, Rust, Go, SQL, etc.)
     - **Frontend Frameworks & UI** (React, Next.js, Vue, Tailwind CSS, Redux, etc.)
     - **Backend & APIs** (FastAPI, Express, Django, Spring Boot, Microservices, etc.)
     - **Databases & Caching** (PostgreSQL, MySQL, MongoDB, Redis, etc.)
     - **Cloud & DevOps** (AWS, Docker, Kubernetes, CI/CD, Terraform, etc.)
     - **AI, ML & Data Science** (PyTorch, TensorFlow, LLMs, Generative AI, RAG, etc.)
     - **Tools & Methodologies** (Git, Jira, Agile, PyTest, Docker Compose, etc.)
     - **Soft Skills** (Leadership, Communication, Problem Solving, etc.)

3. **Job Description Matching & AI Scoring**:
   - Algorithmic multi-factor scoring model (0 - 100%):
     - **40% Technical Skills Coverage**: exact required skill intersection.
     - **20% Domain & Contextual Fit**: pure Python TF-IDF vector cosine similarity.
     - **20% ATS Readability & Contact Completeness**: validates email, phone, links, action verb density, and word count.
     - **20% Experience Alignment**: compares candidate seniority with job requirements.

4. **Missing-Skill Suggestions & Learning Path**:
   - Identifies high-priority missing skills absent from the candidate's resume.
   - Provides targeted online courses, certifications, and bullet-point phrasing advice.

5. **Admin / Recruiter Dashboard (CRM)**:
   - Real-time KPI summary (Total Submissions, Average Match Score, Shortlist rate).
   - Candidate table with live search, score filter, and status update (`Shortlisted`, `Under Review`, `Interview`, `Rejected`).
   - Detailed candidate modal with raw parsed resume text and matched/missing skills.
   - Job Openings Manager: Create, inspect, and delete custom job postings.
   - Talent Intelligence Charts: Score distribution and in-demand skills visualization.

---

## Directory Structure

```
ai-resume-analyzer/
│
├── backend/
│   ├── __init__.py
│   ├── database.py       # SQLAlchemy SQLite configuration & session
│   ├── models.py         # Relational DB models (CandidateResume, JobPosting, ResumeAnalysis)
│   ├── schemas.py        # Pydantic schemas for request/response validation
│   ├── parser.py         # Multi-format text extractor & regex contact parser
│   ├── analyzer.py       # 500+ skill taxonomy, TF-IDF cosine similarity, ATS heuristics
│   ├── seed_data.py      # Pre-populates sample job openings and benchmark candidates
│   ├── main.py           # FastAPI application, CORS, static routes, and REST endpoints
│   └── tests.py          # Unit test suite
│
├── frontend/
│   ├── index.html        # Single-page application (Analyzer, Admin CRM, Jobs, Analytics)
│   ├── css/
│   │   └── style.css     # Glassmorphism, glowing badges, custom scrollbars, animations
│   └── js/
│       └── app.js        # Dynamic UI controller, drag & drop, Chart.js graphs, REST calls
│
├── database/             # Stores SQLite database (resume_analyzer.db)
├── uploads/              # Uploaded resume files storage
├── requirements.txt      # Python dependencies
├── run.py                # Server launcher script
└── README.md
```

---

## How to Run

1. Open your terminal in the project directory:
   ```bash
   cd c:\4-1\ai-resume-analyzer
   ```

2. Run the application:
   ```bash
   python run.py
   ```

3. Open your browser:
   - **Web Application**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - **Interactive API Documentation (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
