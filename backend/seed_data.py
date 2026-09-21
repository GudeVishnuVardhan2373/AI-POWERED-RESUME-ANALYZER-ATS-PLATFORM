from sqlalchemy.orm import Session
from .models import JobPosting, CandidateResume, ResumeAnalysis
from .analyzer import analyze_resume_against_job

SAMPLE_JOBS = [
    {
        "title": "Fullstack Python & React Developer",
        "department": "Software Engineering",
        "experience_level": "Mid-Level (2-4 Years)",
        "description": "We are seeking an experienced Fullstack Developer to build and maintain scalable web applications. You will be responsible for creating robust RESTful APIs using Python (FastAPI/Django), developing modern interactive frontend components in React, and optimizing PostgreSQL database queries. Experience with Docker, Git version control, and CI/CD pipelines is required.",
        "required_skills": ["Python", "FastAPI", "React", "JavaScript", "PostgreSQL", "Docker", "Git", "REST API"],
        "preferred_skills": ["TypeScript", "Redis", "Tailwind CSS", "Kubernetes"]
    },
    {
        "title": "AI / Machine Learning Engineer",
        "department": "Artificial Intelligence",
        "experience_level": "Senior (4+ Years)",
        "description": "Join our AI research and development team to build cutting-edge Generative AI and Machine Learning solutions. You will design, train, and deploy deep learning models using PyTorch and Hugging Face, optimize NLP pipelines, implement RAG (Retrieval-Augmented Generation) architectures, and work with Python data science stacks including Pandas and NumPy.",
        "required_skills": ["Python", "Machine Learning", "Deep Learning", "PyTorch", "NLP", "Generative AI", "Pandas", "Git"],
        "preferred_skills": ["LangChain", "Docker", "AWS", "TensorFlow", "Prompt Engineering"]
    },
    {
        "title": "Cloud & DevOps Infrastructure Engineer",
        "department": "Platform & Cloud Operations",
        "experience_level": "Mid to Senior (3-5 Years)",
        "description": "We are looking for a DevOps Engineer to automate and scale our cloud infrastructure. You will manage containerized microservices using Docker and Kubernetes, build resilient CI/CD pipelines via GitHub Actions, provision infrastructure with Terraform, and monitor AWS cloud environments using Linux shell scripting.",
        "required_skills": ["AWS", "Docker", "Kubernetes", "Linux", "CI/CD", "Terraform", "GitHub Actions", "Bash"],
        "preferred_skills": ["Python", "Prometheus", "Grafana", "Nginx"]
    },
    {
        "title": "Data Analyst & Business Intelligence",
        "department": "Data & Analytics",
        "experience_level": "Entry to Mid (1-3 Years)",
        "description": "Looking for a driven Data Analyst to analyze large datasets and deliver actionable intelligence. Proficient with advanced SQL queries, Python data analysis with Pandas, and dashboard creation in Power BI or Tableau. Must possess strong analytical thinking, problem solving, and cross-functional communication skills.",
        "required_skills": ["SQL", "Python", "Pandas", "Power BI", "Tableau", "Data Analysis", "Communication"],
        "preferred_skills": ["PostgreSQL", "Excel", "Machine Learning", "Problem Solving"]
    }
]

SAMPLE_CANDIDATE_RESUME = """
ALEXANDER MORGAN
Email: alex.morgan.dev@example.com | Phone: +1 (555) 234-5678
LinkedIn: linkedin.com/in/alexmorgan-dev | GitHub: github.com/alexmorgan-code
San Francisco, CA

PROFESSIONAL SUMMARY
Dynamic and results-driven Software Engineer with 3+ years of experience in designing, building, and deploying scalable web applications and REST APIs. Proficient in Python, FastAPI, React, JavaScript, and relational databases. Adept at agile collaboration and automated testing.

TECHNICAL SKILLS
- Programming Languages: Python, JavaScript, TypeScript, SQL, HTML5, CSS3
- Frameworks & Libraries: FastAPI, Flask, React.js, Tailwind CSS, Redux
- Databases: PostgreSQL, SQLite, Redis
- DevOps & Tools: Docker, Git, GitHub Actions, Linux, Postman, Jest, PyTest

PROFESSIONAL EXPERIENCE
Software Engineer | NexaTech Solutions (2022 - Present)
- Architected and engineered high-throughput REST APIs using Python and FastAPI, serving over 150,000 active users.
- Built responsive single-page web applications with React and Tailwind CSS, reducing load times by 35%.
- Optimized complex PostgreSQL database queries and implemented Redis caching, boosting query performance by 40%.
- Automated CI/CD build and testing pipelines using GitHub Actions and Docker containerization.
- Collaborated with cross-functional teams in daily Agile Scrum meetings to deliver features on sprint schedules.

Junior Web Developer | Apex Digital (2021 - 2022)
- Developed client-facing web pages and landing pages using JavaScript, HTML5, and CSS.
- Implemented unit tests using PyTest and Jest to ensure 90%+ code coverage.
- Participated in code reviews and resolved critical customer-reported bugs.

EDUCATION
Bachelor of Technology (B.Tech) in Computer Science & Engineering
Apex University (Graduated 2021)
"""

def seed_database(db: Session):
    """Seed initial job postings and a benchmark sample candidate if tables are empty."""
    # Seed Job Postings
    existing_jobs = db.query(JobPosting).count()
    if existing_jobs == 0:
        for job_data in SAMPLE_JOBS:
            job = JobPosting(
                title=job_data["title"],
                department=job_data["department"],
                experience_level=job_data["experience_level"],
                description=job_data["description"],
                required_skills=job_data["required_skills"],
                preferred_skills=job_data["preferred_skills"]
            )
            db.add(job)
        db.commit()
        print("[DB Seed] Seeded sample job postings successfully.")

    # Seed Sample Candidate if empty
    existing_candidates = db.query(CandidateResume).count()
    if existing_candidates == 0:
        target_job = db.query(JobPosting).first()
        if target_job:
            from .parser import parse_candidate_profile
            from .analyzer import extract_skills

            profile = parse_candidate_profile(SAMPLE_CANDIDATE_RESUME, "alex_morgan_resume.txt")
            skills_dict = extract_skills(SAMPLE_CANDIDATE_RESUME)

            candidate = CandidateResume(
                candidate_name=profile["candidate_name"],
                email=profile["email"],
                phone=profile["phone"],
                filename="sample_alex_morgan_resume.pdf",
                filepath="uploads/sample_alex_morgan_resume.pdf",
                raw_text=SAMPLE_CANDIDATE_RESUME.strip(),
                extracted_skills=skills_dict,
                experience_years=profile["experience_years"],
                education=profile["education"],
                links=profile["links"]
            )
            db.add(candidate)
            db.commit()
            db.refresh(candidate)

            # Analyze candidate against target job
            analysis_data = analyze_resume_against_job(
                resume_text=candidate.raw_text,
                job_description=target_job.description,
                job_required_skills=target_job.required_skills
            )

            analysis = ResumeAnalysis(
                resume_id=candidate.id,
                job_id=target_job.id,
                job_title=target_job.title,
                overall_score=analysis_data["overall_score"],
                skills_score=analysis_data["skills_score"],
                experience_score=analysis_data["experience_score"],
                ats_score=analysis_data["ats_score"],
                domain_score=analysis_data["domain_score"],
                matched_skills=analysis_data["matched_skills"],
                missing_skills=analysis_data["missing_skills"],
                suggestions=analysis_data["suggestions"],
                ats_details=analysis_data["ats_details"],
                status="Shortlisted"
            )
            db.add(analysis)
            db.commit()
            print("[DB Seed] Seeded sample benchmark candidate analysis.")
