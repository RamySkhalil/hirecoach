"""
CV Rewriter and Cover Letter Generator endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

from app.db import get_db
from app.models import CVRewrite, CoverLetter, CVRewriteStyle, CoverLetterTone
from app.schemas import (
    CVRewriteRequest, CVRewriteResponse,
    CoverLetterRequest, CoverLetterResponse
)
from app.services.cv_rewriter_service import CVRewriterService, CoverLetterService

router = APIRouter(prefix="/rewriter", tags=["CV Rewriter & Cover Letter"])


@router.post("/cv", response_model=CVRewriteResponse)
def rewrite_cv(
    request: CVRewriteRequest,
    db: Session = Depends(get_db)
):
    """
    Rewrite CV with AI in specified style.
    
    - **cv_text**: Original CV text
    - **style**: modern, minimal, executive, or ats_optimized
    - **target_job_title**: Optional job title for optimization
    - **target_job_description**: Optional job description for tailoring
    """
    # Create CV rewrite record
    cv_rewrite = CVRewrite(
        original_cv_text=request.cv_text,
        cv_analysis_id=request.cv_analysis_id,
        target_job_title=request.target_job_title,
        target_job_description=request.target_job_description,
        style=CVRewriteStyle(request.style),
        status="processing"
    )
    
    db.add(cv_rewrite)
    db.commit()
    db.refresh(cv_rewrite)
    
    # Store the ID before the long operation
    cv_rewrite_id = cv_rewrite.id
    
    try:
        # Generate rewritten CV (this is a long-running operation)
        result = CVRewriterService.rewrite_cv(
            cv_text=request.cv_text,
            style=request.style,
            target_job_title=request.target_job_title,
            target_job_description=request.target_job_description
        )
        
        # After long operation, refresh the connection and re-query the object
        # This ensures we have a fresh connection and object
        try:
            # Test connection is alive
            db.execute(text("SELECT 1"))
        except Exception:
            # Connection is dead, rollback and re-query
            db.rollback()
        
        # Re-query the object to ensure it's attached to a fresh session
        cv_rewrite = db.query(CVRewrite).filter(CVRewrite.id == cv_rewrite_id).first()
        if not cv_rewrite:
            raise HTTPException(status_code=500, detail="CV rewrite record not found after processing")
        
        # Update record with results
        cv_rewrite.rewritten_cv_text = result.get("rewritten_cv_text")
        cv_rewrite.rewritten_cv_markdown = result.get("rewritten_cv_markdown")
        cv_rewrite.improvements_made = result.get("improvements_made", [])
        cv_rewrite.keywords_added = result.get("keywords_added", [])
        cv_rewrite.ats_score_before = result.get("ats_score_before")
        cv_rewrite.ats_score_after = result.get("ats_score_after")
        cv_rewrite.status = "completed"
        cv_rewrite.completed_at = datetime.utcnow()
        
        try:
            db.commit()
            db.refresh(cv_rewrite)
        except Exception as db_error:
            db.rollback()
            raise HTTPException(
                status_code=500, 
                detail=f"Database error while saving results: {str(db_error)}"
            )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle any other errors
        try:
            db.rollback()
            # Re-query the object to ensure it's attached to the session
            cv_rewrite = db.query(CVRewrite).filter(CVRewrite.id == cv_rewrite.id).first()
            if cv_rewrite:
                cv_rewrite.status = "failed"
                cv_rewrite.error_message = str(e)
                db.commit()
        except Exception as db_error:
            # If rollback/commit fails, log but don't fail again
            print(f"Error updating CV rewrite status: {db_error}")
        
        raise HTTPException(status_code=500, detail=f"CV rewrite failed: {str(e)}")
    
    # Re-query to ensure object is fresh and attached to session
    try:
        cv_rewrite = db.query(CVRewrite).filter(CVRewrite.id == cv_rewrite.id).first()
        if not cv_rewrite:
            raise HTTPException(status_code=500, detail="CV rewrite record not found after completion")
        
        # Build response safely
        return CVRewriteResponse(
            id=cv_rewrite.id,
            original_cv_text=cv_rewrite.original_cv_text,
            rewritten_cv_text=cv_rewrite.rewritten_cv_text,
            rewritten_cv_markdown=cv_rewrite.rewritten_cv_markdown,
            style=cv_rewrite.style.value if cv_rewrite.style else "modern",
            improvements_made=cv_rewrite.improvements_made or [],
            keywords_added=cv_rewrite.keywords_added or [],
            ats_score_before=cv_rewrite.ats_score_before,
            ats_score_after=cv_rewrite.ats_score_after,
            status=cv_rewrite.status,
            created_at=cv_rewrite.created_at,
            completed_at=cv_rewrite.completed_at
        )
    except Exception as e:
        # If response creation fails, log and return error
        print(f"Error creating CV rewrite response: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creating response: {str(e)}")


@router.get("/cv/{rewrite_id}", response_model=CVRewriteResponse)
def get_cv_rewrite(rewrite_id: str, db: Session = Depends(get_db)):
    """Get CV rewrite by ID."""
    cv_rewrite = db.query(CVRewrite).filter(CVRewrite.id == rewrite_id).first()
    
    if not cv_rewrite:
        raise HTTPException(status_code=404, detail="CV rewrite not found")
    
    return CVRewriteResponse(
        id=cv_rewrite.id,
        original_cv_text=cv_rewrite.original_cv_text,
        rewritten_cv_text=cv_rewrite.rewritten_cv_text,
        rewritten_cv_markdown=cv_rewrite.rewritten_cv_markdown,
        style=cv_rewrite.style.value,
        improvements_made=cv_rewrite.improvements_made,
        keywords_added=cv_rewrite.keywords_added,
        ats_score_before=cv_rewrite.ats_score_before,
        ats_score_after=cv_rewrite.ats_score_after,
        status=cv_rewrite.status,
        created_at=cv_rewrite.created_at,
        completed_at=cv_rewrite.completed_at
    )


@router.post("/cover-letter", response_model=CoverLetterResponse)
def generate_cover_letter(
    request: CoverLetterRequest,
    db: Session = Depends(get_db)
):
    """
    Generate cover letter with AI.
    
    - **cv_text**: CV text
    - **job_title**: Target job title
    - **company_name**: Company name
    - **job_description**: Optional job description
    - **tone**: formal, smart, professional, or friendly
    - **additional_info**: Optional additional context
    """
    # Create cover letter record
    cover_letter = CoverLetter(
        cv_text=request.cv_text,
        cv_analysis_id=request.cv_analysis_id,
        job_title=request.job_title,
        company_name=request.company_name,
        job_description=request.job_description,
        tone=CoverLetterTone(request.tone),
        additional_info=request.additional_info,
        status="processing"
    )
    
    db.add(cover_letter)
    db.commit()
    db.refresh(cover_letter)
    
    # Store the ID before the long operation
    cover_letter_id = cover_letter.id
    
    try:
        # Generate cover letter (this is a long-running operation)
        result = CoverLetterService.generate_cover_letter(
            cv_text=request.cv_text,
            job_title=request.job_title,
            company_name=request.company_name,
            job_description=request.job_description,
            tone=request.tone,
            additional_info=request.additional_info
        )
        
        # After long operation, refresh the connection and re-query the object
        # This ensures we have a fresh connection and object
        try:
            # Test connection is alive
            db.execute(text("SELECT 1"))
        except Exception:
            # Connection is dead, rollback and re-query
            db.rollback()
        
        # Re-query the object to ensure it's attached to a fresh session
        cover_letter = db.query(CoverLetter).filter(CoverLetter.id == cover_letter_id).first()
        if not cover_letter:
            raise HTTPException(status_code=500, detail="Cover letter record not found after processing")
        
        # Update record with results
        cover_letter.cover_letter_text = result.get("cover_letter_text")
        cover_letter.cover_letter_markdown = result.get("cover_letter_markdown")
        cover_letter.matching_skills = result.get("matching_skills", [])
        cover_letter.key_highlights = result.get("key_highlights", [])
        cover_letter.status = "completed"
        cover_letter.completed_at = datetime.utcnow()
        
        try:
            db.commit()
            db.refresh(cover_letter)
        except Exception as db_error:
            db.rollback()
            raise HTTPException(
                status_code=500, 
                detail=f"Database error while saving results: {str(db_error)}"
            )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle any other errors
        try:
            db.rollback()
            # Re-query the object to ensure it's attached to the session
            cover_letter = db.query(CoverLetter).filter(CoverLetter.id == cover_letter.id).first()
            if cover_letter:
                cover_letter.status = "failed"
                cover_letter.error_message = str(e)
                db.commit()
        except Exception as db_error:
            # If rollback/commit fails, log but don't fail again
            print(f"Error updating cover letter status: {db_error}")
        
        raise HTTPException(status_code=500, detail=f"Cover letter generation failed: {str(e)}")
    
    return CoverLetterResponse(
        id=cover_letter.id,
        job_title=cover_letter.job_title,
        company_name=cover_letter.company_name,
        tone=cover_letter.tone.value,
        cover_letter_text=cover_letter.cover_letter_text,
        cover_letter_markdown=cover_letter.cover_letter_markdown,
        matching_skills=cover_letter.matching_skills,
        key_highlights=cover_letter.key_highlights,
        status=cover_letter.status,
        created_at=cover_letter.created_at,
        completed_at=cover_letter.completed_at
    )


@router.get("/cover-letter/{letter_id}", response_model=CoverLetterResponse)
def get_cover_letter(letter_id: str, db: Session = Depends(get_db)):
    """Get cover letter by ID."""
    cover_letter = db.query(CoverLetter).filter(CoverLetter.id == letter_id).first()
    
    if not cover_letter:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    
    return CoverLetterResponse(
        id=cover_letter.id,
        job_title=cover_letter.job_title,
        company_name=cover_letter.company_name,
        tone=cover_letter.tone.value,
        cover_letter_text=cover_letter.cover_letter_text,
        cover_letter_markdown=cover_letter.cover_letter_markdown,
        matching_skills=cover_letter.matching_skills,
        key_highlights=cover_letter.key_highlights,
        status=cover_letter.status,
        created_at=cover_letter.created_at,
        completed_at=cover_letter.completed_at
    )

