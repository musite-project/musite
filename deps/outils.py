# coding: utf-8
"""Gestion des fichiers, dossiers et dépôts

Si j'ai bien compris ce qu'est un modèle dans le modèle MVC, ce doit être
à peu près ça.
Vous trouverez aussi à la fin des méthodes un peu "inclassables", mais utiles
en plusieurs points du programme.
"""
import os
import re
from sys import stderr
from pathlib import Path
from sre_constants import error as ReError
import shutil
import traceback
from time import time
import subprocess
from glob import glob as ls
import random as rd
from string import ascii_lowercase
import unicodedata as ud
import functools
from matplotlib import font_manager
from .bottle import SimpleTemplate, template
from etc import config as cfg
from .i18n import lazy_gettext as _, i18n_path

# Ce qui suit vise à éviter la tentation de supprimer l'import de i18n_path :
# en effet, les autres modules l'importent depuis celui-ci, afin de centraliser
# tout cela et de permettre le cas échéant de redéfinir cette méthode.
assert i18n_path


# Liste des polices du système
liste_polices = sorted(set(
    font_manager.FontProperties(fname=fname).get_name()
    for fname in font_manager.get_fontconfig_fonts()
))


def copytree(orig, dest, overwrite='u', ignore=None):
    """Copie récursive d'un dossier vers un emplacement donné

    overwrite peut prendre les valeurs :

    - False : aucun écrasement de fichiers ;
    - 'u' : écrasement si l'origine est plus récente que la destination ;
    - 'c' : écrasement systématique.
    """
    orig = Path(orig)
    dest = Path(dest)
    ignore = ignore if ignore else tuple()
    for dossier, sousdossiers, fichiers in os.walk(str(orig)):
        print(dossier, sousdossiers, fichiers)
        pdir = Path(dossier)
        if pdir.name not in ignore:
            dirpath = pdir.relative_to(orig)
            try:
                (dest / dirpath).mkdir(parents=True)
            except FileExistsError as err:
                traiter_erreur(err)
                if not overwrite:
                    raise
            for fichier in fichiers:
                path = dirpath / fichier
                if (
                        not (dest / path).exists()
                        or overwrite == 'c'
                        or (
                            overwrite == 'u' and
                            (dest / path).stat().st_mtime <
                            (orig / path).stat().st_mtime
                        )
                ):
                    shutil.copy(str(orig / path), str(dest / path))
            for ign in ignore:
                if ign in sousdossiers:
                    sousdossiers.remove(ign)


class Depot():
    """Gestion du dépôt

    C'est ici qu'ont lieu les clonages, commits et autres reverts de cet outil
    magique qu'est git.
    """
    def __init__(self, dossier):
        self.dossier = dossier

    def annuler(self, version, auteur=None):
        """Revenir sur un commit donné
        """
        self.commande([
            'revert',
            '-n',
            version
        ])
        self.sauvegardecomplete(
            'Annulation des changements de la version '
            + version,
            auteur
        )

    def cloner(self, depot):
        """Cloner un dépôt distant

        On n'utilise pas la méthode commande, car le dossier n'existe pas
        encore !
        """
        cmd = ['git', 'clone', depot, str(self.dossier)]
        try:
            resultat = subprocess.check_output(cmd)
        except subprocess.CalledProcessError as err:
            if cfg.DEVEL:
                traiter_erreur(err)
                print(err.output)
            raise
        return resultat.decode('utf-8')

    def commande(self, arguments):
        """Commande sur un dépôt existant
        """
        os.chdir(str(self.dossier))
        ligne = ['git']
        ligne.extend(arguments)
        try:
            resultat = subprocess.check_output(ligne, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            traiter_erreur(err)
            if cfg.DEVEL:
                print(err.returncode, err.output)
            raise GitError(err)
        return resultat.decode('utf-8')

    def comparer(self, version, versionb=None, fichier=None):
        """Comparer deux versions

        Si la deuxième version n'est pas donnée, la version précédant
        la première est automatiquement choisie.
        """
        if versionb:
            parametres = [
                'diff',
                '--word-diff-regex=.??',
                version,
                versionb
            ]
        else:
            parametres = [
                'diff',
                '--word-diff-regex=.??',
                version + '^',
                version
            ]
        if fichier:
            parametres.append(str(fichier))
        return self.commande(parametres).replace('\r', '').split('\n')

    @property
    def etat(self):
        """Retourne l'état du dépôt
        """
        return self.commande(['status', '-s'])

    def initialiser(self):
        """Initialisation du dépôt
        """
        self.commande(['init'])

    def journal(self, arguments=None):
        """Journal des modifications

        Méthode générale.
        """
        ligne = ['log', '--no-merges']
        ligne.extend(arguments if arguments else [])
        return self.commande(ligne)

    @property
    def journalcomplet(self):
        """Journal de l'ensemble des modifications
        """
        entete = [['Id', 'auteur', 'date', 'message']]
        historique = [
            re.sub('Author: |Date: | {2,4}', '', entree).split('\n')[0:5]
            for entree in self.journal().split('commit ')
        ][1:]
        for element in historique:
            element[0] = element[0][:7]
            if len(element) > 3:
                element.pop(3)
        return entete + historique

    def journalfichier(self, fichier):
        """Journal d'un fichier isolé
        """
        entete = [['Id', 'auteur', 'date', 'message']]
        historique = [
            re.sub('Author: |Date: | {2,4}', '', entree).split('\n')[0:5]
            for entree
            in self.journal(['--follow', str(fichier)]).split('commit ')
        ][1:]
        for element in historique:
            element[0] = element[0][:7]
            element.pop(3)
        return entete + historique

    @property
    def origine(self):
        """Adresse du dépôt depuis lequel celui-ci a été clôné
        """
        with Path(self.dossier / '.git' / 'config').open() as gitconfig:
            adresse = False
            for ligne in gitconfig:
                if adresse:
                    return ligne.split('url = ')[1][:-1]
                if '[remote "origin"]' in ligne:
                    adresse = True

    def pull(self, depot=None):
        """Récupérer les modifications depuis un dépôt distant
        """
        self.commande(['pull', depot if depot else self.origine])

    def push(self, depot=None, utilisateur=None, mdp=''):
        """Renvoyer les modifications locales vers un dépôt distant
        """
        depot = depot if depot else self.origine
        if utilisateur:
            depot = depot.replace('://', '://{}:{}@'.format(utilisateur, mdp))
        self.commande(['push', depot])

    def retablir(self, version, fichier=None, auteur=None):
        """Ramener le dépôt à une version donnée
        """
        if fichier:
            self.commande([
                'checkout',
                version,
                str(fichier)
            ])
        else:
            self.commande([
                'revert',
                '-n',
                version + '..HEAD'
            ])
        self.sauvegardecomplete(
            'Retour '
            + ('du fichier {} '.format(fichier.name) if fichier else '')
            + 'à la version '
            + version,
            auteur
        )

    def sauvegarde(self, chemin, message, auteur=None):
        """Actions de sauvegarde

        Méthode générique, appelée pour toutes les sauvegardes.
        """
        arguments = [
            'commit',
            '-m',
            message
        ]
        if auteur:
            arguments.append('--author="{0} <{0}>'.format(auteur))
        self.commande(['add', chemin])
        self.commande(arguments)

    def sauvegardecomplete(self, message=_("Sauvegarde complète"), auteur=None):
        """Sauvegarde de l'ensemble du dépôt
        """
        self.sauvegarde('-A', message, auteur)

    def sauvegardefichier(self, fichier, auteur=None):
        """Sauvegarde d'un fichier isolé
        """
        self.sauvegarde(
            str(fichier),
            fichier.name,
            auteur
        )


class Dossier():
    """Gestion des dossiers
    """
    def __init__(self, dossier):
        self.dossier = Path(dossier)
        if not self.dossier.is_dir():
            raise TypeError(dossier + _(" n'est pas un dossier"))

    def rechercher(self, expression, nom=True, contenu=True):
        """Recherche d'une expression dans le nom ou le contenu des documents
        """
        for dossier, sousdossiers, fichiers in os.walk(str(self.dossier)):
            if dossier[-4:] != '.git/':
                if nom and re.match(expression, dossier.split('/')[-1]):
                    yield dossier
                for fichier in fichiers:
                    document = os.path.join(dossier, fichier)
                    if nom and re.match(expression, fichier):
                        yield document
                    elif contenu:
                        with open(document, 'r') as doc:
                            try:
                                if re.search(expression, doc.read()):
                                    yield document
                            except UnicodeDecodeError as err:
                                traiter_erreur(err)
                                if cfg.DEVEL:
                                    print(document)
                            except ReError as err:
                                traiter_erreur(err)
                                raise ErreurExpression
                if '.git' in sousdossiers:
                    sousdossiers.remove('.git')


def nettoyertmp():
    """Nettoyage des fichiers temporaires"""
    if cfg.TMP.is_dir():
        for ancien in (
                fichier for fichier in cfg.TMP.iterdir()
                if (time() - fichier.stat().st_mtime)/3600 > 3
        ):
            if ancien.is_dir():
                shutil.rmtree(str(ancien))
            else:
                ancien.unlink()
    if (cfg.STATIC / 'tmp').is_dir():
        for ancien in (
                fichier for fichier in (cfg.STATIC / 'tmp').iterdir()
                if (time() - fichier.stat().st_mtime)/3600 > 3
        ):
            if ancien.is_dir():
                shutil.rmtree(str(ancien))
            else:
                ancien.unlink()
    if cfg.DOCS.is_dir():
        for ancien in (
                fichier for fichier in (cfg.DOCS).iterdir()
                if (time() - fichier.stat().st_mtime)/(86400) > 30
        ):
            if ancien.is_dir():
                shutil.rmtree(str(ancien))
            else:
                ancien.unlink()


def sansaccents(entree):
    """Retourne le texte en ôtant les accents
    """
    nkfd_form = ud.normalize('NFKD', entree)
    return "".join([c for c in nkfd_form if not ud.combining(c)])


def motaleatoire(longueur=6, source=ascii_lowercase):
    """Mot aléatoire, pour les fichiers temporaires notamment
    """
    return ''.join(rd.choice(source) for i in range(longueur))


def templateperso(syntaxe='<% %> % <<< >>>'):
    """Modification des délimiteurs dans les gabarits bottle
    """
    class Adaptateur(SimpleTemplate):
        """Classe décorateur
        """
        def __init__(self, syntax=syntaxe, *args, **settings):
            SimpleTemplate.__init__(self, syntax=syntax, *args, **settings)
    return functools.partial(template, template_adapter=Adaptateur)


def erreur(txt):
    """Affichage d'informations sur stderr
    """
    try:
        stderr.write(txt.decode() + '\n\n')
    except AttributeError:
        stderr.write(str(txt) + '\n\n')


def traiter_erreur(err):  # pylint: disable=W0613
    """Méthode appelée lorsqu'une exception est levée
    """
    stderr.write(traceback.format_exc() + '\n')


def url(fichier):
    """Url correspondant à un fichier
    """
    return '/' + fichier.relative_to(cfg.PWD).as_posix()


class ErreurExpression(Exception):
    """Exception levée quand une expression régulière n'est pas reconnue
    """
    pass


class GitError(Exception):
    """Exception levée quand git renvoie une erreur
    """
    def __init__(self, cpe):
        """L'argument cpe doit être une CalledProcessException."""
        Exception.__init__(self)
        self.cpe = cpe
        self.status = {
            doc[3:]: (doc[0], doc[1])
            for doc in
            subprocess.check_output(['git', 'status', '-s'])
            .decode('utf8').split('\n')[:-1]
        }

    def __getattr__(self, attribut):
        try:
            return getattr(self.cpe, attribut)
        except AttributeError:
            raise
