#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
from sys import argv
import osmnx as ox
from shapely import wkt
from random import shuffle, uniform
from engineering_notation import EngNumber
import cartopy.crs as ccrs
import compress_pickle as pkl
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import MoNeT_MGDrivE as monet
import MGSurvE as srv
import auxiliary as aux
ox.settings.log_console=False
ox.settings.use_cache=True
matplotlib.rc('font', family='Savoye LET')

if srv.isNotebook():
    (USR, COUNTRY, CODE, COMMUNE, COORDS) = (
        'sami', 'Burkina Faso', 'BFA', 
        'Nouna', (12.7326, -3.8603)
    )
else:
    (USR, COUNTRY, CODE, COMMUNE, COORDS) = argv[1:]
(PROJ, FOOTPRINT, OVW) = (
    ccrs.PlateCarree(), True, 
    {'dist': True, 'kernel': True}
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
###############################################################################
# Read from Disk
###############################################################################
(BLD, NTW) = (
    pkl.load(path.join(paths['data'], CODE, COMMUNE+'_BLD.bz')),
    pkl.load(path.join(paths['data'], CODE, COMMUNE+'_NTW.bz'))
)
###############################################################################
# Migration Matrix
###############################################################################
(lonLats, clusters) = (
    np.array(list(zip(BLD['centroid_lon'], BLD['centroid_lat']))),
    list(BLD['cluster_id'])
)
# Calculate or load distance --------------------------------------------------
if OVW['dist'] or (not path.isfile(pthDst)):
    migDst = srv.calcDistanceMatrix(lonLats, distFun=srv.haversineDistance)
else:
    migDst = pkl.load(pthDst)
# Calculate or load kernel ----------------------------------------------------
if OVW['kernel'] or (not path.isfile(pthMig)):
    migMat = srv.zeroInflatedExponentialKernel(migDst, srv.AEDES_EXP_PARAMS)
else:
    migMat = pkl.load(pthMig)
# Calculate aggregate landscape -----------------------------------------------
aggMat = monet.aggregateLandscape(migMat, clusters, type=2)
###############################################################################
# Aggregation Centroids
###############################################################################
(aggCentroids, clstSrt) = ([], list(BLD['cluster_id'].unique()))
for cix in clstSrt:
    matches = BLD['cluster_id']==cix
    ctr = list(np.mean(BLD[matches][['centroid_lon', 'centroid_lat']], axis=0))
    clr = BLD[matches].iloc[0]['cluster_color']
    aggCentroids.append([cix]+ctr+[clr])
aggDF = pd.DataFrame(aggCentroids, columns=['ix', 'lon', 'lat', 'color'])
###############################################################################
# Dump to Disk
###############################################################################
pkl.dump(migDst, pthDst, compression='bz2')
pkl.dump(migMat, pthMig, compression='bz2')
pkl.dump(aggMat, pthAgg, compression='bz2')
aggDF.to_csv(pthAct)
###############################################################################
# Map
###############################################################################
STYLE_GD = {'color': '#8da9c4', 'alpha': 0.35, 'width': 0.5, 'step': 0.01, 'range': 1, 'style': ':'}
STYLE_BG = {'color': '#0b2545'}
STYLE_TX = {'color': '#faf9f9', 'size': 40}
STYLE_CN = {'color': '#faf9f9', 'alpha': 0.20, 'size': 100}
STYLE_BD = {'color': '#faf9f9', 'alpha': 0.950}
STYLE_RD = {'color': '#ede0d4', 'alpha': 0.100, 'width': 1.5}
G = ox.project_graph(NTW, to_crs=ccrs.PlateCarree())
(fig, ax) = ox.plot_graph(
    G, node_size=0, figsize=(40, 40), show=False,
    bgcolor=STYLE_BG['color'], edge_color=STYLE_RD['color'], 
    edge_alpha=STYLE_RD['alpha'], edge_linewidth=STYLE_RD['width']
)
if FOOTPRINT:
    (fig, ax) = ox.plot_footprints(
        BLD, ax=ax, save=False, show=False, close=False,
        bgcolor=STYLE_BG['color'], 
        color=STYLE_BD['color'], 
        alpha=STYLE_BD['alpha']
    )
ax.scatter(
    aggDF['lon'], aggDF['lat'], 
    marker='x', s=STYLE_CN['size'],
    alpha=.75,
    color=aggDF['color']
)
(fig, ax) = ox.plot_footprints(
    BLD, ax=ax, save=False, show=False, close=False,
    bgcolor=STYLE_BG['color'], alpha=.45,
    color=list(BLD['cluster_color']), 
)
ax.text(
    0.99, 0.01, 
    'Footprints: {}'.format(EngNumber(BLD.shape[0])), 
    transform=ax.transAxes, 
    horizontalalignment='right', verticalalignment='bottom', 
    color=STYLE_TX['color'], fontsize=STYLE_TX['size']
)
ylims = ax.get_ylim()
ax.set_ylim(ylims[0], ylims[1]*1.0001)
ax.text(
    0.5, 0.975,
    '{}'.format(COMMUNE), 
    transform=ax.transAxes, 
    horizontalalignment='center', verticalalignment='top', 
    color=STYLE_TX['color'], fontsize=STYLE_TX['size']*5
)
ax.vlines(
    np.arange(COORDS[1]-STYLE_GD['range'], COORDS[1]+STYLE_GD['range'], STYLE_GD['step']), 
    COORDS[0]-1, COORDS[0]+1, 
    colors=STYLE_GD['color'], alpha=STYLE_GD['alpha'], linestyles=STYLE_GD['style']
)
ax.hlines(
    np.arange(COORDS[0]-STYLE_GD['range'], COORDS[0]+STYLE_GD['range'], STYLE_GD['step']), 
    COORDS[1]-1, COORDS[1]+1, 
    colors=STYLE_GD['color'], alpha=STYLE_GD['alpha'], linestyles=STYLE_GD['style']
)
ax.set_facecolor(STYLE_BG['color'])
fig.savefig(
    path.join(paths['data'], CODE, COMMUNE+'_AGG.png'), 
    facecolor=STYLE_BG['color'], bbox_inches='tight', pad_inches=1, dpi=300,
    transparent=False
)
plt.close('all')