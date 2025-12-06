"""
LLM Service for interview generation and evaluation.
Supports OpenAI GPT-4 and Anthropic Claude.
"""
from typing import List, Dict, Any
import json
import os
from app.config import settings

import dotenv
dotenv.load_dotenv()    

# Fix SSL certificate issues on Windows
try:
    import certifi
    os.environ['SSL_CERT_FILE'] = certifi.where()
except ImportError:
    pass

# Try to import AI libraries, fall back to dummy if not available
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class LLMService:
    """
    Service for interacting with Language Model APIs.
    Provides methods for generating interview questions, evaluating answers, and summarizing sessions.
    """
    
    @staticmethod
    def _get_client():
        """Get the appropriate LLM client based on configuration."""
        if settings.llm_provider == "openai":
            if not OPENAI_AVAILABLE or not settings.openai_api_key:
                return None
            return OpenAI(api_key=settings.openai_api_key)
        elif settings.llm_provider == "anthropic":
            if not ANTHROPIC_AVAILABLE or not settings.anthropic_api_key:
                return None
            return Anthropic(api_key=settings.anthropic_api_key)
        return None
    
    @staticmethod
    def _call_openai(client: OpenAI, messages: List[Dict[str, str]], response_format: str = "text") -> str:
        """Call OpenAI API."""
        kwargs = {
            "model": settings.llm_model,
            "messages": messages,
            "temperature": settings.llm_temperature,
        }
        
        # Add JSON mode if requested and supported
        if response_format == "json" and "gpt-4" in settings.llm_model:
            kwargs["response_format"] = {"type": "json_object"}
        
        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    @staticmethod
    def _call_anthropic(client: Anthropic, messages: List[Dict[str, str]]) -> str:
        """Call Anthropic API."""
        # Convert messages format for Anthropic
        system_msg = None
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                user_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        kwargs = {
            "model": settings.llm_model,
            "max_tokens": 4096,
            "temperature": settings.llm_temperature,
            "messages": user_messages
        }
        
        if system_msg:
            kwargs["system"] = system_msg
        
        response = client.messages.create(**kwargs)
        return response.content[0].text
    
    @staticmethod
    def _call_llm(messages: List[Dict[str, str]], response_format: str = "text") -> str:
        """Call the configured LLM."""
        client = LLMService._get_client()
        
        if not client:
            # Fall back to dummy implementation
            return None
        
        try:
            if settings.llm_provider == "openai":
                return LLMService._call_openai(client, messages, response_format)
            elif settings.llm_provider == "anthropic":
                return LLMService._call_anthropic(client, messages)
        except Exception as e:
            print(f"LLM API Error: {e}")
            return None
    
    @staticmethod
    def generate_interview_plan(
        job_title: str,
        seniority: str,
        language: str,
        num_questions: int
    ) -> List[Dict[str, Any]]:
        """
        Generate a structured interview plan with questions.
        """
        prompt = f"""You are an expert technical interviewer. Generate {num_questions} interview questions for a {seniority} {job_title} position.

Requirements:
- Mix question types: technical, behavioral, situational, and general
- Each question should test a specific competency
- Questions should be appropriate for {seniority} level
- Language: {language}

Return a JSON array with this exact structure:
[
  {{
    "idx": 1,
    "type": "technical",
    "competency": "Problem Solving",
    "question_text": "Your question here..."
  }},
  ...
]

Types must be one of: technical, behavioral, situational, general
Competencies examples: Problem Solving, Leadership, Communication, Technical Expertise, Adaptability, Strategic Thinking, Teamwork, Innovation

Generate exactly {num_questions} questions now."""

        messages = [
            {"role": "system", "content": "You are an expert interview coach. Always respond with valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = LLMService._call_llm(messages, response_format="json")
        
        if response:
            try:
                questions = json.loads(response)
                # Validate and return
                if isinstance(questions, list) and len(questions) > 0:
                    return questions
            except json.JSONDecodeError:
                print("Failed to parse LLM response as JSON")
        
        # Fall back to dummy implementation
        return LLMService._generate_dummy_questions(job_title, seniority, language, num_questions)
    
    @staticmethod
    def _generate_dummy_questions(job_title: str, seniority: str, language: str, num_questions: int) -> List[Dict[str, Any]]:
        """Dummy implementation for when LLM is not available."""
        import random
        
        question_templates = {
            "technical": [
                f"Describe your experience with key technologies used in {job_title} roles.",
                f"What technical challenges have you faced in {job_title} work, and how did you overcome them?",
                f"Explain a technical project you're proud of in the {job_title} domain.",
                f"How do you stay updated with the latest trends and technologies in {job_title}?",
            ],
            "behavioral": [
                "Tell me about a time when you had to work under pressure. How did you handle it?",
                "Describe a situation where you disagreed with a colleague. How did you resolve it?",
                "Give an example of how you've demonstrated leadership in your role.",
                "Tell me about a time you failed. What did you learn from it?",
            ],
            "situational": [
                f"If you joined our team as a {job_title}, what would be your priorities in the first 90 days?",
                "How would you handle a situation where you're given conflicting priorities?",
                f"Imagine you're working on a critical {job_title} project with a tight deadline, and you discover a major issue. What do you do?",
                "How would you approach mentoring a junior team member?",
            ],
            "general": [
                f"Why are you interested in this {job_title} position?",
                "What are your career goals for the next 3-5 years?",
                "What motivates you in your work?",
                f"What do you think are the most important skills for a {seniority} {job_title}?",
            ]
        }
        
        competencies = {
            "technical": ["Technical Expertise", "Problem Solving", "Innovation"],
            "behavioral": ["Teamwork", "Communication", "Adaptability", "Leadership"],
            "situational": ["Decision Making", "Strategic Thinking", "Conflict Resolution"],
            "general": ["Self-Awareness", "Career Vision", "Motivation"]
        }
        
        questions = []
        question_types = ["technical", "behavioral", "situational", "general"]
        
        for i in range(num_questions):
            q_type = question_types[i % len(question_types)]
            templates = question_templates[q_type]
            comp_options = competencies[q_type]
            
            questions.append({
                "idx": i + 1,
                "type": q_type,
                "competency": random.choice(comp_options),
                "question_text": templates[i % len(templates)]
            })
        
        return questions
    
    @staticmethod
    def evaluate_answer(
        question_text: str,
        question_type: str,
        user_answer: str,
        job_title: str,
        seniority: str
    ) -> Dict[str, Any]:
        """
        Evaluate a user's answer to an interview question.
        """
        prompt = f"""You are an expert interview coach evaluating a candidate's answer.

Job: {seniority} {job_title}
Question Type: {question_type}
Question: {question_text}

Candidate's Answer:
{user_answer}

Evaluate this answer and provide scores (0-100) for:
1. Relevance - Is the answer on-topic and addresses the question?
2. Clarity - Is the answer clear, well-articulated, and easy to understand?
3. Structure - Is the answer well-organized with logical flow?
4. Impact - Does it show results, specific examples, or measurable outcomes?

Also provide constructive coaching notes (2-3 sentences) on how to improve.

Return a JSON object with this exact structure:
{{
  "score_overall": 85,
  "dimension_scores": {{
    "relevance": 90,
    "clarity": 85,
    "structure": 80,
    "impact": 85
  }},
  "coach_notes": "Your constructive feedback here..."
}}

The overall score should be the average of the four dimension scores."""

        messages = [
            {"role": "system", "content": "You are an expert interview coach. Always respond with valid JSON. Be fair but constructive in your evaluation."},
            {"role": "user", "content": prompt}
        ]
        
        response = LLMService._call_llm(messages, response_format="json")
        
        if response:
            try:
                evaluation = json.loads(response)
                # Validate structure
                if "score_overall" in evaluation and "dimension_scores" in evaluation and "coach_notes" in evaluation:
                    return evaluation
            except json.JSONDecodeError:
                print("Failed to parse LLM evaluation as JSON")
        
        # Fall back to dummy implementation
        return LLMService._evaluate_dummy(user_answer, question_type)
    
    @staticmethod
    def _evaluate_dummy(user_answer: str, question_type: str) -> Dict[str, Any]:
        """
        Dummy evaluation for when LLM is not available.
        Note: This is a fallback only. For real evaluation, configure OPENAI_API_KEY.
        """
        import random
        
        # Check answer quality
        word_count = len(user_answer.split())
        char_count = len(user_answer.strip())
        
        # Penalize very short or nonsense answers
        if word_count < 5 or char_count < 20:
            # Very poor answer
            relevance = random.randint(10, 25)
            clarity = random.randint(10, 25)
            structure = random.randint(10, 25)
            impact = random.randint(10, 25)
        elif word_count < 15:
            # Short answer
            relevance = random.randint(25, 45)
            clarity = random.randint(25, 45)
            structure = random.randint(25, 45)
            impact = random.randint(25, 45)
        elif word_count < 30:
            # Decent length
            base_score = 50 + random.randint(-5, 5)
            relevance = max(35, min(70, base_score + random.randint(-10, 10)))
            clarity = max(35, min(70, base_score + random.randint(-10, 10)))
            structure = max(35, min(70, base_score + random.randint(-10, 10)))
            impact = max(35, min(70, base_score + random.randint(-10, 10)))
        else:
            # Good length
            base_score = 60 + random.randint(-5, 10)
            relevance = max(45, min(85, base_score + random.randint(-10, 15)))
            clarity = max(45, min(85, base_score + random.randint(-10, 15)))
            structure = max(45, min(85, base_score + random.randint(-10, 15)))
            impact = max(45, min(85, base_score + random.randint(-10, 15)))
        
        overall = (relevance + clarity + structure + impact) // 4
        
        # Provide feedback based on score
        if overall < 30:
            coach_notes = (
                "⚠️ Your answer needs significant improvement. It appears too brief or lacks substance. "
                "Please provide more detailed responses with specific examples and explanations. "
                "Aim for at least 50-100 words with concrete details."
            )
        elif overall < 50:
            coach_notes = (
                "Your answer is too short and needs more development. Try to elaborate with specific examples, "
                "use the STAR method (Situation, Task, Action, Result) for behavioral questions, and aim for "
                "at least 100-200 words with meaningful content."
            )
        elif overall < 70:
            coach_notes = (
                "Good start, but your answer could be stronger. Add more specific examples, quantifiable results, "
                "and connect your experience more directly to the question. Consider the STAR method for structure."
            )
        else:
            feedback_templates = {
                "technical": [
                    "Your technical explanation shows good understanding. Consider adding more specific examples or metrics.",
                    "Good technical depth. You could discuss trade-offs or alternative approaches you considered.",
                ],
                "behavioral": [
                    "Good example. Using the STAR method more explicitly could make it even stronger.",
                    "Nice story. Emphasize the specific actions you took and the measurable impact.",
                ],
                "situational": [
                    "Thoughtful approach. Consider discussing how you'd prioritize competing demands.",
                    "Good response. Strengthen it by mentioning how you'd involve stakeholders or measure success.",
                ],
                "general": [
                    "Good reflection. Connect your goals more explicitly to the role and company.",
                    "Thoughtful response. Provide more specific examples to illustrate your points.",
                ]
            }
            coach_notes = random.choice(feedback_templates.get(question_type, feedback_templates["general"]))
        
        # Add warning that this is dummy mode
        coach_notes += "\n\n💡 Note: For accurate AI-powered evaluation, please configure OPENAI_API_KEY in backend/.env"
        
        return {
            "score_overall": overall,
            "dimension_scores": {
                "relevance": relevance,
                "clarity": clarity,
                "structure": structure,
                "impact": impact
            },
            "coach_notes": coach_notes
        }
    
    @staticmethod
    def summarize_session(
        job_title: str,
        seniority: str,
        questions: List[Dict[str, Any]],
        answers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of the interview session.
        """
        # Build a summary of Q&A
        qa_summary = []
        for i, (q, a) in enumerate(zip(questions, answers)):
            qa_summary.append(f"Q{i+1} ({q['type']}): {q['question_text']}")
            qa_summary.append(f"Score: {a['score_overall']}/100")
            qa_summary.append(f"Answer excerpt: {a['user_answer'][:200]}...")
            qa_summary.append("")
        
        qa_text = "\n".join(qa_summary)
        
        avg_score = sum(a["score_overall"] for a in answers) // len(answers) if answers else 0
        
        prompt = f"""You are an expert career coach reviewing a mock interview.

Job: {seniority} {job_title}
Overall Score: {avg_score}/100

Interview Performance:
{qa_text}

Based on this interview performance, provide a comprehensive analysis with:

1. STRENGTHS (2-4 items): Specific things the candidate did well
2. WEAKNESSES (2-4 items): Areas that need improvement
3. ACTION PLAN (3-5 items): Concrete, actionable steps to improve
4. SUGGESTED ROLES (2-4 items): Job titles/levels that match their performance

Return a JSON object with this exact structure:
{{
  "overall_score": {avg_score},
  "strengths": ["strength 1", "strength 2", ...],
  "weaknesses": ["weakness 1", "weakness 2", ...],
  "action_plan": ["action 1", "action 2", ...],
  "suggested_roles": ["role 1", "role 2", ...]
}}

Be specific, constructive, and encouraging."""

        messages = [
            {"role": "system", "content": "You are an expert career coach. Always respond with valid JSON. Be honest but supportive."},
            {"role": "user", "content": prompt}
        ]
        
        response = LLMService._call_llm(messages, response_format="json")
        
        if response:
            try:
                summary = json.loads(response)
                if all(key in summary for key in ["overall_score", "strengths", "weaknesses", "action_plan", "suggested_roles"]):
                    return summary
            except json.JSONDecodeError:
                print("Failed to parse LLM summary as JSON")
        
        # Fall back to dummy implementation
        return LLMService._summarize_dummy(job_title, seniority, questions, answers)
    
    @staticmethod
    def _summarize_dummy(job_title: str, seniority: str, questions: List[Dict[str, Any]], answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Dummy summarization for when LLM is not available."""
        overall_score = sum(a["score_overall"] for a in answers) // len(answers) if answers else 0
        
        dimension_avgs = {
            "relevance": sum(a.get("score_relevance", 0) for a in answers) // len(answers) if answers else 0,
            "clarity": sum(a.get("score_clarity", 0) for a in answers) // len(answers) if answers else 0,
            "structure": sum(a.get("score_structure", 0) for a in answers) // len(answers) if answers else 0,
            "impact": sum(a.get("score_impact", 0) for a in answers) // len(answers) if answers else 0,
        }
        
        strengths = []
        if dimension_avgs["relevance"] >= 75:
            strengths.append("Strong relevance - you consistently provided on-topic, applicable answers")
        if dimension_avgs["clarity"] >= 75:
            strengths.append("Excellent communication - your answers were clear and easy to follow")
        if dimension_avgs["structure"] >= 75:
            strengths.append("Well-structured responses - you organized your thoughts logically")
        if dimension_avgs["impact"] >= 75:
            strengths.append("Impactful examples - you demonstrated meaningful results and outcomes")
        
        if not strengths:
            strengths.append("You showed enthusiasm and engagement throughout the interview")
            strengths.append("You provided thoughtful answers to challenging questions")
        
        weaknesses = []
        if dimension_avgs["relevance"] < 65:
            weaknesses.append("Answer relevance - try to stay more focused on what the question is asking")
        if dimension_avgs["clarity"] < 65:
            weaknesses.append("Communication clarity - work on expressing your thoughts more concisely")
        if dimension_avgs["structure"] < 65:
            weaknesses.append("Response structure - consider using frameworks like STAR to organize answers")
        if dimension_avgs["impact"] < 65:
            weaknesses.append("Demonstrating impact - include more specific metrics and measurable outcomes")
        
        if not weaknesses:
            weaknesses.append("Minor: Could provide even more specific examples in some answers")
        
        action_plan = []
        if overall_score < 70:
            action_plan.extend([
                "Practice the STAR method (Situation, Task, Action, Result) for behavioral questions",
                f"Research common {job_title} interview questions and prepare answers",
                "Conduct 2-3 more mock interviews to build confidence"
            ])
        elif overall_score < 80:
            action_plan.extend([
                f"Deepen your technical knowledge in key {job_title} areas",
                "Prepare more quantifiable examples of your achievements",
                "Practice articulating complex ideas more concisely"
            ])
        else:
            action_plan.extend([
                "You're interview-ready! Focus on researching specific companies",
                "Prepare thoughtful questions to ask interviewers",
                "Continue practicing to maintain your strong performance"
            ])
        
        suggested_roles = []
        if overall_score >= 80:
            suggested_roles.append(f"{seniority.title()} {job_title}")
            if seniority != "senior":
                suggested_roles.append(f"Senior {job_title}")
        elif overall_score >= 70:
            suggested_roles.append(f"{seniority.title()} {job_title}")
            suggested_roles.append(f"{job_title} - smaller companies or startups")
        else:
            if seniority != "junior":
                suggested_roles.append(f"Junior {job_title}")
            suggested_roles.append(f"Entry-level {job_title}")
            suggested_roles.append(f"{job_title} Intern or Associate roles")
        
        return {
            "overall_score": overall_score,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "action_plan": action_plan,
            "suggested_roles": suggested_roles
        }
    
    @staticmethod
    def summarize_voice_interview(
        job_title: str,
        seniority: str,
        conversation_transcript: str,
        questions_asked: int,
        total_questions: int
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of a voice/conversational interview session.
        
        This analyzes the full conversation transcript from a LiveKit voice interview.
        """
        prompt = f"""You are an expert career coach reviewing a voice mock interview.

Job: {seniority} {job_title}
Questions Asked: {questions_asked}/{total_questions}
{"⚠️ INTERVIEW PARTIALLY COMPLETED - Candidate left early" if questions_asked < total_questions else "✅ INTERVIEW FULLY COMPLETED"}

Full Interview Conversation:
{conversation_transcript}

Based on this interview conversation, provide a comprehensive analysis with:

1. OVERALL SCORE (0-100): Rate the candidate's overall interview performance
   - If incomplete, score based on what was demonstrated so far
   - Consider engagement level and reason for early exit (if apparent)

2. STRENGTHS (2-4 items): Specific things the candidate did well
   - Focus on demonstrated competencies
   - Highlight positive communication patterns

3. WEAKNESSES (2-4 items): Areas that need improvement
   - If interview was cut short, mention completion as a weakness
   - Identify any communication gaps or areas lacking depth
   - Note if responses seemed rushed or incomplete

4. ACTION PLAN (3-5 items): Concrete, actionable steps to improve
   - If incomplete: Include "Complete full interview sessions to build stamina and consistency"
   - Provide specific, measurable recommendations
   - Prioritize most impactful improvements

5. SUGGESTED ROLES (2-4 items): Job titles/levels that match their performance
   - Be realistic based on demonstrated skills
   - If incomplete interview, suggest roles that match current performance level

Consider:
- Quality and depth of answers
- Communication skills (clarity, confidence, articulation)
- Technical knowledge (if applicable)
- Behavioral examples and storytelling
- Overall professionalism
- Answer relevance to questions
- Commitment to completing the interview

Return a JSON object with this exact structure:
{{
  "overall_score": 78,
  "strengths": ["strength 1", "strength 2", ...],
  "weaknesses": ["weakness 1", "weakness 2", ...],
  "action_plan": ["action 1", "action 2", ...],
  "suggested_roles": ["role 1", "role 2", ...]
}}

Be specific, constructive, and encouraging. Focus on actionable feedback.
If the interview was incomplete, be honest but supportive about the need to complete full sessions."""

        messages = [
            {"role": "system", "content": "You are an expert career coach. Always respond with valid JSON. Be honest but supportive and constructive."},
            {"role": "user", "content": prompt}
        ]
        
        response = LLMService._call_llm(messages, response_format="json")
        
        if response:
            try:
                summary = json.loads(response)
                if all(key in summary for key in ["overall_score", "strengths", "weaknesses", "action_plan", "suggested_roles"]):
                    return summary
            except json.JSONDecodeError:
                print("Failed to parse LLM summary as JSON")
        
        # Fall back to a basic summary
        return {
            "overall_score": 75,
            "strengths": [
                "Completed the voice interview successfully",
                "Engaged in natural conversation with the AI interviewer",
                f"Answered {questions_asked} questions during the session"
            ],
            "weaknesses": [
                "Voice interview analysis requires AI configuration",
                "Unable to provide detailed performance metrics without AI analysis"
            ],
            "action_plan": [
                "Review your interview recording if available",
                "Practice speaking clearly and confidently",
                f"Continue preparing for {job_title} interviews",
                "Focus on providing specific examples in your answers"
            ],
            "suggested_roles": [
                f"{seniority.title()} {job_title}",
                f"{job_title} positions at various companies"
            ]
        }