# coding: utf-8
"""Configuration générale de musite.

Vous pouvez modifier ici le titre du site, l'adresse et le port d'écoute, les
emplacements des dossiers.
Vous pouvez aussi définir si vous êtes ou non en mode développement.
"""
import os


TITRE = 'Musite'

HOTE = '0.0.0.0'
PORT = 8080

PWD = os.sep + os.path.join(
        *os.path.dirname(os.path.realpath(__file__)).split(os.sep)[:-1]
)
TMP = os.path.join(PWD, 'tmp')
DATA = os.path.join(PWD, 'data')
PAGES = os.path.join(PWD, 'pages')

STATIC = 'static'

MODELES = [
    os.path.join(PWD, 'modeles', 'css'),
    os.path.join(PWD, 'modeles', 'html'),
    os.path.join(PWD, 'modeles', 'tex'),
]

# Mettez le paramètre suivant à False en production.
DEVEL = True
