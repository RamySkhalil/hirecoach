"""
CV Analysis Service - Handles resume parsing, scoring, and analysis.
"""
import os
from typing import Dict, Any, Optional
from pathlib import Path

# Try to import PDF/DOCX parsing libraries
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: PyPDF2 not installed. PDF parsing will not work.")

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("Warning: python-docx not installed. DOCX parsing will not work.")

from app.config import settings

# Try to import OpenAI for CV analysis
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class CVService:
    """
    Service for analyzing CVs/Resumes.
    Provides text extraction, parsing, scoring, and AI-powered analysis.
    """
    
    @staticmethod
    def _get_llm_client():
        """Get OpenAI client if available."""
        if not OPENAI_AVAILABLE or not settings.openai_api_key:
            return None
        return OpenAI(api_key=settings.openai_api_key)
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF file."""
        if not PDF_AVAILABLE:
            raise Exception("PDF parsing not available. Install PyPDF2.")
        
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
        
        return text.strip()
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX file."""
        if not DOCX_AVAILABLE:
            raise Exception("DOCX parsing not available. Install python-docx.")
        
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            raise Exception(f"Failed to extract text from DOCX: {str(e)}")
    
    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            raise Exception(f"Failed to extract text from TXT: {str(e)}")
    
    @staticmethod
    def extract_text(file_path: str, file_type: str) -> str:
        """
        Extract text from uploaded file based on type.
        
        Args:
            file_path: Path to the uploaded file
            file_type: File extension (pdf, docx, txt)
        
        Returns:
            Extracted text content
        """
        file_type = file_type.lower().replace('.', '')
        
        if file_type == 'pdf':
            return CVService.extract_text_from_pdf(file_path)
        elif file_type == 'docx':
            return CVService.extract_text_from_docx(file_path)
        elif file_type == 'txt':
            return CVService.extract_text_from_txt(file_path)
        else:
            raise Exception(f"Unsupported file type: {file_type}. Please use PDF, DOCX, or TXT.")
    
    @staticmethod
    def parse_cv_with_llm(cv_text: str, target_job: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse CV using LLM to extract structured information.
        
        Args:
            cv_text: Extracted text from CV
            target_job: Optional target job title for tailored analysis
        
        Returns:
            Parsed CV data with structured fields
        """
        client = CVService._get_llm_client()
        
        if not client:
            # Return dummy parsed data if LLM not available
            return CVService._parse_cv_dummy(cv_text)
        
        try:
            job_context = f" for a {target_job} position" if target_job else ""
            
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an expert HR assistant and resume parser. "
                        "Extract key information from resumes and structure it as JSON."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Parse this resume{job_context} and extract:\n"
                        "1. Contact info (name, email, phone, location)\n"
                        "2. Summary/objective\n"
                        "3. Work experience (company, role, duration, responsibilities)\n"
                        "4. Education (degree, institution, year)\n"
                        "5. Skills (technical and soft skills)\n"
                        "6. Certifications\n"
                        "7. Key achievements\n\n"
                        f"Resume:\n{cv_text}\n\n"
                        "Return as JSON with these fields: contact, summary, experience, education, skills, certifications, achievements."
                    )
                }
            ]
            
            response = client.chat.completions.create(
                model=settings.llm_model,
                messages=messages,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            import json
            parsed_data = json.loads(response.choices[0].message.content)
            return parsed_data
            
        except Exception as e:
            print(f"LLM parsing failed: {e}")
            return CVService._parse_cv_dummy(cv_text)
    
    @staticmethod
    def _parse_cv_dummy(cv_text: str) -> Dict[str, Any]:
        """Dummy CV parser when LLM is not available."""
        lines = cv_text.split('\n')
        
        return {
            "contact": {
                "name": "Extracted from CV",
                "email": "Not parsed (requires LLM)",
                "phone": "Not parsed",
                "location": "Not parsed"
            },
            "summary": "CV text extraction successful. Configure OPENAI_API_KEY for detailed parsing.",
            "experience": [
                {
                    "company": "Parsed from text",
                    "role": "Various roles found",
                    "duration": "See full text",
                    "responsibilities": []
                }
            ],
            "education": [],
            "skills": ["Text extraction working", "LLM parsing requires API key"],
            "certifications": [],
            "achievements": [],
            "note": "Basic text extraction complete. For detailed parsing, configure OPENAI_API_KEY in backend/.env"
        }
    
    @staticmethod
    def analyze_cv(cv_text: str, parsed_data: Dict, target_job: Optional[str] = None, 
                   target_seniority: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze CV and provide scores, strengths, weaknesses, and suggestions.
        
        Args:
            cv_text: Extracted CV text
            parsed_data: Structured CV data
            target_job: Target job title
            target_seniority: Target seniority level
        
        Returns:
            Analysis results with scores and feedback
        """
        client = CVService._get_llm_client()
        
        if not client:
            return CVService._analyze_cv_dummy(cv_text, target_job, target_seniority)
        
        try:
            target_context = ""
            if target_job:
                target_context += f"\nTarget Role: {target_job}"
            if target_seniority:
                target_context += f"\nTarget Seniority: {target_seniority}"
            
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an expert career coach and ATS specialist. "
                        "Analyze resumes and provide detailed, actionable feedback."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Analyze this resume{target_context and ' for this target:' + target_context}.\n\n"
                        f"Resume content:\n{cv_text}\n\n"
                        "Provide analysis as JSON with:\n"
                        "1. overall_score (0-100): Overall resume quality\n"
                        "2. ats_score (0-100): ATS compatibility score\n"
                        "3. scores_breakdown: {content, formatting, keywords, experience, skills} each 0-100\n"
                        "4. strengths: List of 3-5 strong points\n"
                        "5. weaknesses: List of 3-5 areas for improvement\n"
                        "6. suggestions: List of 5-7 specific actionable improvements\n"
                        "7. keywords_found: Relevant keywords present\n"
                        "8. keywords_missing: Important keywords missing for the role\n"
                        "Be specific, constructive, and actionable in your feedback."
                    )
                }
            ]
            
            response = client.chat.completions.create(
                model=settings.llm_model,
                messages=messages,
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            import json
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            print(f"LLM analysis failed: {e}")
            return CVService._analyze_cv_dummy(cv_text, target_job, target_seniority)
    
    @staticmethod
    def _analyze_cv_dummy(cv_text: str, target_job: Optional[str], 
                          target_seniority: Optional[str]) -> Dict[str, Any]:
        """Dummy CV analysis when LLM is not available."""
        import random
        
        word_count = len(cv_text.split())
        
        # Basic scoring based on length and structure
        base_score = min(85, 50 + (word_count // 20))
        
        return {
            "overall_score": base_score,
            "ats_score": base_score - 5,
            "scores_breakdown": {
                "content": base_score,
                "formatting": base_score - 5,
                "keywords": base_score - 10,
                "experience": base_score,
                "skills": base_score - 5
            },
            "strengths": [
                "CV successfully uploaded and text extracted",
                f"Document contains {word_count} words",
                "File format is compatible with ATS systems"
            ],
            "weaknesses": [
                "Detailed analysis requires OpenAI API configuration",
                "Keyword optimization cannot be assessed without LLM",
                "Content quality assessment needs AI analysis"
            ],
            "suggestions": [
                "Configure OPENAI_API_KEY in backend/.env for detailed AI-powered analysis",
                "Use action verbs to describe your accomplishments",
                "Quantify achievements with specific metrics",
                "Tailor your resume to match the job description",
                "Keep formatting clean and ATS-friendly"
            ],
            "keywords_found": ["extracted", "text", "parsed"],
            "keywords_missing": ["Configure API key for keyword analysis"],
            "note": "This is a basic analysis. For comprehensive AI-powered CV analysis with industry-specific insights, please configure OPENAI_API_KEY."
        }
    
    @staticmethod
    def calculate_scores(analysis: Dict[str, Any]) -> tuple:
        """
        Calculate overall and ATS scores from analysis.
        
        Returns:
            (overall_score, ats_score)
        """
        overall_score = analysis.get("overall_score", 70)
        ats_score = analysis.get("ats_score", 65)
        
        return overall_score, ats_score

