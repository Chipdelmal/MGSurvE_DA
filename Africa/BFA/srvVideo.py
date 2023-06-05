# !/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
# Load libraries and limit cores
###############################################################################
import os
import math
import subprocess
import osmnx as ox
from os import path
from sys import argv
from copy import deepcopy
from engineering_notation import EngNumber
import cartopy.crs as ccrs
import compress_pickle as pkl
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from numpy.random import uniform
import MGSurvE as srv
import auxiliary as aux
import constants as cst
from PIL import Image
# matplotlib.use('agg')
matplotlib.rc('font', family='Ubuntu Condensed')

if srv.isNotebook():
    (USR, COUNTRY, CODE, COMMUNE, COORDS, GENS, FRACTION, REP) = (
        'zelda', 'Burkina Faso', 'BFA', 
        'Basberike', (13.14717,-1.03444), 1000, 50, 0
    )
else:
    (USR, COUNTRY, CODE, COMMUNE, COORDS, GENS, FRACTION, REP) = argv[1:]
    (COORDS, GENS, FRACTION, REP) = (
        tuple(map(float, COORDS.split(','))),
        int(GENS), int(FRACTION), int(REP)
    )
(PROJ, FOOTPRINT, OVW, VERBOSE) = (
    ccrs.PlateCarree(), True, 
    {'dist': False, 'kernel': False},
    False
)
###############################################################################
# Set Paths
###############################################################################
paths = aux.userPaths(USR)
(pthDst, pthMig, pthAgg, pthAct) = (
    path.join(paths['data'], CODE, COMMUNE+'_DST.bz'),
    path.join(paths['data'], CODE, COMMUNE+'_MIG.bz'),
    path.join(paths['data'], CODE, COMMUNE+'_AGG.bz'),
    path.join(paths['data'], CODE, COMMUNE+'_ACT.csv')
)
(OUT_LOG, OUT_LND, OUT_VID) = (
    path.join(paths['data'], CODE, COMMUNE+'_LOG.csv'),
    path.join(paths['data'], CODE, COMMUNE+'_LND.bz'),
    path.join(paths['data'], CODE, COMMUNE+'_LND.bz')
)
###############################################################################
# Read from Disk
###############################################################################
(BLD, NTW) = (
    pkl.load(path.join(paths['data'], CODE, COMMUNE+'_BLD.bz')),
    pkl.load(path.join(paths['data'], CODE, COMMUNE+'_NTW.bz'))
)
(MIG, MAG, LAG) = (
    pkl.load(path.join(paths['data'], CODE, COMMUNE+'_MIG.bz')),
    pkl.load(path.join(paths['data'], CODE, COMMUNE+'_AGG.bz')),
    pd.read_csv(pthAct)
)
# Get filename and create out folder ------------------------------------------
SITES_NUM = LAG.shape[0]
TRPS_NUM = math.floor(SITES_NUM/FRACTION)
fNameBase = '{}-{:04d}_{:04d}-{:02d}'.format(COMMUNE, SITES_NUM, TRPS_NUM, REP)
(log, lnd) = (
    pd.read_csv(path.join(paths['data'], CODE, fNameBase+'_LOG.csv')),
    srv.loadLandscape(path.join(paths['data'], CODE), fNameBase+'_LND', fExt='pkl')
)
OUT_VID = path.join(path.join(paths['data'], CODE, fNameBase))
srv.makeFolder(OUT_VID)
###############################################################################
# Plot blank landscape
###############################################################################
(STYLE_GD, STYLE_BG, STYLE_TX, STYLE_CN, STYLE_BD, STYLE_RD) = cst.MAP_STYLE_A
(PAD, DPI) = (0, 300)
lnd.updateTrapsRadii([1])
bbox = lnd.getBoundingBox()
trpMsk = srv.genFixedTrapsMask(lnd.trapsFixed)
# Landscape -------------------------------------------------------------------
(FIG_SIZE, PROJ, BSCA) = ((15, 15), ccrs.PlateCarree(), 0.001)
BBOX = (
    (lnd.landLimits[0][0]-BSCA, lnd.landLimits[0][1]+BSCA),
    (lnd.landLimits[1][0]-BSCA, lnd.landLimits[1][1]+BSCA)
)
(fig, ax) = (
    plt.figure(figsize=FIG_SIZE, facecolor=STYLE_BG['color']), 
    plt.axes(projection=PROJ)
)
G = ox.project_graph(NTW, to_crs=PROJ)
(fig, ax) = ox.plot_graph(
    G, ax, node_size=0, figsize=(40, 40), show=False,
    bgcolor=STYLE_BG['color'], edge_color=STYLE_RD['color'], 
    edge_alpha=STYLE_RD['alpha'], edge_linewidth=STYLE_RD['width']
)
(fig, ax) = ox.plot_footprints(
    BLD, ax=ax, save=False, show=False, close=False,
    bgcolor=STYLE_BG['color'], color=STYLE_BD['color'], 
    alpha=STYLE_BD['alpha']
)
(fig, ax) = ox.plot_footprints(
    BLD, ax=ax, save=False, show=False, close=False,
    bgcolor=STYLE_BG['color'], alpha=0.65,
    color=list(BLD['cluster_color']), 
)
# lnd.plotMigrationNetwork(
#     fig, ax, 
#     lineColor='#ffffff', lineWidth=1, 
#     alphaMin=.125, alphaAmplitude=10000, zorder=20
# )
srv.plotClean(fig, ax, bbox=BBOX)
ax.set_facecolor(STYLE_BG['color'])
fig.savefig(
    path.join(paths['data'], CODE, fNameBase+'_CLN'), 
    transparent=False, facecolor=STYLE_BG['color'],
    bbox_inches='tight', pad_inches=PAD, dpi=DPI
)
plt.close('all')
###############################################################################
# Plot frames
###############################################################################
plt.rcParams['axes.facecolor']='#00000000'
plt.rcParams['savefig.facecolor']='#00000000'
GENS = log.shape[0]
gen = 0
for gen in range(GENS)[0:]:
    print("* Exporting {:04d}/{:04d}".format(gen, GENS), end='\r')
    # Get traps ---------------------------------------------------------------
    trpEntry = log.iloc[gen]['traps']
    trpPos = aux.idStringToArray(trpEntry, discrete=True)
    trpCds = srv.chromosomeIDtoXY(trpPos, lnd.pointID, lnd.pointCoords).T
    # Assemble and update traps -----------------------------------------------
    trapsLocs = pd.DataFrame(
        np.vstack([trpCds, lnd.trapsTypes, lnd.trapsFixed]).T, 
        columns=['lon', 'lat', 't', 'f']
    )
    trapsLocs['t'] = trapsLocs['t'].astype('int64')
    trapsLocs['f'] = trapsLocs['f'].astype('int64')
    lnd.updateTraps(trapsLocs, lnd.trapsKernels)
    lnd.updateTrapsRadii([1])
    fitness = log['min'].iloc[gen]
    # Plot --------------------------------------------------------------------
    (fig, ax) = (plt.figure(figsize=FIG_SIZE), plt.axes(projection=PROJ))
    # lnd.plotSites(fig, ax, size=50)
    lnd.plotTraps(
        fig, ax, 
        zorders=(30, 25), size=750, transparencyHex='99', proj=PROJ
    )
    ax.text(
        0.9, 0.9, '{:.1f}'.format(fitness),
        horizontalalignment='right', verticalalignment='center',
        fontsize=70, color='#ffffff22', rotation=0,
        transform=ax.transAxes, zorder=-10
    )
    ax.text(
        0.9, 0.1, '{:04d}'.format(gen),
        horizontalalignment='right', verticalalignment='center',
        fontsize=20, color='#ffffff22',
        transform=ax.transAxes, zorder=-10
    )
    srv.plotClean(fig, ax, bbox=BBOX)
    fig.savefig(
        path.join(OUT_VID, '{:04d}.png'.format(gen)), 
        transparent=True, facecolor=None,
        bbox_inches='tight', pad_inches=PAD, dpi=DPI
    )
    plt.close("all")
    # Overlay Brute-force -----------------------------------------------------
    # time.sleep(.1)
    background = Image.open(path.join(paths['data'], CODE, fNameBase+'_CLN.png')).convert('RGBA')
    foreground = Image.open(path.join(OUT_VID, '{:04d}.png'.format(gen))).convert('RGBA')
    (w, h) = background.size
    background = background.crop((0, 0, w, h))
    foreground = foreground.resize((int(w/1), int(h/1)), Image.Resampling.LANCZOS)
    background = Image.alpha_composite(background, foreground)
    background.save(path.join(OUT_VID, '{:04d}.png'.format(gen)), dpi=(DPI, DPI))
    background.close(); foreground.close()
###############################################################################
# Export FFMPEG
#   "ffmpeg -start_number 0 -r 4 -f image2 -s 1920x1080
#       -i STP_10_%05d.png -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" 
#       -vcodec libx264 -preset veryslow -crf 15 
#       -pix_fmt yuv420p OUTPUT_PATH.mp4"
############################################################################### 
fmpegBse = "ffmpeg -start_number 0 -r 24 -f image2 -s 1920x1080 -i {}/%04d.png ".format(OUT_VID)
fmpegMid = "-vf pad=ceil(iw/2)*2:ceil(ih/2)*2 -pix_fmt yuv420p {}/{}.mp4 -y".format(OUT_VID, fNameBase)
fmpegFll = fmpegBse+fmpegMid
process = subprocess.Popen(fmpegFll.split(), stdout=subprocess.PIPE)
(output, error) = process.communicate()
    