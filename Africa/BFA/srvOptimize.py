# !/usr/bin/env python
# -*- coding: utf-8 -*-

CORES = 32
###############################################################################
# Load libraries and limit cores
###############################################################################
import os
os.environ["OMP_NUM_THREADS"] = str(CORES)
os.environ["OPENBLAS_NUM_THREADS"] = str(CORES)
os.environ["MKL_NUM_THREADS"] = str(CORES)
os.environ["VECLIB_MAXIMUM_THREADS"] = str(CORES)
os.environ["NUMEXPR_NUM_THREADS"] = str(CORES)
import math
import osmnx as ox
from os import path
from sys import argv
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
    (USR, COUNTRY, CODE, COMMUNE, COORDS, GENS, FRACTION, REP) = (
        'zelda', 'Burkina Faso', 'BFA', 
        'Reo', (12.3201, -2.4753), 1000, 100, 0
    )
else:
    (USR, COUNTRY, CODE, COMMUNE, COORDS, GENS, FRACTION, REP) = argv[1:]
    (COORDS, GENS, FRACTION, REP) = (
        tuple(map(float, COORDS.split(','))),
        int(GENS), int(FRACTION), int(REP)
    )
(PROJ, FOOTPRINT, OVW, VERBOSE) = (
    ccrs.PlateCarree(), True, 
    {'dist': False, 'kernel': False},
    True
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
# Land Variables
###############################################################################
SITES_NUM = LAG.shape[0]
LAG['t'] = 0*SITES_NUM
BBOX = (
    (min(LAG['lon']), max(LAG['lon'])),
    (min(LAG['lat']), max(LAG['lat']))
)
CNTR = [i[0]+(i[1]-i[0])/2 for i in BBOX]
###############################################################################
# Traps' Data
###############################################################################
TRPS_NUM = math.floor(SITES_NUM/FRACTION)
(initLon, initLat) = (
    uniform(BBOX[0][0], BBOX[0][1], TRPS_NUM), 
    uniform(BBOX[0][0], BBOX[0][1], TRPS_NUM)
)
sid = [0]*TRPS_NUM
traps = pd.DataFrame({
    'sid': sid,
    'lon': initLon, 'lat': initLat, 
    't': [0]*TRPS_NUM, 'f': [0]*TRPS_NUM
})
tKer = {0:{'kernel': srv.exponentialDecay, 'params': {'A': 0.5, 'b': 0.041674}}}
###############################################################################
# Setting Landscape Up
###############################################################################
lnd = srv.Landscape(
    LAG, migrationMatrix=MAG,
    traps=traps, trapsKernels=tKer, landLimits=BBOX,
    trapsRadii=[0.250, 0.125, 0.100],
)
bbox = lnd.getBoundingBox()
trpMsk = srv.genFixedTrapsMask(lnd.trapsFixed)
###############################################################################
# GA Settings
############################################################################### 
POP_SIZE = int(10*(lnd.trapsNumber*1.5))
(MAT, MUT, SEL) = (
    {'cxpb':  0.300, 'indpb': 0.35}, 
    {'mutpb': 0.375, 'indpb': 0.50},
    {'tSize': 3}
)
lndGA = deepcopy(lnd)
# Reducing the bbox for init sampling -----------------------------------------
redFract = .25
reduction = [(i[1]-i[0])/2*redFract for i in bbox]
bboxRed = [(i[0]+r, i[1]-r) for (i, r) in zip(bbox,reduction)]
###############################################################################
# Registering GA functions
############################################################################### 
outer = np.mean
(lnd, logbook) = srv.optimizeDiscreteTrapsGA(
    lndGA, pop_size=POP_SIZE, generations=GENS, verbose=VERBOSE,
    mating_params=MAT, mutation_params=MUT, selection_params=SEL,
    fitFuns={'inner': np.sum, 'outer': outer}
)
###############################################################################
# Exporting Results
############################################################################### 
fNameBase = '{}-{:04d}_{:04d}-{:02d}'.format(COMMUNE, SITES_NUM, TRPS_NUM, REP)
srv.exportLog(
    logbook, 
    path.join(paths['data'], CODE), fNameBase+'_LOG'
)
srv.dumpLandscape(
    lnd, 
    path.join(paths['data'], CODE), fNameBase+'_LND',
    fExt='pkl'
)
###############################################################################
# Plot Results
###############################################################################
(STYLE_GD, STYLE_BG, STYLE_TX, STYLE_CN, STYLE_BD, STYLE_RD) = cst.MAP_STYLE_A
(PAD, DPI) = (0, 250)
(FIG_SIZE, PROJ, BSCA) = ((15, 15), ccrs.PlateCarree(), 0.001)
lnd = srv.loadLandscape(
    path.join(paths['data'], CODE), fNameBase+'_LND',
    fExt='pkl'
)
lnd.updateTrapsRadii([1])
# Landscape -------------------------------------------------------------------
BBOX = (
    (lnd.landLimits[0][0]-BSCA, lnd.landLimits[0][1]+BSCA),
    (lnd.landLimits[1][0]-BSCA, lnd.landLimits[1][1]+BSCA)
)
(fig, ax) = (
    plt.figure(figsize=FIG_SIZE, facecolor=STYLE_BG['color']), 
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
    size=500, zorders=(30, 25), transparencyHex='99', 
    proj=ccrs.PlateCarree()
)
ax.text(
    0.99, 0.01, 
    'Min: {:.02f}'.format(min(logbook['min'])), 
    transform=ax.transAxes, 
    horizontalalignment='right', verticalalignment='bottom', 
    color=STYLE_TX['color'], fontsize=STYLE_TX['size'],
    alpha=0.75
)
srv.plotClean(fig, ax, bbox=BBOX)
ax.set_facecolor(STYLE_BG['color'])
fig.savefig(
    path.join(paths['data'], CODE, fNameBase+'_SRV'),
    transparent=False, facecolor=STYLE_BG['color'],
    bbox_inches='tight', pad_inches=PAD, dpi=DPI
)
plt.close('all')
