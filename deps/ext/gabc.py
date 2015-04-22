# coding: utf-8
"""Gestion des partitions gabc

Ces partitions nécessitent Gregorio, TeXLive avec un ensemble raisonnable
d'extensions, et GregorioTeX.

Voir plus d'informations à l'adresse :
http://gregorio-project.github.io/
"""
from ext import txt, tex
from etc import config as cfg
from outils import motaleatoire
import os
import shutil
from bottle import template, TEMPLATE_PATH
TEMPLATE_PATH += cfg.MODELES
import HTMLTags as h
EXT = __name__.split('.')[-1]


class Document(txt.Document):
    def __init__(self, chemin, ext=EXT):
        txt.Document.__init__(self, chemin, ext)
        # Chemin absolu des fichiers temporaires
        self.rd = os.path.join(cfg.TMP, motaleatoire(6))
        self.fichiertmp = os.path.join(self.rd, self.fichierrelatif)
        self.dossiertmp = os.path.join(self.rd, self.dossierrelatif)
        # Chemins des pdf
        self.cheminpdf = os.path.splitext(self.chemin)[0] + '.pdf'
        self.fichierrelatifpdf = self.cheminpdf.replace('/', os.path.sep)
        self.fichierpdf = os.path.join(
            cfg.PWD, cfg.STATIC, 'pdf', self.fichierrelatifpdf
        )
        self.fichiertmppdf = os.path.join(self.rd, self.fichierrelatifpdf)

    @property
    def pdf(self):
        if (
            not os.path.isfile(self.fichierpdf)
            or os.path.getmtime(self.fichierpdf)
                < os.path.getmtime(self.fichier)
        ):
            self.preparer_pdf()
        return '/' + cfg.STATIC + '/pdf/' + self.cheminpdf

    def afficher(self):
        try:
            return h.OBJECT(
                data="{}".format(self.pdf),
                Type="application/pdf",
                width="100%",
                height="100%"
            )
        except tex.ErreurCompilation:
            return (template(
                'erreur',
                {'sortie': tex.traiter_erreur_compilation(self.dossiertmp)}
            ))

    def preparer_pdf(
        self,
        destination=False,
        environnement={}
    ):
        fichiertmp = 'main'
        textmp = os.path.join(self.dossiertmp, fichiertmp + '.tex')
        orig = os.path.join(self.dossiertmp, fichiertmp + '.pdf')
        dest = destination if destination else self.fichierpdf
        shutil.rmtree(self.rd, ignore_errors=True)
        os.makedirs(self.dossiertmp, exist_ok=True)
        shutil.copy2(self.fichier, self.fichiertmp)
        with open(textmp, 'w') as f:
            f.write(template('partgreg', {'partition': self.nom}))
        compiler_pdf(textmp, environnement)
        os.renames(orig, dest)
        shutil.rmtree(self.rd, ignore_errors=True)


def compiler_pdf(fichier, environnement={}):
    tex.compiler_pdf(fichier, environnement)


FichierIllisible = txt.FichierIllisible
