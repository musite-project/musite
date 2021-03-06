# coding: utf-8
"""Gestion des partitions ly

Ces partitions nécessitent LilyPond.

Voir plus d'informations à l'adresse :
http://www.lilypond.org
"""
import os
import shutil
import re
from deps.outils import Path, copytree, templateperso, \
    traiter_erreur, liste_polices, url, _
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
                            (_("Roman"), 'Linux Libertine O', liste_polices),
                        'police_b_sans':
                            (_("Sans"), 'Linux Biolinum O', liste_polices),
                        'police_c_mono':
                            (
                                _("Mono"),
                                'Linux Libertine Mono O',
                                liste_polices
                            ),
                        'police_taille':
                            (_("Taille"), 12),
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

    @property
    def obsolete(self):
        return self.est_obsolete(self._fichiersortie('pdf'))

    def afficher(self, actualiser=2):
        return self.afficher_pdf(
            actualiser=actualiser,
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
        if fichiermidi.is_file():
            return url(fichiermidi)

    def preparer_pdf(self, destination=None, environnement=None):
        """Mise en place du pdf
        """
        orig = self._fichiertmp('pdf')
        origmidi = self._fichiertmp('midi')
        dest = destination if destination else self._fichier('pdf')
        destmidi = Path(
            destination.as_posix().replace('/pdf/', '/midi/')
        ).with_suffix('.midi') if destination else self._fichier('midi')
        try:
            dest.parent.mkdir(parents=True)
        except FileExistsError as err:
            traiter_erreur(err)
        copytree(self.dossier, self.dossiertmp, ignore=('.git',))
        with self._fichiertmp().open('w') as tmp:
            contenu = self.contenu
            entetes = re.findall(r'\\header{[^}]*}', contenu)
            entetes = entetes[0] if len(entetes) else ''
            papier = re.findall(r'\\paper{[^}]*}', contenu)
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
        try:
            dest.parent.mkdir(parents=True)
        except FileExistsError as err:
            traiter_erreur(err)
        try:
            destmidi.parent.mkdir(parents=True)
        except FileExistsError as err:
            traiter_erreur(err)
        orig.replace(dest)
        origmidi.replace(destmidi)

    @property
    def titre(self):
        """Retourne le titre de la partition
        """
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
        str(fichier)
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
    return txt.Document(str(dossier) + '/log').afficher()


FichierIllisible = txt.FichierIllisible


ErreurCompilation = txt.ErreurCompilation
