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
from deps.mistune import markdown
import os
import shutil
import deps.HTMLTags as h
EXT = __name__.split('.')[-1]


# Ce qui suit est nécessaire pour modifier les délimiteurs dans les gabarits.
# Comme LaTeX fait un usage constant des accolades, on utilise les symboles
# <<< et >>>
TEMPLATETEX = templateperso()


class Document(txt.Document):
    """Document gabc
    """
    def __init__(self, chemin, proprietes=None):
        # Formats d'export possibles, avec la méthode renvoyant le document
        # compilé dans chaque format.
        self.fmt = {
            'ly':   self.ly,
            'midi': self.midi,
            'pdf':  self.pdf,
            }

        # Propriétés du document
        # listeproprietes contient la liste des propriétés, avec leur
        # description et leur valeur par défaut.
        listeproprietes = {
            'midi': {
                'tempo':                (_("Tempo"), 165),
                'transposition':        (_("Transposition"), 0),
            },
            'ly': {
                'tempo':                (_("Tempo"), 165),
                'transposition':        (_("Transposition"), 0),
            },
            'pdf': {
                'couleur':              (_("Couleur (R,V,B)"), (154, 0, 0)),
                'couleur_initiale':     (_("Initiale en couleur"), False),
                'couleur_lignes':       (_("Lignes en couleur"), True),
                'couleur_symboles':     (_("Symboles en couleur"), True),
                'epaisseur_lignes':     (_("Épaisseur des lignes"), 20),
                'espace_lignes_texte':  (_("Espace sous la portée"), '7 mm'),
                'papier':               (_("Taille de la page"), 'a5'),
                'taille_initiale':      (_("Taille de l'initiale"), 43),
                'taille_notes':         (_("Taille des notes"), 17),
                'taille_police':        (_("Taille de la police"), 12),
            }
        }
        txt.Document.__init__(
            self,
            chemin,
            formats=self.fmt,
            listeproprietes=listeproprietes,
            proprietes=proprietes
        )

    def afficher(self):
        try:
            return h.OBJECT(
                data="{}".format(self.pdf()),
                Type="application/pdf",
                width="100%",
                height="100%"
            )
        except ErreurCompilation:
            return (markdown(_(
                """\
Il y a eu une erreur pendant le traitement du document.
Ceci vient probablement d'une erreur de syntaxe ; si vous êtes absolument
certain du contraire, merci de signaler le problème.

Voici la sortie de la commande :

                """
            )) + tex.traiter_erreur_compilation(self.dossiertmp))

    def exporter(self, fmt):
        """Export vers d'autres formats
        """
        return self.fmt[fmt]

    def pdf(self, chemin=False, indice=''):
        """Format pdf
        """
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
                < os.path.getmtime(self._fichier())
        ):
            self.preparer_pdf(fichierpdf)
        return url(fichierpdf)

    def gabc(self, fmt, chemin=False, indice=''):
        """Format gabc
        """
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
        with open(self._fichier(), 'r') as fch:
            gabc = Gabc(fch.read(-1))
            partition = Partition(
                gabc=gabc.partition,
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
