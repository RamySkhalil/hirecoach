"""
AI Career Agent Service - Personal career coaching assistant.
"""
from typing import Dict, Any, List, Optional
from app.config import settings

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class CareerAgentService:
    """
    AI Career Coach that provides:
    - Career advice and guidance
    - Job role suggestions
    - Skill development recommendations
    - Resume/interview tips
    - Career path planning
    """
    
    @staticmethod
    def _get_llm_client():
        """Get OpenAI client if available."""
        if not OPENAI_AVAILABLE or not settings.openai_api_key:
            return None
        return OpenAI(api_key=settings.openai_api_key)
    
    @staticmethod
    def chat(
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Chat with the AI career agent.
        
        Args:
            message: User's message
            conversation_history: Previous messages in the conversation
            user_context: Optional user info (job title, experience, skills, etc.)
        
        Returns:
            Dict with agent's response and suggestions
        """
        client = CareerAgentService._get_llm_client()
        
        if not client:
            return CareerAgentService._chat_dummy(message)
        
        try:
            # Build conversation history
            messages = [
                {
                    "role": "system",
                    "content": CareerAgentService._get_system_prompt(user_context)
                }
            ]
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history[-10:]:  # Keep last 10 messages for context
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            # Add current message
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Get AI response
            response = client.chat.completions.create(
                model=settings.llm_model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            agent_message = response.choices[0].message.content
            
            # Parse response for structured data (suggestions, action items)
            suggestions = CareerAgentService._extract_suggestions(agent_message)
            action_items = CareerAgentService._extract_action_items(agent_message)
            
            return {
                "message": agent_message,
                "suggestions": suggestions,
                "action_items": action_items,
                "status": "success"
            }
            
        except Exception as e:
            print(f"Career agent chat failed: {e}")
            return CareerAgentService._chat_dummy(message)
    
    @staticmethod
    def _get_system_prompt(user_context: Optional[Dict[str, Any]] = None) -> str:
        """Create system prompt for the career agent."""
        base_prompt = """You are an expert AI Career Coach and mentor. Your role is to:

1. **Provide Personalized Career Guidance**: Offer tailored advice based on the user's experience, goals, and industry.

2. **Suggest Career Paths**: Recommend suitable job roles and career trajectories based on skills and interests.

3. **Skills Development**: Identify skill gaps and recommend specific courses, certifications, or resources.

4. **Job Search Strategy**: Help with resume optimization, interview preparation, and job search tactics.

5. **Career Growth**: Advise on promotions, salary negotiations, and professional development.

6. **Industry Insights**: Share current trends, in-demand skills, and market opportunities.

**Communication Style:**
- Be encouraging and supportive
- Provide specific, actionable advice
- Use examples and real-world scenarios
- Ask clarifying questions when needed
- Be honest about challenges and opportunities
- Celebrate achievements and progress

**Focus Areas:**
- Resume and CV optimization
- Interview preparation and practice
- Skill development and learning paths
- Job search strategies
- Career transitions and pivots
- Salary negotiation
- Professional networking
- Work-life balance
- Industry trends and opportunities
"""
        
        if user_context:
            context_info = "\n**User Context:**\n"
            if user_context.get("job_title"):
                context_info += f"- Current Role: {user_context['job_title']}\n"
            if user_context.get("experience_years"):
                context_info += f"- Experience: {user_context['experience_years']} years\n"
            if user_context.get("skills"):
                context_info += f"- Skills: {', '.join(user_context['skills'])}\n"
            if user_context.get("goals"):
                context_info += f"- Career Goals: {user_context['goals']}\n"
            
            base_prompt += context_info
        
        return base_prompt
    
    @staticmethod
    def _extract_suggestions(message: str) -> List[str]:
        """Extract suggestions from the agent's response."""
        suggestions = []
        
        # Look for common suggestion patterns
        lines = message.split('\n')
        for line in lines:
            line = line.strip()
            # Check for bullet points or numbered lists that look like suggestions
            if line and (
                line.startswith('•') or 
                line.startswith('-') or 
                line.startswith('*') or
                (len(line) > 2 and line[0].isdigit() and line[1] in '.)')
            ):
                # Clean up the suggestion
                suggestion = line.lstrip('•-*0123456789.) ').strip()
                if len(suggestion) > 10:  # Ignore very short lines
                    suggestions.append(suggestion)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    @staticmethod
    def _extract_action_items(message: str) -> List[str]:
        """Extract action items from the agent's response."""
        action_items = []
        
        # Look for action-oriented phrases
        action_keywords = [
            "you should", "i recommend", "consider", "try", "start by",
            "take", "apply", "practice", "update", "learn", "research"
        ]
        
        lines = message.split('.')
        for line in lines:
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in action_keywords):
                action = line.strip()
                if len(action) > 15 and len(action) < 200:
                    action_items.append(action)
        
        return action_items[:3]  # Return top 3 action items
    
    @staticmethod
    def _chat_dummy(message: str) -> Dict[str, Any]:
        """Dummy response when LLM is not available."""
        responses = {
            "default": (
                "I'm your AI Career Coach! To provide personalized advice, "
                "please configure the OPENAI_API_KEY in your backend/.env file.\n\n"
                "Once configured, I can help you with:\n"
                "• Career path guidance and job role suggestions\n"
                "• Skills development and learning recommendations\n"
                "• Resume and interview preparation tips\n"
                "• Job search strategies and networking advice\n"
                "• Salary negotiation and career growth planning"
            ),
            "resume": (
                "For resume advice, I recommend:\n"
                "• Use action verbs and quantify achievements\n"
                "• Tailor your resume to each job application\n"
                "• Keep it concise (1-2 pages)\n"
                "• Highlight relevant skills and experience\n"
                "• Use our CV Analyzer and Rewriter tools!"
            ),
            "interview": (
                "For interview preparation:\n"
                "• Practice common interview questions\n"
                "• Research the company thoroughly\n"
                "• Prepare STAR method examples\n"
                "• Practice with our AI Interview Coach\n"
                "• Ask thoughtful questions to the interviewer"
            )
        }
        
        message_lower = message.lower()
        if any(word in message_lower for word in ["resume", "cv", "curriculum"]):
            response_text = responses["resume"]
        elif any(word in message_lower for word in ["interview", "prepare", "practice"]):
            response_text = responses["interview"]
        else:
            response_text = responses["default"]
        
        return {
            "message": response_text,
            "suggestions": [
                "Configure OPENAI_API_KEY for personalized advice",
                "Use the CV Analyzer to optimize your resume",
                "Practice interviews with our AI Interview Coach"
            ],
            "action_items": [
                "Set up your OpenAI API key for full AI features"
            ],
            "status": "limited"
        }
    
    @staticmethod
    def get_career_suggestions(
        current_role: str,
        skills: List[str],
        experience_years: int,
        interests: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get career path suggestions based on user profile.
        
        Args:
            current_role: Current job title
            skills: List of skills
            experience_years: Years of experience
            interests: Optional list of interests
        
        Returns:
            Dict with career suggestions and growth paths
        """
        client = CareerAgentService._get_llm_client()
        
        if not client:
            return {
                "suggested_roles": ["Configure OPENAI_API_KEY for personalized suggestions"],
                "growth_paths": [],
                "skills_to_learn": []
            }
        
        try:
            interests_text = f" with interests in {', '.join(interests)}" if interests else ""
            
            prompt = f"""Based on this profile:
- Current Role: {current_role}
- Skills: {', '.join(skills)}
- Experience: {experience_years} years{interests_text}

Suggest 5 suitable next career roles and provide:
1. Recommended job titles
2. Career growth paths
3. Skills to develop for advancement

Return as JSON with: suggested_roles, growth_paths, skills_to_learn (each as arrays)"""
            
            response = client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a career advisor. Provide structured career guidance."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"Career suggestions failed: {e}")
            return {
                "suggested_roles": [
                    f"{current_role} (Senior Level)",
                    f"Lead {current_role}",
                    f"{current_role} Manager"
                ],
                "growth_paths": [
                    "Individual Contributor → Senior → Lead",
                    "Individual Contributor → Manager → Director"
                ],
                "skills_to_learn": [
                    "Leadership and communication",
                    "Strategic thinking",
                    "Project management"
                ]
            }

