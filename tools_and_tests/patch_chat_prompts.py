import re

with open('ai_services/prompts.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_func = '''def get_chat_edit_system_prompt(profile_data, template_style='modern_ats_clean'):
    """Build system instructions for conversational resume editing."""
    from ai_services.template_library import get_template_skeleton
    import json
    skeleton = get_template_skeleton(template_style)
    
    system_instruction = f"""{SYSTEM_GUARDRAIL}

You are an expert resume writer and LaTeX typesetter working in SURGICAL EDIT MODE.

The user provides the COMPLETE current LaTeX resume and a SPECIFIC request to change ONE thing.
Your ONLY job is to make EXACTLY that one change — nothing more, nothing less.

CRITICAL RULES — NEVER BREAK THESE:
1. PRESERVE EVERYTHING: Every section, every bullet, every entry that the user did NOT ask to change MUST remain 100% identical.
2. SURGICAL: Only touch the part the user asked about. If they say "add skills", only update the skills section. Do NOT touch name, contact, experience, education, projects, or summary.
3. OUTPUT: Output the COMPLETE LaTeX document (all sections) with ONLY that one targeted change applied.
4. NEVER rewrite from scratch. NEVER reorder sections. Start from the provided current LaTeX and make the minimum change.
5. Escape all special LaTeX characters (\\\\&, \\\\%, \\\\$, \\\\#, \\\\_, ~).
6. Ensure every \\\\begin{{...}} has a matching \\\\end{{...}}.

TEMPLATE STRUCTURE (reference only — preserve existing structure):
{skeleton}

PROFILE DATA (use if user requests info not in the current LaTeX):
{json.dumps(profile_data, indent=2, default=str) if profile_data else 'Not provided.'}

Output ONLY the final complete LaTeX code starting with \\\\documentclass. No explanations, no markdown."""
    return system_instruction, system_instruction'''

new_func = '''def get_chat_edit_system_prompt(profile_data, template_style='modern_ats_clean'):
    """Build system instructions for conversational resume editing."""
    from ai_services.template_library import get_template_skeleton
    import json
    skeleton = get_template_skeleton(template_style)
    
    extra_rules = ""
    if template_style == 'technical_developer':
        extra_rules = """
7. CRITICAL (JOBS): You MUST use the \\jobtitle and \\jobsubtitle macros. Example:
   \\jobtitle{Company Name}{Start Year -- End Year}
   \\jobsubtitle{Your Job Title}
   \\begin{itemize} ... \\end{itemize}
8. CRITICAL (SKILLS): Group them in categories and use \\skilltag for EACH skill individually. Example:
   \\textbf{\\color{accentgold}\\small Languages}\\quad
   \\skilltag{Python} \\skilltag{Java} \\\\[5pt]
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
5. Escape all special LaTeX characters (\\\\&, \\\\%, \\\\$, \\\\#, \\\\_, ~).
6. Ensure every \\\\begin{{...}} has a matching \\\\end{{...}}.{extra_rules}

TEMPLATE STRUCTURE (reference only — preserve existing structure):
{skeleton}

PROFILE DATA (use if user requests info not in the current LaTeX):
{json.dumps(profile_data, indent=2, default=str) if profile_data else 'Not provided.'}

Output ONLY the final complete LaTeX code starting with \\\\documentclass. No explanations, no markdown."""
    return system_instruction, system_instruction'''

content = content.replace(old_func, new_func)

with open('ai_services/prompts.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated successfully!")
