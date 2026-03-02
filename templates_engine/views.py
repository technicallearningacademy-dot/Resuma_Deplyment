"""
Template engine views for PDF preview.
"""
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .compiler import compile_latex_to_pdf
import json


@login_required
@require_POST
def preview_pdf(request):
    """Generate a PDF preview from LaTeX content."""
    try:
        body = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        latex_content = body.get('latex_content', '')

        if not latex_content:
            return JsonResponse({'error': 'No LaTeX content provided.'}, status=400)

        pdf_bytes = compile_latex_to_pdf(latex_content)

        if pdf_bytes:
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="preview.pdf"'
            return response
        else:
            return JsonResponse({'error': 'PDF compilation failed.'}, status=500)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
