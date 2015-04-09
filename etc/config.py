import os


TITRE = 'Musite'

HOTE = '0.0.0.0'
PORT = 8080

PWD = os.path.abspath(os.getcwd())
TMP = os.path.join(PWD, 'tmp')
DATA = os.path.join(PWD, 'data')
PAGES = os.path.join(PWD, 'pages')

STATIC = 'static'

MODELES = [
    os.path.join(PWD, 'modeles', 'css'),
    os.path.join(PWD, 'modeles', 'html'),
    os.path.join(PWD, 'modeles', 'tex'),
]
