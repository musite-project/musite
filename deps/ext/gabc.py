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
from deps.gabctk import Gabc, Lily, Midi
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
            # Liste des formats, avec :
            # - la méthode permettant de les créér ;
            # - les propriétés nécessaires à cette création ;
            # - l'intitulé correspondant à ces propriétés ;
            # - la valeur par défaut de ces propriétés.
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
                    'document': (_("Document"), {
                        'aa_titre':
                            (_("Titre"), ''),
                        'ab_mode':
                            (_("Mode"), ''),
                        'ab_type':
                            (_("Type"), ''),
                        'ba_papier':
                            (
                                _("Taille de la page (largeur, hauteur)"),
                                ('148mm', '210mm')
                            ),
                        'marge':
                            (
                                _("Marges (haut, bas, gauche, droite)"),
                                ('20mm', '20mm', '20mm', '20mm')
                            ),
                    }),
                    'notes': (_("Notes"), {
                        'notes_taille':
                            (_("Taille des notes"), 17),
                        'notes_couleur_lignes':
                            (_("Lignes en couleur"), True),
                        'notes_epaisseur_lignes':
                            (_("Épaisseur des lignes"), 20),
                        'notes_espace_lignes_texte':
                            (_("Espace sous la portée"), '7mm'),
                    }),
                    'texte': (_("Texte"), {
                        'texte_taille':
                            (_("Taille de la police"), 12),
                        'texte_symboles_couleur':
                            (_("Symboles en couleur"), True),
                        'initiale': (_("Initiale"), {
                            'initiale_couleur':
                                (_("Couleur"), False),
                            'initiale_elevation':
                                (_("Élévation"), '0pt'),
                            'initiale_taille':
                                (_("Taille"), 42),
                            'initiale_espace':
                                (
                                    _("Espace (avant, après)"),
                                    ('2.5mm', '2.5mm')
                                )
                        }),
                        'annotations': (_("Annotations"), {
                            'annotations_couleur':
                                (_("Couleur"), True),
                            'annotations_espace':
                                (_("Espace"), '0.5mm'),
                            'annotations_elevation':
                                (_("Élévation"), '0mm'),
                        }),
                    }),
                })
            },
            proprietes=proprietes
        )
        mode = self._gabc_entete('mode')
        if len(mode) == 1:
            mode += '.'
        try:
            type_piece = {
                '':             '',
                'alleluia':     '',
                'antiphona':    'Ant.',
                'communio':     'Comm.',
                'graduale':     'Grad.',
                'hymnus':       'Hymn.',
                'introitus':    'Intr.',
                'offertorium':  'Off.',
                'responsorium': 'Resp.',
                'sequentia':    'Seq.',
                'tractus':      'Tract.',
                'varia':        '',
                'versus':       '℣.',
            }[self._gabc_entete('office-part')]
        except KeyError as err:
            traiter_erreur(err)
            type_piece = ''
        if not proprietes:
            # Ces propriétés par défaut nécessitant de lire le gabc
            # correspondant, ce qui suppose que l'instance de classe soit
            # déjà initialisée, elles ne peuvent pas être définies ci-dessus.
            proprietes = {
                'aa_titre':     self._gabc_entete('name'),
                'ab_mode':      mode,
                'ab_type':      type_piece
            }
            self.proprietes['pdf'] = self._traiter_options(
                'pdf', self.proprietes_detail['pdf'], proprietes
            )

    @property
    def obsolete(self):
        return self.est_obsolete(self._fichiersortie('pdf'))

    @property
    def _gabc(self):
        """Contenu gabc du document
        """
        try:
            with open(self._fichier(), 'r') as fch:
                return Gabc(fch.read(-1))
        except UnicodeDecodeError as err:
            traiter_erreur(err)
            raise FichierIllisible
        except FileNotFoundError as err:
            traiter_erreur(err)
            return Gabc('')

    def _gabc_entete(self, entete):
        """Entête d'un document gabc

        Renvoie l'entête correspondante, ou bien une chaîne vide si cette
        entête n'est pas définie.
        """
        try:
            return self._gabc.entetes[entete]
        except KeyError as err:
            traiter_erreur(err)
            return ''

    @property
    def entetes(self):
        """Entêtes d'un document gabc

        Renvoie le dictionnaire contenant les entêtes.
        """
        return self._gabc.entetes

    def partition(self, transposition=None):
        """Partition extraite du gabc

        Renvoie un objet partition défini dans gabctk
        """
        return self._gabc.partition(transposition=transposition)

    def afficher(self, actualiser=2):
        return self.afficher_pdf(actualiser=actualiser)

    def gabc(self, fmt, chemin=None, indice=''):
        """Format gabc
        """
        fichier = self._fichiersortie(fmt, chemin=chemin, indice=indice)
        if (
                not os.path.isfile(fichier)
                or os.path.getmtime(fichier)
                < os.path.getmtime(self._fichier())
                or os.path.getmtime(fichier)
                < os.path.getmtime(
                    self._fichiersortie('pdf', chemin=chemin, indice=indice)
                )
        ):
            try:
                self.preparer_gabc(fmt, fichier)
            except IndexError as err:
                traiter_erreur(err)
                raise ErreurCompilation
        return url(fichier)

    def ly(self, chemin=None, indice=''):  # pylint: disable=C0103
        """Format lilypond
        """
        return self.gabc(fmt='ly', chemin=chemin, indice=indice)

    def midi(self, chemin=None, indice=''):
        """Format midi
        """
        try:
            return self.gabc(fmt='midi', chemin=chemin, indice=indice)
        except ErreurCompilation as err:
            traiter_erreur(err)

    def preparer_pdf(self, destination=None, environnement=None):
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

    def preparer_gabc(self, fmt, destination=None):
        """Mise en place du gabc
        """
        dest = destination if destination else self._fichier(fmt)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        fichier = {
            'midi': Midi,
            'ly':   Lily
        }[fmt](
            titre=self._gabc_entete('name'),
            partition=self.partition(
                transposition=self.proprietes[fmt]['transposition']
            ),
            tempo=self.proprietes[fmt]['tempo']
        )
        fichier.ecrire(dest)


def compiler_pdf(fichier, environnement=None):
    """Compilation en pdf
    """
    tex.compiler_pdf(fichier, environnement)


FichierIllisible = txt.FichierIllisible

ErreurCompilation = txt.ErreurCompilation
