"""
Prompt templates for Gemini AI interactions.
Uses pre-tested template skeletons from template_library.py to guide the AI.
"""
import json
from ai_services.template_library import get_template_skeleton


def get_latex_from_text_prompt(raw_text, template_style='modern_ats_clean', custom_prompt=''):
    """Build prompt for generating LaTeX resume from raw CV text."""

    skeleton = get_template_skeleton(template_style)

    prompt = f"""You are an expert resume writer and LaTeX typesetter.
Your task is to fill in the following LaTeX resume template with the candidate's actual data below.

TEMPLATE (do NOT change packages, colors, or structure):
{skeleton}

CANDIDATE INFORMATION:
{raw_text}

RULES:
1. Output ONLY the final, complete, filled-in LaTeX code — no markdown, no explanations, no ```
2. Replace {{{{NAME}}}}, {{{{JOB_TITLE}}}}, {{{{EMAIL}}}}, {{{{PHONE}}}}, {{{{LINKEDIN}}}}, {{{{GITHUB}}}} with actual values
3. Replace {{{{SUMMARY}}}}, {{{{EXPERIENCE}}}}, {{{{EDUCATION}}}}, {{{{SKILLS}}}}, {{{{PROJECTS}}}} with formatted LaTeX content
4. CRITICAL: Keep the exact same packages, colors, and titleformat from the template above
5. CRITICAL: Escape all special LaTeX characters (e.g. \\&, \\%, \\$, \\#, \\_, ~)
6. CRITICAL: Ensure every {{ has a matching }}. Keep environments properly nested.
7. Use \\textbf{{Company}} \\hfill Date \\\\ \\textit{{Title}} format for jobs
8. Use bullet points (\\begin{{itemize}} ... \\end{{itemize}}) for all achievements
9. If data is not provided, omit that section entirely — do NOT leave placeholder text

{f'ADDITIONAL INSTRUCTIONS: {custom_prompt}' if custom_prompt else ''}

Output the COMPLETE LaTeX document starting with \\documentclass:"""

    return prompt


def get_latex_generation_prompt(profile_data, template_style='modern_ats_clean', custom_prompt=''):
    """Build prompt for generating ATS-optimized LaTeX resume from profile data."""

    skeleton = get_template_skeleton(template_style)

    prompt = f"""You are an expert resume writer and LaTeX typesetter.
Your task is to fill in the following LaTeX resume template with the candidate's profile data below.

TEMPLATE (do NOT change packages, colors, or structure):
{skeleton}

PROFILE DATA:
{json.dumps(profile_data, indent=2, default=str)}

RULES:
1. Output ONLY the final, complete, filled-in LaTeX code — no markdown, no explanations, no ```
2. Replace {{{{NAME}}}}, {{{{JOB_TITLE}}}}, {{{{EMAIL}}}}, {{{{PHONE}}}}, {{{{LINKEDIN}}}}, {{{{GITHUB}}}} with actual values from profile
3. Replace {{{{SUMMARY}}}}, {{{{EXPERIENCE}}}}, {{{{EDUCATION}}}}, {{{{SKILLS}}}}, {{{{PROJECTS}}}} with LaTeX-formatted content using all provided data
4. CRITICAL: Keep the exact same packages, colors, and titleformat from the template above
5. CRITICAL: Escape all special LaTeX characters (e.g. \\&, \\%, \\$, \\#, \\_, ~)
6. CRITICAL: Ensure every {{ has a matching }}. Keep environments properly nested.
7. Use \\textbf{{Company}} \\hfill Date \\\\ \\textit{{Title}} format for jobs
8. Use bullet points (\\begin{{itemize}} ... \\end{{itemize}}) for all achievements and descriptions
9. Format skills in groups: \\textbf{{Category:}} Skill1, Skill2, Skill3
10. If a section has no data, omit it entirely — do NOT leave placeholder text

{f'ADDITIONAL INSTRUCTIONS: {custom_prompt}' if custom_prompt else ''}

Output the COMPLETE LaTeX document starting with \\documentclass:"""

    return prompt


def get_enhancement_prompt(text, context='resume'):
    """Build prompt for enhancing resume text."""
    return f"""You are a professional resume writer. Enhance the following {context} text to be more:
- Professional and impactful
- Action-oriented (start with strong verbs)
- Quantified with metrics where possible
- ATS-friendly with relevant keywords
- Concise but comprehensive

Original text:
{text}

Return ONLY the enhanced text, no explanations:"""


def get_extraction_prompt(cv_text):
    """Build prompt for extracting structured data from CV text."""
    return f"""Extract structured data from this CV/resume text and return as JSON.

CV TEXT:
{cv_text}

Return a JSON object with these fields:
{{
    "first_name": "",
    "last_name": "",
    "email": "",
    "phone": "",
    "city": "",
    "country": "",
    "linkedin": "",
    "github": "",
    "portfolio": "",
    "summary": "",
    "job_title": "",
    "education": [
        {{"institution": "", "degree": "", "field_of_study": "", "start_date": "", "end_date": "", "gpa": "", "description": ""}}
    ],
    "experience": [
        {{"company": "", "title": "", "start_date": "", "end_date": "", "is_current": false, "location": "", "description": "", "achievements": ""}}
    ],
    "skills": [
        {{"name": "", "category": "technical|soft|language|tool", "proficiency": "beginner|intermediate|advanced|expert"}}
    ],
    "certifications": [
        {{"name": "", "issuer": "", "date_obtained": ""}}
    ],
    "projects": [
        {{"name": "", "description": "", "technologies": "", "url": ""}}
    ]
}}

Return ONLY the JSON, no explanations:"""


def get_keyword_optimization_prompt(resume_text, job_description=''):
    """Build prompt for ATS keyword optimization."""
    jd_part = f"\\n\\nJOB DESCRIPTION:\\n{job_description}" if job_description else ""

    return f"""You are an ATS optimization expert. Analyze this resume and suggest keyword improvements.{jd_part}

RESUME TEXT:
{resume_text}

Provide:
1. Missing high-impact keywords for the target role
2. Suggestions to replace weak phrases with stronger ATS-friendly alternatives
3. Section-by-section optimization tips

Format as clear, actionable bullet points:"""
