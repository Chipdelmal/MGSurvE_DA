#!/usr/bin/env python
# -*- coding: utf-8 -*-

import warnings
from os import path
from sys import argv
import osmnx as ox
import cartopy.crs as ccrs
import cartopy.feature as cf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import MGSurvE as srv
import auxiliary as aux
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')


(COUNTRY, CODE, COMMUNE) = ('Burkina Faso', 'BFA', 'Gorom Gorom')
if srv.isNotebook():
    USR = 'sami'
else:
    USR = argv[1:]
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
    ox.geometries_from_xml(osm, tags={'building': True}),
    ox.graph_from_xml(osm, retain_all=False)
)
print(list(CNT.columns))
###############################################################################
# Inspect (Cercle ~ State)
###############################################################################
coms = sorted(list(set(CNT['COMMUNE'])))
CNT.sort_values(by='POPULATION', ascending=False).iloc[10]
###############################################################################
# Map
###############################################################################
STYLE_BG = {'color': '#ffffff'}
STYLE_BD = {'color': '#ff006e', 'alpha': 0.85}
STYLE_RD = {'color': '#4361ee', 'alpha': 0.20, 'width': 3.5}
(fig, ax) = ox.plot_graph(
    NTW, node_size=0, figsize=(40, 40), show=False,
    bgcolor=STYLE_BG['color'], edge_color=STYLE_RD['color'], 
    edge_alpha=STYLE_RD['alpha'], edge_linewidth=STYLE_RD['width']
)
(fig, ax) = ox.plot_footprints(
    BLD, ax=ax, save=False, show=False, close=False,
    bgcolor=STYLE_BG['color'], color=STYLE_BD['color'], alpha=STYLE_BD['alpha']
)
