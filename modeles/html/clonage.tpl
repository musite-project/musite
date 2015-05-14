<div id="zonesaisie">
    <form method="post">
        <input name="origine" label="{{_("Adresse d'origine")}} :" placeholder="{{_("https://github.com/<auteur>/<projet>")}}" required>
        <br>
        <input name="nom" label="{{_("Nom de")}} {{quoi}} :" placeholder="{{_("Nom de")}} {{quoi}}" required>
        <br>
        <button type="submit" name="action" value="cloner">{{_("Cloner")}} {{quoi}}</button>
        &nbsp
        <button type="submit" name="action" value="annuler">{{_("Annuler")}}</button>
    </form>
</div>
