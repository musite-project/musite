def log(evenement):
    with open('log','a') as l:
        l.write(str(evenement) + '\n')