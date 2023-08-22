#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import argv, exit
import numpy as np
from os import path
import pandas as pd
import compress_pickle as pkl
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
import MGSurvE as srv
import MoNeT_MGDrivE as monet
import constants as cst


###############################################################################
# Bash and user inputs
###############################################################################
if srv.isNotebook():
    (EPS, MIN) = (500, 1)
else:
    (EPS, MIN) = (int(argv[1]), 1)
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
(aggCentroids, clstSrt) = ([], list(PTS['cluster'].unique()))
for cix in clstSrt:
    matches = PTS['cluster']==cix
    ctr = list(np.mean(PTS[matches][['lon', 'lat']], axis=0))
    aggCentroids.append([cix]+ctr)
aggDF = pd.DataFrame(aggCentroids, columns=['ix', 'lon', 'lat'])
###############################################################################
# Export to Disk
###############################################################################
fID = f'{ID}-{clustersNum:03d}'
pkl.dump(aggMat, path.join(PTH_OUT, fID+'-MAG'), compression='bz2')
pkl.dump(aggDF, path.join(PTH_OUT, fID+'-AGG'), compression='bz2')
pkl.dump(PTS, path.join(PTH_OUT, fID+'-CLS'), compression='bz2')
###############################################################################
# Plot
###############################################################################
# pal = cst.CLUSTER_PALETTE
# colors = [pal[i%len(pal)] for i in PTS['cluster']]
# (fig, ax) = plt.subplots(figsize=(SZE, SZE))
# ax.scatter(PTS['lon'], PTS['lat'], color=colors)
# ax.set_aspect('equal')
# fig.savefig(
#     path.join(PTH_OUT, fID+'-AGG'), 
#     bbox_inches='tight', pad_inches=0, dpi=DPI, transparent=False
# )
# plt.close('all')
###############################################################################
# Exit (for bash)
###############################################################################
if not srv.isNotebook():
    # exit(clustersNum)
    print(clustersNum)