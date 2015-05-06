# coding: utf-8
"""Gestion des partitions ly

Ces partitions nécessitent LilyPond.

Voir plus d'informations à l'adresse :
http://www.lilypond.org
"""
import ext.txt as txt
from etc import config as cfg
from outils import motaleatoire, url, _
import os
import shutil
import subprocess as sp
import HTMLTags as h
import jrnl as l
EXT = __name__.split('.')[-1]


class Document(txt.Document):
    def __init__(self, chemin, ext=EXT):
        txt.Document.__init__(self, chemin, ext)

    def afficher(self):
        return h.OBJECT(
            data="{}".format(self.pdf()),
            Type="application/pdf",
            width="100%",
            height="100%"
        )

    def pdf(self, chemin=False, indice=''):
        chemin = chemin if chemin else 'pdf'
        fichierpdf = self._fichier('pdf')
        cheminpdf = self._chemin('pdf')
        if chemin:
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
                < os.path.getmtime(self.fichier)
        ):
            self.preparer_pdf()
        return url(fichierpdf)

    def preparer_pdf(self, destination=False, environnement={}):
        orig = self._fichiertmp('pdf')
        dest = destination if destination else self._fichier('pdf')
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.rmtree(self.rd, ignore_errors=True)
        shutil.copytree(self.dossier, self.dossiertmp, symlinks=True)
        compiler_pdf(self.fichiertmp, environnement)
        os.renames(orig, dest)
        shutil.rmtree(self.rd, ignore_errors=True)


def compiler_pdf(fichier, environnement={}):
    try:
        os.chdir(os.path.dirname(fichier))
        commande = [
            'lilypond',
            '-dsafe',
            fichier
        ]
        environnement = dict(os.environ, **environnement)
        compilation = sp.Popen(
            commande,
            env=environnement,
            stdout=sp.PIPE,
            stderr=sp.PIPE
        )
        sortie, erreurs = compilation.communicate()
        l.log(
            _('Sortie :')
            + '\n========\n'
            + '\n{}\n\n\n\n'.format(sortie.decode('utf8'))
            + '−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−\n\n\n\n'
            + _('Erreurs :')
            + '\n=========\n'
            + '\n{}\n'.format(erreurs.decode('utf8'))
        )
        if compilation.returncode:
            raise ErreurCompilation
    finally:
        os.chdir(cfg.PWD)


def traiter_erreur_compilation(dossier):
    return txt.Document(dossier.replace(os.path.sep, '/') + '/log').afficher()


FichierIllisible = txt.FichierIllisible


class ErreurCompilation(Exception):
    pass
