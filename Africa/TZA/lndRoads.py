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
import networkx as nx
from copy import deepcopy
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
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

if srv.isNotebook():
    (USR, COUNTRY, CODE, COMMUNE, COORDS, GENS, TRPS_NUM, REP) = (
        'zelda', 'Tanzania', 'TZA', 
        'Mwanza', (-2.5195,32.9046), 1000, 50, 0
    )
else:
    (USR, COUNTRY, CODE, COMMUNE, COORDS, GENS, TRPS_NUM, REP) = argv[1:]
    (COORDS, GENS, FRACTION, REP) = (
        tuple(map(float, COORDS.split(','))),
        int(GENS), int(TRPS_NUM), int(REP)
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
(MAG, LAG) = (
    pkl.load(path.join(paths['data'], CODE, COMMUNE+'_AGG.bz')),
    pd.read_csv(pthAct)
)
# Get filename and create out folder ------------------------------------------
SITES_NUM = LAG.shape[0]
fNameBase = '{}-{:04d}_{:04d}-{:02d}'.format(COMMUNE, SITES_NUM, TRPS_NUM, REP)
(log, lnd) = (
    pd.read_csv(path.join(paths['data'], CODE, fNameBase+'_LOG.csv')),
    srv.loadLandscape(path.join(paths['data'], CODE), fNameBase+'_LND', fExt='pkl')
)
###############################################################################
# Examine landscape
###############################################################################
(PAD, DPI) = (0, 250)
lnd.updateTrapsRadii([1])
bbox = lnd.getBoundingBox()
trpMsk = srv.genFixedTrapsMask(lnd.trapsFixed)
# Get traps ---------------------------------------------------------------
gen=-1
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
###############################################################################
# Get Traps Distance
#   https://github.com/gboeing/osmnx-examples/blob/main/notebooks/02-routing-speed-time.ipynb
###############################################################################
G = ox.project_graph(NTW, to_crs=PROJ)
G = ox.utils_graph.get_largest_component(G, strongly=True)
(ix, jx) = (10, 5)
cNode = ox.nearest_nodes(G, np.mean(BLD['centroid_lon']), np.mean(BLD['centroid_lat']))
(nNodes, dNodes) = ox.nearest_nodes(G, trapsLocs['lon'], trapsLocs['lat'], return_dist=True)
routes = ox.shortest_path(G, TRPS_NUM*[cNode], nNodes, weight="length")
lengths = [
    nx.shortest_path_length(G=G, source=cNode, target=node, weight='length')
    for node in nNodes
]
dMat = aux.routeDistances(G, trpCds[0], trpCds[1])
rMat = aux.routeMatrix(G, nNodes)
# plt.matshow(dMat)
###############################################################################
# Optimize
###############################################################################
def create_data_model():
    data = {}
    data["distance_matrix"] = dMat.astype(int)
    data["num_vehicles"] = 5
    data["depot"] = 40
    return data

def get_solution(data, manager, routing, solution):
    routes = []
    for vehicle_id in range(data["num_vehicles"]):
        index = routing.Start(vehicle_id)
        route = []
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        route = route + [route[0]]
        routes.append(route)
    return routes

data = create_data_model()
manager = pywrapcp.RoutingIndexManager(
    len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
)
routing = pywrapcp.RoutingModel(manager)
def distance_callback(from_index, to_index):
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return data["distance_matrix"][from_node][to_node]

transit_callback_index = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
dimension_name = "Distance"
routing.AddDimension(
    transit_callback_index,
    0,  # no slack
    100000,  # vehicle maximum travel distance
    True,  # start cumul to zero
    dimension_name,
)
distance_dimension = routing.GetDimensionOrDie(dimension_name)
distance_dimension.SetGlobalSpanCostCoefficient(100)
search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
)
solution = routing.SolveWithParameters(search_parameters)
aux.print_solution(data, manager, routing, solution)
OSOL = get_solution(data, manager, routing, solution)
SOL_ROUTES = []
for j in range(data["num_vehicles"]):
    rtes = [
        ox.shortest_path(G, nNodes[OSOL[j][i]], nNodes[OSOL[j][i+1]], weight='length')
        for i in range(len(OSOL[j])-1)
    ]
    SOL_ROUTES.append(rtes)
SOL_LENGTH = np.sum([
    np.sum([
        nx.shortest_path_length(
            G=G, source=nNodes[OSOL[j][i]], target=nNodes[OSOL[j][i+1]], 
            weight='length'
        )
        for i in range(len(OSOL[j])-1)
    ]) for j in range(data["num_vehicles"])
])
###############################################################################
# Plot Landscape
###############################################################################
(STYLE_GD, STYLE_BG, STYLE_TX, STYLE_CN, STYLE_BD, STYLE_RD) = cst.MAP_STYLE_D
ALL_ROUTES = False
(FIG_SIZE, PROJ, BSCA) = ((15, 15), ccrs.PlateCarree(), 0.001)
BBOX = (
    (lnd.landLimits[0][0]-BSCA, lnd.landLimits[0][1]+BSCA),
    (lnd.landLimits[1][0]-BSCA, lnd.landLimits[1][1]+BSCA)
)
(fig, ax) = (
    plt.figure(figsize=FIG_SIZE, facecolor=STYLE_BG['color']), 
    plt.axes(projection=PROJ)
)
(fig, ax) = ox.plot_graph(
    G, ax, node_size=0, figsize=(40, 40), show=False,
    bgcolor=STYLE_BG['color'], edge_color=STYLE_RD['color'], 
    edge_alpha=STYLE_RD['alpha']*.6, edge_linewidth=STYLE_RD['width']
)
lnd.plotTraps(
    fig, ax, 
    size=250, transparencyHex='CC',
    zorders=(30, 25), proj=PROJ
)
lnd.plotLandBoundary(
    fig, ax,  
    landTuples=(('10m', '#dfe7fd99', 30), ('10m', '#ffffffDD', 5))
)
(fig, ax) = ox.plot_footprints(
    BLD, ax=ax, save=False, show=False, close=False,
    bgcolor=STYLE_BG['color'], color=STYLE_BD['color'], 
    alpha=STYLE_BD['alpha']
)
# (fig, ax) = ox.plot_footprints(
#     BLD, ax=ax, save=False, show=False, close=False,
#     bgcolor=STYLE_BG['color'], alpha=0.5,
#     color=list(BLD['cluster_color']), 
# )
depot = trapsLocs.iloc[data['depot']]
ax.plot(
    depot['lon'], depot['lat'], 
    marker="D", ms=15, mew=2, 
    color='#f72585FF', mec='#ffffff',
    zorder=100
)
# for ix in range(TRPS_NUM):
#     ax.text(
#         trpCds[0][ix], trpCds[1][ix], ix, 
#         fontsize=10, ha='center', va='center', zorder=50
#     )
if ALL_ROUTES:
    for route in rMat:
        for r in route:
            (fig, ax) = ox.plot_graph_route(
                G, r, ax=ax, save=False, show=False, close=False,
                route_color='#b5e48c22', route_linewidth=4, 
                node_size=0, node_alpha=0, bgcolor='#00000000', 
                route_alpha=0.0225
            )
else:
    for (ix, vehicle) in enumerate(SOL_ROUTES):
        for route in vehicle:
            (fig, ax) = ox.plot_graph_route(
                G, route, ax=ax, save=False, show=False, close=False,
                route_color=cst.RCOLORS[ix], route_linewidth=4, 
                node_size=0, node_alpha=0, bgcolor='#00000000', 
                route_alpha=0.65
            )
srv.plotClean(fig, ax, bbox=BBOX)
ax.set_facecolor(STYLE_BG['color'])
# ax.text(
#     0.05, 0.05,
#     f'Fitness: {fitness:.2f}\nRoutes Total: {SOL_LENGTH/1e3:.0f} km', 
#     transform=ax.transAxes, 
#     horizontalalignment='left', verticalalignment='bottom', 
#     color=STYLE_BD['color'], fontsize=15,
#     alpha=0.75
# )
fig.savefig(
    path.join(paths['data'], CODE, fNameBase+'_RTE'), 
    transparent=False, facecolor=STYLE_BG['color'],
    bbox_inches='tight', pad_inches=PAD, dpi=DPI
)
# plt.close('all')
 