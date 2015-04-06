import os.path
import HTMLTags as h
import bottle as b
from etc import config as cfg
b.TEMPLATE_PATH += cfg.MODELES
EXT = __name__.split('.')[-1]


class Document:
    def __init__(self, chemin, ext='txt'):
        self.ext = ext
        self.chemin = chemin
        self.fichier = os.path.join(
            cfg.DATA,
            chemin.replace('/', os.path.sep)
        )

    def afficher(self):
        return h.CODE(b.html_escape(contenu(self.fichier)))

    afficher_source = afficher

    @property
    def contenu(self):
        try:
            with open(self.fichier) as f:
                return f.read(-1)
        except UnicodeDecodeError:
            raise FichierIllisible(self.fichier)

    def editer(self):
        return b.template(
            'editeur',
            emplacement=self.chemin,
            texte=self.contenu,
            ext=self.ext
        )

    def enregistrer(self, contenu):
        with open(self.fichier, 'w') as f:
            f.write(contenu)


def afficher(fichier):
    return Document(fichier).afficher()
afficher_source = afficher


def contenu(fichier):
    return Document(fichier).contenu


def editer(fichier):
    return Document(fichier).editer()


def enregistrer(fichier, contenu):
    return Document(fichier).enregistrer(contenu)


class FichierIllisible(Exception):
    pass
