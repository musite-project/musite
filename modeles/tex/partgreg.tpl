\documentclass[%
,<<<proprietes['texte_taille']>>>pt%    Taille de police.
]{scrartcl}

\usepackage[%
    paperwidth=<<<proprietes['ba_papier'][0]>>>,
    paperheight=<<<proprietes['ba_papier'][1]>>>,
    left=<<<proprietes['marge'][2]>>>,
    right=<<<proprietes['marge'][3]>>>,
    top=<<<proprietes['marge'][0]>>>,
    bottom=<<<proprietes['marge'][1]>>>,
]{geometry}
\usepackage[autocompile]{gregoriotex}
\usepackage{libertine}
\usepackage[%
    activate={true,nocompatibility}%
    ,final%
    ,tracking=true%
    ,factor=1100%
    ,stretch=50%
    ,shrink=30%
    ]{microtype}
\usepackage{xcolor}

\pagestyle{empty}

\grechangestaffsize{<<<proprietes['notes_taille']>>>}
\grechangestafflinethickness{<<<proprietes['notes_epaisseur_lignes']>>>}
\grechangedim{spacelinestext}{<<<proprietes['notes_espace_lignes_texte']>>>}{0}
\grechangedim{annotationseparation}{<<<proprietes['annotations_espace']>>>}{0}
\grechangedim{annotationraise}{<<<proprietes['annotations_elevation']>>>}{0}
\grechangedim{beforeinitialshift}{<<<proprietes['initiale_espace'][0]>>>}{0}
\grechangedim{afterinitialshift}{<<<proprietes['initiale_espace'][1]>>>}{0}


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
\gresetlinecolor{gregoriocolor}
%end
%if proprietes['texte_symboles_couleur']:
\let\rubrsym\rubrum
%else:
\def\rubrsym{}
%end
%if proprietes['annotations_couleur']:
\let\rubrannot\rubrum
%else:
\def\rubrannot{}
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
        {\rubrsym \Rbar#1}
}
\catcode`\†=\active \def †{%
    {\rubrsym \GreDagger}%
}
\catcode`\✠=\active \def ✠{%
    {\rubrsym \grecross}%
}
\let\oldGreStar\GreStar
\renewcommand{\GreStar}{%
    {\rubrsym \oldGreStar}%
}
\renewcommand{\greheightstar}{%
    {\GreStar}%
}


\begin{document}

%if proprietes['aa_titre'] != '':
{\centering\LARGE <<<proprietes['aa_titre']>>>\par
\bigskip}
%end

%if proprietes['ab_type']:
\greannotation{%
    {\rubrannot\footnotesize <<<proprietes['ab_type']>>>}%
}
%end
%if proprietes['ab_mode']:
\greannotation{%
    {\rubrannot\footnotesize <<<proprietes['ab_mode']>>>}%
}
%end
\gregorioscore{<<<partition>>>}

\end{document}
