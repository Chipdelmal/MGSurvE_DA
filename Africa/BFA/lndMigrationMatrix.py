#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
from sys import argv
import osmnx as ox
from shapely import wkt
from random import shuffle, uniform
from engineering_notation import EngNumber
import cartopy.crs as ccrs
import compress_pickle as pkl
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import MoNeT_MGDrivE as monet
import MGSurvE as srv
import auxiliary as aux
ox.config(log_console=False , use_cache=True)
matplotlib.rc('font', family='Savoye LET')

if srv.isNotebook():
    (USR, COUNTRY, CODE, COMMUNE) = ('sami', 'Burkina Faso', 'BFA', 'Manga')
else:
    (USR, COUNTRY, CODE, COMMUNE) = argv[1:]
(PROJ, FOOTPRINT) = (ccrs.PlateCarree(), True)
###############################################################################
# Set Paths
###############################################################################
paths = aux.userPaths(USR)
###############################################################################
# Read from Disk
###############################################################################
(BLD, NTW) = (
    pkl.load(path.join(paths['data'], 'HumanMobility', CODE, COMMUNE+'_BLD')),
    pkl.load(path.join(paths['data'], 'HumanMobility', CODE, COMMUNE+'_NTW'))
)
###############################################################################
# Migration Matrix
###############################################################################
(lonLats, clusters) = (
    np.array(list(zip(BLD['centroid_lon'], BLD['centroid_lat']))),
    list(BLD['cluster_id'])
)
migDst = srv.calcDistanceMatrix(lonLats, distFun=srv.haversineDistance)
migMat = srv.zeroInflatedExponentialKernel(migDst, srv.AEDES_EXP_PARAMS)
aggMat = monet.aggregateLandscape(migMat, clusters, type=2)
###############################################################################
# Dump to Disk
###############################################################################
pkl.dump(
    migDst, path.join(paths['data'], 'HumanMobility', CODE, COMMUNE+'_DST'), 
    compression='bz2'
)
pkl.dump(
    migMat, path.join(paths['data'], 'HumanMobility', CODE, COMMUNE+'_MIG'), 
    compression='bz2'
)
pkl.dump(
    aggMat, path.join(paths['data'], 'HumanMobility', CODE, COMMUNE+'_AGG'), 
    compression='bz2'
)
