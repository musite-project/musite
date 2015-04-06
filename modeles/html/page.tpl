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
            %liens
            <b>Liens</b><br>
            <ul>
                %for lien in sorted(liens.keys()):
                <li><a href=/{{liens[lien]}}>{{lien}}</a></li>
                %end
            </ul>
            %except NameError: pass
            %end
            %try:
            %actions
            <b>Actions</b><br>
            <ul>
                %for action in sorted(actions.keys()):
                <li><a href=/{{actions[action]}}>{{action}}</a></li>
                %end
            </ul>
            %except NameError: pass
            %end
        </div>
        <div id="corps">
                {{!corps}}
        </div>
    </body>
</html>
