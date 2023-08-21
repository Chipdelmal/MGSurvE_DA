#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import argv
import numpy as np
import pandas as pd
from os import path
import compress_pickle as pkl
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import normalize
import MGSurvE as srv
import MoNeT_MGDrivE as monet
import constants as cst
pd.options.mode.chained_assignment = None 


###############################################################################
# Bash and user inputs
###############################################################################
if srv.isNotebook():
    (EPS, MIN) = (500, 1)
else:
    pass
(ID, PTH_IN, PTH_OUT) = (
    cst.EXP_ID,
    cst.PATHS['data'], cst.PATHS['data']
)
(SZE, DPI) = (10, 300)
###############################################################################
# Load Data
###############################################################################
(PTS, MIG, DST) = (
    pkl.load(path.join(PTH_IN, f'{ID}-PTS'), compression='bz2'),
    pkl.load(path.join(PTH_IN, f'{ID}-MIG'), compression='bz2'),
    pkl.load(path.join(PTH_IN, f'{ID}-DST'), compression='bz2')
)
meanDst = np.mean(np.extract(DST.reshape(-1) != 0, DST.reshape(-1)))
eps = (cst.KMS_PER_RADIAN/meanDst)*EPS/1e6
###############################################################################
# Cluster Points
###############################################################################
latLons = np.array(list(zip(PTS['lat'], PTS['lon'])))
clustering = DBSCAN(
    eps=eps, min_samples=MIN, 
    algorithm='ball_tree', metric='haversine', n_jobs=cst.JOBS
).fit(np.radians(latLons))
clustersNum = len(set(clustering.labels_))
PTS['cluster'] = clustering.labels_
###############################################################################
# Aggregate Points
###############################################################################
aggMat = monet.aggregateLandscape(MIG, PTS['cluster'], type=0)
###############################################################################
# Export to Disk
###############################################################################
fID = f'{ID}-{EPS:05d}'
pkl.dump(aggMat, path.join(PTH_OUT, fID+'-AGG'), compression='bz2')
pkl.dump(PTS, path.join(PTH_OUT, fID+'-CLS'), compression='bz2')
###############################################################################
# Plot
###############################################################################
pal = cst.CLUSTER_PALETTE
colors = [pal[i%len(pal)] for i in PTS['cluster']]
(fig, ax) = plt.subplots(figsize=(SZE, SZE))
ax.scatter(PTS['lon'], PTS['lat'], color=colors)
ax.set_aspect('equal')