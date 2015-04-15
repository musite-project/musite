import os
import HTMLTags as h
from base64 import b64encode
from etc import config as cfg


def afficher(fichier):
    return h.OBJECT(
        data="data:application/pdf;base64,{}".format(contenu(fichier)),
        Type="application/pdf",
        width="100%",
        height="100%"
        )


def contenu(fichier):
    fichier = os.path.join(cfg.DATA,fichier.replace('/', os.path.sep))
    with open(fichier, "rb") as f:
        return b64encode(f.read()).decode('ascii')


class FichierIllisible(Exception):
    pass
