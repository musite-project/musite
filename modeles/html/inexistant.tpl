<div id="zonesaisie">
    {{_("Il n'y a rien à cet emplacement. Si vous le désirez, vous pouvez :")}}
    <form method="post">
        %if element is None:
        <button type="submit" name="action" value="projet">{{_("Créer un projet")}}</button>
        &nbsp
        %else:
        <button type="submit" name="action" value="dossier">{{_("Créer un dossier")}}</button>
        &nbsp
        <button type="submit" name="action" value="document">{{_("Créer un document")}}</button>
        &nbsp
        %end
        <button type="submit" name="action" value="annuler">{{_("Annuler")}}</button>
    </form>
</div>
