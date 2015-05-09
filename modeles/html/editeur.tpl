%from etc import config as cfg
%if ext in ['gabc']:
<script language="javascript" type="text/javascript" src="/static/js/edit_area/edit_area_full.js"></script>
<script language="javascript" type="text/javascript">
    editAreaLoader.init({
        id : "saisie"
        ,language: "{{cfg.LANGUE}}"
        ,syntax: "{{ext}}"
        ,show_line_colors: true
        ,start_highlight: true
        ,word_wrap: true
    });
</script>
%end
<div id="zonesaisie">
    <form method="post" action="{{i18n_path('/' + emplacement)}}">
        <!--
        <input name="titre" label="titre" placeholder="{{_("titre")}}">
        <br>
        -->
        <textarea name="contenu" id="saisie" placeholder="{{_("Texte")}}">{{texte}}</textarea>
        <br>
        <button type="submit" name="action" value="enregistrer">{{_("Enregistrer")}}</button>
        &nbsp
        <button type="submit" name="action" value="annuler">{{_("Annuler")}}</button>
    </form>
</div>
