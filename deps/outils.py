# coding: utf-8
"""Gestion des fichiers, dossiers et dépôts

Si j'ai bien compris ce qu'est un modèle dans le modèle MVC, ce doit être
à peu près ça.
Vous trouverez aussi à la fin des méthodes un peu "inclassables", mais utiles
en plusieurs points du programme.
"""
import os
import re
import shutil
import traceback
from time import time
import subprocess
from glob import glob as ls
import random as rd
from string import ascii_lowercase
import unicodedata as ud
import functools
from .bottle import SimpleTemplate, template
from etc import config as cfg
from .i18n import lazy_gettext as _, i18n_path

# Ce qui suit vise à éviter la tentation de supprimer l'import de i18n_path :
# en effet, les autres modules l'importent depuis celui-ci, afin de centraliser
# tout cela et de permettre le cas échéant de redéfinir cette méthode.
assert i18n_path


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
        """
        return commande(['clone', depot, self.dossier])
        cmd = ['git', 'clone', depot, self.dossier]
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
        os.chdir(self.dossier)
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
            parametres.append(fichier)
        return self.commande(parametres).replace('\r', '').split('\n')

    @property
    def etat(self):
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
            in self.journal(['--follow', fichier]).split('commit ')
        ][1:]
        for element in historique:
            element[0] = element[0][:7]
            element.pop(3)
        return entete + historique

    @property
    def origine(self):
        """Adresse du dépôt depuis lequel celui-ci a été clôné
        """
        with open(os.path.join(self.dossier, '.git', 'config')) as gitconfig:
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
                fichier.chemin
            ])
        else:
            self.commande([
                'revert',
                '-n',
                version + '..HEAD'
            ])
        self.sauvegardecomplete(
            'Retour '
            + ('du fichier {} '.format(fichier.nom) if fichier else '')
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
            fichier.chemin,
            fichier.nom,
            auteur
        )


class Dossier():
    """Gestion des dossiers
    """
    def __init__(self, dossier):
        self.dossier = dossier
        if not os.path.isdir(dossier):
            raise TypeError(dossier + _(" n'est pas un dossier"))

    def lister(self, expression='*', profondeur=1):
        """Liste du contenu d'un dossier

        Sous la forme d'un dictionnaire, chaque sous-dossier étant une clé
        de ce dictionnaire.
        """
        liste = {
            self.dossier: [
                os.path.split(fichier)[-1]
                for fichier in ls(self.dossier + '/' + expression)
            ]
        }
        if profondeur > 1:
            for sousdossier in liste[self.dossier]:
                try:
                    contenu = Dossier(
                        os.path.join(self.dossier, sousdossier)
                    ).lister(profondeur=profondeur - 1)
                    if contenu[os.path.join(self.dossier, sousdossier)] != []:
                        liste = dict(
                            liste, **contenu
                        )
                except TypeError:
                    pass
        return liste


class Fichier():
    """Gestion des fichiers
    """
    def __init__(self, chemin):
        self.chemin = chemin
        self.dossier = os.path.dirname(chemin)
        self.nom = os.path.basename(chemin)

    def lire(self):
        """Retourne le contenu d'un fichier texte
        """
        fichier = open(self.chemin, 'r')
        try:
            contenu = fichier.read(-1)
        except UnicodeDecodeError:
            contenu = ''
        fichier.close()
        return contenu

    def ouvrir(self):
        """Utile ?
        """
        fichier = open(self.chemin, 'rb')
        contenu = fichier.read(-1)
        fichier.close()
        return contenu


def nettoyertmp():
    """Nettoyage des fichiers temporaires"""
    for ancien in (
            fichier for fichier in ls(os.path.join(cfg.TMP, '*'))
            if (time() - os.path.getmtime(fichier))/3600 > 3
    ):
        if os.path.isdir(ancien):
            shutil.rmtree(ancien)
        else:
            os.remove(ancien)
    for ancien in (
            fichier for fichier in ls(os.path.join(cfg.STATIC, 'tmp', '*'))
            if (time() - os.path.getmtime(fichier))/3600 > 3
    ):
        if os.path.isdir(ancien):
            shutil.rmtree(ancien)
        else:
            os.remove(ancien)


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


def traiter_erreur(err):
    """Méthode appelée lorsqu'une exception est levée
    """
    if cfg.DEVEL:
        print(traceback.format_exc())


def url(fichier):
    """Url correspondant à un fichier
    """
    return fichier.replace(cfg.PWD, '').replace(os.sep, '/')


class GitError(Exception):
    def __init__(self, cpe):
        """L'argument cpe doit être une CalledProcessException."""
        self.cpe = cpe

    def __getattr__(self, attribut):
        try:
            return getattr(self.cpe, attribut)
        except AttributeError:
            raise

    @property
    def status(self):
        etat = subprocess.check_output(['git', 'status', '-s'])\
            .decode('utf8').split('\n')
        print(etat)
        return {doc[3:]: (doc[0], doc[1]) for doc in etat[:-1]}
