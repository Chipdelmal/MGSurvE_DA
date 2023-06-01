#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from math import exp
from sklearn.preprocessing import normalize
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap


def userPaths(user):
    if user=='sami':
        (DTA_ROOT, SIM_ROOT) = (
            '/Users/sanchez.hmsc/Documents/WorkSims/MGSurvE_show/', 
            '/Users/sanchez.hmsc/Documents/WorkSims/MGSurvE_show/'
        )
    elif user=='zelda':
        (DTA_ROOT, SIM_ROOT) = (
            '/RAID5/marshallShare/MGSurvE_DA/', 
            '/RAID5/marshallShare/MGSurvE_DA/'
        )
    return {'data': DTA_ROOT, 'sim': SIM_ROOT}



def exponentialKernel(distMat, decay):
    coordsNum = len(distMat)
    migrMat = np.empty((coordsNum, coordsNum))
    for (i, row) in enumerate(distMat):
        for (j, dst) in enumerate(row):
            migrMat[i][j] = exp(-decay*dst)
        for j in range(len(row)):
            if np.isnan(migrMat[i][j]):
                # print("NaN Warning (check points locations, distances might be too large.")
                migrMat[i][j] = 0
    tauN = normalize(migrMat, axis=1, norm='l1')
    return tauN

#!/usr/bin/env python
# -*- coding: utf-8 -*-


def colorPaletteFromHexList(clist):
    c = mcolors.ColorConverter().to_rgb
    clrs = [c(i) for i in clist]
    rvb = mcolors.LinearSegmentedColormap.from_list("", clrs)
    return rvb