"""
Google Gemini API client with Hugging Face fallback for resume generation.
Automatically falls back to HF when Gemini hits rate limits.
"""
import logging
import requests
import google.generativeai as genai
from huggingface_hub import InferenceClient
from django.conf import settings

logger = logging.getLogger(__name__)

# LongCat API Configuration (Stored in settings for security)
LONGCAT_API_URL = "https://api.longcat.chat/openai/v1/chat/completions"
LONGCAT_MODEL = "LongCat-Flash-Chat"

# Two-tier Hugging Face approach
HF_MODEL = "Qwen/Qwen2.5-Coder-32B-Instruct"
HF_FALLBACK_MODEL = "HuggingFaceH4/zephyr-7b-beta"


class GeminiClient:
    """AI client with Gemini multi-key rotation + Multi-provider fallback."""

    def __init__(self):
        # Configure Gemini with a system-level guardrail
        # Supports multiple keys separated by commas in .env
        raw_keys = getattr(settings, 'GEMINI_API_KEY', '')
        self.gemini_keys = [k.strip() for k in str(raw_keys).split(',') if k.strip()]
        self.current_key_index = 0
        
        # Initialize primary model with the first key
        self._set_active_gemini_key()
        
        # Configure Hugging Face (works without token for free models)
        hf_token = getattr(settings, 'HF_API_TOKEN', None)
        self.hf_client = InferenceClient(token=hf_token, timeout=85)

    def _set_active_gemini_key(self):
        """Configure the generativeai library with the current key in the rotation."""
        from .prompts import get_chat_system_prompt
        if not self.gemini_keys:
            logger.error("No GEMINI_API_KEY found in settings.")
            return

        key = self.gemini_keys[self.current_key_index]
        try:
            genai.configure(api_key=key)
            self.gemini_model = genai.GenerativeModel(
                'models/gemini-2.0-flash',
                system_instruction=get_chat_system_prompt()
            )
            logger.info(f"AI Client: Rotated to Gemini Key #{self.current_key_index + 1}")
        except Exception as e:
            logger.error(f"Failed to configure Gemini with key {self.current_key_index}: {e}")

    def _rotate_gemini_key(self):
        """Switch to the next Gemini key if the current one hit a quota (429)."""
        if len(self.gemini_keys) <= 1:
            return False # No other keys to try
            
        self.current_key_index = (self.current_key_index + 1) % len(self.gemini_keys)
        self._set_active_gemini_key()
        return True

    def generate(self, prompt, max_tokens=6000, fast_mode=False):
        """Generate text using a multi-tiered resilience approach."""
        temperature = 0.1 if fast_mode else 0.4
        out_tokens = min(max_tokens, 4000) if fast_mode else max_tokens

        # Tiered Fallback with Error Tracking
        tier_errors = []

        # Tier 1: Gemini (With Rotation)
        attempts = 0
        max_rotation_attempts = len(self.gemini_keys)
        gemini_failed = False
        
        while attempts < max_rotation_attempts:
            try:
                response = self.gemini_model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=out_tokens,
                        temperature=temperature,
                    )
                )
                tokens = getattr(response, 'usage_metadata', {}).total_token_count if hasattr(response, 'usage_metadata') else 0
                logger.info(f'[MONITOR] Tier 1 Success: Gemini Key #{self.current_key_index+1} ({tokens} tokens)')
                return {"content": response.text, "provider": "Gemini", "tokens": tokens}
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg or "ResourceExhausted" in err_msg or "Quota" in err_msg:
                    logger.warning(f'[MONITOR] Gemini Key #{self.current_key_index+1} hit quota limit. Rotating...')
                    if not self._rotate_gemini_key():
                        tier_errors.append(f"Gemini: All {len(self.gemini_keys)} keys hit quota")
                        gemini_failed = True
                        break # No more keys to try
                    attempts += 1
                else:
                    logger.warning(f'[MONITOR] Tier 1 Gemini critical error: {e}. Moving to backup providers...')
                    tier_errors.append(f"Gemini: {err_msg[:100]}")
                    gemini_failed = True
                    break
        
        if not gemini_failed and attempts >= max_rotation_attempts:
            tier_errors.append(f"Gemini: No keys available")

        # Tier 2: Groq (Industry Standard Performance)
        try:
            groq_key = getattr(settings, 'GROQ_API_KEY', None)
            if groq_key:
                return self._generate_groq(prompt, groq_key, max_tokens)
            else:
                tier_errors.append("Groq: No API Key")
        except Exception as e:
            logger.warning(f'[MONITOR] Tier 2 Groq fallback failed: {e}')
            tier_errors.append(f"Groq: {str(e)[:100]}")

        # Tier 3: LongCat (User Recommended Backup)
        try:
            lc_key = getattr(settings, 'LONGCAT_API_KEY', None)
            if lc_key:
                return self._generate_longcat(prompt, lc_key, max_tokens)
            else:
                tier_errors.append("LongCat: No API Key")
        except Exception as e:
            logger.warning(f'[MONITOR] Tier 3 LongCat failed ({e}), trying Hugging Face...')
            tier_errors.append(f"LongCat: {str(e)[:100]}")

        # Tier 4: Hugging Face (Primary)
        try:
            return self._generate_hf(prompt, HF_MODEL, max_tokens)
        except Exception as e:
            logger.warning(f'[MONITOR] Tier 4 HF-Primary failed ({e}), trying fallback...')
            tier_errors.append(f"HF (Qwen): {str(e)[:100]}")

        # Tier 5: Hugging Face (Fallback)
        try:
            return self._generate_hf(prompt, HF_FALLBACK_MODEL, max_tokens)
        except Exception as e:
            logger.warning(f'[MONITOR] Tier 5 HF-Fallback failed ({e}). Trying Local Ollama...')
            tier_errors.append(f"HF (Zephyr): {str(e)[:100]}")
            
        # Final Tier: Local Ollama
        try:
            return self._generate_local(prompt, max_tokens)
        except Exception as e_local:
            error_summary = " | ".join(tier_errors)
            logger.error(f'[MONITOR] All AI providers failed: {error_summary}')
            model = self._get_local_ollama_model()
            if not model:
                raise Exception(f"All AI providers failed. Reasons: {error_summary}. (No local Ollama found on port 11434)")
            else:
                raise Exception(f"All AI providers failed. Reasons: {error_summary}. Local Ollama Error: {str(e_local)}")

    def _get_local_ollama_model(self):
        """Check if Ollama is running and return the first available model."""
        try:
            resp = requests.get('http://localhost:11434/api/tags', timeout=2)
            if resp.status_code == 200:
                models = resp.json().get('models', [])
                if models:
                    return models[0]['name']
        except Exception:
            pass
        return None

    def _generate_local(self, prompt, max_tokens=6000):
        """Generate text using a local Ollama instance."""
        model = self._get_local_ollama_model()
        if not model:
            raise Exception("All AI providers (Gemini, Groq, LongCat, HuggingFace) failed due to quota limits, and no local Ollama instance was found on port 11434. Please install Ollama or try again later.")
            
        logger.info(f"Routing generation to local Ollama model: {model}")
        try:
            resp = requests.post('http://localhost:11434/api/generate', json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_ctx": 8192,
                    "num_predict": max_tokens,
                    "temperature": 0.7
                }
            }, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            content = data.get('response', '')
            tokens = len(prompt + content) // 4  # Estimate for Ollama
            
            if r'\begin{document}' in content and r'\end{document}' not in content:
                open_items = content.count(r'\begin{itemize}') - content.count(r'\end{itemize}')
                for _ in range(max(0, open_items)):
                    content += '\n\\end{itemize}'
                content += '\n\\end{document}'
                
            logger.info(f'[MONITOR] Tier 5 Success: Local Ollama ({tokens} est. tokens)')
            return {"content": content, "provider": "Ollama (Local)", "tokens": tokens}
        except Exception as e:
            logger.error(f"Local Ollama generation failed: {e}")
            raise Exception(f"Local Ollama model {model} failed: {str(e)}")

    def _generate_local_chat(self, messages, max_tokens=6000):
        """Generate chat response using a local Ollama instance."""
        model = self._get_local_ollama_model()
        if not model:
            raise Exception("All AI providers (Gemini, Groq, LongCat, HuggingFace) failed due to quota limits, and no local Ollama instance was found on port 11434. Please install Ollama or try again later.")
            
        logger.info(f"Routing chat generation to local Ollama model: {model}")
        try:
            resp = requests.post('http://localhost:11434/api/chat', json={
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "num_ctx": 8192,
                    "num_predict": max_tokens,
                    "temperature": 0.7
                }
            }, timeout=120)
            resp.raise_for_status()
            content = resp.json().get('message', {}).get('content', '')
            
            if r'\begin{document}' in content and r'\end{document}' not in content:
                open_items = content.count(r'\begin{itemize}') - content.count(r'\end{itemize}')
                for _ in range(max(0, open_items)):
                    content += '\n\\end{itemize}'
                content += '\n\\end{document}'
                
            return content
        except Exception as e:
            logger.error(f"Local Ollama chat failed: {e}")
            raise Exception(f"Local Ollama model {model} failed: {str(e)}")

    def _generate_longcat(self, prompt, api_key, max_tokens=6000):
        """Generate text using LongCat API platform."""
        import requests
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": LONGCAT_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": min(max_tokens, 8000),
            "temperature": 0.7
        }
        try:
            resp = requests.post(LONGCAT_API_URL, headers=headers, json=data, timeout=120)
            resp.raise_for_status()
            resp_data = resp.json()
            content = resp_data['choices'][0]['message']['content']
            tokens = resp_data.get('usage', {}).get('total_tokens', 0)
            
            if r'\begin{document}' in content and r'\end{document}' not in content:
                open_items = content.count(r'\begin{itemize}') - content.count(r'\end{itemize}')
                for _ in range(max(0, open_items)):
                    content += '\n\\end{itemize}'
                content += '\n\\end{document}'
                
            logger.info(f'[MONITOR] Tier 3 Success: LongCat API ({tokens} tokens)')
            return {"content": content, "provider": "LongCat API", "tokens": tokens}
        except Exception as e:
            logger.error(f"LongCat generation failed: {e}")
            raise Exception(f"LongCat API failed: {str(e)}")

    def _generate_longcat_chat(self, messages, api_key, max_tokens=6000):
        """Generate chat response using LongCat API."""
        import requests
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": LONGCAT_MODEL,
            "messages": messages,
            "max_tokens": min(max_tokens, 8000),
            "temperature": 0.7
        }
        resp = requests.post(LONGCAT_API_URL, headers=headers, json=data, timeout=120)
        resp.raise_for_status()
        resp_data = resp.json()
        content = resp_data['choices'][0]['message']['content']
        tokens = resp_data.get('usage', {}).get('total_tokens', 0)
        
        logger.info(f'[MONITOR] Chat Success: LongCat API ({tokens} tokens)')
        return {"content": content, "provider": "LongCat API", "tokens": tokens}

    def _generate_groq(self, prompt, api_key, max_tokens=6000):
        """Generate text using Groq API (High performance fallback)."""
        import requests
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.1-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": min(max_tokens, 8000),
            "temperature": 0.7
        }
        resp = requests.post(url, headers=headers, json=data, timeout=60)
        resp.raise_for_status()
        resp_data = resp.json()
        content = resp_data['choices'][0]['message']['content']
        tokens = resp_data.get('usage', {}).get('total_tokens', 0)
        
        logger.info(f'[MONITOR] Tier 2 Success: Groq API ({tokens} tokens)')
        return {"content": content, "provider": "Groq API", "tokens": tokens}

    def _generate_groq_chat(self, messages, api_key, max_tokens=6000):
        """Generate chat response using Groq API."""
        import requests
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.1-70b-versatile",
            "messages": messages,
            "max_tokens": min(max_tokens, 8000),
            "temperature": 0.7
        }
        resp = requests.post(url, headers=headers, json=data, timeout=60)
        resp.raise_for_status()
        content = resp.json()['choices'][0]['message']['content']
        return {"content": content, "provider": "Groq API"}

    def _generate_hf(self, prompt, model, max_tokens=6000):
        """Generate text using Hugging Face Inference API."""
        messages = [{"role": "user", "content": prompt}]
        response = self.hf_client.chat_completion(
            messages=messages,
            model=model,
            max_tokens=min(max_tokens, 8000),
            temperature=0.7,
        )
        content = response.choices[0].message.content
        tokens = len(prompt + content) // 4  # Estimate for HF
        
        # Emergency cutoff prevention: if HF hits max tokens and cuts off before closing, force close it
        if r'\begin{document}' in content and r'\end{document}' not in content:
            # Try to close any open itemize lists heuristically
            open_items = content.count(r'\begin{itemize}') - content.count(r'\end{itemize}')
            for _ in range(max(0, open_items)):
                content += '\n\\end{itemize}'
            content += '\n\\end{document}'
            
        logger.info(f'[MONITOR] Tier 3/4 Success: HuggingFace {model} ({tokens} est. tokens)')
        return {"content": content, "provider": f"HF {model}", "tokens": tokens}

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
        Returns a dict: {'reply': str, 'requires_edit': bool}
        """
        from .prompts import get_chat_system_prompt
        import json

        # Build Gemini multi-turn history
        gemini_history = []
        hf_messages = [{"role": "system", "content": get_chat_system_prompt()}]

        if chat_history_qs:
            history_list = list(chat_history_qs)
            
            # Remove ALL trailing user messages from the DB history.
            # This ensures we don't send consecutive user messages when we append the current context_msg.
            # It also cleans up any previous user requests that failed to generate an AI response.
            while history_list and history_list[-1].role == 'user':
                history_list.pop()
                
            for msg in history_list:
                # We only want to feed the text 'reply' back into history, not the raw JSON
                text_content = msg.content
                role_gemini = "user" if msg.role == "user" else "model"
                role_hf = "user" if msg.role == "user" else "assistant"
                
                # Consolidate consecutive roles
                if gemini_history and gemini_history[-1]["role"] == role_gemini:
                    gemini_history[-1]["parts"][0] += "\n\n" + text_content
                else:
                    gemini_history.append({"role": role_gemini, "parts": [text_content]})
                    
                if hf_messages and hf_messages[-1]["role"] == role_hf:
                    hf_messages[-1]["content"] += "\n\n" + text_content
                else:
                    hf_messages.append({"role": role_hf, "content": text_content})

        def _parse_chat_response(res_dict):
            text = res_dict['content']
            try:
                # Find the first { and last } to strip conversational garbage
                start_idx = text.find('{')
                end_idx = text.rfind('}')
                
                if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
                    json_text = text[start_idx:end_idx+1]
                    parsed = json.loads(json_text)
                    
                    req_edit = parsed.get('requires_edit', False)
                    if isinstance(req_edit, str):
                        req_edit = req_edit.lower() == 'true'
                        
                    res_dict['reply'] = parsed.get('reply', text)
                    res_dict['requires_edit'] = bool(req_edit)
                    return res_dict
                    
                # Fallback if no JSON brackets found but we know they asked for an edit via heuristics
                requires_edit = any(word in text.lower() for word in ['update', 'add', 'change', 'remove', 'sure', 'moment', 'generate'])
                res_dict['reply'] = text
                res_dict['requires_edit'] = requires_edit
                return res_dict
            except Exception as e:
                logger.error(f'Failed to parse JSON chat response: {e}. Raw text: {text}')
                # Heuristic fallback
                requires_edit = any(word in text.lower() for word in ['update', 'add', 'change', 'remove', 'sure', 'moment', 'generate'])
                res_dict['reply'] = text
                res_dict['requires_edit'] = requires_edit
                return res_dict

        # Tiered Fallback with Error Tracking
        tier_errors = []

        # Attempt 1: Gemini Chat (With Rotation)
        attempts = 0
        gemini_failed = False
        while attempts < len(self.gemini_keys):
            try:
                chat = self.gemini_model.start_chat(history=gemini_history)
                response = chat.send_message(
                    user_message,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=1024,
                        temperature=0.8,
                    )
                )
                tokens = getattr(response, 'usage_metadata', {}).total_token_count if hasattr(response, 'usage_metadata') else 0
                logger.info(f'[MONITOR] Chat Success: Gemini Key #{self.current_key_index+1} ({tokens} tokens)')
                return _parse_chat_response({"content": response.text, "provider": "Gemini", "tokens": tokens})
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg or "ResourceExhausted" in err_msg or "Quota" in err_msg:
                    logger.warning(f'[MONITOR] Gemini Chat Key #{self.current_key_index+1} hit quota. Rotating...')
                    if not self._rotate_gemini_key(): 
                        tier_errors.append(f"Gemini: All {len(self.gemini_keys)} keys hit quota")
                        gemini_failed = True
                        break
                    attempts += 1
                else:
                    logger.warning(f'[MONITOR] Tier 1 Gemini chat critical error ({e}). Trying backups...')
                    tier_errors.append(f"Gemini: {err_msg[:100]}")
                    gemini_failed = True
                    break

        if not gemini_failed and attempts >= len(self.gemini_keys):
            tier_errors.append(f"Gemini: No keys available")

        hf_messages.append({"role": "user", "content": user_message})

        # Attempt 2: Groq Chat
        try:
            groq_key = getattr(settings, 'GROQ_API_KEY', None)
            if groq_key:
                res = self._generate_groq_chat(hf_messages, groq_key, max_tokens=1024)
                return _parse_chat_response(res)
            else:
                tier_errors.append("Groq: No API Key")
        except Exception as e:
            logger.warning(f'[MONITOR] Groq chat fallback failed: {e}')
            tier_errors.append(f"Groq: {str(e)[:100]}")
        
        # Attempt 3: LongCat API
        try:
            lc_key = getattr(settings, 'LONGCAT_API_KEY', None)
            if lc_key:
                lc_res = self._generate_longcat_chat(hf_messages, lc_key, max_tokens=1024)
                return _parse_chat_response(lc_res)
            else:
                tier_errors.append("LongCat: No API Key")
        except Exception as e:
            logger.warning(f'[MONITOR] LongCat chat failed ({e}), falling back...')
            tier_errors.append(f"LongCat: {str(e)[:100]}")

        # Attempt 4: Hugging Face
        try:
            hf_res = self._generate_hf_chat(hf_messages, HF_MODEL, max_tokens=1024)
            return _parse_chat_response(hf_res)
        except Exception as e:
            logger.warning(f'[MONITOR] HF chat failed ({e}), trying fallback...')
            tier_errors.append(f"HF (Qwen): {str(e)[:100]}")

        try:
            hf_fb_res = self._generate_hf_chat(hf_messages, HF_FALLBACK_MODEL, max_tokens=1024)
            return _parse_chat_response(hf_fb_res)
        except Exception as e:
            logger.warning(f'[MONITOR] HF chat fallback failed: {e}. Trying Local Ollama...')
            tier_errors.append(f"HF (Zephyr): {str(e)[:100]}")
            
        try:
            local_res = self._generate_local_chat(hf_messages, max_tokens=1024)
            return _parse_chat_response(local_res)
        except Exception as e_local:
            error_summary = " | ".join(tier_errors)
            logger.error(f'[MONITOR] All AI providers failed for chat: {error_summary}')
            model = self._get_local_ollama_model()
            if not model:
                raise Exception(f"All AI providers failed. Reasons: {error_summary}. (No local Ollama found on port 11434)")
            else:
                raise Exception(f"All AI providers failed. Reasons: {error_summary}. Local Ollama Error: {str(e_local)}")

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
            history_list = list(chat_history_qs)
            
            # Remove ALL trailing user messages from the DB history.
            # This ensures we don't send consecutive user messages when we append the current context_msg.
            # It also cleans up any previous user requests that failed to generate an AI response.
            while history_list and history_list[-1].role == 'user':
                history_list.pop()
                
            for msg in history_list:
                role_gemini = "user" if msg.role == "user" else "model"
                role_hf = "user" if msg.role == "user" else "assistant"
                
                # Gemini & HF require strictly alternating roles. Guard against consecutive same-role messages.
                if gemini_history and gemini_history[-1]["role"] == role_gemini:
                    gemini_history[-1]["parts"][0] += "\n\n" + msg.content
                else:
                    gemini_history.append({"role": role_gemini, "parts": [msg.content]})
                    
                if hf_history and hf_history[-1]["role"] == role_hf:
                    hf_history[-1]["content"] += "\n\n" + msg.content
                else:
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

        # Tiered Fallback with Error Tracking
        tier_errors = []

        # Tier 1: Gemini (With Rotation)
        attempts = 0
        gemini_failed = False
        while attempts < len(self.gemini_keys):
            try:
                custom_model = genai.GenerativeModel('models/gemini-2.0-flash', system_instruction=system_instruction)
                chat = custom_model.start_chat(history=gemini_history)
                response = chat.send_message(
                    context_msg,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=max_tokens_val,
                        temperature=temperature,
                    )
                )
                tokens = getattr(response, 'usage_metadata', {}).total_token_count if hasattr(response, 'usage_metadata') else 0
                logger.info(f'[MONITOR] Edit Success: Gemini Key #{self.current_key_index+1} ({tokens} tokens)')
                return {"content": response.text, "provider": "Gemini", "tokens": tokens}
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg or "ResourceExhausted" in err_msg or "Quota" in err_msg:
                    logger.warning(f'[MONITOR] Gemini Edit Key #{self.current_key_index+1} hit quota. Rotating...')
                    if not self._rotate_gemini_key(): 
                        tier_errors.append(f"Gemini: All {len(self.gemini_keys)} keys hit quota")
                        gemini_failed = True
                        break
                    attempts += 1
                else:
                    logger.warning(f'[MONITOR] Tier 1 Gemini edit critical error: {e}. Trying backups...')
                    tier_errors.append(f"Gemini: {err_msg[:100]}")
                    gemini_failed = True
                    break
        
        if not gemini_failed and attempts >= len(self.gemini_keys):
            tier_errors.append(f"Gemini: No keys available")

        # Tier 2: Groq Chat
        try:
            groq_key = getattr(settings, 'GROQ_API_KEY', None)
            if groq_key:
                return self._generate_groq_chat(hf_history, groq_key, max_tokens=max_tokens_val)
            else:
                tier_errors.append("Groq: No API Key")
        except Exception as e:
            logger.warning(f'[MONITOR] Tier 2 Groq Edit fallback failed: {e}')
            tier_errors.append(f"Groq: {str(e)[:100]}")
            
        # Tier 3: LongCat API
        try:
            lc_key = getattr(settings, 'LONGCAT_API_KEY', None)
            if lc_key:
                return self._generate_longcat_chat(hf_history, lc_key, max_tokens=max_tokens_val)
            else:
                tier_errors.append("LongCat: No API Key")
        except Exception as e:
            logger.warning(f'LongCat primary model failed ({e}), trying Hugging Face...')
            tier_errors.append(f"LongCat: {str(e)[:100]}")

        # Tier 4: Hugging Face (Qwen2.5-Coder)
        try:
            return self._generate_hf_chat(hf_history, HF_MODEL)
        except Exception as e:
            logger.warning(f'HF primary model failed ({e}), trying fallback...')
            tier_errors.append(f"HF (Qwen): {str(e)[:100]}")

        # Tier 5: Hugging Face fallback
        try:
            return self._generate_hf_chat(hf_history, HF_FALLBACK_MODEL)
        except Exception as e:
            logger.warning(f'HF fallback model failed ({e}). Trying Local Ollama...')
            tier_errors.append(f"HF (Zephyr): {str(e)[:100]}")
            
        # Final Tier: Local Ollama
        try:
            return self._generate_local_chat(hf_history, max_tokens=max_tokens_val)
        except Exception as e_local:
            error_summary = " | ".join(tier_errors)
            logger.error(f'[MONITOR] All AI providers failed: {error_summary}')
            model = self._get_local_ollama_model()
            if not model:
                raise Exception(f"All AI providers failed. Reasons: {error_summary}. (No local Ollama found on port 11434)")
            else:
                raise Exception(f"All AI providers failed. Reasons: {error_summary}. Local Ollama Error: {str(e_local)}")

    def _generate_hf_chat(self, messages, model, max_tokens=6000):
        """Generate text using Hugging Face Inference API with conversation history."""
        response = self.hf_client.chat_completion(
            messages=messages,
            model=model,
            max_tokens=min(max_tokens, 8000),
            temperature=0.7,
        )
        content = response.choices[0].message.content
        tokens = len(str(messages) + content) // 4  # Estimate for HF Chat
        
        if r'\begin{document}' in content and r'\end{document}' not in content:
            open_items = content.count(r'\begin{itemize}') - content.count(r'\end{itemize}')
            for _ in range(max(0, open_items)):
                content += '\n\\end{itemize}'
            content += '\n\\end{document}'
            
        logger.info(f'[MONITOR] Edit Success: HF Chat {model} ({tokens} est. tokens)')
        return {"content": content, "provider": f"HF Chat {model}", "tokens": tokens}


# Singleton instance
_client = None

def get_client():
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client
