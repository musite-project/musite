#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gestion des utilisateurs et des groupes
"""
import sys as s
import os
import hashlib as h
from etc import config as cfg


def encoder(mdp):
    return h.sha1(mdp.encode('utf-8')).hexdigest()


# Gestion des utilisateurs #

def lister(fichier):
    with fichier.open() as f:
        return {
            u[0]: u[1].replace('\n', '')
            for u in [
                l.split('\t')
                for l in f.readlines()
                if '\t' in l
            ]
        }


class Utilisateur:
    def __init__(self, nom, mdp=''):
        self.nom = nom
        self.mdp = encoder(mdp)
        self.fichier = cfg.ETC / 'utilisateurs'

    def ajouter(self, fichier=None):
        if not fichier:
            fichier = self.fichier
        if self.nom == '':
            raise NomDUtilisateurRequis
        if self.mdp == '':
            raise MotDePasseRequis
        if self.nom not in lister(fichier).keys():
            with fichier.open('a') as f:
                f.write('{0}\t{1}\n'.format(self.nom, self.mdp))
        else:
            raise UtilisateurExistant(self.nom)

    def supprimer(self, fichier=None):
        if not fichier:
            fichier = self.fichier
        utilisateurs = lister(fichier)
        try:
            del utilisateurs[self.nom]
            with fichier.open('w') as f:
                for nom in utilisateurs.keys():
                    f.write('{0}\t{1}\n'.format(nom, utilisateurs[nom]))
        except KeyError:
            pass

    def modifier(self, fichier=None):
        if not fichier:
            fichier = self.fichier
        if self.mdp == '':
            raise MotDePasseRequis
        utilisateurs = lister(fichier)
        utilisateurs[self.nom] = self.mdp
        with fichier.open('w') as f:
            for nom in utilisateurs.keys():
                f.write('{0}\t{1}\n'.format(nom, utilisateurs[nom]))

    def __str__(self):
        return self.nom + '\t' + self.mdp

    def __repr__(self):
        return self.__str__()


class UtilisateurExistant(Exception):
    pass


class NomDUtilisateurRequis(Exception):
    pass


class MotDePasseRequis(Exception):
    pass

# Gestion des groupes ###


def listergroupes(fichier):
    with fichier.open() as f:
        return {
            groupes[0]: [
                utilisateur
                for utilisateur in groupes[1].replace('\n', '').split(',')
            ]
            for groupes in [
                ligne.split('\t')
                for ligne in f.readlines()
                if '\t' in ligne
            ]
            }


class Groupe:
    def __init__(self, nom):
        self.nom = nom

    def creer(self, fichier):
        if self.nom not in lister(fichier).keys():
            with fichier.open('a') as f:
                f.write('{0}\t\n'.format(self.nom))
        else:
            raise GroupeExistant(self.nom)

    def supprimer(self, fichier):
        groupes = lister(fichier)
        try:
            del groupes[self.nom]
            with fichier.open('w') as f:
                f.write(
                    '\n'.join(
                        ['\t'.join((
                            nom, ','.join([u for u in groupes[nom] if u])
                        )) for nom in groupes.keys()]
                        ) + '\n'
                    )
        except KeyError:
            pass

    def ajouter(self, utilisateur, fichier):
        groupes = lister(fichier)
        if utilisateur not in groupes[self.nom]:
            groupes[self.nom].append(utilisateur)
            with fichier.open('w') as f:
                f.write(
                    '\n'.join(
                        ['\t'.join((
                            nom, ','.join([u for u in groupes[nom] if u])
                        )) for nom in groupes.keys()]
                        ) + '\n'
                    )
        else:
            raise DejaEnregistre(utilisateur, self. nom)

    def retirer(self, utilisateur, fichier):
        groupes = lister(fichier)
        groupes[self.nom] = [u for u in groupes[self.nom] if u != utilisateur]
        with fichier.open('w') as f:
            f.write(
                '\n'.join(
                    ['\t'.join((
                        nom, ','.join([u for u in groupes[nom] if u])
                        )) for nom in groupes.keys()]
                    ) + '\n'
                )


class GroupeExistant(Exception):
    pass


class DejaEnregistre(Exception):
    pass

if __name__ == '__main__':
    try:
        u = Utilisateur(s.argv[2], s.argv[3])
        {
            '-a': u.ajouter,
            '-s': u.supprimer,
            '-m': u.modifier}[s.argv[1]](s.argv[4])
    except IndexError:
        print(encoder(s.argv[1]))
