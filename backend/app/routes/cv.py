"""
CV Analysis endpoints.
"""
import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from pathlib import Path

from app.db import get_db
from app.models import CVAnalysis, CVAnalysisStatus
from app.schemas import CVAnalysisResponse, CVListResponse, CVScoresBreakdown
from app.services.cv_service import CVService
from app.services.cv_export_service import CVExportService

router = APIRouter(prefix="/cv", tags=["CV Analysis"])

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads/cvs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/upload", response_model=CVAnalysisResponse)
async def upload_cv(
    file: UploadFile = File(...),
    target_job_title: Optional[str] = Form(None),
    target_seniority: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload and analyze a CV/Resume.
    
    - **file**: CV file (PDF, DOCX, or TXT)
    - **target_job_title**: Optional target job for tailored analysis
    - **target_seniority**: Optional target seniority (junior, mid, senior)
    - **user_id**: Optional user ID from Clerk auth
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Create CV analysis record
    cv_analysis = CVAnalysis(
        user_id=user_id,
        filename=file.filename,
        file_size=file_size,
        file_type=file_ext,
        target_job_title=target_job_title,
        target_seniority=target_seniority,
        status=CVAnalysisStatus.PENDING
    )
    
    db.add(cv_analysis)
    db.commit()
    db.refresh(cv_analysis)
    
    # Save file
    file_path = UPLOAD_DIR / f"{cv_analysis.id}{file_ext}"
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        cv_analysis.file_path = str(file_path)
        db.commit()
        
    except Exception as e:
        cv_analysis.status = CVAnalysisStatus.FAILED
        cv_analysis.error_message = f"File upload failed: {str(e)}"
        db.commit()
        raise HTTPException(status_code=500, detail="File upload failed")
    
    # Process CV asynchronously (for now, process immediately)
    try:
        cv_analysis.status = CVAnalysisStatus.PROCESSING
        db.commit()
        
        # Extract text
        extracted_text = CVService.extract_text(str(file_path), file_ext)
        cv_analysis.extracted_text = extracted_text
        
        # Parse CV with LLM
        parsed_data = CVService.parse_cv_with_llm(
            extracted_text,
            target_job=target_job_title
        )
        cv_analysis.parsed_data = parsed_data
        
        # Analyze CV
        analysis_result = CVService.analyze_cv(
            extracted_text,
            parsed_data,
            target_job=target_job_title,
            target_seniority=target_seniority
        )
        
        # Update CV analysis with results
        cv_analysis.overall_score = analysis_result.get("overall_score")
        cv_analysis.ats_score = analysis_result.get("ats_score")
        cv_analysis.scores_breakdown = analysis_result.get("scores_breakdown")
        cv_analysis.strengths = analysis_result.get("strengths", [])
        cv_analysis.weaknesses = analysis_result.get("weaknesses", [])
        cv_analysis.suggestions = analysis_result.get("suggestions", [])
        cv_analysis.keywords_found = analysis_result.get("keywords_found", [])
        cv_analysis.keywords_missing = analysis_result.get("keywords_missing", [])
        
        cv_analysis.status = CVAnalysisStatus.COMPLETED
        cv_analysis.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(cv_analysis)
        
    except Exception as e:
        cv_analysis.status = CVAnalysisStatus.FAILED
        cv_analysis.error_message = str(e)
        db.commit()
        db.refresh(cv_analysis)
        raise HTTPException(status_code=500, detail=f"CV analysis failed: {str(e)}")
    
    # Convert scores_breakdown to Pydantic model if it exists
    scores_breakdown = None
    if cv_analysis.scores_breakdown:
        scores_breakdown = CVScoresBreakdown(**cv_analysis.scores_breakdown)
    
    return CVAnalysisResponse(
        id=cv_analysis.id,
        filename=cv_analysis.filename,
        status=cv_analysis.status.value,
        overall_score=cv_analysis.overall_score,
        ats_score=cv_analysis.ats_score,
        scores_breakdown=scores_breakdown,
        strengths=cv_analysis.strengths,
        weaknesses=cv_analysis.weaknesses,
        suggestions=cv_analysis.suggestions,
        keywords_found=cv_analysis.keywords_found,
        keywords_missing=cv_analysis.keywords_missing,
        parsed_data=cv_analysis.parsed_data,
        created_at=cv_analysis.created_at,
        completed_at=cv_analysis.completed_at
    )


@router.get("/{cv_id}", response_model=CVAnalysisResponse)
def get_cv_analysis(cv_id: str, db: Session = Depends(get_db)):
    """
    Get CV analysis by ID.
    """
    cv_analysis = db.query(CVAnalysis).filter(CVAnalysis.id == cv_id).first()
    
    if not cv_analysis:
        raise HTTPException(status_code=404, detail="CV analysis not found")
    
    # Convert scores_breakdown to Pydantic model if it exists
    scores_breakdown = None
    if cv_analysis.scores_breakdown:
        scores_breakdown = CVScoresBreakdown(**cv_analysis.scores_breakdown)
    
    return CVAnalysisResponse(
        id=cv_analysis.id,
        filename=cv_analysis.filename,
        status=cv_analysis.status.value,
        overall_score=cv_analysis.overall_score,
        ats_score=cv_analysis.ats_score,
        scores_breakdown=scores_breakdown,
        strengths=cv_analysis.strengths,
        weaknesses=cv_analysis.weaknesses,
        suggestions=cv_analysis.suggestions,
        keywords_found=cv_analysis.keywords_found,
        keywords_missing=cv_analysis.keywords_missing,
        parsed_data=cv_analysis.parsed_data,
        created_at=cv_analysis.created_at,
        completed_at=cv_analysis.completed_at
    )


@router.get("/", response_model=CVListResponse)
def list_cv_analyses(
    user_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List CV analyses, optionally filtered by user_id.
    """
    query = db.query(CVAnalysis)
    
    if user_id:
        query = query.filter(CVAnalysis.user_id == user_id)
    
    total = query.count()
    analyses = query.order_by(CVAnalysis.created_at.desc()).offset(offset).limit(limit).all()
    
    # Convert to response models
    analyses_response = []
    for cv_analysis in analyses:
        scores_breakdown = None
        if cv_analysis.scores_breakdown:
            scores_breakdown = CVScoresBreakdown(**cv_analysis.scores_breakdown)
        
        analyses_response.append(CVAnalysisResponse(
            id=cv_analysis.id,
            filename=cv_analysis.filename,
            status=cv_analysis.status.value,
            overall_score=cv_analysis.overall_score,
            ats_score=cv_analysis.ats_score,
            scores_breakdown=scores_breakdown,
            strengths=cv_analysis.strengths,
            weaknesses=cv_analysis.weaknesses,
            suggestions=cv_analysis.suggestions,
            keywords_found=cv_analysis.keywords_found,
            keywords_missing=cv_analysis.keywords_missing,
            parsed_data=cv_analysis.parsed_data,
            created_at=cv_analysis.created_at,
            completed_at=cv_analysis.completed_at
        ))
    
    return CVListResponse(analyses=analyses_response, total=total)


@router.delete("/{cv_id}")
def delete_cv_analysis(cv_id: str, db: Session = Depends(get_db)):
    """
    Delete CV analysis and associated file.
    """
    cv_analysis = db.query(CVAnalysis).filter(CVAnalysis.id == cv_id).first()
    
    if not cv_analysis:
        raise HTTPException(status_code=404, detail="CV analysis not found")
    
    # Delete file if it exists
    if cv_analysis.file_path and os.path.exists(cv_analysis.file_path):
        try:
            os.remove(cv_analysis.file_path)
        except Exception as e:
            print(f"Failed to delete file: {e}")
    
    # Delete database record
    db.delete(cv_analysis)
    db.commit()
    
    return {"message": "CV analysis deleted successfully", "id": cv_id}


@router.post("/improve/{cv_id}")
async def improve_cv(
    cv_id: str,
    style: str = "ats_optimized",
    db: Session = Depends(get_db)
):
    """
    Generate improved CV based on analysis suggestions.
    Automatically applies all improvements and returns rewritten CV.
    """
    from app.services.cv_rewriter_service import CVRewriterService
    from app.models import CVRewrite, CVRewriteStyle
    
    # Get the CV analysis
    cv_analysis = db.query(CVAnalysis).filter(CVAnalysis.id == cv_id).first()
    if not cv_analysis:
        raise HTTPException(status_code=404, detail="CV analysis not found")
    
    if not cv_analysis.extracted_text:
        raise HTTPException(status_code=400, detail="CV text not available for improvement")
    
    # Build context from analysis
    improvement_context = []
    if cv_analysis.weaknesses:
        improvement_context.append("Fix these weaknesses:")
        improvement_context.extend([f"- {w}" for w in cv_analysis.weaknesses])
    
    if cv_analysis.suggestions:
        improvement_context.append("\nApply these suggestions:")
        improvement_context.extend([f"- {s}" for s in cv_analysis.suggestions])
    
    if cv_analysis.keywords_missing:
        improvement_context.append(f"\nAdd these keywords: {', '.join(cv_analysis.keywords_missing[:10])}")
    
    context_text = "\n".join(improvement_context) if improvement_context else None
    
    # Create CV rewrite record
    cv_rewrite = CVRewrite(
        cv_analysis_id=cv_id,
        original_cv_text=cv_analysis.extracted_text,
        style=CVRewriteStyle(style),
        status="processing"
    )
    
    db.add(cv_rewrite)
    db.commit()
    db.refresh(cv_rewrite)
    
    try:
        # Generate improved CV with context
        result = CVRewriterService.rewrite_cv(
            cv_text=cv_analysis.extracted_text,
            style=style,
            target_job_title=cv_analysis.target_job_title,
            target_job_description=context_text  # Use context as job description
        )
        
        # Update record
        cv_rewrite.rewritten_cv_text = result.get("rewritten_cv_text")
        cv_rewrite.rewritten_cv_markdown = result.get("rewritten_cv_markdown")
        cv_rewrite.improvements_made = result.get("improvements_made", [])
        cv_rewrite.keywords_added = result.get("keywords_added", [])
        cv_rewrite.ats_score_before = cv_analysis.ats_score or result.get("ats_score_before")
        cv_rewrite.ats_score_after = result.get("ats_score_after")
        cv_rewrite.status = "completed"
        cv_rewrite.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(cv_rewrite)
        
        return {
            "rewrite_id": cv_rewrite.id,
            "analysis_id": cv_id,
            "original_text": cv_rewrite.original_cv_text,
            "improved_text": cv_rewrite.rewritten_cv_text,
            "improvements_made": cv_rewrite.improvements_made,
            "keywords_added": cv_rewrite.keywords_added,
            "ats_score_before": cv_rewrite.ats_score_before,
            "ats_score_after": cv_rewrite.ats_score_after,
            "style": cv_rewrite.style.value,
            "analysis_weaknesses": cv_analysis.weaknesses,
            "analysis_suggestions": cv_analysis.suggestions,
        }
        
    except Exception as e:
        cv_rewrite.status = "failed"
        cv_rewrite.error_message = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"CV improvement failed: {str(e)}")


@router.get("/export/{rewrite_id}/{format}")
async def export_cv(
    rewrite_id: str,
    format: str,
    db: Session = Depends(get_db)
):
    """
    Export improved CV in specified format (pdf, docx, txt).
    """
    from app.models import CVRewrite
    from io import BytesIO
    
    # Get the CV rewrite
    cv_rewrite = db.query(CVRewrite).filter(CVRewrite.id == rewrite_id).first()
    if not cv_rewrite:
        raise HTTPException(status_code=404, detail="CV rewrite not found")
    
    if not cv_rewrite.rewritten_cv_text:
        raise HTTPException(status_code=400, detail="No rewritten CV text available")
    
    cv_text = cv_rewrite.rewritten_cv_text
    filename_base = f"cv-{cv_rewrite.style.value}-{rewrite_id[:8]}"
    
    try:
        if format.lower() == "txt":
            # TXT export (always works)
            buffer = BytesIO(cv_text.encode('utf-8'))
            buffer.seek(0)
            return StreamingResponse(
                buffer,
                media_type="text/plain",
                headers={"Content-Disposition": f"attachment; filename={filename_base}.txt"}
            )
        
        elif format.lower() == "pdf":
            # PDF export (requires reportlab)
            try:
                buffer = CVExportService.export_to_pdf(cv_text)
                return StreamingResponse(
                    buffer,
                    media_type="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename={filename_base}.pdf"}
                )
            except ImportError:
                raise HTTPException(
                    status_code=503,
                    detail="PDF export not available. Install reportlab: pip install reportlab"
                )
        
        elif format.lower() == "docx":
            # DOCX export (requires python-docx)
            try:
                buffer = CVExportService.export_to_docx(cv_text)
                return StreamingResponse(
                    buffer,
                    media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    headers={"Content-Disposition": f"attachment; filename={filename_base}.docx"}
                )
            except ImportError:
                raise HTTPException(
                    status_code=503,
                    detail="DOCX export not available. Install python-docx: pip install python-docx"
                )
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format: {format}. Use pdf, docx, or txt"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Export error: {str(e)}")  # Log for debugging
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/export-formats")
async def get_export_formats():
    """
    Get list of available export formats.
    """
    return {"formats": CVExportService.get_export_formats()}

