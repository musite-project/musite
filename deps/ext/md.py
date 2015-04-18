from mistune import markdown
import ext.txt as txt
EXT = __name__.split('.')[-1]


class Document(txt.Document):
    def __init__(self, chemin, ext=EXT):
        txt.Document.__init__(self, chemin, ext)

    def afficher(self):
        return markdown(self.contenu)


FichierIllisible = txt.FichierIllisible
