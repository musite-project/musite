# coding: utf-8
"""Gestion des gabarits tex.
En pratique, se ramène à l'extension tex.
"""

EXT = __name__.split('.')[-1]
from .tex import Document as DocTeX

class Document(DocTeX):
    """Document sty
    """
    def __init__(self, chemin, ext=None):
        DocTeX.__init__(self, chemin, ext=None)
