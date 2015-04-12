\documentclass[%
a5paper%                       Taille de page.
,12pt%                         Taille de police.
,DIV=15%                       Plus grand => des marges plus petites.
]{scrartcl}

\usepackage[autocompile]{gregoriotex}
\usepackage{libertine}
\usepackage{xcolor}

\definecolor{rubrum}{rgb}{.6,0,0}
\def\rubrum{\color{rubrum}}

\def\greinitialformat#1{\\
%
{\fontsize{43}{43}\selectfont #1}\\
%
}

\let\Vbar\Vbarsmall
\let\Rbar\Rbarsmall
\catcode`\℣=\active \def ℣#1{%
	{\rubrum \Vbar\hspace{-.25ex}#1}
}
\catcode`\℟=\active \def ℟#1{%
	{\rubrum \Rbar\hspace{-.25ex}#1}
}
\catcode`\†=\active \def †{%
    {\rubrum\gredagger}%
}
\catcode`\✠=\active \def ✠{%
    {\rubrum\grecross}%
}
\renewcommand{\grestar}{%
    {\rubrum\gresixstar}%
}
\renewcommand{\greheightstar}{\grestar}

\setstafflinethickness{20}
\grecoloredlines{154}{0}{0}


\begin{document}
\includescore{\\
%
{{partition}}\\
%
}
\end{document}
