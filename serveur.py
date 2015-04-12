#!/usr/bin/python3

# Import de librairies externes ###############################################

import os
import sys
import shutil
from pkgutil import iter_modules
from importlib import import_module
sys.path.insert(0, 'deps')
import outils as f
import auth as a
import utilisateurs as u
import bottle as b
from bottle import request as rq
import HTMLTags as h
from mistune import markdown
from etc import config as cfg


# Paramètres bottle ###########################################################

b.TEMPLATE_PATH += cfg.MODELES
app = b.Bottle()


# Import des modules qui vont traiter chaque extension ########################
EXT = {
    e[1]: import_module('ext.' + e[1]) for e in iter_modules(path=['deps/ext'])
}
txt = EXT['txt']
md = EXT['md']


# Classes #####################################################################

class Document:
    def __init__(self, projet, element, ext):
        self.projet = projet
        self.element = element
        self.ext = ext
        self.chemin = '/'.join((projet, element + ('.' + ext if ext else '')))
        self.fichier = os.path.join(cfg.DATA, self.chemin.replace('/', os.sep))
        self.dossier = os.path.join(cfg.DATA, os.path.dirname(self.chemin))

    def afficher(self, contenu):
        actions = {
            'Aperçu': self.chemin,
            'Source': '_src/' + self.chemin
        }
        try:
            if a.authentifier(rq.auth[0], rq.auth[1]):
                actions['Éditer'] = '_editer/' + self.chemin
                actions['Supprimer'] = '_supprimer/' + self.chemin
        except TypeError:
            pass
        liens = {
            'Projet': self.projet,
            'Dossier': '/'.join(self.chemin.split('/')[:-1])
        }
        return {
            'corps': contenu,
            'actions': actions,
            'liens': liens,
        }

    @property
    def contenu(self):
        try:
            return self.afficher(EXT[self.ext].afficher(self.chemin))
        except (KeyError, AttributeError):
            # Si le type de document est inconnu ou ne prévoit pas d'affichage,
            # on essaie de le traiter comme un document texte.
            # Sinon, on abandonne.
            try:
                return self.afficher(txt.afficher(self.chemin))
            except txt.FichierIllisible:
                return self.afficher("Extension inconnue : {}.".format(e))
            except FileNotFoundError:
                b.abort(404)
        except EXT[self.ext].FichierIllisible:
            return self.afficher("Ce fichier est illisible.")

    @property
    def source(self):
        try:
            return self.afficher(EXT[self.ext].afficher_source(self.chemin))
        except (KeyError, AttributeError):
            # Si le type de document est inconnu ou ne prévoit pas d'affichage
            # de la source, on essaie de le traiter comme un document texte.
            # Sinon, on abandonne.
            try:
                return self.afficher(txt.afficher_source(chemin))
            except txt.FichierIllisible:
                return self.afficher(
                    "Extension inconnue : {}.".format(e)
                    + h.BR()
                    + 'Voici les données de la requète :'
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
            return self.afficher("Ce fichier est illisible.")

    def creer(self):
        print(self.projet, self.element, self.ext)
        if not os.path.exists(self.fichier):
            self.enregistrer('_')
        else:
            return self.editer()

    def supprimer(self):
        try:
            EXT[self.ext].supprimer(self.chemin)
        except KeyError:
            txt.supprimer(self.chemin)
        f.Depot(
            os.path.join(
                cfg.DATA, self.projet
            )
        ).sauvegardecomplete('Suppression du document {}'.format(self.chemin))
        return self.afficher('Document supprimé !')

    def editer(self):
        try:
            return self.afficher(EXT[self.ext].editer(self.chemin))
        except KeyError:
            # Si le type de document est inconnu, on essaie de le traiter
            # comme un document texte. Sinon, on abandonne.
            try:
                return self.afficher(txt.editer(self.chemin))
            except txt.FichierIllisible:
                return self.afficher("Ce type de document n'est pas éditable.")
        except AttributeError:
            # Si le type de document ne prévoit pas d'édition, on abandonne.
            return self.afficher("Ce type de document n'est pas éditable.")
        except EXT[self.ext].FichierIllisible:
            return self.afficher(
                '''Si je ne puis même pas lire ce fichier,
                comment voulez-vous que je l'édite ?'''
                )

    def enregistrer(self, contenu):
        try:
            EXT[self.ext].enregistrer(self.chemin, contenu)
        except AttributeError:
            txt.enregistrer(self.chemin, contenu)
        f.Depot(
            os.path.join(
                cfg.DATA, self.projet
            )
        ).sauvegardefichier(f.Fichier(self.fichier))
        b.redirect('/' + self.chemin)


class Dossier:
    def __init__(self, projet, element):
        self.projet = projet
        self.nom = element
        self.chemin = '/'.join((projet, element))
        self.dossier = os.path.join(cfg.DATA, self.chemin.replace('/', os.sep))

    def afficher(self, contenu):
        actions = {}
        try:
            if a.authentifier(rq.auth[0], rq.auth[1]):
                actions['Créer document'] = '_creer/' + self.chemin
                actions['Créer dossier'] = '_creerdossier/' + self.chemin
                actions['Supprimer'] = \
                    '_supprimerdossier/' + self.chemin
        except TypeError:
            pass
        liens = {
            'Projet': self.projet,
            'Parent': self.projet + (
                '/'.join(self.nom.split('/')[:-1])
            )
        }
        return {
            'corps': contenu,
            'actions': actions,
            'liens': liens,
        }

    def creer(self):
        os.makedirs(self.dossier, exist_ok=True)
        return self.lister()

    def lister(self):
        listefichiers = f.Dossier(self.dossier).lister(1)
        # Si l'on n'est pas à la racine, on affiche un lien vers le parent.
        try:
            if self.chemin[:-1] != self.projet:
                liste = [
                    h.A(
                        '../',
                        href='/{}'.format(
                            '/'.join(self.chemin.split('/')[:-1])
                        )
                    )
                ]
            else:
                liste = []
        # Si cette exception est levée, c'est que l'on est à la racine.
        except ValueError:
            liste = []
        # Formatage de la liste des fichiers.
        liste += [
            h.A(
                fichier + '/' if (
                    os.path.isdir(os.path.join(
                        self.dossier, fichier
                    ))
                ) else fichier,
                href='/{}/{}/{}'.format(
                    self.projet, self.nom, fichier
                ).replace('//', '/')
            )
            for fichier in listefichiers[self.dossier]
        ]
        return self.afficher(b.template('liste', liste=liste))

    def supprimer(self):
        shutil.rmtree(self.dossier, ignore_errors=True)
        f.Depot(
            os.path.join(
                cfg.DATA, self.projet
            )
        ).sauvegardecomplete('Suppression du dossier {}'.format(self.chemin))
        return self.afficher('Dossier supprimé !')


class Projet(Dossier):
    def __init__(self, projet):
        Dossier.__init__(self, projet, '')

    def afficher(self, contenu, suppression=False):
        actions = {}
        try:
            if a.authentifier(rq.auth[0], rq.auth[1]):
                if not suppression:
                    actions['Créer document'] = '_creer/' + self.chemin
                    actions['Créer dossier'] = '_creerdossier/' + self.chemin
                    actions['Supprimer'] = \
                        '_supprimerprojet/' + self.chemin
                else:
                    actions = {'Créer projet': '_creerprojet'}
        except TypeError:
            pass
        liens = {'Projet': self.projet}
        return {
            'corps': contenu,
            'actions': actions,
            'liens': liens,
        }

    def creer(self):
        try:
            os.makedirs(self.dossier, exist_ok=False)
            f.Depot(
                os.path.join(
                    cfg.DATA, self.projet
                )
            ).initialiser()
            return self.lister()
        except FileExistsError:
            return self.afficher('Ce projet existe déjà !')

    def supprimer(self):
        try:
            shutil.rmtree(self.dossier, ignore_errors=False)
            return self.afficher('Projet supprimé !', suppression=True)
        except FileNotFoundError:
            # Cette exception est levée quand le projet n'existe pas.
            return self.afficher('''C'est drôle, ce que vous me demandez :
                il n'y a pas de projet ici !''', suppression=True)


# Méthodes globales :  ########################################################


# I. Bidouille et décorateurs destinés à éviter les redondances ########

@app.hook('before_request')
def strip_path():
    rq.environ['PATH_INFO'] = rq.environ['PATH_INFO'].rstrip('/')


def page(fonction):
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
    """ Page d'accueil du site.
    """
    try:
        actions = {'Créer projet': '_creerprojet'} \
            if a.authentifier(rq.auth[0], rq.auth[1]) \
            else {}
    except TypeError:
        # Cette exception est levée en l'absence d'authentification
        actions = {}
    liens = {'Projets': '_projets'}
    return {
        'corps': md.afficher(
            os.path.join(cfg.PAGES, 'md', 'Accueil.md')),
        'actions': actions,
        'liens': liens
    }


@app.get('/_projets')
@page
def lister_projets():
    try:
        actions = {'Créer projet': '_creerprojet'} \
            if a.authentifier(rq.auth[0], rq.auth[1]) \
            else {}
    except TypeError:
        # Cette exception est levée en l'absence d'authentification
        actions = {}
    listefichiers = f.Dossier(cfg.DATA).lister(1)
    # Formatage de la liste des fichiers.
    liste = [
        h.A(
            projet, href='/{}'.format(projet)
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
@b.auth_basic(a.authentifier, 'Accès réservé')
@page
def authentifier(action=''):
    """ Page destinée à forcer l'authentification.
    """
    return {
        'corps': 'Bonjour, {} !'.format(rq.auth[0]),
    }


@app.get('/admin')
@app.get('/admin/<action>')
@b.auth_basic(a.admin, 'Vous devez être administrateur')
@page
def admin(action=''):
    """ Pages réservées à l'administrateur.
    """
    retour = {'actions': {'Utilisateurs': 'admin/utilisateurs'}}
    if action == 'utilisateurs':
        retour['corps'] = b.template('utilisateurs')
    else:
        retour['corps'] = \
            md.afficher(os.path.join(cfg.PAGES, 'md', 'Admin.md'))
    return retour


@app.get('/admin/supprimerutilisateur/<nom>')
@b.auth_basic(a.admin, 'Vous devez être administrateur')
def utilisateur_suppression(nom):
    u.Utilisateur(nom).supprimer()
    b.redirect('/admin/utilisateurs')


@app.post('/admin/utilisateurs')
@b.auth_basic(a.admin, 'Vous devez être administrateur')
def utilisateur_ajout():
    """ Ajout d'un nouvel utilisateur à la base.
    """
    print(rq.forms.nom, rq.forms.mdp, rq.forms.mdp_v)
    if rq.forms.mdp == rq.forms.mdp_v:
        u.Utilisateur(rq.forms.nom, rq.forms.mdp).ajouter()
    b.redirect('/admin/utilisateurs')


#   3. Fichiers statiques
@app.get('/static')
@app.get('/static/<chemin:path>')
def static(chemin='/'):
    """ Fichiers statiques.
    """
    telecharger = True if rq.query.action == 'telecharger' else False
    return b.static_file(
        chemin.replace('/', os.sep),
        root=os.path.join(cfg.PWD, cfg.STATIC),
        download=telecharger
    )


#   4. Pages de gestion de projets
#      Attention, l'ordre des méthodes est important.

# Création d'un document
@app.get('/_creer/<nom>')
@app.get('/_creer/<nom>/<element:path>')
@app.get('/_creer/<nom>/<element:path>.<ext>')
@b.auth_basic(a.editeur, 'Réservé aux éditeurs')
@page
def document_creer_infos(nom, element=None, ext=None):
    """ Page de création d'un document.
    """
    if element and ext:
        return Document(nom, element, ext).creer()
    else:
        return {'corps': b.template('creation', {'quoi': 'fichier'})}


@app.post('/_creer/<nom>')
@app.post('/_creer/<nom>/<element:path>')
@b.auth_basic(a.editeur, 'Réservé aux éditeurs')
@page
def document_creer(nom, element=''):
    """ Création effective du document.
    """
    doc = rq.forms.nom.split('.')
    element, ext = element + '/' + '.'.join((doc[:-1])), doc[-1]
    return Document(nom, element, ext).creer()


@app.get('/_creerdossier/<nom>')
@app.get('/_creerdossier/<nom>/<element:path>')
@b.auth_basic(a.editeur, 'Réservé aux éditeurs')
@page
def dossier_creer_infos(nom, element=''):
    """ Page de création d'un dossier.
    """
    return {'corps': b.template('creation', {'quoi': 'dossier'})}


@app.post('/_creerdossier/<nom>')
@app.post('/_creerdossier/<nom>/<element:path>')
@b.auth_basic(a.editeur, 'Réservé aux éditeurs')
@page
def dossier_creer(nom, element=''):
    """ Création effective du dossier.
    """
    return Dossier(nom, '/'.join((element, rq.forms.nom))).creer()


@app.get('/_creerprojet')
@b.auth_basic(a.editeur, 'Réservé aux éditeurs')
@page
def projet_creer_infos():
    """ Page de création d'un projet.
    """
    return {'corps': b.template('creation', {'quoi': 'projet'})}


@app.post('/_creerprojet')
@b.auth_basic(a.editeur, 'Réservé aux éditeurs')
@page
def projet_creer():
    """ Création effective du projet.
    """
    return Projet(rq.forms.nom).creer()


# Suppression d'un document
@app.get('/_supprimer/<nom>/<element:path>')
@b.auth_basic(a.editeur, 'Réservé aux éditeurs')
@page
def document_supprimer_confirmation(nom, element=False):
    if not element:
        b.abort(404)
    else:
        return {'corps': b.template(
            'suppression',
            {'quoi': 'le fichier {}/{}'.format(nom, element)}
        )}


@app.post('/_supprimer/<nom>/<element:path>')
@b.auth_basic(a.editeur, 'Réservé aux éditeurs')
@page
def document_supprimer(nom, element=False):
    if not element:
        b.abort(404)
    else:
        if rq.forms.action == 'supprimer':
            element, ext = os.path.splitext(element)
            return Document(nom, element, ext[1:]).supprimer()
        else:
            b.redirect('/{}/{}'.format(nom, element))


@app.get('/_supprimerdossier/<nom>/<element:path>')
@b.auth_basic(a.editeur, 'Réservé aux éditeurs')
@page
def dossier_supprimer_confirmation(nom, element=False):
    if not element:
        b.abort(404)
    else:
        return {'corps': b.template(
            'suppression',
            {'quoi': 'le dossier {}/{} et tout son contenu ?'
                .format(nom, element)}
        )}


@app.post('/_supprimerdossier/<nom>/<element:path>')
@b.auth_basic(a.editeur, 'Réservé aux éditeurs')
@page
def dossier_supprimer(nom, element=False):
    if not element:
        b.abort(404)
    else:
        if rq.forms.action == 'supprimer':
            return Dossier(nom, element).supprimer()
        else:
            b.redirect('/{}/{}'.format(nom, element))


@app.get('/_supprimerprojet/<nom>')
@b.auth_basic(a.editeur, 'Réservé aux éditeurs')
@page
def projet_supprimer_confirmation(nom):
    return {'corps': b.template(
        'suppression',
        {
            'quoi': 'le projet {} et tout son contenu ? '.format(nom)
                    + 'Attention : cette opération est irréversible !'
        }
    )}


@app.post('/_supprimerprojet/<nom>')
@b.auth_basic(a.editeur, 'Réservé aux éditeurs')
@page
def projet_supprimer(nom):
    if rq.forms.action == 'supprimer':
        return Projet(nom).supprimer()
    else:
        b.redirect('/{}'.format(nom))


# Édition d'un document
@app.get('/_editer/<nom>/<element:path>.<ext>')
@b.auth_basic(a.editeur, 'Réservé aux éditeurs')
@page
def document_editer(nom, element='', ext=''):
    """ Page d'édition d'un document.
    """
    return Document(nom, element, ext).editer()


# Affichage de la source d'un document
@app.get('/_src/<nom>/<element:path>.<ext>')
@page
def document_src(nom, element='', ext=''):
    """ Source d'un document.
    """
    return Document(nom, element, ext).source


# Listing des dossiers et aperçu des documents
@app.get('/<nom>')
@app.get('/<nom>/<element:path>')
@app.get('/<nom>/<element:path>.<ext>')
@page
def document_afficher(nom, element=None, ext=None):
    """ Affichage des fichiers et dossiers d'un projet.

    Cette page renvoie :
        − la liste des fichiers si <element> pointe sur un dossier ;
        − la mise en forme du document s'il s'agit d'un fichier connu.
    #~ """
    try:
        if not element:
            return Projet(nom).lister()
        else:
            return Dossier(nom, element).lister()
    except TypeError:    # Cette exception est levée s'il s'agit d'un document.
        return Document(nom, element, ext).contenu


# Enregistrement des documents après édition
@app.post('/<nom>/<element:path>.<ext>')
@page
def document_enregistrer(nom, element='', ext=''):
    if rq.forms.action == 'enregistrer':
        Document(nom, element, ext).enregistrer(rq.forms.contenu)
    else:
        return {'corps': 'Pourriez-vous expliciter votre intention ?'}


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
    return {'corps': 'Accès réservé !'}


@app.error(code=404)
@page
def erreur_pageintrouvable(erreur):
    return {'corps': "Il n'y a rien ici !"}


# Lancement du serveur ########################################################

# En cours de développement ####
if cfg.DEVEL:
    # On active le débogage pour avoir des messages d'erreur plus explicites.
    b.debug(True)
    b.run(
        app=app,
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
        app,
        server_name='Musite',
        numthreads=30)
    server.start()
