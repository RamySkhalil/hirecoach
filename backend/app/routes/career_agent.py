"""
AI Career Agent endpoints - Personal career coaching assistant.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.services.career_agent_service import CareerAgentService

router = APIRouter(prefix="/career", tags=["Career Agent"])


class ChatMessage(BaseModel):
    """Single chat message."""
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Request to chat with career agent."""
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = None
    user_context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Response from career agent."""
    message: str
    suggestions: List[str]
    action_items: List[str]
    status: str


class CareerSuggestionsRequest(BaseModel):
    """Request for career path suggestions."""
    current_role: str
    skills: List[str]
    experience_years: int
    interests: Optional[List[str]] = None


class CareerSuggestionsResponse(BaseModel):
    """Career path suggestions response."""
    suggested_roles: List[str]
    growth_paths: List[str]
    skills_to_learn: List[str]


@router.post("/chat", response_model=ChatResponse)
def chat_with_agent(request: ChatRequest):
    """
    Chat with the AI Career Agent.
    
    Send a message and receive personalized career advice.
    The agent remembers conversation history and provides contextual responses.
    """
    try:
        result = CareerAgentService.chat(
            message=request.message,
            conversation_history=request.conversation_history,
            user_context=request.user_context
        )
        
        return ChatResponse(
            message=result["message"],
            suggestions=result.get("suggestions", []),
            action_items=result.get("action_items", []),
            status=result.get("status", "success")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Career agent chat failed: {str(e)}"
        )


@router.post("/suggestions", response_model=CareerSuggestionsResponse)
def get_career_suggestions(request: CareerSuggestionsRequest):
    """
    Get personalized career path suggestions.
    
    Based on your current role, skills, and experience,
    get AI-powered recommendations for your next career moves.
    """
    try:
        result = CareerAgentService.get_career_suggestions(
            current_role=request.current_role,
            skills=request.skills,
            experience_years=request.experience_years,
            interests=request.interests
        )
        
        return CareerSuggestionsResponse(
            suggested_roles=result.get("suggested_roles", []),
            growth_paths=result.get("growth_paths", []),
            skills_to_learn=result.get("skills_to_learn", [])
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get career suggestions: {str(e)}"
        )


@router.get("/quick-tips")
def get_quick_tips(topic: Optional[str] = None):
    """
    Get quick career tips.
    
    Topics: resume, interview, networking, salary, skills
    """
    tips_by_topic = {
        "resume": [
            "Use action verbs to describe accomplishments",
            "Quantify achievements with specific metrics",
            "Tailor your resume to each job application",
            "Keep it concise - 1-2 pages maximum",
            "Use keywords from the job description"
        ],
        "interview": [
            "Research the company thoroughly before the interview",
            "Prepare STAR method examples for behavioral questions",
            "Ask thoughtful questions about the role and team",
            "Practice common interview questions out loud",
            "Follow up with a thank-you email within 24 hours"
        ],
        "networking": [
            "Attend industry events and conferences regularly",
            "Connect with people on LinkedIn with personalized messages",
            "Offer help before asking for favors",
            "Follow up with new connections within a week",
            "Join professional groups and online communities"
        ],
        "salary": [
            "Research industry salary ranges beforehand",
            "Consider total compensation, not just base salary",
            "Practice salary negotiation conversations",
            "Know your worth and be confident",
            "Time your negotiation strategically"
        ],
        "skills": [
            "Focus on high-demand skills in your industry",
            "Build a portfolio to showcase your work",
            "Take online courses and earn certifications",
            "Practice regularly through real projects",
            "Stay updated with industry trends"
        ],
        "general": [
            "Set clear short-term and long-term career goals",
            "Seek feedback regularly and act on it",
            "Build a strong professional network",
            "Invest in continuous learning",
            "Document your achievements and wins"
        ]
    }
    
    selected_topic = topic.lower() if topic else "general"
    tips = tips_by_topic.get(selected_topic, tips_by_topic["general"])
    
    return {
        "topic": selected_topic,
        "tips": tips
    }

