#!/usr/bin/env python
# -*- coding: utf-8 -*-

CORES = 32
###############################################################################
# Load libraries and limit cores
###############################################################################
import os
os.environ["OMP_NUM_THREADS"] = str(CORES)
os.environ["OPENBLAS_NUM_THREADS"] = str(CORES)
os.environ["MKL_NUM_THREADS"] = str(CORES)
os.environ["VECLIB_MAXIMUM_THREADS"] = str(CORES)
os.environ["NUMEXPR_NUM_THREADS"] = str(CORES)
from sys import argv
from os import path
from sys import argv
from copy import deepcopy
import compress_pickle as pkl
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import MGSurvE as srv
import constants as cst


###############################################################################
# Bash and user inputs
###############################################################################
if srv.isNotebook():
    (CLS_NUM, TRPS_NUM, REP_ID) = (120, 10, 0)
else:
    (CLS_NUM, TRPS_NUM, REP_ID) = (argv[1], int(argv[2]), int(argv[3]))
    CLS_NUM = int(CLS_NUM.split('-')[1])
(ID, PTH_IN, PTH_OUT) = (
    cst.EXP_ID,
    cst.PATHS['data'], cst.PATHS['optimization']
)
VERBOSE = False
(SZE, DPI) = (10, 300)
###############################################################################
# Load data
###############################################################################
fID = f'{ID}-{CLS_NUM:03d}'
(AGG, MAG, PTS, LND) = (
    pkl.load(path.join(PTH_IN, fID+'-AGG'), compression='bz2'),
    pkl.load(path.join(PTH_IN, fID+'-MAG'), compression='bz2'),
    pkl.load(path.join(PTH_IN, fID+'-CLS'), compression='bz2'),
    srv.loadLandscape(PTH_IN, fID+'-LND', fExt='pkl')
)
###############################################################################
# Registering GA functions
###############################################################################
lndGA = deepcopy(LND)
(lnd, logbook) = srv.optimizeDiscreteTrapsGA(
    lndGA, verbose=VERBOSE,
    generations=cst.GA['GEN'], 
    mating_params=cst.GA['MAT'], 
    mutation_params=cst.GA['MUT'], 
    selection_params=cst.GA['SEL'],
     pop_size=int(cst.GA['POP']*LND.trapsNumber),
    fitFuns={'inner': cst.GA['IMT'], 'outer': cst.GA['OMT']}
)
###############################################################################
# Export
###############################################################################
srv.dumpLandscape(lnd, PTH_OUT, f'{fID}-LOP_{REP_ID:02d}', fExt='pkl')
###############################################################################
# Plot
###############################################################################
(pal, proj) = (cst.CLUSTER_PALETTE, ccrs.PlateCarree())
colors = [pal[i%len(pal)] for i in PTS['cluster']]
lnd.updateTrapsRadii([1])
(fig, ax) = (plt.figure(figsize=(SZE, SZE)), plt.axes(projection=proj))
# lnd.plotSites(fig, ax, size=1, alpha=1, lw=0)
ax.scatter(
    PTS['lon'], PTS['lat'], 
    ec='#ffffff88', lw=1.5,
    color=colors, zorder=10, alpha=0.5, s=75,
    transform=proj
)
lnd.plotTraps(fig, ax, proj=proj)
lnd.plotMigrationNetwork(
    fig, ax, 
    lineWidth=100, alphaMin=.4, alphaAmplitude=50,
)
lnd.plotLandBoundary(fig, ax)
srv.plotClean(fig, ax, bbox=lnd.landLimits)
fig.savefig(
    path.join(PTH_OUT, f'{fID}-MOP_{REP_ID:02d}'), 
    bbox_inches='tight', pad_inches=0, dpi=DPI, transparent=False
)
plt.close('all')