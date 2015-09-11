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
from .outils import Path, GitError, i18n_path, ls, url, motaleatoire, erreur, _
from . import auth as a
from . import HTMLTags as h
from .mistune import markdown
from etc import config as cfg


# Import des modules qui vont traiter chaque extension ########################

EXT = {
    e[1]: import_module('ext.' + e[1])
    for e in iter_modules(
        path=[str(cfg.PWD / 'deps' / 'ext')]
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
        self.depot = f.Depot(cfg.DATA / projet)

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
        except f.GitError as err:
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
        """Initialisation d'un nouveau dépôt
        """
        self.depot.initialiser()

    @property
    def origine(self):
        """Adresse du dépôt depuis lequel celui-ci a été clôné
        """
        return self.depot.origine

    def pull(self, depot):
        """Réception des changements distants
        """
        self.depot.pull(depot)

    def push(self, depot, utilisateur, mdp):
        """Envoi des modifications locales
        """
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
        self.ext = ext.lower() if ext else None
        self.chemin = projet + '/' + element + ('.' + ext if ext else '')
        self.fichier = cfg.DATA / self.chemin
        self.dossier = self.fichier.parent
        try:
            self.document = EXT[self.ext].Document(self.chemin)
        except KeyError as err:
            f.traiter_erreur(err)
            self.document = TXT.Document(self.chemin)
        except EXT[self.ext].FichierIllisible as err:
            f.traiter_erreur(err)
            self.document = TXT.Document(self.chemin)
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
                if self.ext == 'gabc':
                    actions[_('Éditer gabc')] = '_gabc_editer/' + self.chemin
        except TypeError as err:
            f.traiter_erreur(err)
        liens = {
            _('Projet'): self.projet,
            _('Dossier'): '/'.join(self.chemin.split('/')[:-1])
        }
        try:
            exports = {
                fmt: self.chemin + '?fmt=' + fmt
                for fmt in self.document.proprietes
            }
        except (AttributeError, KeyError) as err:
            f.traiter_erreur(err)
            # Cette exception est levée quand le module concerné ne définit pas
            # de format d'export.
            exports = {}
        try:
            midi = self.document.midi()
        except (AttributeError, KeyError) as err:
            f.traiter_erreur(err)
            # Cette exception est levée quand le module concerné ne définit pas
            # de fichier midi.
            midi = None
        actualiser = (
            (self.chemin + '/?act=1', self.document.obsolete)
            if hasattr(self.document, 'obsolete')
            else None
        )
        return {
            'corps': contenu,
            'actualiser': actualiser,
            'actions': actions,
            'exports': exports,
            'liens': liens,
            'midi': midi,
        }

    def contenu(self, actualiser=None):
        """Contenu du document

        Ce contenu dépend du type du document : c'est donc le module gérant
        l'extension concernée qui s'occupe de retourner un code html
        correspondant audit contenu.
        Pour développer un module gérant une nouvelle extension, référez-vous
        aux docstrings du module deps/ext/txt.py.
        """
        try:
            if actualiser:
                return self.afficher(
                    self.document.afficher(actualiser=actualiser)
                )
            else:
                return self.afficher(
                    self.document.afficher()
                )
        except AttributeError as err:
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
        except TXT.FichierIllisible as err:
            f.traiter_erreur(err)
            return self.afficher(_("Ce fichier est illisible."))

    @property
    def source(self):
        """Affichage de la source du document
        """
        try:
            return self.afficher(
                self.document.afficher_source()
            )
        except AttributeError as err:
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
        except TXT.FichierIllisible as err:
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
            self.document.supprimer()
        except KeyError as err:
            f.traiter_erreur(err)
            self.document.supprimer()
        try:
            self.depot.sauvegarder(
                message=_('Suppression du document {}').format(self.chemin)
            )
        except GitError as err:
            f.traiter_erreur(err)
        b.redirect(url(Path(self.dossier)).replace('/data', ''))

    def editer(self, creation=False):
        """Édition du document
        """
        try:
            return self.afficher(
                self.document.editer(creation)
            )
        except (AttributeError, TXT.FichierIllisible) as err:
            f.traiter_erreur(err)
            # Si le type de document ne prévoit pas d'édition, on abandonne.
            return self.afficher(_("Ce type de document n'est pas éditable."))

    def enregistrer(self, contenu):
        """Enregistrement du document
        """
        self.document.enregistrer(contenu)
        try:
            self.depot.sauvegarder(
                fichier=self.fichier,
                message=self.fichier.name
            )
        except f.GitError as err:
            f.traiter_erreur(err)
            if cfg.DEVEL:
                print(err.status)
            return self.afficher(markdown(
                _(
                    "Il y a eu une erreur pendant la sauvegarde du document "
                    "dans l'historique. Cela vient probablement d'erreurs de "
                    "fusion non corrigées."
                ) + "\n- " +
                (
                    "\n- ".join(
                        str(h.A(
                            doc, href=i18n_path('/' + self.projet + '/' + doc)
                        ))
                        for doc in err.status.keys()
                        if err.status[doc] == ('U', 'U')
                    )
                ) if len(err.status) else ""
            ))
        b.redirect(i18n_path(('/' + self.chemin).replace('//', '/')))

    def copier(self, destination, ecraser=False):
        """Copie d'un dossier
        """
        dest = cfg.DATA / destination
        if not dest.exists() or ecraser:
            try:
                dest.parent.mkdir(parents=True)
            except FileExistsError as err:
                f.traiter_erreur(err)
            shutil.copy2(str(self.fichier), str(dest))
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

Voici la sortie de la commande :

"""
                )
                + _('Sortie :')
                + '\n========\n'
                + '\n{}\n\n\n\n'.format(err.sortie)
                + '−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−\n\n\n\n'
                + _('Erreurs :')
                + '\n=========\n'
                + '\n{}\n'.format(err.erreurs)
            ))

    def exporter_infos(self, fmt):
        """Informations pour l'export
        """
        return self.afficher(b.template(
            'export',
            {
                'listeproprietes':
                    self.document.proprietes_detail[fmt],
                'proprietes':
                    self.document.proprietes_liste[fmt]
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
        self.depot.retablir(commit, self.fichier, rq.auth[0])
        b.redirect(i18n_path('/_historique/' + self.chemin))


class Dossier:
    """Gestion des dossiers
    """
    def __init__(self, projet, element):
        self.projet = projet
        self.nom = element
        self.chemin = '/'.join((projet, element))
        self.dossier = \
            cfg.DATA / self.chemin if self.chemin != '/' else cfg.DATA
        self.depot = Depot(self.projet)

    def afficher(self, contenu, suppression=False):
        """Propriétés communes des pages de gestion de dossiers

        Cette méthode définit en particulier ce qui apparaît dans le menu.
        C'est ici qu'il faut définir ce qui est commun à toutes les pages
        proposant une opération sur un dossier.
        """
        actions = {
            _('Télécharger'): '_telechargerdossier/' + self.chemin,
        }
        try:
            if a.authentifier(rq.auth[0], rq.auth[1]) and not suppression:
                actions[_('Créer document')] = \
                    '_creer/' + self.chemin
                actions[_('Créer dossier')] = \
                    '_creerdossier/' + self.chemin
                actions[_('Copier')] = \
                    '_copier/' + self.chemin
                actions[_('Déplacer')] = \
                    '_deplacer/' + self.chemin
                actions[_('Envoyer fichier')] = \
                    '_envoyer/' + self.chemin
                actions[_('Envoyer dossier')] = \
                    '_envoyerdossier/' + self.chemin
                actions[_('Supprimer')] = \
                    '_supprimerdossier/' + self.chemin
        except TypeError as err:
            f.traiter_erreur(err)
        liens = {
            _('Projet'): self.projet,
            _('Parent'): '/'.join(self.chemin.split('/')[:-1])
        }
        return {
            'corps': contenu,
            'actions': actions,
            'liens': liens,
            'recherche': self.chemin,
        }

    def creer(self):
        """Création d'un nouveau dossier
        """
        try:
            self.dossier.mkdir(parents=True)
        except FileExistsError as err:
            f.traiter_erreur(err)
        b.redirect(i18n_path('/' + self.chemin))

    def deplacer(self, destination, ecraser=False):
        """Déplacement/renommage d'un dossier (ou document)
        """
        dest = cfg.DATA / destination
        if not dest.exists() or ecraser:
            self.dossier.replace(dest)
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
        dest = cfg.DATA / destination
        if not dest.exists() or ecraser:
            shutil.copytree(str(self.dossier), str(dest))
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
            fichier.save(str(self.dossier), int(ecraser))
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
        f.nettoyertmp()
        fichiers = tuple(
            fichier for fichier in Path(self.dossier).iterdir()
            if fichier.name[0] != '.'
        )
        # Si l'on n'est pas à la racine, on affiche un lien vers le parent.
        try:
            if self.chemin[:-1] != self.projet:
                liste = [
                    h.A(
                        '../',
                        href=i18n_path('/{}'.format(
                            '/'.join(self.chemin.split('/')[:-1])
                        )),
                        Class='dossier'
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
                str(fichier.relative_to(self.dossier).as_posix()) + '/'
                for fichier in fichiers
                if (self.dossier / fichier).is_dir()
            ],
            key=lambda s: s.lower()
        )
        listefichiers = sorted(
            [
                str(fichier.relative_to(self.dossier).as_posix())
                for fichier in fichiers
                if not (self.dossier / fichier).is_dir()
            ],
            key=lambda s: s.lower()
        )
        # Formatage de la liste des fichiers.
        liste += [
            h.A(
                dossier,
                href=i18n_path('/{}/{}/{}'.format(
                    self.projet, self.nom, dossier
                ).replace('//', '/')),
                Class='dossier'
            )
            for dossier in listedossiers
        ]
        liste += [
            h.A(
                fichier,
                href=i18n_path('/{}/{}/{}'.format(
                    self.projet, self.nom, fichier
                ).replace('//', '/')),
                Class='fichier'
            )
            for fichier in listefichiers
        ]
        for fichier in (
                'README-{}.md'.format(rq.locale.upper()),
                'README-{}.MD'.format(rq.locale.upper()),
                'Readme-{}.md'.format(rq.locale),
                'readme-{}.md'.format(rq.locale),
                'README.md', 'README.MD', 'Readme.md', 'readme.md',
                'README', 'Readme', 'readme',
                'README.txt', 'README.TXT', 'Readme.txt', 'readme.txt',
        ):
            try:
                with (self.dossier / fichier).open() as readme:
                    readme = markdown(readme.read(-1))
                    break
            except FileNotFoundError as err:
                f.traiter_erreur(err)
                readme = ''
        return self.afficher(b.template(
            'liste',
            liste=liste,
            readme=readme,
        ))

    def rechercher(self, expression, nom=True, contenu=True):
        """Recherche dans le nom ou le contenu des documents
        """
        try:
            liens = (
                url(Path(dossier)).replace('/data', '')
                for dossier in f.Dossier(self.dossier).rechercher(
                    expression, nom, contenu
                )
            )
            return self.afficher(markdown(
                _(
                    "# Documents du dossier *{d}* "
                    "contenant l'expression _{e}_"
                ).format(
                    d=self.chemin, e=expression
                ) + '\n\n- ' +
                '\n- '.join(str(
                    h.A(lien.replace('/' + self.projet + '/', ''), href=lien)
                ) for lien in liens)
            ))
        except f.ErreurExpression:
            return self.afficher(markdown(
                "Votre expression a généré une erreur : veuillez respecter "
                "la syntaxe des expressions régulières de Python."
            ))

    def supprimer(self):
        """Suppression d'un dossier et de son contenu
        """
        shutil.rmtree(str(self.dossier), ignore_errors=True)
        self.depot.sauvegarder(
            message=_('Suppression du dossier {}').format(self.chemin)
        )
        return self.afficher(_('Dossier supprimé !'))

    def telecharger(self):
        """Téléchargement d'un dossier sous forme d'archive
        """
        rnd = cfg.STATIC / 'tmp' / motaleatoire(6)
        archive = self.dossier.name
        dossier = self.dossier.parent
        try:
            rnd.mkdir(parents=True)
        except FileExistsError as err:
            f.traiter_erreur(err)
        try:
            os.chdir(str(rnd))
            shutil.make_archive(
                archive,
                'zip',
                root_dir=str(dossier),
                base_dir=str(archive)
            )
        finally:
            os.chdir(str(cfg.PWD))
        b.redirect(
            i18n_path(
                '/{}/{}.zip?action=telecharger'.format(url(rnd), archive)
                .replace('//', '/')
            )
        )

    def telecharger_envoi(self, archive):
        """Intégration d'une archive au sein d'un dossier
        """
        tmp_root = cfg.DATA/'.tmp'
        tmp = tmp_root / motaleatoire(6)
        try:
            (tmp_root).mkdir()
        except FileExistsError as err:
            f.traiter_erreur(err)
        tmp.mkdir()
        tmp_archive = tmp / archive.filename
        archive.save(str(tmp_archive))
        try:
            os.chdir(str(tmp))
            shutil.unpack_archive(
                str(tmp_archive),
                extract_dir=str(tmp),
                format='zip',
            )
            tmp_archive.unlink()
            for racine, dossiers, fichiers in os.walk('.'):
                if '.git' not in racine:
                    for fichier in fichiers:
                        os.renames(
                            os.path.join(racine, fichier),
                            os.path.join(str(self.dossier), racine, fichier)
                        )
                    if '.git' in dossiers:
                        dossiers.remove('.git')
                    for dossier in dossiers:
                        os.renames(
                            os.path.join(racine, dossier),
                            os.path.join(str(self.dossier), racine, dossier)
                        )
            self.depot.sauvegarder(
                message="Intégration de l'archive " + archive.filename
            )
            b.redirect(i18n_path('/' + self.chemin))
        except shutil.ReadError as err:
            f.traiter_erreur(err)
            return self.afficher(_("Ceci n'est pas une archive zip."))
        finally:
            os.chdir(str(cfg.PWD))
            shutil.rmtree(str(tmp_root))

    def telecharger_envoi_infos(self):
        """Informations pour l'envoi d'un fichier
        """
        return self.afficher(b.template('envoi_dossier'))


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
        actions = {
            _('Historique'): '_historique/' + self.chemin,
            _('Télécharger'): '_telechargerdossier/' + self.projet,
        }
        try:
            if a.authentifier(rq.auth[0], rq.auth[1]):
                if not suppression:
                    actions[_('Créer document')] = \
                        '_creer/' + self.chemin
                    actions[_('Créer dossier')] = \
                        '_creerdossier/' + self.chemin
                    actions[_('Copier')] = \
                        '_copier/' + self.chemin
                    actions[_('Distant-envoi')] = \
                        '_emettreprojet/' + self.chemin
                    actions[_('Distant-réception')] = \
                        '_recevoirprojet/' + self.chemin
                    actions[_('Envoyer fichier')] = \
                        '_envoyer/' + self.chemin
                    actions[_('Envoyer dossier')] = \
                        '_envoyerdossier/' + self.chemin
                    actions[_('Renommer')] = \
                        '_deplacer/' + self.chemin
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
            'recherche': self.chemin,
        }

    def annuler(self, commit):
        """Annulation d'un commit malheureux
        """
        try:
            self.depot.annuler(commit)
            b.redirect(self.url)
        except f.GitError as err:
            return self.afficher(self._conflit(err))

    def cloner(self, depot):
        """Clonage d'un projet distant
        """
        self.depot.cloner(depot)
        b.redirect(self.url)

    def _conflit(self, err):
        """Message en cas de conflit de fusion
        """
        return markdown(
            _(
                "Il y a conflit de fusion sur les fichiers suivants :\n"
                "\n"
                "- {}\n"
                "\n"
                "Veuillez régler manuellement les conflits en question ; "
                "pour cela, recherchez les lignes `<<<<<<< HEAD`, qui "
                "indiquent le début de la zone de conflit.\n"
                "\n"
                "Attention : faites cela préalablement à tout autre "
                "travail, car l'historique ne fonctionnera normalement "
                "qu'après résolution des conflits."
            ).format(
                "\n- ".join(str(h.A(
                    doc, href=i18n_path('/' + self.chemin + doc)
                )) for doc in err.status.keys())
            )
        )

    def copier(self, destination, ecraser=False):
        """Copie d'un projet
        """
        dest = cfg.DATA / destination
        if not dest.exists():
            shutil.copytree(str(self.dossier), str(dest))
            b.redirect(i18n_path('/' + destination))
        else:
            return self.afficher(_('Il y a déjà un projet portant ce nom !'))

    def creer(self):
        """Création d'un nouveau projet
        """
        try:
            self.dossier.mkdir(parents=True)
            self.depot.initialiser()
            b.redirect(self.url)
        except FileExistsError as err:
            f.traiter_erreur(err)
            return self.afficher(_('Ce projet existe déjà !'))

    def envoyer(self, depot, utilisateur, mdp):
        """Envoi des modifications locales"""
        self.depot.push(depot, utilisateur, mdp)
        b.redirect(self.url)

    def recevoir(self, depot):
        """Réception des modifications distantes"""
        try:
            self.depot.pull(depot)
        except f.GitError as err:
            f.traiter_erreur(err)
            return self.afficher(self._conflit(err))
        b.redirect(self.url)

    def renommer(self, destination):
        """Renommage d'un projet
        """
        dest = cfg.DATA / destination
        if not dest.exists():
            self.dossier.replace(dest)
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
            shutil.rmtree(str(self.dossier), ignore_errors=False)
            return self.afficher(_('Projet supprimé !'), suppression=True)
        except FileNotFoundError as err:
            f.traiter_erreur(err)
            # Cette exception est levée quand le projet n'existe pas.
            return self.afficher(_('''C'est drôle, ce que vous me demandez :
                il n'y a pas de projet ici !'''), suppression=True)

    def telecharger_envoi(self, archive):
        """Intégration d'une archive au sein d'un dossier
        """
        tmp = cfg.TMP / motaleatoire(6)
        tmp.mkdir()
        tmp_archive = tmp / archive.filename
        archive.save(str(tmp_archive))
        try:
            os.chdir(str(tmp))
            shutil.unpack_archive(
                str(tmp_archive),
                extract_dir=str(tmp),
                format='zip',
            )
            tmp_archive.unlink()
            dossier = [dss for dss in tmp.iterdir()]
            if len(dossier) != 1:
                return self.afficher(markdown(_(
                    "L'archive doit contenir un et un seul dossier, "
                    "dans lequel doivent se trouver :\n\n"
                    "- les fichiers du projet ;\n"
                    "- éventuellement, le dossier `.git` contenant "
                    "les données de gestion de version."
                )))
            dossier = dossier[0]
            shutil.copytree(str(dossier), str(self.dossier))
            if not (self.dossier / '.git').is_dir():
                self.depot.initialiser()
            b.redirect(i18n_path('/' + self.chemin))
        except shutil.ReadError as err:
            f.traiter_erreur(err)
            return self.afficher(_("Ceci n'est pas une archive zip."))
        finally:
            os.chdir(str(cfg.PWD))
            shutil.rmtree(str(tmp))

    def telecharger_envoi_infos(self):
        """Informations pour l'envoi d'un fichier
        """
        return self.afficher(b.template('envoi_projet'))


class DocumentGabc(Document):
    """Gestion des documents gabc

    Cet objet est rendu nécessaire du fait de l'interface d'édition
    spécifique au gabc.
    """
    def __init__(self, projet, element, ext):
        Document.__init__(self, projet, element, ext)

    def editer_gabc(self, creation=False):
        """Éditeur spécifique aux fichiers gabc"""
        try:
            return self.afficher(b.template(
                'jgabc',
                emplacement=self.document.chemin,
                paroles=re.sub('  +', ' ', self.document.partition().texte),
                melodie=self.document.partition().gabc,
                entetes='\n'.join(
                    '{}:{};'.format(entete, valeur)
                    for entete, valeur in self.document.entetes.items()
                )
            ))
        except FileNotFoundError:
            if creation:
                return self.afficher(b.template(
                    'jgabc',
                    emplacement=self.document.chemin,
                    paroles=re.sub(
                        '  +', ' ',
                        self.document.partition().texte
                    ),
                    melodie=self.document.partition().gabc,
                    entetes='\n'.join(
                        '{}:{};'.format(entete, valeur)
                        for entete, valeur in self.document.entetes.items()
                    )
                ))
            else:
                b.abort(404)
