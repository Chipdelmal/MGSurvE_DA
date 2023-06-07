# !/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Load libraries and limit cores
###############################################################################
import os
import math
import osmnx as ox
from os import path
from sys import argv
from glob import glob
from copy import deepcopy
from engineering_notation import EngNumber
import cartopy.crs as ccrs
import compress_pickle as pkl
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from numpy.random import uniform
import MGSurvE as srv
import auxiliary as aux
import constants as cst
matplotlib.rc('font', family='Ubuntu Condensed')

if srv.isNotebook():
    (USR, COUNTRY, CODE, COMMUNE, COORDS, GENS, FRACTION) = (
        'zelda', 'Burkina Faso', 'BFA', 
        'Basberike', (13.14717,-1.03444), 100, 50
    )
else:
    (USR, COUNTRY, CODE, COMMUNE, COORDS, GENS, FRACTION) = argv[1:]
    (COORDS, GENS, FRACTION) = (
        tuple(map(float, COORDS.split(','))),
        int(GENS), int(FRACTION)
    )
(PROJ, FOOTPRINT, OVW, VERBOSE) = (
    ccrs.PlateCarree(), True, 
    {'dist': False, 'kernel': False},
    False
)
###############################################################################
# Set Paths
###############################################################################
paths = aux.userPaths(USR)
(pthDst, pthMig, pthAgg, pthAct) = (
    path.join(paths['data'], CODE, COMMUNE+'_DST.bz'),
    path.join(paths['data'], CODE, COMMUNE+'_MIG.bz'),
    path.join(paths['data'], CODE, COMMUNE+'_AGG.bz'),
    path.join(paths['data'], CODE, COMMUNE+'_ACT.csv')
)
(OUT_LOG, OUT_LND) = (
    path.join(paths['data'], CODE, COMMUNE+'_LOG.csv'),
    path.join(paths['data'], CODE, COMMUNE+'_LND.bz')
)
###############################################################################
# Read from Disk
###############################################################################
(BLD, NTW) = (
    pkl.load(path.join(paths['data'], CODE, COMMUNE+'_BLD.bz')),
    pkl.load(path.join(paths['data'], CODE, COMMUNE+'_NTW.bz'))
)
(MIG, MAG, LAG) = (
    pkl.load(path.join(paths['data'], CODE, COMMUNE+'_MIG.bz')),
    pkl.load(path.join(paths['data'], CODE, COMMUNE+'_AGG.bz')),
    pd.read_csv(pthAct)
)
###############################################################################
# Loading Results
###############################################################################
SITES_NUM = LAG.shape[0]
TRPS_NUM = math.floor(SITES_NUM/FRACTION)
fNameBase = '{}-{:04d}_{:04d}-{}'.format(COMMUNE, SITES_NUM, TRPS_NUM, '*')
(filesLog, filesLnd) = (
    sorted(glob(path.join(paths['data'], CODE, fNameBase+'_LOG.csv'))),
    sorted(glob(path.join(paths['data'], CODE, fNameBase+'_LND.pkl')))
)
logs = [pd.read_csv(f) for f in filesLog]
lnds = [
    srv.loadLandscape(
        path.join(paths['data'], CODE), f.split('/')[-1].split('.')[0],
        fExt='pkl'
    ) 
    for f in filesLnd
]
mins = [np.array(i['min']) for i in logs]
minIx = [i[-1] for i in mins].index(min([i[-1] for i in mins]))
###############################################################################
# Plotting Traps
###############################################################################
XRAN = (0, 100)
(fig, ax) = plt.subplots(1, 1, figsize=(25, 3), sharey=False)
(fig, ax) = srv.plotTrapsKernels(
    fig, ax, lnds[0], distRange=(XRAN[0], XRAN[1]), aspect=.125
)
# ax.set_xticks([])
# ax.set_yticks([])
# ax.spines['top'].set_visible(False)
# ax.spines['right'].set_visible(False)
# ax.spines['bottom'].set_visible(False)
# ax.spines['left'].set_visible(False)
fig.savefig(
    path.join(paths['data'], CODE, fNameBase[:-2]+'-KER.png'), 
    facecolor=None, bbox_inches='tight', transparent=True,
    pad_inches=0, dpi=350
)
plt.close('all')
###############################################################################
# Plot GA Evolution
###############################################################################
(XRAN, YRAN) = ((0, 1000), (0, 20))
(fig, ax) = plt.subplots(figsize=(25, 3))
for (ix, trc) in enumerate(mins):
    ax.plot(trc.T, color='#390099'+'77', lw=1.25)
ax.set_xlim(0, XRAN[1])
ax.set_ylim(0, YRAN[1])
ax.hlines(np.arange(YRAN[0], YRAN[1]+25, 1000), XRAN[0], XRAN[1], color='#00000055', lw=1, zorder=-10)
ax.vlines(np.arange(XRAN[0], XRAN[1]+20, 100),  YRAN[0], YRAN[1], color='#00000055', lw=1, zorder=-10)
# ax.set_xticks([])
# ax.set_yticks([])
# ax.spines['top'].set_visible(False)
# ax.spines['right'].set_visible(False)
# ax.spines['bottom'].set_visible(False)
# ax.spines['left'].set_visible(False)
fig.savefig(
    path.join(paths['data'], CODE, fNameBase[:-2]+'-GAV.png'), 
    facecolor=None, bbox_inches='tight', transparent=True,
    pad_inches=0, dpi=350
)
plt.close('all')
###############################################################################
# Plot Optimal
###############################################################################
(STYLE_GD, STYLE_BG, STYLE_TX, STYLE_CN, STYLE_BD, STYLE_RD) = cst.MAP_STYLE_A
lnd = lnds[minIx]
lnd.updateTrapsRadii([1])
# Landscape -------------------------------------------------------------------
(fig, ax) = (
    plt.figure(figsize=(15, 15), facecolor=STYLE_BG['color']), 
    plt.axes(projection=ccrs.PlateCarree())
)
G = ox.project_graph(NTW, to_crs=ccrs.PlateCarree())
(fig, ax) = ox.plot_graph(
    G, ax, node_size=0, figsize=(40, 40), show=False,
    bgcolor=STYLE_BG['color'], edge_color=STYLE_RD['color'], 
    edge_alpha=STYLE_RD['alpha'], edge_linewidth=STYLE_RD['width']
)
(fig, ax) = ox.plot_footprints(
    BLD, ax=ax, save=False, show=False, close=False,
    bgcolor=STYLE_BG['color'], color=STYLE_BD['color'], 
    alpha=STYLE_BD['alpha']
)
(fig, ax) = ox.plot_footprints(
    BLD, ax=ax, save=False, show=False, close=False,
    bgcolor=STYLE_BG['color'], alpha=0.65,
    color=list(BLD['cluster_color']), 
)
lnd.plotTraps(
    fig, ax, 
    size=500, zorders=(30, 25), transparencyHex='33', 
    proj=ccrs.PlateCarree()
)
# lnd.plotSites(fig, ax, size=75)
# lnd.plotMigrationNetwork(
#     fig, ax, 
#     lineColor='#ffffff', lineWidth=1, 
#     alphaMin=.125, alphaAmplitude=10000, zorder=20
# )
# srv.plotClean(fig, ax, bbox=lnd.landLimits)
ax.set_facecolor(STYLE_BG['color'])
fig.savefig(
    path.join(paths['data'], CODE, fNameBase+'_OPT'),
    transparent=False, facecolor=STYLE_BG['color'],
    bbox_inches='tight', pad_inches=0, dpi=400
)
plt.close('all')
