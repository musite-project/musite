# coding: utf-8
"""Configuration générale de musite.

Vous pouvez modifier ici le titre du site, l'adresse et le port d'écoute, les
emplacements des dossiers.
Vous pouvez aussi définir si vous êtes ou non en mode développement.
"""
import os
from pathlib import Path


TITRE = 'Musite'

HOTE = '0.0.0.0'
PORT = 8080

PWD = Path(os.path.realpath(__file__)).parents[1]
ETC = PWD / 'etc'
EXT = PWD / 'ext'
DATA = PWD / 'data'
I18N = PWD / 'i18n'
PAGES = PWD / 'pages'
PANDOC = PWD / 'modeles' / 'pandoc'
STATIC = PWD / 'static'
DOCS = STATIC / 'docs'
TMP = DOCS / 'tmp'

LANGUES = [
    ('fr', 'french'),
    ('en', 'english'),
]
LANGUE = 'fr'

MODELES = [
    PWD / 'modeles' / 'css',
    PWD / 'modeles' / 'html',
    PWD / 'modeles' / 'ly',
    PWD / 'modeles' / 'tex',
]

# Mettez le paramètre suivant à False en production.
DEVEL = False
