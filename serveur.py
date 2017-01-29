#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Musite − wiki musical

Musite est une sorte de wiki, pensé pour gérer des documents contenant des
partitions de musique, mais adaptable à toutes sortes d'autres usages.

Ce fichier gère la partie interface du site, renvoyant les pages correspondant
aux urls saisies dans le navigateur.Si j'ai bien compris ce qu'est une vue
dans le modèle MVC, ce doit être à peu près ça.
"""

__appname__ = 'serveur'
__license__ = 'MIT'


# Import de librairies externes ###############################################

import os.path
import sys
from functools import wraps

LIB = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'deps')
sys.path.insert(0, str(LIB))
from deps.outils import Path, i18n_path, _
import bottle as b
b.BaseRequest.MEMFILE_MAX = 2048 * 2048
from bottle import request as rq
from deps.i18n import I18NPlugin as Traduction
from deps import HTMLTags as h
from deps.mistune import markdown

from deps.controleur import Projet, Dossier, Document, DocumentGabc
from deps import outils as f
from deps import auth as a
from deps import utilisateurs as u
from etc import config as cfg


# Paramètres bottle ###########################################################

b.TEMPLATE_PATH += [str(modele) for modele in cfg.MODELES]
APP = b.Bottle()


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
    @wraps(fonction)
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
        with (
            cfg.PAGES / 'md' / ('Accueil.' + rq.locale + '.md')
        ).open() as acc:
            corps = markdown(acc.read(-1))
    except FileNotFoundError as err:
        f.traiter_erreur(err)
        with cfg.PAGES / 'md' / 'Accueil.fr.md'.open() as acc:
            corps = markdown(acc.read(-1))
    return {
        'corps': corps,
        'actions': actions,
        'liens': liens,
        'recherche': '',
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
            _('Envoyer projet'): '_envoyerprojet',
        } \
            if a.authentifier(rq.auth[0], rq.auth[1]) \
            else {}
    except TypeError as err:
        f.traiter_erreur(err)
        # Cette exception est levée en l'absence d'authentification
        actions = {}
    listefichiers = [
        fichier.relative_to(cfg.DATA) for fichier in cfg.DATA.iterdir()
    ]
    # Formatage de la liste des fichiers.
    liste = [
        h.A(
            projet, href=i18n_path('/{}'.format(projet))
        )
        for projet in sorted(listefichiers)
        if (cfg.DATA / projet).is_dir()
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
            + (
                h.A(_('Retour à la page précédente'), href=rq['HTTP_REFERER'])
                if 'HTTP_REFERER' in rq else ''
            ),
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
            with (
                cfg.PAGES / 'md' / ('Admin.' + rq.locale + '.md')
            ).open() as adm:
                retour['corps'] = markdown(adm.read(-1))
        except FileNotFoundError as err:
            f.traiter_erreur(err)
            with (cfg.PAGES / 'md' / 'Admin.fr.md').open() as adm:
                retour['corps'] = markdown(adm.read(-1))
    return retour


@APP.post('/admin/groupes')
@b.auth_basic(a.admin, _('Vous devez être administrateur'))
def groupes():
    """Enregistrement des groupes
    """
    with (cfg.ETC / 'groupes').open('w') as grp:
        grp.write(rq.forms.decode().groupes)
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
    forms = rq.forms.decode()
    if forms.mdp == forms.mdp_v:
        utilisateur = u.Utilisateur(forms.nom, forms.mdp)
        try:
            utilisateur.ajouter()
        except u.UtilisateurExistant as err:
            f.traiter_erreur(err)
            utilisateur.modifier()
        except u.NomDUtilisateurRequis as err:
            f.traiter_erreur(err)
    b.redirect(i18n_path('/admin/utilisateurs'))


#   3. Fichiers statiques
@APP.get('/static')
@APP.get('/static/<chemin:path>')
def static(chemin='/'):
    """ Fichiers statiques
    """
    telecharger = True if rq.query.action == 'telecharger' else False
    document = b.static_file(
        str(Path(chemin)),
        root=str(cfg.STATIC),
        download=telecharger
    )
    if isinstance(document, b.HTTPError):
        document = b.static_file(
            str(Path(chemin + '/index.html')),
            root=str(cfg.STATIC),
            download=telecharger
        )
    return document


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
        doc = rq.forms.decode().nom.split('.')
        if len(doc) > 1:
            element, ext = element + '/' + '.'.join((doc[:-1])), doc[-1]
        else:
            element, ext = doc[0], ''
        return Document(nom, element, ext).creer()
    else:
        b.redirect(i18n_path('/{}/{}'.format(nom, element).replace('//', '/')))


@APP.get('/_creerdossier/<nom>')
@APP.get('/_creerdossier/<nom>/<element:path>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def dossier_creer_infos(nom, element=None, **args):  # pylint: disable=W0613
    """ Page de création d'un dossier
    """
    return {'corps': b.template('creation', {'quoi': _('dossier')})}


@APP.post('/_creerdossier/<nom>')
@APP.post('/_creerdossier/<nom>/<element:path>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def dossier_creer(nom, element=''):
    """ Création effective du dossier
    """
    if rq.forms.action == 'creer':
        return Dossier(nom, '/'.join((element, rq.forms.decode().nom))).creer()
    else:
        b.redirect(i18n_path('/{}/{}'.format(nom, element).replace('//', '/')))


@APP.get('/_rechercher')
@APP.get('/_rechercher/<nom>')
@APP.get('/_rechercher/<nom>/<element:path>')
@APP.post('/_rechercher')
@APP.post('/_rechercher/<nom>')
@APP.post('/_rechercher/<nom>/<element:path>')
@page
def dossier_rechercher(nom='', element=''):
    """Recherche d'une expression dans le nom ou le contenu des documents
    """
    if 'expr' in rq.forms:
        expression = rq.forms.decode().expr
        recherchenom = rq.forms.nom
        contenu = rq.forms.contenu
    else:
        expression = rq.query.expr if 'expr' in rq.query else '.*'
        recherchenom = contenu = True
    return Dossier(nom, element).rechercher(
        expression, nom=recherchenom, contenu=contenu
    )


@APP.get('/_telechargerdossier/<nom>')
@APP.get('/_telechargerdossier/<nom>/<element:path>')
@page
def dossier_telecharger_infos(nom, element=''):
    """ Page de téléchargement d'un dossier
    """
    return Dossier(nom, element).telecharger()


@APP.get('/_envoyerdossier/<nom>')
@APP.get('/_envoyerdossier/<nom>/<element:path>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def dossier_telecharger_envoi_infos(nom, element=''):
    """ Page d'envoi d'un dossier
    """
    return Dossier(nom, element).telecharger_envoi_infos()


@APP.post('/_envoyerdossier/<nom>')
@APP.post('/_envoyerdossier/<nom>/<element:path>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def dossier_telecharger_envoi(nom, element=''):
    """ Envoi effectif de l'archive
    """
    if rq.forms.action == 'envoi':
        return Dossier(
            nom, element
        ).telecharger_envoi(rq.files.get('fichier'))
    else:
        b.redirect(i18n_path('/{}/{}'.format(nom, element).replace('//', '/')))


@APP.get('/_clonerprojet')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def projet_cloner_infos():
    """ Formulaire pour cloner un projet distant
    """
    return {'corps': b.template('depot', {
        'action': ('cloner', _('Cloner')),
        'quoi': _('projet')
    })}


@APP.post('/_clonerprojet')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def projet_cloner():
    """ Clonage effectif du projet
    """
    forms = rq.forms.decode()
    if forms.action == 'cloner':
        return Projet(forms.nom).cloner(forms.origine)
    else:
        b.redirect(i18n_path('/_projets'))


@APP.get('/_envoyerprojet')
@APP.get('/_envoyerprojet/<nom>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def projet_telecharger_envoi_infos(nom=''):
    """ Page d'envoi d'un projet
    """
    return Projet(nom).telecharger_envoi_infos()


@APP.post('/_envoyerprojet')
@APP.post('/_envoyerprojet/<nom>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def projet_telecharger_envoi(nom=None):
    """ Envoi effectif de l'archive
    """
    nom = nom if nom else rq.forms.decode().nom
    if rq.forms.action == 'envoi':
        return Projet(nom).telecharger_envoi(archive=rq.files.get('fichier'))
    else:
        b.redirect(i18n_path('/_projets'))


@APP.get('/_creerprojet')
@APP.get('/_creerprojet/<nom>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def projet_creer_infos(nom=None, **args):  # pylint:disable=W0613
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
        return Projet(rq.forms.decode().nom).creer()
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
    forms = rq.forms.decode()
    if forms.action == "deplacer":
        if element:
            return Dossier(nom, element).deplacer(
                forms.destination,
                ecraser=bool(forms.ecraser)
            )
        else:
            return Projet(nom).renommer(forms.destination)
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
    forms = rq.forms.decode()
    if forms.action == "copier":
        if element:
            try:
                return Dossier(nom, element).copier(
                    forms.destination,
                    ecraser=bool(forms.ecraser)
                )
            except (NotADirectoryError, FileNotFoundError) as err:
                f.traiter_erreur(err)
                return Document(nom, element, ext).copier(
                    forms.destination,
                    ecraser=bool(forms.ecraser)
                )
        else:
            return Projet(nom).copier(forms.destination)
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
            {'quoi': _('le fichier {}/{} ?').format(nom, element)}
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
            b.redirect(
                i18n_path('/{}/{}'.format(nom, element).replace('//', '/'))
            )


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
            b.redirect(
                i18n_path('/{}/{}'.format(nom, element).replace('//', '/'))
            )


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


@APP.get('/_<action>projet/<nom>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def projet_action_infos(action, nom):
    """ Formulaire pour l'envoi/réception vers un dépôt distant
    """
    try:
        return {'corps': b.template('depot', {
            'action': (
                action,
                {'recevoir': _('Recevoir'), 'emettre': _('Envoyer')}[action]
            ),
            'origine': Projet(nom).depot.origine,
            'quoi': _('projet')
        })}
    except KeyError as err:
        f.traiter_erreur(err)
        b.abort(404)


@APP.post('/_<action>projet/<nom>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def projet_action(action, nom):
    """ Envoi/réception vers un dépôt distant
    """
    forms = rq.forms.decode()
    if action == 'recevoir' and forms.action == 'recevoir':
        return Projet(nom).recevoir(forms.origine)
    elif action == 'emettre' and forms.action == 'emettre':
        return Projet(nom).envoyer(
            forms.origine, forms.utilisateur, forms.mdp
        )
    else:
        b.redirect(Projet(nom).url)


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
                + '<br>'.join(
                    ':'.join(item) for item in rq.forms.decode().items()
                )
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
        }[rq.forms.action](nom=nom, element=element, ext=ext)
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


@APP.post('/_annuler/<nom>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def projet_annuler_commit(nom):
    """Annulation des changements d'une version antérieure
    """
    return Projet(nom).annuler(rq.forms.commit)


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


# Édition d'un document gabc : alternative pour débutants
@APP.get('/_gabc_editer/<nom>/<element:path>')
@APP.get('/_gabc_editer/<nom>/<element:path>.<ext>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def document_gabc_editer(nom, element='', ext=''):
    """ Page d'édition d'un document
    """
    return DocumentGabc(nom, element, ext).editer_gabc()


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
        return Document(
            nom, element, ext
        ).exporter(
            rq.query.fmt, rq.forms.decode()
        )
    else:
        b.redirect(i18n_path('/{}/{}.{}'.format(nom, element, ext)))


# Affichage de la source d'un document
@APP.get('/_src/<nom>/<element:path>.<ext>')
@page
def document_src(nom, element='', ext=''):
    """ Source d'un document
    """
    try:
        return Document(nom, element, ext).source
    except FileNotFoundError as err:
        f.traiter_erreur(err)
        # Cette exception est levée s'il n'y a pas de document, ce qui
        # arrive notamment lorsque l'on renonce à créer un nouveau
        # document.
        b.redirect(i18n_path('/' + nom))


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
            return Dossier(nom, element + ('.' + ext if ext else '')).lister()
    except (FileNotFoundError, NotADirectoryError) as err:
        f.traiter_erreur(err)
        # Cette exception est levée s'il ne s'agit pas d'un dossier.
        try:
            document = Document(nom, element, ext)
            actualiser = rq.query.act
            if actualiser:
                return document.contenu(actualiser=int(actualiser))
            else:
                return document.contenu()
        except (FileNotFoundError, TypeError) as err:
            f.traiter_erreur(err)
            # Cette exception est levée si l'on tente d'accéder à un
            # emplacement inexistant.
            b.redirect(i18n_path(
                '/_inexistant/'
                + nom
                + ('/' + element if element else "")
                + ('.' + ext if ext else "")
            ))


# Enregistrement des documents après édition
@APP.post('/<nom>/<element:path>')
@APP.post('/<nom>/<element:path>.<ext>')
@b.auth_basic(a.editeur, _('Réservé aux éditeurs'))
@page
def document_enregistrer(nom, element='', ext=''):
    """Enregistrement d'un document
    """
    if rq.forms.action == 'enregistrer':
        return Document(
            nom, element, ext
        ).enregistrer(
            rq.forms.decode().contenu
        )
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
                + '<br>'.join(
                    ':'.join(item) for item in rq.forms.decode().items()
                )
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
    locale_dir=str(cfg.I18N),
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
        # Rechargement automatique du serveur, utile pendant le développement.
        reloader=True
    )
# En production ####
else:
    from deps.wsgiserver import WSGIServer
    SERVER = WSGIServer(
        WEBAPP,
        host=cfg.HOTE,
        port=cfg.PORT,
        server_name='Musite',
        numthreads=30)
    SERVER.start()
