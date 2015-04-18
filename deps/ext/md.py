# coding: utf-8
"""Gestion des fichiers MarkDown

Le langage MarkDown est géré ici par le module mistune, intégré au programme :
il n'y a donc pas de dépendance externe particulière.

Voyez pour la syntaxe :
http://fr.wikipedia.org/wiki/Markdown
"""
from mistune import markdown
import ext.txt as txt
EXT = __name__.split('.')[-1]


class Document(txt.Document):
    def __init__(self, chemin, ext=EXT):
        txt.Document.__init__(self, chemin, ext)

    def afficher(self):
        return markdown(self.contenu)


FichierIllisible = txt.FichierIllisible
