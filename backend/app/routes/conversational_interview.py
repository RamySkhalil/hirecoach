"""
Conversational Interview API Routes

This provides endpoints for the new conversational interview system
that uses LangChain + OpenAI for dynamic, adaptive conversations.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.db import get_db
from app.models import InterviewSession
from app.services.conversational_interview_service import ConversationalInterviewService

router = APIRouter(prefix="/interview/conversational", tags=["conversational-interview"])

# Store active interview agents in memory (in production, use Redis/database)
active_interviews: dict[str, ConversationalInterviewService] = {}


class StartConversationalInterviewRequest(BaseModel):
    """Request to start a conversational interview."""
    job_title: str
    seniority: str
    num_questions: int = 5


class StartConversationalInterviewResponse(BaseModel):
    """Response after starting interview."""
    session_id: str
    message: str
    type: str
    questions_asked: int
    total_questions: int


class SubmitAnswerRequest(BaseModel):
    """Request to submit an answer in conversational mode."""
    session_id: str
    answer: str


class SubmitAnswerResponse(BaseModel):
    """Response after submitting an answer."""
    message: str
    type: str
    questions_asked: int
    total_questions: int
    is_complete: bool


@router.post("/start", response_model=StartConversationalInterviewResponse)
def start_conversational_interview(
    request: StartConversationalInterviewRequest,
    db: Session = Depends(get_db)
):
    """
    Start a new conversational interview session.
    
    This creates an AI interview agent that will conduct a natural,
    adaptive conversation with the candidate.
    """
    try:
        # Create database session
        session = InterviewSession(
            job_title=request.job_title,
            seniority=request.seniority,
            num_questions=request.num_questions,
            status="active"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        session_id = str(session.id)
        
        # Create conversational agent
        agent = ConversationalInterviewService(
            job_title=request.job_title,
            seniority=request.seniority,
            num_questions=request.num_questions,
            session_id=session_id
        )
        
        # Get opening message
        response = agent.start_interview()
        
        # Store agent in memory
        active_interviews[session_id] = agent
        
        return StartConversationalInterviewResponse(
            session_id=session_id,
            message=response["message"],
            type=response["type"],
            questions_asked=response["questions_asked"],
            total_questions=response["total_questions"]
        )
        
    except Exception as e:
        print(f"Error starting conversational interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/answer", response_model=SubmitAnswerResponse)
def submit_conversational_answer(
    request: SubmitAnswerRequest,
    db: Session = Depends(get_db)
):
    """
    Submit an answer in a conversational interview.
    
    The AI will process your answer and respond naturally with
    a follow-up question or transition to a new topic.
    """
    try:
        # Get the interview agent
        agent = active_interviews.get(request.session_id)
        
        if not agent:
            raise HTTPException(
                status_code=404,
                detail="Interview session not found or expired"
            )
        
        # Process the answer and get next response
        response = agent.process_answer(request.answer)
        
        # If interview is complete, clean up
        if response.get("is_complete"):
            # Save conversation history to database
            session = db.query(InterviewSession).filter(
                InterviewSession.id == request.session_id
            ).first()
            
            if session:
                session.status = "completed"
                session.completed_at = datetime.now()
                db.commit()
            
            # Optional: Keep agent for final summary, or remove
            # del active_interviews[request.session_id]
        
        return SubmitAnswerResponse(
            message=response["message"],
            type=response["type"],
            questions_asked=response["questions_asked"],
            total_questions=response["total_questions"],
            is_complete=response.get("is_complete", False)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/end")
def end_conversational_interview(session_id: str):
    """
    End a conversational interview and get closing message.
    """
    try:
        agent = active_interviews.get(session_id)
        
        if not agent:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        response = agent.end_interview()
        
        # Clean up
        del active_interviews[session_id]
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error ending interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/{session_id}")
def get_conversation_summary(session_id: str):
    """Get a summary of the entire conversation."""
    try:
        agent = active_interviews.get(session_id)
        
        if not agent:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        return agent.get_conversation_summary()
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
def health_check():
    """Check if conversational interview service is available."""
    from app.services.conversational_interview_service import LANGCHAIN_AVAILABLE
    from app.config import settings
    
    return {
        "status": "healthy",
        "langchain_available": LANGCHAIN_AVAILABLE,
        "openai_configured": bool(settings.openai_api_key),
        "active_sessions": len(active_interviews)
    }

