# !/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Load libraries and limit cores
###############################################################################
import os
import math
import subprocess
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
from PIL import Image
# matplotlib.use('agg')
matplotlib.rc('font', family='Ubuntu Condensed')

if srv.isNotebook():
    (USR, COUNTRY, CODE, COMMUNE, COORDS, GENS, FRACTION, REP) = (
        'sami', 'Burkina Faso', 'BFA', 
        'Banfora', (10.6376,-4.7526), 4000, 93, 5
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
(OUT_LOG, OUT_LND, OUT_VID) = (
    path.join(paths['data'], CODE, COMMUNE+'_LOG.csv'),
    path.join(paths['data'], CODE, COMMUNE+'_LND.bz'),
    path.join(paths['data'], CODE, COMMUNE+'_LND.bz')
)
###############################################################################
# Read from Disk
###############################################################################
(BLD, NTW) = (
    pkl.load(path.join(paths['data'], CODE, COMMUNE+'_BLD.bz')),
    pkl.load(path.join(paths['data'], CODE, COMMUNE+'_NTW.bz'))
)
(MAG, LAG) = (
    pkl.load(path.join(paths['data'], CODE, COMMUNE+'_AGG.bz')),
    pd.read_csv(pthAct)
)
# Get filename and create out folder ------------------------------------------
SITES_NUM = LAG.shape[0]
TRPS_NUM = math.floor(SITES_NUM/FRACTION)
fNameBase = '{}-{:04d}_{:04d}-{:02d}'.format(COMMUNE, SITES_NUM, TRPS_NUM, REP)
(log, lnd) = (
    pd.read_csv(path.join(paths['data'], CODE, fNameBase+'_LOG.csv')),
    srv.loadLandscape(path.join(paths['data'], CODE), fNameBase+'_LND', fExt='pkl')
)
###############################################################################
# Examine landscape
###############################################################################
(STYLE_GD, STYLE_BG, STYLE_TX, STYLE_CN, STYLE_BD, STYLE_RD) = cst.MAP_STYLE_A
(PAD, DPI) = (0, 250)
lnd.updateTrapsRadii([1])
bbox = lnd.getBoundingBox()
trpMsk = srv.genFixedTrapsMask(lnd.trapsFixed)
# Get traps ---------------------------------------------------------------
gen=-1
trpEntry = log.iloc[gen]['traps']
trpPos = aux.idStringToArray(trpEntry, discrete=True)
trpCds = srv.chromosomeIDtoXY(trpPos, lnd.pointID, lnd.pointCoords).T
# Assemble and update traps -----------------------------------------------
trapsLocs = pd.DataFrame(
    np.vstack([trpCds, lnd.trapsTypes, lnd.trapsFixed]).T, 
    columns=['lon', 'lat', 't', 'f']
)
trapsLocs['t'] = trapsLocs['t'].astype('int64')
trapsLocs['f'] = trapsLocs['f'].astype('int64')
lnd.updateTraps(trapsLocs, lnd.trapsKernels)
lnd.updateTrapsRadii([1])
fitness = log['min'].iloc[gen]
###############################################################################
# Get Traps Distance
#   https://github.com/gboeing/osmnx-examples/blob/main/notebooks/02-routing-speed-time.ipynb
###############################################################################
G = ox.project_graph(NTW, to_crs=PROJ)
(ix, jx) = (10, 5)
cNode = ox.nearest_nodes(G, np.mean(BLD['centroid_lon']), np.mean(BLD['centroid_lat']))
nNodes = ox.nearest_nodes(G, trapsLocs['lon'], trapsLocs['lat'])
routes = ox.shortest_path(G, TRPS_NUM*[cNode], nNodes)
# routes = ox.shortest_path(G, TRPS_NUM*[nNodes[ix]], nNodes)
# (tPosA, tPosB) = (trapsLocs.iloc[ix], trapsLocs.iloc[jx])
# (cNdeA, cNdeB) = ( 
#     ox.nearest_nodes(G, tPosA['lon'], tPosA['lat']),
#     ox.nearest_nodes(G, tPosB['lon'], tPosB['lat'])
# )
# route = ox.shortest_path(G, cNdeA, cNdeB, weight="length")
###############################################################################
# Plot Landscape
###############################################################################
(FIG_SIZE, PROJ, BSCA) = ((15, 15), ccrs.PlateCarree(), 0.001)
BBOX = (
    (lnd.landLimits[0][0]-BSCA, lnd.landLimits[0][1]+BSCA),
    (lnd.landLimits[1][0]-BSCA, lnd.landLimits[1][1]+BSCA)
)
(fig, ax) = (
    plt.figure(figsize=FIG_SIZE, facecolor=STYLE_BG['color']), 
    plt.axes(projection=PROJ)
)
(fig, ax) = ox.plot_graph(
    G, ax, node_size=0, figsize=(40, 40), show=False,
    bgcolor=STYLE_BG['color'], edge_color=STYLE_RD['color'], 
    edge_alpha=STYLE_RD['alpha'], edge_linewidth=STYLE_RD['width']
)
lnd.plotTraps(
    fig, ax, 
    zorders=(30, 25), size=750, transparencyHex='99', proj=PROJ
)
for route in routes:
    (fig, ax) = ox.plot_graph_route(
        G, route, ax=ax, save=False, show=False, close=False,
        route_color='#b5e48c', route_linewidth=2.5, 
        node_size=0, bgcolor='#00000000', zorder=-10
    )
(fig, ax) = ox.plot_footprints(
    BLD, ax=ax, save=False, show=False, close=False,
    bgcolor=STYLE_BG['color'], color=STYLE_BD['color'], 
    alpha=STYLE_BD['alpha']
)
(fig, ax) = ox.plot_footprints(
    BLD, ax=ax, save=False, show=False, close=False,
    bgcolor=STYLE_BG['color'], alpha=0.25,
    color=list(BLD['cluster_color']), 
)
srv.plotClean(fig, ax, bbox=BBOX)
ax.set_facecolor(STYLE_BG['color'])
# fig.savefig(
#     path.join(paths['data'], CODE, fNameBase+'_CLN'), 
#     transparent=False, facecolor=STYLE_BG['color'],
#     bbox_inches='tight', pad_inches=PAD, dpi=DPI
# )
# plt.close('all')
