#!/usr/bin/env python
# -*- coding: utf-8 -*-

CORES = 8
###############################################################################
# Load libraries and limit cores
###############################################################################
import os
os.environ["OMP_NUM_THREADS"] = str(CORES)
os.environ["OPENBLAS_NUM_THREADS"] = str(CORES)
os.environ["MKL_NUM_THREADS"] = str(CORES)
os.environ["VECLIB_MAXIMUM_THREADS"] = str(CORES)
os.environ["NUMEXPR_NUM_THREADS"] = str(CORES)
# Load libraries --------------------------------------------------------------
from sys import argv
import numpy as np
import pandas as pd
from os import path
from sys import argv
from copy import deepcopy
import matplotlib.pyplot as plt
from numpy.random import uniform
from sklearn.preprocessing import normalize
import MGSurvE as srv
import cartopy.crs as ccrs


###############################################################################
# Bash and user inputs
###############################################################################
if srv.isNotebook():
    # User input (interactive session)
    (FXD_TRPS, AP, TRPS_NUM, RID) = (True, 'man', 5, '07')
else:
    # Bash call input
    (FXD_TRPS, AP, TRPS_NUM, RID) = (True, 'man', int(argv[1]), int(argv[2]))
ID = 'STC'
OUT_PTH = './sims_out/'
###############################################################################
# Not accessible masses
###############################################################################
IX_SPLIT = 27
NOT_ACCESSIBLE = [51, 239]
NOT_ACCESSIBLE_IX = tuple([i-IX_SPLIT for i in NOT_ACCESSIBLE])
###############################################################################
# Output Folder
###############################################################################
RID = int(RID)
srv.makeFolder(OUT_PTH)
###############################################################################
# Debugging fixed traps at land masses
###############################################################################
ID = 'STP' if FXD_TRPS else 'STPN'
###############################################################################
# Load Pointset
###############################################################################
sites = pd.read_csv(path.join('./GEO', 'STP_LatLonN.csv'))
sites['t'] = [0]*sites.shape[0]
SAO_TOME_LL = sites.iloc[IX_SPLIT:]
SAO_bbox = (
    (min(SAO_TOME_LL['lon']), max(SAO_TOME_LL['lon'])),
    (min(SAO_TOME_LL['lat']), max(SAO_TOME_LL['lat']))
)
SAO_cntr = [i[0]+(i[1]-i[0])/2 for i in SAO_bbox]
SAO_LIMITS = ((6.41, 6.79), (-0.0475, .45))
###############################################################################
# Load Migration Matrix
###############################################################################
migration = np.genfromtxt(
    path.join('./GEO', 'STP_MigrationN.csv'), 
    delimiter=','
)
msplit = migration[IX_SPLIT:,IX_SPLIT:]
###############################################################################
# Delete non-accessible
###############################################################################
SAO_TOME_LL.drop(index=NOT_ACCESSIBLE, axis=0, inplace=True)
msplit = np.delete(msplit, NOT_ACCESSIBLE_IX, axis=0)
msplit = np.delete(msplit, NOT_ACCESSIBLE_IX, axis=1)
SAO_TOME_MIG = normalize(msplit, axis=1, norm='l1')
