# coding: utf-8
"""Gestion des partitions gabc

Ces partitions nécessitent Gregorio, TeXLive avec un ensemble raisonnable
d'extensions, et GregorioTeX.

Voir plus d'informations à l'adresse :
http://gregorio-project.github.io/
"""
from ext import txt, tex
from etc import config as cfg
from outils import templateperso, motaleatoire, _
from mistune import markdown
import os
import shutil
from bottle import template
import HTMLTags as h
EXT = __name__.split('.')[-1]


# Ce qui suit est nécessaire pour modifier les délimiteurs dans les gabarits.
# Comme LaTeX fait un usage constant des accolades, on utilise les symboles
# <<< et >>>
templatetex = templateperso()


class Document(txt.Document):
    def __init__(self, chemin, ext=EXT, proprietes=False):
        txt.Document.__init__(self, chemin, ext)
        # Chemin absolu des fichiers temporaires
        self.rd = os.path.join(cfg.TMP, motaleatoire(6))
        self.fichiertmp = os.path.join(self.rd, self.fichierrelatif)
        self.dossiertmp = os.path.join(self.rd, self.dossierrelatif)
        # Chemins des pdf
        self.cheminpdf = os.path.splitext(self.chemin)[0] + '.pdf'
        self.fichierrelatifpdf = self.cheminpdf.replace('/', os.path.sep)
        self.dossierpdf = 'pdf'
        self.fichierpdf = os.path.join(
            cfg.PWD, cfg.STATIC, self.dossierpdf, self.fichierrelatifpdf
        )
        self.fichiertmppdf = os.path.join(self.rd, self.fichierrelatifpdf)

        # Formats d'export possibles
        self.fmt = ['pdf']

        # Propriétés du document
        # self.listeproprietes contient la liste des propriétés, avec leur
        # description et leur valeur par défaut.
        # self.proprietes contient les propriétés définies par l'utilisateur,
        # ou à défaut les valeurs par défaut.
        self.listeproprietes = {}
        self.proprietes = {}
        self.listeproprietes['pdf'] = {
            'couleur':              (_("Couleur (R,V,B)"), (154, 0, 0)),
            'couleur_initiale':     (_("Initiale en couleur"), False),
            'couleur_lignes':       (_("Lignes en couleur"), True),
            'couleur_symboles':     (_("Symboles en couleur"), True),
            'epaisseur_lignes':     (_("Épaisseur des lignes"), 20),
            'espace_lignes_texte':  (_("Espacement sous la portée"), '6 mm'),
            'papier':               (_("Taille de la page"), 'a5'),
            'taille_initiale':      (_("Taille de l'initiale"), 43),
            'taille_notes':         (_("Taille des notes"), 17),
            'taille_police':        (_("Taille de la police"), 12),
        }
        self.proprietes['pdf'] = {
            prop: val[1]
            for prop, val in self.listeproprietes['pdf'].items()
        }
        if proprietes and 'pdf' in proprietes:
            for prop, val in proprietes['pdf'].items():
                if prop in self.listeproprietes['pdf']:
                    t = type(self.listeproprietes['pdf'][prop][1])
                    if t in (str, int, float):
                        self.proprietes['pdf'][prop] = t(val)
                    elif t is bool:
                        self.proprietes['pdf'][prop] = t(int(val))
                    elif t in (tuple, list):
                        self.proprietes['pdf'][prop] = tuple(
                            type(pr)(i)
                            for i, pr
                            in zip(
                                val.split(','),
                                self.listeproprietes['pdf'][prop][1]
                            )
                        )

    def pdf(self, chemin=False, indice=''):
        chemin = chemin if chemin else self.dossierpdf
        fichierpdf = self.fichierpdf.replace(
            '/{}/'.format(self.dossierpdf),
            '/{}/{}/'.format(chemin, indice)
        )
        cheminpdf = self.cheminpdf.replace(
            '/{}/'.format(self.dossierpdf),
            '/{}/{}/'.format(chemin, indice)
        )
        if (
            not os.path.isfile(fichierpdf)
            or os.path.getmtime(fichierpdf)
                < os.path.getmtime(self.fichier)
        ):
            self.preparer_pdf(fichierpdf)
        return fichierpdf.replace(cfg.PWD, '').replace(os.sep, '/')

    def afficher(self):
        try:
            return h.OBJECT(
                data="{}".format(self.pdf()),
                Type="application/pdf",
                width="100%",
                height="100%"
            )
        except tex.ErreurCompilation:
            return (markdown(_(
                """\
Il y a eu une erreur pendant le traitement du document.
Ceci vient probablement d'une erreur de syntaxe ; si vous êtes absolument
certain du contraire, merci de signaler le problème.

Voici la sortie de la commande :

                """
            )) + tex.traiter_erreur_compilation(self.dossiertmp)
            )

    def preparer_pdf(
        self,
        destination=False,
        environnement={}
    ):
        fichiertmp = 'main'
        textmp = os.path.join(self.dossiertmp, fichiertmp + '.tex')
        orig = os.path.join(self.dossiertmp, fichiertmp + '.pdf')
        dest = destination if destination else self.fichierpdf
        shutil.rmtree(self.rd, ignore_errors=True)
        os.makedirs(self.dossiertmp, exist_ok=True)
        shutil.copy2(self.fichier, self.fichiertmp)
        with open(textmp, 'w') as f:
            f.write(templatetex(
                'partgreg',
                {
                    'partition': self.nom,
                    'proprietes': self.proprietes['pdf']
                },
            ))
        compiler_pdf(textmp, environnement)
        os.renames(orig, dest)
        if not cfg.DEVEL:
                shutil.rmtree(self.rd, ignore_errors=True)


def compiler_pdf(fichier, environnement={}):
    tex.compiler_pdf(fichier, environnement)


FichierIllisible = txt.FichierIllisible

ErreurCompilation = tex.ErreurCompilation
