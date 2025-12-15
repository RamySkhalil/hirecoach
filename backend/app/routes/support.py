"""
Support Chat endpoints - Linda support assistant.
Linda only answers questions about the application, not general questions.
Records conversations for registered users to maintain memory.
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.services.llm_service import LLMService
from app.db import get_db
from app.models import SupportChatMessage, User
from app.services.auth_service import ClerkAuthService

router = APIRouter(prefix="/support", tags=["Support"])


class SupportMessage(BaseModel):
    """Single support message."""
    role: str  # "user" or "assistant"
    content: str


class SupportChatRequest(BaseModel):
    """Request to chat with Linda support assistant."""
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = None
    conversation_id: Optional[str] = None  # For continuing existing conversations


class SupportChatResponse(BaseModel):
    """Response from Linda support assistant."""
    message: str
    conversation_id: Optional[str] = None


class ConversationHistoryResponse(BaseModel):
    """Response with conversation history."""
    messages: List[Dict[str, str]]
    conversation_id: Optional[str] = None


# Application knowledge base for Linda
APPLICATION_INFO = """You are Linda, a friendly and helpful support assistant for Interviewly - an AI-powered career preparation platform.

CRITICAL: You MUST ONLY answer questions about the Interviewly application and its features. You CANNOT answer general questions, provide general knowledge, discuss topics unrelated to Interviewly, or act as a general-purpose assistant.

APPLICATION FEATURES:
1. AI Interview Coach - Voice-enabled mock interviews with real-time feedback and scoring. Users can practice interviews with AI, get instant feedback, and receive detailed scoring on every answer.
2. CV Analyzer - Upload CVs for instant AI analysis with ATS scores, strengths, and suggestions. Provides keyword analysis and ATS compatibility scores.
3. CV Rewriter - Transform CVs with AI in multiple professional styles: Modern, Minimal, Executive, and ATS Optimized. Job-tailored and ATS-optimized rewrites.
4. AI Career Coach - Chat with personal AI career advisor for guidance on career growth, skills, and job search strategies.
5. ATS Screening (for Recruiters) - AI-powered applicant tracking system with CV-to-JD matching for recruiters.

KEY INFORMATION:
- The platform is powered by GPT-4o
- Users can practice interviews with voice-enabled AI
- CV analysis provides ATS scores and keyword analysis
- CV rewriter offers 4 different professional styles
- The platform supports both job seekers and recruiters
- All features are AI-powered and provide instant feedback
- Users can access features through the main page navigation

COMMON QUESTIONS YOU CAN ANSWER:
- How to use the interview coach
- How to analyze a CV
- How to rewrite a CV
- What features are available
- How to get started with Interviewly
- Technical issues with the platform
- Feature explanations and how they work
- Account and access questions
- Navigation and platform usage
- Differences between features
- Best practices for using the platform

STRICT RULES - YOU MUST FOLLOW THESE:
1. ONLY answer questions about Interviewly application features, usage, and platform-related topics
2. If asked about ANYTHING else (weather, news, general knowledge, other topics, etc.), you MUST respond with: "I'm Linda, your Interviewly support assistant. I can only help with questions about our Interviewly platform and its features. How can I assist you with Interviewly today?"
3. Do NOT provide general advice, information, or knowledge outside of Interviewly
4. Do NOT answer questions about other companies, products, or services
5. Be friendly, professional, and concise
6. If you don't know something specific about the application, say so honestly
7. Always redirect non-Interviewly questions back to Interviewly topics
8. Focus exclusively on helping users understand and use the Interviewly platform effectively

Remember: Your role is LIMITED to Interviewly support. You are NOT a general-purpose assistant."""


async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.
    Allows support chat to work for both authenticated and anonymous users.
    """
    if not authorization:
        return None
    
    try:
        token_info = await ClerkAuthService.get_user_from_token(authorization)
        clerk_user_id = token_info.get("user_id")
        
        if not clerk_user_id:
            return None
        
        # Get or create user
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


def get_or_create_conversation_id(
    db: Session,
    user: Optional[User],
    conversation_id: Optional[str] = None
) -> str:
    """
    Get existing conversation ID or create a new one.
    For authenticated users, we can group messages by conversation_id.
    For anonymous users, each session gets a new conversation_id.
    """
    if conversation_id:
        # Verify conversation exists (optional validation)
        return conversation_id
    
    # Create new conversation ID
    return str(uuid.uuid4())


@router.get("/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    conversation_id: Optional[str] = None,
    limit: int = 50,
    user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get conversation history for the current user.
    Returns empty list for anonymous users or if no conversation_id provided.
    """
    if not user or not conversation_id:
        return ConversationHistoryResponse(messages=[], conversation_id=conversation_id)
    
    # Fetch messages for this user and conversation
    query = db.query(SupportChatMessage).filter(
        SupportChatMessage.user_id == user.id,
        SupportChatMessage.conversation_id == conversation_id
    ).order_by(SupportChatMessage.created_at.asc()).limit(limit)
    
    messages = query.all()
    
    return ConversationHistoryResponse(
        messages=[
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ],
        conversation_id=conversation_id
    )


@router.get("/conversations")
async def list_conversations(
    user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
    limit: int = 10
):
    """
    List recent conversations for the authenticated user.
    Returns list of conversation IDs with metadata.
    """
    if not user:
        return {"conversations": []}
    
    # Get distinct conversations for user, ordered by most recent message
    from sqlalchemy import func
    
    conversations = db.query(
        SupportChatMessage.conversation_id,
        func.max(SupportChatMessage.created_at).label('last_message_at'),
        func.count(SupportChatMessage.id).label('message_count')
    ).filter(
        SupportChatMessage.user_id == user.id,
        SupportChatMessage.conversation_id.isnot(None)
    ).group_by(
        SupportChatMessage.conversation_id
    ).order_by(
        func.max(SupportChatMessage.created_at).desc()
    ).limit(limit).all()
    
    return {
        "conversations": [
            {
                "conversation_id": conv.conversation_id,
                "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else None,
                "message_count": conv.message_count
            }
            for conv in conversations
        ]
    }


@router.post("/chat", response_model=SupportChatResponse)
async def chat_with_linda(
    request: SupportChatRequest,
    user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Chat with Linda, the support assistant.
    Linda only answers questions about the Interviewly application.
    Saves messages to database for authenticated users.
    """
    try:
        # Get or create conversation ID
        conversation_id = get_or_create_conversation_id(
            db, user, request.conversation_id
        )
        
        # Load conversation history from database if user is authenticated
        db_messages = []
        if user:
            db_messages = db.query(SupportChatMessage).filter(
                SupportChatMessage.user_id == user.id,
                SupportChatMessage.conversation_id == conversation_id
            ).order_by(SupportChatMessage.created_at.asc()).limit(50).all()
        
        # Build conversation history
        messages = [
            {"role": "system", "content": APPLICATION_INFO}
        ]
        
        # Add messages from database (for authenticated users with history)
        if db_messages:
            for msg in db_messages:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        # Fallback to provided conversation history if no DB history
        elif request.conversation_history:
            for msg in request.conversation_history:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": request.message
        })
        
        # Save user message to database if authenticated
        if user:
            user_msg = SupportChatMessage(
                user_id=user.id,
                clerk_user_id=user.clerk_user_id,
                role="user",
                content=request.message,
                conversation_id=conversation_id
            )
            db.add(user_msg)
            db.commit()
        
        # Call LLM service
        response = LLMService._call_llm(messages, response_format="text")
        
        if not response:
            # Fallback response if LLM is not available
            assistant_message = "I'm Linda, your Interviewly support assistant. I'm currently experiencing technical difficulties. Please try again later or contact support directly."
        else:
            assistant_message = response
        
        # Save assistant response to database if authenticated
        if user:
            assistant_msg = SupportChatMessage(
                user_id=user.id,
                clerk_user_id=user.clerk_user_id,
                role="assistant",
                content=assistant_message,
                conversation_id=conversation_id
            )
            db.add(assistant_msg)
            db.commit()
        
        return SupportChatResponse(
            message=assistant_message,
            conversation_id=conversation_id
        )
        
    except Exception as e:
        print(f"Support chat error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process support chat request: {str(e)}"
        )

