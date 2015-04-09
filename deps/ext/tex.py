import ext.txt as t
from etc import config as cfg
from outils import motaleatoire
import os
import shutil
import subprocess as sp
import jrnl as l
EXT = __name__.split('.')[-1]


class Document(t.Document):
    def __init__(self, chemin, ext=EXT):
        t.Document.__init__(self, chemin, ext)
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
        if not os.path.isfile(self.fichierpdf):
            self.preparer_pdf()
        return '/' + cfg.STATIC + '/pdf/' + self.cheminpdf

    def preparer_pdf(
        self,
        destination=False,
        environnement={}
    ):
        orig = self.fichiertmppdf
        dest = destination if destination else self.fichierpdf
        shutil.rmtree(self.rd, ignore_errors=True)
        shutil.copytree(self.dossier, self.dossiertmp, symlinks=True)
        compiler_pdf(self.fichiertmp, environnement)
        os.renames(orig, dest)
        shutil.rmtree(self.rd, ignore_errors=True)


def afficher(fichier):
    return Document(fichier).afficher()
afficher_source = afficher


def contenu(fichier):
    return Document(fichier).contenu


def editer(fichier):
    return Document(fichier).editer()


def enregistrer(fichier, contenu):
    return Document(fichier).enregistrer(contenu)


def pdf(fichier, recompiler=False):
    return Document(fichier).pdf


def compiler_pdf(fichier, environnement={}):
    try:
        os.chdir(os.path.dirname(fichier))
        commande = [
            'lualatex',
            '-interaction=nonstopmode',
            '-shell-escape',
            fichier
        ]
        environnement = dict(os.environ, **environnement)
        sortie, erreurs = sp.Popen(
            commande,
            env=environnement,
            stdout=sp.PIPE,
            stderr=sp.PIPE
        ).communicate()
        l.log(
            'Sortie :\n{}\n\n'.format(sortie.decode('utf8'))
            + 'Erreurs :\n{}\n'.format(erreurs.decode('utf8'))
        )
    finally:
        os.chdir(cfg.PWD)


FichierIllisible = t.FichierIllisible
