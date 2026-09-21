import os
import shutil
import uuid
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from .database import engine, Base, get_db
from .models import JobPosting, CandidateResume, ResumeAnalysis
from .schemas import (
    JobPostingCreate, JobPostingResponse,
    ResumeAnalysisResponse, CandidateSummary, CandidateDetail,
    StatusUpdate, DashboardAnalytics
)
from .parser import extract_text_from_file, parse_candidate_profile
from .analyzer import extract_skills, analyze_resume_against_job
from .seed_data import seed_database

# Create tables
Base.metadata.create_all(bind=engine)

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="AI-Powered Resume Analyzer",
    description="Fullstack ATS & AI Resume Analysis Platform with Recruiter Dashboard",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup: seed sample data if tables empty
@app.on_event("startup")
def startup_populate_data():
    db = next(get_db())
    try:
        seed_database(db)
    finally:
        db.close()


# ---------------- API ROUTES ----------------

# 1. Analyze Resume Endpoint
@app.post("/api/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume_endpoint(
    file: UploadFile = File(...),
    job_id: Optional[int] = Form(None),
    custom_job_title: Optional[str] = Form(None),
    custom_job_description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    # Validate extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in [".pdf", ".docx", ".doc", ".txt"]:
        raise HTTPException(status_code=400, detail="Allowed file types: PDF, DOCX, TXT")

    # Generate unique filename and save
    unique_filename = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    saved_filepath = os.path.join(UPLOAD_DIR, unique_filename)
    with open(saved_filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text and profile
    raw_text = extract_text_from_file(saved_filepath)
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from file. Please ensure it is not an image-only scan.")

    profile = parse_candidate_profile(raw_text, file.filename)
    extracted_skills_dict = extract_skills(raw_text)

    # Determine Job Context
    job_title = "Custom Job Description"
    job_description = ""
    required_skills = []

    if job_id:
        target_job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
        if target_job:
            job_title = target_job.title
            job_description = target_job.description
            required_skills = target_job.required_skills or []
    elif custom_job_description and custom_job_description.strip():
        job_description = custom_job_description.strip()
        job_title = custom_job_title.strip() if (custom_job_title and custom_job_title.strip()) else "Custom Role"
    else:
        # Fallback to first job in db if none chosen
        target_job = db.query(JobPosting).first()
        if target_job:
            job_id = target_job.id
            job_title = target_job.title
            job_description = target_job.description
            required_skills = target_job.required_skills or []

    # Run Analysis
    analysis_result = analyze_resume_against_job(
        resume_text=raw_text,
        job_description=job_description,
        job_required_skills=required_skills
    )

    # Persist Candidate
    candidate = CandidateResume(
        candidate_name=profile["candidate_name"],
        email=profile["email"],
        phone=profile["phone"],
        filename=file.filename,
        filepath=saved_filepath,
        raw_text=raw_text,
        extracted_skills=extracted_skills_dict,
        experience_years=profile["experience_years"],
        education=profile["education"],
        links=profile["links"]
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    # Persist Analysis
    analysis = ResumeAnalysis(
        resume_id=candidate.id,
        job_id=job_id,
        job_title=job_title,
        overall_score=analysis_result["overall_score"],
        skills_score=analysis_result["skills_score"],
        experience_score=analysis_result["experience_score"],
        ats_score=analysis_result["ats_score"],
        domain_score=analysis_result["domain_score"],
        matched_skills=analysis_result["matched_skills"],
        missing_skills=analysis_result["missing_skills"],
        suggestions=analysis_result["suggestions"],
        ats_details=analysis_result["ats_details"],
        status="Under Review"
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return ResumeAnalysisResponse(
        id=analysis.id,
        resume_id=candidate.id,
        candidate_name=candidate.candidate_name,
        email=candidate.email,
        phone=candidate.phone,
        job_id=job_id,
        job_title=job_title,
        overall_score=analysis.overall_score,
        skills_score=analysis.skills_score,
        experience_score=analysis.experience_score,
        ats_score=analysis.ats_score,
        domain_score=analysis.domain_score,
        matched_skills=analysis.matched_skills,
        missing_skills=analysis.missing_skills,
        suggestions=analysis.suggestions,
        ats_details=analysis.ats_details,
        status=analysis.status,
        created_at=analysis.created_at
    )


# 2. Job Postings Endpoints
@app.get("/api/jobs", response_model=List[JobPostingResponse])
def get_job_postings(db: Session = Depends(get_db)):
    jobs = db.query(JobPosting).order_by(desc(JobPosting.created_at)).all()
    results = []
    for j in jobs:
        count = db.query(ResumeAnalysis).filter(ResumeAnalysis.job_id == j.id).count()
        results.append(
            JobPostingResponse(
                id=j.id,
                title=j.title,
                department=j.department,
                experience_level=j.experience_level,
                description=j.description,
                required_skills=j.required_skills or [],
                preferred_skills=j.preferred_skills or [],
                created_at=j.created_at,
                applicant_count=count
            )
        )
    return results


@app.post("/api/jobs", response_model=JobPostingResponse)
def create_job_posting(payload: JobPostingCreate, db: Session = Depends(get_db)):
    job = JobPosting(
        title=payload.title,
        department=payload.department or "Engineering",
        experience_level=payload.experience_level or "Mid-Level",
        description=payload.description,
        required_skills=payload.required_skills,
        preferred_skills=payload.preferred_skills
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return JobPostingResponse(
        id=job.id,
        title=job.title,
        department=job.department,
        experience_level=job.experience_level,
        description=job.description,
        required_skills=job.required_skills or [],
        preferred_skills=job.preferred_skills or [],
        created_at=job.created_at,
        applicant_count=0
    )


@app.delete("/api/jobs/{job_id}")
def delete_job_posting(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"message": "Job deleted successfully"}


# 3. Candidates / Admin Endpoints
@app.get("/api/candidates", response_model=List[CandidateSummary])
def list_candidates(
    search: Optional[str] = None,
    job_id: Optional[int] = None,
    min_score: Optional[float] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(CandidateResume).join(ResumeAnalysis, CandidateResume.id == ResumeAnalysis.resume_id)
    
    if search:
        query = query.filter(
            (CandidateResume.candidate_name.ilike(f"%{search}%")) |
            (CandidateResume.email.ilike(f"%{search}%")) |
            (ResumeAnalysis.job_title.ilike(f"%{search}%"))
        )
    if job_id:
        query = query.filter(ResumeAnalysis.job_id == job_id)
    if min_score is not None:
        query = query.filter(ResumeAnalysis.overall_score >= min_score)
    if status and status.lower() != "all":
        query = query.filter(ResumeAnalysis.status.ilike(status))

    resumes = query.order_by(desc(ResumeAnalysis.created_at)).all()
    results = []
    for r in resumes:
        latest_analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.resume_id == r.id).order_by(desc(ResumeAnalysis.created_at)).first()
        if latest_analysis:
            results.append(
                CandidateSummary(
                    id=r.id,
                    candidate_name=r.candidate_name,
                    email=r.email,
                    phone=r.phone,
                    filename=r.filename,
                    job_title=latest_analysis.job_title,
                    overall_score=latest_analysis.overall_score,
                    status=latest_analysis.status,
                    uploaded_at=r.uploaded_at,
                    analysis_id=latest_analysis.id
                )
            )
    return results


@app.get("/api/candidates/{candidate_id}", response_model=CandidateDetail)
def get_candidate_detail(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(CandidateResume).filter(CandidateResume.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    latest_analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.resume_id == candidate.id).order_by(desc(ResumeAnalysis.created_at)).first()
    
    analysis_resp = None
    if latest_analysis:
        analysis_resp = ResumeAnalysisResponse(
            id=latest_analysis.id,
            resume_id=candidate.id,
            candidate_name=candidate.candidate_name,
            email=candidate.email,
            phone=candidate.phone,
            job_id=latest_analysis.job_id,
            job_title=latest_analysis.job_title,
            overall_score=latest_analysis.overall_score,
            skills_score=latest_analysis.skills_score,
            experience_score=latest_analysis.experience_score,
            ats_score=latest_analysis.ats_score,
            domain_score=latest_analysis.domain_score,
            matched_skills=latest_analysis.matched_skills or [],
            missing_skills=latest_analysis.missing_skills or [],
            suggestions=latest_analysis.suggestions or [],
            ats_details=latest_analysis.ats_details or {},
            status=latest_analysis.status,
            created_at=latest_analysis.created_at
        )

    return CandidateDetail(
        id=candidate.id,
        candidate_name=candidate.candidate_name,
        email=candidate.email,
        phone=candidate.phone,
        filename=candidate.filename,
        raw_text=candidate.raw_text,
        extracted_skills=candidate.extracted_skills or {},
        experience_years=candidate.experience_years,
        education=candidate.education or [],
        links=candidate.links or [],
        uploaded_at=candidate.uploaded_at,
        latest_analysis=analysis_resp
    )


@app.patch("/api/candidates/{candidate_id}/status")
def update_candidate_status(candidate_id: int, payload: StatusUpdate, db: Session = Depends(get_db)):
    analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.resume_id == candidate_id).order_by(desc(ResumeAnalysis.created_at)).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Candidate analysis not found")
    analysis.status = payload.status
    db.commit()
    return {"message": "Status updated successfully", "status": payload.status}


@app.delete("/api/candidates/{candidate_id}")
def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = db.query(CandidateResume).filter(CandidateResume.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    # Clean up file if exists
    if candidate.filepath and os.path.exists(candidate.filepath):
        try:
            os.remove(candidate.filepath)
        except Exception:
            pass
    db.delete(candidate)
    db.commit()
    return {"message": "Candidate deleted successfully"}


# 4. Analytics Dashboard Endpoint
@app.get("/api/analytics/dashboard", response_model=DashboardAnalytics)
def get_dashboard_analytics(db: Session = Depends(get_db)):
    analyses = db.query(ResumeAnalysis).all()
    total_resumes = len(analyses)
    avg_score = round(sum(a.overall_score for a in analyses) / total_resumes, 1) if total_resumes > 0 else 0.0

    shortlisted = sum(1 for a in analyses if a.status.lower() == "shortlisted")
    under_review = sum(1 for a in analyses if a.status.lower() == "under review")
    rejected = sum(1 for a in analyses if a.status.lower() == "rejected")

    # Score distribution brackets
    dist = {"90-100": 0, "75-89": 0, "50-74": 0, "<50": 0}
    for a in analyses:
        if a.overall_score >= 90:
            dist["90-100"] += 1
        elif a.overall_score >= 75:
            dist["75-89"] += 1
        elif a.overall_score >= 50:
            dist["50-74"] += 1
        else:
            dist["<50"] += 1

    # Frequency of in-demand skills from job postings
    skill_counts = {}
    jobs = db.query(JobPosting).all()
    for j in jobs:
        for sk in (j.required_skills or []):
            skill_counts[sk] = skill_counts.get(sk, 0) + 1
    top_in_demand = sorted([{"skill": k, "count": v} for k, v in skill_counts.items()], key=lambda x: x["count"], reverse=True)[:6]

    # Frequency of missing skills across candidates
    missing_counts = {}
    for a in analyses:
        for sk in (a.missing_skills or []):
            missing_counts[sk] = missing_counts.get(sk, 0) + 1
    top_missing = sorted([{"skill": k, "count": v} for k, v in missing_counts.items()], key=lambda x: x["count"], reverse=True)[:6]

    # Recent candidate summaries
    recent_candidates = list_candidates(db=db)[:5]

    return DashboardAnalytics(
        total_resumes=total_resumes,
        average_score=avg_score,
        shortlisted_count=shortlisted,
        under_review_count=under_review,
        rejected_count=rejected,
        top_in_demand_skills=top_in_demand,
        top_missing_skills=top_missing,
        score_distribution=dist,
        recent_candidates=recent_candidates
    )


# ---------------- Frontend Static Mount ----------------
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def serve_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "AI Resume Analyzer API running. Visit /docs for OpenAPI specifications."}
