"""
SQLAlchemy models for Interviewly.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Enum as SQLEnum, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.db import Base

# Import pgvector type for vector embeddings
try:
    from pgvector.sqlalchemy import Vector
    PGVECTOR_AVAILABLE = True
except ImportError:
    PGVECTOR_AVAILABLE = False
    # Fallback: use Text for non-Postgres databases
    Vector = Text


class SessionStatus(str, enum.Enum):
    """Interview session status enum."""
    ACTIVE = "active"
    COMPLETED = "completed"


class Seniority(str, enum.Enum):
    """Job seniority levels."""
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"


class QuestionType(str, enum.Enum):
    """Types of interview questions."""
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SITUATIONAL = "situational"
    GENERAL = "general"


class InterviewSession(Base):
    """
    Represents a complete interview session.
    """
    __tablename__ = "interview_sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True)  # For future user authentication
    
    # Session configuration
    job_title = Column(String(255), nullable=False)
    seniority = Column(String(20), nullable=False)  # junior, mid, senior
    language = Column(String(10), nullable=False, default="en")  # en, ar
    num_questions = Column(Integer, nullable=False)
    
    # Session state
    status = Column(String(20), nullable=False, default="active")  # active, completed
    
    # Results
    overall_score = Column(Integer, nullable=True)  # 0-100
    summary_json = Column(JSON, nullable=True)  # Stores full summary report
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    questions = relationship("InterviewQuestion", back_populates="session", cascade="all, delete-orphan")
    answers = relationship("InterviewAnswer", back_populates="session", cascade="all, delete-orphan")


class InterviewQuestion(Base):
    """
    Represents a single question in an interview session.
    """
    __tablename__ = "interview_questions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    
    # Question metadata
    idx = Column(Integer, nullable=False)  # 1-based index (Question 1, 2, 3...)
    type = Column(String(50), nullable=False)  # technical, behavioral, situational, general
    competency = Column(String(255), nullable=True)  # e.g., "Problem Solving", "Leadership"
    question_text = Column(Text, nullable=False)
    
    # Relationships
    session = relationship("InterviewSession", back_populates="questions")
    answer = relationship("InterviewAnswer", back_populates="question", uselist=False)


class InterviewAnswer(Base):
    """
    Represents a user's answer to a specific question.
    """
    __tablename__ = "interview_answers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("interview_questions.id", ondelete="CASCADE"), nullable=False)
    
    # User answer
    user_answer_text = Column(Text, nullable=False)
    user_answer_audio = Column(String(512), nullable=True)  # URL to audio file (future)
    
    # Evaluation scores (0-100 scale)
    score_overall = Column(Integer, nullable=False)
    score_relevance = Column(Integer, nullable=True)
    score_clarity = Column(Integer, nullable=True)
    score_structure = Column(Integer, nullable=True)
    score_impact = Column(Integer, nullable=True)
    
    # AI coach feedback
    coach_notes = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    session = relationship("InterviewSession", back_populates="answers")
    question = relationship("InterviewQuestion", back_populates="answer")


class CVAnalysisStatus(str, enum.Enum):
    """CV analysis status enum."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CVAnalysis(Base):
    """
    Represents a CV/Resume analysis.
    """
    __tablename__ = "cv_analyses"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True)  # Clerk user ID
    
    # File information
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)  # Local storage path
    file_size = Column(Integer, nullable=True)  # File size in bytes
    file_type = Column(String(50), nullable=True)  # pdf, docx, txt
    
    # Target job (optional)
    target_job_title = Column(String(255), nullable=True)
    target_seniority = Column(String(20), nullable=True)
    
    # Analysis status
    status = Column(SQLEnum(CVAnalysisStatus), nullable=False, default=CVAnalysisStatus.PENDING)
    
    # Extracted information
    extracted_text = Column(Text, nullable=True)
    parsed_data = Column(JSON, nullable=True)  # Structured CV data
    
    # Scoring results
    overall_score = Column(Integer, nullable=True)  # 0-100
    ats_score = Column(Integer, nullable=True)  # ATS compatibility score
    scores_breakdown = Column(JSON, nullable=True)  # Detailed scores
    
    # Analysis results
    strengths = Column(JSON, nullable=True)  # List of strengths
    weaknesses = Column(JSON, nullable=True)  # List of weaknesses
    suggestions = Column(JSON, nullable=True)  # Improvement suggestions
    keywords_found = Column(JSON, nullable=True)  # Relevant keywords
    keywords_missing = Column(JSON, nullable=True)  # Missing keywords
    
    # Metadata
    analysis_notes = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)


class SubscriptionTier(str, enum.Enum):
    """Subscription tier enum."""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, enum.Enum):
    """Subscription status enum."""
    ACTIVE = "active"
    CANCELED = "canceled"
    EXPIRED = "expired"
    TRIAL = "trial"


class User(Base):
    """
    User model with Clerk integration.
    """
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    clerk_user_id = Column(String(255), unique=True, nullable=False, index=True)  # Clerk's user ID
    
    # Profile information
    email = Column(String(255), nullable=False, unique=True, index=True)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # User preferences
    preferred_language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")
    
    # Account status
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    
    # Usage stats
    total_interviews = Column(Integer, default=0)
    total_cv_analyses = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="user", uselist=False)


class Subscription(Base):
    """
    User subscription model.
    """
    __tablename__ = "subscriptions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True)
    
    # Subscription details
    tier = Column(SQLEnum(SubscriptionTier), nullable=False, default=SubscriptionTier.FREE)
    status = Column(SQLEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE)
    
    # Billing
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    price_id = Column(String(255), nullable=True)
    
    # Limits
    interviews_limit = Column(Integer, default=5)  # Per month
    cv_analyses_limit = Column(Integer, default=3)  # Per month
    interviews_used = Column(Integer, default=0)
    cv_analyses_used = Column(Integer, default=0)
    
    # Dates
    trial_ends_at = Column(DateTime, nullable=True)
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    canceled_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="subscription")


class JobStatus(str, enum.Enum):
    """Job posting status enum."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


class ApplicationStatus(str, enum.Enum):
    """Application status enum."""
    SUBMITTED = "submitted"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFERED = "offered"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class CVRewriteStyle(str, enum.Enum):
    """CV rewrite style enum."""
    MODERN = "modern"
    MINIMAL = "minimal"
    EXECUTIVE = "executive"
    ATS_OPTIMIZED = "ats_optimized"


class CoverLetterTone(str, enum.Enum):
    """Cover letter tone enum."""
    FORMAL = "formal"
    SMART = "smart"
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"


class JobPosting(Base):
    """
    Job posting model for ATS integration.
    """
    __tablename__ = "job_postings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)  # Company/recruiter
    
    # Job details
    title = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    remote = Column(Boolean, default=False)
    job_type = Column(String(50), nullable=True)  # full-time, part-time, contract
    
    # Description
    description = Column(Text, nullable=False)
    requirements = Column(JSON, nullable=True)  # List of requirements
    responsibilities = Column(JSON, nullable=True)  # List of responsibilities
    benefits = Column(JSON, nullable=True)  # List of benefits
    
    # Compensation
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String(10), default="USD")
    
    # Job attributes
    seniority = Column(String(20), nullable=True)  # junior, mid, senior
    department = Column(String(100), nullable=True)
    skills_required = Column(JSON, nullable=True)  # List of skills
    
    # Status
    status = Column(SQLEnum(JobStatus), nullable=False, default=JobStatus.DRAFT)
    views_count = Column(Integer, default=0)
    applications_count = Column(Integer, default=0)
    
    # External integration
    external_id = Column(String(255), nullable=True)  # For ATS sync
    external_url = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    published_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    
    # Relationships
    applications = relationship("Application", back_populates="job")


class Application(Base):
    """
    Job application model.
    """
    __tablename__ = "applications"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("job_postings.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)  # Applicant
    
    # Applicant information
    applicant_email = Column(String(255), nullable=False)
    applicant_name = Column(String(255), nullable=False)
    applicant_phone = Column(String(50), nullable=True)
    
    # Application documents
    cv_id = Column(String(36), ForeignKey("cv_analyses.id"), nullable=True)
    cover_letter = Column(Text, nullable=True)
    portfolio_url = Column(String(500), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    
    # Status and scoring
    status = Column(SQLEnum(ApplicationStatus), nullable=False, default=ApplicationStatus.SUBMITTED)
    cv_match_score = Column(Integer, nullable=True)  # 0-100 match with job
    interview_score = Column(Integer, nullable=True)  # From mock interview
    
    # Interview details
    interview_session_id = Column(String(36), ForeignKey("interview_sessions.id"), nullable=True)
    interview_scheduled_at = Column(DateTime, nullable=True)
    interview_completed_at = Column(DateTime, nullable=True)
    
    # Notes and feedback
    recruiter_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # External integration
    external_id = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)
    
    # Relationships
    job = relationship("JobPosting", back_populates="applications")


class CVRewrite(Base):
    """
    CV rewrite/generation model for creating optimized versions.
    """
    __tablename__ = "cv_rewrites"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True)
    cv_analysis_id = Column(String(36), ForeignKey("cv_analyses.id"), nullable=True)
    
    # Input
    original_cv_text = Column(Text, nullable=False)
    target_job_title = Column(String(255), nullable=True)
    target_job_description = Column(Text, nullable=True)
    style = Column(SQLEnum(CVRewriteStyle), nullable=False, default=CVRewriteStyle.MODERN)
    
    # Output
    rewritten_cv_text = Column(Text, nullable=True)
    rewritten_cv_markdown = Column(Text, nullable=True)
    improvements_made = Column(JSON, nullable=True)  # List of improvements
    keywords_added = Column(JSON, nullable=True)  # List of keywords added
    ats_score_before = Column(Integer, nullable=True)
    ats_score_after = Column(Integer, nullable=True)
    
    # Status
    status = Column(String(20), nullable=False, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)


class CoverLetter(Base):
    """
    Cover letter generation model.
    """
    __tablename__ = "cover_letters"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True)
    cv_analysis_id = Column(String(36), ForeignKey("cv_analyses.id"), nullable=True)
    job_posting_id = Column(String(36), ForeignKey("job_postings.id"), nullable=True)
    
    # Input
    cv_text = Column(Text, nullable=False)
    job_title = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    job_description = Column(Text, nullable=True)
    tone = Column(SQLEnum(CoverLetterTone), nullable=False, default=CoverLetterTone.PROFESSIONAL)
    additional_info = Column(Text, nullable=True)  # User's additional context
    
    # Output
    cover_letter_text = Column(Text, nullable=True)
    cover_letter_markdown = Column(Text, nullable=True)
    matching_skills = Column(JSON, nullable=True)  # Skills matched from CV to job
    key_highlights = Column(JSON, nullable=True)  # Key points highlighted
    
    # Status
    status = Column(String(20), nullable=False, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)


class UserMessageEmbedding(Base):
    """
    Stores vector embeddings of user messages for AI Career Agent memory.
    Uses pgvector for semantic search and context retrieval.
    """
    __tablename__ = "user_message_embeddings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), nullable=False, index=True)  # Clerk user ID or session ID
    message_id = Column(String(36), nullable=False, index=True)  # Unique message identifier
    
    # Message content
    message_text = Column(Text, nullable=False)  # Original message text
    message_role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    
    # Vector embedding (1536 dimensions for OpenAI ada-002 or similar)
    # For Postgres with pgvector: stores actual vector
    # For SQLite fallback: stores JSON string of vector
    embedding = Column(Vector(1536) if PGVECTOR_AVAILABLE else Text, nullable=True)
    
    # Metadata for context
    conversation_id = Column(String(36), nullable=True, index=True)  # Group related messages
    context_type = Column(String(50), nullable=True)  # 'career_chat', 'interview', etc.
    metadata_json = Column(JSON, nullable=True)  # Additional metadata
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<UserMessageEmbedding(id={self.id}, user_id={self.user_id}, role={self.message_role})>"

