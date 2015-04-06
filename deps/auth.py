import os
import hashlib
import random as r
import utilisateurs as u
import jrnl as l
from etc import config as cfg

PWD = cfg.PWD

def crypter(mdp):
    '''Encodage des mots de passe.'''
    mdp = mdp.encode('utf-8')
    return hashlib.sha1(mdp).hexdigest()

def utilisateurs():
    '''Liste des utilisateurs'''
    return u.lister(os.path.join(PWD,'etc','utilisateurs'))

def groupes():
    '''Liste des groupes.'''
    return u.listergroupes(os.path.join(PWD,'etc','groupes'))

def authentifier(nom, mdp):
    '''Vérification des identifiants.'''
    try:
        return utilisateurs()[nom] == crypter(mdp)
    except KeyError:
        return False

def valider(nom, mdp, critere):
    '''Validation de la correspondance à un nom ou de l'appartenance
    à un groupe.'''
    if not authentifier(nom, mdp):
        return False
    if 'utilisateur' in critere:
        return (nom == critere['utilisateur'])
    elif 'utilisateurs' in critere:
        return (nom in critere['utilisateurs'].keys())
    elif 'groupe' in critere:
        return (nom in groupes()[critere['groupe']])

def administrateur(nom, mdp):
    return valider(nom, mdp, {'groupe': 'admin'})

def editeur(nom, mdp):
    return valider(nom, mdp, {'groupe': 'editeurs'})
