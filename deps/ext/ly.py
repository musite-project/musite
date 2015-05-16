# coding: utf-8
"""Gestion des partitions ly

Ces partitions nécessitent LilyPond.

Voir plus d'informations à l'adresse :
http://www.lilypond.org
"""
from . import txt
import os
import shutil
EXT = __name__.split('.')[-1]  # pylint: disable=R0801


class Document(txt.Document):
    """Document lilypond
    """
    def __init__(self, chemin):
        txt.Document.__init__(self, chemin)

    def afficher(self):
        return self.afficher_pdf(
            message="""
Il est aussi possible que vous ayez saisi du code *Scheme* dans votre
document : par souci de sécurité, `Lilypond` est lancé avec des options plus
restrictives, qui rendent impossibles certaines opérations.
"""
        )

    def preparer_pdf(self, destination=False, environnement=None):
        """Mise en place du pdf
        """
        orig = self._fichiertmp('pdf')
        dest = destination if destination else self._fichier('pdf')
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.rmtree(self.rnd, ignore_errors=True)
        shutil.copytree(self.dossier, self.dossiertmp, symlinks=True)
        compiler_pdf(self._fichiertmp(), environnement)
        os.renames(orig, dest)
        shutil.rmtree(self.rnd, ignore_errors=True)


def compiler_pdf(fichier, environnement=None):
    """Compilation en pdf
    """
    commande = [
        'lilypond',
        '-dsafe',
        fichier
    ]
    environnement = dict(
        os.environ,
        **environnement if environnement else {}
    )
    compiler(commande, fichier, environnement)


compiler = txt.compiler  # pylint: disable=C0103


def traiter_erreur_compilation(dossier):
    """Réaction en cas d'erreur de compilation
    """
    return txt.Document(dossier.replace(os.path.sep, '/') + '/log').afficher()


FichierIllisible = txt.FichierIllisible


ErreurCompilation = txt.ErreurCompilation
