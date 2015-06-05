<div id="zonesaisie">
    <form method="post" enctype="multipart/form-data">
        <p>{{_("Sélectionnez une archive zip contenant ce que vous voulez envoyer :")}}</p>
        <input type="file" name="fichier" />
        <p>Nom du nouveau projet :</p>
        <input name="nom" />
        <br><br>
        <button type="submit" name="action" value="envoi">{{_("Envoyer")}}</button>
        &nbsp
        <button type="submit" name="action" value="annuler">{{_("Annuler")}}</button>
    </form>
</div>
