#!/usr/bin/env python
# -*- coding: utf-8 -*-

import warnings
from os import path
from sys import argv
import osmnx as ox

import pandas as pd
import MGSurvE as srv
import auxiliary as aux
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')


(COUNTRY, CODE, COMMUNE) = ('Burkina Faso', 'BFA', 'Gorom Gorom')
if srv.isNotebook():
    USR = 'sami'
else:
    USR = argv[1:]
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
    ox.graph_from_xml(osm, retain_all=True)
)
print(list(CNT.columns))
###############################################################################
# Inspect (Cercle ~ State)
###############################################################################
coms = sorted(list(set(CNT['COMMUNE'])))
CNT.sort_values(by='POPULATION', ascending=False).iloc[10]