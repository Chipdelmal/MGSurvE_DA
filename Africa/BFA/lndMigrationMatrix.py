# !/usr/bin/env python
# -*- coding: utf-8 -*-

import math
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
import constants as cst
ox.settings.log_console=False
ox.settings.use_cache=True
matplotlib.rc('font', family='Ubuntu Condensed')

if srv.isNotebook():
    (USR, COUNTRY, CODE, COMMUNE, COORDS) = (
        'zelda', 'Burkina Faso', 'BFA', 
        'Fanka', (13.1490, -1.0171)
    )
else:
    (USR, COUNTRY, CODE, COMMUNE, COORDS) = argv[1:]
    COORDS = tuple(map(float, COORDS.split(',')))
(PROJ, FOOTPRINT, OVW) = (
    ccrs.PlateCarree(), True, 
    {'dist': True, 'kernel': True}
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
    # migMat = srv.zeroInflatedExponentialKernel(migDst, srv.AEDES_EXP_PARAMS)
    # Inverse of mean daily dispersal distance (in meters)
    migMat = aux.exponentialKernel(migDst, 1/MEAN_DISPERSAL)
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
clustersNum = aggDF.shape[0]
###############################################################################
# Plot Matrices
###############################################################################
(SZE, DPI) = (10, 300)
(fig, ax) = plt.subplots(figsize=(SZE, SZE))
ax.matshow(
    migDst, cmap=aux.colorPaletteFromHexList(['#ffffff', '#ff0054'])
)
ax.axis('off')
fig.savefig(
    path.join(paths['data'], CODE, COMMUNE+'_DST.png'), 
    dpi=DPI, transparent=False, bbox_inches='tight', pad_inches=0
)
plt.close('all')
(fig, ax) = plt.subplots(figsize=(SZE, SZE))
ax.matshow(
    migMat, cmap=aux.colorPaletteFromHexList(['#ffffff', '#3a0ca3']), 
    vmin=0, vmax=0.05
)
ax.axis('off')
fig.savefig(
    path.join(paths['data'], CODE, COMMUNE+'_MIG.png'), 
    dpi=DPI, transparent=False, bbox_inches='tight', pad_inches=0
)
plt.close('all')
(fig, ax) = plt.subplots(figsize=(SZE, SZE))
ax.matshow(
    aggMat, cmap=aux.colorPaletteFromHexList(['#ffffff', '#7776bc']), 
    vmin=0, vmax=0.05
)
ax.axis('off')
fig.savefig(
    path.join(paths['data'], CODE, COMMUNE+'_MAG.png'), 
    dpi=DPI, transparent=False, bbox_inches='tight', pad_inches=0
)
plt.close('all')
###############################################################################
# Dump to Disk
###############################################################################
pkl.dump(migDst, pthDst, compression='bz2')
pkl.dump(migMat, pthMig, compression='bz2')
pkl.dump(aggMat, pthAgg, compression='bz2')
aggDF.to_csv(pthAct, index=False)
###############################################################################
# Map
###############################################################################
(STYLE_GD, STYLE_BG, STYLE_TX, STYLE_CN, STYLE_BD, STYLE_RD) = cst.MAP_STYLE_A
G = ox.project_graph(NTW, to_crs=ccrs.PlateCarree())
(fig, ax) = ox.plot_graph(
    G, node_size=0, figsize=(40, 40), show=False,
    bgcolor=STYLE_BG['color'], edge_color=STYLE_RD['color'], 
    edge_alpha=STYLE_RD['alpha'], edge_linewidth=STYLE_RD['width']
)
ax.scatter(
    aggDF['lon'], aggDF['lat'], 
    marker='x', s=STYLE_CN['size'],
    alpha=.75, zorder=10,
    # facecolors='none',
    color=aggDF['color']
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
ax.text(
    0.99, 0.01, 
    'Footprints: {}\nClusters: {}'.format(
        EngNumber(BLD.shape[0]), 
        clustersNum
    ), 
    transform=ax.transAxes, 
    horizontalalignment='right', verticalalignment='bottom', 
    color=STYLE_TX['color'], fontsize=STYLE_TX['size'],
    alpha=0.75
)
ylims = ax.get_ylim()
ax.set_ylim(ylims[0], ylims[1]*1.0001)
ax.text(
    0.5, 0.975,
    '{}'.format(COMMUNE), 
    transform=ax.transAxes, 
    horizontalalignment='center', verticalalignment='top', 
    color=STYLE_TX['color'], fontsize=STYLE_TX['size']*5,
    alpha=0.75
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


# import matplotlib.font_manager
# from IPython.core.display import HTML
# def make_html(fontname):
#     return "<p>{font}: <span style='font-family:{font}; font-size: 24px;'>{font}</p>".format(font=fontname)
# code = "\n".join([make_html(font) for font in sorted(set([f.name for f in matplotlib.font_manager.fontManager.ttflist]))])
# HTML("<div style='column-count: 2;'>{}</div>".format(code))
