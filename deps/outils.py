# coding: utf-8
"""Gestion des fichiers, dossiers et dépôts

Vous trouverez aussi à la fin des méthodes un peu "inclassables", mais utiles
en plusieurs points du programme.
"""
import os
import re
import subprocess
from datetime import datetime
from glob import glob as ls
import random as rd
from string import ascii_lowercase
import unicodedata as ud
import jrnl as l
import functools
from bottle import SimpleTemplate, template
from etc import config as cfg
from deps.i18n import lazy_gettext as _, i18n_path


class Depot():
    def __init__(self, dossier):
        self.dossier = dossier

    def commande(self, arguments):
        os.chdir(self.dossier)
        ligne = ['git']
        ligne.extend(arguments)
        try:
            resultat = subprocess.check_output(ligne)
        except subprocess.CalledProcessError as e:
            if cfg.DEVEL:
                print(e.output)
            raise
        return resultat.decode('utf-8')

    def initialiser(self):
        self.commande(['init'])

    def journal(self, arguments=[]):
        ligne = ['log']
        ligne.extend(arguments)
        return self.commande(ligne)

    @property
    def journalcomplet(self):
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
        historique = [
            version.split(' ')
            for version in self.journal(
                [
                    '--follow',
                    fichier
                ]
            )[1:-1].split('"\n"')
        ]
        return historique

    def comparer(self, version, versionb=None, fichier=None):
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
        def sauver(self, chemin, message):
            arguments = [
                'commit',
                '-m',
                message
            ]
            if auteur:
                arguments.append('--author="{0} <{0}>'.format(auteur))
            self.commande(['add', chemin])
            self.commande(arguments)

        try:
            sauver(self, chemin, message)
        except subprocess.CalledProcessError as e:
            if e.returncode == 128:
                try:
                    self.initialiser()
                except subprocess.CalledProcessError:
                    pass
            else:
                print(e.__dict__)

    def sauvegardefichier(self, fichier, auteur=None):
        self.sauvegarde(
            fichier.chemin.replace(self.dossier + os.sep, ''),
            fichier.nom,
            auteur
        )

    def sauvegardecomplete(self, message='Sauvegarde complète', auteur=None):
            self.sauvegarde('-A', message, auteur)


class Dossier():
    def __init__(self, dossier):
        self.dossier = dossier
        if not os.path.isdir(dossier):
            raise TypeError(dossier + " n'est pas un dossier")

    def lister(self, profondeur=1):
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
    def __init__(self, chemin):
        self.chemin = chemin
        self.dossier = os.path.dirname(chemin)
        self.nom = os.path.basename(chemin)

    def lire(self):
        fichier = open(self.chemin, 'r')
        try:
            contenu = fichier.read(-1)
        except UnicodeDecodeError:
            contenu = ''
        fichier.close()
        return contenu

    def ouvrir(self):
        fichier = open(self.chemin, 'rb')
        contenu = fichier.read(-1)
        fichier.close()
        return contenu

    def ecrire(self, contenu):
        self.creerdossier()
        fichier = open(self.chemin, 'w')
        fichier.write(contenu)
        fichier.close()
        if self.nom not in (recherche, gitlog):
            depot.sauvegardefichier(self)

    def ecrirebinaire(self, contenu):
        self.creerdossier()
        fichier = open(self.chemin, 'wb')
        fichier.write(contenu)
        fichier.close()

    def copier(self, fin):
        try:
            shutil.copytree(self.dossier, fin.dossier)
        except Exception as e:
            l.log('Erreur l. 758 :', type(e))
            pass
        shutil.copy(self.chemin, fin.chemin)
        depot.sauvegardecomplete('Clonage')

    def deplacer(self, fin):
        fin.creerdossier()
        os.rename(self.chemin, fin.chemin)
        self.effacerdossier()
        depot.sauvegardecomplete('Déplacement')

    def creerdossier(self):
        try:
            os.makedirs(self.dossier)
        except FileExistsError as e:
            pass

    def effacerdossier(self):
        try:
            os.removedirs(self.dossier)
        except Exception as e:
            l.log('Erreur l. 779 :', type(e))
            pass

    def effacer(self):
        poubelle = os.path.join(travail, '.poubelle')
        dossierpoubelle = os.path.join(poubelle, self.dossier)
        fichierpoubelle = os.path.join(poubelle, self.chemin)
        if self.dossier != '':
            try:
                os.mkdir(dossierpoubelle)
            except Exception as e:
                l.log('Erreur l. 788 :', type(e))
                try:
                    os.remove(dossierpoubelle[0:-1])
                except Exception as e:
                    l.log('Erreur l. 791 :', type(e))
                    pass
                try:
                    os.makedirs(dossierpoubelle)
                except Exception as e:
                    l.log('Erreur l. 795 :', type(e))
                    pass
        try:
            os.rename(self.chemin, fichierpoubelle)
        except Exception as e:
            l.log('Erreur l. 799 :', type(e))
            try:
                fichiers = os.listdir(fichierpoubelle)
                for fichier in fichiers:
                    Fichier(fichierpoubelle, fichier).supprimer()
            except Exception as e:
                l.log('Erreur l. 804 :', type(e))
                pass
            try:
                os.removedirs(fichierpoubelle)
            except Exception as e:
                l.log('Erreur l. 808 :', type(e))
                pass
            dossiers = os.path.split(self.chemin)
            for i in range(len(dossiers)):
                chemin = os.path.join(dossiers[:-i])
                try:
                    os.remove(os.path.join(poubelle, chemin))
                except Exception as e:
                    l.log('Erreur l. 815 :', type(e))
                    pass
            self.effacer()
        self.effacerdossier()
        depot.sauvegardecomplete('Effacement')

    def supprimer(self):
        os.remove(self.chemin)

    def supprimerdossier(self):
        try:
            for fichier in os.listdir(self.dossier):
                os.remove(self.dossier + '/' + fichier)
        except Exception as e:
            l.log('Erreur l. 828 :', type(e))
            pass
        try:
            os.removedirs(self.dossier)
        except Exception as e:
            l.log('Erreur l. 832 :', type(e))
            pass

    def mouliner(self, commande):
        os.chdir(self.dossier)
        subprocess.call([commande, self.chemin])


def sansaccents(entree):
    nkfd_form = ud.normalize('NFKD', entree)
    return "".join([c for c in nkfd_form if not ud.combining(c)])


def motaleatoire(longueur, source=ascii_lowercase):
    return ''.join(rd.choice(source) for i in range(longueur))


def templateperso(syntaxe='<% %> % <<< >>>'):
    class Adaptateur(SimpleTemplate):
        def __init__(self, syntax=syntaxe, *args, **settings):
            SimpleTemplate.__init__(self, syntax=syntax, *args, **settings)
    return functools.partial(template, template_adapter=Adaptateur)
