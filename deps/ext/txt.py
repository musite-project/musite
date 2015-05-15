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
from deps import HTMLTags as h
from deps import bottle as b
from deps.outils import motaleatoire
from etc import config as cfg
b.TEMPLATE_PATH += cfg.MODELES
EXT = __name__.split('.')[-1]


class Document:
    """Classe gérant les documents
    """
    def __init__(self, chemin):
        self.chemin = chemin
        self.nom, self.ext = os.path.splitext(chemin.split('/')[-1])
        self.ext = self.ext[1:]
        # Chemin absolu des fichiers temporaires
        self.rnd = os.path.join(cfg.TMP, motaleatoire(6))

    def _chemin(self, ext=None):
        """Url vers un fichier portant ce nom avec une autre extension
        """
        return os.path.splitext(self.chemin)[0] \
            + ('.' + ext if ext else '.' + self.ext if self.ext else '')

    def _fichierrelatif(self, ext=None):
        """Chemin vers un fichier portant ce nom avec une autre extension
        """
        return self._chemin(ext if ext else self.ext).replace('/', os.path.sep)

    def _fichier(self, ext=None):
        """Chemin absolu
        """
        if ext:
            return os.path.join(
                cfg.PWD, cfg.STATIC, ext,
                self._fichierrelatif(ext)
            )
        else:
            return os.path.join(cfg.DATA, self._fichierrelatif())

    def _fichiertmp(self, ext=None):
        """Fichier temporaire
        """
        return os.path.join(
            self.rnd,
            self._fichierrelatif(
                ext if ext else self.ext
            )
        )

    @property
    def dossier(self):
        return os.path.dirname(self._fichier())

    @property
    def dossiertmp(self):
        return os.path.dirname(self._fichiertmp())

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
            with open(self._fichier()) as doc:
                return doc.read(-1)
        except UnicodeDecodeError:
            raise FichierIllisible(fichier)

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
        with open(self._fichier(), 'w') as doc:
            doc.write(contenu)

    def supprimer(self):
        """Suppression du document
        """
        os.remove(self._fichier())


class FichierIllisible(Exception):
    """Exception renvoyée quand le fichier est illisible

    Ici, cette exception est utile si le fichier est un binaire et non un
    document texte.
    """
    pass
