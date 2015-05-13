# coding: utf-8
"""Gestion des fichiers MarkDown

Le langage MarkDown est géré ici par le module mistune, intégré au programme :
il n'y a donc pas de dépendance externe particulière.

Voyez pour la syntaxe :
http://fr.wikipedia.org/wiki/Markdown
"""
import os
import shutil
import subprocess as sp
from mistune import markdown
import ext.txt as txt
from etc import config as cfg
from outils import url, _
from deps.i18n import i18n_path
import jrnl as l
EXT = __name__.split('.')[-1]


class Document(txt.Document):
    def __init__(self, chemin, ext=EXT, proprietes=None):
        txt.Document.__init__(self, chemin, ext)

        # Formats d'export possibles, avec la méthode renvoyant le document
        # compilé dans chaque format.
        self.fmt = {
            'pdf':  self.pdf,
            'reveal.js': self.revealjs,
            'beamer': self.beamer,
            }

        # Propriétés du document
        # self.listeproprietes contient la liste des propriétés, avec leur
        # description et leur valeur par défaut.
        # self.proprietes contient les propriétés définies par l'utilisateur,
        # ou à défaut les valeurs par défaut.
        self.listeproprietes = {}
        self.proprietes = {}
        for fmt in self.fmt:
            self.listeproprietes[fmt] = {}
        self.listeproprietes['pdf'] = {
            'papier':               (_("Taille de la page"), 'a4'),
            'taillepolice':         (_("Taille de la police"), '12'),
        }
        self.listeproprietes['reveal.js'] = {
            'theme':                (_("Thème"), 'white')
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
        return markdown(self.contenu)

    def exporter(self, fmt):
        return self.fmt[fmt]

    def pdf(self, chemin=False, indice='', fmt=None):
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
            self.preparer('pdf', fichierpdf, fmt)
        return url(fichierpdf)

    def beamer(self, chemin=False, indice=''):
        return self.pdf(chemin=chemin, indice=indice, fmt='beamer')

    def revealjs(self, chemin=False, indice=''):
        chemin = chemin if chemin else 'rj'
        fichierhtml = self._fichier('html')
        cheminhtml = self._chemin('html')
        if chemin:
            fichierhtml = fichierhtml.replace(
                '/html/',
                '/{}/{}/'.format(chemin, indice).replace('//', '/')
            )
            cheminhtml = cheminhtml.replace(
                '/html/',
                '/{}/{}/'.format(chemin, indice).replace('//', '/')
            )
        if (
            not os.path.isfile(fichierhtml)
            or os.path.getmtime(fichierhtml)
                < os.path.getmtime(self.fichier)
        ):
            self.preparer('html', fichierhtml, fmt='revealjs')
        return url(fichierhtml)

    def preparer(self, ext='pdf', destination=False, fmt=None):
        orig = self._fichiertmp(ext)
        dest = destination if destination else self._fichier(ext)
        shutil.rmtree(self.rd, ignore_errors=True)
        shutil.copytree(self.dossier, self.dossiertmp, symlinks=True)
        arguments = []
        if ext == 'pdf':
            arguments = [
                '--variable=fontsize:' + self.proprietes['pdf']['taillepolice'],
                '--variable=papersize:'
                + self.proprietes['pdf']['papier']
                + 'paper',
            ]
        if ext == 'html':
            arguments = ['-c',
                'reveal.js/css/theme/{}.css'.format(
                    self.proprietes['reveal.js']['theme']
            )]
            if fmt == 'revealjs':
                arguments += ['-i',]
        pandoc(self.fichiertmp, destination=orig, fmt=fmt, arguments=arguments)
        os.renames(orig, dest)
        if not cfg.DEVEL:
            shutil.rmtree(self.rd, ignore_errors=True)


def pandoc(fichier, destination, fmt=None, arguments=[]):
    try:
        os.chdir(os.path.dirname(fichier))
        commande = [
            'pandoc',
            '-S',
            '-s',
            '--data-dir', cfg.PANDOC,
            '--self-contained',
            '--variable=lang:' + {'fr':'french', 'en':'english'}[cfg.LANGUE],
            '-o', destination
        ]
        if fmt:
            commande = commande + ['-t', fmt]
        if arguments:
            commande = commande + arguments
        commande.append(fichier)
        if cfg.DEVEL:
            print(commande)
        environnement = os.environ
        if cfg.DEVEL:
            print(environnement)
        compilation = sp.Popen(
            commande,
            env=environnement,
            stdout=sp.PIPE,
            stderr=sp.PIPE
        )
        sortie, erreurs = compilation.communicate()
        try:
            l.log(
                _('Sortie :')
                + '\n========\n'
                + '\n{}\n\n\n\n'.format(sortie.decode('utf8'))
                + '−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−\n\n\n\n'
                + _('Erreurs :')
                + '\n=========\n'
                + '\n{}\n'.format(erreurs.decode('utf8'))
            )
        except UnicodeDecodeError:
            raise FichierIllisible
        if compilation.returncode:
            print(erreurs)
            raise ErreurCompilation
    finally:
        os.chdir(cfg.PWD)

FichierIllisible = txt.FichierIllisible

class ErreurCompilation(Exception):
    pass

