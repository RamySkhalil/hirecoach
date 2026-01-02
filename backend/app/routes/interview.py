"""
Interview-related API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel

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
        status="active",
        program_metadata=request.program_metadata
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


class VoiceInterviewCompleteRequest(BaseModel):
    """Request model for completing a voice interview."""
    transcript: list
    questions_asked: int


@router.post("/voice-session/{session_id}/complete")
def complete_voice_interview(
    session_id: str,
    request: VoiceInterviewCompleteRequest,
    db: Session = Depends(get_db)
):
    """
    Complete a voice interview session and generate a detailed report.
    
    This endpoint is called by the LiveKit voice agent when the interview ends.
    It saves the transcript and generates a comprehensive summary report.
    """
    try:
        # Validate session exists
        session = db.query(InterviewSession).filter(
            InterviewSession.id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Interview session not found")
        
        # If already completed, return existing summary
        if session.status == "completed" and session.summary_json:
            return {
                "message": "Interview already completed",
                "session_id": session_id,
                "summary": session.summary_json
            }
        
        # Validate transcript data
        if not request.transcript or len(request.transcript) == 0:
            print(f"⚠️ Empty transcript received for session {session_id}")
            # Still save empty transcript to mark session as attempted
            session.transcript_json = []
            session.status = "in_progress"
            db.commit()
            return {
                "message": "Transcript saved (empty)",
                "session_id": session_id,
                "summary": None,
                "warning": "No transcript data received. Interview may have been interrupted."
            }
        
        # Store the transcript in the session (even if partial)
        session.transcript_json = request.transcript
        print(f"💾 Saving transcript: {len(request.transcript)} messages, {request.questions_asked} questions asked")
        
        # Generate summary from voice transcript using LLM
        # Extract questions and answers from transcript
        conversation_text = "\n".join([
            f"{'Agent' if item.get('role') == 'assistant' else 'Candidate'}: {item.get('content', '')}"
            for item in request.transcript
        ])
        
        # Use LLM to analyze the conversation and generate report
        from app.services.llm_service import LLMService
        
        try:
            summary_data = LLMService.summarize_voice_interview(
                job_title=session.job_title,
                seniority=session.seniority,
                conversation_transcript=conversation_text,
                questions_asked=request.questions_asked,
                total_questions=session.num_questions
            )
        except Exception as llm_error:
            # If LLM fails (e.g., quota exceeded), create a basic summary
            print(f"⚠️ LLM summary generation failed: {llm_error}")
            print(f"   Creating fallback summary from transcript...")
            
            # Create basic summary from transcript
            user_messages = [t for t in request.transcript if t.get('role') == 'user']
            assistant_messages = [t for t in request.transcript if t.get('role') == 'assistant']
            
            summary_data = {
                "overall_score": 70,  # Default score
                "strengths": [
                    "Participated in the interview",
                    "Provided responses to questions"
                ] if len(user_messages) > 0 else ["Interview session started"],
                "weaknesses": [
                    "Interview was incomplete",
                    "Limited data available for comprehensive evaluation"
                ],
                "action_plan": [
                    "Complete a full interview session for better evaluation",
                    "Answer all questions to receive detailed feedback"
                ],
                "suggested_roles": [session.job_title] if session.job_title else [],
                "questions_completed": request.questions_asked,
                "total_questions": session.num_questions,
                "completion_status": "partial",
                "note": "Report generated from partial transcript due to technical limitations"
            }
        
        # Add completion info (ensure questions_completed is set)
        if "questions_completed" not in summary_data:
            summary_data["questions_completed"] = request.questions_asked
        summary_data["total_questions"] = session.num_questions
        summary_data["completion_status"] = "completed" if request.questions_asked >= session.num_questions else "partial"
        
        # Update session with summary and mark as completed
        session.status = "completed"
        session.overall_score = summary_data.get("overall_score", 75)
        session.summary_json = summary_data
        session.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(session)
        
        return {
            "message": "Interview completed successfully",
            "session_id": session_id,
            "summary": summary_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error completing voice interview: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


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


@router.get("/session/{session_id}/report")
def get_or_generate_report(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get or generate interview report at any time.
    Works even if interview was interrupted or incomplete.
    Includes retry logic to handle race conditions when transcript is being saved.
    """
    import time
    
    # Validate session exists
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")
    
    print(f"📊 Report request for session {session_id}")
    
    # If already has a complete summary, return it
    if session.summary_json and session.status == "completed":
        print(f"✅ Returning existing completed report")
        return {
            "session_id": session_id,
            "status": "completed",
            "summary": session.summary_json,
            "questions_completed": session.num_questions,
            "total_questions": session.num_questions
        }
    
    # Retry logic: Check for transcript up to 3 times with exponential backoff
    # This handles race conditions where frontend navigates before backend saves
    transcript_data = None
    max_retries = 3
    retry_delay = 0.5  # Start with 500ms
    
    for attempt in range(1, max_retries + 1):
        # Refresh session to get latest data from database
        db.refresh(session)
        
        # Get transcript data
        transcript_data = session.transcript_json if hasattr(session, 'transcript_json') else None
        
        print(f"   Attempt {attempt}/{max_retries}: Checking transcript...")
        print(f"   - transcript_json exists: {transcript_data is not None}")
        print(f"   - transcript length: {len(transcript_data) if transcript_data else 0}")
        
        # Lower threshold: Accept even 1 message (greeting counts as engagement)
        # This allows reports for users who answered at least 1 question
        has_transcript = transcript_data and len(transcript_data) >= 1
        
        if has_transcript:
            print(f"✅ Found transcript with {len(transcript_data)} messages")
            break  # Found transcript, exit retry loop
        
        if attempt < max_retries:
            print(f"   ⏳ No transcript yet, waiting {retry_delay}s before retry...")
            time.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff: 0.5s, 1s, 2s
    
    # Final check after retries
    if not transcript_data or len(transcript_data) < 1:
        print(f"⚠️ No transcript found after {max_retries} attempts")
        return {
            "session_id": session_id,
            "status": "in_progress",
            "message": "Interview in progress - not enough data yet for a report. Please answer at least one question.",
            "summary": None,
            "transcript_length": len(transcript_data) if transcript_data else 0,
            "debug_info": {
                "attempts": max_retries,
                "transcript_exists": transcript_data is not None,
                "transcript_length": len(transcript_data) if transcript_data else 0
            }
        }
    
    # Generate report from whatever transcript we have
    print(f"📝 Generating report from transcript...")
    print(f"   - Transcript messages: {len(transcript_data)}")
    
    conversation_text = "\n".join([
        f"{'Agent' if item.get('role') == 'assistant' else 'Candidate'}: {item.get('content', '')}"
        for item in transcript_data
    ])
    
    # Count questions asked (agent messages, excluding greeting)
    questions_asked = len([t for t in transcript_data if t.get('role') == 'assistant']) // 2
    # If we have at least 1 assistant message and 1 user message, count as 1 question
    if len(transcript_data) >= 2:
        assistant_messages = len([t for t in transcript_data if t.get('role') == 'assistant'])
        user_messages = len([t for t in transcript_data if t.get('role') == 'user'])
        if assistant_messages >= 1 and user_messages >= 1:
            questions_asked = max(1, questions_asked)  # At least 1 question if we have Q&A
    
    print(f"   - Questions asked: {questions_asked}")
    print(f"   - Total questions: {session.num_questions}")
    
    # Generate summary
    from app.services.llm_service import LLMService
    
    print(f"🤖 Calling LLM to generate summary...")
    summary_data = LLMService.summarize_voice_interview(
        job_title=session.job_title,
        seniority=session.seniority,
        conversation_transcript=conversation_text,
        questions_asked=questions_asked,
        total_questions=session.num_questions
    )
    
    print(f"✅ LLM summary generated")
    print(f"   - Overall score: {summary_data.get('overall_score', 'N/A')}")
    
    # Add completion status to summary
    summary_data["questions_completed"] = questions_asked
    summary_data["total_questions"] = session.num_questions
    summary_data["completion_status"] = "completed" if questions_asked >= session.num_questions else "partial"
    
    # Update session with summary
    session.summary_json = summary_data
    session.overall_score = summary_data.get("overall_score", 0)
    if questions_asked >= session.num_questions:
        session.status = "completed"
        session.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(session)
    
    print(f"💾 Report saved to database")
    
    return {
        "session_id": session_id,
        "status": session.status,
        "summary": summary_data,
        "questions_completed": questions_asked,
        "total_questions": session.num_questions
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

