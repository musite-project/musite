\documentclass[%
<<<proprietes['papier']>>>paper%         Taille de page.
,<<<proprietes['taille_police']>>>pt%    Taille de police.
,DIV=15%                                 Plus grand => des marges plus petites.
]{scrartcl}

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


\def\greinitialformat#1{{%
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
\includescore{<<<partition>>>}
\end{document}
