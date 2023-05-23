#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shutup; shutup.please()
from os import path
from sys import argv
import osmnx as ox
from shapely import wkt
from engineering_notation import EngNumber
import cartopy.crs as ccrs
import cartopy.feature as cf
import compress_pickle as pkl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import MGSurvE as srv
import auxiliary as aux
ox.config(log_console=False , use_cache=True)


if srv.isNotebook():
    (USR, COUNTRY, CODE, COMMUNE, COORDS, DIST) = (
        'sami',
        'Burkina Faso', 'BFA', 
        'Niangoloko', (10.2829, -4.9213), 5000
    )
else:
    (USR, COUNTRY, CODE, COMMUNE, COORDS, DIST) = argv[1:]
    COORDS = tuple(map(float, COORDS.split(', ')))
    DIST = int(DIST)
(PROJ, FOOTPRINT) = (ccrs.PlateCarree(), True)
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
###############################################################################
# Map
###############################################################################
STYLE_BG = {'color': '#0b2545'}
STYLE_TX = {'color': '#faf9f9', 'size': 20}
STYLE_CN = {'color': '#faf9f9', 'alpha': 0.20, 'size': 25}
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
        bgcolor=STYLE_BG['color'], color=STYLE_BD['color'], 
        alpha=STYLE_BD['alpha']
    )
else:
    ax.scatter(
        BLD['centroid_lon'], BLD['centroid_lat'], 
        marker='x', s=STYLE_CN['size'], 
        color=STYLE_BD['color'], alpha=STYLE_BD['alpha']
    )
ax.text(
    0.99, 0.01, 
    'Footprints: {}'.format(EngNumber(BLD.shape[0])), 
    transform=ax.transAxes, 
    horizontalalignment='right', verticalalignment='bottom', 
    color=STYLE_TX['color'], fontsize=STYLE_TX['size']
)
fig.savefig(
    path.join(paths['data'], 'HumanMobility', CODE, COMMUNE+'.png'), 
    facecolor='w', bbox_inches='tight', pad_inches=0.1, dpi=300,
    transparent=False
)
plt.close('all')
###############################################################################
# Export to Disk
###############################################################################
pkl.dump(
    BLD, path.join(paths['data'], 'HumanMobility', CODE, COMMUNE+'_BLD'), 
    compression='bz2'
)
pkl.dump(
    NTW, path.join(paths['data'], 'HumanMobility', CODE, COMMUNE+'_NTW'), 
    compression='bz2'
)