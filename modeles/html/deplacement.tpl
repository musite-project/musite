<div id="zonesaisie">
    <form method="post">
        <input name="destination" label="{{deplacement}} :" placeholder="{{deplacement}}" value="{{destination}}">
        <br>
        %if action == _("Déplacer"):
        <input name="ecraser" value="0" type="hidden">
        <input
            type="checkbox"
            name="ecraser"
            value="1"
        > {{_("Ne pas vérifier s'il y a déjà quelque chose à cet emplacement.")}}
        <br>
        %end
        <button type="submit" name="action" value="deplacer">{{action}}</button>
        &nbsp
        <button type="submit" name="action" value="annuler">{{_("Annuler")}}</button>
    </form>
</div>
