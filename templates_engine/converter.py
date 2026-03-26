"""
LaTeX to DOCX converter using PDF intermediate for pixel-perfect layout preservation.
"""
import io
import os
import tempfile
import logging
from .compiler import compile_latex_to_pdf

logger = logging.getLogger(__name__)

def latex_to_docx(latex_content, title='Resume', user=None):
    """
    Convert LaTeX content to a perfectly formatted DOCX.
    Works by first compiling to PDF to get the exact layout, then 
    using pdf2docx to convert that PDF into a Word document.
    """
    try:
        # Step 0: Optimize LaTeX for Word conversion (Simplify TikZ clippings)
        # pdf2docx often fails to extract images wrapped in complex TikZ macros.
        import re
        # Pattern to find TikZ blocks containing the profile image and simplify them.
        # This more robust regex matches any tikzpicture containing a profile image includegraphics.
        # It replaces the entire tikzpicture with just the inner includegraphics.
        robust_tikz = r'\\begin\{tikzpicture\}.*?(\\includegraphics\[[^\]]*\]\{profile[^}]+\}).*?\\end\{tikzpicture\}'
        
        def simplify_image(match):
            inner_includegraphics = match.group(1)
            # Ensure we keep the width reasonable for Word
            if 'width=' not in inner_includegraphics:
                inner_includegraphics = inner_includegraphics.replace('\\includegraphics', '\\includegraphics[width=2.5cm]')
            return inner_includegraphics
            
        latex_content = re.sub(robust_tikz, simplify_image, latex_content, flags=re.DOTALL)

        # Step 1: Compile the exact beautiful layout to a PDF buffer
        pdf_bytes = compile_latex_to_pdf(latex_content, user=user)
        if not pdf_bytes:
            logger.error('Failed to compile LaTeX to PDF during DOCX conversion.')
            return None

        # Step 2: Use pdf2docx to convert that exact layout to DOCX
        from pdf2docx import Converter
        
        # We need physical temporary files because Converter uses PyMuPDF under the hood
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
            temp_pdf.write(pdf_bytes)
            temp_pdf_path = temp_pdf.name
            
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_docx:
            temp_docx_path = temp_docx.name

        try:
            # Convert PDF to DOCX retaining layout
            cv = Converter(temp_pdf_path)
            cv.convert(temp_docx_path, start=0, end=None)
            cv.close()

            # Read the generated DOCX bytes
            with open(temp_docx_path, 'rb') as f:
                docx_bytes = f.read()
                
            return docx_bytes

        finally:
            # Clean up both temp files
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)
            if os.path.exists(temp_docx_path):
                os.remove(temp_docx_path)

    except Exception as e:
        logger.error(f'DOCX conversion failed: {e}')
        return None
