# Musite
Une sorte de wiki pour documents musicaux


## Installation

### Dépendances

Musite est prévu pour être le plus simple *possible* à installer, c'est pourquoi ses dépendances sont réduites au minimum requis pour les fonctionnalités attendues :

- [Python](https://www.python.org) en version 3 (testé avec la 3.4), avec la librairie matplotlib (pour la gestion des polices de caractères) ;
- une distribution de LaTeX, de préférence [TeXLive](https://www.tug.org/texlive) (la seule qui ait été testée), avec au minimum LuaLaTeX et la police Libertine ; une sélection raisonnable d'extensions est toutefois plus que vivement recommandée ;
- [Gregorio et GregorioTeX](http://gregorio-project.github.io) pour les partitions grégoriennes ;
- [LilyPond](http://www.lilypond.org) pour les partitions classiques ;
- [Pandoc](http://pandoc.org) pour les textes en markdown (et, potentiellement, nombre d'autres usages) ;
- [Git](http://git-scm.com/) pour la gestion de version (qui vous permettra d'annuler les changements intempestifs).

#### Sous Debian

Les commandes suivantes devraient installer le nécessaire :

    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys FE42299E
    echo deb http://ppa.launchpad.net/gregorio-project/gregorio/ubuntu trusty main >> /etc/apt/sources.list
    apt-get -y update ; apt-get -y dist-upgrade
    apt-get -y --force-yes install --no-install-recommends \
    texlive texlive-latex-extra texlive-xetex texlive-luatex \
    texlive-lang-european texlive-lang-french \
    texlive-humanities texlive-extra-utils latex-xcolor \
    texlive-fonts-extra fonts-linuxlibertine lmodern \
    lilypond gregorio gregoriotex \
    pandoc
    apt-get -y install git python3 python3-matplotlib


### Installation

Clonez le dépôt de musite (si vous voulez avoir tout l'historique des changements, enlevez `--depth=1` :

    git clone --depth=1 https://github.com/musite-project/musite

Puis placez-vous dans le dossier musite obtenu ; créez un dossier *tmp* pour les fichiers temporaires et un dossier *data* pour les données, puis renommez les modèles de fichiers utilisateurs/groupes. Ce qui donne, sous Linux :

    cd musite ; mkdir tmp data
    mv etc/utilisateurs.sample etc/utilisateurs
    mv etc/groupes.sample etc/groupes

Configurez votre nom d'utilisateur et votre courriel pour git :

    git config --global user.email "VOTRE@COURRIEL" && git config --global user.name "VOTRE NOM"


## Mise en route

Toujours dans le dossier *musite*, exécutez le fichier *serveur.py* :

    ./serveur.py

Ensuite, dans votre navigateur, saisissez l'adresse :

    http://localhost:8080

Et voilà !

Éventuellement, vous pouvez utiliser la fonction *Cloner projet* de la page *Projets* pour importer la documentation
de musite :

    https://github.com/musite-project/musite-doc


## Configuration

Vous pouvez définir certains paramètres dans le fichier *etc/config.py*. En particulier, il est recommandé de définir l'adresse d'écoute sur l'adresse de la carte réseau où vous voulez rendre l'interface accessible. Si ceci vous semble du chinois, remplacez *0.0.0.0* par *127.0.0.1*. De même, pour une utilisation ordinaire, définissez le paramètre *DEVEL* à *False*.


## Translating

If you want to translate this program in your language, you can do it thanks to gettext. First type this command (replacing `en` by your language code in two letters) :

    ./traduction.sh creer en

Then edit the file `i18n/YOUR_LANGUAGE/LC_MESSAGES/musite.po`. When done, type this command :

    ./traduction.sh maj en

You're done ! If you'd like to share your work, your pull requests are welcome !
