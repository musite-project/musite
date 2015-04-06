import os
from glob import glob as ls
import jrnl as l

class Fichier(object):
    def __init__(self, dossier, titre):
        os.chdir(depot.dossier)
        self.dossier = dossier
        self.nom = titre
        self.chemin = os.path.join(dossier, titre)

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


class Dossier(object):
    def __init__(self, dossier):
        self.dossier = dossier
        if not os.path.isdir(dossier):
            raise TypeError(dossier + " n'est pas un dossier")

    def lister_ancien(self):
        chemins = []
        for racine, dossiers, fichiers in os.walk(self.dossier):
            for fichier in fichiers:
                chemins.append([racine, fichier])
        return chemins

    def lister(self,profondeur=1):
        liste = {
            self.dossier: [
                os.path.split(fichier)[-1]
                for fichier in ls(self.dossier + '/*')
            ]
        }
        if profondeur > 1:
            for sousdossier in liste[self.dossier]:
                contenu = Dossier(
                    os.path.join(self.dossier,sousdossier)
                ).lister(profondeur - 1)
                if contenu[os.path.join(self.dossier,sousdossier)] != []:
                    liste = dict(
                        liste, **contenu
                    )
        return liste


def sansaccents(entree):
    nkfd_form = ud.normalize('NFKD', entree)
    return "".join([c for c in nkfd_form if not ud.combining(c)])
