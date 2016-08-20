FROM debian:stable

ENV DEBIAN_FRONTEND noninteractive

# Mises à jour
RUN echo deb http://httpredir.debian.org/debian unstable main >> /etc/apt/sources.list; \
	apt-get -y update ; apt-get -y dist-upgrade ; apt-get -y autoremove --purge

# Gestion de l'utf8
RUN apt-get -y install locales
RUN locale-gen C.UTF-8 && \
    /usr/sbin/update-locale LANG=C.UTF-8

ENV LC_ALL C.UTF-8

# Installation des programmes requis
RUN apt-get -y --force-yes install --no-install-recommends \
	texlive texlive-latex-extra texlive-xetex texlive-luatex \
	texlive-lang-european texlive-lang-french \
	texlive-humanities texlive-extra-utils latex-xcolor \
	texlive-fonts-extra fonts-linuxlibertine lmodern \
	texlive-music lilypond \
	pandoc

RUN apt-get -y install git python3 python3-matplotlib


# Configuration de git
RUN git config --global user.email "musite@localhost" && \
	git config --global user.name "Musite"

# Installation du site
RUN cd /opt && \
	git clone --depth=1 https://github.com/musite-project/musite && \
	mkdir /opt/musite/data /opt/musite/etc && \
	mkdir /usr/share/fonts/perso

VOLUME ["/opt/musite/data","/opt/musite/static/docs","/opt/musite/etc","/usr/share/fonts/perso"]

ADD serveur.sh /opt/musite/serveur.sh

EXPOSE 80

CMD ["/opt/musite/serveur.sh"]
