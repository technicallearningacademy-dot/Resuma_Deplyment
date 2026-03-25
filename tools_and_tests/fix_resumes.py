import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from resumes.models import Resume

fixed = 0
for r in Resume.objects.all():
    content = r.latex_content or ""
    has_latex = "\\documentclass" in content or "\\begin{document}" in content
    
    if content and not has_latex:
        print(f"FIXING ID:{r.id} Title:{r.title} - content is NOT LaTeX ({len(content)} chars)")
        print(f"  Was: {content[:80]}...")
        r.latex_content = ""
        r.save()
        fixed += 1
    else:
        print(f"OK ID:{r.id} Title:{r.title} ({len(content)} chars)")

print(f"\nFixed {fixed} corrupted resume(s).")
