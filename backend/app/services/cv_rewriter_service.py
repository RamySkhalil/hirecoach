"""
CV Rewriter Service - AI-powered CV rewriting and optimization.
"""
from typing import Dict, Any, Optional
from app.config import settings

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class CVRewriterService:
    """
    Service for rewriting and optimizing CVs with AI.
    """
    
    @staticmethod
    def _get_llm_client():
        """Get OpenAI client if available."""
        if not OPENAI_AVAILABLE or not settings.openai_api_key:
            return None
        return OpenAI(api_key=settings.openai_api_key)
    
    @staticmethod
    def get_style_instructions(style: str) -> str:
        """Get formatting instructions for each style."""
        styles = {
            "modern": (
                "Create a modern, visually appealing CV with:\n"
                "- Clear section headers with subtle styling\n"
                "- Bullet points for achievements\n"
                "- Quantified results where possible\n"
                "- Professional but contemporary language\n"
                "- Skills section with categories\n"
                "- Focus on impact and results"
            ),
            "minimal": (
                "Create a clean, minimal CV with:\n"
                "- Simple section headers\n"
                "- Concise bullet points\n"
                "- White space for readability\n"
                "- Essential information only\n"
                "- No unnecessary details\n"
                "- Focus on clarity and brevity"
            ),
            "executive": (
                "Create an executive-level CV with:\n"
                "- Professional summary highlighting leadership\n"
                "- Strategic achievements and business impact\n"
                "- Board memberships and key appointments\n"
                "- Quantified business results (revenue, growth, savings)\n"
                "- Industry recognition and awards\n"
                "- Focus on leadership and strategic vision"
            ),
            "ats_optimized": (
                "Create an ATS-optimized CV with:\n"
                "- Standard section headers (Experience, Education, Skills)\n"
                "- Keyword-rich content matching job requirements\n"
                "- Simple formatting (no tables, columns, or graphics)\n"
                "- Standard fonts and bullet points\n"
                "- Clear date formats\n"
                "- Industry-specific keywords and skills"
            )
        }
        return styles.get(style, styles["modern"])
    
    @staticmethod
    def rewrite_cv(
        cv_text: str,
        style: str = "modern",
        target_job_title: Optional[str] = None,
        target_job_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Rewrite CV with AI based on style and target job.
        
        Args:
            cv_text: Original CV text
            style: Style to use (modern, minimal, executive, ats_optimized)
            target_job_title: Optional target job title
            target_job_description: Optional job description for optimization
        
        Returns:
            Dict with rewritten CV and metadata
        """
        client = CVRewriterService._get_llm_client()
        
        if not client:
            return CVRewriterService._rewrite_cv_dummy(cv_text, style)
        
        try:
            style_instructions = CVRewriterService.get_style_instructions(style)
            
            job_context = ""
            if target_job_title:
                job_context = f"\n\nTarget Job: {target_job_title}"
            if target_job_description:
                job_context += f"\n\nJob Description:\n{target_job_description[:500]}"
            
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an expert CV writer and career coach. "
                        "You create compelling, ATS-friendly CVs that get results. "
                        "You use action verbs, quantify achievements, and highlight impact."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Rewrite this CV in {style} style:\n\n"
                        f"{cv_text}\n\n"
                        f"Style Requirements:\n{style_instructions}"
                        f"{job_context}\n\n"
                        "Return JSON with:\n"
                        "- rewritten_cv_text: The complete rewritten CV\n"
                        "- rewritten_cv_markdown: Markdown formatted version\n"
                        "- improvements_made: List of 5-7 key improvements\n"
                        "- keywords_added: List of important keywords added\n"
                        "- ats_score_before: Estimated ATS score before (0-100)\n"
                        "- ats_score_after: Estimated ATS score after (0-100)\n"
                        "\nMake the CV compelling, achievement-focused, and ATS-friendly."
                    )
                }
            ]
            
            response = client.chat.completions.create(
                model=settings.llm_model,
                messages=messages,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"CV rewrite failed: {e}")
            return CVRewriterService._rewrite_cv_dummy(cv_text, style)
    
    @staticmethod
    def _rewrite_cv_dummy(cv_text: str, style: str) -> Dict[str, Any]:
        """Dummy CV rewriter when LLM is not available."""
        lines = cv_text.split('\n')
        
        # Basic formatting improvements
        formatted_lines = []
        for line in lines:
            if line.strip():
                # Add bullet points to lines that look like achievements
                if not line.startswith('•') and not line.startswith('-') and len(line) > 20:
                    formatted_lines.append(f"• {line.strip()}")
                else:
                    formatted_lines.append(line.strip())
        
        rewritten = '\n'.join(formatted_lines)
        
        return {
            "rewritten_cv_text": rewritten,
            "rewritten_cv_markdown": f"# Resume\n\n{rewritten}",
            "improvements_made": [
                "Added consistent bullet points",
                "Improved formatting and structure",
                "Enhanced readability",
                f"Applied {style} style formatting",
                "⚠️ Configure OPENAI_API_KEY for AI-powered rewriting"
            ],
            "keywords_added": ["professional", "experienced", "skilled"],
            "ats_score_before": 65,
            "ats_score_after": 75,
            "note": "This is basic formatting. For AI-powered CV rewriting with style templates, configure OPENAI_API_KEY."
        }


class CoverLetterService:
    """
    Service for generating cover letters with AI.
    """
    
    @staticmethod
    def _get_llm_client():
        """Get OpenAI client if available."""
        if not OPENAI_AVAILABLE or not settings.openai_api_key:
            return None
        return OpenAI(api_key=settings.openai_api_key)
    
    @staticmethod
    def get_tone_instructions(tone: str) -> str:
        """Get tone instructions for cover letter."""
        tones = {
            "formal": (
                "Use formal, traditional business language. "
                "Be respectful and professional. "
                "Use complete sentences and proper titles."
            ),
            "smart": (
                "Use intelligent, insightful language. "
                "Show thoughtfulness and strategic thinking. "
                "Balance professionalism with personality."
            ),
            "professional": (
                "Use standard professional business language. "
                "Be clear, confident, and competent. "
                "Maintain appropriate formality."
            ),
            "friendly": (
                "Use warm, personable language. "
                "Be approachable while remaining professional. "
                "Show enthusiasm and genuine interest."
            )
        }
        return tones.get(tone, tones["professional"])
    
    @staticmethod
    def generate_cover_letter(
        cv_text: str,
        job_title: str,
        company_name: str,
        job_description: Optional[str] = None,
        tone: str = "professional",
        additional_info: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate cover letter with AI.
        
        Args:
            cv_text: CV text
            job_title: Target job title
            company_name: Company name
            job_description: Optional job description
            tone: Tone to use
            additional_info: Additional context
        
        Returns:
            Dict with cover letter and metadata
        """
        client = CoverLetterService._get_llm_client()
        
        if not client:
            return CoverLetterService._generate_cover_letter_dummy(
                job_title, company_name, tone
            )
        
        try:
            tone_instructions = CoverLetterService.get_tone_instructions(tone)
            
            job_context = f"Job Title: {job_title}\nCompany: {company_name}"
            if job_description:
                job_context += f"\n\nJob Description:\n{job_description[:800]}"
            if additional_info:
                job_context += f"\n\nAdditional Context:\n{additional_info}"
            
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an expert cover letter writer. "
                        "You create compelling, personalized cover letters that get interviews. "
                        "You highlight relevant experience and show genuine interest in the role."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Generate a cover letter for this application:\n\n"
                        f"{job_context}\n\n"
                        f"Candidate's CV:\n{cv_text[:1500]}\n\n"
                        f"Tone: {tone} - {tone_instructions}\n\n"
                        "Return JSON with:\n"
                        "- cover_letter_text: Complete cover letter (3-4 paragraphs)\n"
                        "- cover_letter_markdown: Markdown formatted version\n"
                        "- matching_skills: List of skills from CV matching the job\n"
                        "- key_highlights: 3-5 key points highlighted in letter\n"
                        "\nMake it compelling, specific, and show genuine interest in the role."
                    )
                }
            ]
            
            response = client.chat.completions.create(
                model=settings.llm_model,
                messages=messages,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"Cover letter generation failed: {e}")
            return CoverLetterService._generate_cover_letter_dummy(
                job_title, company_name, tone
            )
    
    @staticmethod
    def _generate_cover_letter_dummy(
        job_title: str,
        company_name: str,
        tone: str
    ) -> Dict[str, Any]:
        """Dummy cover letter when LLM is not available."""
        letter = f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company_name}. With my background and experience, I am confident I would be a valuable addition to your team.

Throughout my career, I have developed strong skills and delivered measurable results. I am particularly drawn to this opportunity at {company_name} because of your reputation for excellence and innovation.

I would welcome the opportunity to discuss how my experience and skills would benefit your team. Thank you for considering my application.

Sincerely,
[Your Name]

⚠️ This is a template. For personalized, AI-powered cover letters, configure OPENAI_API_KEY in backend/.env"""
        
        return {
            "cover_letter_text": letter,
            "cover_letter_markdown": f"# Cover Letter\n\n{letter}",
            "matching_skills": ["Communication", "Problem-solving", "Teamwork"],
            "key_highlights": [
                "Strong background in the field",
                "Proven track record of results",
                "Enthusiasm for the company"
            ],
            "note": "Configure OPENAI_API_KEY for personalized AI-generated cover letters."
        }

