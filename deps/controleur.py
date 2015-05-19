# -*- coding: utf-8 -*-
"""Contrôleur

Si j'ai bien compris ce qu'est un contrôleur dans le modèle MVC, ce doit être
à peu près ça.
"""

import os
import shutil
import re
import bottle as b
from bottle import request as rq
from subprocess import CalledProcessError
from pkgutil import iter_modules
from importlib import import_module
from . import outils as f
from .outils import i18n_path, _
from . import auth as a
from . import HTMLTags as h
from .mistune import markdown
from etc import config as cfg


# Import des modules qui vont traiter chaque extension ########################

EXT = {
    e[1]: import_module('ext.' + e[1])
    for e in iter_modules(
        path=[os.path.join(os.path.dirname(os.path.realpath(__file__)), 'ext')]
    )
}
TXT = EXT['txt']


class Depot:
    """Interaction avec le dépôt des documents.

    Cette classe ne gère pas directement le dépôt, mais l'affichage des
    messages le concernant et la transmission des instructions en provenance
    de l'interface.
    """
    def __init__(self, projet):
        self.projet = projet
        self.depot = f.Depot(os.path.join(cfg.DATA, projet))

    def annuler(self, commit):
        """Annulation des modifications d'un seul commit

        Cette méthode est là au cas où elle pourrait servir dans la suite, mais
        son usage est très délicat : cette opération peut en effet engendrer
        des conflits, dont la gestion depuis un script est complexe. À utiliser
        avec modération !
        """
        self.depot.annuler(commit)

    def cloner(self, depot):
        """Clonage d'un dépôt existant.
        """
        self.depot.cloner(depot)

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

    def initialiser(self):
        """Initialisation d'un nouveau dépôt.
        """
        self.depot.initialiser()

    @property
    def origine(self):
        return self.depot.origine

    def pull(self, depot):
        self.depot.pull(depot)

    def push(self, depot, utilisateur, mdp):
        self.depot.push(depot, utilisateur, mdp)

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
        doc = EXT[self.ext].Document(self.chemin)
        return self.afficher(b.template(
            'export',
            {
                'listeproprietes':
                    doc.proprietes_detail[fmt],
                'proprietes':
                    doc.proprietes_liste[fmt]
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
                    actions[_('Distant-envoi')] = \
                        '_envoyerprojet/' + self.chemin
                    actions[_('Distant-réception')] = \
                        '_recevoirprojet/' + self.chemin
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

    def envoyer(self, depot, utilisateur, mdp):
        self.depot.push(depot, utilisateur, mdp)
        b.redirect(self.url)

    def recevoir(self, depot):
        self.depot.pull(depot)
        b.redirect(self.url)

    def renommer(self, destination):
        """Renommage d'un projet
        """
        dest = os.path.join(cfg.DATA, destination)
        if not os.path.exists(dest):
            shutil.move(self.dossier, dest)
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
