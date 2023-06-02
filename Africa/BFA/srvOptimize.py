# !/usr/bin/env python
# -*- coding: utf-8 -*-

CORES = 16
###############################################################################
# Load libraries and limit cores
###############################################################################
import os
import math
os.environ["OMP_NUM_THREADS"] = str(CORES)
os.environ["OPENBLAS_NUM_THREADS"] = str(CORES)
os.environ["MKL_NUM_THREADS"] = str(CORES)
os.environ["VECLIB_MAXIMUM_THREADS"] = str(CORES)
os.environ["NUMEXPR_NUM_THREADS"] = str(CORES)
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
import MoNeT_MGDrivE as monet
import MGSurvE as srv
import auxiliary as aux
import constants as cst
matplotlib.rc('font', family='Ubuntu Condensed')

if srv.isNotebook():
    (USR, COUNTRY, CODE, COMMUNE, COORDS, GENS, FRACTION, REP) = (
        'zelda', 'Burkina Faso', 'BFA', 
        'Basberike', (13.14717,-1.03444), 100, 10, 0
    )
else:
    (USR, COUNTRY, CODE, COMMUNE, COORDS, GENS, FRACTION, REP) = argv[1:]
    COORDS = tuple(map(float, COORDS.split(',')))
    GENS = int(GENS)
    FRACTION = int(FRACTION)
(PROJ, FOOTPRINT, OVW, VERBOSE) = (
    ccrs.PlateCarree(), True, 
    {'dist': False, 'kernel': False},
    False
)
MEAN_DISPERSAL = 300
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
tKer = {0: {'kernel': srv.exponentialDecay, 'params': {'A': 0.5, 'b': 0.041674}}}
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
srv.exportLog(
    logbook, path.join(paths['data'], CODE), 
    '{}-{}_{}_-{}_LOG'.format(
        COMMUNE, str(SITES_NUM).zfill(4), str(TRPS_NUM).zfill(4),
        str(REP).zfill(2)
    )
)
srv.dumpLandscape(
    lnd, path.join(paths['data'], CODE), 
    '{}-{}_{}-{}_LND'.format(
        COMMUNE, str(SITES_NUM).zfill(4), str(TRPS_NUM).zfill(4),
        str(REP).zfill(2)
    ),
    fExt='pkl'
)
###############################################################################
# Plot Results
###############################################################################
(STYLE_GD, STYLE_BG, STYLE_TX, STYLE_CN, STYLE_BD, STYLE_RD) = cst.MAP_STYLE_A
lnd = srv.loadLandscape(
    path.join(
        paths['data'], CODE), 
        '{}-{}_{}-{}_LND'.format(
            COMMUNE, str(SITES_NUM).zfill(4), str(TRPS_NUM).zfill(4),
            str(REP).zfill(2)
    ),
    fExt='pkl'
)
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
lnd.updateTrapsRadii([1])
# lnd.plotSites(fig, ax, size=75)
lnd.plotTraps(
    fig, ax, 
    size=500, zorders=(30, 25), transparencyHex='33', 
    proj=ccrs.PlateCarree()
)
# lnd.plotMigrationNetwork(
#     fig, ax, 
#     lineColor='#ffffff', lineWidth=1, 
#     alphaMin=.125, alphaAmplitude=10000, zorder=20
# )
ax.set_facecolor(STYLE_BG['color'])
# srv.plotClean(fig, ax, bbox=lnd.landLimits)
fig.savefig(
    path.join(
        paths['data'], CODE, 
        '{}-{}_{}-{}_SRV'.format(
            COMMUNE, str(SITES_NUM).zfill(4), str(TRPS_NUM).zfill(4),
            str(REP).zfill(2)
        )
    ),
    facecolor='w', bbox_inches='tight', pad_inches=0.2, dpi=400
)
plt.close('all')
