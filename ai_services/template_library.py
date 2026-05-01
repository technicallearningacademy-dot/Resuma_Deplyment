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
    'technical_developer': r"""
\documentclass[10pt,a4paper]{article}
\usepackage[left=1.1cm, right=1.1cm, top=1.1cm, bottom=1.1cm]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[scaled]{helvet}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{marvosym}
\newcommand{\faEnvelope}{\Letter}
\newcommand{\faPhone}{\Telefon}
\newcommand{\faGithub}{GitHub}
\newcommand{\faLinkedin}{LinkedIn}
\newcommand{\faMapMarker}{$\bullet$}
\newcommand{\faLink}{\textrightarrow}
\newcommand{\faGooglePlay}{$\triangleright$}
\newcommand{\faChevronRight}{\textbullet}
\usepackage{pagecolor}
\usepackage{multicol}
\usepackage{array}
\usepackage{tabularx}
\usepackage{tikz}
\usepackage{mdframed}
\usepackage{graphicx}

% ---- COLOR PALETTE ----
\definecolor{bg}{HTML}{FFFFFF}
\definecolor{surface}{HTML}{F3F6FA}
\definecolor{accent}{HTML}{1A56DB}
\definecolor{accentgold}{HTML}{B45309}
\definecolor{textprimary}{HTML}{111827}
\definecolor{textsecondary}{HTML}{6B7280}
\definecolor{headercol}{HTML}{111827}
\definecolor{divider}{HTML}{D1D5DB}
\definecolor{tagbg}{HTML}{EFF6FF}
\definecolor{tagtxt}{HTML}{1D4ED8}
\definecolor{greenbadge}{HTML}{D1FAE5}
\definecolor{greentxt}{HTML}{065F46}

\pagecolor{bg}
\color{textprimary}

\hypersetup{colorlinks=true, urlcolor=accent}

% ---- FONTS ----
\renewcommand{\familydefault}{\sfdefault}

% ---- SECTION STYLE ----
\titleformat{\section}
  {\normalfont\normalsize\bfseries\color{accentgold}\sffamily}
  {}{0em}
  {\MakeUppercase}
  [\vspace{1pt}\color{divider}\rule{\linewidth}{0.5pt}]

\titlespacing{\section}{0pt}{10pt}{5pt}

% ---- HELPERS ----
\newcommand{\skilltag}[1]{%
  \tikz[baseline=(t.base)]{
    \node[fill=tagbg, draw=accent!30, rounded corners=3pt,
          inner xsep=5pt, inner ysep=2.5pt, text=tagtxt, font=\footnotesize\sffamily] (t) {#1};
  }%
}

\newcommand{\jobtitle}[2]{%
  \textbf{\color{headercol}#1} \hfill \textcolor{textsecondary}{\small #2}\\
}

\newcommand{\jobsubtitle}[1]{%
  \textit{\color{accent}\small #1}\\[-2pt]
}

\setlength{\parindent}{0pt}
\pagestyle{empty}
\setlist[itemize]{noitemsep, topsep=2pt, leftmargin=14pt, label={\textcolor{accent}{\tiny\faChevronRight}}}

\begin{document}

% ================================================================
% HEADER
% ================================================================
\begin{tikzpicture}[remember picture, overlay]
  \fill[surface] (current page.north west) rectangle ([yshift=-2.8cm]current page.north east);
\end{tikzpicture}

\vspace{0pt}
% CRITICAL: DO NOT REMOVE THIS IfFileExists GUARD. IT PREVENTS COMPILATION FAILURE IF PHOTO IS MISSING.
\IfFileExists{profile.jpg}{
\begin{minipage}[c]{0.78\textwidth}
  {\color{headercol}\fontsize{26}{30}\selectfont\bfseries\sffamily {{NAME}}}\\[3pt]
  {\color{accent}\large\sffamily {{JOB_TITLE}}} \quad
  {\color{textsecondary}\small\sffamily $\bullet$ \ {{CITY}}, {{COUNTRY}}}\\[6pt]

  \textcolor{textsecondary}{\small
    \faEnvelope\ \href{mailto:{{EMAIL}}}{\color{accent}{{EMAIL}}} \quad
    \faPhone\ \color{textprimary}{{PHONE}} \quad
    \faGithub\ \href{{{GITHUB}}}{\color{accent}GitHub} \quad
    \faLinkedin\ \href{{{LINKEDIN}}}{\color{accent}LinkedIn}
  }
\end{minipage}
\hfill
\begin{minipage}[c]{0.2\textwidth}
\begin{tikzpicture}
\clip (0,0) circle (1.2cm);
\node at (0,0) {\includegraphics[width=2.4cm]{profile.jpg}};
\end{tikzpicture}
\end{minipage}
}{
  {\color{headercol}\fontsize{26}{30}\selectfont\bfseries\sffamily {{NAME}}}\\[3pt]
  {\color{accent}\large\sffamily {{JOB_TITLE}}} \quad
  {\color{textsecondary}\small\sffamily $\bullet$ \ {{CITY}}, {{COUNTRY}}}\\[6pt]

  \textcolor{textsecondary}{\small
    \faEnvelope\ \href{mailto:{{EMAIL}}}{\color{accent}{{EMAIL}}} \quad
    \faPhone\ \color{textprimary}{{PHONE}} \quad
    \faGithub\ \href{{{GITHUB}}}{\color{accent}GitHub} \quad
    \faLinkedin\ \href{{{LINKEDIN}}}{\color{accent}LinkedIn}
  }
}

\vspace{6pt}
\textcolor{accent}{\rule{\linewidth}{1pt}}
\vspace{2pt}

% ================================================================
% SUMMARY
% ================================================================
\section{Professional Summary}
\textcolor{textsecondary}{
{{SUMMARY}}
}

% ================================================================
% SKILLS  (Multi-column tag layout)
% ================================================================
\section{Technical Skills}
\begin{mdframed}[
  backgroundcolor=surface,
  linecolor=divider,
  linewidth=0.5pt,
  innerleftmargin=10pt,
  innerrightmargin=10pt,
  innertopmargin=8pt,
  innerbottommargin=8pt,
  roundcorner=4pt
]
{{SKILLS}}
\end{mdframed}

% ================================================================
% EXPERIENCE
% ================================================================
\section{Professional Experience}
{{EXPERIENCE}}

% ================================================================
% PROJECTS
% ================================================================
\section{Key Projects}
{{PROJECTS}}

% ================================================================
% EDUCATION
% ================================================================
\section{Education}
{{EDUCATION}}

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
    # Removed duplicate technical_developer entry

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
