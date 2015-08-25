FROM debian:testing

ENV DEBIAN_FRONTEND noninteractive

# Mises à jour
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys FE42299E ; \
	echo deb http://ppa.launchpad.net/gregorio-project/gregorio-unstable/ubuntu trusty main >> /etc/apt/sources.list ; \
	apt-get -y update ; apt-get -y dist-upgrade

# Gestion de l'utf8
RUN apt-get install locales
RUN locale-gen C.UTF-8 && \
    /usr/sbin/update-locale LANG=C.UTF-8

ENV LC_ALL C.UTF-8

# Installation des programmes requis
RUN apt-get -y --force-yes install --no-install-recommends \
	texlive texlive-latex-extra texlive-xetex texlive-luatex \
	texlive-lang-european texlive-lang-french \
	texlive-humanities texlive-extra-utils latex-xcolor \
	texlive-fonts-extra fonts-linuxlibertine lmodern \
	lilypond gregorio gregoriotex \
	pandoc

RUN apt-get -y install git python3


# Configuration de git
RUN git config --global user.email "musite@localhost" && \
	git config --global user.name "Musite"

# Installation du site
RUN cd /opt && \
	git clone --depth=1 https://github.com/jperon/musite && \
	mkdir /opt/musite/data /opt/musite/etc

VOLUME ["/opt/musite/data","/opt/musite/static/docs","/opt/musite/etc"]

RUN if [ ! -e /opt/musite/etc/config.py ] ; then cp /opt/musite/etc.sample/config.py /opt/musite/etc/ && \
	sed -i "s/DEVEL = True/DEVEL = False/" /opt/musite/etc/config.py && \
	sed -i "s/PORT = 8080/PORT = 80/" /opt/musite/etc/config.py ; fi && \
	if [ ! -e /opt/musite/etc/utilisateurs ] ; then cp /opt/musite/etc.sample/utilisateurs /opt/musite/etc/ ; fi && \
	if [ ! -e /opt/musite/etc/groupes ] ; then cp /opt/musite/etc.sample/groupes /opt/musite/etc/ ; fi

EXPOSE 80

CMD ["/opt/musite/serveur.py"]
