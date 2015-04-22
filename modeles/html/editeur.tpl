%from outils import msg
%from etc import config as cfg
<script language="javascript" type="text/javascript" src="/static/js/edit_area/edit_area_full.js"></script>
<script language="javascript" type="text/javascript">
    editAreaLoader.init({
        id : "saisie"
        ,language: "{{cfg.LNG}}"
        %if ext in ['gabc']:
        ,syntax: "{{ext}}"
        ,show_line_colors: true
        ,start_highlight: true
        %end
        ,word_wrap: true
    });
</script>
<div id="zonesaisie">
    <form method="post" action="/{{emplacement}}">
        <!--
        <input name="titre" label="{{msg.tt}}" placeholder="{{msg.tt}}">
        <input name="mode" label="{{msg.md}}" placeholder="{{msg.md}}">
        <input name="type" label="{{msg.tp}}" placeholder="{{msg.tp}}">
        <br>
        -->
        <textarea name="contenu" id="saisie" placeholder="{{msg.Txt}}">{{texte}}</textarea>
        <br>
        <button type="submit" name="action" value="enregistrer">{{msg.Enrg}}</button>
        &nbsp
        <button type="submit" name="action" value="annuler">{{msg.Ann}}</button>
    </form>
</div>
