# coding: utf-8
"""Gestion des fichiers MarkDown

Le langage MarkDown est géré ici par le module mistune pour la traduction en
html, par pandoc pour les exports ; d'où dépendance sur ce dernier.

Voyez pour la syntaxe :
http://fr.wikipedia.org/wiki/Markdown
"""
import os
import shutil
from sys import stderr
from . import txt
from etc import config as cfg
from deps.outils import copytree, url, traiter_erreur, _


class Document(txt.Document):
    """Document markdown
    """
    def __init__(self, chemin, proprietes=None):
        proprietes_papier = {
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
            })
        }
        proprietes_tex = {
            'police': (_("Police"), {
                'police_famille':
                    (_("Nom"), 'libertine'),
                'police_taille':
                    (_("Taille de la police"), '12pt'),
            })
        }
        proprietes_tex.update(proprietes_papier)
        txt.Document.__init__(
            self, chemin,
            # Liste des formats, avec :
            # - la méthode permettant de les créér ;
            # - les propriétés nécessaires à cette création ;
            # - l'intitulé correspondant à ces propriétés ;
            # - la valeur par défaut de ces propriétés.
            formats={
                'beamer': (self.beamer, {}),
                'docx': (self.docx, proprietes_papier),
                'epub': (self.epub, {}),
                'pdf': (self.pdf, proprietes_tex),
                'odt': (self.odt, proprietes_papier),
                'reveal.js': (self.revealjs, {'theme': (_("Thème"), 'black', (
                    'black', 'night', 'serif', 'simple', 'white',
                ))}),
                'rtf': (self.rtf, {}),
                'tex': (self.tex, proprietes_tex),
            },
            proprietes=proprietes
        )

    @property
    def obsolete(self):
        return self.est_obsolete(self._fichiersortie('html'))

    def afficher(self, actualiser=0):
        return self.html(actualiser=actualiser)

    def html(self, chemin='html', indice='', fmt=None, actualiser=2):
        """Format html
        """
        fichierhtml = self._fichiersortie('html', chemin=chemin, indice=indice)
        if self.doit_etre_actualise(fichierhtml, actualiser):
            self.preparer('html', fichierhtml, fmt)
        with fichierhtml.open() as doc:
            return doc.read()

    # pylint: disable=W0221
    def pdf(self, chemin='pdf', indice='', fmt=None, actualiser=2):
        """Format pdf
        """
        fichierpdf = self._fichiersortie('pdf', chemin=chemin, indice=indice)
        if self.doit_etre_actualise(fichierpdf, actualiser):
            self.preparer('pdf', fichierpdf, fmt=fmt)
        return url(fichierpdf)

    def docx(self, chemin='docx', indice='', fmt=None, actualiser=2):
        """Format docx
        """
        fichierdocx = self._fichiersortie('docx', chemin=chemin, indice=indice)
        if self.doit_etre_actualise(fichierdocx, actualiser):
            self.preparer('docx', fichierdocx, fmt)
        return url(fichierdocx)

    def epub(self, chemin='epub', indice='', fmt=None, actualiser=2):
        """Format epub
        """
        fichierepub = self._fichiersortie('epub', chemin=chemin, indice=indice)
        if self.doit_etre_actualise(fichierepub, actualiser):
            self.preparer('epub', fichierepub, fmt)
        return url(fichierepub)

    def odt(self, chemin='odt', indice='', fmt=None, actualiser=2):
        """Format odt
        """
        fichierodt = self._fichiersortie('odt', chemin=chemin, indice=indice)
        if self.doit_etre_actualise(fichierodt, actualiser):
            self.preparer('odt', fichierodt, fmt)
        return url(fichierodt)

    def rtf(self, chemin='rtf', indice='', fmt=None, actualiser=2):
        """Format rtf
        """
        fichierrtf = self._fichiersortie('rtf', chemin=chemin, indice=indice)
        if self.doit_etre_actualise(fichierrtf, actualiser):
            self.preparer('rtf', fichierrtf, fmt)
        return url(fichierrtf)

    def tex(self, chemin='tex', indice='', fmt=None, actualiser=2):
        """Format tex
        """
        fichiertex = self._fichiersortie('tex', chemin=chemin, indice=indice)
        if self.doit_etre_actualise(fichiertex, actualiser):
            self.preparer('tex', fichiertex, fmt)
        return url(fichiertex)

    def beamer(self, chemin=False, indice='', actualiser=2):
        """Format beamer

        Format pdf pour les présentations.
        """
        return self.pdf(
            chemin=chemin, indice=indice, fmt='beamer', actualiser=actualiser
        )

    def revealjs(self, chemin=False, indice='', actualiser=2):
        """Format reveal.js

        Format html5 pour les présentations.
        """
        chemin = chemin if chemin else 'rj'
        fichierhtml = self._fichiersortie('html', chemin=chemin, indice=indice)
        if self.doit_etre_actualise(fichierhtml, actualiser):
            self.preparer('html', fichierhtml, fmt='revealjs')
        return url(fichierhtml)

    def preparer(self, ext='pdf', destination=False, fmt=None):
        """Préparation des divers formats

        C'est ici que l'on appelle la commande pandoc en vue des divers
        exports possibles
        """
        orig = self._fichiertmp(ext)
        dest = destination if destination else self._fichier(ext)
        copytree(self.dossier, self.dossiertmp, ignore=('.git',))
        arguments = [
            '--filter=' +
            str(cfg.PWD / 'deps' / 'pandoc' / 'gabc.py'),
            '--filter=' +
            str(cfg.PWD / 'deps' / 'pandoc' / 'lilypond.py'),
        ]
        if ext in ('tex', 'pdf'):
            arguments += [
                '--latex-engine=lualatex',
                '--variable=fontfamily:' +
                self.proprietes[ext]['police_famille'],
                '--variable=fontsize:' +
                self.proprietes[ext]['police_taille'],
                '--variable=papersize:' +
                self.proprietes[ext]['ba_papier'] +
                'paper',
                "--variable=geometry:top=" +
                self.proprietes[ext]['marge'][0],
                "--variable=geometry:bottom=" +
                self.proprietes[ext]['marge'][1],
                "--variable=geometry:left=" +
                self.proprietes[ext]['marge'][2],
                "--variable=geometry:right=" +
                self.proprietes[ext]['marge'][3],
                '--variable=include-before:' +
                '\\widowpenalty=10000\\clubpenalty=10000',
            ]
            if not self.proprietes[ext]['page_numero']:
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
            if fmt == 'revealjs':
                arguments += [
                    '-i',
                    '-c',
                    str(
                        cfg.PANDOC / 'reveal.js' / 'css' / 'theme' /
                        (self.proprietes['reveal.js']['theme'] + '.css')
                    ),
                    '--variable=revealjs-url:' + str(cfg.PANDOC / 'reveal.js'),
                ]
        pandoc(
            self._fichiertmp(),
            destination=orig,
            fmt=fmt,
            arguments=arguments
        )
        try:
            dest.parent.mkdir(parents=True)
        except FileExistsError as err:
            traiter_erreur(err)
        orig.replace(dest)


def pandoc(fichier, destination, fmt=None, arguments=None):
    """Méthode appelant la commande pandoc
    """
    try:
        os.chdir(str(fichier.parent))
        commande = [
            'pandoc',
            '-S',
            '-s',
            '--data-dir', str(cfg.PANDOC),
            '--self-contained',
            '--variable=lang:' + {'fr': 'french', 'en': 'english'}[cfg.LANGUE],
            '-o', str(destination)
        ]
        if fmt:
            commande = commande + ['-t', fmt]
        if arguments:
            commande = commande + arguments
        commande.append(str(fichier))
        if cfg.DEVEL:
            stderr.write(' '.join(commande) + '\n\n')
        environnement = os.environ.copy()
        environnement['shell_escape_commands'] = (
            "bibtex,bibtex8,kpsewhich,makeindex,mpost,repstopdf,"
            "gregorio,lilypond"
        )
        environnement['TEXINPUTS'] = ("lib:")
        try:
            compiler(commande, fichier, environnement)
        except ErreurCompilation as err:
            traiter_erreur(err)
            raise
    finally:
        os.chdir(str(cfg.PWD))

compiler = txt.compiler  # pylint: disable=C0103


FichierIllisible = txt.FichierIllisible


ErreurCompilation = txt.ErreurCompilation
