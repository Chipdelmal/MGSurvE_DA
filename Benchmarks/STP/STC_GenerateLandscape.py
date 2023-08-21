#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import argv
import numpy as np
import pandas as pd
from os import path
from sys import argv
from copy import deepcopy
import compress_pickle as pkl
import matplotlib.pyplot as plt
from numpy.random import uniform
import MGSurvE as srv
import constants as cst


###############################################################################
# Bash and user inputs
###############################################################################
if srv.isNotebook():
    (CLS_NUM, TRPS_NUM) = (236, 10)
else:
    (TRPS_NUM) = (int(argv[1]), int(argv[2]))
(ID, PTH_IN, PTH_OUT) = (
    cst.EXP_ID,
    cst.PATHS['data'], cst.PATHS['data']
)
(SZE, DPI) = (10, 300)
###############################################################################
# Load data
###############################################################################
fID = f'{ID}-{CLS_NUM:03d}'
MIG = pkl.load(path.join(PTH_IN, fID+'-AGG'), compression='bz2')
PTS = pkl.load(path.join(PTH_IN, fID+'-CLS'), compression='bz2')
###############################################################################
# Setup traps
###############################################################################
NULL_TRP = [0]*TRPS_NUM
(NULL_LON, NULL_LAT) = ([
    uniform(*cst.SAO_LIMITS[0], TRPS_NUM), 
    uniform(*cst.SAO_LIMITS[1], TRPS_NUM)
])
TRAPS = pd.DataFrame({
    'sid': NULL_TRP, 'lon': NULL_LON, 'lat': NULL_LAT, 
    't': NULL_TRP, 'f': NULL_TRP
})
###############################################################################
# Setting Landscape Up
###############################################################################
# lnd = srv.Landscape(
#     SAO_TOME_LL, migrationMatrix=SAO_TOME_MIG,
#     traps=traps, trapsKernels=tKer, landLimits=SAO_LIMITS,
#     trapsRadii=[1],
# )
# bbox = lnd.getBoundingBox()
# trpMsk = srv.genFixedTrapsMask(lnd.trapsFixed)