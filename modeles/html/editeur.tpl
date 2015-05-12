%from etc import config as cfg
%if ext in ['gabc']:
<script language="javascript" type="text/javascript" src="/static/js/edit_area/edit_area_full.js"></script>
<script language="javascript" type="text/javascript">
    editAreaLoader.init({
        id : "t_saisie"
        ,language: "{{cfg.LANGUE}}"
        ,syntax: "{{ext}}"
        ,show_line_colors: true
        ,start_highlight: true
        ,word_wrap: false
    });
</script>
%end

<div id="zonesaisie">
    <form method="post" action="{{i18n_path('/' + emplacement)}}">
        <!--
        <input name="titre" label="titre" placeholder="{{_("titre")}}">
        <br>
        -->
        %if ext != 'gabc':
        <div name="contenu" id="saisie">{{texte}}</div>
        %end
        <textarea type="hidden" name="contenu" id="t_saisie" placeholder="{{_("Texte")}}">{{texte}}</textarea>
        <div id="boutons_editeur">
                <button type="submit" name="action" id="enregistrer" value="enregistrer">{{_("Enregistrer")}}</button>
                &nbsp
                <button type="submit" name="action" value="annuler">{{_("Annuler")}}</button>
        </div>
    </form>
</div>

%if ext != 'gabc':
<script src="/static/js/jquery.min.js" type="text/javascript" charset="utf-8"></script>
<script src="/static/js/ace/ace.js" type="text/javascript" charset="utf-8"></script>
%if ext in ['tex', 'sty']:
<script src="/static/js/ace/mode-tex.js" type="text/javascript" charset="utf-8"></script>
%elif ext in ['md']:
<script src="/static/js/ace/mode-markdown.js" type="text/javascript" charset="utf-8"></script>
%else:
<script src="/static/js/ace/mode-text.js" type="text/javascript" charset="utf-8"></script>
%end
<script>
        var editor = ace.edit("saisie");
        %if ext in ['tex', 'sty']:
        var Mode = ace.require("ace/mode/tex").Mode;
        %elif ext in ['md']:
        var Mode = ace.require("ace/mode/markdown").Mode;
        %else:
        var Mode = ace.require("ace/mode/text").Mode;
        %end
        editor.setTheme("ace/theme/textmate");
        editor.getSession().setMode(new Mode());
        var textarea = $('textarea[name="contenu"]').hide();
        editor.getSession().on('change', function(){
                textarea.val(editor.getSession().getValue());
        });
</script>
%end
