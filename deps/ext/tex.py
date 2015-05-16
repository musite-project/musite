# coding: utf-8
"""Gestion des documents tex

Ces documents nécessitent TeXLive (ou équivalent) avec un ensemble raisonnable
d'extensions.

Pour la documentation, google est votre ami…
Les pages de M. Pégourié-Gonnard peuvent être de quelque utilité pour un bon
point de départ :
https://elzevir.fr/imj/latex/
"""
from . import txt as txt
from etc import config as cfg
import os
import shutil
import re
EXT = __name__.split('.')[-1]  # pylint: disable=R0801


class Document(txt.Document):
    """Document tex
    """
    def __init__(self, chemin):
        txt.Document.__init__(self, chemin)

    def afficher(self):
        def documentmaitre():
            """Test pour savoir s'il s'agit d'un document maître
            """
            entete = re.compile('\\\\documentclass')
            with open(self._fichier()) as doc:
                for ligne in doc:
                    if entete.match(ligne):
                        return True
            return False
        if documentmaitre():
            return self.afficher_pdf()
        else:
            return txt.Document.afficher(self)

    def preparer_pdf(self, destination=False, environnement=None):
        """Mise en place du pdf
        """
        environnement = \
            environnement if environnement else {'TEXINPUTS': 'lib:'}
        orig = self._fichiertmp('pdf')
        dest = destination if destination else self._fichier('pdf')
        shutil.rmtree(self.rnd, ignore_errors=True)
        shutil.copytree(self.dossier, self.dossiertmp, symlinks=True)
        compiler_pdf(self._fichiertmp(), environnement)
        os.renames(orig, dest)
        if not cfg.DEVEL:
            shutil.rmtree(self.rnd, ignore_errors=True)


def compiler_pdf(fichier, environnement=None):
    """Compilation en pdf
    """
    environnement = environnement if environnement else {'TEXINPUTS': 'lib:'}
    commande = [
        'lualatex',
        '-interaction=nonstopmode',
        '-shell-restricted',
        fichier
    ]
    environnement = dict(os.environ, **environnement)
    environnement['shell_escape_commands'] = (
        "bibtex,bibtex8,kpsewhich,makeindex,mpost,repstopdf,"
        "gregorio,lilypond"
    )
    compiler(commande, fichier, environnement)
    if os.path.exists(os.path.splitext(fichier)[0] + '.toc'):
        if cfg.DEVEL:
            print('Table des matières : 2e compilation')
        compiler(commande, fichier, environnement)


compiler = txt.compiler  # pylint: disable=C0103

# pylint: disable=C0103
traiter_erreur_compilation = txt.traiter_erreur_compilation

FichierIllisible = txt.FichierIllisible

ErreurCompilation = txt.ErreurCompilation
