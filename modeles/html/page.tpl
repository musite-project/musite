<html>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
%from deps import auth as a
%from deps import outils as o
%from etc import config as cfg
%hote = rq.headers['Host']
    <head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" />
    <link rel="stylesheet" href="/css">
    <title>{{cfg.TITRE}}</title>
    </head>
    <body>

        <div id="logo">
            <a href={{i18n_path('/')}}><img src="/static/img/logo.png" width="150px" alt="Musite"></a>
        </div>
        <div id="entete">
            <h1 id='titre'><a href={{i18n_path('/')}}>{{cfg.TITRE}}</a></h1>
        </div>

        <div id="menu">
            %try:
            %if len(liens) > 0:  # S'il y a des liens à afficher, on en fait la liste.
            <b>{{_("Liens")}}</b><br>
            <ul>
                %for lien in sorted(liens.keys(), key=lambda s: o.sansaccents(s.lower())):
                <li><a href={{i18n_path('/' + liens[lien])}}>{{lien}}</a></li>
                %end
            </ul>
            %end
            %except NameError: pass
            %end

            %try:
            %if len(actions) > 0:  # Même chose pour les actions sur les documents.
            <b>{{_("Actions")}}</b><br>
            <ul>
                %for action in sorted(actions.keys(), key=lambda s: o.sansaccents(s.lower())):
                <li><a href={{i18n_path('/' + actions[action])}}>{{action}}</a></li>
                %end
            </ul>
            %end
            %except NameError: pass
            %end

            <div id="acces">
                <b>{{_("Accès réservé")}}</b><br>
                <ul>
                    %try:
                    %if a.authentifier(rq.auth[0], rq.auth[1]) and rq.auth[0] != 'anonyme':
                    <li>
                        <a href={{'http://anonyme@' + hote + i18n_path('/')}}>
                            {{_("Déconnexion")}}
                        </a>
                    </li>
                    %else:
                    <li>
                        <a href={{'http://{}{}authentification'.format(hote,i18n_path('/'))}}>
                            {{_("S'authentifier")}}
                        </a>
                    </li>
                    %end
                    %except TypeError:
                    <li>
                        <a href={{'http://{}{}authentification'.format(hote,i18n_path('/'))}}>
                            {{_("S'authentifier")}}
                        </a>
                    </li>
                    %end
                    %# Liens réservés aux administrateurs.
                    %try:
                    %if a.admin(rq.auth[0], rq.auth[1]):
                    <li><a href={{i18n_path('/admin')}}>{{_("Administration")}}</a></li>
                    %end
                    %except TypeError: pass
                    %end
                </ul>
            </div>
        </div>

        <div id="corps">
                {{!corps}}
        </div>
    </body>
</html>
