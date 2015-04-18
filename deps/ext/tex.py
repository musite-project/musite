import ext.txt as txt
from etc import config as cfg
from outils import motaleatoire
import os
import shutil
import subprocess as sp
import HTMLTags as h
import jrnl as l
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
        compilation = sp.Popen(
            commande,
            env=environnement,
            stdout=sp.PIPE,
            stderr=sp.PIPE
        )
        sortie, erreurs = compilation.communicate()
        l.log(
            'Sortie :'
            + '\n========\n'
            + '\n{}\n\n\n\n'.format(sortie.decode('utf8'))
            + '−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−\n\n\n\n'
            + 'Erreurs :'
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
