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
        from .prompts import get_chat_system_prompt
        # Configure Gemini with a system-level guardrail to restrict to resume topics
        api_key = settings.GEMINI_API_KEY
        if api_key:
            genai.configure(api_key=api_key)
        self.gemini_model = genai.GenerativeModel(
            'models/gemini-1.5-flash',
            system_instruction=get_chat_system_prompt()  # Global restriction applied to ALL calls
        )

        # Configure Hugging Face (works without token for free models) with 85s timeout
        hf_token = getattr(settings, 'HF_API_TOKEN', None) or None
        self.hf_client = InferenceClient(token=hf_token, timeout=85)


    def generate(self, prompt, max_tokens=6000, fast_mode=False):
        """Generate text using Gemini 2.0 Flash with automatic fallback to Hugging Face."""
        temperature = 0.1 if fast_mode else 0.4
        out_tokens = min(max_tokens, 4000) if fast_mode else max_tokens

        # Attempt 1: Gemini
        try:
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=out_tokens,
                    temperature=temperature,
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

    def generate_latex_resume(self, profile_data, template_style='modern_ats_clean', custom_prompt='', fast_mode=False):
        """Generate ATS-optimized LaTeX resume from structured profile data."""
        from .prompts import get_latex_generation_prompt
        prompt = get_latex_generation_prompt(profile_data, template_style, custom_prompt)
        return self.generate(prompt, fast_mode=fast_mode)

    def generate_from_text(self, raw_text, template_style='modern_ats_clean', custom_prompt='', fast_mode=False):
        """Generate LaTeX resume directly from raw text (when no profile exists)."""
        from .prompts import get_latex_from_text_prompt
        prompt = get_latex_from_text_prompt(raw_text, template_style, custom_prompt)
        return self.generate(prompt, fast_mode=fast_mode)

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

    def chat_with_assistant(self, user_message, chat_history_qs=None):
        """
        Handle a pure conversational chat (no LaTeX generation).
        Returns a plain-text conversational response about resume topics.
        The system guardrail restricts topics to resume/career only.

        chat_history_qs: optional QuerySet of ResumeChatMessage for multi-turn context.
        """
        from .prompts import get_chat_system_prompt

        # Build Gemini multi-turn history
        gemini_history = []
        hf_messages = [{"role": "system", "content": get_chat_system_prompt()}]

        if chat_history_qs:
            for msg in chat_history_qs:
                role_g = "user" if msg.role == "user" else "model"
                role_h = "user" if msg.role == "user" else "assistant"
                gemini_history.append({"role": role_g, "parts": [msg.content]})
                hf_messages.append({"role": role_h, "content": msg.content})

        # Attempt 1: Gemini Chat
        try:
            chat = self.gemini_model.start_chat(history=gemini_history)
            response = chat.send_message(
                user_message,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=1024,
                    temperature=0.8,
                )
            )
            logger.info('Chat response via Gemini')
            return response.text
        except Exception as e:
            logger.warning(f'Gemini chat failed ({e}), falling back to HF...')

        # Attempt 2: Hugging Face
        hf_messages.append({"role": "user", "content": user_message})
        try:
            return self._generate_hf_chat(hf_messages, HF_MODEL, max_tokens=1024)
        except Exception as e:
            logger.warning(f'HF chat failed ({e}), trying fallback...')

        try:
            return self._generate_hf_chat(hf_messages, HF_FALLBACK_MODEL, max_tokens=1024)
        except Exception as e:
            logger.error(f'All AI providers failed for chat: {e}')
            raise Exception('AI service unavailable. Please try again in a moment.')

    def extract_from_pdf(self, pdf_text):
        """
        Extract structured resume data from raw text extracted from a PDF.
        Returns a JSON string with all resume fields.
        """
        from .prompts import get_pdf_extraction_prompt
        prompt = get_pdf_extraction_prompt(pdf_text)
        return self.generate(prompt, max_tokens=4096)

    def chat_resume_edit(self, user_prompt, profile_data, current_latex, template_style, chat_history_qs=None, fast_mode=False):
        """
        Handle a conversational resume edit request.
        Allows the AI to modify the user's current resume based on chat history.
        """
        from .prompts import get_chat_edit_system_prompt
        
        system_instruction, hf_system = get_chat_edit_system_prompt(profile_data, template_style)
        
        gemini_history = []
        hf_history = [{"role": "system", "content": hf_system}]
        
        if chat_history_qs:
            # The chat history querysets includes the message the user *just* sent, 
            # because views.py saves it to the DB before calling this function.
            # We need to build the history of all *past* turns, excluding this very last user prompt,
            # because we will attach this final prompt directly to the LaTeX payload below.
            history_list = list(chat_history_qs)
            
            # If the last message in DB matches the current prompt, exclude it from the history loop
            if history_list and history_list[-1].role == 'user' and history_list[-1].content == user_prompt:
                history_list = history_list[:-1]
                
            for msg in history_list:
                role_gemini = "user" if msg.role == "user" else "model"
                role_hf = "user" if msg.role == "user" else "assistant"
                
                gemini_history.append({"role": role_gemini, "parts": [msg.content]})
                hf_history.append({"role": role_hf, "content": msg.content})
                
        # Now, create ONE final turn that combines the LaTeX state with the user's specific request
        # The order matters: LaTeX first (reference), then the request (instruction)
        context_msg = (
            f"=== CURRENT RESUME LATEX (DO NOT REWRITE — ONLY MODIFY THE SPECIFIC PART REQUESTED) ===\n"
            f"{current_latex}\n\n"
            f"=== USER'S SPECIFIC REQUEST (ONLY change this, keep EVERYTHING else identical) ===\n"
            f"{user_prompt}\n\n"
            f"REMINDER: Output the COMPLETE LaTeX document with ONLY the above change applied. "
            f"Do NOT reorder sections, do NOT remove any existing content, do NOT change formatting."
        )
        
        # We don't append this to gemini_history because we send it directly via send_message
        hf_history.append({"role": "user", "content": context_msg})

        temperature = 0.1 if fast_mode else 0.7
        max_tokens_val = 4000 if fast_mode else 8192

        # Attempt 1: Gemini (Using start_chat to maintain exact structure expectations)
        try:
            chat = self.gemini_model.start_chat(history=gemini_history)
            response = chat.send_message(
                context_msg,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens_val,
                    temperature=temperature,
                    system_instruction=system_instruction
                )
            )
            logger.info('Generated edit via Gemini Chat')
            return response.text
        except Exception as e:
            logger.warning(f'Gemini Chat failed ({e}), falling back to Hugging Face...')
            
        # Attempt 2: Hugging Face (Qwen2.5-Coder)
        try:
            return self._generate_hf_chat(hf_history, HF_MODEL)
        except Exception as e:
            logger.warning(f'HF primary model failed ({e}), trying fallback...')

        # Attempt 3: Hugging Face fallback
        try:
            return self._generate_hf_chat(hf_history, HF_FALLBACK_MODEL)
        except Exception as e:
            logger.error(f'All AI providers failed: {e}')
            raise Exception('All AI providers failed. Please try again in a minute.')

    def _generate_hf_chat(self, messages, model, max_tokens=6000):
        """Generate text using Hugging Face Inference API with conversation history."""
        response = self.hf_client.chat_completion(
            messages=messages,
            model=model,
            max_tokens=min(max_tokens, 8000),
            temperature=0.7,
        )
        logger.info(f'Generated edit via HuggingFace Chat ({model})')
        content = response.choices[0].message.content
        
        if r'\begin{document}' in content and r'\end{document}' not in content:
            open_items = content.count(r'\begin{itemize}') - content.count(r'\end{itemize}')
            for _ in range(max(0, open_items)):
                content += '\n\\end{itemize}'
            content += '\n\\end{document}'
            
        return content


# Singleton instance
_client = None

def get_client():
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client
