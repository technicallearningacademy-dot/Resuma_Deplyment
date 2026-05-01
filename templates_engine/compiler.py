"""
LaTeX to PDF compiler.
"""
import os
import subprocess
import tempfile
import logging
import shutil

logger = logging.getLogger(__name__)


def compile_latex_to_pdf(latex_content, user=None):
    """Compile LaTeX content to PDF bytes.
    
    Tries pdflatex first, falls back to a simple text-based PDF if not available.
    """
    # Try pdflatex first
    result = _compile_with_pdflatex(latex_content, user)
    if result:
        return result
    
    # Fallback: generate a simple PDF using reportlab or return None
    logger.warning('pdflatex not available. Using fallback PDF generation.')
    return _fallback_pdf(latex_content, user=user)


def _compile_with_pdflatex(latex_content, user=None):
    """Compile with pdflatex if available."""
    if not shutil.which('pdflatex'):
        logger.info('pdflatex not found in PATH')
        return None

    tmpdir = tempfile.mkdtemp()
    try:
        tex_path = os.path.join(tmpdir, 'resume.tex')
        pdf_path = os.path.join(tmpdir, 'resume.pdf')

        # If user has a profile image, copy it to the build dir as a normalized RGB jpg
        if user and hasattr(user, 'profile_image') and user.profile_image:
            try:
                from PIL import Image
                img_src = user.profile_image.path
                if os.path.exists(img_src):
                    # Convert to RGB JPG to resolve transparency/format issues for DOCX
                    with Image.open(img_src) as img:
                        rgb_img = img.convert('RGB')
                        rgb_img.save(os.path.join(tmpdir, 'profile.jpg'), 'JPEG', quality=95)
            except Exception as e:
                logger.warning(f"Could not normalize profile image for latex: {e}")
                # Fallback: simple copy if Pillow fails
                try:
                    shutil.copy2(user.profile_image.path, os.path.join(tmpdir, 'profile.jpg'))
                except: pass

        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(latex_content)

        # Run pdflatex twice for references
        for _ in range(2):
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-output-directory', tmpdir, tex_path],
                capture_output=True, text=True, timeout=60
            )

        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                return f.read()
        else:
            logger.error(f'pdflatex failed: {result.stderr}')
            return None

    except subprocess.TimeoutExpired:
        logger.error('pdflatex timed out')
        return None
    except Exception as e:
        logger.error(f'LaTeX compilation error: {e}')
        return None
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def _fallback_pdf(latex_content, user=None):
    """Fallback: compile PDF using a public LaTeX API.
    
    This is used when pdflatex is not installed locally (e.g. on Railway).
    Now supports sending the profile image to the remote API.
    """
    # 1. Try robust POST via texlive.net (handles large resumes)
    try:
        import requests
        url = 'https://texlive.net/cgi-bin/latexcgi'
        
        # Prepare files list (using list of tuples to allow multiple 'filecontents[]' keys)
        files = [('filecontents[]', ('document.tex', latex_content))]
        
        # If user has a profile image, send it too
        if user and hasattr(user, 'profile_image') and user.profile_image:
            try:
                from PIL import Image
                import io
                img_src = user.profile_image.path
                if os.path.exists(img_src):
                    with Image.open(img_src) as img:
                        rgb_img = img.convert('RGB')
                        img_byte_arr = io.BytesIO()
                        rgb_img.save(img_byte_arr, format='JPEG', quality=95)
                        img_bytes = img_byte_arr.getvalue()
                        files.append(('filecontents[]', ('profile.jpg', img_bytes)))
            except Exception as e:
                logger.warning(f"Could not prepare profile image for remote latex: {e}")

        data = {'filename[]': 'document.tex', 'engine': 'pdflatex', 'return': 'pdf'}
        
        response = requests.post(url, files=files, data=data, timeout=30)
        if response.status_code == 200:
            content = response.content
            if content.startswith(b'%PDF'):
                return content
            else:
                logger.error(f'texlive.net compilation failed: {content[:200]}...')
        else:
            logger.error(f'texlive.net returned status {response.status_code}')
            
    except ImportError:
        logger.warning("requests library not found. Falling back to HTTP GET limits.")
        # 2. Fallback to GET via latexonline.cc (has 8KB URL limits)
        try:
            import urllib.request
            import urllib.parse
            encoded_latex = urllib.parse.quote(latex_content)
            url = f'https://latexonline.cc/compile?text={encoded_latex}'
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req, timeout=30)
            if response.status == 200:
                return response.read()
        except Exception as e:
            logger.error(f'latexonline.cc GET failed: {e}')
            
    except Exception as e:
        logger.error(f'POST API PDF generation failed: {e}')
        
    # 3. Final emergency fallback: raw text PDF
    try:
        from fpdf import FPDF
        import re
        
        # If compilation failed entirely, do not strip the LaTeX. Provide the raw LaTeX cleanly in the PDF so they can copy it, 
        # or at minimum format it nicely without destroying the braces.
        text = latex_content
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Courier', size=9) # Use monospace for code
        text = text.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 5, text)
        return pdf.output(dest='S').encode('latin-1')
    except:
        return None
