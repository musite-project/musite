# coding: utf-8
"""Gestion des documents txt

Ce module sert aussi de module de base pour d'autres types de documents :
soyez vigilant si vous y apportez des modifications.
Il n'y a aucune dépendance externe particulière.

Si vous voulez définir un module pour gérer une nouvelle extension, il doit
comporter au moins les méthodes documentées ici. Le cas échéant, vous pouvez
user des mécanismes d'héritage de Python en vous basant sur ce module.
"""
import os.path
import subprocess as sp
import shutil
from deps import HTMLTags as h
from deps import bottle as b
from deps.outils import Path, motaleatoire, traiter_erreur, url, erreur, _
from deps.mistune import markdown
from deps import jrnl as l
from etc import config as cfg
b.TEMPLATE_PATH += [str(modele) for modele in cfg.MODELES]


class Document:
    """Classe gérant les documents texte
    """
    def __init__(
            self,
            chemin,
            formats=None,
            proprietes=None
    ):
        self.chemin = chemin
        self.nom, self.ext = os.path.splitext(chemin.split('/')[-1])
        self.ext = self.ext[1:]
        # Chemin absolu des fichiers temporaires
        self.rnd = cfg.TMP / motaleatoire(6)
        if formats:
            self.fmt = formats
            self.proprietes = {}
            for fmt in self.fmt:
                self.proprietes[fmt] = \
                    self._traiter_options(
                        fmt, self.proprietes_detail[fmt], self.proprietes
                    )
            if proprietes:
                for fmt in proprietes:
                    self._traiter_proprietes(
                        fmt, proprietes[fmt], self.proprietes_liste[fmt]
                    )

    def doit_etre_actualise(self, fichier, actualiser):
        """Teste s'il est nécessaire de rafraîchir le document
        """
        return actualiser == 1 or not fichier.is_file() or (
            actualiser and self.est_obsolete(fichier)
        )

    def est_obsolete(self, fichier):
        """Teste l'obsolescence d'un fichier
        """
        try:
            return fichier.stat().st_mtime < self._fichier().stat().st_mtime
        except FileNotFoundError:
            return True

    def _fichierrelatif(self, ext=None):
        """Chemin vers un fichier portant ce nom avec une autre extension
        """
        return Path(self.chemin).with_suffix(
            '.' + ext if ext else '.' + self.ext if self.ext else ''
        )

    def _fichier(self, ext=None):
        """Chemin absolu
        """
        if ext:
            return (
                cfg.DOCS / ext / self._fichierrelatif(ext)
            )
        else:
            return cfg.DATA / self._fichierrelatif()

    def _fichiertmp(self, ext=None):
        """Fichier temporaire
        """
        return cfg.TMP / self._fichierrelatif(ext if ext else self.ext)

    def _fichiersortie(self, ext=None, chemin=None, indice=''):
        """Fichier de destination pour un export
        """
        chemin = chemin if chemin else ext
        return (
            cfg.PWD / cfg.STATIC / 'docs' /
            chemin / indice / self._fichierrelatif(ext)
        )

    def _traiter_options(self, fmt, options, props):
        """Options

        Renvoie un dictionnaire 'à une dimension' à partir des options définies
        dans la liste des propriétés.
        """
        proprietes = {}
        for prop, val in options.items():
            if type(val[1]) is dict:
                proprietes = dict(
                    proprietes,
                    **self._traiter_options(fmt, val[1], props)
                )
            else:
                if prop in self.proprietes:
                    proprietes[prop] = self.proprietes[prop]
                elif prop in props:
                    proprietes[prop] = props[prop]
                else:
                    proprietes[prop] = val[1]
        return proprietes

    def _traiter_proprietes(self, fmt, proprietes, listeproprietes):
        """Mise en place des propriétés

        Convertit les chaînes de caractères reçues de l'interface dans les
        types de données attendus par le document.
        """
        for prop, val in proprietes.items():
            if prop in listeproprietes:
                typ = type(listeproprietes[prop])
                if typ in (str, int, float):
                    self.proprietes[fmt][prop] = typ(val)
                elif typ is bool:
                    self.proprietes[fmt][prop] = typ(int(val))
                elif typ in (tuple, list):
                    if type(val) in (tuple, list):
                        self.proprietes[fmt][prop] = val
                    else:
                        self.proprietes[fmt][prop] = tuple(
                            type(pr)(i)
                            for i, pr
                            in zip(
                                val.split(','),
                                listeproprietes[prop]
                            )
                        )

    @property
    def dossier(self):
        """Dossier contenant le document
        """
        return self._fichier().parent

    @property
    def dossiertmp(self):
        """Dossier temporaire
        """
        return self._fichiertmp().parent

    @property
    def obsolete(self):  # pylint: disable=R0201
        """Par défaut, on considère qu'un aperçu est à jour
        """
        return False

    @property
    def proprietes_detail(self):
        """Liste hiérarchisée des propriétés utiles à chaque format d'export
        """
        return {fmt: self.fmt[fmt][1] for fmt in self.fmt}

    @property
    def proprietes_liste(self):
        """Liste non hiérarchisée des propriétés
        """
        listeproprietes = {}
        for fmt, props in self.fmt.items():
            listeproprietes[fmt] = self._traiter_options(
                fmt, props[1], self.proprietes[fmt]
            )
        return listeproprietes

    def afficher(self, actualiser=2):  # pylint: disable=W0613
        """Affichage du contenu du document

        Il doit s'agir ou bien d'un simple texte, ou bien de code html.
        """
        return h.CODE(b.html_escape(self.contenu))

    afficher_source = afficher

    def afficher_pdf(self, message_erreur='', actualiser=2):
        """Affichage du document pdf en html (base 64)
        """
        try:
            return h.OBJECT(
                data="{}".format(self.pdf(actualiser=actualiser)),
                Type="application/pdf",
                width="100%",
                height="100%"
            )
        except ErreurCompilation as err:
            traiter_erreur(err)
            return traiter_erreur_compilation(self.dossiertmp, message_erreur)

    @property
    def contenu(self):
        """Contenu du document
        """
        try:
            with self._fichier().open() as doc:
                return doc.read(-1)
        except UnicodeDecodeError:
            raise FichierIllisible(self._fichier())

    def editer(self, creation=False):
        """Page d'édition du document

        Ce n'est pas ici qu'il importe de s'occuper de cosmétique : on renvoie
        le strict nécessaire, en html, pour l'édition d'un document.
        """
        try:
            return b.template(
                'editeur',
                emplacement=self.chemin,
                texte=self.contenu,
                ext=self.ext
            )
        except FileNotFoundError:
            if creation:
                return b.template(
                    'editeur',
                    emplacement=self.chemin,
                    texte='',
                    ext=self.ext
                )
            else:
                b.abort(404)

    def enregistrer(self, contenu):
        """Enregistrement du document
        """
        with self._fichier().open('w') as doc:
            doc.write(contenu)

    def supprimer(self):
        """Suppression du document
        """
        try:
            self._fichier().unlink()
        except FileNotFoundError as err:
            traiter_erreur(err)
        for doc in cfg.DOCS.glob('*/' + str(self._fichierrelatif().with_suffix('')) + '.*'):
            print(doc)
            doc.unlink()

    def exporter(self, fmt):
        """Export dans les différents formats
        """
        return self.fmt[fmt][0]

    def pdf(self, chemin=None, indice='', actualiser=2):
        """Format pdf

        Si un pdf existe déjà dans l'arborescence de musite, il sera
        actualisé en fonction du paramètre *actualiser* :

        - 0 : aucune actualisation ;
        - 1 : actualisation forcée ;
        - 2 : actualisation si le pdf est plus ancien que l'original.
        """
        chemin = chemin if chemin else 'pdf'
        fichierpdf = self._fichiersortie('pdf', chemin=chemin, indice=indice)
        if actualiser == 1 or (
                not fichierpdf.is_file()
                or (
                    actualiser
                    and self.est_obsolete(fichierpdf)
                )
        ):
            self.preparer_pdf(destination=fichierpdf)
        return url(fichierpdf)


def compiler(commande, fichier, environnement):
    """Appel de commande externe

    Cette méthode est surtout appelée dans les modules dépendant de celui-ci.
    """
    try:
        os.chdir(str(fichier.parent))
        erreur(str(environnement) + '\n\n')
        erreur(' '.join(commande) + '\n\n')
        compilation = sp.Popen(
            commande,
            env=environnement,
            stdout=sp.PIPE,
            stderr=sp.PIPE
        )
        sortie, erreurs = compilation.communicate()
        try:
            l.log(
                _('Sortie :')
                + '\n========\n'
                + '\n{}\n\n\n\n'.format(sortie.decode('utf8'))
                + '−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−−\n\n\n\n'
                + _('Erreurs :')
                + '\n=========\n'
                + '\n{}\n'.format(erreurs.decode('utf8')),
                mode = 'w'
            )
        except UnicodeDecodeError:
            raise FichierIllisible
        if compilation.returncode:
            raise ErreurCompilation(sortie.decode(), erreurs.decode())
    finally:
        os.chdir(str(cfg.PWD))


def traiter_erreur_compilation(dossier, message_erreur = ''):
    """Réaction en cas d'erreur de compilation
    """
    return markdown(
                _(
                    """\
Il y a eu une erreur pendant le traitement du document.
Ceci vient probablement d'une erreur de syntaxe ; si vous êtes absolument
certain du contraire, merci de signaler le problème.

{}

Voici la sortie de la commande :

                    """
                ).format(message_erreur)
            ) + Document(dossier.as_posix() + '/log').afficher()


class FichierIllisible(Exception):
    """Exception renvoyée quand le fichier est illisible

    Ici, cette exception est utile si le fichier est un binaire et non un
    document texte.
    """
    pass


class ErreurCompilation(Exception):
    """Exception levée en cas d'erreur de compilation
    """
<<<<<<< HEAD
    def __init__(self, sortie=None, erreurs=None):
        print(sortie, erreurs)
=======
    def __init__(self, sortie='', erreurs=''):
        self.sortie = sortie
        self.erreurs = erreurs
>>>>>>> 1061cca57fd690d921d556f57be97a5686f635ca
