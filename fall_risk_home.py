"""
Lukas Adamowicz

June 15th, 2018

Python 3.6 on Windows 10 x64
"""

from os import walk, sep
from numpy import genfromtxt, append, where, array
import pickle
import matplotlib.pyplot as pl
import matplotlib.collections as mc
import matplotlib.patches as mp
from time import localtime


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
        t0, a0, i0, s0, wd0, ws0 = genfromtxt(subjs[subj][0], skip_header=1, unpack=True, delimiter=',', dtype='str',
                                              usecols=(0,2,3,4,5,6))
        try:  # if the sensor didn't record for a long time, (ie S0003) need this check
            t1, a1, i1, s1, wd1, ws1 = genfromtxt(subjs[subj][1], skip_header=1, unpack=True, delimiter=',', dtype='str'
                                                  , usecols=(0,2,3,4,5,6))
        except ValueError:  # if the sensors didn't record the whole time, append empty lists
            t1, a1, i1, s1, wd1, ws1 = [], [], [], [], [], []

        data[subj] = dict()

        # accumulate data
        data[subj]['time'] = append(t0, t1)
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
        for key in ['time', 'intensity', 'walking distance', 'walking speed']:
            data[subj][key] = data[subj][key].astype('float')

    return data

# importing data
base = "C:\\Users\\Lukas Adamowicz\\Documents\\School\\Masters\\Project - MS Fall Study\\Data\\MS Fall At Home Analytics"

try:  # data is serialized later for faster importing.  check if the file exists
    data_file = open(base + sep + 'data.pickle', 'rb')
    data = pickle.load(data_file)
    data_file.close()
# if the file doesn't exist
except FileNotFoundError:

    data = import_data(base)

    fid = open(base + sep + 'data.pickle', 'wb')
    pickle.dump(data, fid)
    fid.close()

# data plotting

clrs = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b','#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
        '#ffffff']
activities = ['MOVING:LYING_MOVING', 'MOVING:STANDING_MOVING:OTHER', 'MOVING:STANDING_MOVING:WALKING', 'RESTING:LYING',
              'RESTING:SITTING', 'RESTING:STANDING', 'SLEEPING:ASLEEP', 'SLEEPING:AWAKE', 'STAIR_ASCENT',
              'STAIR_DESCENT', 'None']

mov_patch = [mp.Patch(color=clrs[0], label=activities[0].split(':')[-1].capitalize()),
             mp.Patch(color=clrs[1], label=activities[1].split(':')[-1].capitalize()),
             mp.Patch(color=clrs[2], label=activities[2].split(':')[-1].capitalize())]
rest_patch = [mp.Patch(color=clrs[3], label=activities[3].split(':')[-1].capitalize()),
              mp.Patch(color=clrs[4], label=activities[4].split(':')[-1].capitalize()),
              mp.Patch(color=clrs[5], label=activities[5].split(':')[-1].capitalize())]
sleep_patch = [mp.Patch(color=clrs[6], label=activities[6].split(':')[-1].capitalize()),
               mp.Patch(color=clrs[7], label=activities[7].split(':')[-1].capitalize())]
stair_patch = [mp.Patch(color=clrs[8], label=activities[8].split(':')[-1].capitalize()),
               mp.Patch(color=clrs[9], label=activities[9].split(':')[-1].capitalize())]

plots = dict()
for subj in data.keys():
    plots[subj] = dict()
    plots[subj]['f'], plots[subj]['ax'] = pl.subplots(figsize=(12,2))

    colors = []
    for act in data[subj]['activity']:
        colors.append(clrs[where(act == array(activities))[0][0]])

    segments = []
    for x1, x2 in zip(data[subj]['time'], data[subj]['time'][1:]):
        segments.append([(x1, 1), (x2, 1)])

    lc = mc.LineCollection(segments, colors=colors, linewidths=45)

    plots[subj]['ax'].add_collection(lc)
    plots[subj]['ax'].set_xlim(data[subj]['time'][0], data[subj]['time'][-1])
    plots[subj]['ax'].set_ylim(0.75, 1.25)
    plots[subj]['ax'].autoscale(axis='y', tight=True)

    xtls = []  # x-tick labels
    xts = []  # x-tick locations

    for t in data[subj]['time']:
        time = localtime(t/1000)
        if time[3] % 2 == 1 and time[4] == 0:
            xts.append(t)
            xtls.append(f"{time[3]}:00")

    plots[subj]['ax'].set_xticks(xts)
    plots[subj]['ax'].set_xticklabels(xtls)
    plots[subj]['ax'].set_xlabel('Time of Day')

    plots[subj]['ax'].add_artist(pl.legend(handles=mov_patch, bbox_to_anchor=(0., 1.02, .25, .102), loc=3,
                                           mode='expand', title='Moving'))
    plots[subj]['ax'].add_artist(pl.legend(handles=rest_patch, bbox_to_anchor=(.25, 1.02, .25, .102), loc=3,
                                           mode='expand', title='Resting'))
    plots[subj]['ax'].add_artist(pl.legend(handles=sleep_patch, bbox_to_anchor=(0.5, 1.02, .25, .102), loc=3,
                                           mode='expand', title='Sleeping'))
    plots[subj]['ax'].add_artist(pl.legend(handles=stair_patch, bbox_to_anchor=(0.75, 1.02, .25, .102), loc=3,
                                           mode='expand', title='Stairs'))

    plots[subj]['ax'].spines['top'].set_visible(False)
    plots[subj]['ax'].spines['right'].set_visible(False)
    plots[subj]['ax'].spines['left'].set_visible(False)
    plots[subj]['ax'].spines['bottom'].set_visible(False)
    plots[subj]['ax'].axes.get_yaxis().set_visible(False)

    plots[subj]['ax'].set_title(subj)

    plots[subj]['f'].tight_layout()




