# coding: utf-8
"""Gestion des fichiers MarkDown

Le langage MarkDown est géré ici par le module mistune pour la traduction en
html, par pandoc pour les exports ; d'où dépendance sur ce dernier.

Voyez pour la syntaxe :
http://fr.wikipedia.org/wiki/Markdown
"""
import os
import shutil
from deps.mistune import markdown
from . import txt
from etc import config as cfg
from deps.outils import url, traiter_erreur, _


class Document(txt.Document):
    """Document markdown
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
                        'page_numero':
                            (_("Numéros de page"), True),
                    }),
                    'police': (_("Police"), {
                        'police_famille':
                            (_("Nom"), 'libertine'),
                        'police_taille':
                            (_("Taille de la police"), '12pt'),
                    })
                }),
                'reveal.js': (self.revealjs, {
                    'theme':            (_("Thème"), 'black')
                }),
                'beamer': (self.beamer, {}),
            },
            proprietes=proprietes
        )

    def afficher(self):
        return markdown(self.contenu)

    def pdf(self, chemin='pdf', indice='', fmt=None):  # pylint: disable=W0221
        """Format pdf
        """
        fichierpdf = self._fichiersortie('pdf', chemin=chemin, indice=indice)
        if (
                not os.path.isfile(fichierpdf)
                or os.path.getmtime(fichierpdf)
                < os.path.getmtime(self._fichier())
        ):
            self.preparer('pdf', fichierpdf, fmt)
        return url(fichierpdf)

    def beamer(self, chemin=False, indice=''):
        """Format beamer

        Format pdf pour les présentations.
        """
        return self.pdf(chemin=chemin, indice=indice, fmt='beamer')

    def revealjs(self, chemin=False, indice=''):
        """Format reveal.js

        Format html5 pour les présentations.
        """
        chemin = chemin if chemin else 'rj'
        fichierhtml = self._fichiersortie('html', chemin=chemin, indice=indice)
        if (
                not os.path.isfile(fichierhtml)
                or os.path.getmtime(fichierhtml)
                < os.path.getmtime(self._fichier())
        ):
            self.preparer('html', fichierhtml, fmt='revealjs')
        return url(fichierhtml)

    def preparer(self, ext='pdf', destination=False, fmt=None):
        """Préparation des divers formats

        C'est ici que l'on appelle la commande pandoc en vue des divers
        exports possibles
        """
        orig = self._fichiertmp(ext)
        dest = destination if destination else self._fichier(ext)
        shutil.rmtree(self.rnd, ignore_errors=True)
        shutil.copytree(self.dossier, self.dossiertmp, symlinks=True)
        arguments = []
        if ext == 'pdf':
            arguments = [
                '--latex-engine=lualatex',
                '--variable=fontfamily:' +
                self.proprietes['pdf']['police_famille'],
                '--variable=fontsize:' +
                self.proprietes['pdf']['police_taille'],
                '--variable=papersize:' +
                self.proprietes['pdf']['ba_papier'] +
                'paper',
                "--variable=geometry:top=" +
                self.proprietes['pdf']['marge'][0],
                "--variable=geometry:bottom=" +
                self.proprietes['pdf']['marge'][1],
                "--variable=geometry:left=" +
                self.proprietes['pdf']['marge'][2],
                "--variable=geometry:right=" +
                self.proprietes['pdf']['marge'][3],
                '--variable=include-before:' +
                '\\widowpenalty=10000\\clubpenalty=10000',
            ]
            if not self.proprietes['pdf']['page_numero']:
                arguments.append(
                    '--variable=header-includes:' +
                    "\\pagestyle{empty}"
                )
                arguments.append(
                    '--variable=include-before:' +
                    "\\thispagestyle{empty}"
                )
            if fmt != 'beamer':
                arguments.append('--variable=documentclass:scrartcl')
        if ext == 'html':
            arguments = []
            if fmt == 'revealjs':
                arguments = [
                    '-i',
                    '-c',
                    os.path.join(
                        cfg.PANDOC,
                        'reveal.js',
                        'css',
                        'theme',
                        self.proprietes['reveal.js']['theme'] + '.css'
                    ),
                    '--variable=revealjs-url:' + os.path.join(
                        cfg.PANDOC,
                        'reveal.js'
                    ),
                ]
        pandoc(
            self._fichiertmp(),
            destination=orig,
            fmt=fmt,
            arguments=arguments
        )
        os.renames(orig, dest)
        if not cfg.DEVEL:
            shutil.rmtree(self.rnd, ignore_errors=True)


def pandoc(fichier, destination, fmt=None, arguments=None):
    """Méthode appelant la commande pandoc
    """
    os.chdir(os.path.dirname(fichier))
    commande = [
        'pandoc',
        '-S',
        '-s',
        '--data-dir', cfg.PANDOC,
        '--self-contained',
        '--variable=lang:' + {'fr': 'french', 'en': 'english'}[cfg.LANGUE],
        '-o', destination
    ]
    if fmt:
        commande = commande + ['-t', fmt]
    if arguments:
        commande = commande + arguments
    commande.append(fichier)
    try:
        compiler(commande, fichier, os.environ)
    except ErreurCompilation as err:
        traiter_erreur(err)
        raise

compiler = txt.compiler  # pylint: disable=C0103


FichierIllisible = txt.FichierIllisible


ErreurCompilation = txt.ErreurCompilation
