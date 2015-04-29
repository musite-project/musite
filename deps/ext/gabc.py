# coding: utf-8
"""Gestion des partitions gabc

Ces partitions nécessitent Gregorio, TeXLive avec un ensemble raisonnable
d'extensions, et GregorioTeX.

Voir plus d'informations à l'adresse :
http://gregorio-project.github.io/
"""
from ext import txt, tex
from etc import config as cfg
from outils import templateperso, url,  _
from gabctk import Gabc, Lily, Midi, Partition
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

        # Formats d'export possibles, avec la méthode renvoyant le document
        # compilé dans chaque format.
        self.fmt = {
            'ly':   self.ly,
            'midi': self.midi,
            'pdf':  self.pdf,
            }

        # Propriétés du document
        # self.listeproprietes contient la liste des propriétés, avec leur
        # description et leur valeur par défaut.
        # self.proprietes contient les propriétés définies par l'utilisateur,
        # ou à défaut les valeurs par défaut.
        self.listeproprietes = {}
        self.proprietes = {}
        self.listeproprietes['midi']\
            = self.listeproprietes['ly']\
            = {
                'tempo':                (_("Tempo"), 165),
                'transposition':        (_("Transposition"), 0)
            }
        self.listeproprietes['pdf'] = {
            'couleur':              (_("Couleur (R,V,B)"), (154, 0, 0)),
            'couleur_initiale':     (_("Initiale en couleur"), False),
            'couleur_lignes':       (_("Lignes en couleur"), True),
            'couleur_symboles':     (_("Symboles en couleur"), True),
            'epaisseur_lignes':     (_("Épaisseur des lignes"), 20),
            'espace_lignes_texte':  (_("Espacement sous la portée"), '7 mm'),
            'papier':               (_("Taille de la page"), 'a5'),
            'taille_initiale':      (_("Taille de l'initiale"), 43),
            'taille_notes':         (_("Taille des notes"), 17),
            'taille_police':        (_("Taille de la police"), 12),
        }
        for fmt in self.fmt:
            self.proprietes[fmt] = {
                prop: val[1]
                for prop, val in self.listeproprietes[fmt].items()
            }
        if proprietes:
            for fmt in proprietes:
                for prop, val in proprietes[fmt].items():
                    if prop in self.listeproprietes[fmt]:
                        t = type(self.listeproprietes[fmt][prop][1])
                        if t in (str, int, float):
                            self.proprietes[fmt][prop] = t(val)
                        elif t is bool:
                            self.proprietes[fmt][prop] = t(int(val))
                        elif t in (tuple, list):
                            if type(val) in (tuple, list):
                                self.proprietes[fmt][prop] = val
                            else:
                                self.proprietes[fmt][prop] = tuple(
                                    type(pr)(i)
                                    for i, pr
                                    in zip(
                                        val.split(','),
                                        self.listeproprietes[fmt][prop][1]
                                    )
                                )

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

    def exporter(self, fmt):
        return self.fmt[fmt]

    def pdf(self, chemin=False, indice=''):
        chemin = chemin if chemin else 'pdf'
        fichierpdf = self._fichier('pdf')
        cheminpdf = self._chemin('pdf')
        if chemin:
            fichierpdf = fichierpdf.replace(
                '/pdf/',
                '/{}/{}/'.format(chemin, indice).replace('//', '/')
            )
            cheminpdf = cheminpdf.replace(
                '/pdf/',
                '/{}/{}/'.format(chemin, indice).replace('//', '/')
            )
        if (
            not os.path.isfile(fichierpdf)
            or os.path.getmtime(fichierpdf)
                < os.path.getmtime(self.fichier)
        ):
            self.preparer_pdf(fichierpdf)
        return url(fichierpdf)

    def gabc(self, fmt, chemin=False, indice=''):
        chemin = chemin if chemin else fmt
        fichier = self._fichier(fmt)
        if chemin:
            fichier = fichier.replace(
                '/{}/'.format(fmt),
                '/{}/{}/'.format(chemin, indice).replace('//', '/')
            )
        if (
            not os.path.isfile(fichier)
            or os.path.getmtime(fichier)
                < os.path.getmtime(self.fichier)
        ):
            self.preparer_gabc(fmt, fichier)
        return url(fichier)

    def ly(self, chemin=False, indice=''):
        return self.gabc('ly', chemin, indice)

    def midi(self, chemin=False, indice=''):
        return self.gabc('midi', chemin, indice)

    def preparer_pdf(self, destination=False, environnement={}):
        fichiertmp = 'main'
        textmp = os.path.join(self.dossiertmp, fichiertmp + '.tex')
        orig = os.path.join(self.dossiertmp, fichiertmp + '.pdf')
        dest = destination if destination else self._fichier('pdf')
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

    def preparer_gabc(self, fmt, destination=False):
        dest = destination if destination else self._fichier(fmt)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(self.fichier, 'r') as f:
            g = Gabc(f.read(-1))
            partition = Partition(
                gabc=g.partition,
                transposition=self.proprietes[fmt]['transposition']
            )
            fichier = {
                'midi': Midi,
                'ly':   Lily
            }[fmt](partition, self.proprietes[fmt]['tempo'])
            fichier.ecrire(dest)


def compiler_pdf(fichier, environnement={}):
    tex.compiler_pdf(fichier, environnement)


FichierIllisible = txt.FichierIllisible

ErreurCompilation = tex.ErreurCompilation
