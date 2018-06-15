"""
Lukas Adamowicz

June 15th, 2018

Python 3.6 on Windows 10 x64
"""

from os import walk, sep
from numpy import genfromtxt, append, where
import pickle


def import_data(base_loc):
    walk_res = walk(base_loc)

    files = []

    for root, directory, file in walk_res:
        for i in range(len(file)):
            if 'activity_channels' in file[i]:
                files.append(root + sep + file[i])

    subjs = dict()

    for file in files:
        ind = [i for i, s in enumerate(file.split(sep)) if 's0' in s]
        try:
            subjs[file.split('\\')[ind[0]]]
        except KeyError:
            subjs[file.split('\\')[ind[0]]] = []
        subjs[file.split('\\')[ind[0]]].append(file)

    data = dict()

    for subj in subjs.keys():
        # import activity classification data
        t0, d0, a0, i0, s0, wd0, ws0 = genfromtxt(subjs[subj][0], skip_header=1, unpack=True, delimiter=',',
                                                  dtype='str')
        try:  # if the sensor didn't record for a long time, (ie S0003) need this check
            t1, d1, a1, i1, s1, wd1, ws1 = genfromtxt(subjs[subj][1], skip_header=1, unpack=True, delimiter=',',
                                                      dtype='str')
        except ValueError:  # if the sensors didn't record the whole time, append empty lists
            t1, d1, a1, i1, s1, wd1, ws1 = [], [], [], [], [], [], []

        data[subj] = dict()

        # accumulate data
        data[subj]['time'] = append(t0, t1)
        data[subj]['date'] = append(d0, d1)
        data[subj]['activity'] = append(a0, a1)
        data[subj]['intensity'] = append(i0, i1)
        data[subj]['walking distance'] = append(wd0, wd1)
        data[subj]['walking speed'] = append(ws0, ws1)

        # determine where the sensors were being worn
        wearing = where(data[subj]['walking speed'] != '')

        # strip data form where sensors weren't being worn
        for key in data[subj].keys():
            data[subj][key] = data[subj][key][wearing]

        # convert numerical data to floats
        for key in ['intensity', 'walking distance', 'walking speed']:
            data[subj][key] = data[subj][key].astype('float')

    return data


base = "C:\\Users\\Lukas Adamowicz\\Documents\\School\\Masters\\Project - MS Fall Study\\Data\\MS Fall At Home Analytics"

try:  # data is serialized later for faster importing.  check if the file exists
    data_file = open(base + sep + 'data.pickle', 'rb')
    pickle.load(data_file)
    data_file.close()
# if the file doesn't exist
except FileNotFoundError:

    data = import_data(base)

    fid = open(base + sep + 'data.pickle', 'wb')
    pickle.dump(data, fid)
    fid.close()
