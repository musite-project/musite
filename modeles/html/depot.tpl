<div id="zonesaisie">
    <form method="post">
        <input
            name="origine"
            %try:
            value="{{origine}}"
            %except NameError: pass
            %end
            label="{{_("Adresse d'origine")}} :"
            placeholder="{{"https://github.com/<auteur>/<projet>"}}"
            required
        >
        <br>
        %if action[0] == 'cloner':
        <input
            name="nom"
            label="{{_("Nom de")}} {{quoi}} :"
            placeholder="{{_("Nom de")}} {{quoi}}"
            required
        >
        <br>
        %elif action[0] == 'emettre':
        <input
            name="utilisateur"
            label="{{_("Nom d'utilisateur")}} :"
            placeholder="{{_('Utilisateur')}}"
            required
        >
        <br>
        <input
            name="mdp"
            label="{{_("Mot de passe")}} :"
            placeholder="{{_("MdP")}}"
            type="password"
            required
        >
        <br>
        %end
        <button
            type="submit"
            name="action"
            value="{{action[0]}}"
        >{{action[1]}}
        </button>
        &nbsp
        <button type="submit" name="action" value="annuler">{{_("Annuler")}}</button>
    </form>
</div>
