from ext import txt, tex
from etc import config as cfg
import os
import shutil
from bottle import template
EXT = __name__.split('.')[-1]


class Document(txt.Document):
    def __init__(self, chemin, ext=EXT):
        txt.Document.__init__(self, chemin, ext)
        # Chemin absolu des fichiers temporaires
        self.fichiertmp = os.path.join(cfg.TMP, self.fichierrelatif)
        self.dossiertmp = os.path.join(cfg.TMP, self.dossierrelatif)
        # Chemins des pdf
        self.cheminpdf = os.path.splitext(self.chemin)[0] + '.pdf'
        self.fichierrelatifpdf = self.cheminpdf.replace('/', os.path.sep)
        self.fichierpdf = os.path.join(
            cfg.PWD, cfg.STATIC, 'pdf', self.fichierrelatifpdf
        )
        self.fichiertmppdf = os.path.join(cfg.TMP, self.fichierrelatifpdf)

    @property
    def pdf(self):
        if not os.path.isfile(self.fichierpdf):
            self.preparer_pdf()
        return '/' + cfg.STATIC + '/pdf/' + self.cheminpdf

    def preparer_pdf(
        self,
        destination=False,
        environnement={}
    ):
        fichiertmp = 'main'
        textmp = os.path.join(self.dossiertmp, fichiertmp + '.tex')
        orig = os.path.join(self.dossiertmp, fichiertmp + '.pdf')
        dest = destination if destination else self.fichierpdf
        shutil.rmtree(self.dossiertmp, True)
        shutil.copytree(self.dossier, self.dossiertmp, True)
        with open(textmp, 'w') as f:
            f.write(template('partgreg', {'partition': self.nom}))
        compiler_pdf(textmp, environnement)
        os.renames(orig, dest)
        shutil.rmtree(self.dossiertmp, True)


def afficher(fichier):
    return Document(fichier).afficher()
afficher_source = afficher


def contenu(fichier):
    return Document(fichier).contenu


def editer(fichier):
    return Document(fichier).editer()


def enregistrer(fichier, contenu):
    return Document(fichier).enregistrer(contenu)


def pdf(fichier):
    return Document(fichier).pdf


def compiler_pdf(fichier, environnement={}):
    tex.compiler_pdf(fichier, environnement)


FichierIllisible = txt.FichierIllisible
