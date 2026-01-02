"""
30-Day Programs API endpoints.
Handles program browsing, enrollment, and progress tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.db import get_db
from app.models import (
    Program, ProgramDay, ProgramDayTask, ProgramEnrollment, 
    ProgramTaskProgress, ProgramDayCompletion,
    ProgramEnrollmentStatus, ProgramTaskType, User
)
from app.services.auth_service import ClerkAuthService
from pydantic import BaseModel


router = APIRouter(prefix="/api", tags=["Programs"])


# ========================================
# Response Models
# ========================================

class ProgramSummary(BaseModel):
    """Summary of a program for listings."""
    id: str
    slug: str
    title: str
    description: str
    target_role: str
    difficulty: str


class TaskSummary(BaseModel):
    """Summary of a task."""
    id: str
    task_type: str
    title: str
    details: Optional[str]
    meta: Optional[Dict[str, Any]]
    sort_order: int


class DaySummary(BaseModel):
    """Summary of a program day."""
    id: str
    day_number: int
    title: str
    focus_competencies: Optional[List[str]]
    tasks: List[TaskSummary]


class ProgramDetail(BaseModel):
    """Detailed program information."""
    id: str
    slug: str
    title: str
    description: str
    target_role: str
    difficulty: str
    days: List[DaySummary]


class EnrollmentSummary(BaseModel):
    """User enrollment summary."""
    id: str
    program_id: str
    program_title: str
    program_slug: str
    target_role: str
    status: str
    progress_percentage: float
    enrolled_at: datetime
    current_day: int  # Suggested current day based on enrollment date


class EnrollmentDetail(BaseModel):
    """Detailed enrollment with full program and progress."""
    id: str
    program: ProgramDetail
    status: str
    progress_percentage: float
    enrolled_at: datetime
    current_day: int
    task_progress: Dict[str, bool]  # task_id -> is_done
    completed_days: List[int]  # list of completed day numbers


class TaskCompleteRequest(BaseModel):
    """Request to mark a task complete."""
    pass  # No additional fields needed


class EnrollRequest(BaseModel):
    """Request to enroll in a program."""
    pass  # No additional fields needed


# ========================================
# Helper Functions
# ========================================

async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None."""
    if not authorization:
        return None
    
    try:
        token_info = await ClerkAuthService.get_user_from_token(authorization)
        clerk_user_id = token_info.get("user_id")
        
        if not clerk_user_id:
            return None
        
        user = ClerkAuthService.get_user_by_clerk_id(db, clerk_user_id)
        if not user:
            user = ClerkAuthService.get_or_create_user_from_clerk(
                db,
                clerk_user_id,
                token_info.get("email", ""),
                token_info.get("full_name")
            )
        
        return user
    except Exception:
        return None


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user (required)."""
    user = await get_current_user_optional(authorization, db)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def calculate_current_day(enrolled_at: datetime) -> int:
    """Calculate suggested current day based on enrollment date."""
    days_since_enrolled = (datetime.utcnow() - enrolled_at).days
    return min(max(1, days_since_enrolled + 1), 30)


def calculate_progress_percentage(db: Session, enrollment: ProgramEnrollment) -> float:
    """Calculate progress percentage for an enrollment."""
    # Get total tasks for the program
    total_tasks = db.query(ProgramDayTask).join(ProgramDay).filter(
        ProgramDay.program_id == enrollment.program_id
    ).count()
    
    if total_tasks == 0:
        return 0.0
    
    # Get completed tasks for this enrollment
    completed_tasks = db.query(ProgramTaskProgress).filter(
        ProgramTaskProgress.enrollment_id == enrollment.id,
        ProgramTaskProgress.is_done == True
    ).count()
    
    return (completed_tasks / total_tasks) * 100


# ========================================
# Public Endpoints
# ========================================

@router.get("/programs", response_model=List[ProgramSummary])
def list_programs(db: Session = Depends(get_db)):
    """Get list of all published programs."""
    programs = db.query(Program).filter(Program.is_published == True).all()
    
    return [
        ProgramSummary(
            id=p.id,
            slug=p.slug,
            title=p.title,
            description=p.description,
            target_role=p.target_role,
            difficulty=p.difficulty.value
        )
        for p in programs
    ]


@router.get("/programs/{program_id}", response_model=ProgramDetail)
def get_program_detail(program_id: str, db: Session = Depends(get_db)):
    """Get detailed program information including all days and tasks."""
    program = db.query(Program).filter(
        Program.id == program_id,
        Program.is_published == True
    ).first()
    
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    # Get days and tasks
    days = db.query(ProgramDay).filter(
        ProgramDay.program_id == program_id
    ).order_by(ProgramDay.day_number).all()
    
    days_data = []
    for day in days:
        tasks = db.query(ProgramDayTask).filter(
            ProgramDayTask.program_day_id == day.id
        ).order_by(ProgramDayTask.sort_order).all()
        
        tasks_data = [
            TaskSummary(
                id=task.id,
                task_type=task.task_type.value,
                title=task.title,
                details=task.details,
                meta=task.meta,
                sort_order=task.sort_order
            )
            for task in tasks
        ]
        
        days_data.append(DaySummary(
            id=day.id,
            day_number=day.day_number,
            title=day.title,
            focus_competencies=day.focus_competencies,
            tasks=tasks_data
        ))
    
    return ProgramDetail(
        id=program.id,
        slug=program.slug,
        title=program.title,
        description=program.description,
        target_role=program.target_role,
        difficulty=program.difficulty.value,
        days=days_data
    )


# ========================================
# Authenticated Endpoints
# ========================================

@router.post("/programs/{program_id}/enroll")
def enroll_in_program(
    program_id: str,
    request: EnrollRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enroll user in a program."""
    # Check if program exists and is published
    program = db.query(Program).filter(
        Program.id == program_id,
        Program.is_published == True
    ).first()
    
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    # Check if user is already enrolled
    existing_enrollment = db.query(ProgramEnrollment).filter(
        ProgramEnrollment.user_id == user.id,
        ProgramEnrollment.program_id == program_id
    ).first()
    
    if existing_enrollment:
        return {"enrollment_id": existing_enrollment.id, "message": "Already enrolled"}
    
    # Create new enrollment
    enrollment = ProgramEnrollment(
        user_id=user.id,
        program_id=program_id,
        status=ProgramEnrollmentStatus.ACTIVE
    )
    
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    
    return {"enrollment_id": enrollment.id, "message": "Successfully enrolled"}


@router.get("/me/programs", response_model=List[EnrollmentSummary])
def list_user_enrollments(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all user enrollments with progress."""
    enrollments = db.query(ProgramEnrollment).join(Program).filter(
        ProgramEnrollment.user_id == user.id
    ).all()
    
    result = []
    for enrollment in enrollments:
        progress = calculate_progress_percentage(db, enrollment)
        current_day = calculate_current_day(enrollment.enrolled_at)
        
        result.append(EnrollmentSummary(
            id=enrollment.id,
            program_id=enrollment.program_id,
            program_title=enrollment.program.title,
            program_slug=enrollment.program.slug,
            target_role=enrollment.program.target_role,
            status=enrollment.status.value,
            progress_percentage=progress,
            enrolled_at=enrollment.enrolled_at,
            current_day=current_day
        ))
    
    return result


@router.get("/me/programs/{program_id}", response_model=EnrollmentDetail)
def get_user_program_detail(
    program_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed enrollment information with full program and progress."""
    enrollment = db.query(ProgramEnrollment).filter(
        ProgramEnrollment.user_id == user.id,
        ProgramEnrollment.program_id == program_id
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # Get program details
    program_detail = get_program_detail(program_id, db)
    
    # Get task progress
    task_progress = {}
    progress_records = db.query(ProgramTaskProgress).filter(
        ProgramTaskProgress.enrollment_id == enrollment.id
    ).all()
    
    for progress in progress_records:
        task_progress[progress.program_day_task_id] = progress.is_done
    
    # Get completed days
    completed_days = db.query(ProgramDayCompletion.day_number).filter(
        ProgramDayCompletion.enrollment_id == enrollment.id
    ).all()
    completed_day_numbers = [day[0] for day in completed_days]
    
    # Calculate progress percentage
    progress_pct = calculate_progress_percentage(db, enrollment)
    current_day = calculate_current_day(enrollment.enrolled_at)
    
    return EnrollmentDetail(
        id=enrollment.id,
        program=program_detail,
        status=enrollment.status.value,
        progress_percentage=progress_pct,
        enrolled_at=enrollment.enrolled_at,
        current_day=current_day,
        task_progress=task_progress,
        completed_days=completed_day_numbers
    )


@router.post("/me/programs/{program_id}/tasks/{task_id}/complete")
def complete_task(
    program_id: str,
    task_id: str,
    request: TaskCompleteRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a task as completed."""
    # Verify enrollment
    enrollment = db.query(ProgramEnrollment).filter(
        ProgramEnrollment.user_id == user.id,
        ProgramEnrollment.program_id == program_id
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # Verify task exists and belongs to this program
    task = db.query(ProgramDayTask).join(ProgramDay).filter(
        ProgramDayTask.id == task_id,
        ProgramDay.program_id == program_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get or create task progress record
    progress = db.query(ProgramTaskProgress).filter(
        ProgramTaskProgress.enrollment_id == enrollment.id,
        ProgramTaskProgress.program_day_task_id == task_id
    ).first()
    
    if not progress:
        progress = ProgramTaskProgress(
            enrollment_id=enrollment.id,
            program_day_task_id=task_id,
            is_done=True,
            done_at=datetime.utcnow()
        )
        db.add(progress)
    else:
        progress.is_done = True
        progress.done_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Task marked as complete"}


@router.post("/me/programs/{program_id}/days/{day_number}/complete")
def complete_day(
    program_id: str,
    day_number: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a day as completed (validates all tasks are done first)."""
    if day_number < 1 or day_number > 30:
        raise HTTPException(status_code=400, detail="Day number must be between 1 and 30")
    
    # Verify enrollment
    enrollment = db.query(ProgramEnrollment).filter(
        ProgramEnrollment.user_id == user.id,
        ProgramEnrollment.program_id == program_id
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    # Get the day and its tasks
    day = db.query(ProgramDay).filter(
        ProgramDay.program_id == program_id,
        ProgramDay.day_number == day_number
    ).first()
    
    if not day:
        raise HTTPException(status_code=404, detail="Day not found")
    
    # Check if all tasks for this day are completed
    tasks = db.query(ProgramDayTask).filter(
        ProgramDayTask.program_day_id == day.id
    ).all()
    
    for task in tasks:
        progress = db.query(ProgramTaskProgress).filter(
            ProgramTaskProgress.enrollment_id == enrollment.id,
            ProgramTaskProgress.program_day_task_id == task.id
        ).first()
        
        if not progress or not progress.is_done:
            raise HTTPException(
                status_code=400, 
                detail=f"Task '{task.title}' is not completed yet"
            )
    
    # Check if day is already completed
    existing_completion = db.query(ProgramDayCompletion).filter(
        ProgramDayCompletion.enrollment_id == enrollment.id,
        ProgramDayCompletion.day_number == day_number
    ).first()
    
    if existing_completion:
        return {"message": "Day already completed"}
    
    # Mark day as completed
    completion = ProgramDayCompletion(
        enrollment_id=enrollment.id,
        day_number=day_number
    )
    
    db.add(completion)
    db.commit()
    
    return {"message": "Day marked as complete"}
