"""
Google Gemini API client with Hugging Face fallback for resume generation.
Automatically falls back to HF when Gemini hits rate limits.
"""
import logging
import google.generativeai as genai
from huggingface_hub import InferenceClient
from django.conf import settings

logger = logging.getLogger(__name__)

# Best free HF models for LaTeX/code generation
HF_MODEL = "Qwen/Qwen2.5-Coder-32B-Instruct"
HF_FALLBACK_MODEL = "meta-llama/Llama-3.2-3B-Instruct"


class GeminiClient:
    """AI client with Gemini primary + Hugging Face fallback."""

    def __init__(self):
        # Configure Gemini
        api_key = settings.GEMINI_API_KEY
        if api_key:
            genai.configure(api_key=api_key)
        self.gemini_model = genai.GenerativeModel('models/gemini-2.0-flash-lite')

        # Configure Hugging Face (works without token for free models)
        hf_token = getattr(settings, 'HF_API_TOKEN', None) or None
        self.hf_client = InferenceClient(token=hf_token)

    def generate(self, prompt, max_tokens=8192):
        """Try Gemini first, fall back to Hugging Face on failure."""
        # Attempt 1: Gemini
        try:
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7,
                )
            )
            logger.info('Generated via Gemini')
            return response.text
        except Exception as e:
            logger.warning(f'Gemini failed ({e}), falling back to Hugging Face...')

        # Attempt 2: Hugging Face (Qwen2.5-Coder)
        try:
            return self._generate_hf(prompt, HF_MODEL, max_tokens)
        except Exception as e:
            logger.warning(f'HF primary model failed ({e}), trying fallback...')

        # Attempt 3: Hugging Face fallback (Mixtral)
        try:
            return self._generate_hf(prompt, HF_FALLBACK_MODEL, max_tokens)
        except Exception as e:
            logger.error(f'All AI providers failed: {e}')
            raise Exception('All AI providers failed. Please try again in a minute.')

    def _generate_hf(self, prompt, model, max_tokens=6000):
        """Generate text using Hugging Face Inference API."""
        messages = [{"role": "user", "content": prompt}]
        response = self.hf_client.chat_completion(
            messages=messages,
            model=model,
            max_tokens=min(max_tokens, 8000),
            temperature=0.7,
        )
        logger.info(f'Generated via HuggingFace ({model})')
        content = response.choices[0].message.content
        
        # Emergency cutoff prevention: if HF hits max tokens and cuts off before closing, force close it
        if r'\begin{document}' in content and r'\end{document}' not in content:
            # Try to close any open itemize lists heuristically
            open_items = content.count(r'\begin{itemize}') - content.count(r'\end{itemize}')
            for _ in range(max(0, open_items)):
                content += '\n\\end{itemize}'
            content += '\n\\end{document}'
            
        return content

    def generate_latex_resume(self, profile_data, template_style='modern_ats_clean', custom_prompt=''):
        """Generate ATS-optimized LaTeX resume from structured profile data."""
        from .prompts import get_latex_generation_prompt
        prompt = get_latex_generation_prompt(profile_data, template_style, custom_prompt)
        return self.generate(prompt)

    def generate_from_text(self, raw_text, template_style='modern_ats_clean', custom_prompt=''):
        """Generate LaTeX resume directly from raw text (when no profile exists)."""
        from .prompts import get_latex_from_text_prompt
        prompt = get_latex_from_text_prompt(raw_text, template_style, custom_prompt)
        return self.generate(prompt)

    def enhance_text(self, text, context='resume'):
        """Improve resume language for professionalism and ATS optimization."""
        from .prompts import get_enhancement_prompt
        prompt = get_enhancement_prompt(text, context)
        return self.generate(prompt)

    def extract_cv_data(self, cv_text):
        """Extract structured data from CV text."""
        from .prompts import get_extraction_prompt
        prompt = get_extraction_prompt(cv_text)
        return self.generate(prompt)

    def optimize_keywords(self, resume_text, job_description=''):
        """Optimize resume keywords for ATS ranking."""
        from .prompts import get_keyword_optimization_prompt
        prompt = get_keyword_optimization_prompt(resume_text, job_description)
        return self.generate(prompt)


# Singleton instance
_client = None

def get_client():
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client
