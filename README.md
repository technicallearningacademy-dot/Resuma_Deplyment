# 🚀 AI Resume Builder

<p align="center">
  <img src="https://img.shields.io/badge/Django-5.1.4-green?style=for-the-badge&logo=django" />
  <img src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/AI-Gemini%202.0-orange?style=for-the-badge&logo=google" />
  <img src="https://img.shields.io/badge/LaTeX-Powered-red?style=for-the-badge&logo=latex" />
  <img src="https://img.shields.io/badge/License-MIT-purple?style=for-the-badge" />
</p>
> **A full-stack AI-powered resume builder** that generates professional, ATS-optimized LaTeX resumes from your profile — with live PDF preview, 14 beautiful templates, and multi-model AI with automatic fallback.

---

## 📸 Screenshots

| Dashboard | Resume Builder | PDF Preview |
|-----------|---------------|-------------|
| Manage all your resumes | AI prompt + LaTeX editor | Live compiled PDF |

---

## ✨ Features

### 🤖 AI-Powered Generation & Conversational Editing
- **Surgical AI Edits**: Highlight specific sections to incrementally edit your resume using intelligent conversational memory.
- **Google Gemini 2.0 Flash-Lite** as primary model — fast and cost-effective
- **Hugging Face Qwen2.5-Coder-32B** as automatic fallback
- **Llama 3.2-3B** as final emergency fallback
- Generates complete, valid LaTeX from your profile in seconds
- Custom prompt support for role-specific optimization
- Animated typing indicators for AI progress feedback

### 📄 14 Professional Templates
| Template | Style |
|----------|-------|
| **Modern ATS Clean** | Navy blue, Helvetica, FontAwesome icons |
| **Minimal Academic** | Classic black/white serif, no color |
| **Corporate Executive** | Forest green, bold headers, executive layout |
| **Creative Designer** | Teal color-block sections, vibrant sans-serif |
| **Technical Developer** | Dark terminal theme, monospace, code aesthetic |
| **Ocean Blue Modern** | ⚡ *New!* - Light blue accents, clean sans-serif |
| **Pink Horizon Premium** | ⚡ *New!* - Bold pink branding, premium uppercase headers |
| **Violet X Executive** | ⚡ *New!* - Deep violet leadership design, Palatino font |
| **Gold Luxury** | ⚡ *New!* - Gold & midnight aesthetic, elegant serif |

All 14 templates are **pre-tested** and verified to compile against the `texlive.net` LaTeX compiler.

### 🖥 Live PDF Preview
- Split-screen editor: write LaTeX on the left, see compiled PDF on the right
- Full Preview mode to view the PDF in full-screen
- **CodeMirror** syntax highlighting with LaTeX mode
- Auto-recompilation on edit (2.5s debounce)
- Auto-loads PDF on resume open
- Compiles using local `pdflatex` → fallback to `texlive.net` API

### 📥 Download & Share Options
- **PDF** — full compiled, professionally typeset resume
- **DOCX** — Word-compatible version (via `python-docx`)
- **Share** — Generates a unique public link to share via Gmail, WhatsApp, or direct copy
- Auto-saves before download

### 📁 Version History
- Every save creates a new version snapshot
- Full restore capability from version history
- Tracks change notes and timestamps

### 👤 User Profile System & Rate Limits
- Complete profile: name, contact, summary, job title
- Education entries (institution, degree, GPA, dates)
- Work experience (company, role, dates, achievements)
- Skills (name, category, proficiency level)
- Certifications, projects, links (LinkedIn, GitHub, Portfolio)
- **Global AI Rate Limits**: Admin-controlled total daily usage limits across all AI tools (Chat, Generate, Enhance) with a professional "Locked" state once limits are reached to ensure cost management.

### 🔐 Authentication
- Email/password registration and login
- Google OAuth login via `django-allauth`
- Secure session management

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 5.1.4 |
| **AI Primary** | Google Gemini 2.0 Flash-Lite |
| **AI Fallback** | Hugging Face (Qwen2.5-Coder-32B, Llama-3.2-3B) |
| **LaTeX Compiler** | pdflatex (local) + texlive.net (cloud fallback) |
| **Auth** | django-allauth (email + Google OAuth) |
| **Frontend** | Vanilla HTML/CSS/JS + Tailwind CSS (CDN) |
| **Code Editor** | CodeMirror 5 (LaTeX/stex mode) |
| **PDF Layout** | Split.js for resizable panels |
| **DOCX Export** | python-docx |
| **Image Processing** | Pillow |
| **Deployment** | Gunicorn + WhiteNoise |
| **Database** | SQLite (dev) / PostgreSQL (prod) |

---

## 🗂 Project Structure

```
AI_Resuma_Builder/
│
├── ai_services/              # AI generation logic
│   ├── client.py             # Gemini + HuggingFace client with fallback
│   ├── prompts.py            # Prompt templates for all AI operations
│   ├── template_library.py   # 10 pre-tested LaTeX template skeletons
│   ├── rate_limiter.py       # Per-user daily API call limits
│   ├── views.py              # AI AJAX endpoints (/ai/generate/, /ai/enhance/, /ai/optimize/)
│   └── urls.py               # AI URL routing
│
├── resumes/                  # Resume CRUD and builder
│   ├── models.py             # Resume, ResumeVersion, AIPromptLog, UploadedCV
│   ├── views.py              # Builder, save, preview, download, history
│   └── urls.py               # Resume URL routing
│
├── templates_engine/         # LaTeX compilation
│   ├── compiler.py           # pdflatex → texlive.net → FPDF fallback chain
│   └── converter.py          # LaTeX → DOCX conversion
│
├── users/                    # Authentication & profiles
│   ├── models.py             # UserProfile, Education, Experience, Skill, etc.
│   ├── views.py              # Profile setup, settings
│   └── forms.py              # Profile forms
│
├── templates/                # Django HTML templates
│   ├── base.html             # Base layout
│   ├── landing.html          # Marketing landing page
│   └── resumes/
│       ├── builder.html      # Main split-screen builder UI
│       ├── dashboard.html    # Resume management dashboard
│       ├── history.html      # Version history view
│       └── create.html       # New resume creation
│
├── static/
│   └── css/main.css          # Global styles
│
├── core/
│   ├── settings.py           # Django settings
│   └── urls.py               # Root URL configuration
│
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
└── manage.py
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.11+
- `pdflatex` installed locally (optional but recommended for faster compilation)
  - **Windows:** Install [MiKTeX](https://miktex.org/) or [TeX Live](https://tug.org/texlive/)
  - **Ubuntu/Debian:** `sudo apt install texlive-full`
  - **macOS:** `brew install --cask mactex`

### 1. Clone the Repository
```bash
git clone https://github.com/ihtesham0332/AI_Resuma_Builder.git
cd AI_Resuma_Builder
```

### 2. Create a Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the example env file and fill in your values:
```bash
cp .env.example .env
```

Open `.env` and set:
```env
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Google Gemini AI (get from https://aistudio.google.com/)
GEMINI_API_KEY=your-gemini-api-key

# Hugging Face (optional — works without token for free models)
HF_API_TOKEN=your-hf-token-optional

# Google OAuth (optional — for "Sign in with Google")
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
```

### 5. Apply Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser (optional)
```bash
python manage.py createsuperuser
```

### 7. Run the Development Server
```bash
python manage.py runserver 0.0.0.0:8000
```

Visit **http://127.0.0.1:8000** in your browser on the host machine.
To access the app from another device on the same local network (LAN), find your machine's local IP address (e.g. `192.168.1.X`) and visit **http://<YOUR_LAN_IP>:8000**.

---

## 🔑 Getting API Keys

### Google Gemini API Key (Required)
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Click **"Get API Key"** → **"Create API Key"**
3. Copy the key and paste into your `.env` as `GEMINI_API_KEY`

> **Free tier:** 1,500 requests/day — more than enough for development and small-scale production.

### Hugging Face Token (Optional)
1. Create a free account at [huggingface.co](https://huggingface.co/)
2. Go to Settings → Access Tokens → **New token**
3. Paste into `.env` as `HF_API_TOKEN`

> The app works without the HF token but with lower rate limits on free models.

---

## 🤖 AI Architecture

The AI system uses a **3-tier automatic fallback**:

```
User Request
     │
     ▼
┌─────────────────────────────┐
│  Google Gemini 2.0 Flash-Lite │  ← Primary (fast, high quality)
└─────────────────────────────┘
     │ (fails / rate limited)
     ▼
┌─────────────────────────────┐
│  Qwen2.5-Coder-32B (HF)    │  ← Fallback 1 (excellent for code/LaTeX)
└─────────────────────────────┘
     │ (fails)
     ▼
┌─────────────────────────────┐
│  Llama-3.2-3B (HF)         │  ← Fallback 2 (last resort)
└─────────────────────────────┘
```

### How Resume Generation Works

1. User selects a **template** and provides an optional **custom prompt**
2. System loads the **pre-tested LaTeX template skeleton** for that style
3. AI model fills in the skeleton with actual profile data (name, experience, skills, etc.)
4. Generated LaTeX is compiled to PDF using `pdflatex` or `texlive.net`
5. PDF is rendered in the live preview iframe

---

## 📐 LaTeX Compilation Chain

```
LaTeX Source
     │
     ▼
┌─────────────────┐
│  Local pdflatex │  ← Fastest, highest quality
└─────────────────┘
     │ (not installed / fails)
     ▼
┌─────────────────┐
│  texlive.net    │  ← Free cloud LaTeX compiler (API)
└─────────────────┘
     │ (fails)
     ▼
┌─────────────────┐
│  FPDF fallback  │  ← Renders raw .tex as readable code (last resort)
└─────────────────┘
```

---

## 💰 Cost Estimation (Gemini API)

| Users/Month | Avg Generations | Monthly Cost |
|-------------|----------------|--------------|
| 100 users   | 3 each          | ~$1.10       |
| 1,000 users | 3 each          | ~$11         |
| 10,000 users| 3 each          | ~$110        |

> **Free tier covers:** ~15,000 users/month with 3 API calls each — completely free.

**Pricing:** `$0.075 / 1M input tokens` · `$0.30 / 1M output tokens` (Gemini 2.0 Flash-Lite)

---

## 🗄 Database Models

```
User (Django Auth)
 └── UserProfile (1:1) — contact, summary, job title, photo
      ├── EducationEntry (1:N) — institution, degree, dates, GPA
      ├── ExperienceEntry (1:N) — company, role, dates, achievements
      ├── Skill (1:N) — name, category, proficiency
      ├── Certification (1:N) — name, issuer, date
      └── Project (1:N) — name, description, tech, URL

Resume (N:1 to User)
 ├── ResumeVersion (1:N) — full version history snapshots
 └── AIPromptLog (1:N) — logs every AI call for debugging
```

---

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Landing page |
| `/dashboard/` | GET | User resume dashboard |
| `/resume/create/` | GET/POST | Create new resume |
| `/resume/<id>/builder/` | GET | Resume builder UI |
| `/resume/<id>/save/` | POST | Save LaTeX content |
| `/resume/<id>/preview/` | POST | Compile and return PDF |
| `/resume/<id>/download/pdf/` | GET | Download compiled PDF |
| `/resume/<id>/download/docx/` | GET | Download DOCX version |
| `/resume/<id>/history/` | GET | View version history |
| `/ai/generate/` | POST | Generate LaTeX with AI |
| `/ai/enhance/` | POST | Enhance selected text |
| `/ai/optimize/` | POST | ATS keyword optimization |
| `/profile/setup/` | GET/POST | User profile management |

---

## 🚀 Deployment

### Deploy to a VPS (Ubuntu)

1. **Install system dependencies:**
```bash
sudo apt update
sudo apt install python3.11 python3-pip nginx texlive-full postgresql -y
```

2. **Clone and set up:**
```bash
git clone https://github.com/ihtesham0332/AI_Resuma_Builder.git
cd AI_Resuma_Builder
pip install -r requirements.txt
```

3. **Set environment variables in `.env`** (set `DEBUG=False`, proper `SECRET_KEY`, `ALLOWED_HOSTS`)

4. **Collect static files:**
```bash
python manage.py collectstatic
```

5. **Run with Gunicorn:**
```bash
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

6. **Configure Nginx** as a reverse proxy pointing to `127.0.0.1:8000`

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Ihtesham**
- GitHub: [@ihtesham0332](https://github.com/ihtesham0332)
- Email: ihtesham0345@gmail.com

---

## ⭐ Acknowledgements

- [Google Gemini API](https://ai.google.dev/) — Primary AI model
- [Hugging Face](https://huggingface.co/) — AI fallback models
- [texlive.net](https://texlive.net/) — Cloud LaTeX compiler
- [CodeMirror](https://codemirror.net/) — Code editor in the browser
- [Split.js](https://split.js.org/) — Resizable split panels
- [FontAwesome 5](https://fontawesome.com/) — Icons in LaTeX with `fontawesome5` package

---

<p align="center">Made with ❤️ and LaTeX</p>
