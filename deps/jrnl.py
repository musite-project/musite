# coding: utf-8
"""Journal utilisable pour le débogage
"""


def log(evenement, mode='a'):
    with open('log', mode) as l:
        l.write(str(evenement) + '\n')
