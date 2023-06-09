#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
from sys import argv
import osmnx as ox
from random import shuffle
from engineering_notation import EngNumber
from collections import Counter
import cartopy.crs as ccrs
import compress_pickle as pkl
import matplotlib
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN, OPTICS
import numpy as np
import MGSurvE as srv
import auxiliary as aux
import constants as cst
ox.settings.log_console=False
ox.settings.use_cache=True
matplotlib.rc('font', family='Ubuntu Condensed')

if srv.isNotebook():
    (USR, COUNTRY, CODE, COMMUNE, COORDS, DIST, EPS, MIN) = (
        'zelda',
        'Burkina Faso', 'BFA', 
        'Banfora', (10.6376,-4.7526), 4000, 0.024, 5
    )
else:
    (USR, COUNTRY, CODE, COMMUNE, COORDS, DIST, EPS, MIN) = argv[1:]
    COORDS = tuple(map(float, COORDS.split(',')))
    DIST = int(DIST)
(PROJ, FOOTPRINT, CLUSTERS_ALG, CLUSTER_PAR, DROP_NOISE) = (
    ccrs.PlateCarree(), True, 
    DBSCAN, {'eps': float(EPS), 'min': int(MIN)}, True
)
###############################################################################
# Set Paths
###############################################################################
paths = aux.userPaths(USR)
###############################################################################
# Download Data
#   https://wiki.openstreetmap.org/wiki/Tag:place%3Dcity_block
#   tags={'building': True}
###############################################################################
BLD = ox.geometries.geometries_from_point(
    COORDS, tags={'building': True} , dist=DIST
)
NTW = ox.graph_from_point(
    COORDS, dist=DIST, network_type='all',
    retain_all=True, simplify=True, truncate_by_edge=True
)
BLD['centroid_lon'] = [poly.centroid.x for poly in BLD['geometry']]
BLD['centroid_lat'] = [poly.centroid.y for poly in BLD['geometry']]
BLD.reset_index(inplace=True)
###############################################################################
# Cluster Data
###############################################################################
if CLUSTERS_ALG:
    # lonLats = np.array(list(zip(BLD['centroid_lon'], BLD['centroid_lat'])))
    # clustering = CLUSTERS_ALG(n_clusters=CLUSTERS_NUM).fit(lonLats)
    latLons = np.array(list(zip(BLD['centroid_lat'], BLD['centroid_lon'])))
    clustering = DBSCAN(
        eps=CLUSTER_PAR['eps']/cst.KMS_PER_RADIAN, 
        min_samples=CLUSTER_PAR['min'], 
        algorithm='ball_tree', metric='haversine', n_jobs=4
    ).fit(np.radians(latLons))
    clustersNum = len(set(clustering.labels_))
    BLD['cluster_id'] = clustering.labels_
    Counter(clustering.labels_)
else:
    BLD['cluster_id'] = range(0, BLD.shape[0])
###############################################################################
# Map
###############################################################################
(STYLE_GD, STYLE_BG, STYLE_TX, STYLE_CN, STYLE_BD, STYLE_RD) = cst.MAP_STYLE_A
# Generate colors -------------------------------------------------------------
CLST_COL = cst.CLUSTER_PALETTE*clustersNum
shuffle(CLST_COL)
CLST_COLS_COL = [CLST_COL[ix] for ix in BLD['cluster_id']]
BLD['cluster_color'] = CLST_COLS_COL
BLD.loc[BLD['cluster_id']==-1, 'cluster_color'] = '#293241'
# Plot map --------------------------------------------------------------------
G = ox.project_graph(NTW, to_crs=ccrs.PlateCarree())
(fig, ax) = ox.plot_graph(
    G, node_size=0, figsize=(40, 40), show=False,
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
ax.text(
    0.99, 0.01, 
    'Footprints: {}\nNon-Noise: {}\nClusters: {}'.format(
        EngNumber(BLD.shape[0]), 
        EngNumber(int(BLD.shape[0]-np.sum(BLD['cluster_id']==-1))), 
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
    path.join(paths['data'], CODE, COMMUNE+'.png'), 
    facecolor=STYLE_BG['color'], bbox_inches='tight', pad_inches=1, dpi=300,
    transparent=False
)
plt.close('all')
###############################################################################
# Export to Disk
###############################################################################
BLD = BLD.drop(BLD[BLD['cluster_id']==-1].index)
pkl.dump(
    BLD, path.join(paths['data'], CODE, COMMUNE+'_BLD'), 
    compression='bz2'
)
pkl.dump(
    NTW, path.join(paths['data'], CODE, COMMUNE+'_NTW'), 
    compression='bz2'
)

