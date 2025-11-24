"""
Interview-related API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from datetime import datetime

from app.db import get_db
from app.models import InterviewSession, InterviewQuestion, InterviewAnswer
from app.schemas import (
    InterviewStartRequest,
    InterviewStartResponse,
    QuestionResponse,
    AnswerSubmitRequest,
    AnswerSubmitResponse,
    DimensionScores,
    InterviewFinishRequest,
    InterviewFinishResponse,
    InterviewSummary
)
from app.services.llm_service import LLMService
from app.services.tts_service import TTSService

router = APIRouter(prefix="/interview", tags=["interview"])


@router.post("/start", response_model=InterviewStartResponse)
def start_interview(
    request: InterviewStartRequest,
    db: Session = Depends(get_db)
):
    """
    Start a new interview session.
    
    Creates a session record and generates interview questions using LLM.
    Returns the session ID and first question.
    """
    # Create interview session
    session = InterviewSession(
        job_title=request.job_title,
        seniority=request.seniority,
        language=request.language,
        num_questions=request.num_questions,
        status="active"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Generate interview questions using LLM service
    questions_data = LLMService.generate_interview_plan(
        job_title=request.job_title,
        seniority=request.seniority,
        language=request.language,
        num_questions=request.num_questions
    )
    
    # Store questions in database
    db_questions = []
    for q_data in questions_data:
        question = InterviewQuestion(
            session_id=session.id,
            idx=q_data["idx"],
            type=q_data["type"],
            competency=q_data.get("competency"),
            question_text=q_data["question_text"]
        )
        db.add(question)
        db_questions.append(question)
    
    db.commit()
    
    # Refresh to get IDs
    for q in db_questions:
        db.refresh(q)
    
    # Return session ID and first question
    first_question = db_questions[0]
    
    return InterviewStartResponse(
        session_id=session.id,
        first_question=QuestionResponse(
            id=first_question.id,
            idx=first_question.idx,
            type=first_question.type,
            competency=first_question.competency,
            question_text=first_question.question_text
        )
    )


@router.post("/answer", response_model=AnswerSubmitResponse)
def submit_answer(
    request: AnswerSubmitRequest,
    db: Session = Depends(get_db)
):
    """
    Submit an answer to a question.
    
    Evaluates the answer using LLM, stores the result, and returns
    feedback along with the next question (if any).
    """
    # Validate session exists and is active
    session = db.query(InterviewSession).filter(
        InterviewSession.id == request.session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    if session.status != "active":
        raise HTTPException(status_code=400, detail="Interview session is not active")
    
    # Validate question exists and belongs to this session
    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == request.question_id,
        InterviewQuestion.session_id == request.session_id
    ).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found or does not belong to this session")
    
    # Check if answer already exists for this question
    existing_answer = db.query(InterviewAnswer).filter(
        InterviewAnswer.question_id == request.question_id
    ).first()
    
    if existing_answer:
        raise HTTPException(status_code=400, detail="Answer already submitted for this question")
    
    # Evaluate answer using LLM service
    evaluation = LLMService.evaluate_answer(
        question_text=question.question_text,
        question_type=question.type,
        user_answer=request.user_answer_text,
        job_title=session.job_title,
        seniority=session.seniority
    )
    
    # Store answer
    answer = InterviewAnswer(
        session_id=request.session_id,
        question_id=request.question_id,
        user_answer_text=request.user_answer_text,
        score_overall=evaluation["score_overall"],
        score_relevance=evaluation["dimension_scores"]["relevance"],
        score_clarity=evaluation["dimension_scores"]["clarity"],
        score_structure=evaluation["dimension_scores"]["structure"],
        score_impact=evaluation["dimension_scores"]["impact"],
        coach_notes=evaluation["coach_notes"]
    )
    db.add(answer)
    db.commit()
    db.refresh(answer)
    
    # Determine if this is the last question
    total_questions = session.num_questions
    current_idx = question.idx
    is_last = current_idx >= total_questions
    
    # Get next question if not last
    next_question = None
    if not is_last:
        next_q = db.query(InterviewQuestion).filter(
            InterviewQuestion.session_id == request.session_id,
            InterviewQuestion.idx == current_idx + 1
        ).first()
        
        if next_q:
            next_question = QuestionResponse(
                id=next_q.id,
                idx=next_q.idx,
                type=next_q.type,
                competency=next_q.competency,
                question_text=next_q.question_text
            )
    
    # Convert float scores to integers (LLM sometimes returns floats)
    dimension_scores_dict = evaluation["dimension_scores"]
    dimension_scores_int = {
        k: int(round(v)) for k, v in dimension_scores_dict.items()
    }
    
    return AnswerSubmitResponse(
        score_overall=int(round(evaluation["score_overall"])),
        dimension_scores=DimensionScores(**dimension_scores_int),
        coach_notes=evaluation["coach_notes"],
        is_last_question=is_last,
        next_question=next_question
    )


@router.post("/finish", response_model=InterviewFinishResponse)
def finish_interview(
    request: InterviewFinishRequest,
    db: Session = Depends(get_db)
):
    """
    Finish an interview session and generate final report.
    
    Analyzes all questions and answers, generates a comprehensive summary
    with strengths, weaknesses, action plan, and suggested roles.
    """
    # Validate session exists
    session = db.query(InterviewSession).filter(
        InterviewSession.id == request.session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    if session.status == "completed":
        # Already completed, return existing summary
        return InterviewFinishResponse(
            session_id=session.id,
            summary=InterviewSummary(**session.summary_json)
        )
    
    # Get all questions and answers for this session
    questions = db.query(InterviewQuestion).filter(
        InterviewQuestion.session_id == request.session_id
    ).order_by(InterviewQuestion.idx).all()
    
    answers = db.query(InterviewAnswer).filter(
        InterviewAnswer.session_id == request.session_id
    ).all()
    
    # Verify all questions have been answered
    if len(answers) < len(questions):
        raise HTTPException(
            status_code=400,
            detail=f"Not all questions have been answered. Answered: {len(answers)}/{len(questions)}"
        )
    
    # Build data structures for summarization
    questions_data = [
        {
            "idx": q.idx,
            "type": q.type,
            "competency": q.competency,
            "question_text": q.question_text
        }
        for q in questions
    ]
    
    answers_data = [
        {
            "question_id": a.question_id,
            "user_answer": a.user_answer_text,
            "score_overall": a.score_overall,
            "score_relevance": a.score_relevance,
            "score_clarity": a.score_clarity,
            "score_structure": a.score_structure,
            "score_impact": a.score_impact,
            "coach_notes": a.coach_notes
        }
        for a in answers
    ]
    
    # Generate summary using LLM service
    summary_data = LLMService.summarize_session(
        job_title=session.job_title,
        seniority=session.seniority,
        questions=questions_data,
        answers=answers_data
    )
    
    # Update session with summary and mark as completed
    session.status = "completed"
    session.overall_score = summary_data["overall_score"]
    session.summary_json = summary_data
    session.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(session)
    
    return InterviewFinishResponse(
        session_id=session.id,
        summary=InterviewSummary(**summary_data)
    )


@router.get("/session/{session_id}")
def get_session(session_id: str, db: Session = Depends(get_db)):
    """
    Get interview session details (optional endpoint for frontend to fetch state).
    """
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    questions = db.query(InterviewQuestion).filter(
        InterviewQuestion.session_id == session_id
    ).order_by(InterviewQuestion.idx).all()
    
    answers = db.query(InterviewAnswer).filter(
        InterviewAnswer.session_id == session_id
    ).all()
    
    return {
        "session_id": session.id,
        "job_title": session.job_title,
        "seniority": session.seniority,
        "language": session.language,
        "status": session.status,
        "num_questions": session.num_questions,
        "questions": [
            {
                "id": q.id,
                "idx": q.idx,
                "type": q.type,
                "competency": q.competency,
                "question_text": q.question_text
            }
            for q in questions
        ],
        "answers_count": len(answers),
        "overall_score": session.overall_score,
        "summary": session.summary_json
    }


@router.get("/question/{question_id}/audio")
async def get_question_audio(question_id: int, db: Session = Depends(get_db)):
    """
    Get audio version of a specific question using TTS.
    Returns MP3 audio file.
    """
    # Get the question
    question = db.query(InterviewQuestion).filter(
        InterviewQuestion.id == question_id
    ).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Generate audio using TTS
    result = await TTSService.synthesize_speech(question.question_text)
    
    # If we have audio bytes, return them
    if result.get("audio_bytes"):
        return Response(
            content=result["audio_bytes"],
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"attachment; filename=question_{question_id}.mp3"
            }
        )
    
    # Otherwise return error
    raise HTTPException(
        status_code=503,
        detail="TTS service not available. Please configure ELEVENLABS_API_KEY"
    )

