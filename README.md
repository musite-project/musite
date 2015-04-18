# Musite
Une sorte de wiki pour documents musicaux


## Installation

### Dépendances

Musite est prévu pour être le plus simple *possible* à installer, c'est pourquoi ses dépendances sont réduites au minimum requis pour les fonctionnalités attendues :

- [Python](https://www.python.org) en version 3 (testé avec la 3.4) ;
- une distribution de LaTeX, de préférence [TeXLive](https://www.tug.org/texlive) (la seule qui ait été testée), avec au minimum LuaLaTeX et la police Libertine ; une sélection raisonnable d'extensions est toutefois plus que vivement recommandée ;
- [Gregorio et GregorioTeX](http://gregorio-project.github.io) pour les partitions grégoriennes ;
- [LilyPond](http://www.lilypond.org) pour les partitions classiques ;
- [Git](http://git-scm.com/) pour la gestion de version (qui vous permettra d'annuler les changements intempestifs).

Concrètement, sous Debian, la commande suivante devrait installer le nécessaire, Gregorio mis à part :

    apt-get install python3 lilypond git texlive texlive-latex-extra texlive-xetex texlive-lang-latin texlive-lang-french texlive-humanities texlive-extra-utils latex-xcolor texlive-fonts-extra fonts-linuxlibertine lmodern gregorio gregoriotex

Quant à Gregorio :

- si vous ne craignez pas d'activer les dépôts *sid* (ce qui suppose que vous sachiez ce que vous faites) :

    apt-get install gregorio gregoriotex

- option recommandée : suivez les [instructions du site de Gregorio](http://gregorio-project.github.io/installation.html).


### Installation

Clonez le dépôt de musite :

    git clone https://github.com/jperon/musite

Puis placez-vous dans le dossier musite obtenu ; créez un dossier *tmp* pour les fichiers temporaires et un dossier *data* pour les données. Ce qui donne, sous Linux :

    cd musite ; mkdir tmp data


## Mise en route

Toujours dans le dossier *musite*, exécutez le fichier *serveur.py* :

    ./serveur.py

Ensuite, dans votre navigateur, saisissez l'adresse :

    http://localhost:8080

Et voilà !


## Configuration

Vous pouvez définir certains paramètres dans le fichier *etc/config.py*. En particulier, il est recommandé de définir l'adresse d'écoute sur l'adresse de la carte réseau où vous voulez rendre l'interface accessible. Si ceci vous semble du chinois, remplacez *0.0.0.0* par *127.0.0.1*. De mème, pour une utilisation ordinaire, définissez le paramètre *DEVEL* à *False*.
