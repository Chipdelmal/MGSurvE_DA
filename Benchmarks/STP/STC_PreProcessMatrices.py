#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import argv
import numpy as np
import pandas as pd
from os import path
import compress_pickle as pkl
import matplotlib.pyplot as plt
from sklearn.preprocessing import normalize
import MGSurvE as srv
import constants as cst
pd.options.mode.chained_assignment = None 

###############################################################################
# Bash and user inputs
###############################################################################
if srv.isNotebook():
    pass
else:
    pass
(ID, OUT_PTH) = (cst.EXP_ID, cst.PATHS['data'])
###############################################################################
# Not accessible masses
###############################################################################
(IX_SPLIT, NOT_ACCESSIBLE) = (cst.IX_SPLIT, cst.NOT_ACCESSIBLE)
NOT_ACCESSIBLE_IX = tuple([i-IX_SPLIT for i in NOT_ACCESSIBLE])
###############################################################################
# Output Folder
###############################################################################
srv.makeFolder(OUT_PTH)
###############################################################################
# Load Pointset
###############################################################################
sites = pd.read_csv(path.join(cst.PATHS['geo'], 'STP_LatLonN.csv'))
sites['t'] = [0]*sites.shape[0]
SAO_TOME_LL = sites.iloc[IX_SPLIT:]
###############################################################################
# Load Migration Matrix
###############################################################################
migration = np.genfromtxt(
    path.join(cst.PATHS['geo'], 'STP_MigrationN.csv'), 
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
###############################################################################
# Calculate distance matrix
###############################################################################
migDst = srv.calcDistanceMatrix(
    np.asarray(SAO_TOME_LL[['lon', 'lat']]), 
    distFun=srv.haversineDistance
)
###############################################################################
# Dump files to disk
###############################################################################
pkl.dump(migDst, path.join(OUT_PTH, f'{ID}-DST'), compression='bz2')
pkl.dump(SAO_TOME_MIG, path.join(OUT_PTH, f'{ID}-MIG'), compression='bz2')
pkl.dump(SAO_TOME_LL, path.join(OUT_PTH, f'{ID}-PTS'), compression='bz2')