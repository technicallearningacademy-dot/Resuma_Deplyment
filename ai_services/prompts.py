"""
Prompt templates for Gemini AI interactions.
Uses pre-tested template skeletons from template_library.py to guide the AI.

All prompts include a SYSTEM_GUARDRAIL that restricts the AI to resume-only tasks.
"""
import json
from ai_services.template_library import get_template_skeleton

# =============================================================================
# SYSTEM GUARDRAIL — injected into every AI prompt
# Prevents the AI from doing anything outside resume building
# =============================================================================
SYSTEM_GUARDRAIL = """
IMPORTANT SYSTEM RESTRICTIONS — YOU MUST FOLLOW THESE AT ALL TIMES:
1. You are ResumeForge AI, a world-class professional resume coach and career assistant.
2. Your primary purpose is to help users create, edit, and optimize their resumes, CVs, and professional profiles.
3. You should be helpful, encouraging, and highly professional. Respond naturally like a human expert (similar to ChatGPT). 
4. Valid requests include changing personal details (phone, email, LinkedIn), adding/removing experience or skills, and rewriting summaries.
5. You must ONLY refuse requests that are completely unrelated to careers (e.g., recipes, movies, unrelated coding).
6. When generating LaTeX, always output ONLY valid LaTeX code — no markdown, no explanations.
"""


def get_latex_from_text_prompt(raw_text, template_style='modern_ats_clean', custom_prompt=''):
    """Build prompt for generating LaTeX resume from raw CV text."""

    skeleton = get_template_skeleton(template_style)

    prompt = f"""{SYSTEM_GUARDRAIL}

You are an expert resume writer and LaTeX typesetter.
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

    prompt = f"""{SYSTEM_GUARDRAIL}

You are an expert resume writer and LaTeX typesetter.
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


def get_chat_edit_system_prompt(profile_data, template_style='modern_ats_clean'):
    """Build system instructions for conversational resume editing."""
    from ai_services.template_library import get_template_skeleton
    import json
    skeleton = get_template_skeleton(template_style)
    
    extra_rules = ""
    if template_style == 'technical_developer':
        extra_rules = """
7. CRITICAL (JOBS): You MUST use the \jobtitle and \jobsubtitle macros. Example:
   \jobtitle{Company Name}{Start Year -- End Year}
   \jobsubtitle{Your Job Title}
   \begin{itemize} ... \end{itemize}
8. CRITICAL (SKILLS): Group them in categories and use \skilltag for EACH skill individually. Example:
   \textbf{\color{accentgold}\small Languages}\quad
   \skilltag{Python} \skilltag{Java} \\[5pt]
"""

    system_instruction = f"""{SYSTEM_GUARDRAIL}

You are an expert resume writer and LaTeX typesetter working in SURGICAL EDIT MODE.

The user provides the COMPLETE current LaTeX resume and a SPECIFIC request to change ONE thing.
Your ONLY job is to make EXACTLY that one change — nothing more, nothing less.

CRITICAL RULES — NEVER BREAK THESE:
1. PRESERVE EVERYTHING: Every section, every bullet, every entry that the user did NOT ask to change MUST remain 100% identical.
2. SURGICAL: Only touch the part the user asked about. If they say "add skills", only update the skills section. Do NOT touch name, contact, experience, education, projects, or summary.
3. OUTPUT: Output the COMPLETE LaTeX document (all sections) with ONLY that one targeted change applied.
4. NEVER rewrite from scratch. NEVER reorder sections. Start from the provided current LaTeX and make the minimum change.
5. Escape all special LaTeX characters (\\&, \\%, \\$, \\#, \\_, ~).
6. Ensure every \\begin{{...}} has a matching \\end{{...}}.{extra_rules}

TEMPLATE STRUCTURE (reference only — preserve existing structure):
{skeleton}

PROFILE DATA (use if user requests info not in the current LaTeX):
{json.dumps(profile_data, indent=2, default=str) if profile_data else 'Not provided.'}

Output ONLY the final complete LaTeX code starting with \\documentclass. No explanations, no markdown."""
    return system_instruction, system_instruction


def get_chat_system_prompt():
    return f"""{SYSTEM_GUARDRAIL}

You are now in Conversational Mode. Your goal is to guide the user and acknowledge their requests warmly.

CRITICAL RULES:
1. NEVER output LaTeX code in this mode.
2. Be helpful and expert. Use a professional yet friendly human tone (like ChatGPT).
3. Keep responses under 150 words.
4. Output your response as a valid JSON object (no markdown code blocks).

JSON Format:
{{
    "reply": "Your friendly, human-like response acknowledging the user's specific request.",
    "requires_edit": true or false
}}

SET "requires_edit" to TRUE if the user asks for ANY modification to their resume data (e.g., "Change my phone number", "Add this skill", "Make my summary better", "Update my contact info").
SET "requires_edit" to FALSE if they are just asking a question or seeking career advice.
"""


def get_pdf_extraction_prompt(pdf_text):
    """Build prompt for extracting structured resume data from PDF text."""
    return f"""{SYSTEM_GUARDRAIL}

Extract ALL resume data from the text below into a structured JSON object. 
Be thorough but concise.

TEXT:
{pdf_text}

Return ONLY valid JSON:
{{
    "first_name": "", "last_name": "", "email": "", "phone": "",
    "city": "", "country": "", "linkedin": "", "github": "", "portfolio": "",
    "summary": "", "job_title": "",
    "education": [
        {{"institution": "", "degree": "", "field_of_study": "", "start_date": "", "end_date": "", "gpa": "", "description": ""}}
    ],
    "experience": [
        {{"company": "", "position": "", "location": "", "start_date": "", "end_date": "", "description": ""}}
    ],
    "skills": [],
    "projects": [
        {{"name": "", "description": "", "link": ""}}
    ],
    "languages": [],
    "certifications": []
}}
"""



def get_enhancement_prompt(text, context='resume'):
    """Build prompt for enhancing resume text."""
    return f"""{SYSTEM_GUARDRAIL}

You are a professional resume writer. Enhance the following {context} text to be more:
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
    return get_pdf_extraction_prompt(cv_text)


def get_keyword_optimization_prompt(resume_text, job_description=''):
    """Build prompt for ATS keyword optimization."""
    jd_part = f"\n\nJOB DESCRIPTION:\n{job_description}" if job_description else ""

    return f"""{SYSTEM_GUARDRAIL}

You are an ATS optimization expert. Analyze this resume and suggest keyword improvements.{jd_part}

RESUME TEXT:
{resume_text}

Provide:
1. Missing high-impact keywords for the target role
2. Suggestions to replace weak phrases with stronger ATS-friendly alternatives
3. Section-by-section optimization tips

Format as clear, actionable bullet points:"""
