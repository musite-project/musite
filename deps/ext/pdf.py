# coding: utf-8
"""Gestion des fichiers pdf
"""
import os
import shutil
from pathlib import Path
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
        self.fichierrelatif = Path(chemin)
        self.dossierrelatif = self.fichierrelatif.parent
        # Chemin absolu du fichier
        self.fichier = cfg.DATA / self.fichierrelatif
        self.dossier = self.fichier.parent

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
        with self.fichier.open("rb") as doc:
            return b64encode(doc.read()).decode('ascii')

    def _fichier(self, ext='pdf'):
        """Chemin absolu
        """
        return cfg.STATIC / 'docs' / ext / self._fichierrelatif(ext)

    def _fichierrelatif(self, ext=None):
        """Chemin vers un fichier portant ce nom avec une autre extension
        """
        return Path(self.chemin).with_suffix(
            '.' + ext if ext else '.' + self.ext if self.ext else ''
        )

    def preparer(self):
        """Copie le pdf dans le dossier static
        """
        if not self._fichier().is_file() \
        or self._fichier().stat().st_mtime < self.fichier.stat().st_mtime:
            os.makedirs(str(self._fichier().parent))
            shutil.copy(str(self.fichier), str(self._fichier()))

    def supprimer(self):
        """Suppression du document
        """
        self.fichier.unlink()
