#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import argv
from glob import glob
import pandas as pd
from os import path
from sys import argv
from copy import deepcopy
import compress_pickle as pkl
import matplotlib.pyplot as plt
from numpy.random import uniform
import cartopy.crs as ccrs
import MGSurvE as srv
import constants as cst


###############################################################################
# Bash and user inputs
###############################################################################
if srv.isNotebook():
    (CLS_NUM, TRPS_NUM) = (120, 10)
else:
    (CLS_NUM, TRPS_NUM) = (int(argv[1]), int(argv[2]))
    # fNames = glob(path.join(cst.PATHS['data'], '*-*-CLS.bz'))
    # CLS_NUM = sorted(list(set(
    #     [int(i.split('/')[-1].split('-')[1]) for i in fNames]
    # )))
(ID, PTH_IN, PTH_OUT) = (
    cst.EXP_ID,
    cst.PATHS['data'], cst.PATHS['data']
)
(SZE, DPI) = (10, 300)
###############################################################################
# Load data
###############################################################################
fID = f'{ID}-{CLS_NUM:03d}'
(AGG, MAG, PTS) = (
    pkl.load(path.join(PTH_IN, fID+'-AGG'), compression='bz2'),
    pkl.load(path.join(PTH_IN, fID+'-MAG'), compression='bz2'),
    pkl.load(path.join(PTH_IN, fID+'-CLS'), compression='bz2')
)
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
lnd = srv.Landscape(
    AGG, migrationMatrix=MAG,
    traps=TRAPS, trapsKernels=cst.TRAP_KERNEL, 
    landLimits=cst.SAO_LIMITS, trapsRadii=[1],
)
bbox = lnd.getBoundingBox()
###############################################################################
# Plot
###############################################################################
pal = cst.CLUSTER_PALETTE
colors = [pal[i%len(pal)] for i in PTS['cluster']]
(fig, ax) = (
    plt.figure(figsize=(SZE, SZE)),
    plt.axes(projection=ccrs.PlateCarree())
)
# lnd.plotSites(fig, ax, size=1, alpha=1, lw=0)
ax.scatter(
    PTS['lon'], PTS['lat'], 
    ec='#ffffff88', lw=1.5,
    color=colors, zorder=10, alpha=0.75, s=50,
    transform=ccrs.PlateCarree()
)
# lnd.plotTraps(fig, ax)
lnd.plotMigrationNetwork(
    fig, ax, 
    lineWidth=100, alphaMin=.35, alphaAmplitude=50,
)
lnd.plotLandBoundary(fig, ax)
srv.plotClean(fig, ax, bbox=lnd.landLimits)
fig.savefig(
    path.join(PTH_OUT, fID+'-MAG'), 
    bbox_inches='tight', pad_inches=0, dpi=DPI, transparent=False
)
plt.close('all')
