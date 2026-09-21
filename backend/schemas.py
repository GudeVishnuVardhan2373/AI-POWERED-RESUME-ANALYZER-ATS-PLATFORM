from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

# ----------------- Job Posting Schemas -----------------
class JobPostingBase(BaseModel):
    title: str
    department: Optional[str] = "Engineering"
    experience_level: Optional[str] = "Mid-Level"
    description: str
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)

class JobPostingCreate(JobPostingBase):
    pass

class JobPostingResponse(JobPostingBase):
    id: int
    created_at: datetime
    applicant_count: Optional[int] = 0

    class Config:
        from_attributes = True


# ----------------- Analysis & Candidate Schemas -----------------
class ATSCheckItem(BaseModel):
    passed: bool
    label: str
    tip: str

class SkillBreakdown(BaseModel):
    category: str
    skills: List[str]

class ResumeAnalysisResponse(BaseModel):
    id: int
    resume_id: int
    candidate_name: str
    email: Optional[str]
    phone: Optional[str]
    job_id: Optional[int]
    job_title: str
    overall_score: float
    skills_score: float
    experience_score: float
    ats_score: float
    domain_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    suggestions: List[Dict[str, Any]]
    ats_details: Dict[str, Any]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class CandidateSummary(BaseModel):
    id: int
    candidate_name: str
    email: Optional[str]
    phone: Optional[str]
    filename: str
    job_title: str
    overall_score: float
    status: str
    uploaded_at: datetime
    analysis_id: int

class CandidateDetail(BaseModel):
    id: int
    candidate_name: str
    email: Optional[str]
    phone: Optional[str]
    filename: str
    raw_text: str
    extracted_skills: Dict[str, List[str]]
    experience_years: float
    education: List[str]
    links: List[str]
    uploaded_at: datetime
    latest_analysis: Optional[ResumeAnalysisResponse] = None

    class Config:
        from_attributes = True


class StatusUpdate(BaseModel):
    status: str


class DashboardAnalytics(BaseModel):
    total_resumes: int
    average_score: float
    shortlisted_count: int
    under_review_count: int
    rejected_count: int
    top_in_demand_skills: List[Dict[str, Any]]
    top_missing_skills: List[Dict[str, Any]]
    score_distribution: Dict[str, int]
    recent_candidates: List[CandidateSummary]
