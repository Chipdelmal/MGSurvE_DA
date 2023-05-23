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


if srv.isNotebook():
    (USR, COUNTRY, CODE, COMMUNE) = (
        'sami', 
        'Burkina Faso', 'BFA', 
        'Fanka'
    )
else:
    (USR, COUNTRY, CODE, COMMUNE) = argv[1:]
PROJ = ccrs.PlateCarree()
###############################################################################
# Read files
###############################################################################
paths = aux.userPaths(USR)
osm = path.join(paths['data'], 'HumanMobility', CODE, COMMUNE+'.osm')
DATA = pd.read_excel(
    path.join(paths['data'], 'HumanMobility', 'HumanMobility.xlsx'),
    sheet_name=[f"{c} Coordinates" for c in ('Mali', 'Burkina Faso', 'Zambia', 'Tanzania')]
)
CNT = DATA[f'{COUNTRY} Coordinates']
(BLD, NTW) = (
    ox.geometries_from_xml(osm, tags={'building': True}).reset_index(),
    ox.graph_from_xml(osm, retain_all=False)
)
BLD['centroid_x'] = [poly.centroid.x for poly in BLD['geometry']]
BLD['centroid_y'] = [poly.centroid.y for poly in BLD['geometry']]
# print(list(CNT.columns))
###############################################################################
# Inspect (Cercle ~ State)
###############################################################################
coms = sorted(list(set(CNT['COMMUNE'])))
CNT.sort_values(by='POPULATION', ascending=False)
###############################################################################
# Map
###############################################################################
STYLE_BG = {'color': '#ffffff'}
STYLE_CN = {'color': '#1d3557', 'alpha': 0.20, 'size': 35}
STYLE_BD = {'color': '#ff006e', 'alpha': 0.80}
STYLE_RD = {'color': '#4361ee', 'alpha': 0.15, 'width': 3.5}
G = ox.project_graph(NTW, to_crs=ccrs.PlateCarree())
(fig, ax) = ox.plot_graph(
    G, node_size=0, figsize=(40, 40), show=False,
    bgcolor=STYLE_BG['color'], edge_color=STYLE_RD['color'], 
    edge_alpha=STYLE_RD['alpha'], edge_linewidth=STYLE_RD['width']
)
(fig, ax) = ox.plot_footprints(
    BLD, ax=ax, save=False, show=False, close=False,
    bgcolor=STYLE_BG['color'], color=STYLE_BD['color'], alpha=STYLE_BD['alpha']
)
ax.scatter(
    BLD['centroid_x'], BLD['centroid_y'], marker='x',
    s=STYLE_CN['size'], color=STYLE_CN['color'], alpha=STYLE_CN['alpha']
)
fig.savefig(
    path.join(paths['data'], 'HumanMobility', CODE, COMMUNE+'.png'), 
    facecolor='w', bbox_inches='tight', pad_inches=0.1, dpi=350,
    transparent=False
)