import ext.txt as t
EXT = __name__.split('.')[-1]


class Document(t.Document):
    def __init__(self, chemin, ext=EXT):
        t.Document.__init__(self, chemin, ext)
        print(EXT, self.ext)


def afficher(fichier):
    return Document(fichier).afficher()
afficher_source = afficher


def contenu(fichier):
    return Document(fichier).contenu


def editer(fichier):
    return Document(fichier).editer()


def enregistrer(fichier, contenu):
    return Document(fichier).enregistrer(contenu)


def compiler_pdf(fichier):
    pass


FichierIllisible = t.FichierIllisible
