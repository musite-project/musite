# coding: utf-8
"""Gestion des fichiers, dossiers et dépôts

Vous trouverez aussi à la fin des méthodes un peu "inclassables", mais utiles
en plusieurs points du programme.
"""
import os
import re
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

    def commande(self, arguments):
        """Commande sur un dépôt existant
        """
        os.chdir(self.dossier)
        ligne = ['git']
        ligne.extend(arguments)
        try:
            resultat = subprocess.check_output(ligne)
        except subprocess.CalledProcessError as err:
            traiter_erreur(err)
            raise
        return resultat.decode('utf-8')

    def cloner(self, depot):
        """Cloner un dépôt distant
        """
        cmd = ['git', 'clone', depot, self.dossier]
        try:
            resultat = subprocess.check_output(cmd)
        except subprocess.CalledProcessError as err:
            if cfg.DEVEL:
                traiter_erreur(err)
                print(err.output)
            raise
        return resultat.decode('utf-8')

    def initialiser(self):
        """Initialisation du dépôt
        """
        self.commande(['init'])

    def journal(self, arguments=None):
        """Journal des modifications

        Méthode générale.
        """
        ligne = ['log']
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
        details = self.commande(parametres).replace('\r', '').split('\n')
        return details

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
        try:
            self.commande(['add', chemin])
            self.commande(arguments)
        except subprocess.CalledProcessError as err:
            if err.returncode == 128:
                try:
                    self.initialiser()
                except subprocess.CalledProcessError:
                    pass
            else:
                print(err.__dict__)

    def sauvegardefichier(self, fichier, auteur=None):
        """Sauvegarde d'un fichier isolé
        """
        self.sauvegarde(
            fichier.chemin.replace(self.dossier + os.sep, ''),
            fichier.nom,
            auteur
        )

    def sauvegardecomplete(self, message=_("Sauvegarde complète"), auteur=None):
        """Sauvegarde de l'ensemble du dépôt
        """
        self.sauvegarde('-A', message, auteur)


class Dossier():
    """Gestion des dossiers
    """
    def __init__(self, dossier):
        self.dossier = dossier
        if not os.path.isdir(dossier):
            raise TypeError(dossier + _(" n'est pas un dossier"))

    def lister(self, profondeur=1):
        """Liste du contenu d'un dossier

        Sous la forme d'un dictionnaire, chaque sous-dossier étant une clé
        de ce dictionnaire.
        """
        liste = {
            self.dossier: [
                os.path.split(fichier)[-1]
                for fichier in ls(self.dossier + '/*')
            ]
        }
        if profondeur > 1:
            for sousdossier in liste[self.dossier]:
                contenu = Dossier(
                    os.path.join(self.dossier, sousdossier)
                ).lister(profondeur - 1)
                if contenu[os.path.join(self.dossier, sousdossier)] != []:
                    liste = dict(
                        liste, **contenu
                    )
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
    if cfg.DEVEL:
        print(type(err), err)


def url(fichier):
    """Url correspondant à un fichier
    """
    return fichier.replace(cfg.PWD, '').replace(os.sep, '/')
