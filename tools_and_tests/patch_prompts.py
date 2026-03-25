import re

with open('ai_services/prompts.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace get_latex_generation_prompt definition
old_func = '''def get_latex_generation_prompt(profile_data, template_style='modern_ats_clean', custom_prompt=''):
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

    return prompt'''

new_func = '''def get_latex_generation_prompt(profile_data, template_style='modern_ats_clean', custom_prompt=''):
    """Build prompt for generating ATS-optimized LaTeX resume from profile data."""

    skeleton = get_template_skeleton(template_style)

    if template_style == 'technical_developer':
        style_instructions = """
7. CRITICAL: For jobs, use the \jobtitle and \jobsubtitle macros. Example:
   \jobtitle{Company Name}{Start Year -- End Year}
   \jobsubtitle{Your Job Title}
   \\begin{itemize} ... \end{itemize}
8. CRITICAL: For skills, group them in categories and use \skilltag for EACH skill individually. Example:
   \\textbf{\color{accentgold}\small Languages}\quad
   \skilltag{Python} \skilltag{Java} \\\\[5pt]
"""
    else:
        style_instructions = """
7. Use \\textbf{Company} \hfill Date \\\\ \\textit{Title} format for jobs
8. Format skills in groups: \\textbf{Category:} Skill1, Skill2, Skill3
"""

    prompt = f"""{SYSTEM_GUARDRAIL}

You are an expert resume writer and LaTeX typesetter.
Your task is to fill in the following LaTeX resume template with the candidate's profile data below.

TEMPLATE (do NOT change packages, colors, or structure):
{skeleton}

PROFILE DATA:
{json.dumps(profile_data, indent=2, default=str)}

RULES:
1. Output ONLY the final, complete, filled-in LaTeX code — no markdown, no explanations, no ```
2. Replace {{{{NAME}}}}, {{{{JOB_TITLE}}}}, {{{{EMAIL}}}}, {{{{PHONE}}}}, {{{{LINKEDIN}}}}, {{{{GITHUB}}}}, {{{{CITY}}}}, {{{{COUNTRY}}}} with actual values from profile
3. Replace {{{{SUMMARY}}}}, {{{{EXPERIENCE}}}}, {{{{EDUCATION}}}}, {{{{SKILLS}}}}, {{{{PROJECTS}}}} with LaTeX-formatted content using all provided data
4. CRITICAL: Keep exactly the same packages, colors, and titleformat from the template above
5. CRITICAL: Escape all special LaTeX characters (e.g. \\&, \\%, \\$, \\#, \\_, ~)
6. CRITICAL: Ensure every {{ has a matching }}. Keep environments properly nested.{style_instructions}9. Use bullet points (\\begin{{itemize}} ... \\end{{itemize}}) for all achievements/descriptions unless specified otherwise
10. If a section has no data, omit it entirely — do NOT leave placeholder text

{f'ADDITIONAL INSTRUCTIONS: {custom_prompt}' if custom_prompt else ''}

Output the COMPLETE LaTeX document starting with \\documentclass:"""

    return prompt'''

content = content.replace(old_func, new_func)

with open('ai_services/prompts.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated successfully!")
