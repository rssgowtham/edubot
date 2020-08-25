import os
import glob

def deleteFiles(id):
    file = "media/" + id + "*"
    for filename in glob.glob(file):
        os.remove(filename)