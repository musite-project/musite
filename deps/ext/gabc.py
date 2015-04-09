from ext import txt, tex
from etc import config as cfg
from outils import motaleatoire
import os
import shutil
from bottle import template
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
        if not os.path.isfile(self.fichierpdf):
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
            return (
                "Il y a eu une erreur pendant le traitement du document. "
                + "Ceci vient probablement d'une erreur de syntaxe ; "
                + "si vous êtes absolument certain du contraire, merci de "
                + "signaler le problème."
                + h.BR()
                + 'Voici la sortie de la commande :'
                + h.BR()
                + h.BR()
                + tex.traiter_erreur_compilation(self.dossiertmp)
            )

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


def afficher(fichier):
    return Document(fichier).afficher()


def afficher_source(fichier):
    return txt.Document(fichier).afficher_source()


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
