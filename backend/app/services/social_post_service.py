"""
Service for generating social media posts for job listings.
Uses OpenAI to create engaging social media content.
"""
from typing import Dict, Any
from app.services.llm_service import LLMService
from app.config import settings


class SocialPostService:
    """Service for generating social media posts."""
    
    @staticmethod
    def generate_social_post(
        job_title: str,
        company_name: str,
        location: str = None,
        employment_type: str = None,
        description: str = "",
        min_salary: float = None,
        max_salary: float = None,
        currency: str = "USD",
        job_url: str = None
    ) -> Dict[str, Any]:
        """
        Generate a social media post for a job listing.
        
        Returns:
            Dict with 'text' (the post content) and 'link' (application URL)
        """
        # Build job details summary
        job_details = []
        job_details.append(f"Position: {job_title}")
        if company_name:
            job_details.append(f"Company: {company_name}")
        if location:
            job_details.append(f"Location: {location}")
        if employment_type:
            job_details.append(f"Type: {employment_type.replace('_', ' ')}")
        if min_salary or max_salary:
            salary_str = ""
            if min_salary and max_salary:
                salary_str = f"{min_salary:,.0f} - {max_salary:,.0f} {currency}"
            elif min_salary:
                salary_str = f"{min_salary:,.0f}+ {currency}"
            elif max_salary:
                salary_str = f"Up to {max_salary:,.0f} {currency}"
            if salary_str:
                job_details.append(f"Salary: {salary_str}")
        
        job_summary = "\n".join(job_details)
        
        # Generate the post using LLM
        prompt = f"""You are a professional social media content creator specializing in job postings.

Create an engaging, professional social media post for this job opportunity:

{job_summary}

Job Description:
{description[:500]}{'...' if len(description) > 500 else ''}

Requirements:
- The post should be engaging and professional
- Include relevant hashtags (3-5 hashtags)
- Make it compelling to attract qualified candidates
- Keep it concise (150-250 words for LinkedIn, shorter for Twitter)
- Include a call-to-action
- Use an enthusiastic but professional tone
- Highlight key benefits or unique aspects of the role

Format the post as plain text (no markdown). Include hashtags at the end.

Return ONLY the post text, nothing else."""

        messages = [
            {
                "role": "system",
                "content": "You are an expert social media content creator. Create engaging, professional job postings for LinkedIn, Twitter, and other platforms."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        post_text = LLMService._call_llm(messages, response_format="text")
        
        # Fallback if LLM fails
        if not post_text:
            post_text = SocialPostService._generate_fallback_post(
                job_title, company_name, location, employment_type
            )
        
        # Add signature link
        if job_url:
            link = job_url
        else:
            # Default to Interviewly job portal (you can customize this)
            link = f"https://interviewly.com/jobs/{job_title.lower().replace(' ', '-')}"
        
        # Ensure post ends with the link and signature
        if link not in post_text:
            post_text += f"\n\n🔗 Apply now: {link}"
        
        # Add Interviewly signature
        post_text += "\n\n---\nPosted via Interviewly - AI-Powered Hiring Platform"
        
        return {
            "text": post_text.strip(),
            "link": link
        }
    
    @staticmethod
    def _generate_fallback_post(
        job_title: str,
        company_name: str,
        location: str = None,
        employment_type: str = None
    ) -> str:
        """Fallback post generation if LLM is unavailable."""
        post = f"🚀 We're hiring! {job_title}"
        
        if company_name:
            post += f" at {company_name}"
        
        if location:
            post += f" ({location})"
        
        if employment_type:
            post += f" - {employment_type.replace('_', ' ')}"
        
        post += "\n\nJoin our team and make an impact! Apply now to learn more about this exciting opportunity."
        post += "\n\n#Hiring #Jobs #CareerOpportunity"
        
        if job_title:
            # Add job title as hashtag
            job_tag = job_title.replace(' ', '').replace('-', '')
            post += f" #{job_tag}"
        
        return post

