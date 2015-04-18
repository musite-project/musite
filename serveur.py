#!/usr/bin/python3

# Import de librairies externes ###############################################

import os
import sys
import shutil
import re
from subprocess import CalledProcessError
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

class Depot:
    def __init__(self, projet):
        self.projet = projet
        self.depot = f.Depot(os.path.join(cfg.DATA, projet))

    def initialiser(self):
        self.depot.initialiser()

    def comparer(self, commit, commitb=None, fichier=''):
        if not commitb:
            commitb = commit
            commit += '^'
        try:
            modification = b.html_escape(
                '\n'.join(self.depot.comparer(commit, commitb, fichier=fichier))
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
            return "Il n'y a rien avant la création !"

    def historique(self, fichier=None):
        try:
            if fichier:
                tableau = self.depot.journalfichier(fichier)
            else:
                tableau = self.depot.journalcomplet
        except CalledProcessError:
            return "Il n'y a pas encore de modifications à signaler."
        for element in tableau[1:]:
            element[0] = h.A(element[0], href='?commit=' + element[0])
            element[1] = re.sub('\<.*\>', '', element[1])
        return b.template('tableau', tableau=tableau)

    def annuler(self, commit):
        self.depot.annuler(commit)

    def retablir(self, commit, fichier=None, auteur=None):
        self.depot.retablir(commit, fichier)


class Document:
    def __init__(self, projet, element, ext):
        self.projet = projet
        self.element = element
        self.ext = ext
        self.chemin = '/'.join((projet, element + ('.' + ext if ext else '')))
        self.fichier = os.path.join(cfg.DATA, self.chemin.replace('/', os.sep))
        self.dossier = os.path.join(cfg.DATA, os.path.dirname(self.chemin))
        self.depot = Depot(self.projet)

    def afficher(self, contenu):
        actions = {
            'Aperçu': self.chemin,
            'Historique': '_historique/' + self.chemin,
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
            return self.afficher(EXT[self.ext].Document(self.chemin).afficher())
        except (KeyError, AttributeError):
            # Si le type de document est inconnu ou ne prévoit pas d'affichage,
            # on essaie de le traiter comme un document texte.
            # Sinon, on abandonne.
            try:
                return self.afficher(txt.Document(self.chemin).afficher())
            except txt.FichierIllisible:
                return self.afficher("Extension inconnue : {}.".format(e))
            except FileNotFoundError:
                b.abort(404)
        except EXT[self.ext].FichierIllisible:
            return self.afficher("Ce fichier est illisible.")

    @property
    def source(self):
        try:
            return self.afficher(EXT[self.ext].Document(self.chemin).afficher_source())
        except (KeyError, AttributeError):
            # Si le type de document est inconnu ou ne prévoit pas d'affichage
            # de la source, on essaie de le traiter comme un document texte.
            # Sinon, on abandonne.
            try:
                return self.afficher(txt.Document(self.chemin).afficher_source())
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
        return self.editer(creation=True)

    def supprimer(self):
        try:
            EXT[self.ext].Document(self.chemin).supprimer()
        except KeyError:
            txt.Document(self.chemin).supprimer()
        f.Depot(
            os.path.join(
                cfg.DATA, self.projet
            )
        ).sauvegardecomplete(
            'Suppression du document {}'.format(self.chemin),
            rq.auth[0]
        )
        return self.afficher('Document supprimé !')

    def editer(self, creation=False):
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
            EXT[self.ext].Document(self.chemin).enregistrer(contenu)
        except AttributeError:
            txt.Document(self.chemin).enregistrer(self.chemin)
        f.Depot(
            os.path.join(
                cfg.DATA, self.projet
            )
        ).sauvegardefichier(f.Fichier(self.fichier), rq.auth[0])
        b.redirect('/' + self.chemin)

    @property
    def historique(self):
        return self.afficher(self.depot.historique(self.fichier))

    def modification(self, commit):
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
        self.depot.retablir(commit, f.Fichier(self.fichier), rq.auth[0])
        b.redirect('/_historique/' + self.chemin)


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
        ).sauvegardecomplete(
            'Suppression du dossier {}'.format(self.chemin),
            rq.auth[0]
        )
        return self.afficher('Dossier supprimé !')


class Projet(Dossier):
    def __init__(self, projet):
        Dossier.__init__(self, projet, '')
        self.projet = projet
        self.depot = Depot(self.projet)

    def afficher(self, contenu, suppression=False):
        actions = {'Historique': '_historique/' + self.chemin}
        try:
            if a.authentifier(rq.auth[0], rq.auth[1]):
                if not suppression:
                    actions['Créer document'] = '_creer/' + self.chemin
                    actions['Créer dossier'] = '_creerdossier/' + self.chemin
                    actions['Supprimer'] = \
                        '_supprimerprojet/' + self.chemin
                else:
                    actions['Créer projet'] = '_creerprojet'
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
            self.depot.initialiser()
            return self.lister()
        except FileExistsError:
            return self.afficher('Ce projet existe déjà !')

    @property
    def historique(self):
        return self.afficher(self.depot.historique())

    def modification(self, commit):
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
        self.depot.retablir(commit)
        b.redirect('/_historique/' + self.chemin)

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
        'corps': md.Document(
            os.path.join(cfg.PAGES, 'md', 'Accueil.md')).afficher(),
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


@app.get('/favicon.ico')
def favicon():
    """Icône du site.
    """
    return static('img/favicon.ico')


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
    element, ext = element + '.'.join((doc[:-1])), doc[-1]
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


# Historique d'un document
@app.get('/_historique/<nom>/<element:path>')
@page
def document_historique(nom, element):
    element, ext = os.path.splitext(element)
    if rq.query.commit:
        return Document(nom, element, ext[1:]).modification(rq.query.commit)
    else:
        # Ceci survient si l'on ne demande pas un commit précis.
        return Document(nom, element, ext[1:]).historique


@app.post('/_retablir/<nom>/<element:path>')
@b.auth_basic(a.editeur, 'Réservé aux éditeurs')
@page
def document_retablir_commit(nom, element):
    element, ext = os.path.splitext(element)
    return Document(nom, element, ext[1:]).retablir(rq.forms.commit)


# Historique d'un projet
@app.get('/_historique/<nom>')
@page
def projet_historique(nom):
    if rq.query.commit:
        return Projet(nom).modification(rq.query.commit)
    else:
        # Ceci survient si l'on ne demande pas un commit précis.
        return Projet(nom).historique


@app.post('/_retablir/<nom>')
@b.auth_basic(a.editeur, 'Réservé aux éditeurs')
@page
def projet_retablir_commit(nom):
    return Projet(nom).retablir(rq.forms.commit)


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
        try:
            return Document(nom, element, ext).contenu
        except FileNotFoundError:
            # Cette exception est levée s'il n'y a pas de document, ce qui
            # arrive notamment lorsque l'on renonce à créer un nouveau
            # document.
            b.redirect('/' + nom)


# Enregistrement des documents après édition
@app.post('/<nom>/<element:path>.<ext>')
@page
def document_enregistrer(nom, element='', ext=''):
    if rq.forms.action == 'enregistrer':
        Document(nom, element, ext).enregistrer(rq.forms.contenu)
    elif rq.forms.action == 'annuler':
        b.redirect(
            '/' + nom
            + ('/' + element if element else '')
            + ('.' + ext if ext else '')
        )
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
