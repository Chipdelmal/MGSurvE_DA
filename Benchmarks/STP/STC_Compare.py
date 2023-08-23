#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Load libraries and limit cores
###############################################################################
from sys import argv
from os import path
from sys import argv
from glob import glob
import compress_pickle as pkl
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import pandas as pd
import MGSurvE as srv
import MoNeT_MGDrivE as monet
import constants as cst


###############################################################################
# Bash and user inputs
###############################################################################
if srv.isNotebook():
    (CLS_NUM, TRPS_NUM, REP_ID) = (120, 8, 0)
else:
    (CLS_NUM, TRPS_NUM, REP_ID) = (argv[1], int(argv[2]), int(argv[3]))
    CLS_NUM = int(CLS_NUM.split('-')[1])
(ID, PTH_IN, PTH_OUT) = (
    cst.EXP_ID,
    cst.PATHS['optimization'], cst.PATHS['optimization']
)
VERBOSE = False
(SZE, DPI) = (10, 300)
###############################################################################
# Load data
###############################################################################
FPATS = ('*.pkl', '*LOG*.csv')
(FNAMES_LND, FNAMES_LOG) = [sorted(glob(path.join(PTH_IN, i))) for i in FPATS]
SIDS = sorted(list(set(
    [fname.split('/')[-1].split('-')[1] for fname in FNAMES_LOG]
)))
# Generate data dicts ---------------------------------------------------------
sid = SIDS[0]
(logDict, lndDict) = ({}, {})
for sid in SIDS:
    (logFnames,  lndFnames) = [
        sorted(glob(path.join(PTH_IN, (f'*{sid}*{tag}*'))))
        for tag in ('LOG', 'LOP')
    ]
    (logDict[sid], lndDict[sid]) = (
        [pd.read_csv(i) for i in logFnames],
        [pkl.load(i) for i in lndFnames]
    )
minsDict = {sid: np.array([(i['min']) for i in logDict[sid]]) for sid in SIDS}
###############################################################################
# Plot
###############################################################################
(XRAN, YRAN) = (
    (0, 500), # cst.GA['GEN']/2), 
    (0, 1200)
)
# CLRS = cst.CLUSTER_PALETTE
CMAP = monet.colorPaletteFromHexList(['#3a0ca3', '#f72585'])
(fig, ax) = plt.subplots(figsize=(20, 4))
for (ix, k) in enumerate(minsDict.keys()):
    ax.plot(
        minsDict[k].T, 
        # color=CLRS[(ix)%len(CLRS)], 
        color=CMAP(np.interp(ix, (0, len(SIDS)), (0, 1))),
        alpha=0.25, lw=1.25
    )
ax.set_xlim(0, XRAN[1])
ax.set_ylim(YRAN[0], YRAN[1])