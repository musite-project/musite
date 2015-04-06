from mistune import markdown
import ext.txt as t
EXT = __name__.split('.')[-1]


class Document(t.Document):
    def __init__(self, chemin, ext=EXT):
        t.Document.__init__(self, chemin, ext)

    def afficher(self):
        return markdown(self.contenu)


def afficher(fichier):
    return Document(fichier).afficher()


def afficher_source(fichier):
    return Document(fichier).afficher_source()


def contenu(fichier):
    return Document(fichier).contenu


def editer(fichier):
    return Document(fichier).editer()


def enregistrer(fichier, contenu):
    return Document(fichier).enregistrer(contenu)


FichierIllisible = t.FichierIllisible
