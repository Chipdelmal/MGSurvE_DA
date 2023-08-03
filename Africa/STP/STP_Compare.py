#!/usr/bin/env python
# -*- coding: utf-8 -*-

from glob import glob
import numpy as np
import pandas as pd
from os import path
from sys import argv
from glob import glob
import cartopy.crs as ccrs
import shapely.geometry as sgeom
from cartopy.geodesic import Geodesic
import matplotlib.pyplot as plt
import MGSurvE as srv
import auxiliary as aux
from copy import deepcopy
plt.rcParams['axes.facecolor']='#00000000'
plt.rcParams['savefig.facecolor']='#00000000'


###############################################################################
# Bash and user inputs
###############################################################################
if srv.isNotebook():
    # User input (interactive session)
    (ID, AP) = ('STPD', 'max')
else:
    # Bash call input
    (ID, AP) = argv[1:]
GENS = 5000
FPAT = ID+'-'+AP+'_{}*'
(TRPS, COLS) =  (
    ['25', '30'],
    ['#390099', '#072ac8', '#e01a4f', '#ee964b'],
)
MPATS = ['man', ]
###############################################################################
# File ID
###############################################################################
OUT_PTH = '/RAID5/marshallShare/MGSurvE_v3/{}_{}'.format(ID, GENS)
srv.makeFolder(OUT_PTH)
###############################################################################
# Load Files
###############################################################################
(logs, traces) = ([], [])
for trps in TRPS:
    logFiles = sorted(glob(path.join(OUT_PTH, (FPAT+'LOG.csv').format(trps))))
    logs.append([pd.read_csv(f) for f in logFiles])
mins = [np.array([fc['min'].values for fc in log]) for log in logs]
# minFits = [m[2500] for m in mins[3]]
# minVal = min(minFits) 
# minIdx = minFits. index(minVal)
# print('{} @ {}'.format(minVal, minIdx+1))
###############################################################################
# Plot GA Evolution
###############################################################################
(XRAN, YRAN) = ((0, 1000), (0, 3000))
(fig, ax) = plt.subplots(figsize=(25, 3))
for (ix, trc) in enumerate(mins):
    ax.plot(trc.T, color=COLS[ix]+'77', lw=1.25)
ax.set_xlim(0, XRAN[1])
ax.set_ylim(YRAN[0], YRAN[1])
ax.hlines(np.arange(YRAN[0], YRAN[1]+25, 1000), XRAN[0], XRAN[1], color='#00000055', lw=1, zorder=-10)
ax.vlines(np.arange(XRAN[0], XRAN[1]+20, 100),  YRAN[0], YRAN[1], color='#00000055', lw=1, zorder=-10)
ax.set_xticks([])
ax.set_yticks([])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
fig.savefig(
    path.join(OUT_PTH, (FPAT[:-7]+'GA.png')), 
    facecolor=None, bbox_inches='tight', transparent=True,
    pad_inches=0, dpi=350
)
plt.close('all')
###############################################################################
# Load Landscape
###############################################################################
for trps in TRPS:
    lndFiles = sorted(glob(path.join(OUT_PTH, (FPAT+'TRP.pkl').format(trps))))
    lnd = srv.loadLandscape(
        OUT_PTH, lndFiles[0].split('/')[-1].split('.')[0], 
        fExt='pkl'
    )
    # Traps Kernels ---------------------------------------------------------------
    (XRAN, YRAN) = ((0, 100), (0, 1))
    (fig, ax) = plt.subplots(1, 1, figsize=(25, 3), sharey=False)
    (fig, ax) = srv.plotTrapsKernels(
        fig, ax, lnd, distRange=(XRAN[0], XRAN[1]), aspect=.125
    )
    ax.set_xticks([])
    ax.set_yticks([])
    ax.hlines(np.arange(YRAN[0], YRAN[1]+.25, .25), XRAN[0], XRAN[1], color='#00000055', lw=1, zorder=-10)
    ax.vlines(np.arange(XRAN[0], XRAN[1]+20, 12.5), YRAN[0], YRAN[1], color='#00000055', lw=1, zorder=-10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    fig.savefig(
        path.join(OUT_PTH, '{}-{}_KER.png'.format(ID, trps)), 
        facecolor=None, bbox_inches='tight', 
        pad_inches=0, dpi=300, transparent=True
    )
    plt.close('all')
###############################################################################
# Inspect Landscape
###############################################################################
PRINT_IDS = {'sites': False, 'traps': False}
(outer, itr, gen) = ('max', 1, GENS)
trps = '25'
for (logIx, trps) in enumerate(TRPS):
    lndFiles = sorted(glob(path.join(OUT_PTH, (FPAT+'TRP.pkl').format(trps))))
    lnd = srv.loadLandscape(
        OUT_PTH, lndFiles[0].split('/')[-1].split('.')[0], 
        fExt='pkl'
    )
    if ID == 'STPD':
        itrsFitsPos = [aux.getBestTraps(l) for l in logs[logIx]]
        (fitVal, trpPos) = sorted(itrsFitsPos, key=lambda x: x[0])[0]
        fitsFun = aux.switchFunction(MPATS[0])
        trapsCoords = srv.chromosomeIDtoXY(trpPos, lnd.pointID, lnd.pointCoords).T
    else:
        itrsFitsPos = [aux.getBestTraps(l, discrete=False) for l in logs[logIx]]
        (fitVal, trpPos) = sorted(itrsFitsPos, key=lambda x: x[0])[0]
        fitsFun = aux.switchFunction(MPATS[logIx])
        trapsCoords = np.reshape(trpPos, (-1, 2)).T
    trapsLocs = pd.DataFrame(
        np.vstack([trapsCoords, lnd.trapsTypes, lnd.trapsFixed]).T, 
        columns=['lon', 'lat', 't', 'f']
    )
    trapsLocs['t'] = trapsLocs['t'].astype('int64')
    trapsLocs['f'] = trapsLocs['f'].astype('int64')
    # Update landscape --------------------------------------------------------
    lnd.updateTraps(trapsLocs, lnd.trapsKernels)
    if ID == 'STPD':
        fitness = srv.calcDiscreteFitness(
            trpPos, lnd, optimFunction=srv.getDaysTillTrapped,
            optimFunctionArgs={'inner': np.sum, 'outer': fitsFun}
        )[0]
    else:
        fitness = srv.calcFitness(
            trpPos, lnd, optimFunction=srv.getDaysTillTrapped,
            optimFunctionArgs={'inner': np.sum, 'outer': fitsFun}
        )[0]
    assert(np.isclose(fitVal, fitness))
    # Plot --------------------------------------------------------------------  
    (fig, ax) = (
        plt.figure(figsize=(15, 15)),
        plt.axes(projection=ccrs.PlateCarree())
    )
    lnd.plotSites(fig, ax, size=250)
    lnd.plotLandBoundary(fig, ax)
    lnd.updateTrapsRadii([0.250, 0.125, 0.100])
    # lnd.plotMigrationNetwork(
    #     fig, ax, lineWidth=30, alphaMin=.25, alphaAmplitude=2.5
    # )
    lnd.plotTraps(
        fig, ax, size=750,
        zorders=(30, 25), transparencyHex='88', 
        proj=ccrs.PlateCarree()
    )
    srv.plotFitness(
        fig, ax, fitness, 
        fmt='{:.0f}', fontSize=30, color='#00000066', pos=(0.75, 0.10)
    )
    srv.plotClean(fig, ax, bbox=((6.45, 6.77), (-0.02, 0.42)))
    if PRINT_IDS['sites']:
        for (ix, xy) in enumerate(lnd.pointCoords):
            ax.text(
                xy[0], xy[1], int(ix), 
                fontsize=3.5, zorder=10, ha='center', va='center_baseline'
            )
    if PRINT_IDS['traps']:
        for (ix, xy) in enumerate(lnd.trapsCoords):
            ax.text(
                xy[0], xy[1], int(ix), 
                fontsize=10, zorder=50, ha='center', va='center_baseline'
            )
    fig.savefig(
        path.join(OUT_PTH, (FPAT[:-1]+'.png').format(trps)), 
        facecolor='w', bbox_inches='tight', pad_inches=0.1, dpi=350,
        transparent=False
    )
    plt.close('all')
###############################################################################
# Export Landscape for MGDrivE
###############################################################################
pops = pd.read_csv(path.join('./GEO', 'STP_LatLonN.csv'))['pop']
lndDF = lnd.exportForMGDrivE()