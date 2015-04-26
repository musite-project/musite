#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Musite − wiki musical

Musite est une sorte de wiki, pensé pour gérer des documents contenant des
partitions de musique, mais adaptable à toutes sortes d'autres usages.

Ce fichier gère la partie interface du site, renvoyant les pages
correspondant aux urls saisies dans le navigateur.
"""

__appname__ = 'serveur'
__license__ = 'GPLv2'


# Import de librairies externes ###############################################

import os
import sys
LIB = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'deps')
sys.path.insert(0, LIB)
import shutil
import re
from subprocess import CalledProcessError
from pkgutil import iter_modules
from importlib import import_module
import outils as f
from outils import i18n_path, _
import auth as a
import utilisateurs as u
import bottle as b
from bottle import request as rq
import HTMLTags as h
from deps.i18n import I18NPlugin as Traduction
from mistune import markdown
from etc import config as cfg


# Paramètres bottle ###########################################################

b.TEMPLATE_PATH += cfg.MODELES
app = b.Bottle()


# Import des modules qui vont traiter chaque extension ########################
EXT = {
    e[1]: import_module('ext.' + e[1])
    for e in iter_modules(path=[os.path.join(LIB, 'ext')])
}
txt = EXT['txt']
md = EXT['md']


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

    def initialiser(self):
        """Initialisation d'un nouveau dépôt."""
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
                'index.*\n.*\n\+\+\+ b/(.*)',
                str(h.B(h.I('{}'))).format(h.A('\\1', href='\\1')),
                modification
            )
            modification = re.sub(
                '(@@.*@@)', '\n{}\n'.format(h.B(h.I('\\1'))), modification
            )
            return h.CODE(modification)
        except CalledProcessError:
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
        except CalledProcessError:
            return _("Il n'y a pas encore de modifications à signaler.")
        for element in tableau[1:]:
            element[0] = h.A(element[0], href='?commit=' + element[0])
            element[1] = re.sub('\<.*\>', '', element[1])
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
                actions[_('Éditer')] = '_editer/' + self.chemin
                actions[_('Supprimer')] = '_supprimer/' + self.chemin
        except TypeError:
            pass
        liens = {
            _('Projet'): self.projet,
            _('Dossier'): '/'.join(self.chemin.split('/')[:-1])
        }
        exports = {
            fmt: self.chemin + '?fmt=' + fmt
            for fmt in EXT[self.ext].Document(self.chemin).fmt
        }
        return {
            'corps': contenu,
            'actions': actions,
            'exports': exports,
            'liens': liens,
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
        except (KeyError, AttributeError):
            # Si le type de document est inconnu ou ne prévoit pas d'affichage,
            # on essaie de le traiter comme un document texte.
            # Sinon, on abandonne.
            try:
                return self.afficher(txt.Document(self.chemin).afficher())
            except txt.FichierIllisible:
                return self.afficher(_("Extension inconnue : {}.").format(e))
            except FileNotFoundError:
                b.abort(404)
        except EXT[self.ext].FichierIllisible:
            return self.afficher(_("Ce fichier est illisible."))

    @property
    def source(self):
        """Affichage de la source du document
        """
        try:
            return self.afficher(
                EXT[self.ext].Document(self.chemin).afficher_source()
            )
        except (KeyError, AttributeError):
            # Si le type de document est inconnu ou ne prévoit pas d'affichage
            # de la source, on essaie de le traiter comme un document texte.
            # Sinon, on abandonne.
            try:
                return self.afficher(
                    txt.Document(self.chemin).afficher_source()
                )
            except txt.FichierIllisible:
                return self.afficher(
                    _("Extension inconnue : {}.").format(e)
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
            except NameError:
                b.abort(404)
        except EXT[self.ext].FichierIllisible:
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
        except KeyError:
            txt.Document(self.chemin).supprimer()
        f.Depot(
            os.path.join(
                cfg.DATA, self.projet
            )
        ).sauvegardecomplete(
            _('Suppression du document {}').format(self.chemin),
            rq.auth[0]
        )
        return self.afficher(_('Document supprimé !'))

    def editer(self, creation=False):
        """Édition du document
        """
        try:
            return self.afficher(
                EXT[self.ext].Document(self.chemin).editer(creation)
            )
        except KeyError:
            # Si le type de document est inconnu, on essaie de le traiter
            # comme un document texte. Sinon, on abandonne.
            try:
                return self.afficher(
                    txt.Document(self.chemin).editer(creation)
                )
            except txt.FichierIllisible:
                return self.afficher(
                    _("Ce type de document n'est pas éditable.")
                )
        except AttributeError:
            # Si le type de document ne prévoit pas d'édition, on abandonne.
            return self.afficher(_("Ce type de document n'est pas éditable."))
        except EXT[self.ext].FichierIllisible:
            return self.afficher(
                '''Si je ne puis même pas lire ce fichier,
                comment voulez-vous que je l'édite ?'''
                )

    def enregistrer(self, contenu):
        """Enregistrement du document
        """
        try:
            EXT[self.ext].Document(self.chemin).enregistrer(contenu)
        except AttributeError:
            txt.Document(self.chemin).enregistrer(self.chemin)
        f.Depot(
            os.path.join(
                cfg.DATA, self.projet
            )
        ).sauvegardefichier(f.Fichier(self.fichier), rq.auth[0])
        b.redirect(i18n_path('/' + self.chemin))

    def exporter(self, fmt, proprietes):
        proprietes = {fmt: proprietes}
        try:
            b.redirect(
                i18n_path(EXT[self.ext]\
                    .Document(self.chemin, proprietes=proprietes)\
                    .pdf('tmp', f.motaleatoire(3))
                + '?action=telecharger'
                )
            )
        except EXT[self.ext].ErreurCompilation:
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
        return self.afficher(b.template(
            'export',
            {'proprietes': EXT[self.ext].Document(self.chemin).listeproprietes[fmt]}
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

    def afficher(self, contenu):
        """Propriétés communes des pages de gestion de dossiers

        Cette méthode définit en particulier ce qui apparaît dans le menu.
        C'est ici qu'il faut définir ce qui est commun à toutes les pages
        proposant une opération sur un dossier.
        """
        actions = {}
        try:
            if a.authentifier(rq.auth[0], rq.auth[1]):
                actions[_('Créer document')] = '_creer/' + self.chemin
                actions[_('Créer dossier')] = '_creerdossier/' + self.chemin
                actions[_('Supprimer')] = \
                    '_supprimerdossier/' + self.chemin
        except TypeError:
            pass
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
        except ValueError:
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
        return self.afficher(b.template('liste', liste=liste))

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
                    actions[_('Supprimer')] = \
                        '_supprimerprojet/' + self.chemin
                else:
                    actions[_('Créer projet')] = '_creerprojet'
        except TypeError:
            pass
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
            return self.lister()
        except FileExistsError:
            return self.afficher(_('Ce projet existe déjà !'))

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
        except FileNotFoundError:
            # Cette exception est levée quand le projet n'existe pas.
            return self.afficher(_('''C'est drôle, ce que vous me demandez :
                il n'y a pas de projet ici !'''), suppression=True)


# Méthodes globales :  ########################################################


# I. Bidouille et décorateurs destinés à éviter les redondances ########

@app.hook('before_request')
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
        contenu = fonction(*arguments, **parametres)
        contenu['rq'] = rq
        return b.template('page', contenu)
    return afficher


# II. pages du site ########

#   1. Accueil
@app.get('/')
@page
def accueil():
    """ Page d'accueil du site
    """
    try:
        actions = {_('Créer projet'): '_creerprojet'} \
            if a.authentifier(rq.auth[0], rq.auth[1]) \
            else {}
    except TypeError:
        # Cette exception est levée en l'absence d'authentification
        actions = {}
    liens = {_('Projets'): '_projets'}
    try:
        with open(os.path.join(
            cfg.PAGES,
            'md',
            'Accueil.{}.md'.format(i18n_path('/').replace('/', ''))
        ), 'r') as f:
            corps = markdown(f.read(-1))
    except FileNotFoundError:
        with open(os.path.join(cfg.PAGES, 'md', 'Accueil.fr.md'), 'r') as f:
            corps = markdown(f.read(-1))
    return {
        'corps': corps,
        'actions': actions,
        'liens': liens
    }


@app.get('/_projets')
@page
def lister_projets():
    """Liste des projets existants
    """
    try:
        actions = {_('Créer projet'): '_creerprojet'} \
            if a.authentifier(rq.auth[0], rq.auth[1]) \
            else {}
    except TypeError:
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
@app.get('/authentification')
@app.get('/authentification/<action>')
@b.auth_basic(a.authentifier, _('Accès réservé'))
@page
def authentifier(action=''):
    """ Page destinée à forcer l'authentification.
    """
    return {
        'corps': _('Bonjour, {} !').format(rq.auth[0]),
    }


@app.get('/admin')
@app.get('/admin/<action>')
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
                'Admin.{}.md'.format(i18n_path('/').replace('/', ''))
            ), 'r') as f:
                retour['corps'] = markdown(f.read(-1))
        except FileNotFoundError:
            with open(os.path.join(cfg.PAGES, 'md', 'Admin.fr.md'), 'r') as f:
                retour['corps'] = markdown(f.read(-1))
    return retour


@app.get('/admin/supprimerutilisateur/<nom>')
@b.auth_basic(a.admin, _('Vous devez être administrateur'))
def utilisateur_suppression(nom):
    """Suppression d'un utilisateur
    """
    u.Utilisateur(nom).supprimer()
    b.redirect(i18n_path('/admin/utilisateurs'))


@app.post('/admin/utilisateurs')
@b.auth_basic(a.admin, _('Vous devez être administrateur'))
def utilisateur_ajout():
    """ Ajout d'un nouvel utilisateur à la base
    """
    if rq.forms.mdp == rq.forms.mdp_v:
        u.Utilisateur(rq.forms.nom, rq.forms.mdp).ajouter()
    b.redirect(i18n_path('/admin/utilisateurs'))


#   3. Fichiers statiques
@app.get('/static')
@app.get('/static/<chemin:path>')
def static(chemin='/'):
    """ Fichiers statiques
    """
    telecharger = True if rq.query.action == 'telecharger' else False
    return b.static_file(
        chemin.replace('/', os.sep),
        root=os.path.join(cfg.PWD, cfg.STATIC),
        download=telecharger
    )


@app.get('/favicon.ico')
def favicon():
    """Icône du site
    """
    return static('img/favicon.ico')


#   4. Pages de gestion de projets
#      Attention, l'ordre des méthodes est important.

# Création d'un document
@app.get('/_creer/<nom>')
@app.get('/_creer/<nom>/<element:path>')
@app.get('/_creer/<nom>/<element:path>.<ext>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def document_creer_infos(nom, element=None, ext=None):
    """ Page de création d'un document
    """
    if element and ext:
        return Document(nom, element, ext).creer()
    else:
        return {'corps': b.template('creation', {'quoi': _('fichier')})}


@app.post('/_creer/<nom>')
@app.post('/_creer/<nom>/<element:path>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def document_creer(nom, element=''):
    """ Création effective du document
    """
    if rq.forms.action == 'creer':
        doc = rq.forms.nom.split('.')
        element, ext = element + '.'.join((doc[:-1])), doc[-1]
        return Document(nom, element, ext).creer()
    else:
        b.redirect(i18n_path('/{}/{}'.format(nom, element)))


@app.get('/_creerdossier/<nom>')
@app.get('/_creerdossier/<nom>/<element:path>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def dossier_creer_infos(nom, element=''):
    """ Page de création d'un dossier
    """
    return {'corps': b.template('creation', {'quoi': _('dossier')})}


@app.post('/_creerdossier/<nom>')
@app.post('/_creerdossier/<nom>/<element:path>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def dossier_creer(nom, element=''):
    """ Création effective du dossier
    """
    if rq.forms.action == 'creer':
        return Dossier(nom, '/'.join((element, rq.forms.nom))).creer()
    else:
        b.redirect(i18n_path('/{}/{}'.format(nom, element)))


@app.get('/_creerprojet')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def projet_creer_infos():
    """ Page de création d'un projet
    """
    return {'corps': b.template('creation', {'quoi': _('projet')})}


@app.post('/_creerprojet')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def projet_creer():
    """ Création effective du projet
    """
    if rq.forms.action == 'creer':
        return Projet(rq.forms.nom).creer()
    else:
        b.redirect(i18n_path('/'))


# Suppression d'un document
@app.get('/_supprimer/<nom>/<element:path>')
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


@app.post('/_supprimer/<nom>/<element:path>')
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


@app.get('/_supprimerdossier/<nom>/<element:path>')
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
            {'quoi': 'le dossier {}/{} et tout son contenu ?'
                .format(nom, element)}
        )}


@app.post('/_supprimerdossier/<nom>/<element:path>')
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


@app.get('/_supprimerprojet/<nom>')
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


@app.post('/_supprimerprojet/<nom>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def projet_supprimer(nom):
    """Suppression effective du projet
    """
    if rq.forms.action == 'supprimer':
        return Projet(nom).supprimer()
    else:
        b.redirect(i18n_path('/{}'.format(nom)))


# Historique d'un document
@app.get('/_historique/<nom>/<element:path>')
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


@app.post('/_retablir/<nom>/<element:path>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def document_retablir_commit(nom, element):
    """Retour à une version antérieure d'un document
    """
    element, ext = os.path.splitext(element)
    return Document(nom, element, ext[1:]).retablir(rq.forms.commit)


# Historique d'un projet
@app.get('/_historique/<nom>')
@page
def projet_historique(nom):
    """Page affichant les modifications successives affectant un projet
    """
    if rq.query.commit:
        return Projet(nom).modification(rq.query.commit)
    else:
        # Ceci survient si l'on ne demande pas un commit précis.
        return Projet(nom).historique


@app.post('/_retablir/<nom>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def projet_retablir_commit(nom):
    """Retour à une version antérieure de l'ensemble d'un projet
    """
    return Projet(nom).retablir(rq.forms.commit)


# Édition d'un document
@app.get('/_editer/<nom>/<element:path>.<ext>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def document_editer(nom, element='', ext=''):
    """ Page d'édition d'un document
    """
    return Document(nom, element, ext).editer()


# Export d'un document
@app.get('/_exporter/<nom>/<element:path>.<ext>')
@page
def document_exporter_infos(nom, element='', ext=''):
    """ Page où l'utilisateur définit les propriétés du document à exporter"""
    return Document(nom, element, ext).exporter_infos(rq.query.fmt)


@app.post('/_exporter/<nom>/<element:path>.<ext>')
@page
def document_exporter(nom, element='', ext=''):
    """ Page où l'utilisateur définit les propriétés du document à exporter"""
    if rq.forms.action == 'exporter':
        return Document(nom, element, ext).exporter(rq.query.fmt, rq.forms)
    else:
        b.redirect(i18n_path('/{}/{}.{}'.format(nom, element, ext)))


# Affichage de la source d'un document
@app.get('/_src/<nom>/<element:path>.<ext>')
@page
def document_src(nom, element='', ext=''):
    """ Source d'un document
    """
    return Document(nom, element, ext).source


# Listing des dossiers et aperçu des documents
@app.get('/<nom>')
@app.get('/<nom>/<element:path>')
@app.get('/<nom>/<element:path>.<ext>')
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
    except TypeError:
        # Cette exception est levée s'il ne s'agit pas d'un dossier.
        try:
            return Document(nom, element, ext).contenu
        except FileNotFoundError as e:
            # Cette exception est levée s'il n'y a pas de document, ce qui
            # arrive notamment lorsque l'on renonce à créer un nouveau
            # document.
            b.redirect(i18n_path('/' + nom))
            print(e)
        except TypeError as e:
            # Cette exception est levée si l'on tente d'accéder à un
            # emplacement inexistant.
            raise
            b.abort(404)


# Enregistrement des documents après édition
@app.post('/<nom>/<element:path>.<ext>')
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

@app.get('/css')
@app.get('/css/<ext>')
@b.view('style')
def css(ext=''):
    """ Feuilles de style."""
    return {'ext': ext}


# IV. pages d'erreur ########

@app.error(code=401)
@page
def erreur_accesreserve(erreur):
    """Accès réservé

    Cette erreur est renvoyée lorsque quelqu'un tente d'accéder à une page
    réservée.
    """
    return {'corps': _('Accès réservé !')}


@app.error(code=404)
@page
def erreur_pageintrouvable(erreur):
    """Page introuvable

    Cette erreur est renvoyée lorsque quelqu'un tente d'accéder à une page
    qui n'existe pas.
    """
    return {'corps': _("Il n'y a rien ici !")}


# Traduction ##################################################################

webapp = Traduction(
    app,
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
        app=webapp,
        host=cfg.HOTE,
        port=cfg.PORT,
        server='cherrypy',
        # Rechargement automatique du serveur, utile pendant le développement.
        reloader=True
    )
# En production ####
else:
    from cherrypy.wsgiserver import CherryPyWSGIServer
    server = CherryPyWSGIServer(
        (cfg.HOTE, cfg.PORT),
        webapp,
        server_name='Musite',
        numthreads=30)
    server.start()
