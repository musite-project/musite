#!/bin/bash

if [ ! -e /opt/musite/etc/config.py ] ; then
    cp /opt/musite/etc.sample/config.py /opt/musite/etc/
    sed -i "s/DEVEL = True/DEVEL = False/" /opt/musite/etc/config.py
    sed -i "s/PORT = 8080/PORT = 80/" /opt/musite/etc/config.py
fi
if [ ! -e /opt/musite/etc/utilisateurs ] ; then
    cp /opt/musite/etc.sample/utilisateurs /opt/musite/etc/
fi
if [ ! -e /opt/musite/etc/groupes ] ; then
    cp /opt/musite/etc.sample/groupes /opt/musite/etc/
fi
/opt/musite/serveur.py
