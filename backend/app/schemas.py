"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


# ============================================================================
# Interview Session Schemas
# ============================================================================

class InterviewStartRequest(BaseModel):
    """Request schema for starting a new interview session."""
    job_title: str = Field(..., min_length=1, max_length=255, description="Job title for the interview")
    seniority: str = Field(..., pattern="^(junior|mid|senior)$", description="Seniority level")
    language: str = Field(default="en", pattern="^(en|ar)$", description="Interview language")
    num_questions: int = Field(..., ge=1, le=20, description="Number of questions (1-20)")


class QuestionResponse(BaseModel):
    """Response schema for a single question."""
    id: int
    idx: int
    type: str
    competency: Optional[str] = None
    question_text: str
    
    class Config:
        from_attributes = True


class InterviewStartResponse(BaseModel):
    """Response schema after starting an interview."""
    session_id: str
    first_question: QuestionResponse


# ============================================================================
# Answer Submission Schemas
# ============================================================================

class AnswerSubmitRequest(BaseModel):
    """Request schema for submitting an answer."""
    session_id: str
    question_id: int
    user_answer_text: str = Field(..., min_length=1, description="User's answer text")


class DimensionScores(BaseModel):
    """Breakdown of scoring dimensions."""
    relevance: int = Field(..., ge=0, le=100)
    clarity: int = Field(..., ge=0, le=100)
    structure: int = Field(..., ge=0, le=100)
    impact: int = Field(..., ge=0, le=100)


class AnswerSubmitResponse(BaseModel):
    """Response schema after submitting an answer."""
    score_overall: int = Field(..., ge=0, le=100)
    dimension_scores: DimensionScores
    coach_notes: str
    is_last_question: bool
    next_question: Optional[QuestionResponse] = None


# ============================================================================
# Interview Finish Schemas
# ============================================================================

class InterviewFinishRequest(BaseModel):
    """Request schema for finishing an interview."""
    session_id: str


class InterviewSummary(BaseModel):
    """Complete interview summary report."""
    overall_score: int = Field(..., ge=0, le=100)
    strengths: List[str]
    weaknesses: List[str]
    action_plan: List[str]
    suggested_roles: List[str]


class InterviewFinishResponse(BaseModel):
    """Response schema after finishing an interview."""
    session_id: str
    summary: InterviewSummary


# ============================================================================
# Media/STT/TTS Schemas
# ============================================================================

class STTResponse(BaseModel):
    """Response from Speech-to-Text service."""
    text: str


class TTSRequest(BaseModel):
    """Request for Text-to-Speech service."""
    text: str


class TTSResponse(BaseModel):
    """Response from Text-to-Speech service."""
    audio_url: Optional[str] = None
    audio_bytes_length: int = 0


# ============================================================================
# CV Analysis Schemas
# ============================================================================

class CVUploadRequest(BaseModel):
    """Request schema for CV upload (multipart form data)."""
    target_job_title: Optional[str] = None
    target_seniority: Optional[str] = Field(None, pattern="^(junior|mid|senior)$")


class CVScoresBreakdown(BaseModel):
    """Detailed CV scores breakdown."""
    content: int = Field(..., ge=0, le=100, description="Content quality score")
    formatting: int = Field(..., ge=0, le=100, description="Format and structure score")
    keywords: int = Field(..., ge=0, le=100, description="Keyword optimization score")
    experience: int = Field(..., ge=0, le=100, description="Experience relevance score")
    skills: int = Field(..., ge=0, le=100, description="Skills match score")


class CVAnalysisResponse(BaseModel):
    """Response schema for CV analysis."""
    id: str
    filename: str
    status: str
    overall_score: Optional[int] = None
    ats_score: Optional[int] = None
    scores_breakdown: Optional[CVScoresBreakdown] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None
    keywords_found: Optional[List[str]] = None
    keywords_missing: Optional[List[str]] = None
    parsed_data: Optional[Dict] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CVListResponse(BaseModel):
    """Response schema for listing CVs."""
    analyses: List[CVAnalysisResponse]
    total: int


# ============================================================================
# CV Rewriter Schemas
# ============================================================================

class CVRewriteRequest(BaseModel):
    """Request schema for CV rewrite."""
    cv_text: str = Field(..., min_length=50, description="Original CV text")
    cv_analysis_id: Optional[str] = None
    target_job_title: Optional[str] = None
    target_job_description: Optional[str] = None
    style: str = Field(default="modern", pattern="^(modern|minimal|executive|ats_optimized)$")


class CVRewriteResponse(BaseModel):
    """Response schema for CV rewrite."""
    id: str
    original_cv_text: str
    rewritten_cv_text: Optional[str] = None
    rewritten_cv_markdown: Optional[str] = None
    style: str
    improvements_made: Optional[List[str]] = None
    keywords_added: Optional[List[str]] = None
    ats_score_before: Optional[int] = None
    ats_score_after: Optional[int] = None
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Cover Letter Schemas
# ============================================================================

class CoverLetterRequest(BaseModel):
    """Request schema for cover letter generation."""
    cv_text: str = Field(..., min_length=50, description="CV text")
    cv_analysis_id: Optional[str] = None
    job_title: str = Field(..., min_length=1, description="Job title")
    company_name: str = Field(..., min_length=1, description="Company name")
    job_description: Optional[str] = None
    tone: str = Field(default="professional", pattern="^(formal|smart|professional|friendly)$")
    additional_info: Optional[str] = None


class CoverLetterResponse(BaseModel):
    """Response schema for cover letter."""
    id: str
    job_title: str
    company_name: str
    tone: str
    cover_letter_text: Optional[str] = None
    cover_letter_markdown: Optional[str] = None
    matching_skills: Optional[List[str]] = None
    key_highlights: Optional[List[str]] = None
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# Health Check
# ============================================================================

class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    app_name: str
    timestamp: datetime

