\documentclass[%
,<<<proprietes['texte_police_taille']>>>pt%    Taille de police.
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
\usepackage{fontspec}
\setmainfont{<<<proprietes['texte_police_famille']>>>}
%if proprietes['texte_police_famille'] != 'EB Garamond':
\usepackage[%
    activate={true,nocompatibility}%
    ,final
    ,factor=1100%
    ,stretch=50%
    ,shrink=30%
    ]{microtype}
%end
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

\grechangestyle{initial}{%
    \fontspec{<<<proprietes['initiale_police']>>>}%
    \fontsize{<<<proprietes['initiale_taille']>>>}{<<<proprietes['initiale_taille']>>>}\selectfont%
    \rubrinit
}
\grechangedim{initialraise}{<<<proprietes['initiale_elevation']>>>}{0}

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

\newcommand{\aci}{\bfseries}
\newcommand{\pri}{\itshape}


\begin{document}

%if proprietes['aa_titre'] != '':
{\centering\LARGE%
    %if proprietes['aa_titre_sc']:
    \sc%
    %end
    <<<proprietes['aa_titre']>>>%
    \par
\bigskip}
%end

%if proprietes['ab_type']:
\greannotation{%
    {\rubrannot\footnotesize%
    %if proprietes['ab_type_sc']:
    \textsc{%
    %end
    <<<proprietes['ab_type']>>>}%
    %if proprietes['ab_type_sc']:
    }%
    %end
}
%end
%if proprietes['ab_mode']:
\greannotation{%
    {\rubrannot\footnotesize%
    %if proprietes['ab_mode_sc']:
    \textsc{%
    %end
    <<<proprietes['ab_mode']>>>}%
    %if proprietes['ab_mode_sc']:
    }%
    %end
}
%end
%if proprietes['ac_commentaire']:
\grecommentary{%
    %if proprietes['ac_commentaire_sc']:
    \textsc{%
    %end
    <<<proprietes['ac_commentaire']>>>}%
    %if proprietes['ac_commentaire_sc']:
    }%
    %end
%end
\gregorioscore{<<<partition>>>}

\end{document}
