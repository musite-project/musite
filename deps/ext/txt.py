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
        self.nom = os.path.splitext(chemin.split('/')[-1])[0]
        # Chemin relatif du fichier
        self.fichierrelatif = chemin.replace('/', os.path.sep)
        self.dossierrelatif = os.path.dirname(self.fichierrelatif)
        # Chemin absolu du fichier
        self.fichier = os.path.join(
            cfg.DATA,
            self.fichierrelatif
        )
        self.dossier = os.path.dirname(self.fichier)

    def afficher(self):
        return h.CODE(b.html_escape(self.contenu))

    afficher_source = afficher

    @property
    def contenu(self):
        try:
            with open(self.fichier) as f:
                return f.read(-1)
        except UnicodeDecodeError:
            raise FichierIllisible(self.fichier)

    def editer(self, creation=False):
        try:
            return b.template(
                'editeur',
                emplacement=self.chemin,
                texte=self.contenu,
                ext=self.ext
            )
        except FileNotFoundError:
            if creation:
                return b.template(
                'editeur',
                emplacement=self.chemin,
                texte='',
                ext=self.ext
            )
            else:
                b.abort(404)

    def enregistrer(self, contenu):
        with open(self.fichier, 'w') as f:
            f.write(contenu)

    def supprimer(self):
        os.remove(self.fichier)


class FichierIllisible(Exception):
    pass
