\usepackage{<<<proprietes['police_famille']>>>}
\usepackage{xcolor}
\usepackage{geometry}
\geometry{%
    papersize={<<<proprietes['ba_papier']>>>},%
    left=<<<proprietes['marge'][2]>>>,%
    right=<<<proprietes['marge'][3]>>>,%
    top=<<<proprietes['marge'][0]>>>,%
    bottom=<<<proprietes['marge'][1]>>>%
}
<<<'\pagestyle{empty}' if not proprietes['page_numero'] else ''>>>
