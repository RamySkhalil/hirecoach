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
    transcript_json = Column(JSON, nullable=True)  # Stores voice interview transcript
    
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


class UserRole(str, enum.Enum):
    """User role enum."""
    RECRUITER = "RECRUITER"
    CANDIDATE = "CANDIDATE"


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
    
    # User role (RECRUITER or CANDIDATE)
    role = Column(SQLEnum(UserRole), nullable=True, index=True)
    
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
    User subscription model with dynamic plan reference.
    Links users to pricing plans instead of hard-coded tiers.
    """
    __tablename__ = "subscriptions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    plan_id = Column(Integer, ForeignKey("pricing_plans.id"), nullable=False, index=True)
    
    # Subscription details
    billing_period = Column(String(20), nullable=False)  # 'monthly' or 'yearly'
    status = Column(SQLEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE)
    
    # Payment provider integration
    stripe_customer_id = Column(String(255), nullable=True, index=True)
    stripe_subscription_id = Column(String(255), nullable=True, index=True)
    stripe_price_id = Column(String(255), nullable=True)
    
    # Billing cycle dates
    trial_ends_at = Column(DateTime, nullable=True)
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    canceled_at = Column(DateTime, nullable=True)
    
    # Legacy fields (deprecated - use UserFeatureUsage instead)
    # Kept for backward compatibility during migration
    interviews_limit = Column(Integer, nullable=True)
    cv_analyses_limit = Column(Integer, nullable=True)
    interviews_used = Column(Integer, default=0)
    cv_analyses_used = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="subscription")
    plan = relationship("PricingPlan", back_populates="subscriptions")


class JobStatus(str, enum.Enum):
    """Job posting status enum."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


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
    # Note: Old JobPosting model - kept for backward compatibility
    # New ATS system uses Job model instead


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


# ========================================
# PRICING & USAGE TRACKING MODELS
# ========================================

class PricingPlan(Base):
    """
    Defines high-level subscription plans (Free, Basic, Pro, etc.).
    Dynamic pricing system - plans configured in database, not hard-coded.
    """
    __tablename__ = "pricing_plans"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True)  # 'free', 'basic', 'pro'
    name = Column(String(100), nullable=False)  # Display name: 'Free', 'Pro'
    description = Column(Text, nullable=True)  # Marketing description
    is_active = Column(Boolean, default=True, nullable=False)  # Can be disabled
    sort_order = Column(Integer, default=0, nullable=False)  # Display order
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    prices = relationship("PlanPrice", back_populates="plan", cascade="all, delete-orphan")
    features = relationship("PlanFeature", back_populates="plan", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="plan")
    
    def __repr__(self):
        return f"<PricingPlan(code={self.code}, name={self.name})>"


class PlanPrice(Base):
    """
    Stores pricing for each plan by billing period (monthly/yearly).
    Multiple prices per plan for different billing cycles.
    """
    __tablename__ = "plan_prices"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey("pricing_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    billing_period = Column(String(20), nullable=False)  # 'monthly' or 'yearly'
    price_cents = Column(Integer, nullable=False)  # Price in cents (e.g., 9900 = $99.00)
    currency = Column(String(10), nullable=False, default="USD")
    trial_days = Column(Integer, default=0, nullable=False)  # Free trial period
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    plan = relationship("PricingPlan", back_populates="prices")
    
    def __repr__(self):
        return f"<PlanPrice(plan_id={self.plan_id}, period={self.billing_period}, price={self.price_cents})>"


class PlanFeature(Base):
    """
    Defines per-feature limits for each pricing plan.
    Dynamic feature configuration - add new features without code changes.
    """
    __tablename__ = "plan_features"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey("pricing_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    feature_code = Column(String(50), nullable=False, index=True)  # 'cv_generate', 'mock_interview', etc.
    monthly_quota = Column(Integer, nullable=True)  # NULL = unlimited, 0 = disabled, >0 = limit
    hard_cap = Column(Boolean, default=True, nullable=False)  # TRUE = block after limit, FALSE = allow with warning
    rollover = Column(Boolean, default=False, nullable=False)  # For future: carry over unused quota
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    plan = relationship("PricingPlan", back_populates="features")
    
    def __repr__(self):
        return f"<PlanFeature(plan_id={self.plan_id}, feature={self.feature_code}, quota={self.monthly_quota})>"


class UserFeatureUsage(Base):
    """
    Tracks per-user feature usage within a billing period.
    Resets at the start of each billing cycle.
    """
    __tablename__ = "user_feature_usage"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)  # Clerk user ID
    plan_id = Column(Integer, ForeignKey("pricing_plans.id"), nullable=False, index=True)
    feature_code = Column(String(50), nullable=False, index=True)
    
    # Billing period
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False, index=True)
    
    # Usage tracking
    used_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<UserFeatureUsage(user_id={self.user_id}, feature={self.feature_code}, used={self.used_count})>"


class ModelPricing(Base):
    """
    Configuration table for LLM model pricing.
    Used to calculate cost from token usage.
    """
    __tablename__ = "model_pricing"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(100), unique=True, nullable=False, index=True)  # 'gpt-4o', 'gpt-4o-mini'
    input_cost_per_1k = Column(Float, nullable=False)  # USD per 1000 input tokens
    output_cost_per_1k = Column(Float, nullable=False)  # USD per 1000 output tokens
    currency = Column(String(10), nullable=False, default="USD")
    effective_from = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ModelPricing(model={self.model_name}, input=${self.input_cost_per_1k}/1k, output=${self.output_cost_per_1k}/1k)>"


class TokenUsageLog(Base):
    """
    Logs every LLM API call's token usage and cost.
    Used for profit/loss analysis and usage insights.
    """
    __tablename__ = "token_usage_log"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=True, index=True)  # Clerk user ID (nullable for system calls)
    plan_id = Column(Integer, ForeignKey("pricing_plans.id"), nullable=True, index=True)
    feature_code = Column(String(50), nullable=True, index=True)  # 'career_chat', 'cv_generate', etc.
    
    # Token usage
    model_name = Column(String(100), nullable=False, index=True)
    input_tokens = Column(Integer, nullable=False)
    output_tokens = Column(Integer, nullable=False)
    cost_usd = Column(Float, nullable=False)  # Calculated cost in USD
    
    # Metadata
    request_id = Column(String(100), nullable=True)  # For tracing
    metadata_json = Column(JSON, nullable=True)  # Additional context
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<TokenUsageLog(user_id={self.user_id}, model={self.model_name}, cost=${self.cost_usd})>"


# ========================================
# ATS (APPLICANT TRACKING SYSTEM) MODELS
# ========================================

class Company(Base):
    """
    Company model for recruiters.
    """
    __tablename__ = "companies"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    recruiter_profiles = relationship("RecruiterProfile", back_populates="company")
    jobs = relationship("Job", back_populates="company")


class RecruiterProfile(Base):
    """
    Recruiter profile linked to a user.
    """
    __tablename__ = "recruiter_profiles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=True, index=True)
    job_title = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User")
    company = relationship("Company", back_populates="recruiter_profiles")


class EmploymentType(str, enum.Enum):
    """Employment type enum."""
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    INTERNSHIP = "INTERNSHIP"
    TEMPORARY = "TEMPORARY"


class JobStatus(str, enum.Enum):
    """Job status enum for ATS."""
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    PAUSED = "PAUSED"
    CLOSED = "CLOSED"


class Job(Base):
    """
    Job posting model for ATS.
    """
    __tablename__ = "jobs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=True, index=True)
    
    # Job details
    title = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    employment_type = Column(SQLEnum(EmploymentType), nullable=True)
    description = Column(Text, nullable=False)
    requirements_raw = Column(Text, nullable=True)  # Original JD text
    
    # Status
    status = Column(SQLEnum(JobStatus), nullable=False, default=JobStatus.DRAFT, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)  # Controls if ad is visible to candidates
    
    # Compensation
    min_salary = Column(Float, nullable=True)
    max_salary = Column(Float, nullable=True)
    currency = Column(String(10), nullable=True, default="USD")
    
    # Creator
    created_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="jobs")
    skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="job")


class JobSkill(Base):
    """
    Skills required for a job.
    """
    __tablename__ = "job_skills"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(255), nullable=False)
    weight = Column(Integer, default=1, nullable=False)  # Importance weight (1-10)
    
    # Relationships
    job = relationship("Job", back_populates="skills")


class Candidate(Base):
    """
    Candidate model (separate from User - for external applicants).
    """
    __tablename__ = "candidates"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    years_experience = Column(Integer, nullable=True)
    current_title = Column(String(255), nullable=True)
    resume_key = Column(String(500), nullable=True)  # R2 object key (e.g., "Applicants/abc123.pdf"), NOT a URL
    resume_url = Column(String(500), nullable=True)  # DEPRECATED: Legacy field, kept for migration compatibility
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    applications = relationship("Application", back_populates="candidate")


class ApplicationStatus(str, enum.Enum):
    """Application status enum for ATS."""
    APPLIED = "APPLIED"
    SCREENING = "SCREENING"
    SHORTLISTED = "SHORTLISTED"
    INTERVIEW_SCHEDULED = "INTERVIEW_SCHEDULED"
    OFFERED = "OFFERED"
    REJECTED = "REJECTED"
    HIRED = "HIRED"


class Application(Base):
    """
    Job application model.
    """
    __tablename__ = "applications"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False, index=True)
    candidate_id = Column(String(36), ForeignKey("candidates.id"), nullable=False, index=True)
    
    # Status and scoring
    status = Column(SQLEnum(ApplicationStatus), nullable=False, default=ApplicationStatus.APPLIED, index=True)
    source = Column(String(50), nullable=True)  # "portal", "manual_upload", etc.
    applied_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    fit_score = Column(Float, nullable=True)  # 0-100 CV-to-JD match score
    ai_interview_score = Column(Float, nullable=True)  # 0-100 AI interview score
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    job = relationship("Job", back_populates="applications")
    candidate = relationship("Candidate", back_populates="applications")
    screenings = relationship("Screening", back_populates="application")
    interviews = relationship("Interview", back_populates="application")


class Screening(Base):
    """
    CV-to-JD screening result.
    """
    __tablename__ = "screenings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id = Column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Scoring results
    fit_score = Column(Float, nullable=False)  # 0-100
    skills_matched = Column(JSON, nullable=True)  # List of matched skills
    skills_missing = Column(JSON, nullable=True)  # List of missing skills
    embedding_model = Column(String(100), nullable=True)  # e.g. "text-embedding-3-large"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    application = relationship("Application", back_populates="screenings")


class InterviewType(str, enum.Enum):
    """Interview type enum."""
    HUMAN = "HUMAN"
    AI = "AI"


class InterviewStatus(str, enum.Enum):
    """Interview status enum."""
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"


class Interview(Base):
    """
    Interview model (for recruiter ATS interviews).
    """
    __tablename__ = "interviews"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id = Column(String(36), ForeignKey("applications.id"), nullable=False, index=True)
    
    # Interview details
    type = Column(SQLEnum(InterviewType), nullable=False)
    status = Column(SQLEnum(InterviewStatus), nullable=False, default=InterviewStatus.SCHEDULED, index=True)
    
    # Scheduling
    scheduled_start = Column(DateTime, nullable=True)
    scheduled_end = Column(DateTime, nullable=True)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    
    # LiveKit integration
    livekit_room_name = Column(String(255), nullable=True)
    livekit_recording_id = Column(String(255), nullable=True)
    recording_url = Column(String(500), nullable=True)  # S3/R2 URL
    
    # Creator
    created_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    application = relationship("Application", back_populates="interviews")
    metrics = relationship("InterviewMetric", back_populates="interview", uselist=False)
    feedback = relationship("InterviewFeedback", back_populates="interview")


class InterviewMetric(Base):
    """
    Interview performance metrics (from AI or video analytics).
    """
    __tablename__ = "interview_metrics"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_id = Column(String(36), ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Scoring metrics
    overall_score = Column(Float, nullable=True)  # 0-100
    eye_contact_pct = Column(Float, nullable=True)  # 0-100
    speech_fluency_score = Column(Float, nullable=True)  # 0-100
    sentiment_score = Column(Float, nullable=True)  # -1 to 1
    engagement_score = Column(Float, nullable=True)  # 0-100
    notes = Column(Text, nullable=True)
    raw_metrics = Column(JSON, nullable=True)  # Additional metrics as JSON
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    interview = relationship("Interview", back_populates="metrics")


class InterviewFeedback(Base):
    """
    Human recruiter feedback on interviews.
    """
    __tablename__ = "interview_feedback"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    interview_id = Column(String(36), ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Feedback
    rating = Column(Integer, nullable=True)  # 1-5 stars
    comment = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    interview = relationship("Interview", back_populates="feedback")

