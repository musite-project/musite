# coding: utf-8
"""Gestion des messages, afin de permettre une traduction facile."""


class FR:
    """Messages en français"""

    # Messages susceptibles de servir en plusieurs circonstances
    acr = "Accès réservé"
    Adm = "Administration"
    admin = "Vous devez être administrateur"
    ann = "annuler"
    Ann = "Annuler"
    auteur = "auteur"
    auth = "S'authentifier"
    cf = "Oui, je suis sûr"
    Cr = "Créer"
    crdoc = "Créer document"
    crdss = "Créer dossier"
    crprj = "Créer projet"
    date = "date"
    Dc = "Déconnexion"
    dfch = "du fichier "
    dss = "dossier"
    Dss = "Dossier"
    edit = "Éditer"
    edt = "Réservé aux éditeurs"
    enrg = "enregistrer"
    Enrg = "Enregistrer"
    errs = "Erreurs"
    fch = "fichier"
    Grps = "Groupes"
    hist = "Historique"
    lfch = "le fichier "
    ldss = "le dossier "
    lprj = "le projet "
    md = "mode"
    mdf = "modifier"
    mdp = "mot de passe"
    msg = "message"
    nm = "nom"
    Nm = "Nom"
    prj = "projet"
    Prj = "Projet"
    prjs = "projets"
    Prjs = "Projets"
    prt = "Parent"
    rf = "Non, je me suis trompé"
    src = "Source"
    srt = "Sortie"
    suppr = "supprimer"
    Suppr = "Supprimer"
    tp = "type"
    tt = "titre"
    Txt = "Texte"
    usr = "utilisateur"
    usrs = "utilisateurs"
    Usr = "Utilisateur"
    Usrs = "Utilisateurs"
    voir = "Aperçu"

    # Messages appelés directement par le serveur
    a = "Il n'y a rien avant la création !"
    b = "Il n'y a pas encore de modifications à signaler."
    c = "Extension inconnue : "
    d = "Ce fichier est illisible."
    e = "Voici les données de la requète :"
    f = "Suppression du document "
    g = "Document supprimé !"
    h = "Ce type de document n'est pas éditable."
    i = """Si je ne puis même pas lire ce fichier,
        comment voulez-vous que je l'édite ?"""
    j = "Suppression du dossier "
    k = "Dossier supprimé !"
    l = "Projet supprimé !"
    m = "C'est drôle, ce que vous me demandez : il n'y a pas de projet ici !"
    n = " et tout son contenu ?"
    o = "Attention : cette opération est irréversible !"
    p = "Pourriez-vous expliciter votre intention ?"
    q = "Il n'y a rien ici !"

    # Messages des modules de traitement des divers types de fichiers
    r = """Il y a eu une erreur pendant le traitement du document. Ceci vient
        probablement d'une erreur de syntaxe ; si vous êtes absolument certain
        du contraire, merci de signaler le problème."""
    s = "Voici la sortie de la commande :"
    t = "Retour {}à la version "
    u = "Sauvegarde complète"
    v = " n'est pas un dossier"
    w = "Clonage"
    x = "Déplacement"
    y = "Effacement"
    z = "Êtes-vous sûr de vouloir supprimer"

    # Textes des modèles
    aa = "Nom de"
    ab = "Créer le"
    ac = """
        <p>
        Les <em class='suppr'><del>suppressions</del></em> sont en italique,
        les <strong class='add'>additions</strong> en gras.
        Seules sont affichées les parties concernées par les changements.
        <br>
        Les <em class='suppr'>[- -]</em>
        et les <strong class='add'>{+ +}</strong>
        ne font pas partie de la suppression ou de l'addition, mais servent à
        les mettre davantage en évidence.
        </p>

        <h2>Changements apportés par la modification {{commit}} :</h2>
    """
    ad = "<h2>Changements effectués depuis cette modification :</h2>"
    ae = "Revenir à cette version"
    af = "Ajout ou modification d'un utilisateur :"
    ag = "(de nouveau)"


msg = {
    'fr': FR
}
