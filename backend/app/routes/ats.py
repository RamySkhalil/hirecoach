"""
ATS (Applicant Tracking System) API routes for recruiters.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import os

from app.db import get_db
from app.models import (
    User, UserRole, Company, RecruiterProfile, Job, JobSkill, Candidate,
    Application, Screening, Interview, InterviewMetric, InterviewFeedback,
    JobStatus, ApplicationStatus, InterviewType, InterviewStatus, EmploymentType
)
from app.routes.auth import get_current_user, require_role
from app.services.social_post_service import SocialPostService
from app.services.r2_storage_service import get_r2_service

router = APIRouter(prefix="/api/ats/v1", tags=["ATS"])


# ============================================================================
# Request/Response Models
# ============================================================================

class CreateJobRequest(BaseModel):
    """Request to create a job posting."""
    title: str
    location: Optional[str] = None
    employment_type: Optional[str] = None
    description: str
    requirements_raw: Optional[str] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    currency: Optional[str] = "USD"
    company_name: Optional[str] = None


class JobResponse(BaseModel):
    """Job response model."""
    id: str
    title: str
    location: Optional[str]
    employment_type: Optional[str]
    description: str
    status: str
    company_name: Optional[str]
    created_at: datetime
    applications_count: int = 0
    is_active: bool = True
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    currency: Optional[str] = None
    
    class Config:
        from_attributes = True


class ApplyJobRequest(BaseModel):
    """Request to apply for a job."""
    candidate_name: str
    candidate_email: str
    candidate_phone: Optional[str] = None
    candidate_location: Optional[str] = None
    resume_url: Optional[str] = None


class ApplicationResponse(BaseModel):
    """Application response model."""
    id: str
    job_id: str
    candidate_id: str
    candidate_name: str
    candidate_email: str
    candidate_location: Optional[str] = None
    resume_url: Optional[str] = None  # DEPRECATED: Kept for backward compatibility, will be None for new uploads
    status: str
    fit_score: Optional[float]
    applied_at: datetime
    
    class Config:
        from_attributes = True


class CVUrlResponse(BaseModel):
    """Response model for presigned CV URL."""
    url: str


class CreateInterviewRequest(BaseModel):
    """Request to create an interview."""
    type: str  # "HUMAN" or "AI"
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None


class InterviewResponse(BaseModel):
    """Interview response model."""
    id: str
    application_id: str
    type: str
    status: str
    scheduled_start: Optional[datetime]
    scheduled_end: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Helper Functions
# ============================================================================

def get_or_create_company(db: Session, company_name: str, user_id: str) -> Company:
    """Get or create a company for the recruiter."""
    # For now, create a default company per recruiter
    # In future, allow multiple companies
    company = db.query(Company).filter(Company.name == company_name).first()
    if not company:
        company = Company(name=company_name)
        db.add(company)
        db.commit()
        db.refresh(company)
    
    # Ensure recruiter profile exists
    profile = db.query(RecruiterProfile).filter(RecruiterProfile.user_id == user_id).first()
    if not profile:
        profile = RecruiterProfile(
            user_id=user_id,
            company_id=company.id
        )
        db.add(profile)
        db.commit()
    elif not profile.company_id:
        profile.company_id = company.id
        db.commit()
    
    return company


def calculate_placeholder_fit_score(job: Job, candidate: Candidate) -> float:
    """
    Placeholder fit score calculation.
    In future, use embeddings/RAG for CV-to-JD matching.
    """
    # Simple placeholder: return random score between 50-90
    import random
    return round(random.uniform(50.0, 90.0), 2)


# ============================================================================
# Job Routes
# ============================================================================

@router.post("/jobs", response_model=JobResponse)
async def create_job(
    request: CreateJobRequest,
    user: User = Depends(require_role(UserRole.RECRUITER)),
    db: Session = Depends(get_db)
):
    """
    Create a new job posting.
    
    Requires RECRUITER role.
    """
    # Get or create company
    company_name = request.company_name or f"{user.full_name or user.email}'s Company"
    company = get_or_create_company(db, company_name, user.id)
    
    # Parse employment type
    employment_type = None
    if request.employment_type:
        try:
            employment_type = EmploymentType(request.employment_type.upper())
        except ValueError:
            pass
    
    # Create job (default to OPEN so it's publicly visible)
    job = Job(
        company_id=company.id,
        title=request.title,
        location=request.location,
        employment_type=employment_type,
        description=request.description,
        requirements_raw=request.requirements_raw,
        min_salary=request.min_salary,
        max_salary=request.max_salary,
        currency=request.currency,
        created_by_user_id=user.id,
        status=JobStatus.OPEN,  # Set to OPEN so candidates can apply
        is_active=True  # Default to active
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    return JobResponse(
        id=str(job.id),
        title=job.title,
        location=job.location,
        employment_type=job.employment_type.value if job.employment_type else None,
        description=job.description,
        status=job.status.value,
        company_name=company.name,
        created_at=job.created_at,
        applications_count=0,
        min_salary=job.min_salary,
        max_salary=job.max_salary,
        currency=job.currency,
        is_active=job.is_active if hasattr(job, 'is_active') else True
    )


@router.get("/jobs", response_model=List[JobResponse])
async def list_jobs(
    search: Optional[str] = None,
    filter_status: Optional[str] = None,  # "all", "active", "inactive"
    user: User = Depends(require_role(UserRole.RECRUITER)),
    db: Session = Depends(get_db)
):
    """
    List all jobs created by the current recruiter.
    Supports search by title and filter by active/inactive status.
    """
    query = db.query(Job).filter(Job.created_by_user_id == user.id)
    
    # Search by title
    if search:
        query = query.filter(Job.title.ilike(f"%{search}%"))
    
    # Filter by active/inactive
    if filter_status == "active":
        query = query.filter(Job.is_active == True)
    elif filter_status == "inactive":
        query = query.filter(Job.is_active == False)
    # "all" or None means no filter
    
    jobs = query.all()
    
    result = []
    for job in jobs:
        company = db.query(Company).filter(Company.id == job.company_id).first() if job.company_id else None
        apps_count = db.query(func.count(Application.id)).filter(Application.job_id == job.id).scalar() or 0
        
        result.append(JobResponse(
            id=str(job.id),
            title=job.title,
            location=job.location,
            employment_type=job.employment_type.value if job.employment_type else None,
            description=job.description,
            status=job.status.value,
            company_name=company.name if company else None,
            created_at=job.created_at,
            applications_count=apps_count,
            min_salary=job.min_salary,
            max_salary=job.max_salary,
            currency=job.currency,
            is_active=job.is_active if hasattr(job, 'is_active') else True
        ))
    
    return result


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    user: User = Depends(require_role(UserRole.RECRUITER)),
    db: Session = Depends(get_db)
):
    """
    Get a specific job by ID (RECRUITER only).
    """
    job = db.query(Job).filter(Job.id == job_id, Job.created_by_user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    company = db.query(Company).filter(Company.id == job.company_id).first() if job.company_id else None
    apps_count = db.query(func.count(Application.id)).filter(Application.job_id == job.id).scalar() or 0
    
    return JobResponse(
        id=str(job.id),
        title=job.title,
        location=job.location,
        employment_type=job.employment_type.value if job.employment_type else None,
        description=job.description,
        status=job.status.value,
        company_name=company.name if company else None,
        created_at=job.created_at,
        applications_count=apps_count,
        min_salary=job.min_salary,
        max_salary=job.max_salary,
        currency=job.currency,
        is_active=job.is_active if hasattr(job, 'is_active') else True
    )


@router.get("/jobs/{job_id}/public", response_model=JobResponse)
async def get_job_public(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a job by ID for public viewing (no auth required).
    Only returns jobs with status OPEN and is_active=True.
    """
    job = db.query(Job).filter(
        Job.id == job_id, 
        Job.status == JobStatus.OPEN,
        Job.is_active == True
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or no longer accepting applications")
    
    company = db.query(Company).filter(Company.id == job.company_id).first() if job.company_id else None
    
    # Also include salary info for public view
    return JobResponse(
        id=str(job.id),
        title=job.title,
        location=job.location,
        employment_type=job.employment_type.value if job.employment_type else None,
        description=job.description,
        status=job.status.value,
        company_name=company.name if company else None,
        created_at=job.created_at,
        applications_count=0,  # Don't show count to public
        min_salary=job.min_salary,
        max_salary=job.max_salary,
        currency=job.currency,
        is_active=job.is_active if hasattr(job, 'is_active') else True
    )


@router.patch("/jobs/{job_id}/toggle-active", response_model=JobResponse)
async def toggle_job_active(
    job_id: str,
    user: User = Depends(require_role(UserRole.RECRUITER)),
    db: Session = Depends(get_db)
):
    """
    Toggle the active status of a job (activate/deactivate ad).
    """
    job = db.query(Job).filter(Job.id == job_id, Job.created_by_user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Toggle is_active
    job.is_active = not job.is_active
    db.commit()
    db.refresh(job)
    
    company = db.query(Company).filter(Company.id == job.company_id).first() if job.company_id else None
    apps_count = db.query(func.count(Application.id)).filter(Application.job_id == job.id).scalar() or 0
    
    return JobResponse(
        id=str(job.id),
        title=job.title,
        location=job.location,
        employment_type=job.employment_type.value if job.employment_type else None,
        description=job.description,
        status=job.status.value,
        company_name=company.name if company else None,
        created_at=job.created_at,
        applications_count=apps_count,
        min_salary=job.min_salary,
        max_salary=job.max_salary,
        currency=job.currency,
        is_active=job.is_active
    )


@router.post("/jobs/{job_id}/apply", response_model=ApplicationResponse)
async def apply_to_job(
    job_id: str,
    candidate_name: str = Form(...),
    candidate_email: str = Form(...),
    candidate_phone: Optional[str] = Form(None),
    candidate_location: Optional[str] = Form(None),
    resume_file: Optional[UploadFile] = File(None),
    resume_url: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Apply to a job (public endpoint - candidates can apply).
    
    Accepts either:
    - resume_file: CV file upload (PDF, DOCX, DOC, TXT)
    - resume_url: URL to existing CV/resume
    
    If both are provided, resume_file takes precedence.
    """
    # Check job exists and is active
    job = db.query(Job).filter(
        Job.id == job_id, 
        Job.status == JobStatus.OPEN,
        Job.is_active == True
    ).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or not accepting applications")
    
    # Handle file upload if provided
    resume_key = None
    
    if resume_file:
        r2_service = get_r2_service()
        if not r2_service:
            raise HTTPException(
                status_code=503,
                detail="File upload service is not configured. Please contact support."
            )
        
        # Validate file
        file_content = await resume_file.read()
        file_size = len(file_content)
        
        is_valid, error_msg = r2_service.validate_file(resume_file.filename or "resume", file_size)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Upload to R2 - returns object key, not URL
        try:
            from io import BytesIO
            file_obj = BytesIO(file_content)
            resume_key = r2_service.upload_file(
                file_obj,
                resume_file.filename or "resume",
                folder="Applicants"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload resume: {str(e)}"
            )
    elif resume_url:
        # Legacy support: if URL is provided, try to extract key
        # This handles old data or manual entries
        import re
        if "Applicants/" in resume_url:
            match = re.search(r'Applicants/[^/?]+', resume_url)
            if match:
                resume_key = match.group(0)
    
    # Get or create candidate
    candidate = db.query(Candidate).filter(Candidate.email == candidate_email).first()
    if not candidate:
        candidate = Candidate(
            full_name=candidate_name,
            email=candidate_email,
            phone=candidate_phone,
            location=candidate_location,
            resume_key=resume_key
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
    else:
        # Update candidate info if needed
        if resume_key and not candidate.resume_key:
            candidate.resume_key = resume_key
        if candidate_location and not candidate.location:
            candidate.location = candidate_location
        if candidate_phone and not candidate.phone:
            candidate.phone = candidate_phone
        db.commit()
    
    # Create application
    application = Application(
        job_id=job_id,
        candidate_id=candidate.id,
        status=ApplicationStatus.APPLIED,
        source="portal",
        applied_at=datetime.utcnow()
    )
    db.add(application)
    db.commit()
    
    # Calculate placeholder fit score
    fit_score = calculate_placeholder_fit_score(job, candidate)
    application.fit_score = fit_score
    
    # Create screening record
    screening = Screening(
        application_id=application.id,
        fit_score=fit_score,
        skills_matched=[],
        skills_missing=[]
    )
    db.add(screening)
    db.commit()
    db.refresh(application)
    
    return ApplicationResponse(
        id=application.id,
        job_id=application.job_id,
        candidate_id=application.candidate_id,
        candidate_name=candidate.full_name,
        candidate_email=candidate.email,
        candidate_location=candidate.location,
        resume_url=None,  # No longer returned - use /cv endpoint instead
        status=application.status.value,
        fit_score=application.fit_score,
        applied_at=application.applied_at
    )


@router.get("/jobs/{job_id}/applications", response_model=List[ApplicationResponse])
async def get_job_applications(
    job_id: str,
    user: User = Depends(require_role(UserRole.RECRUITER)),
    db: Session = Depends(get_db)
):
    """
    Get all applications for a job.
    """
    # Verify job belongs to recruiter
    job = db.query(Job).filter(Job.id == job_id, Job.created_by_user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    applications = db.query(Application).filter(Application.job_id == job_id).all()
    
    result = []
    for app in applications:
        candidate = db.query(Candidate).filter(Candidate.id == app.candidate_id).first()
        result.append(ApplicationResponse(
            id=app.id,
            job_id=app.job_id,
            candidate_id=app.candidate_id,
            candidate_name=candidate.full_name if candidate else "Unknown",
            candidate_email=candidate.email if candidate else "",
            candidate_location=candidate.location if candidate else None,
            resume_url=None,  # No longer returned - use /cv endpoint instead
            status=app.status.value,
            fit_score=app.fit_score,
            applied_at=app.applied_at
        ))
    
    return result


@router.get("/applications/{application_id}/cv", response_model=CVUrlResponse)
async def get_application_cv(
    application_id: str,
    user: User = Depends(require_role(UserRole.RECRUITER)),
    db: Session = Depends(get_db)
):
    """
    Get a presigned URL to access an application's CV.
    
    This endpoint:
    - Authenticates the user (must be RECRUITER)
    - Authorizes access to the application (must own the job)
    - Generates a short-lived presigned URL (10 minutes) for the CV
    - Returns the URL for frontend to open
    
    Security:
    - CVs are stored privately in R2
    - Only accessible via presigned URLs after authorization
    - URLs expire after 10 minutes
    """
    # Load application
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Authorize: verify user owns the job for this application
    job = db.query(Job).filter(
        Job.id == application.job_id,
        Job.created_by_user_id == user.id
    ).first()
    if not job:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to access this application's CV"
        )
    
    # Get candidate and check for CV
    candidate = db.query(Candidate).filter(Candidate.id == application.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Check if candidate has a CV (prefer resume_key, fallback to resume_url for legacy)
    cv_key = candidate.resume_key
    if not cv_key and candidate.resume_url:
        # Legacy: try to extract key from URL
        import re
        if "Applicants/" in candidate.resume_url:
            match = re.search(r'Applicants/[^/?]+', candidate.resume_url)
            if match:
                cv_key = match.group(0)
    
    if not cv_key:
        raise HTTPException(
            status_code=404,
            detail="CV not found for this application"
        )
    
    # Generate presigned URL
    r2_service = get_r2_service()
    if not r2_service:
        raise HTTPException(
            status_code=503,
            detail="File storage service is not configured"
        )
    
    try:
        # Generate presigned URL valid for 10 minutes (600 seconds)
        presigned_url = r2_service.generate_presigned_cv_url(
            object_key=cv_key,
            expires_in_seconds=600
        )
        return CVUrlResponse(url=presigned_url)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate CV access URL: {str(e)}"
        )


# ============================================================================
# Interview Routes
# ============================================================================

@router.post("/applications/{application_id}/interviews", response_model=InterviewResponse)
async def create_interview(
    application_id: str,
    request: CreateInterviewRequest,
    user: User = Depends(require_role(UserRole.RECRUITER)),
    db: Session = Depends(get_db)
):
    """
    Schedule an interview for an application.
    """
    # Verify application exists and belongs to recruiter's job
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    job = db.query(Job).filter(Job.id == application.job_id, Job.created_by_user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=403, detail="Not authorized for this application")
    
    # Parse interview type
    try:
        interview_type = InterviewType(request.type.upper())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid interview type. Must be 'HUMAN' or 'AI'")
    
    # Create interview
    interview = Interview(
        application_id=application_id,
        type=interview_type,
        status=InterviewStatus.SCHEDULED,
        scheduled_start=request.scheduled_start,
        scheduled_end=request.scheduled_end,
        created_by_user_id=user.id
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    
    return InterviewResponse(
        id=interview.id,
        application_id=interview.application_id,
        type=interview.type.value,
        status=interview.status.value,
        scheduled_start=interview.scheduled_start,
        scheduled_end=interview.scheduled_end,
        created_at=interview.created_at
    )


@router.get("/applications/{application_id}/interviews", response_model=List[InterviewResponse])
async def get_application_interviews(
    application_id: str,
    user: User = Depends(require_role(UserRole.RECRUITER)),
    db: Session = Depends(get_db)
):
    """
    Get all interviews for an application.
    """
    # Verify application belongs to recruiter's job
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    job = db.query(Job).filter(Job.id == application.job_id, Job.created_by_user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    interviews = db.query(Interview).filter(Interview.application_id == application_id).all()
    
    return [
        InterviewResponse(
            id=i.id,
            application_id=i.application_id,
            type=i.type.value,
            status=i.status.value,
            scheduled_start=i.scheduled_start,
            scheduled_end=i.scheduled_end,
            created_at=i.created_at
        )
        for i in interviews
    ]


# ============================================================================
# Social Media Post Generation
# ============================================================================

class SocialPostResponse(BaseModel):
    """Social media post response."""
    text: str
    link: str


@router.post("/jobs/{job_id}/social-post", response_model=SocialPostResponse)
async def generate_social_post(
    job_id: str,
    user: User = Depends(require_role(UserRole.RECRUITER)),
    db: Session = Depends(get_db)
):
    """
    Generate a social media post for a job listing.
    Uses AI to create engaging content ready to share on LinkedIn, Twitter, etc.
    """
    # Verify job belongs to recruiter
    job = db.query(Job).filter(Job.id == job_id, Job.created_by_user_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    company = db.query(Company).filter(Company.id == job.company_id).first() if job.company_id else None
    
    # Generate application URL (customize with your actual frontend URL)
    # For now, use localhost for development - update this to your actual domain in production
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")  # Update this to your actual frontend URL
    job_url = f"{frontend_url}/jobs/{job_id}"  # Public job listing page
    
    # Generate social media post
    post_data = SocialPostService.generate_social_post(
        job_title=job.title,
        company_name=company.name if company else None,
        location=job.location,
        employment_type=job.employment_type.value if job.employment_type else None,
        description=job.description,
        min_salary=job.min_salary,
        max_salary=job.max_salary,
        currency=job.currency or "USD",
        job_url=job_url
    )
    
    return SocialPostResponse(
        text=post_data["text"],
        link=post_data["link"]
    )

