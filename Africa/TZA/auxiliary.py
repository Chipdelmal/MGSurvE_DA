#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from math import exp
import networkx as nx
import osmnx as ox
from sklearn.preprocessing import normalize
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap


def roundBase(x, base=5, fun=round):
    return base * fun(x/base)

def userPaths(user):
    if user=='sami':
        (DTA_ROOT, SIM_ROOT) = (
            '/Users/sanchez.hmsc/Documents/WorkSims/MGSurvE_DA/', 
            '/Users/sanchez.hmsc/Documents/WorkSims/MGSurvE_DA/'
        )
    elif user=='zelda':
        (DTA_ROOT, SIM_ROOT) = (
            '/RAID5/marshallShare/MGSurvE_DA/', 
            '/RAID5/marshallShare/MGSurvE_DA/'
        )
    elif user=='link':
        (DTA_ROOT, SIM_ROOT) = (
            '/home/sanchez.hmsc/MGSurvE_Africa/', 
            '/home/sanchez.hmsc/MGSurvE_Africa/'
        )
    elif user=='lab':
        (DTA_ROOT, SIM_ROOT) = (
            '/Users/sanchez.hmsc/Documents/WorkSims/MGSurvE_DA/Africa/', 
            '/Users/sanchez.hmsc/Documents/WorkSims/MGSurvE_DA/Africa/'
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


def colorPaletteFromHexList(clist):
    c = mcolors.ColorConverter().to_rgb
    clrs = [c(i) for i in clist]
    rvb = mcolors.LinearSegmentedColormap.from_list("", clrs)
    return rvb


def idStringToArray(string, discrete=True):
    if discrete:
        return np.array([int(i) for i in string[1:-1].split(',')])
    else:
        return np.array([float(i) for i in string[1:-1].split(',')])


def reArrangeMatrix(matrix, sorting):
    return matrix[sorting][:,sorting]


def reArrangeClusterMatrix(matrix, clusters, distances=None):
    ran = np.arange(0, len(clusters))
    if not distances:
        clusterSorts = list(np.lexsort((ran, clusters)))
    else:
        clusterSorts = list(np.lexsort((ran, clusters, distances)))
    return reArrangeMatrix(matrix, clusterSorts)


def aggregateLandscape(migrationMatrix, clusters, type=0):
    '''
    Takes the migration matrix, and the clusters list and performs the Markov
        aggregation of the landscape.
    '''
    if type == 0:
        return aggregateLandscapeBase(migrationMatrix, clusters)
    elif type == 1:
        return aggregateLandscapeAltGill(migrationMatrix, clusters)
    elif type == 2:
        return aggregateLandscapeAltVic(migrationMatrix, clusters)


def aggregateLandscapeBase(migrationMatrix, clusters):
    '''
    Takes the migration matrix, and the clusters list and performs the Markov
        aggregation of the landscape.
    '''
    num_clusters = len(set(clusters))
    aggr_matrix = np.zeros([num_clusters, num_clusters], dtype=float)
    aggr_latlongs = [[] for x in range(num_clusters)]
    for idx, label in enumerate(clusters):
        aggr_latlongs[label].append(idx)
    for row in range(num_clusters):
        row_ids = aggr_latlongs[row]
        for colum in range(num_clusters):
            colum_ids = aggr_latlongs[colum]
            res = 0
            for rid in row_ids:
                for cid in colum_ids:
                    res += migrationMatrix[rid][cid]
            aggr_matrix[row][colum] = res /len(row_ids)
    return aggr_matrix


def aggregateLandscapeAltVic(migrationMatrix, clusters):
    '''
    Faster version of the aggregation algorithm dev by Gillian
    '''
    matrix_size = len(clusters)
    num_clusters = len(set(clusters))
    aggr_matrix = np.zeros([num_clusters, num_clusters], dtype=float)
    aggr_number = [0]*num_clusters
    for row in range(matrix_size):
        cRow = clusters[row]
        aggr_number[cRow] += 1
        for col in range(matrix_size):
            cCol = clusters[col]
            aggr_matrix[cRow][cCol] += migrationMatrix[row][col]
    for row in range(num_clusters):
        aggr_matrix[row] = [x/aggr_number[row] for x in aggr_matrix[row]]
    return aggr_matrix


def aggregateLandscapeAltGill(migrationMatrix, clusters):
    '''
    Another alternative of the aggregation algorithm dev by Gillian
    '''
    num_clusters = len(set(clusters))
    aggr_matrix = np.zeros([num_clusters, num_clusters], dtype=float)
    aggr_latlongs = [[] for x in range(num_clusters)]
    # get all the patches that fall under each label
    [aggr_latlongs[label].append(idx) for idx, label in enumerate(clusters)]
    # get the number of patches in each label for normalization later
    normVal = dict()
    for idx, label in enumerate(clusters):
        normVal[label] = len(aggr_latlongs[label])
    for row in range(num_clusters):
        row_ids = aggr_latlongs[row]
        for column in range(num_clusters):
            colum_ids = aggr_latlongs[column]
            all_comb = [
                migrationMatrix[x][y] for (x, y) in [itertools.product([row_ids, colum_ids])]
            ]
            aggr_matrix[row][column] = sum(all_comb)/len(row_ids)
    return aggr_matrix


###############################################################################
# Routing
###############################################################################
def routeDistancesMatrix(G, nNodes):
    TRPS_NUM = len(nNodes)
    dMatrix = np.zeros((TRPS_NUM, TRPS_NUM), dtype=float)
    for row in range(TRPS_NUM):
        cnode = nNodes[row]
        for col in range(TRPS_NUM):
            tnode = nNodes[col]
            dMatrix[row, col] = nx.shortest_path_length(
                G=G, source=cnode, target=tnode, weight='length'
            )
    return dMatrix


def routeMatrix(G, nNodes):
    TRPS_NUM = len(nNodes)
    dMatrix = []
    for row in range(TRPS_NUM):
        cnode = nNodes[row]
        dRow = []
        for col in range(TRPS_NUM):
            tnode = nNodes[col]
            route = nx.shortest_path(
                G=G, source=cnode, target=tnode, weight='length'
            )
            dRow.append(route)
        dMatrix.append(dRow)
    return dMatrix


def routeDistances(G, trpsX, trpsY):
    (nNodes, dNodes) = ox.nearest_nodes(G, trpsX, trpsY, return_dist=True)
    dMat = routeDistancesMatrix(G, nNodes)
    return dMat




def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    print(f"Objective: {solution.ObjectiveValue()}")
    max_route_distance = 0
    for vehicle_id in range(data["num_vehicles"]):
        index = routing.Start(vehicle_id)
        plan_output = f"Route for vehicle {vehicle_id}:\n"
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += f" {manager.IndexToNode(index)}, "
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id
            )
        plan_output += f"{manager.IndexToNode(index)}\n"
        plan_output += f"Distance of the route: {route_distance}m\n"
        print(plan_output)
        max_route_distance = max(route_distance, max_route_distance)
    print(f"Maximum of the route distances: {max_route_distance}m")

