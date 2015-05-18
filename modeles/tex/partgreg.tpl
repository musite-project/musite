\documentclass[%
,<<<proprietes['taille_police']>>>pt%    Taille de police.
]{scrartcl}

\usepackage[%
    paperwidth=<<<proprietes['papier'][0]>>>,
    paperheight=<<<proprietes['papier'][1]>>>,
    left=<<<proprietes['marge_gauche']>>>,
    right=<<<proprietes['marge_droite']>>>,
    top=<<<proprietes['marge_haut']>>>,
    bottom=<<<proprietes['marge_bas']>>>,
]{geometry}
\usepackage[autocompile]{gregoriotex}
\usepackage{libertine}
\usepackage{xcolor}

\pagestyle{empty}

\setgrefactor{<<<proprietes['taille_notes']>>>}
\setstafflinethickness{<<<proprietes['epaisseur_lignes']>>>}
\grechangedim{spacelinestext}{<<<proprietes['espace_lignes_texte']>>>}{0}

\definecolor{gregoriocolor}{rgb}{%
    <<<','.join(str(p / 255) for p in proprietes['couleur'])>>>%
}
\def\rubrum{\color{gregoriocolor}}
%if proprietes['couleur_initiale']:
\let\rubrinit\rubrum
%else:
\def\rubrinit{}
%end
%if proprietes['couleur_lignes']:
\grecoloredlines{<<<'}{'.join(str(int(c)) for c in proprietes['couleur'])>>>}
%end
%if proprietes['couleur_symboles']:
\let\rubrsym\rubrum
%else:
\def\rubrsym{}
%end


\def\greinitialformat#1{\raisebox{<<<proprietes['elevation_initiale']>>>}{%
    \fontsize{%
        <<<proprietes['taille_initiale']>>>%
    }{%
        <<<proprietes['taille_initiale']>>>}\selectfont{}%
    \rubrinit #1%
}}

\catcode`\℣=\active \def ℣#1{%
        {\rubrsym \Vbar\hspace{-.25ex}#1}
}
\catcode`\℟=\active \def ℟#1{%
        {\rubrsym \Rbar\hspace{-.25ex}#1}
}
\catcode`\†=\active \def †{%
    {\rubrsym \gredagger}%
}
\catcode`\✠=\active \def ✠{%
    {\rubrsym \grecross}%
}
\renewcommand{\grestar}{%
    {\rubrsym \gresixstar}%
}
\renewcommand{\greheightstar}{\grestar}


\begin{document}

%if proprietes['titre'] != '':
{\centering\LARGE <<<proprietes['titre']>>>\par
\bigskip}
%end

\includescore{<<<partition>>>}

\end{document}
