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
\let\Vbar\Vbarsmall
\let\Rbar\Rbarsmall
\catcode`\℣=\active \def ℣#1{%
	{\rubrum \Vbar\hspace{-.4ex}#1}
}
\catcode`\℟=\active \def ℟#1{%
	{\rubrum \Rbar\hspace{-.4ex}#1}
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


\begin{document}
\includescore{\\
%
{{partition}}\\
%
}
\end{document}
