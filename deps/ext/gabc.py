# coding: utf-8
"""Gestion des partitions gabc

Ces partitions nécessitent Gregorio, TeXLive avec un ensemble raisonnable
d'extensions, et GregorioTeX.

Voir plus d'informations à l'adresse :
http://gregorio-project.github.io/
"""
from . import txt, tex
from etc import config as cfg
from deps.outils import templateperso, url, traiter_erreur, _
from deps.gabctk import Gabc, Lily, Midi, Partition
import os
import shutil


# Ce qui suit est nécessaire pour modifier les délimiteurs dans les gabarits.
# Comme LaTeX fait un usage constant des accolades, on utilise les symboles
# <<< et >>>
TEMPLATETEX = templateperso()


class Document(txt.Document):
    """Document gabc
    """
    def __init__(self, chemin, proprietes=None):
        txt.Document.__init__(
            self, chemin,
            formats={
                'midi': (self.midi, {
                    'tempo':                (_("Tempo"), 165),
                    'transposition':        (_("Transposition"), 0),
                }),
                'ly': (self.ly, {
                    'tempo':                (_("Tempo"), 165),
                    'transposition':        (_("Transposition"), 0),
                }),
                'pdf': (self.pdf, {
                    'couleur':
                        (_("Couleur (R,V,B)"), (154, 0, 0)),
                    'initiale': (_("Initiale"), {
                        'taille_initiale':
                            (_("Taille"), 43),
                        'elevation_initiale':
                            (_("Élévation"), '0 pt'),
                        'couleur_initiale':
                            (_("Couleur"), False),
                    }),
                    'document': (_("Document"), {
                        'papier':
                            (_("Taille de la page"), ('148mm', '210mm')),
                        'titre':
                            (_("Titre"), ''),
                        'marges':
                            (_("Marges"), {
                                'marge_gauche': (_("gauche"), '20mm'),
                                'marge_droite': (_("droite"), '20mm'),
                                'marge_haut':   (_("haut"), '20mm'),
                                'marge_bas':    (_("bas"), '20mm'),
                            }),
                    }),
                    'notes': (_("Notes"), {
                        'taille_notes':
                            (_("Taille des notes"), 17),
                        'couleur_lignes':
                            (_("Lignes en couleur"), True),
                        'epaisseur_lignes':
                            (_("Épaisseur des lignes"), 20),
                        'espace_lignes_texte':
                            (_("Espace sous la portée"), '7 mm'),
                    }),
                    'texte': (_("Texte"), {
                        'taille_police':
                            (_("Taille de la police"), 12),
                        'couleur_symboles':
                            (_("Symboles en couleur"), True),
                    }),
                })
            },
            proprietes=proprietes
        )
        self.fmt['pdf'][1]['document'][1]['titre'] = \
            (_("Titre"), self._gabc.entetes['name'])

    @property
    def _gabc(self):
        """Contenu gabc du document
        """
        with open(self._fichier(), 'r') as fch:
            return Gabc(fch.read(-1))

    def afficher(self):
        return self.afficher_pdf()

    def gabc(self, fmt, chemin=False, indice=''):
        """Format gabc
        """
        fichier = self._fichiersortie(fmt, chemin=chemin, indice=indice)
        if (
                not os.path.isfile(fichier)
                or os.path.getmtime(fichier)
                < os.path.getmtime(self._fichier())
        ):
            try:
                self.preparer_gabc(fmt, fichier)
            except IndexError as err:
                traiter_erreur(err)
                raise ErreurCompilation
        return url(fichier)

    def ly(self, chemin=False, indice=''):  # pylint: disable=C0103
        """Format lilypond
        """
        return self.gabc('ly', chemin, indice)

    def midi(self, chemin=False, indice=''):
        """Format midi
        """
        try:
            return self.gabc('midi', chemin, indice)
        except ErreurCompilation as err:
            traiter_erreur(err)

    def preparer_pdf(self, destination=False, environnement=None):
        """Mise en place du pdf
        """
        fichiertmp = 'main'
        textmp = os.path.join(self.dossiertmp, fichiertmp + '.tex')
        orig = os.path.join(self.dossiertmp, fichiertmp + '.pdf')
        dest = destination if destination else self._fichier('pdf')
        shutil.rmtree(self.rnd, ignore_errors=True)
        os.makedirs(self.dossiertmp, exist_ok=True)
        shutil.copy2(self._fichier(), self._fichiertmp())
        with open(textmp, 'w') as tmp:
            tmp.write(TEMPLATETEX(
                'partgreg',
                {
                    'partition': self.nom,
                    'proprietes': self.proprietes['pdf']
                },
            ))
        compiler_pdf(textmp, environnement)
        os.renames(orig, dest)
        if not cfg.DEVEL:
            shutil.rmtree(self.rnd, ignore_errors=True)

    def preparer_gabc(self, fmt, destination=False):
        """Mise en place du gabc
        """
        dest = destination if destination else self._fichier(fmt)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        partition = Partition(
            gabc=self._gabc.partition,
            transposition=self.proprietes[fmt]['transposition']
        )
        fichier = {
            'midi': Midi,
            'ly':   Lily
        }[fmt](partition, self.proprietes[fmt]['tempo'])
        fichier.ecrire(dest)


def compiler_pdf(fichier, environnement=None):
    """Compilation en pdf
    """
    tex.compiler_pdf(fichier, environnement)


FichierIllisible = txt.FichierIllisible

ErreurCompilation = txt.ErreurCompilation
