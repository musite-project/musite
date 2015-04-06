#!/usr/bin/python3

# Import de librairies externes ###############################################

import os
import sys
from pkgutil import iter_modules
from importlib import import_module
sys.path.insert(0, 'deps')
import outils as f
import auth as a
import bottle as b
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


# Classes : gestion des documents et des dossiers #############################

class Document:
    def __init__(self, projet, element, ext):
        self.projet = projet
        self.element = element
        self.ext = ext
        self.chemin = '/'.join((projet, element + ('.' + ext if ext else '')))
        self.fichier = os.path.join(cfg.DATA, self.chemin.replace('/', os.sep))
        self.dossier = os.path.join(cfg.DATA, os.path.dirname(self.chemin))

    def afficher(self, contenu):
        return {
            'corps': contenu,
            'actions': {
                'Aperçu': self.chemin,
                'Source': '_src/' + self.chemin,
                'Éditer': '_editer/' + self.chemin,
            },
            'liens': {
                'Projet': self.projet,
                'Dossier': self.projet + (
                    '/'.join('/'.split(self.element)[:-1])
                )
            },
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
                            for item in b.request.query.items()
                        )
                    )
                )
        except EXT[self.ext].FichierIllisible:
            return self.afficher("Ce fichier est illisible.")

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

    def lister(self):
        listefichiers = f.Dossier(self.dossier).lister(1)
        # Si l'on n'est pas à la racine, on affiche un lien vers le parent.
        try:
            liste = [
                h.A(
                    '../',
                    href='/{projet}/{dossier}'.format(
                        projet=self.projet,
                        dossier='/'.join('/'.split(self.nom)[:-1])
                    )
                )
            ]
        # Si cette exception est levée, c'est que l'on est à la racine.
        except ValueError:
            liste = []
        # Formatage de la liste des fichiers.
        liste += [
            h.A(
                fichier + '/' if (
                    os.path.isdir(os.path.join(
                        cfg.DATA, self.projet, fichier
                    ))
                ) else fichier,
                href='/{}/{}/{}'.format(
                    self.projet, self.nom, fichier
                ).replace('//', '/')
            )
            for fichier in listefichiers[self.dossier]
        ]
        return {
            'corps': b.template('liste', liste=liste)
        }


# Méthodes globales :  ########################################################

@app.hook('before_request')
def strip_path():
    b.request.environ['PATH_INFO'] = b.request.environ['PATH_INFO'].rstrip('/')


# I. pages du site ########

#   1. Accueil
@app.get('/')
@b.view('page')
def accueil():
    """ Page d'accueil du site.
    """
    return {
        'corps': md.afficher(
            os.path.join(cfg.PAGES, 'md', 'Accueil.md'))
    }


#   2. Administration
@app.get('/admin')
@app.get('/admin/<action>')
@b.auth_basic(a.administrateur)
@b.view('page')
def admin(action='utilisateurs'):
    """ Pages réservées à l'administrateur.
    """
    return {
        'corps': md.afficher(
            os.path.join(cfg.PAGES, 'md', 'Admin.md'))
    }


#   3. Fichiers statiques
@app.get('/static')
@app.get('/static/<chemin:path>')
def static(chemin='/'):
    """ Fichiers statiques.
    """
    telecharger = True if b.request.query.action == 'telecharger' else False
    return b.static_file(
        chemin.replace('/', os.sep),
        root=cfg.STATIC,
        download=telecharger
    )


#   4. Pages de gestion de projets
#      Attention, l'ordre des méthodes est important.

# Édition d'un document
@app.get('/_editer/<nom>/<element:path>.<ext>')
@b.auth_basic(a.editeur)
@b.view('page')
def document_editer(nom, element='', ext=''):
    """ Page d'édition d'un document.
    """
    return Document(nom, element, ext).editer()


# Affichage de la source d'un document
@app.get('/_src/<nom>/<element:path>.<ext>')
@b.view('page')
def document_src(nom, element='', ext=''):
    """ Source d'un document.
    """
    return Document(nom, element, ext).source


# Listing des dossiers et aperçu des documents
@app.get('/<nom>')
@app.get('/<nom>/<element:path>')
@app.get('/<nom>/<element:path>.<ext>')
@b.view('page')
def document_afficher(nom, element='', ext=''):
    """ Affichage des fichiers et dossiers d'un projet.

    Cette page renvoie :
        − la liste des fichiers si <element> pointe sur un dossier ;
        − la mise en forme du document s'il s'agit d'un fichier connu.
    #~ """
    try:
        return Dossier(nom, element).lister()
    except TypeError:    # Cette exception est levée s'il s'agit d'un document.
        return Document(nom, element, ext).contenu


# Enregistrement des documents après édition
@app.post('/<nom>/<element:path>.<ext>')
@b.view('page')
def document_enregistrer(nom, element='', ext=''):
    if b.request.forms.action == 'enregistrer':
        Document(nom, element, ext).enregistrer(b.request.forms.contenu)
    else:
        return {'corps': 'Pourriez-vous expliciter votre intention ?'}


# II. Feuilles de style ########

@app.get('/css')
@app.get('/css/<ext>')
@b.view('style')
def css(ext=''):
    """ Feuilles de style."""
    return {'ext': ext}


# III. pages d'erreur ########

@app.error(code=401)
@b.view('page')
def erreur_accesreserve(erreur):
    return {'corps': 'Accès réservé !'}


@app.error(code=404)
@b.view('page')
def erreur_pageintrouvable(erreur):
    return {'corps': "Il n'y a rien ici !"}


# Lancement du serveur ########################################################

# On active le débogage pour avoir des messages d'erreur plus explicites.
# Commentez cette ligne en production.
b.debug(True)

b.run(
    app=app,
    # Rechargement automatique du serveur, utile pendant le développement.
    reloader=True
)
