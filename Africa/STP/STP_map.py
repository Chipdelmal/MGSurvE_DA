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
# Bash and User Inputs
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
    OUT_PTH, lndFile.split('/')[-1].split('.')[0], fExt='pkl'
)
###############################################################################
# Plot Landscape
###############################################################################
(fig, ax) = (
    plt.figure(figsize=(15, 15)), plt.axes(projection=ccrs.PlateCarree())
)
lnd.plotSites(fig, ax, size=350, colors=('#8093f133', ))
lnd.plotLandBoundary(
    fig, ax,  
    landTuples=(('10m', '#dfe7fd99', 30), ('10m', '#ffffffDD', 5))
)
sites = lnd.pointCoords
for (i, site) in enumerate(sites):
    if (site[0]>6.45) and (site[1]<0.17) and (site[1]>0):
        ax.scatter(
            site[0], site[1], zorder=5, color='#3d348bCC',
            s=350, edgecolors='w', linewidths=1.25
        )
sites = lnd.trapsCoords
for (i, site) in enumerate(sites):
    if (site[0]>6.45) and (site[1]<0.17) and (site[1]>0):
        ax.scatter(
            site[0], site[1], zorder=5, color='#f72585CC',
            s=350, edgecolors='w', linewidths=1.25,
            marker='o'
        )
# lnd.plotTraps(
#     fig, ax, size=325,
#     zorders=(30, 25), transparencyHex='BB', 
#     proj=ccrs.PlateCarree()
# )
srv.plotClean(fig, ax, bbox=((6.45, 6.77), (-0.02, 0.42)))
fig.savefig(
    path.join(OUT_PTH, (FPAT[:-1]+'.png').format(TRP)), 
    facecolor='w', bbox_inches='tight', pad_inches=0.1, dpi=350,
    transparent=False
)
plt.close('all')