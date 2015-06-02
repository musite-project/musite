<div id="zonesaisie">
    <p>{{_("Sélectionnez une archive zip contenant ce que vous voulez envoyer :")}}</p>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="fichier" />
        &nbsp
        <button type="submit" name="action" value="envoi">{{_("Envoyer")}}</button>
        &nbsp
        <button type="submit" name="action" value="annuler">{{_("Annuler")}}</button>
    </form>
</div>
