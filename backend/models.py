import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .database import Base

class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    department = Column(String(100), default="Engineering")
    experience_level = Column(String(50), default="Mid-Level")
    description = Column(Text, nullable=False)
    required_skills = Column(JSON, default=list)  # list of skill strings
    preferred_skills = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    analyses = relationship("ResumeAnalysis", back_populates="job", cascade="all, delete-orphan")


class CandidateResume(Base):
    __tablename__ = "candidate_resumes"

    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String(200), default="Unknown Candidate")
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    raw_text = Column(Text, nullable=False)
    extracted_skills = Column(JSON, default=dict)  # {"technical": [], "soft": [], "tools": []}
    experience_years = Column(Float, default=0.0)
    education = Column(JSON, default=list)
    links = Column(JSON, default=list)  # LinkedIn, GitHub, etc.
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    analyses = relationship("ResumeAnalysis", back_populates="resume", cascade="all, delete-orphan")


class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("candidate_resumes.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("job_postings.id", ondelete="SET NULL"), nullable=True)
    job_title = Column(String(200), default="Custom Role")
    
    overall_score = Column(Float, default=0.0)
    skills_score = Column(Float, default=0.0)
    experience_score = Column(Float, default=0.0)
    ats_score = Column(Float, default=0.0)
    domain_score = Column(Float, default=0.0)
    
    matched_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    suggestions = Column(JSON, default=list)
    ats_details = Column(JSON, default=dict)
    
    status = Column(String(50), default="Under Review")  # Under Review, Shortlisted, Interview, Rejected
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    resume = relationship("CandidateResume", back_populates="analyses")
    job = relationship("JobPosting", back_populates="analyses")
