#!/usr/bin/env python
# -*- coding: utf-8 -*-

import warnings
from os import path
from sys import argv
import osmnx as ox
from shapely import wkt
import cartopy.crs as ccrs
import cartopy.feature as cf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import MGSurvE as srv
import auxiliary as aux
ox.config(log_console=False , use_cache=True)
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')
warnings.filterwarnings("ignore", category=RuntimeWarning) 
warnings.filterwarnings("ignore", category=UserWarning) 


if srv.isNotebook():
    (USR, COUNTRY, CODE, COMMUNE, COORDS, DIST) = (
        'sami',
        'Burkina Faso', 'BFA', 
        'Ouagadougou', (12.3732634, -1.5437957), 15000
    )
else:
    USR = argv[1:]
(PROJ, FOOTPRINT) = (ccrs.PlateCarree(), True)
###############################################################################
# Set Paths
###############################################################################
paths = aux.userPaths(USR)
###############################################################################
# Download Data
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
STYLE_CN = {'color': '#faf9f9', 'alpha': 0.20, 'size': 35}
STYLE_BD = {'color': '#faf9f9', 'alpha': 0.80}
STYLE_RD = {'color': '#ede0d4', 'alpha': 0.10, 'width': 1.25}
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
fig.savefig(
    path.join(paths['data'], 'HumanMobility', CODE, COMMUNE+'.png'), 
    facecolor='w', bbox_inches='tight', pad_inches=0.1, dpi=300,
    transparent=False
)
plt.close('all')