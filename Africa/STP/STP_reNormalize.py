#!/usr/bin/env python
# -*- coding: utf-8 -*-

from glob import glob
import numpy as np
import pandas as pd
from os import path
from sys import argv
from glob import glob
from sklearn.preprocessing import normalize
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
(ORIGINAL_AMP, NEW_AMP) = (0.5, 0.05)
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
    OUT_PTH, lndFile.split('/')[-1].split('.')[0], fExt='pkl'
)
###############################################################################
# Rescale Migration
###############################################################################
SCALING = (1/ORIGINAL_AMP*NEW_AMP)
migMat = np.copy(lnd.trapsMigration)
(sitesNum, trapsNum) = (
    migMat.shape[0]-lnd.trapsNumber, lnd.trapsNumber
)
nu = np.copy(migMat[:sitesNum,-trapsNum:-1])
migMat[:sitesNum,-trapsNum:-1] = nu*SCALING
migMat = normalize(migMat, axis=1, norm='l2')
###############################################################################
# Plot Matrices
###############################################################################
(fig, ax) = plt.subplots(1, 2, figsize=(10, 10), sharey=True)
srv.plotMatrix(fig, ax[0], lnd.trapsMigration, trapsNum)
srv.plotMatrix(fig, ax[1], migMat, trapsNum)
###############################################################################
# Export to Disk
###############################################################################