# coding: utf-8
"""Gestion des documents tex

Ces documents nécessitent TeXLive (ou équivalent) avec un ensemble raisonnable
d'extensions.

Pour la documentation, google est votre ami…
Les pages de M. Pégourié-Gonnard peuvent être de quelque utilité pour un bon
point de départ :
https://elzevir.fr/imj/latex/
"""
from . import txt as txt
from etc import config as cfg
import os
import shutil
import re
from deps.outils import copytree, traiter_erreur, templateperso, _

TEMPLATETEX = templateperso()


class Document(txt.Document):
    """Document tex
    """
    def __init__(self, chemin, proprietes=None):
        txt.Document.__init__(
            self, chemin,
            formats={
                'pdf': (self.pdf, {
                    'aa_perso': (_("Personnaliser la mise en page"), False),
                    'document': (_("Document"), {
                        'ba_papier':
                            (
                                _("Taille de la page (largeur, hauteur)"),
                                '210mm, 297mm'
                            ),
                        'marge':
                            (
                                _("Marges (haut, bas, gauche, droite)"),
                                ('25mm', '35mm', '25mm', '25mm')
                            ),
                        'page_numero':
                            (_("Numéros de page"), True),
                    }),
                    'police': (_("Police"), {
                        'police_famille':
                            (_("Nom"), 'libertine'),
                        'police_taille':
                            (_("Taille de la police"), '12'),
                    }),
                }),
            },
            proprietes=proprietes
        )

    @property
    def _documentmaitre(self):
        """Test pour savoir s'il s'agit d'un document maître
        """
        entete = re.compile('\\\\documentclass|\\\\begin{document}')
        with self._fichier().open() as doc:
            for ligne in doc:
                if entete.match(ligne):
                    return True
        return False

    @property
    def obsolete(self):
        return self.est_obsolete(self._fichiersortie('pdf'))

    def afficher(self, actualiser=0):
        if self._documentmaitre:
            return self.afficher_pdf(actualiser=actualiser)
        else:
            return txt.Document.afficher(self, actualiser=actualiser)

    def pdf(self, chemin=None, indice='', actualiser=0):
        """Format pdf

        Pour les documents latex, on désactive l'actualisation automatique,
        pour les raisons suivantes :

        - la compilation peut être longue, et l'utilisateur n'a pas forcément
          envie de la recommencer à chaque modification de détail ;
        - la compilation peut être rendue nécessaire par la modification d'un
          autre document que le document maître, ce que ne détecte pas la
          compilation automatique.
        """
        return txt.Document.pdf(
            self, chemin=chemin, indice=indice, actualiser=actualiser
        )

    def preparer_pdf(self, destination=False, environnement=None):
        """Mise en place du pdf
        """
        environnement = \
            environnement if environnement else {'TEXINPUTS': 'lib:'}
        orig = self._fichiertmp('pdf')
        dest = destination if destination else self._fichier('pdf')
        try:
            dest.parent.mkdir(parents=True)
        except FileExistsError as err:
            traiter_erreur(err)
        copytree(self.dossier, self.dossiertmp, ignore=('.git',))
        if self.proprietes['pdf']['aa_perso']:
            with self._fichiertmp().open('w') as doc:
                doc.write(re.sub(
                    r'fontsize=\d*',
                    'fontsize={}'.format(
                        self.proprietes['pdf']['police_taille']
                    ),
                    self.contenu.replace(
                        "\\begin{document}",
                        TEMPLATETEX(
                            'entete',
                            proprietes=self.proprietes['pdf']
                        ) +
                        "\n\\begin{document}"
                    )
                ))
        compiler_pdf(self._fichiertmp(), environnement)
        try:
            dest.parent.mkdir(parents=True)
        except FileExistsError as err:
            traiter_erreur(err)
        orig.replace(dest)


def compiler_pdf(fichier, environnement=None):
    """Compilation en pdf
    """
    environnement = environnement if environnement else {'TEXINPUTS': 'lib:'}
    commande = [
        'lualatex',
        '-interaction=nonstopmode',
        '-shell-restricted',
        str(fichier)
    ]
    environnement = dict(os.environ, **environnement)
    environnement['shell_escape_commands'] = (
        "bibtex,bibtex8,kpsewhich,makeindex,mpost,repstopdf,"
        "gregorio,lilypond"
    )
    compiler(commande, fichier, environnement)
    if fichier.with_suffix('.toc').exists():
        if cfg.DEVEL:
            print('Table des matières : 2e compilation')
        compiler(commande, fichier, environnement)


compiler = txt.compiler  # pylint: disable=C0103

# pylint: disable=C0103
traiter_erreur_compilation = txt.traiter_erreur_compilation

FichierIllisible = txt.FichierIllisible

ErreurCompilation = txt.ErreurCompilation
