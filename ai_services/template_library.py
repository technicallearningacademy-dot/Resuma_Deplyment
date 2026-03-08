"""
Pre-tested, verified compilable LaTeX template skeletons for each theme.
These are used as the base templates that the AI fills in with actual profile data.
All templates are verified to compile on texlive.net.
"""

TEMPLATES = {
    'modern_ats_clean': r"""
\documentclass[10pt,a4paper]{article}
\usepackage[left=1cm, right=1cm, top=1.2cm, bottom=1.2cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{fontawesome5}

\definecolor{primary}{HTML}{000080}
\definecolor{gray}{HTML}{666666}

\hypersetup{colorlinks=true, urlcolor=primary, linkcolor=primary}

\titleformat{\section}{\large\bfseries\color{primary}}{}{0em}{}[\vspace{-6pt}\rule{\linewidth}{1pt}\vspace{2pt}]
\titlespacing{\section}{0pt}{10pt}{4pt}

\setlength{\parindent}{0pt}
\pagestyle{empty}
\setlist[itemize]{noitemsep, topsep=2pt, leftmargin=15pt}

\begin{document}

% ---- HEADER ----
\begin{center}
    {\LARGE\bfseries\color{primary} {{NAME}}} \\[4pt]
    {\color{gray} {{JOB_TITLE}}} \\[6pt]
    \faEnvelope\ \href{mailto:{{EMAIL}}}{{{EMAIL}}} \quad
    \faPhone\ {{PHONE}} \quad
    \faLinkedin\ \href{{{LINKEDIN}}}{LinkedIn} \quad
    \faGithub\ \href{{{GITHUB}}}{GitHub}
\end{center}

\vspace{4pt}

% ---- SUMMARY ----
\section{Professional Summary}
{{SUMMARY}}

% ---- EXPERIENCE ----
\section{Experience}
{{EXPERIENCE}}

% ---- EDUCATION ----
\section{Education}
{{EDUCATION}}

% ---- SKILLS ----
\section{Skills}
{{SKILLS}}

% ---- PROJECTS ----
\section{Projects}
{{PROJECTS}}

\end{document}
""",

    'minimal_academic': r"""
\documentclass[11pt,a4paper]{article}
\usepackage[left=2cm, right=2cm, top=2cm, bottom=2cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{hyperref}

\hypersetup{colorlinks=false, hidelinks}

\titleformat{\section}{\large\scshape}{}{0em}{}[\rule{\linewidth}{0.4pt}]
\titlespacing{\section}{0pt}{12pt}{6pt}
\titleformat{\subsection}{\normalsize\bfseries}{}{0em}{}
\titlespacing{\subsection}{0pt}{6pt}{2pt}

\setlength{\parindent}{0pt}
\pagestyle{empty}
\setlist[itemize]{noitemsep, topsep=2pt, leftmargin=15pt}

\begin{document}

% ---- HEADER ----
\begin{center}
    {\LARGE\scshape {{NAME}}} \\[4pt]
    {{JOB_TITLE}} \\[4pt]
    \href{mailto:{{EMAIL}}}{{{EMAIL}}} \quad | \quad {{PHONE}} \\[2pt]
    \href{{{LINKEDIN}}}{LinkedIn} \quad | \quad \href{{{GITHUB}}}{GitHub}
\end{center}

\section{Professional Summary}
{{SUMMARY}}

\section{Experience}
{{EXPERIENCE}}

\section{Education}
{{EDUCATION}}

\section{Skills}
{{SKILLS}}

\section{Projects}
{{PROJECTS}}

\end{document}
""",

    'corporate_executive': r"""
\documentclass[10pt,a4paper]{article}
\usepackage[left=1.2cm, right=1.2cm, top=1.5cm, bottom=1.5cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{fontawesome5}

\definecolor{primary}{HTML}{228B22}
\definecolor{darkgray}{HTML}{2C2C2C}

\hypersetup{colorlinks=true, urlcolor=primary}

\titleformat{\section}{\large\bfseries\color{primary}}{}{0em}{}[\color{primary}\rule{\linewidth}{1.5pt}\vspace{2pt}]
\titlespacing{\section}{0pt}{12pt}{6pt}

\setlength{\parindent}{0pt}
\pagestyle{empty}
\setlist[itemize]{noitemsep, topsep=2pt, leftmargin=15pt}

\begin{document}

% ---- EXECUTIVE HEADER ----
\begin{center}
    {\Huge\bfseries\color{darkgray} {{NAME}}} \\[6pt]
    {\large\color{primary} {{JOB_TITLE}}} \\[6pt]
    \faEnvelope\ \href{mailto:{{EMAIL}}}{{{EMAIL}}} \quad
    \faPhone\ {{PHONE}} \quad
    \faLinkedin\ \href{{{LINKEDIN}}}{LinkedIn}
\end{center}

\vspace{6pt}

\section{Executive Summary}
{{SUMMARY}}

\section{Professional Experience}
{{EXPERIENCE}}

\section{Education}
{{EDUCATION}}

\section{Core Competencies}
{{SKILLS}}

\section{Key Projects}
{{PROJECTS}}

\end{document}
""",

    'creative_designer': r"""
\documentclass[10pt,a4paper]{article}
\usepackage[left=1cm, right=1cm, top=1.2cm, bottom=1.2cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{fontawesome5}

\definecolor{accent}{HTML}{008080}
\definecolor{lightaccent}{HTML}{E0F4F4}
\definecolor{darkgray}{HTML}{333333}

\hypersetup{colorlinks=true, urlcolor=accent}

\newcommand{\sectiontitle}[1]{%
    \vspace{8pt}%
    {\large\bfseries\color{white}\colorbox{accent}{\makebox[\linewidth][l]{\hspace{4pt}#1}}}%
    \vspace{4pt}%
}

\setlength{\parindent}{0pt}
\pagestyle{empty}
\setlist[itemize]{noitemsep, topsep=2pt, leftmargin=15pt}

\begin{document}

% ---- CREATIVE HEADER ----
{\Huge\bfseries\color{accent} {{NAME}}} \hfill
{\large\color{darkgray} {{JOB_TITLE}}} \\[6pt]
\faEnvelope\ \href{mailto:{{EMAIL}}}{{{EMAIL}}} \quad
\faPhone\ {{PHONE}} \quad
\faLinkedin\ \href{{{LINKEDIN}}}{LinkedIn} \quad
\faGithub\ \href{{{GITHUB}}}{GitHub}

\rule{\linewidth}{0.6pt}
\vspace{2pt}

\sectiontitle{About Me}
{{SUMMARY}}

\sectiontitle{Experience}
{{EXPERIENCE}}

\sectiontitle{Education}
{{EDUCATION}}

\sectiontitle{Skills}
{{SKILLS}}

\sectiontitle{Projects}
{{PROJECTS}}

\end{document}
""",

    'technical_developer': r"""
\documentclass[10pt,a4paper]{article}
\usepackage[left=1.2cm, right=1.2cm, top=1.2cm, bottom=1.2cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{inconsolata}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{fontawesome5}
\usepackage{pagecolor}

\definecolor{background}{HTML}{2F3136}
\definecolor{accent}{HTML}{00468B}
\definecolor{textcol}{HTML}{DCDDDE}
\definecolor{headercol}{HTML}{FFFFFF}

\pagecolor{background}
\color{textcol}
\hypersetup{colorlinks=true, urlcolor=accent}

\titleformat{\section}{\normalfont\large\bfseries\ttfamily\color{headercol}}{}{0em}{}
\titlespacing{\section}{0pt}{10pt}{4pt}

\setlength{\parindent}{0pt}
\pagestyle{empty}
\setlist[itemize]{noitemsep, topsep=2pt, leftmargin=15pt, label=\textcolor{accent}{>}}

\begin{document}

% ---- TECH HEADER ----
{\color{headercol}\Huge\bfseries\ttfamily {{NAME}}} \\[4pt]
{\color{accent} {{JOB_TITLE}}} \\[6pt]
\faEnvelope\ \href{mailto:{{EMAIL}}}{{{EMAIL}}} \quad
\faPhone\ {{PHONE}} \quad
\faGithub\ \href{{{GITHUB}}}{GitHub} \quad
\faLinkedin\ \href{{{LINKEDIN}}}{LinkedIn}

\vspace{4pt}
\textcolor{accent}{\rule{\linewidth}{0.6pt}}

\section{Summary}
{{SUMMARY}}

\section{Experience}
{{EXPERIENCE}}

\section{Education}
{{EDUCATION}}

\section{Skills}
{{SKILLS}}

\section{Projects}
{{PROJECTS}}

\end{document}
""",

    'startup_founder': r"""
\documentclass[10pt,a4paper]{article}
\usepackage[left=1.5cm, right=1.5cm, top=1.5cm, bottom=1.5cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[default]{sourcesanspro}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{fontawesome5}

\definecolor{primary}{HTML}{FF6B35}
\definecolor{darkblue}{HTML}{1A365D}
\definecolor{gray}{HTML}{4A5568}

\hypersetup{colorlinks=true, urlcolor=primary, linkcolor=primary}

\titleformat{\section}{\large\bfseries\color{darkblue}}{}{0em}{}[\color{primary}\vspace{-4pt}\rule{\linewidth}{2pt}\vspace{2pt}]
\titlespacing{\section}{0pt}{12pt}{6pt}

\setlength{\parindent}{0pt}
\pagestyle{empty}
\setlist[itemize]{noitemsep, topsep=2pt, leftmargin=15pt}

\begin{document}

% ---- HEADER ----
\begin{center}
    {\Huge\bfseries\color{darkblue} {{NAME}}} \\[6pt]
    {\Large\color{primary} {{JOB_TITLE}}} \\[6pt]
    {\color{gray}
    \faEnvelope\ \href{mailto:{{EMAIL}}}{{{EMAIL}}} \quad
    \faPhone\ {{PHONE}} \quad
    \faLinkedin\ \href{{{LINKEDIN}}}{LinkedIn} \quad
    \faGithub\ \href{{{GITHUB}}}{GitHub}
    }
\end{center}

\vspace{6pt}

\section{Summary}
{{SUMMARY}}

\section{Experience}
{{EXPERIENCE}}

\section{Education}
{{EDUCATION}}

\section{Skills}
{{SKILLS}}

\section{Projects}
{{PROJECTS}}

\end{document}
""",

    'data_scientist': r"""
\documentclass[10pt,a4paper]{article}
\usepackage[left=1.2cm, right=1.2cm, top=1.2cm, bottom=1.2cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{fontawesome5}
\usepackage{tabularx}

\definecolor{primary}{HTML}{2B6CB0}
\definecolor{gray}{HTML}{718096}

\hypersetup{colorlinks=true, urlcolor=primary}

\titleformat{\section}{\large\scshape\color{primary}}{}{0em}{}[\vspace{-4pt}\rule{\linewidth}{1pt}\vspace{2pt}]
\titlespacing{\section}{0pt}{12pt}{4pt}

\setlength{\parindent}{0pt}
\pagestyle{empty}
\setlist[itemize]{noitemsep, topsep=2pt, leftmargin=15pt}

\begin{document}

% ---- HEADER ----
{\Huge\scshape\color{primary} {{NAME}}} \hfill
{\large\color{gray} {{JOB_TITLE}}} \\[6pt]
\begin{tabularx}{\linewidth}{@{} X r @{}}
\faEnvelope\ \href{mailto:{{EMAIL}}}{{{EMAIL}}} & \faLinkedin\ \href{{{LINKEDIN}}}{LinkedIn} \\
\faPhone\ {{PHONE}} & \faGithub\ \href{{{GITHUB}}}{GitHub} \\
\end{tabularx}

\vspace{4pt}

\section{Profile Analysis}
{{SUMMARY}}

\section{Methodology \& Experience}
{{EXPERIENCE}}

\section{Academic Foundation}
{{EDUCATION}}

\section{Technical Arsenal}
{{SKILLS}}

\section{Research \& Projects}
{{PROJECTS}}

\end{document}
""",

    'marketing_pro': r"""
\documentclass[10pt,a4paper]{article}
\usepackage[left=1.5cm, right=1.5cm, top=1.5cm, bottom=1.5cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{fontawesome5}

\definecolor{primary}{HTML}{805AD5}
\definecolor{dark}{HTML}{2D3748}

\hypersetup{colorlinks=true, urlcolor=primary}

\titleformat{\section}{\large\bfseries\color{white}}{}{0em}{%
  \colorbox{primary}{%
    \parbox{\dimexpr\linewidth-2\fboxsep\relax}{%
      \centering #1%
    }%
  }%
}
\titlespacing{\section}{0pt}{12pt}{6pt}

\setlength{\parindent}{0pt}
\pagestyle{empty}
\setlist[itemize]{noitemsep, topsep=2pt, leftmargin=15pt}

\begin{document}

% ---- HEADER ----
\begin{center}
    {\Huge\bfseries\color{primary} {{NAME}}} \\[6pt]
    {\Large\color{dark} {{JOB_TITLE}}} \\[6pt]
    \faEnvelope\ \href{mailto:{{EMAIL}}}{{{EMAIL}}} \quad
    \faPhone\ {{PHONE}} \quad
    \faLinkedin\ \href{{{LINKEDIN}}}{LinkedIn}
\end{center}

\vspace{6pt}

\section{Profile}
{{SUMMARY}}

\section{Campaigns \& Experience}
{{EXPERIENCE}}

\section{Education}
{{EDUCATION}}

\section{Expertise \& Tools}
{{SKILLS}}

\section{Portfolio Projects}
{{PROJECTS}}

\end{document}
""",

    'legal_standard': r"""
\documentclass[11pt,a4paper]{article}
\usepackage[left=2.5cm, right=2.5cm, top=2.5cm, bottom=2.5cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{mathptmx} % Times Roman
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{hyperref}

\hypersetup{colorlinks=false, hidelinks}

\titleformat{\section}{\large\scshape\centering}{}{0em}{}[\vspace{-4pt}\rule{\linewidth}{0.5pt}\vspace{2pt}]
\titlespacing{\section}{0pt}{14pt}{8pt}

\titleformat{\subsection}{\normalsize\bfseries}{}{0em}{}
\titlespacing{\subsection}{0pt}{8pt}{4pt}

\setlength{\parindent}{0pt}
\pagestyle{empty}
\setlist[itemize]{noitemsep, topsep=2pt, leftmargin=20pt, label=--}

\begin{document}

% ---- HEADER ----
\begin{center}
    {\huge\scshape {{NAME}}} \\[8pt]
    {\large {{JOB_TITLE}}} \\[6pt]
    {{EMAIL}} \quad \textbar \quad {{PHONE}} \\[2pt]
    {{LINKEDIN}}
\end{center}

\vspace{10pt}

\section{Professional Summary}
{{SUMMARY}}

\section{Legal Experience}
{{EXPERIENCE}}

\section{Education \& Bar Admissions}
{{EDUCATION}}

\section{Specialized Skills}
{{SKILLS}}

\section{Notable Cases \& Projects}
{{PROJECTS}}

\end{document}
""",

    'medical_clinical': r"""
\documentclass[10pt,a4paper]{article}
\usepackage[left=1.5cm, right=1.5cm, top=1.5cm, bottom=1.5cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{tgheros}
\renewcommand{\familydefault}{\sfdefault}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{fontawesome5}

\definecolor{primary}{HTML}{00A3C4}
\definecolor{dark}{HTML}{1A202C}

\hypersetup{colorlinks=true, urlcolor=primary}

\titleformat{\section}{\large\bfseries\color{primary}}{}{0em}{}[\vspace{-4pt}\rule{\linewidth}{1.5pt}\vspace{2pt}]
\titlespacing{\section}{0pt}{12pt}{6pt}

\setlength{\parindent}{0pt}
\pagestyle{empty}
\setlist[itemize]{noitemsep, topsep=2pt, leftmargin=15pt}

\begin{document}

% ---- HEADER ----
{\Huge\bfseries\color{dark} {{NAME}}} \\[6pt]
{\large\color{primary} {{JOB_TITLE}}} \\[8pt]
\faEnvelope\ \href{mailto:{{EMAIL}}}{{{EMAIL}}} \quad
\faPhone\ {{PHONE}} \quad
\faLinkedin\ \href{{{LINKEDIN}}}{LinkedIn}

\vspace{6pt}

\section{Clinical Summary}
{{SUMMARY}}

\section{Clinical Experience}
{{EXPERIENCE}}

\section{Education \& Training}
{{EDUCATION}}

\section{Certifications \& Skills}
{{SKILLS}}

\section{Research \& Publications}
{{PROJECTS}}

\end{document}
""",

    'ocean_blue_modern': r"""
\documentclass[10pt,a4paper]{article}
\usepackage[left=1.5cm, right=1.5cm, top=1.5cm, bottom=1.5cm]{geometry}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{fontawesome5}
\usepackage{tgheros}
\renewcommand{\familydefault}{\sfdefault}

\definecolor{ocean}{HTML}{0ea5e9}
\definecolor{dark}{HTML}{1e293b}

\hypersetup{colorlinks=true, urlcolor=ocean}
\titleformat{\section}{\large\bfseries\color{ocean}}{}{0em}{}[\vspace{-4pt}\rule{\linewidth}{0.8pt}]
\titlespacing{\section}{0pt}{12pt}{6pt}

\begin{document}
\begin{center}
    {\Huge\bfseries\color{dark} {{NAME}}} \\[4pt]
    {\large\color{ocean} {{JOB_TITLE}}} \\[6pt]
    \faEnvelope\ \href{mailto:{{EMAIL}}}{{{EMAIL}}} \quad \faPhone\ {{PHONE}} \quad \faLinkedin\ \href{{{LINKEDIN}}}{LinkedIn}
\end{center}
\section{Summary} {{SUMMARY}}
\section{Experience} {{EXPERIENCE}}
\section{Education} {{EDUCATION}}
\section{Skills} {{SKILLS}}
\section{Projects} {{PROJECTS}}
\end{document}
""",

    'pink_horizon_premium': r"""
\documentclass[10pt,a4paper]{article}
\usepackage[left=1.5cm, right=1.5cm, top=1.5cm, bottom=1.5cm]{geometry}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{fontawesome5}
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}

\definecolor{pinkh}{HTML}{db2777}
\definecolor{charcoal}{HTML}{374151}

\hypersetup{colorlinks=true, urlcolor=pinkh}
\titleformat{\section}{\large\bfseries\color{pinkh}\uppercase}{}{0em}{}[\vspace{-2pt}\rule{\linewidth}{1.2pt}]
\titlespacing{\section}{0pt}{14pt}{8pt}

\begin{document}
{\Huge\bfseries\color{pinkh} {{NAME}}} \hfill {\large\color{charcoal} {{JOB_TITLE}}} \\[6pt]
\faEnvelope\ \href{mailto:{{EMAIL}}}{{{EMAIL}}} \quad \faPhone\ {{PHONE}} \quad \faLinkedin\ \href{{{LINKEDIN}}}{LinkedIn}
\rule{\linewidth}{0.4pt}
\section{Profile} {{SUMMARY}}
\section{Professional Experience} {{EXPERIENCE}}
\section{Education} {{EDUCATION}}
\section{Tools \& Expertise} {{SKILLS}}
\end{document}
""",

    'violet_x_executive': r"""
\documentclass[10pt,a4paper]{article}
\usepackage[left=1.2cm, right=1.2cm, top=1.2cm, bottom=1.2cm]{geometry}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{fontawesome5}
\usepackage{palatino}

\definecolor{violetx}{HTML}{7c3aed}
\definecolor{deep}{HTML}{1e1b4b}

\hypersetup{colorlinks=true, urlcolor=violetx}
\titleformat{\section}{\Large\bfseries\color{deep}}{}{0em}{}[\vspace{-2pt}\textcolor{violetx}{\rule{\linewidth}{2pt}}]
\titlespacing{\section}{0pt}{12pt}{6pt}

\begin{document}
{\Huge\bfseries\color{deep} {{NAME}}} \\[2pt]
{\large\color{violetx} {{JOB_TITLE}}} \\[8pt]
\faEnvelope\ \href{mailto:{{EMAIL}}}{{{EMAIL}}} \quad \faPhone\ {{PHONE}} \quad \faLinkedin\ \href{{{LINKEDIN}}}{LinkedIn} \quad \faGithub\ \href{{{GITHUB}}}{GitHub}
\vspace{10pt}
\section{Executive Summary} {{SUMMARY}}
\section{Leadership \& Experience} {{EXPERIENCE}}
\section{Education} {{EDUCATION}}
\section{Technical Skills} {{SKILLS}}
\end{document}
""",

    'gold_luxury': r"""
\documentclass[10pt,a4paper]{article}
\usepackage[left=1.5cm, right=1.5cm, top=1.5cm, bottom=1.5cm]{geometry}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{fontawesome5}
\usepackage{times}

\definecolor{gold}{HTML}{b45309}
\definecolor{night}{HTML}{0f172a}

\hypersetup{colorlinks=true, urlcolor=gold}
\titleformat{\section}{\large\bfseries\color{gold}\centering}{}{0em}{}[\vspace{-2pt}\rule{0.2\linewidth}{0.5pt}]
\titlespacing{\section}{0pt}{12pt}{6pt}

\begin{document}
\begin{center}
    {\Huge\bfseries\color{night} {{NAME}}} \\[4pt]
    {\large\itshape\color{gold} {{JOB_TITLE}}} \\[6pt]
    \small \faEnvelope\ \href{mailto:{{EMAIL}}}{{{EMAIL}}} \ | \ \faPhone\ {{PHONE}} \ | \ \faLinkedin\ \href{{{LINKEDIN}}}{LinkedIn}
\end{center}
\section{Overview} {{SUMMARY}}
\section{Career History} {{EXPERIENCE}}
\section{Academic Foundation} {{EDUCATION}}
\section{Core Skills} {{SKILLS}}
\end{document}
""",
}

def get_template_skeleton(template_style):
    """Return the pre-tested base template skeleton for a given style."""
    return TEMPLATES.get(template_style, TEMPLATES['modern_ats_clean'])
