"""
Conversational Interview Service using LangChain + OpenAI

This replaces the static question system with a dynamic conversational AI
that adapts to the candidate's answers in real-time.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.config import settings

# Try to import LangChain
try:
    from langchain_openai import ChatOpenAI
    from langchain.memory import ConversationBufferMemory
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain.schema import HumanMessage, AIMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️ LangChain not installed. Install with: pip install langchain langchain-openai")


class ConversationalInterviewService:
    """
    AI Interview Agent that conducts natural, adaptive conversations.
    
    Features:
    - Remembers conversation history
    - Asks follow-up questions based on answers
    - Adapts difficulty and topics based on candidate's responses
    - Natural conversation flow like a real interviewer
    """
    
    def __init__(
        self,
        job_title: str,
        seniority: str,
        num_questions: int = 5,
        session_id: Optional[str] = None
    ):
        """Initialize the conversational interview agent."""
        self.job_title = job_title
        self.seniority = seniority
        self.num_questions = num_questions
        self.session_id = session_id or f"session-{datetime.now().timestamp()}"
        
        # Conversation state
        self.questions_asked = 0
        self.conversation_history: List[Dict[str, str]] = []
        self.topics_covered: List[str] = []
        
        # Initialize LangChain components
        if LANGCHAIN_AVAILABLE and settings.openai_api_key:
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",  # or "gpt-4" for better quality
                temperature=0.7,
                openai_api_key=settings.openai_api_key
            )
            
            # Memory to track conversation
            self.memory = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history"
            )
            
            # System prompt for the AI interviewer
            self.system_prompt = self._create_system_prompt()
        else:
            self.llm = None
            self.memory = None
            print("⚠️ Conversational AI not available - using fallback")
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the AI interviewer."""
        return f"""You are an expert technical interviewer conducting a {self.seniority} {self.job_title} interview.

Your role:
1. Conduct a natural, conversational interview (not a rigid Q&A session)
2. Ask thoughtful questions that assess the candidate's skills and experience
3. Listen to their answers and ask relevant follow-up questions
4. Adapt your questions based on their responses
5. Be encouraging and help them showcase their abilities
6. Keep questions clear and concise (2-3 sentences)
7. Cover different topics: technical skills, past experience, problem-solving, teamwork, etc.

Interview goals:
- Total questions to ask: {self.num_questions}
- Current questions asked: {{questions_asked}}
- Topics to cover: Technical expertise, past projects, problem-solving, teamwork, career goals

Interview style:
- Be conversational and natural (like a real person)
- Show interest in their answers ("That's interesting!", "Tell me more about...", etc.)
- Ask follow-up questions when they mention something important
- Vary your question types (technical, behavioral, situational)
- Don't just move to the next topic - explore their answers

Remember: This should feel like a real conversation with a human interviewer, not a robotic Q&A session!"""
    
    def start_interview(self) -> Dict[str, Any]:
        """Start the interview with an opening greeting."""
        if not self.llm:
            return self._fallback_start()
        
        try:
            # Opening message
            opening_prompt = f"""Start the interview by:
1. Greeting the candidate warmly
2. Briefly introducing the role ({self.seniority} {self.job_title})
3. Asking them to introduce themselves

Keep it conversational and friendly (2-3 sentences).
"""
            
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=opening_prompt)
            ]
            
            response = self.llm.invoke(messages)
            ai_message = response.content
            
            # Save to history
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_message,
                "timestamp": datetime.now().isoformat(),
                "type": "greeting"
            })
            
            self.questions_asked = 0
            
            return {
                "message": ai_message,
                "type": "greeting",
                "questions_asked": self.questions_asked,
                "total_questions": self.num_questions
            }
            
        except Exception as e:
            print(f"Error starting interview: {e}")
            return self._fallback_start()
    
    def process_answer(self, user_answer: str) -> Dict[str, Any]:
        """
        Process the candidate's answer and generate the next question/response.
        
        This is the core of the conversational AI - it:
        1. Understands what the candidate said
        2. Decides what to ask next (follow-up or new topic)
        3. Generates a natural response
        """
        if not self.llm:
            return self._fallback_response(user_answer)
        
        try:
            # Add user answer to history
            self.conversation_history.append({
                "role": "user",
                "content": user_answer,
                "timestamp": datetime.now().isoformat()
            })
            
            # Determine if we should continue or wrap up
            is_final_question = self.questions_asked >= self.num_questions - 1
            
            # Create prompt for next response
            if is_final_question:
                next_prompt = f"""The candidate just answered: "{user_answer}"

This is the LAST question of the interview.

1. Acknowledge their answer briefly
2. Ask one final, important question about their career goals or why they want this role
3. Keep it conversational

Remember: This should feel like a natural conversation, not a robotic response!"""
            else:
                next_prompt = f"""The candidate just answered: "{user_answer}"

Based on their answer:
1. If they mentioned something interesting, ask a follow-up question about it
2. If the topic is exhausted, transition naturally to a new relevant topic
3. Show you're listening ("I see...", "That's interesting...", etc.)
4. Ask your next question

Questions asked so far: {self.questions_asked + 1}/{self.num_questions}

Remember: Be conversational and natural, like a real interviewer!"""
            
            # Build message history for context
            messages = [SystemMessage(content=self.system_prompt)]
            
            # Add recent conversation (last 6 messages for context)
            recent_history = self.conversation_history[-6:]
            for msg in recent_history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))
            
            # Add current prompt
            messages.append(HumanMessage(content=next_prompt))
            
            # Get AI response
            response = self.llm.invoke(messages)
            ai_message = response.content
            
            # Update state
            self.questions_asked += 1
            
            # Save AI response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_message,
                "timestamp": datetime.now().isoformat(),
                "type": "follow_up" if not is_final_question else "final_question"
            })
            
            return {
                "message": ai_message,
                "type": "follow_up" if not is_final_question else "final_question",
                "questions_asked": self.questions_asked,
                "total_questions": self.num_questions,
                "is_complete": is_final_question
            }
            
        except Exception as e:
            print(f"Error processing answer: {e}")
            return self._fallback_response(user_answer)
    
    def end_interview(self) -> Dict[str, Any]:
        """Generate a closing message for the interview."""
        if not self.llm:
            return self._fallback_end()
        
        try:
            closing_prompt = """Generate a warm closing message that:
1. Thanks the candidate for their time
2. Briefly mentions what impressed you
3. Explains next steps will be communicated

Keep it professional but friendly (2-3 sentences)."""
            
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=closing_prompt)
            ]
            
            response = self.llm.invoke(messages)
            ai_message = response.content
            
            return {
                "message": ai_message,
                "type": "closing",
                "conversation_history": self.conversation_history
            }
            
        except Exception as e:
            print(f"Error ending interview: {e}")
            return self._fallback_end()
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the entire interview conversation."""
        return {
            "session_id": self.session_id,
            "job_title": self.job_title,
            "seniority": self.seniority,
            "questions_asked": self.questions_asked,
            "total_questions": self.num_questions,
            "conversation_history": self.conversation_history,
            "topics_covered": self.topics_covered
        }
    
    # Fallback methods for when LangChain is not available
    
    def _fallback_start(self) -> Dict[str, Any]:
        """Fallback opening when LangChain is not available."""
        return {
            "message": f"Hello! Thank you for interviewing for the {self.seniority} {self.job_title} position. Let's begin by having you tell me a bit about yourself and your relevant experience.",
            "type": "greeting",
            "questions_asked": 0,
            "total_questions": self.num_questions
        }
    
    def _fallback_response(self, user_answer: str) -> Dict[str, Any]:
        """Fallback response when LangChain is not available."""
        self.questions_asked += 1
        
        templates = [
            "Thank you for that answer. Can you tell me about a challenging project you've worked on?",
            "I see. How do you approach problem-solving in your work?",
            "Interesting. Can you describe your experience with teamwork and collaboration?",
            "Great. What are your career goals for the next few years?",
            "Thank you. Why are you interested in this particular role?"
        ]
        
        is_final = self.questions_asked >= self.num_questions
        
        if self.questions_asked <= len(templates):
            message = templates[self.questions_asked - 1]
        else:
            message = "Thank you for sharing that."
        
        return {
            "message": message,
            "type": "follow_up" if not is_final else "final_question",
            "questions_asked": self.questions_asked,
            "total_questions": self.num_questions,
            "is_complete": is_final
        }
    
    def _fallback_end(self) -> Dict[str, Any]:
        """Fallback closing when LangChain is not available."""
        return {
            "message": "Thank you for your time today. We'll review your responses and be in touch soon. Have a great day!",
            "type": "closing",
            "conversation_history": []
        }

