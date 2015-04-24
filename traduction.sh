#!/bin/bash

# Script destiné à faciliter la création et la mise-à-jour de fichiers de traduction.

# Exemple pour créer la traduction française :
# traduction.sh creer fr

# Exemple pour mettre à jour la traduction française :
# traduction.sh maj fr

# Exemple pour mettre à jour toutes les traductions :
# traduction.sh majtt

ACTION="$1"
LANGUE="./i18n/$2/LC_MESSAGES"
NOM="musite"
shift 3
FICHIERS="./serveur.py deps/*.py deps/ext/*.py modeles/**/*.tpl"
#echo $FICHIERS ; exit 0
LANGUES=$(ls -d ./i18n/??/LC_MESSAGES)

mkdir -p "$LANGUE"

if [ $ACTION = "creer" ] ; then
	xgettext --language=Python --keyword=_ --from-code=utf-8 --output=./i18n/"$NOM".pot $FICHIERS
	msginit --input=./i18n/"$NOM".pot --output="$LANGUE"/"$NOM".po
elif [ $ACTION = "maj" ] ; then
	msgfmt "$LANGUE"/"$NOM".po --output-file "$LANGUE"/"$NOM".mo
	if [ "$FICHIERS" ] ; then
		xgettext --language=Python --keyword=_ --from-code=utf-8 --output=./i18n/"$NOM".pot $FICHIERS
		msgmerge --update "$LANGUE"/"$NOM".po ./i18n/"$NOM".pot
	fi
elif [ $ACTION = "majtt" ] ; then
	xgettext \
		--language=Python \
		--keyword=_ \
		--from-code=utf-8 \
		--output=./i18n/"$NOM".pot \
		./serveur.py deps/*.py deps/ext/*.py modeles/**/*.tpl
	for LANGUE in $LANGUES ; do
		msgmerge --update "$LANGUE"/"$NOM".po ./i18n/"$NOM".pot
		msgfmt "$LANGUE"/"$NOM".po --output-file "$LANGUE"/"$NOM".mo
	done
fi

