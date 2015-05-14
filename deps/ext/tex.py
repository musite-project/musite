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
from deps.outils import url, _
import os
import shutil
import subprocess as sp
import re
from deps import HTMLTags as h
from deps.mistune import markdown
from deps import jrnl as l
EXT = __name__.split('.')[-1]


class Document(txt.Document):
    """Document tex
    """
    def __init__(self, chemin, ext=EXT):
        txt.Document.__init__(self, chemin, ext)

    def afficher(self):
        def documentmaitre():
            """Test pour savoir s'il s'agit d'un document maître
            """
            entete = re.compile('\\\\documentclass')
            with open(self.fichier) as doc:
                for ligne in doc:
                    if entete.match(ligne):
                        return True
            return False
        if documentmaitre():
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
                    )) + traiter_erreur_compilation(self. dossiertmp))
        else:
            return txt.Document.afficher(self)

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
                not os.path.isfile(self._fichier('pdf'))
                or os.path.getmtime(self._fichier('pdf'))
                < os.path.getmtime(self.fichier)
        ):
            self.preparer_pdf()
        return url(fichierpdf)

    def preparer_pdf(
            self, destination=False,
            environnement=None
    ):
        """Mise en place du pdf
        """
        environnement = \
            environnement if environnement else {'TEXINPUTS': 'lib:'}
        orig = self._fichiertmp('pdf')
        dest = destination if destination else self._fichier('pdf')
        shutil.rmtree(self.rd, ignore_errors=True)
        shutil.copytree(self.dossier, self.dossiertmp, symlinks=True)
        compiler_pdf(self.fichiertmp, environnement)
        os.renames(orig, dest)
        if not cfg.DEVEL:
            shutil.rmtree(self.rd, ignore_errors=True)


def compiler_pdf(fichier, environnement=None):
    """Compilation en pdf
    """
    environnement = environnement if environnement else {'TEXINPUTS': 'lib:'}
    try:
        os.chdir(os.path.dirname(fichier))
        commande = [
            'lualatex',
            '-interaction=nonstopmode',
            '-shell-restricted',
            fichier
        ]
        environnement = dict(os.environ, **environnement)
        environnement['shell_escape_commands'] = (
            "bibtex,bibtex8,kpsewhich,makeindex,mpost,repstopdf,"
            "gregorio,lilypond"
        )
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
            raise ErreurCompilation
        if os.path.exists(os.path.splitext(fichier)[0] + '.toc'):
            if cfg.DEVEL:
                print('Table des matières : 2e compilation')
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
                    + '−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−\n\n\n\n'
                    + _('Erreurs :')
                    + '\n=========\n'
                    + '\n{}\n'.format(erreurs.decode('utf8'))
                )
            except UnicodeDecodeError:
                raise FichierIllisible
            if compilation.returncode:
                raise ErreurCompilation
    finally:
        os.chdir(cfg.PWD)


def traiter_erreur_compilation(dossier):
    """Réaction en cas d'erreur de compilation
    """
    return txt.Document(dossier.replace(os.path.sep, '/') + '/log').afficher()


FichierIllisible = txt.FichierIllisible


class ErreurCompilation(Exception):
    """Exception levée en cas d'erreur de compilation
    """
    pass
