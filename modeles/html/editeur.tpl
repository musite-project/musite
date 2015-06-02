%from etc import config as cfg
%from deps.outils import i18n_path, _
<script type="text/javascript">
    window.onbeforeunload = function(){
        return "Attention : si vous quittez cette page, vos modifications seront perdues.";
};
    function avant_enregistrement(){
        window.onbeforeunload = null;
};
</script>

<div id="zonesaisie">
    <form method="post" action="{{i18n_path('/' + emplacement)}}">
        <div name="contenu" id="saisie">{{texte}}</div>
        <textarea type="hidden" name="contenu" id="t_saisie" placeholder="{{_("Texte")}}">{{texte}}</textarea>
        <div id="boutons_editeur">
                <button type="submit" name="action" id="enregistrer" value="enregistrer" onClick="avant_enregistrement();">{{_("Enregistrer")}}</button>
                &nbsp
                <button type="submit" name="action" value="annuler">{{_("Annuler")}}</button>
        </div>
    </form>
</div>

<script src="/static/js/jquery/jquery.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/ace/ace.js" type="text/javascript" charset="utf-8"></script>
%if ext in ['tex', 'sty']:
<script src="/static/js/ace/mode-tex.js" type="text/javascript" charset="utf-8"></script>
%elif ext in ['gabc']:
<script src="/static/js/ace/mode-gabc.js" type="text/javascript" charset="utf-8"></script>
%elif ext in ['md']:
<script src="/static/js/ace/mode-markdown.js" type="text/javascript" charset="utf-8"></script>
%else:
<script src="/static/js/ace/mode-text.js" type="text/javascript" charset="utf-8"></script>
%end
<script>
        var editor = ace.edit("saisie");
        %if ext in ['tex', 'sty']:
        var Mode = ace.require("ace/mode/tex").Mode;
        %elif ext in ['gabc']:
        var Mode = ace.require("ace/mode/gabc").Mode;
        %elif ext in ['md']:
        var Mode = ace.require("ace/mode/markdown").Mode;
        %else:
        var Mode = ace.require("ace/mode/text").Mode;
        %end
        editor.setOptions({wrap: true, fontSize: "96%"});
        editor.setTheme("ace/theme/textmate");
        editor.getSession().setMode(new Mode());
        var textarea = $('textarea[name="contenu"]').hide();
        editor.getSession().on('change', function(){
                textarea.val(editor.getSession().getValue());
        });
</script>

