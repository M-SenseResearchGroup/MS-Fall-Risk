"""
Lukas Adamowicz

June 15th, 2018

Python 3.6 on Windows 10 x64
"""

from os import walk
from numpy import argwhere


base = "C:\\Users\\Lukas Adamowicz\\Documents\\School\\Masters\\Project - MS Fall Study\\Data\\MS Fall At Home Analytics"

walk_res = walk(base)

files = []

for root, directory, file in walk_res:
    for i in range(len(file)):
        if 'activity_channels' in file[i]:
            files.append(root + file[i])

subjs = dict()

for file in files:
    ind = [i for i, s in enumerate(file.split('\\')) if 's0' in s]
    try:
        subjs[file.split('\\')[ind[0]]]
    except KeyError:
        subjs[file.split('\\')[ind[0]]] = []
    subjs[file.split('\\')[ind[0]]].append(file)
