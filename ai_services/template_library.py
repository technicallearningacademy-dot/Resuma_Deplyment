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
}

def get_template_skeleton(template_style):
    """Return the pre-tested base template skeleton for a given style."""
    return TEMPLATES.get(template_style, TEMPLATES['modern_ats_clean'])
