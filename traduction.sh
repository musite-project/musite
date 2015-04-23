#!/bin/bash

# Script destiné à faciliter la création et la mise-à-jour de fichiers de traduction.

# Exemple pour créer la traduction du serveur :
# traduction.sh ./serveur.py fr creer serveur serveur.py

# Exemple pour mettre-à-jour la traduction de tous les gabarits :
# traduction.sh ./serveur.py fr maj gabarits modeles/**/*.tpl

LANGUE="$1"
ACTION="$2"
NOM="$3"
shift 3
FICHIERS="$@"
#echo $FICHIERS ; exit 0

mkdir -p i18n/"$LANGUE"/LC_MESSAGES

if [ $ACTION = "creer" ] ; then
	xgettext --language=Python --keyword=_ --from-code=utf-8 --output=./i18n/"$NOM".pot $FICHIERS
	msginit --input=./i18n/"$NOM".pot --output=./i18n/"$LANGUE"/LC_MESSAGES/"$NOM".po
elif [ $ACTION = "maj" ] ; then
	msgfmt ./i18n/"$LANGUE"/LC_MESSAGES/"$NOM".po --output-file ./i18n/"$LANGUE"/LC_MESSAGES/"$NOM".mo
	xgettext --language=Python --keyword=_ --from-code=utf-8 --output=./i18n/"$NOM".pot $FICHIERS
	msgmerge --update ./i18n/"$LANGUE"/LC_MESSAGES/"$NOM".po ./i18n/"$NOM".pot
fi
