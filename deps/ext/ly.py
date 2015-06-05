# coding: utf-8
"""Gestion des partitions ly

Ces partitions nécessitent LilyPond.

Voir plus d'informations à l'adresse :
http://www.lilypond.org
"""
import os
import shutil
import re
from deps.outils import templateperso, traiter_erreur, url, _
from etc import config as cfg
from . import txt

TEMPLATELY = templateperso()


class Document(txt.Document):
    """Document lilypond
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
                'pdf': (self.pdf, {
                    'document': (_("Document"), {
                        'ba_papier':
                            (_("Taille de la page"), 'a4'),
                        'marge':
                            (
                                _("Marges (haut, bas, gauche, droite)"),
                                ('25mm', '35mm', '25mm', '25mm')
                            ),
                        'aa_titre': (_("Titre"), ''),
                    }),
                    'police': (_("Police"), {
                        'police_a_roman':
                            (_("Roman"), 'Linux Libertine O'),
                        'police_b_sans':
                            (_("Sans"), 'Linux Biolinum O'),
                        'police_c_mono':
                            (_("Mono"), 'Linux Libertine Mono O'),
                    }),
                    'portee': (_("Portées"), {
                        'portee_taille': (_('Taille'), 20)
                    }),
                }),
                'midi': (self.midi, {})
            },
            proprietes=proprietes
        )
        if not proprietes:
            self.proprietes['pdf'] = self._traiter_options(
                'pdf', self.proprietes_detail['pdf'], {'aa_titre': self.titre}
            )

    def afficher(self):
        return self.afficher_pdf(
            message_erreur=_("""
Il est aussi possible que vous ayez saisi du code *Scheme* dans votre
document : par souci de sécurité, `Lilypond` est lancé avec des options plus
restrictives, qui rendent impossibles certaines opérations.
""")
        )

    def midi(self, chemin=None, indice=''):
        """Format midi
        """
        chemin = chemin if chemin else 'midi'
        fichiermidi = self._fichiersortie('midi', chemin=chemin, indice=indice)
        # Sous lilypond, le fichier midi est produit en même temps que le pdf,
        # à condition qu'il y ait une instruction \midi() dans le bloc \score.
        contenu = self.contenu
        if '\\midi{' not in contenu:
            self.enregistrer(
                contenu.replace('\\layout{', '\\midi{} \\layout{')
            )
        try:
            assert self.pdf(chemin=chemin, indice=indice)
        except ErreurCompilation as err:
            traiter_erreur(err)
        if os.path.isfile(fichiermidi):
            return url(fichiermidi)

    def preparer_pdf(self, destination=None, environnement=None):
        """Mise en place du pdf
        """
        orig = self._fichiertmp('pdf')
        origmidi = self._fichiertmp('midi')
        dest = destination if destination else self._fichier('pdf')
        destmidi = destination\
            .replace('/pdf/', '/midi/')\
            .replace('.pdf', '.midi')\
            if destination else self._fichier('midi')
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.rmtree(self.rnd, ignore_errors=True)
        shutil.copytree(
            self.dossier, self.dossiertmp, symlinks=True,
            ignore=lambda x, y: '.git'
        )
        with open(self._fichiertmp(), 'w') as tmp:
            contenu = self.contenu
            entetes = re.findall('\\\header{[^}]*}', contenu)
            entetes = entetes[0] if len(entetes) else ''
            papier = re.findall('\\\paper{[^}]*}', contenu)
            papier = papier[0] if len(papier) else ''
            entetes = (
                entete for entete in entetes.split('\n')[1:-1]
                if 'title' not in entete
            )
            papier = (
                reglage for reglage in papier.split('\n')[1:-1]
                if 'paper-size' not in papier
            )
            tmp.write(TEMPLATELY(
                'lily',
                {
                    'contenu':      contenu,
                    'entetes':      entetes,
                    'papier':       papier,
                    'proprietes':   self.proprietes['pdf'],
                },
            ))
        compiler_pdf(self._fichiertmp(), environnement)
        os.renames(orig, dest)
        os.renames(origmidi, destmidi)
        if not cfg.DEVEL:
            shutil.rmtree(self.rnd, ignore_errors=True)

    @property
    def titre(self):
        contenu = self.contenu
        entete = re.findall('header{[^}]*}', contenu)
        entete = entete[0] if len(entete) else ''
        titre = re.findall('title.*', entete)
        titre = titre[0] if len(titre) else None
        return re.sub('^\\s+|"', '', titre.split('=')[1]) if titre else ''


def compiler_pdf(fichier, environnement=None):
    """Compilation en pdf
    """
    commande = [
        'lilypond',
        fichier
    ]
    environnement = dict(
        os.environ,
        **environnement if environnement else {}
    )
    compiler(commande, fichier, environnement)


compiler = txt.compiler  # pylint: disable=C0103


def traiter_erreur_compilation(dossier):
    """Réaction en cas d'erreur de compilation
    """
    return txt.Document(dossier.replace(os.path.sep, '/') + '/log').afficher()


FichierIllisible = txt.FichierIllisible


ErreurCompilation = txt.ErreurCompilation
