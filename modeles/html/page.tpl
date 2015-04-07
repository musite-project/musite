%from deps import auth as a
%hote = rq.headers['Host']
<html>
    <head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" />
    <link rel="stylesheet" href="/css">
    <title>Musite</title>
    </head>
    <body>

        <div id="logo">
            <a href="/"><img src="/static/img/logo.png" width="150px" alt="Musite"></a>
        </div>
        <div id="entete">
            <h1 id='titre'><a href="/">Musite</a></h1>
        </div>

        <div id="menu">
            %try:
            %liens  # S'il y a des liens à afficher, on en fait la liste.
            <b>Liens</b><br>
            <ul>
                %for lien in sorted(liens.keys()):
                <li><a href=/{{liens[lien]}}>{{lien}}</a></li>
                %end
            </ul>
            %except NameError: pass
            %end

            %try:
            %actions  # Même chose pour les actions sur les documents.
            <b>Actions</b><br>
            <ul>
                %for action in sorted(actions.keys()):
                <li><a href=/{{actions[action]}}>{{action}}</a></li>
                %end
            </ul>
            %except NameError: pass
            %end

            <div id="acces">
                <b>Accès réservé</b><br>
                <ul>
                    <li><a href=http://log:log@{{hote}}/authentification>S'authentifier</a></li>
                    %# Liens réservés aux administrateurs.
                    %try:
                    %if a.admin(rq.auth[0], rq.auth[1]):
                    <li><a href=/admin>Administration</a></li>
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
