<div id="zonesaisie">
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="fichier" />
        <br>
        <input name="ecraser" value="0" type="hidden">
        <input
            type="checkbox"
            name="ecraser"
            value="1"
        > {{_("Écraser le fichier s'il existe.")}}
        <br>
        <button type="submit" name="action" value="envoi">{{_("Envoyer")}}</button>
        &nbsp
        <button type="submit" name="action" value="annuler">{{_("Annuler")}}</button>
    </form>
</div>
