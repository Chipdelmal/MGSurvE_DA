#!/usr/bin/env python
# -*- coding: utf-8 -*-

from glob import glob
import numpy as np
import pandas as pd
from os import path
from sys import argv
from glob import glob
import cartopy.crs as ccrs
import shapely.geometry as sgeom
from cartopy.geodesic import Geodesic
import matplotlib.pyplot as plt
import MGSurvE as srv
import auxiliary as aux
from copy import deepcopy
plt.rcParams['axes.facecolor']='#00000000'
plt.rcParams['savefig.facecolor']='#00000000'


###############################################################################
# Bash and user inputs
###############################################################################
if srv.isNotebook():
    # User input (interactive session)
    (ID, AP, TRP) = ('STPD', 'max', 25)
else:
    # Bash call input
    (ID, AP) = argv[1:]
GENS = 5000
FPAT = ID+'-'+AP+'_{}*'
###############################################################################
# Working Folder
###############################################################################
OUT_PTH = '/RAID5/marshallShare/MGSurvE_v3/'
srv.makeFolder(OUT_PTH)
###############################################################################
# Load Landscape
###############################################################################
lndFiles = sorted(glob(path.join(OUT_PTH, (FPAT+'TRP.pkl').format(TRP))))
lndFile = lndFiles[0]
lnd = srv.loadLandscape(
    OUT_PTH, 
    lndFile.split('/')[-1].split('.')[0], 
    fExt='pkl'
)

(fig, ax) = plt.subplots(1, 1, figsize=(10, 10), sharey=False)
srv.plotMatrix(fig, ax, lnd.trapsMigration, lnd.trapsNumber)


plt.matshow(lnd.trapsMigration[:,-lnd.trapsNumber:-1])