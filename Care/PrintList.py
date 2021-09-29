import os

def printList(xxx):
    with open(os.path.join('C:/Users/ash/.qgis2/python/plugins/Care', 'completeName.txt'), "w") as file1:
        toFile = repr(xxx)
        file1.write(toFile)

