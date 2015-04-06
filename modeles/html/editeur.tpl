<script language="javascript" type="text/javascript" src="/static/js/edit_area/edit_area_full.js"></script>
<script language="javascript" type="text/javascript">
    editAreaLoader.init({
        id : "saisie"
        ,language: "fr"
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
        <input name="titre" label="titre" placeholder="titre">
        <input name="mode" label="mode" placeholder="mode">
        <input name="type" label="type" placeholder="type">
        <br>
        -->
        <textarea name="contenu" id="saisie" placeholder="Texte">{{texte}}</textarea>
        <br>
        <button type="submit" name="action" value="enregistrer">Enregistrer</button>
    </form>
</div>
