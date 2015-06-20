# coding: utf-8
"""Gestion des fichiers pdf
"""
import os
import shutil
from deps import HTMLTags as h
from base64 import b64encode
from etc import config as cfg
from deps.outils import url


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
        self.preparer()
        return h.OBJECT(
            data="{}".format(url(self._fichier())),
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

    def _fichier(self, ext='pdf'):
        """Chemin absolu
        """
        return os.path.join(
            cfg.PWD, cfg.STATIC, 'docs', ext,
            self._fichierrelatif(ext)
        )

    def _fichierrelatif(self, ext=None):
        """Chemin vers un fichier portant ce nom avec une autre extension
        """
        return os.path.splitext(self.chemin)[0] \
            + ('.' + ext if ext else '.' + self.ext if self.ext else '')\
            .replace('/', os.path.sep)

    def preparer(self):
        """Copie le pdf dans le dossier static
        """
        if not os.path.isfile(self._fichier()) \
        or os.path.getmtime(self._fichier()) < os.path.getmtime(self.fichier):
            os.makedirs(os.path.dirname(self._fichier()))
            shutil.copy(self.fichier, self._fichier())

    def supprimer(self):
        """Suppression du document
        """
        os.remove(self.fichier)
