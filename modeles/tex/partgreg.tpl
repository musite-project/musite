\documentclass[%
,<<<proprietes['texte_taille']>>>pt%    Taille de police.
]{scrartcl}

\usepackage[%
    paperwidth=<<<proprietes['ba_papier'][0]>>>,
    paperheight=<<<proprietes['ba_papier'][1]>>>,
    left=<<<proprietes['marge_gauche']>>>,
    right=<<<proprietes['marge_droite']>>>,
    top=<<<proprietes['marge_haut']>>>,
    bottom=<<<proprietes['marge_bas']>>>,
]{geometry}
\usepackage[autocompile]{gregoriotex}
\usepackage{libertine}
\usepackage{xcolor}

\pagestyle{empty}

\setgrefactor{<<<proprietes['notes_taille']>>>}
\setstafflinethickness{<<<proprietes['notes_epaisseur_lignes']>>>}
\grechangedim{spacelinestext}{<<<proprietes['notes_espace_lignes_texte']>>>}{0}
\setaboveinitialseparation{<<<proprietes['annotations_espace']>>>}{0}


\definecolor{gregoriocolor}{rgb}{%
    <<<','.join(str(p / 255) for p in proprietes['couleur'])>>>%
}
\def\rubrum{\color{gregoriocolor}}
%if proprietes['initiale_couleur']:
\let\rubrinit\rubrum
%else:
\def\rubrinit{}
%end
%if proprietes['notes_couleur_lignes']:
\grecoloredlines{<<<'}{'.join(str(int(c)) for c in proprietes['couleur'])>>>}
%end
%if proprietes['texte_symboles_couleur']:
\let\rubrsym\rubrum
%else:
\def\rubrsym{}
%end


\def\greinitialformat#1{\raisebox{<<<proprietes['initiale_elevation']>>>}{%
    \fontsize{%
        <<<proprietes['initiale_taille']>>>%
    }{%
        <<<proprietes['initiale_taille']>>>}\selectfont{}%
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

%if proprietes['aa_titre'] != '':
{\centering\LARGE <<<proprietes['aa_titre']>>>\par
\bigskip}
%end

\setfirstannotation{%
    \raisebox{<<<proprietes['annotations_elevation']>>>}[1.2\height][1ex]{%
    \footnotesize <<<proprietes['ab_type']>>>%
    }%
}
\setsecondannotation{%
    \raisebox{<<<proprietes['annotations_elevation']>>>}[1.2\height][1ex]{%
    \footnotesize <<<proprietes['ab_mode']>>>%
    }%
}
\includescore{<<<partition>>>}

\end{document}
