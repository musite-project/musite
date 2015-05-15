# coding: utf-8
"""Gestion des partitions ly

Ces partitions nécessitent LilyPond.

Voir plus d'informations à l'adresse :
http://www.lilypond.org
"""
from . import txt
from etc import config as cfg
from deps.outils import url, _
from deps.mistune import markdown
import os
import shutil
import deps.HTMLTags as h
EXT = __name__.split('.')[-1]


class Document(txt.Document):
    """Document lilypond
    """
    def __init__(self, chemin):
        txt.Document.__init__(self, chemin)

    def afficher(self):
        try:
            return h.OBJECT(
                data="{}".format(self.pdf()),
                Type="application/pdf",
                width="100%",
                height="100%"
            )
        except ErreurCompilation:
            return (markdown(_(
                """\
Il y a eu une erreur pendant le traitement du document.
Ceci vient probablement d'une erreur de syntaxe ; si vous êtes absolument
certain du contraire, merci de signaler le problème.

Il est aussi possible que vous ayez saisi du code *Scheme* dans votre
document : par souci de sécurité, `Lilypond` est lancé avec des options plus
restrictives, qui rendent impossibles certaines opérations.

Voici la sortie de la commande :

                """
            )) + traiter_erreur_compilation(self.dossiertmp))

    def pdf(self, chemin=False, indice=''):
        """Format pdf
        """
        chemin = chemin if chemin else 'pdf'
        fichierpdf = self._fichier('pdf')
        cheminpdf = self._chemin('pdf')
        fichierpdf = fichierpdf.replace(
            '/pdf/',
            '/{}/{}/'.format(chemin, indice).replace('//', '/')
        )
        cheminpdf = cheminpdf.replace(
            '/pdf/',
            '/{}/{}/'.format(chemin, indice).replace('//', '/')
        )
        if (
                not os.path.isfile(self._fichier('pdf'))
                or os.path.getmtime(self._fichier('pdf'))
                < os.path.getmtime(self._fichier())
        ):
            self.preparer_pdf()
        print(fichierpdf)
        return url(fichierpdf)

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
    try:
        os.chdir(os.path.dirname(fichier))
        commande = [
            'lilypond',
            '-dsafe',
            fichier
        ]
        environnement = dict(
            os.environ,
            **environnement if environnement else {}
        )
        compiler(commande, environnement)
    finally:
        os.chdir(cfg.PWD)


compiler = txt.compiler  # pylint: disable=C0103


def traiter_erreur_compilation(dossier):
    """Réaction en cas d'erreur de compilation
    """
    return txt.Document(dossier.replace(os.path.sep, '/') + '/log').afficher()


FichierIllisible = txt.FichierIllisible


ErreurCompilation = txt.ErreurCompilation
