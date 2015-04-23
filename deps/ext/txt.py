# coding: utf-8
"""Gestion des documents txt

Ce module sert aussi de module de base pour d'autres types de documents : soyez
vigilant si vous y apportez des modifications.
Il n'y a aucune dépendance externe particulière.

Si vous voulez définir un module pour gérer une nouvelle extension, il doit
comporter au moins les méthodes documentées ici. Le cas échéant, vous pouvez
user des mécanismes d'héritage de Python en vous basant sur ce module.
"""
import os.path
import HTMLTags as h
import bottle as b
from etc import config as cfg
import gettext
gettext.install('modules', cfg.I18N)
b.TEMPLATE_PATH += cfg.MODELES
EXT = __name__.split('.')[-1]


class Document:
    """Classe gérant les documents
    """
    def __init__(self, chemin, ext=EXT):
        self.ext = ext
        self.chemin = chemin
        self.nom = os.path.splitext(chemin.split('/')[-1])[0]
        # Chemin relatif du fichier
        self.fichierrelatif = chemin.replace('/', os.path.sep)
        self.dossierrelatif = os.path.dirname(self.fichierrelatif)
        # Chemin absolu du fichier
        self.fichier = os.path.join(
            cfg.DATA,
            self.fichierrelatif
        )
        self.dossier = os.path.dirname(self.fichier)

    def afficher(self):
        """Affichage du contenu du document

        Il doit s'agir ou bien d'un simple texte, ou bien de code html.
        """
        return h.CODE(b.html_escape(self.contenu))

    afficher_source = afficher

    @property
    def contenu(self):
        """Contenu du document
        """
        try:
            with open(self.fichier) as f:
                return f.read(-1)
        except UnicodeDecodeError:
            raise FichierIllisible(self.fichier)

    def editer(self, creation=False):
        """Page d'édition du document

        Ce n'est pas ici qu'il importe de s'occuper de cosmétique : on renvoie
        le strict nécessaire, en html, pour l'édition d'un document.
        """
        try:
            return b.template(
                'editeur',
                emplacement=self.chemin,
                texte=self.contenu,
                ext=self.ext
            )
        except FileNotFoundError:
            if creation:
                return b.template(
                'editeur',
                emplacement=self.chemin,
                texte='',
                ext=self.ext
            )
            else:
                b.abort(404)

    def enregistrer(self, contenu):
        """Enregistrement du document
        """
        with open(self.fichier, 'w') as f:
            f.write(contenu)

    def supprimer(self):
        """Suppression du document
        """
        os.remove(self.fichier)


class FichierIllisible(Exception):
    """Exception renvoyée quand le fichier est illisible

    Ici, cette exception est utile si le fichier est un binaire et non un
    document texte.
    """
    pass
