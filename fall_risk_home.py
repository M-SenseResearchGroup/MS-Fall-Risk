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
from time import localtime, mktime


def import_mc10_analytics_data(base_loc):
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


def import_sms_data(file):
    # [i,j] where i is the subject, j is the column (response, time)
    raw_data = genfromtxt(file, skip_header=3, delimiter=',',
                          usecols=tuple(i for i in range(129)), dtype=str)

    subjs = []

    for i in range(len(raw_data[:, 0])):
        if raw_data[i, 1] != '':
            subjs.append((raw_data[i, 0].lower(), i))

    sdata = dict()
    for subj, i in subjs:
        sdata[subj] = dict()
        sdata[subj]['fat'] = dict()
        sdata[subj]['fat']['ans'] = raw_data[i, 1:][[i for i in range(0, 32, 2)]]
        sdata[subj]['fat']['time'] = raw_data[i, 1:][[i for i in range(1, 32, 2)]]

        sdata[subj]['fof'] = dict()
        sdata[subj]['fof']['ans'] = raw_data[i, 1:][[i for i in range(32, 64, 2)]]
        sdata[subj]['fof']['time'] = raw_data[i, 1:][[i for i in range(33, 64, 2)]]

        sdata[subj]['fall'] = dict()
        sdata[subj]['fall']['ans'] = raw_data[i, 1:][[i for i in range(64, 96, 2)]]
        sdata[subj]['fall']['time'] = raw_data[i, 1:][[i for i in range(65, 96, 2)]]

        sdata[subj]['cst'] = dict()
        sdata[subj]['cst']['ans'] = raw_data[i, 1:][[i for i in range(96, 128, 2)]]
        sdata[subj]['cst']['time'] = raw_data[i, 1:][[i for i in range(97, 128, 2)]]

    return sdata


def text_message_xy(times, ans):
    x = []
    y = []
    for ti, a in zip(times, ans):
        if a != '888' and a != '999':
            y.append(a)

            p1, p2 = ti.split(' ')[0], ti.split(' ')[1]
            mo, da, yr = p1.split('/')
            hr, mi = p2.split(':')

            stime = (int(yr), int(mo), int(da), int(hr), int(mi), 0, 0, 0, -1)

            x.append(mktime(stime))

    return x, y

# ******************************************************************************************************************
# Importing Data
# ******************************************************************************************************************


base = "C:\\Users\\Lukas Adamowicz\\Documents\\School\\Masters\\Project - MS Fall Study\\Data"
mc10_base = base + sep + "MS Fall At Home Analytics"

try:  # data is serialized later for faster importing.  check if the file exists
    data_file = open(mc10_base + sep + 'data.pickle', 'rb')
    data = pickle.load(data_file)
    data_file.close()
# if the file doesn't exist
except FileNotFoundError:
    data = import_mc10_analytics_data(mc10_base)

    fid = open(mc10_base + sep + 'data.pickle', 'wb')
    pickle.dump(data, fid)
    fid.close()

try:
    sms_file = open(base + sep + "sms_data.pickle", 'rb')
    sms = pickle.load(sms_file)
    sms_file.close()
except FileNotFoundError:
    sms = import_sms_data(base + sep + "Spreadsheet for MS Fall Study.csv")

    fid = open(base + sep + "sms_data.pickle", 'wb')
    pickle.dump(sms, fid)
    fid.close()


# ******************************************************************************************************************
# Data Plotting
# ******************************************************************************************************************

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
    plots[subj]['f'], plots[subj]['ax'] = pl.subplots(6, figsize=(12, 8), sharex=True)

    # ******************************************************************************************************************
    # Plotting activity classifications
    # ******************************************************************************************************************
    colors = []
    for act in data[subj]['activity']:
        colors.append(clrs[where(act == array(activities))[0][0]])

    segments = []
    for x1, x2 in zip(data[subj]['time'], data[subj]['time'][1:]):
        segments.append([(x1, 1), (x2, 1)])

    lc = mc.LineCollection(segments, colors=colors, linewidths=45)

    plots[subj]['ax'][-1].add_collection(lc)
    plots[subj]['ax'][-1].set_xlim(data[subj]['time'][0], data[subj]['time'][-1])
    plots[subj]['ax'][-1].set_ylim(0.75, 1.25)
    plots[subj]['ax'][-1].autoscale(axis='y', tight=True)

    xtls = []  # x-tick labels
    xts = []  # x-tick locations

    for t in data[subj]['time']:
        time = localtime(t/1000)
        if time[3] % 2 == 1 and time[4] == 0:
            xts.append(t)
            xtls.append(f"{time[3]}:00")

    plots[subj]['ax'][-1].set_xticks(xts)
    plots[subj]['ax'][-1].set_xticklabels(xtls)
    plots[subj]['ax'][-1].set_xlabel('Time of Day')

    plots[subj]['ax'][-1].add_artist(pl.legend(handles=mov_patch, bbox_to_anchor=(0., -.5, .25, .102), loc=2,
                                               mode='expand', title='Moving'))
    plots[subj]['ax'][-1].add_artist(pl.legend(handles=rest_patch, bbox_to_anchor=(.25, -.5, .25, .102), loc=2,
                                               mode='expand', title='Resting'))
    plots[subj]['ax'][-1].add_artist(pl.legend(handles=sleep_patch, bbox_to_anchor=(.5, -.5, .25, .102), loc=2,
                                               mode='expand', title='Sleeping'))
    plots[subj]['ax'][-1].add_artist(pl.legend(handles=stair_patch, bbox_to_anchor=(.75, -.5, .25, .102), loc=2,
                                               mode='expand', title='Stairs'))

    plots[subj]['ax'][-1].spines['top'].set_visible(False)
    plots[subj]['ax'][-1].spines['right'].set_visible(False)
    plots[subj]['ax'][-1].spines['left'].set_visible(False)
    plots[subj]['ax'][-1].spines['bottom'].set_visible(False)
    plots[subj]['ax'][-1].axes.get_yaxis().set_visible(False)

    # ******************************************************************************************************************
    # Plotting activity intensity
    # ******************************************************************************************************************

    plots[subj]['ax'][-2].fill_between(data[subj]['time'], data[subj]['intensity'])
    plots[subj]['ax'][-2].set_ylim(ymin=0)
    plots[subj]['ax'][-2].set_title('Intensity')

    plots[subj]['ax'][-2].tick_params(axis='x', length=0)

    # ******************************************************************************************************************
    # Plotting text message data
    # ******************************************************************************************************************

    fatx, faty = text_message_xy(sms[subj]['fat']['time'], sms[subj]['fat']['ans'])
    plots[subj]['ax'][0].plot(array(fatx)*1000, array(faty).astype(int), 'o-')

    plots[subj]['ax'][0].set_title('How often has fatigue prevented you completing activities?')
    plots[subj]['ax'][0].set_ylim(.75, 5.5)
    plots[subj]['ax'][0].set_yticks([1, 2, 3, 4, 5])
    plots[subj]['ax'][0].set_yticklabels(['Never', 'Rarely', 'Sometimes', 'Often', 'Always'])

    fofx, fofy = text_message_xy(sms[subj]['fof']['time'], sms[subj]['fof']['ans'])
    plots[subj]['ax'][1].plot(array(fofx) * 1000, array(fofy).astype(int), 'o-')

    plots[subj]['ax'][1].set_title('How confident that you would not fall')
    plots[subj]['ax'][1].set_ylim(.75, 5.5)
    plots[subj]['ax'][1].set_yticks([1, 2, 3, 4, 5])
    plots[subj]['ax'][1].set_yticklabels(['Very Confident', 'Confident', 'Neutral', 'Not Confident',
                                          'Very Not Confident'])

    cstx, csty = text_message_xy(sms[subj]['cst']['time'], sms[subj]['cst']['ans'])
    plots[subj]['ax'][2].plot(array(cstx) * 1000, array(csty).astype(int), 'o-')

    plots[subj]['ax'][2].set_title('Chair Stand Test')

    fallx, fally_old = text_message_xy(sms[subj]['cst']['time'], sms[subj]['cst']['ans'])
    fally = [1 if x == 'y' else 0 for x in fally_old]
    plots[subj]['ax'][3].plot(array(fallx) * 1000, fally, 'o-')

    plots[subj]['ax'][3].set_title('Did you fall?')
    plots[subj]['ax'][3].set_yticks([0, 1])
    plots[subj]['ax'][3].set_yticklabels(['No', 'Yes'])

    # ******************************************************************************************************************
    # Figure modifications
    # ******************************************************************************************************************

    plots[subj]['f'].tight_layout()
    plots[subj]['f'].suptitle(subj, x=.25, y=.99)
