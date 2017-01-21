FROM musite/gregorio

# La deuxième commande ci-dessous est un contournement temporaire d'un bug de python3-matplotlib
RUN apt-get -y install git python3 python3-matplotlib ; \
	sed -i s/"%{file}'"/"%{file}\\\\\\\\n'"/ /usr/lib/python3/dist-packages/matplotlib/font_manager.py


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
