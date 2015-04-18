# coding: utf-8
"""Journal utilisable pour le débogage
"""


def log(evenement):
    with open('log', 'a') as l:
        l.write(str(evenement) + '\n')
