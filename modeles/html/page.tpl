<html>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
%import re
%from deps import auth as a
%from deps import outils as o
%from etc import config as cfg
%hote = rq.headers['Host']
%prefixe = rq.url.split(':')[0]
%if cfg.DEVEL: print('\n', dict(rq), '\n'); end
    <head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" />
    <link rel="stylesheet" href="/css">
    <title>{{cfg.TITRE + rq['PATH_INFO']}}</title>
    %try:
    %if midi:
    <script src="/static/js/midi/midi.min.js"></script>
    <script type="text/javascript">
    var mp;
    function init() {
        mp = new MidiPlayer("{{i18n_path(midi)}}", 'btnmidi');
    }
    function doPlay(m, btnmidi) {
        if (btnmidi.value == '▶') {
            m.play();
            btnmidi.value = '■';
        }
        else {
            m.stop();
            btnmidi.value = '▶';
        }
    }
    </script>
    %end
    %except NameError: pass
    %end
    </head>
    %try:
    %if midi:
    <body onload="javascript:init();">
    %else:
    <body>
    %end
    %except NameError:
    <body>
    %end
        <div id="logo">
            <a href={{i18n_path('/')}}><img src="/static/img/logo.png" width="150px" alt="Musite"></a>
        </div>
        <div id="entete">
            <h1 id='titre'><a href={{i18n_path('/')}}>{{cfg.TITRE}}</a></h1>
        </div>
        <div id="langues">
            %for langue in sorted(langue[0] for langue in languages):
            <a href="{{str(i18n_path()).replace(str(i18n_path('/')), '/{}/'.format(langue))}}">{{langue}}</a>&nbsp;
            %end
        </div>

        <div id="menu">
            %try:
            %if midi:
            <object data="{{prefixe + '://' + hote + i18n_path(midi)}}" type="audio/x-midi" width="50px" height="25px">
            <input type="button" value="▶" id='btnmidi' onclick="doPlay(mp, this);"/>
            </object>
            <br><br>
            %end
            %except NameError: pass
            %end

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

            %try:
            %if len(exports) > 0:  # Même chose pour les actions sur les documents.
            <b>{{_("Export")}}</b><br>
            <ul>
                %for export in sorted(exports.keys(), key=lambda s: o.sansaccents(s.lower())):
                <li><a href={{i18n_path('/_exporter/' + exports[export])}}>{{export}}</a></li>
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
                        <a href={{prefixe + '://anonyme@' + hote + i18n_path()}}>
                            {{_("Déconnexion")}}
                        </a>
                    </li>
                    %else:
                    <li>
                        <a href={{prefixe + '://' + hote + i18n_path('/authentification')}}>
                            {{_("S'authentifier")}}
                        </a>
                    </li>
                    %end
                    %except TypeError:
                    <li>
                        <a href={{prefixe + '://' + hote + i18n_path('/authentification')}}>
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
