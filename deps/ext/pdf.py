# coding: utf-8
"""Gestion des fichiers pdf
"""
import os
from deps import HTMLTags as h
from base64 import b64encode
from etc import config as cfg


class Document:
    """Document pdf
    """
    def __init__(self, chemin, ext='pdf'):
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
        """Contenu du pdf embarqué dans un code html
        """
        return h.OBJECT(
            data="data:application/pdf;base64,{}".format(self.contenu),
            Type="application/pdf",
            width="100%",
            height="100%"
            )

    @property
    def contenu(self):
        """Contenu du pdf en base 64
        """
        with open(self.fichier, "rb") as doc:
            return b64encode(doc.read()).decode('ascii')

    def supprimer(self):
        """Suppression du document
        """
        os.remove(self.fichier)
