#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Musite − wiki musical

Musite est une sorte de wiki, pensé pour gérer des documents contenant des
partitions de musique, mais adaptable à toutes sortes d'autres usages.

Ce fichier gère la partie interface du site, renvoyant les pages
correspondant aux urls saisies dans le navigateur.
"""

__appname__ = 'serveur'
__license__ = 'MIT'


# Import de librairies externes ###############################################

import os
import sys
import shutil
import re
LIB = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'deps')
sys.path.insert(0, LIB)
import bottle as b
from bottle import request as rq
from deps.i18n import I18NPlugin as Traduction
from subprocess import CalledProcessError
from pkgutil import iter_modules
from importlib import import_module
from deps import outils as f
from deps.outils import i18n_path, _
from deps import auth as a
from deps import utilisateurs as u
from deps import HTMLTags as h
from deps.mistune import markdown
from etc import config as cfg


# Paramètres bottle ###########################################################

b.TEMPLATE_PATH += cfg.MODELES
APP = b.Bottle()


# Import des modules qui vont traiter chaque extension ########################
EXT = {
    e[1]: import_module('ext.' + e[1])
    for e in iter_modules(path=[os.path.join(LIB, 'ext')])
}
TXT = EXT['txt']


# Classes #####################################################################

class Depot:
    """Interaction avec le dépôt des documents.

    Cette classe ne gère pas directement le dépôt, mais l'affichage des
    messages le concernant et la transmission des instructions en provenance
    de l'interface.
    """
    def __init__(self, projet):
        self.projet = projet
        self.depot = f.Depot(os.path.join(cfg.DATA, projet))

    def cloner(self, depot):
        """Clonage d'un dépôt existant.
        """
        self.depot.cloner(depot)

    def initialiser(self):
        """Initialisation d'un nouveau dépôt.
        """
        self.depot.initialiser()

    def comparer(self, commit, commitb=None, fichier=''):
        """Comparaison entre deux versions.

        Si le deuxième commit n'est pas précisé, on compare la version
        demandée avec la précédente.
        """
        if not commitb:
            commitb = commit
            commit += '^'
        try:
            modification = b.html_escape(
                '\n'.join(
                    self.depot.comparer(commit, commitb, fichier=fichier)
                )
            ) \
                .replace('[-', '<em class="suppr"><del>[-') \
                .replace('-]', '-]</del></em class="suppr">') \
                .replace('{+', '<strong class="add">{+') \
                .replace('+}', '+}</strong class="add">')
            modification = re.sub(
                'diff.*\n', '\n\n<hr>\n', modification
            )
            modification = re.sub(
                r'index.*\n.*\n\+\+\+ b/(.*)',
                str(h.B(h.I('{}'))).format(h.A('\\1', href='\\1')),
                modification
            )
            modification = re.sub(
                '(@@.*@@)', '\n{}\n'.format(h.B(h.I('\\1'))), modification
            )
            return h.CODE(modification)
        except CalledProcessError as err:
            f.traiter_erreur(err)
            return _("Il n'y a rien avant la création !")

    def historique(self, fichier=None):
        """Liste des modifications d'un dépôt ou d'un fichier

        Si un fichier est précisé, on renvoie la liste des modifications de ce
        fichier uniquement ; sinon, on renvoie tout l'historique du dépôt.
        """
        try:
            if fichier:
                tableau = self.depot.journalfichier(fichier)
            else:
                tableau = self.depot.journalcomplet
        except CalledProcessError as err:
            f.traiter_erreur(err)
            return _("Il n'y a pas encore de modifications à signaler.")
        for element in tableau[1:]:
            element[0] = h.A(element[0], href='?commit=' + element[0])
            element[1] = re.sub(r'\<.*\>', '', element[1])
        return b.template('tableau', tableau=tableau)

    def annuler(self, commit):
        """Annulation des modifications d'un seul commit

        Cette méthode est là au cas où elle pourrait servir dans la suite, mais
        son usage est très délicat : cette opération peut en effet engendrer
        des conflits, dont la gestion depuis un script est complexe. À utiliser
        avec modération !
        """
        self.depot.annuler(commit)

    def retablir(self, commit, fichier=None, auteur=None):
        """Retour en arrière à une version donnée

        Cette méthode revient à la version spécifiée, ou pour l'ensemble du
        dépôt, ou pour un seul fichier. Elle est non-destructrice : bien que
        les modifications ayant suivi cette version soient annulées, elles
        restent présentes dans l'historique.
        """
        self.depot.retablir(commit, fichier, auteur)

    def sauvegarder(self, fichier=None, message=_("Sauvegarde complète")):
        """Sauvegarde du dépôt

        Cette méthode sauvegarde ou un fichier donné,
        ou le dépôt en son entier.
        """
        if fichier:
            self.depot.sauvegardefichier(fichier, rq.auth[0])
        else:
            self.depot.sauvegardecomplete(message, rq.auth[0])


class Document:
    """Gestion des documents
    """
    def __init__(self, projet, element, ext):
        self.projet = projet
        self.element = element
        self.ext = ext
        self.chemin = '/'.join((projet, element + ('.' + ext if ext else '')))
        self.fichier = os.path.join(cfg.DATA, self.chemin.replace('/', os.sep))
        self.dossier = os.path.join(cfg.DATA, os.path.dirname(self.chemin))
        self.depot = Depot(self.projet)

    def afficher(self, contenu):
        """Propriétés communes des pages de gestion de documents

        Cette méthode définit en particulier ce qui apparaît dans le menu.
        C'est ici qu'il faut définir ce qui est commun à toutes les pages
        proposant une opération sur un document.
        """
        actions = {
            _('Aperçu'): self.chemin,
            _('Historique'): '_historique/' + self.chemin,
            _('Source'): '_src/' + self.chemin
        }
        try:
            if a.authentifier(rq.auth[0], rq.auth[1]):
                actions[_('Copier')] = '_copier/' + self.chemin
                actions[_('Déplacer')] = '_deplacer/' + self.chemin
                actions[_('Éditer')] = '_editer/' + self.chemin
                actions[_('Supprimer')] = '_supprimer/' + self.chemin
        except TypeError as err:
            f.traiter_erreur(err)
        liens = {
            _('Projet'): self.projet,
            _('Dossier'): '/'.join(self.chemin.split('/')[:-1])
        }
        try:
            exports = {
                fmt: self.chemin + '?fmt=' + fmt
                for fmt in EXT[self.ext].Document(self.chemin).proprietes
            }
        except (AttributeError, KeyError) as err:
            f.traiter_erreur(err)
            # Cette exception est levée quand le module concerné ne définit pas
            # de format d'export.
            exports = {}
        try:
            midi = EXT[self.ext].Document(self.chemin).midi()
        except (AttributeError, KeyError) as err:
            f.traiter_erreur(err)
            # Cette exception est levée quand le module concerné ne définit pas
            # de fichier midi.
            midi = None
        return {
            'corps': contenu,
            'actions': actions,
            'exports': exports,
            'liens': liens,
            'midi': midi,
        }

    @property
    def contenu(self):
        """Contenu du document

        Ce contenu dépend du type du document : c'est donc le module gérant
        l'extension concernée qui s'occupe de retourner un code html
        correspondant audit contenu.
        Pour développer un module gérant une nouvelle extension, référez-vous
        aux docstrings du module deps/ext/txt.py.
        """
        try:
            return self.afficher(
                EXT[self.ext].Document(self.chemin).afficher()
            )
        except (KeyError, AttributeError) as err:
            f.traiter_erreur(err)
            # Si le type de document est inconnu ou ne prévoit pas d'affichage,
            # on essaie de le traiter comme un document texte.
            # Sinon, on abandonne.
            try:
                return self.afficher(TXT.Document(self.chemin).afficher())
            except TXT.FichierIllisible as err:
                f.traiter_erreur(err)
                return self.afficher(_("Extension inconnue : {}.").format(err))
            except FileNotFoundError as err:
                f.traiter_erreur(err)
                b.abort(404)
        except EXT[self.ext].FichierIllisible as err:
            f.traiter_erreur(err)
            return self.afficher(_("Ce fichier est illisible."))

    @property
    def source(self):
        """Affichage de la source du document
        """
        try:
            return self.afficher(
                EXT[self.ext].Document(self.chemin).afficher_source()
            )
        except (KeyError, AttributeError) as err:
            f.traiter_erreur(err)
            # Si le type de document est inconnu ou ne prévoit pas d'affichage
            # de la source, on essaie de le traiter comme un document texte.
            # Sinon, on abandonne.
            try:
                return self.afficher(
                    TXT.Document(self.chemin).afficher_source()
                )
            except TXT.FichierIllisible as err:
                f.traiter_erreur(err)
                return self.afficher(
                    _("Extension inconnue : {}.").format(err)
                    + h.BR()
                    + _('Voici les données de la requète :')
                    + h.BR()
                    + '{}'.format(
                        str(h.BR()).join(
                            "{!s}={!r}".format(item[0], item[1])
                            for item in rq.query.items()
                        )
                    )
                )
            except NameError as err:
                f.traiter_erreur(err)
                b.abort(404)
        except EXT[self.ext].FichierIllisible as err:
            f.traiter_erreur(err)
            return self.afficher(_("Ce fichier est illisible."))

    def creer(self):
        """Création d'un nouveau document
        """
        return self.editer(creation=True)

    def supprimer(self):
        """Suppression du document
        """
        try:
            EXT[self.ext].Document(self.chemin).supprimer()
        except KeyError as err:
            f.traiter_erreur(err)
            TXT.Document(self.chemin).supprimer()
        self.depot.sauvegarder(
            message=_('Suppression du document {}').format(self.chemin)
        )
        return self.afficher(_('Document supprimé !'))

    def editer(self, creation=False):
        """Édition du document
        """
        try:
            return self.afficher(
                EXT[self.ext].Document(self.chemin).editer(creation)
            )
        except KeyError as err:
            f.traiter_erreur(err)
            # Si le type de document est inconnu, on essaie de le traiter
            # comme un document texte. Sinon, on abandonne.
            try:
                return self.afficher(
                    TXT.Document(self.chemin).editer(creation)
                )
            except TXT.FichierIllisible as err:
                f.traiter_erreur(err)
                return self.afficher(
                    _("Ce type de document n'est pas éditable.")
                )
        except AttributeError as err:
            f.traiter_erreur(err)
            # Si le type de document ne prévoit pas d'édition, on abandonne.
            return self.afficher(_("Ce type de document n'est pas éditable."))
        except EXT[self.ext].FichierIllisible as err:
            f.traiter_erreur(err)
            return self.afficher(
                '''Si je ne puis même pas lire ce fichier,
                comment voulez-vous que je l'édite ?'''
                )

    def enregistrer(self, contenu):
        """Enregistrement du document
        """
        try:
            EXT[self.ext].Document(self.chemin).enregistrer(contenu)
        except (AttributeError, KeyError) as err:
            f.traiter_erreur(err)
            TXT.Document(self.chemin).enregistrer(self.chemin)
        f.Depot(
            os.path.join(
                cfg.DATA, self.projet
            )
        ).sauvegardefichier(f.Fichier(self.fichier), rq.auth[0])
        b.redirect(i18n_path('/' + self.chemin))

    def copier(self, destination, ecraser=False):
        """Copie d'un dossier
        """
        dest = os.path.join(cfg.DATA, destination)
        if not os.path.exists(dest) or ecraser:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            print(self.fichier, dest)
            shutil.copy2(self.fichier, dest)
            self.depot.sauvegarder(
                message=(
                    _('copie')
                    + ' ' + '/'.join(self.chemin.split('/')[1:])
                    + ' -> ' + '/'.join(destination.split('/')[1:])
                )
            )
            b.redirect(i18n_path('/' + destination))
        else:
            return self.afficher(markdown(_(
                "Il y a déjà quelque chose à cet emplacement.\n\n"
                "- Si vous désirez copier un fichier ou un dossier au sein"
                " d'un autre dossier, merci de spécifier le chemin complet de"
                " la destination.\n"
                "- Si vous désirez remplacer un fichier existant, supprimez-le"
                " auparavant."
            )))

    def exporter(self, fmt, proprietes):
        """Export d'un document en différents formats
        """
        proprietes = {fmt: proprietes}
        try:
            b.redirect(
                i18n_path(
                    EXT[self.ext].Document(
                        self.chemin, proprietes=proprietes
                    ).exporter(fmt)('tmp', f.motaleatoire(3))
                    + '?action=telecharger'
                )
            )
        except EXT[self.ext].ErreurCompilation as err:
            f.traiter_erreur(err)
            return self.afficher(
                markdown(_(
                    """\
Il y a eu une erreur pendant le traitement du document.
Ceci vient probablement d'une erreur de syntaxe ou d'une erreur dans vos
paramètres ; si vous êtes absolument certain du contraire,
merci de signaler le problème.
                    """
                )))

    def exporter_infos(self, fmt):
        """Informations pour l'export
        """
        return self.afficher(b.template(
            'export',
            {
                'proprietes':
                    EXT[self.ext].Document(self.chemin).listeproprietes[fmt]
            }
        ))

    @property
    def historique(self):
        """Liste des modifications
        """
        return self.afficher(self.depot.historique(self.fichier))

    def modification(self, commit):
        """Affichage des modifications effectuées dans une version donnée
        """
        modifications = self.depot.comparer(commit, fichier=self.fichier)
        differences = self.depot.comparer(commit, 'HEAD', fichier=self.fichier)
        return self.afficher(
            b.template(
                'historique',
                commit=commit,
                modifications=modifications,
                differences=differences,
                emplacement=self.chemin,
                rq=rq
            )
        )

    def retablir(self, commit):
        """Retour en arrière jusqu'à une version donnée
        """
        self.depot.retablir(commit, f.Fichier(self.fichier), rq.auth[0])
        b.redirect(i18n_path('/_historique/' + self.chemin))


class Dossier:
    """Gestion des dossiers
    """
    def __init__(self, projet, element):
        self.projet = projet
        self.nom = element
        self.chemin = '/'.join((projet, element))
        self.dossier = os.path.join(cfg.DATA, self.chemin.replace('/', os.sep))
        self.depot = Depot(self.projet)

    def afficher(self, contenu, suppression=False):
        """Propriétés communes des pages de gestion de dossiers

        Cette méthode définit en particulier ce qui apparaît dans le menu.
        C'est ici qu'il faut définir ce qui est commun à toutes les pages
        proposant une opération sur un dossier.
        """
        actions = {}
        try:
            if a.authentifier(rq.auth[0], rq.auth[1]) and not suppression:
                actions[_('Créer document')] = '_creer/' + self.chemin
                actions[_('Créer dossier')] = '_creerdossier/' + self.chemin
                actions[_('Copier')] = '_copier/' + self.chemin
                actions[_('Déplacer')] = '_deplacer/' + self.chemin
                actions[_('Envoyer fichier')] = '_envoyer/' + self.chemin
                actions[_('Supprimer')] = \
                    '_supprimerdossier/' + self.chemin
        except TypeError as err:
            f.traiter_erreur(err)
        liens = {
            _('Projet'): self.projet,
            _('Parent'): self.projet + (
                '/'.join(self.nom.split('/')[:-1])
            )
        }
        return {
            'corps': contenu,
            'actions': actions,
            'liens': liens,
        }

    def creer(self):
        """Création d'un nouveau dossier
        """
        os.makedirs(self.dossier, exist_ok=True)
        return self.lister()

    def deplacer(self, destination, ecraser=False):
        """Déplacement/renommage d'un dossier (ou document)
        """
        dest = os.path.join(cfg.DATA, destination)
        if not os.path.exists(dest) or ecraser:
            shutil.move(self.dossier, dest)
            self.depot.sauvegarder(
                message=(
                    self.nom
                    + ' -> ' + '/'.join(destination.split('/')[1:])
                )
            )
            b.redirect(i18n_path('/' + destination))

    def copier(self, destination, ecraser=False):
        """Copie d'un dossier
        """
        dest = os.path.join(cfg.DATA, destination)
        if not os.path.exists(dest) or ecraser:
            shutil.copytree(self.dossier, dest)
            self.depot.sauvegarder(
                message=(
                    _('copie')
                    + ' ' + self.nom
                    + ' -> ' + '/'.join(destination.split('/')[1:])
                )
            )
            b.redirect(i18n_path('/' + destination))
        else:
            return self.afficher(markdown(_(
                "Il y a déjà quelque chose à cet emplacement.\n\n"
                "- Si vous désirez copier un fichier ou un dossier au sein"
                " d'un autre dossier, merci de spécifier le chemin complet de"
                " la destination.\n"
                "- Si vous désirez remplacer un fichier existant, supprimez-le"
                " auparavant."
            )))

    def envoyer_fichier(self, fichier, ecraser=False):
        """Envoi d'un fichier vers le dossier
        """
        try:
            fichier.save(self.dossier, int(ecraser))
            self.depot.sauvegarder(
                message=str(_(
                    "Envoi du fichier {}".format(fichier.filename)
                ))
            )
            b.redirect(i18n_path('/' + self.chemin))
        except OSError as err:
            f.traiter_erreur(err)
            return self.afficher(_(
                "Le fichier existe déjà. Si vous voulez l'écraser, merci de "
                "cocher la case correspondante."
            ))

    def envoyer_fichier_infos(self):
        """Informations pour l'envoi d'un fichier
        """
        return self.afficher(b.template('envoi'))

    def lister(self):
        """Affichage des fichiers présents dans un dossier
        """
        fichiers = f.Dossier(self.dossier).lister(1)[self.dossier]
        # Si l'on n'est pas à la racine, on affiche un lien vers le parent.
        try:
            if self.chemin[:-1] != self.projet:
                liste = [
                    h.A(
                        '../',
                        href=i18n_path('/{}'.format(
                            '/'.join(self.chemin.split('/')[:-1])
                        ))
                    )
                ]
            else:
                liste = []
        # Si cette exception est levée, c'est que l'on est à la racine.
        except ValueError as err:
            f.traiter_erreur(err)
            liste = []
        # Liste des dossiers, puis des fichiers
        listedossiers = sorted(
            [
                fichier + '/'
                for fichier in fichiers
                if os.path.isdir(os.path.join(self.dossier, fichier))
            ],
            key=lambda s: s.lower()
        )
        listefichiers = sorted(
            [
                fichier
                for fichier in fichiers
                if not os.path.isdir(os.path.join(self.dossier, fichier))
            ],
            key=lambda s: s.lower()
        )
        # Formatage de la liste des fichiers.
        liste += [
            h.A(
                dossier,
                href=i18n_path('/{}/{}/{}'.format(
                    self.projet, self.nom, dossier
                ).replace('//', '/'))
            )
            for dossier in listedossiers
        ]
        liste += [
            h.A(
                fichier,
                href=i18n_path('/{}/{}/{}'.format(
                    self.projet, self.nom, fichier
                ).replace('//', '/'))
            )
            for fichier in listefichiers
        ]
        try:
            with open(os.path.join(self.dossier, 'README.md'), 'r') as readme:
                readme = markdown(readme.read(-1))
        except FileNotFoundError as err:
            f.traiter_erreur(err)
            readme = None
        return self.afficher(b.template(
            'liste',
            liste=liste,
            readme=readme,
        ))

    def supprimer(self):
        """Suppression d'un dossier et de son contenu
        """
        shutil.rmtree(self.dossier, ignore_errors=True)
        f.Depot(
            os.path.join(
                cfg.DATA, self.projet
            )
        ).sauvegardecomplete(
            _('Suppression du dossier {}').format(self.chemin),
            rq.auth[0]
        )
        return self.afficher(_('Dossier supprimé !'))


class Projet(Dossier):
    """Gestion des projets
    """
    def __init__(self, projet):
        Dossier.__init__(self, projet, '')
        self.projet = projet
        self.depot = Depot(self.projet)
        self.url = i18n_path('/' + projet)

    def afficher(self, contenu, suppression=False):
        """Propriétés communes des pages de gestion de dossiers

        Cette méthode définit en particulier ce qui apparaît dans le menu.
        C'est ici qu'il faut définir ce qui est commun à toutes les pages
        proposant une opération sur un projet.
        """
        actions = {_('Historique'): '_historique/' + self.chemin}
        try:
            if a.authentifier(rq.auth[0], rq.auth[1]):
                if not suppression:
                    actions[_('Créer document')] = '_creer/' + self.chemin
                    actions[_('Créer dossier')] = \
                        '_creerdossier/' + self.chemin
                    actions[_('Copier')] = '_copier/' + self.chemin
                    actions[_('Envoyer fichier')] = '_envoyer/' + self.chemin
                    actions[_('Renommer')] = '_deplacer/' + self.chemin
                    actions[_('Supprimer')] = \
                        '_supprimerprojet/' + self.chemin
                else:
                    actions[_('Créer projet')] = '_creerprojet'
        except TypeError as err:
            f.traiter_erreur(err)
        liens = {_('Projet'): self.projet}
        return {
            'corps': contenu,
            'actions': actions,
            'liens': liens,
        }

    def creer(self):
        """Création d'un nouveau projet
        """
        try:
            os.makedirs(self.dossier, exist_ok=False)
            self.depot.initialiser()
            b.redirect(self.url)
        except FileExistsError as err:
            f.traiter_erreur(err)
            return self.afficher(_('Ce projet existe déjà !'))

    def renommer(self, destination):
        """Renommage d'un projet
        """
        dest = os.path.join(cfg.DATA, destination)
        if not os.path.exists(dest):
            shutil.move(self.dossier, dest)
            b.redirect(i18n_path('/' + destination))
        else:
            return self.afficher(_('Il y a déjà un projet portant ce nom !'))

    def cloner(self, depot):
        """Clonage d'un projet distant
        """
        self.depot.cloner(depot)
        b.redirect(self.url)

    def copier(self, destination, ecraser=False):
        """Copie d'un projet
        """
        dest = os.path.join(cfg.DATA, destination)
        if not os.path.exists(dest):
            shutil.copytree(self.dossier, dest)
            b.redirect(i18n_path('/' + destination))
        else:
            return self.afficher(_('Il y a déjà un projet portant ce nom !'))

    @property
    def historique(self):
        """Liste des modifications
        """
        return self.afficher(self.depot.historique())

    def modification(self, commit):
        """Affichage des modifications effectuées dans une version donnée
        """
        modifications = self.depot.comparer(commit)
        differences = self.depot.comparer(commit, 'HEAD')
        return self.afficher(
            b.template(
                'historique',
                commit=commit,
                modifications=modifications,
                differences=differences,
                emplacement=self.projet,
                rq=rq
            )
        )

    def retablir(self, commit):
        """Retour en arrière jusqu'à une version donnée
        """
        self.depot.retablir(commit, auteur=rq.auth[0])
        b.redirect(i18n_path('/_historique/' + self.chemin))

    def supprimer(self):
        """Suppression du projet
        """
        try:
            shutil.rmtree(self.dossier, ignore_errors=False)
            return self.afficher(_('Projet supprimé !'), suppression=True)
        except FileNotFoundError as err:
            f.traiter_erreur(err)
            # Cette exception est levée quand le projet n'existe pas.
            return self.afficher(_('''C'est drôle, ce que vous me demandez :
                il n'y a pas de projet ici !'''), suppression=True)


# Méthodes globales :  ########################################################


# I. Bidouille et décorateurs destinés à éviter les redondances ########

@APP.hook('before_request')
def strip_path():
    """Effacement du / final s'il y en a un dans l'url
    """
    rq.environ['PATH_INFO'] = rq.environ['PATH_INFO'].rstrip('/')


def page(fonction):
    """Mise en forme commune à toutes les pages

    Cette fonction est un décorateur à appliquer à toutes les fonctions
    affichant des pages, mais non à celles qui retournent des données
    particulières, tels les css ou les fichiers statiques.
    """
    def afficher(*arguments, **parametres):
        """Décorateur
        """
        contenu = fonction(*arguments, **parametres)
        contenu['rq'] = rq
        return b.template('page', contenu)
    return afficher


# II. pages du site ########

#   1. Accueil
@APP.get('/')
@page
def accueil():
    """ Page d'accueil du site
    """
    try:
        actions = {_('Créer projet'): '_creerprojet'} \
            if a.authentifier(rq.auth[0], rq.auth[1]) \
            else {}
    except TypeError as err:
        f.traiter_erreur(err)
        # Cette exception est levée en l'absence d'authentification
        actions = {}
    liens = {_('Projets'): '_projets'}
    try:
        with open(os.path.join(
            cfg.PAGES,
            'md',
            'Accueil.{}.md'.format(rq.locale)
        ), 'r') as acc:
            corps = markdown(acc.read(-1))
    except FileNotFoundError as err:
        f.traiter_erreur(err)
        with open(os.path.join(cfg.PAGES, 'md', 'Accueil.fr.md'), 'r') as acc:
            corps = markdown(acc.read(-1))
    return {
        'corps': corps,
        'actions': actions,
        'liens': liens
    }


@APP.get('/_projets')
@page
def lister_projets():
    """Liste des projets existants
    """
    try:
        actions = {
            _('Créer projet'): '_creerprojet',
            _('Cloner projet'): '_clonerprojet',
        } \
            if a.authentifier(rq.auth[0], rq.auth[1]) \
            else {}
    except TypeError as err:
        f.traiter_erreur(err)
        # Cette exception est levée en l'absence d'authentification
        actions = {}
    listefichiers = f.Dossier(cfg.DATA).lister(1)
    # Formatage de la liste des fichiers.
    liste = [
        h.A(
            projet, href=i18n_path('/{}'.format(projet))
        )
        for projet in sorted(listefichiers[cfg.DATA])
        if os.path.isdir(os.path.join(cfg.DATA, projet))
    ]
    return {
        'corps': b.template('liste', liste=liste),
        'actions': actions
    }


#   2. Authentification et administration
@APP.get('/authentification')
@APP.get('/authentification/<action>')
@b.auth_basic(a.authentifier, _('Accès réservé'))
@page
def authentifier():
    """ Page destinée à forcer l'authentification.
    """
    return {
        'corps':
            _('Bonjour, {} !').format(rq.auth[0])
            + h.BR() + h.BR()
            + h.A(_('Retour à la page précédente'), href=rq['HTTP_REFERER']),
    }


@APP.get('/admin')
@APP.get('/admin/<action>')
@b.auth_basic(a.admin, _('Vous devez être administrateur'))
@page
def admin(action=''):
    """ Pages réservées à l'administrateur.
    """
    retour = {'actions': {_('Utilisateurs'): 'admin/utilisateurs'}}
    if action == 'utilisateurs':
        retour['corps'] = b.template('utilisateurs')
    else:
        try:
            with open(os.path.join(
                cfg.PAGES,
                'md',
                'Admin.{}.md'.format(rq.locale)
            ), 'r') as adm:
                retour['corps'] = markdown(adm.read(-1))
        except FileNotFoundError as err:
            f.traiter_erreur(err)
            with open(os.path.join(
                cfg.PAGES, 'md', 'Admin.fr.md'
            ), 'r') as adm:
                retour['corps'] = markdown(adm.read(-1))
    return retour


@APP.post('/admin/groupes')
@b.auth_basic(a.admin, _('Vous devez être administrateur'))
def groupes():
    """Enregistrement des groupes
    """
    with open(os.path.join(cfg.ETC, 'groupes'), 'w') as grp:
        grp.write(rq.forms.groupes)
    b.redirect(i18n_path('/admin/utilisateurs'))


@APP.get('/admin/supprimerutilisateur/<nom>')
@b.auth_basic(a.admin, _('Vous devez être administrateur'))
def utilisateur_suppression(nom):
    """Suppression d'un utilisateur
    """
    u.Utilisateur(nom).supprimer()
    b.redirect(i18n_path('/admin/utilisateurs'))


@APP.post('/admin/utilisateurs')
@b.auth_basic(a.admin, _('Vous devez être administrateur'))
def utilisateur_ajout():
    """ Ajout d'un nouvel utilisateur à la base
    """
    if rq.forms.mdp == rq.forms.mdp_v:
        u.Utilisateur(rq.forms.nom, rq.forms.mdp).ajouter()
    b.redirect(i18n_path('/admin/utilisateurs'))


#   3. Fichiers statiques
@APP.get('/static')
@APP.get('/static/<chemin:path>')
def static(chemin='/'):
    """ Fichiers statiques
    """
    telecharger = True if rq.query.action == 'telecharger' else False
    return b.static_file(
        chemin.replace('/', os.sep),
        root=os.path.join(cfg.PWD, cfg.STATIC),
        download=telecharger
    )


@APP.get('/favicon.ico')
def favicon():
    """Icône du site
    """
    return static('img/favicon.ico')


#   4. Pages de gestion de projets
#      Attention, l'ordre des méthodes est important.

# Création d'un document
@APP.get('/_creer/<nom>')
@APP.get('/_creer/<nom>/<element:path>')
@APP.get('/_creer/<nom>/<element:path>.<ext>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def document_creer_infos(nom, element=None, ext=None):
    """ Page de création d'un document
    """
    if element and ext:
        return Document(nom, element, ext).creer()
    else:
        return {'corps': b.template('creation', {'quoi': _('fichier')})}


@APP.post('/_creer/<nom>')
@APP.post('/_creer/<nom>/<element:path>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def document_creer(nom, element=''):
    """ Création effective du document
    """
    if rq.forms.action == 'creer':
        doc = rq.forms.nom.split('.')
        element, ext = element + '/' + '.'.join((doc[:-1])), doc[-1]
        return Document(nom, element, ext).creer()
    else:
        b.redirect(i18n_path('/{}/{}'.format(nom, element)))


@APP.get('/_creerdossier/<nom>')
@APP.get('/_creerdossier/<nom>/<element:path>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def dossier_creer_infos(nom, element=None):
    """ Page de création d'un dossier
    """
    if element:
        return Dossier(nom, element).creer()
    else:
        return {'corps': b.template('creation', {'quoi': _('dossier')})}


@APP.post('/_creerdossier/<nom>')
@APP.post('/_creerdossier/<nom>/<element:path>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def dossier_creer(nom, element=''):
    """ Création effective du dossier
    """
    if rq.forms.action == 'creer':
        return Dossier(nom, '/'.join((element, rq.forms.nom))).creer()
    else:
        b.redirect(i18n_path('/{}/{}'.format(nom, element)))


@APP.get('/_clonerprojet')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def projet_cloner_infos():
    """ Formulaire pour cloner un projet distant
    """
    return {'corps': b.template('clonage', {'quoi': _('projet')})}


@APP.post('/_clonerprojet')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def projet_cloner():
    """ Clonage effectif du projet
    """
    if rq.forms.action == 'cloner':
        return Projet(rq.forms.nom).cloner(rq.forms.origine)
    else:
        b.redirect(i18n_path('/_projets'))


@APP.get('/_creerprojet')
@APP.get('/_creerprojet/<nom>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def projet_creer_infos(nom=None):
    """ Page de création d'un projet
    """
    if nom:
        return Projet(nom).creer()
    else:
        return {'corps': b.template('creation', {'quoi': _('projet')})}


@APP.post('/_creerprojet')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def projet_creer():
    """ Création effective du projet
    """
    if rq.forms.action == 'creer':
        return Projet(rq.forms.nom).creer()
    else:
        b.redirect(i18n_path('/'))


# Déplacement d'un projet, dossier ou document
@APP.get('/_deplacer/<nom>')
@APP.get('/_deplacer/<nom>/<element:path>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def deplacer_infos(nom, element=None):
    """ Page de création d'un document
    """
    return {'corps': b.template(
        'deplacement',
        {
            'deplacement': _('Nouvel emplacement'),
            'action': ('deplacer', _('Déplacer')),
            'destination': nom + '/' + element
        }
        if element else
        {
            'deplacement': _('Nouveau nom'),
            'action': ('deplacer', _('Renommer')),
            'destination': nom
        }
    )}


@APP.post('/_deplacer/<nom>')
@APP.post('/_deplacer/<nom>/<element:path>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def deplacer(nom, element=None):
    """ Page de création d'un document
    """
    if rq.forms.action == "deplacer":
        if element:
            return Dossier(nom, element).deplacer(
                rq.forms.destination,
                ecraser=bool(rq.forms.ecraser)
            )
        else:
            return Projet(nom).renommer(rq.forms.destination)
    else:
        b.redirect(i18n_path(
            '/' + nom
            + ('/' + element if element else '')
        ))


# Déplacement d'un projet, dossier ou document
@APP.get('/_copier/<nom>')
@APP.get('/_copier/<nom>/<element:path>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def copier_infos(nom, element=None):
    """ Page de création d'un document
    """
    return {'corps': b.template(
        'deplacement',
        {
            'deplacement': _('Destination'),
            'action': ('copier', _('Copier')),
            'destination': nom + ('/' + element if element else '')
        }
    )}


@APP.post('/_copier/<nom>')
@APP.post('/_copier/<nom>/<element:path>')
@APP.post('/_copier/<nom>/<element:path>.<ext>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def copier(nom, element=None, ext=None):
    """ Page de création d'un document
    """
    if rq.forms.action == "copier":
        if element:
            try:
                return Dossier(nom, element).copier(
                    rq.forms.destination,
                    ecraser=bool(rq.forms.ecraser)
                )
            except (NotADirectoryError, FileNotFoundError) as err:
                f.traiter_erreur(err)
                print(nom, element, ext)
                return Document(nom, element, ext).copier(
                    rq.forms.destination,
                    ecraser=bool(rq.forms.ecraser)
                )
        else:
            return Projet(nom).copier(rq.forms.destination)
    else:
        b.redirect(i18n_path(
            '/' + nom
            + ('/' + element if element else '')
        ))


# Suppression d'un document
@APP.get('/_supprimer/<nom>/<element:path>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def document_supprimer_confirmation(nom, element=False):
    """Page de confirmation avant de supprimer un document
    """
    if not element:
        b.abort(404)
    else:
        return {'corps': b.template(
            'suppression',
            {'quoi': _('le fichier {}/{}').format(nom, element)}
        )}


@APP.post('/_supprimer/<nom>/<element:path>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def document_supprimer(nom, element=False):
    """Suppression effective du document
    """
    if not element:
        b.abort(404)
    else:
        if rq.forms.action == 'supprimer':
            element, ext = os.path.splitext(element)
            return Document(nom, element, ext[1:]).supprimer()
        else:
            b.redirect(i18n_path('/{}/{}'.format(nom, element)))


@APP.get('/_supprimerdossier/<nom>/<element:path>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def dossier_supprimer_confirmation(nom, element=False):
    """Page de confirmation avant de supprimer un dossier
    """
    if not element:
        b.abort(404)
    else:
        return {'corps': b.template(
            'suppression',
            {
                'quoi':
                    'le dossier {}/{} et tout son contenu ?'.format(
                        nom,
                        element
                    )
            }
        )}


@APP.post('/_supprimerdossier/<nom>/<element:path>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def dossier_supprimer(nom, element=False):
    """Suppression effective du dossier
    """
    if not element:
        b.abort(404)
    else:
        if rq.forms.action == 'supprimer':
            return Dossier(nom, element).supprimer()
        else:
            b.redirect(i18n_path('/{}/{}'.format(nom, element)))


@APP.get('/_supprimerprojet/<nom>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def projet_supprimer_confirmation(nom):
    """Page de confirmation avant de supprimer un projet
    """
    return {'corps': b.template(
        'suppression',
        {
            'quoi':
            _('le projet {} et tout son contenu ? ').format(nom)
            + _('Attention : cette opération est irréversible !')
        }
    )}


@APP.post('/_supprimerprojet/<nom>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def projet_supprimer(nom):
    """Suppression effective du projet
    """
    if rq.forms.action == 'supprimer':
        return Projet(nom).supprimer()
    else:
        b.redirect(i18n_path('/{}'.format(nom)))


# Envoi d'un fichier
@APP.get('/_envoyer/<nom>')
@APP.get('/_envoyer/<nom>/<element:path>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def document_envoyer_infos(nom, element=''):
    """Page où l'utilisateur est invité à choisir un fichier à envoyer vers
    un dossier"""
    return Dossier(nom, element).envoyer_fichier_infos()


@APP.post('/_envoyer/<nom>')
@APP.post('/_envoyer/<nom>/<element:path>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def document_envoyer(nom, element=''):
    """Envoi effectif du document"""
    if rq.forms.action == "envoi":
        return Dossier(nom, element).envoyer_fichier(
            rq.files.get('fichier'),
            ecraser=rq.forms.ecraser
        )
    elif rq.forms.action == 'annuler':
        b.redirect(i18n_path(
            '/' + nom + ('/' + element if element else '')
        ))
    else:
        return {
            'corps':
                _('Pourriez-vous expliciter votre intention ?')
                + '<br><br>'
                + '<br>'.join(':'.join(item) for item in rq.forms.items())
        }


# Emplacement inexistant
@APP.get('/_inexistant/<nom>')
@APP.get('/_inexistant/<nom>/<element:path>')
@APP.get('/_inexistant/<nom>/<element:path>.<ext>')
@page
def inexistant(nom, element=None, ext=None):  # pylint: disable=W0613
    """Page renvoyée pour proposer la création d'un emplacement inexistant
    """
    return {
        'corps': b.template('inexistant', {'element': element})
    }


@APP.post('/_inexistant/<nom>')
@APP.post('/_inexistant/<nom>/<element:path>')
@APP.post('/_inexistant/<nom>/<element:path>.<ext>')
def inexistant_creer(nom, element=None, ext=None):
    """ Création effective de l'élément en question
    """
    try:
        return {
            'dossier':  dossier_creer_infos,
            'document': document_creer_infos,
            'projet':   projet_creer_infos
        }[rq.forms.action](nom, element, ext)
    except KeyError as err:
        f.traiter_erreur(err)
        b.redirect(i18n_path('/'))


# Historique d'un document
@APP.get('/_historique/<nom>/<element:path>')
@page
def document_historique(nom, element):
    """Page affichant les modifications successives affectant un document
    """
    element, ext = os.path.splitext(element)
    if rq.query.commit:
        return Document(nom, element, ext[1:]).modification(rq.query.commit)
    else:
        # Ceci survient si l'on ne demande pas un commit précis.
        return Document(nom, element, ext[1:]).historique


@APP.post('/_retablir/<nom>/<element:path>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def document_retablir_commit(nom, element):
    """Retour à une version antérieure d'un document
    """
    element, ext = os.path.splitext(element)
    return Document(nom, element, ext[1:]).retablir(rq.forms.commit)


# Historique d'un projet
@APP.get('/_historique/<nom>')
@page
def projet_historique(nom):
    """Page affichant les modifications successives affectant un projet
    """
    if rq.query.commit:
        return Projet(nom).modification(rq.query.commit)
    else:
        # Ceci survient si l'on ne demande pas un commit précis.
        return Projet(nom).historique


@APP.post('/_retablir/<nom>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def projet_retablir_commit(nom):
    """Retour à une version antérieure de l'ensemble d'un projet
    """
    return Projet(nom).retablir(rq.forms.commit)


# Édition d'un document
@APP.get('/_editer/<nom>/<element:path>')
@APP.get('/_editer/<nom>/<element:path>.<ext>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def document_editer(nom, element='', ext=''):
    """ Page d'édition d'un document
    """
    return Document(nom, element, ext).editer()


# Export d'un document
@APP.get('/_exporter/<nom>/<element:path>.<ext>')
@page
def document_exporter_infos(nom, element='', ext=''):
    """ Page où l'utilisateur définit les propriétés du document à exporter"""
    return Document(nom, element, ext).exporter_infos(rq.query.fmt)


@APP.post('/_exporter/<nom>/<element:path>.<ext>')
@page
def document_exporter(nom, element='', ext=''):
    """ Page où l'utilisateur définit les propriétés du document à exporter"""
    if rq.forms.action == 'exporter':
        return Document(nom, element, ext).exporter(rq.query.fmt, rq.forms)
    else:
        b.redirect(i18n_path('/{}/{}.{}'.format(nom, element, ext)))


# Affichage de la source d'un document
@APP.get('/_src/<nom>/<element:path>.<ext>')
@page
def document_src(nom, element='', ext=''):
    """ Source d'un document
    """
    return Document(nom, element, ext).source


# Listing des dossiers et aperçu des documents
@APP.get('/<nom>')
@APP.get('/<nom>/<element:path>')
@APP.get('/<nom>/<element:path>.<ext>')
@page
def document_afficher(nom, element=None, ext=None):
    """ Affichage des fichiers et dossiers d'un projet

    Cette page renvoie :
        − la liste des fichiers si <element> pointe sur un dossier ;
        − la mise en forme du document s'il s'agit d'un fichier connu.
    #~ """
    try:
        if not element:
            return Projet(nom).lister()
        else:
            return Dossier(nom, element).lister()
    except TypeError as err:
        f.traiter_erreur(err)
        # Cette exception est levée s'il ne s'agit pas d'un dossier.
        try:
            return Document(nom, element, ext).contenu
        except FileNotFoundError as err:
            f.traiter_erreur(err)
            # Cette exception est levée s'il n'y a pas de document, ce qui
            # arrive notamment lorsque l'on renonce à créer un nouveau
            # document.
            b.redirect(i18n_path('/' + nom))
        except TypeError as err:
            f.traiter_erreur(err)
            # Cette exception est levée si l'on tente d'accéder à un
            # emplacement inexistant.
            b.redirect(i18n_path(
                '/_inexistant/'
                + nom
                + ('/' + element if element else "")
                + ('.' + ext if ext else "")
            ))
            raise


# Enregistrement des documents après édition
@APP.post('/<nom>/<element:path>')
@APP.post('/<nom>/<element:path>.<ext>')
@page
def document_enregistrer(nom, element='', ext=''):
    """Enregistrement d'un document
    """
    if rq.forms.action == 'enregistrer':
        Document(nom, element, ext).enregistrer(rq.forms.contenu)
    elif rq.forms.action == 'annuler':
        b.redirect(i18n_path(
            '/' + nom
            + ('/' + element if element else '')
            + ('.' + ext if ext else '')
        ))
    else:
        return {
            'corps':
                _('Pourriez-vous expliciter votre intention ?')
                + '<br><br>'
                + '<br>'.join(':'.join(item) for item in rq.forms.items())
        }


# III. Feuilles de style ########

@APP.get('/css')
@APP.get('/css/<ext>')
@b.view('style')
def css(ext=''):
    """ Feuilles de style."""
    return {'ext': ext}


# IV. pages d'erreur ########

@APP.error(code=401)
@page
def erreur_accesreserve(erreur):  # pylint: disable=W0613
    """Accès réservé

    Cette erreur est renvoyée lorsque quelqu'un tente d'accéder à une page
    réservée.
    """
    return {
        'corps':
            _('Accès réservé !')
            + h.BR() + h.BR()
            + h.A('Retour à la page précédente', href=rq['HTTP_REFERER'])
    }


@APP.error(code=404)
@page
def erreur_pageintrouvable(erreur):  # pylint: disable=W0613
    """Page introuvable

    Cette erreur est renvoyée lorsque quelqu'un tente d'accéder à une page
    qui n'existe pas.
    """
    return {'corps': _("Il n'y a rien ici !")}


# Traduction ##################################################################

WEBAPP = Traduction(
    APP,
    langs=cfg.LANGUES,
    default_locale=cfg.LANGUE,
    locale_dir=cfg.I18N,
    domain='musite'
)

# Lancement du serveur ########################################################

# En cours de développement ####
if cfg.DEVEL:
    # On active le débogage pour avoir des messages d'erreur plus explicites.
    b.debug(True)
    b.run(
        app=WEBAPP,
        host=cfg.HOTE,
        port=cfg.PORT,
        server='cherrypy',
        # Rechargement automatique du serveur, utile pendant le développement.
        reloader=True
    )
# En production ####
else:
    from deps.cherrypy.wsgiserver.wsgiserver3 import CherryPyWSGIServer
    SERVER = CherryPyWSGIServer(
        (cfg.HOTE, cfg.PORT),
        WEBAPP,
        server_name='Musite',
        numthreads=30)
    SERVER.start()
