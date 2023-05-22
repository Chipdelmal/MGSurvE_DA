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


(COUNTRY, COMMUNE) = ('Burkina Faso', 'Gorom Gorom')
if srv.isNotebook():
    USR = 'sami'
else:
    USR = argv[1:]
###############################################################################
# Read files
###############################################################################
paths = aux.userPaths(USR)
DATA = pd.read_excel(
    path.join(paths['data'], 'HumanMobility', 'HumanMobility.xlsx'),
    sheet_name=[f"{c} Coordinates" for c in ('Mali', 'Burkina Faso', 'Zambia', 'Tanzania')]
)
CNT = DATA[f'{COUNTRY} Coordinates']
print(list(CNT.columns))
###############################################################################
# Inspect (Cercle ~ State)
###############################################################################
coms = sorted(list(set(CNT['COMMUNE'])))
CNT.sort_values(by='POPULATION', ascending=False).iloc[10]