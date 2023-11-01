# !/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# Sims:
#   https://github.com/Chipdelmal/MGDrivE/blob/master/Main/ReplacementTPP/sims-bf-server-high.R#L566-L581
#   https://github.com/Chipdelmal/MGDrivE/blob/master/Main/ReplacementTPP/sims-kenya-server-low.R#L562-L577
###############################################################################


###############################################################################
# Load libraries and limit cores
###############################################################################
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
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import MGSurvE as srv
import routing as rte
import auxiliary as aux
import constants as cst
# matplotlib.use('agg')
# ox.config(use_cache=True, log_console=False)

if srv.isNotebook():
    (USR, COUNTRY, CODE, COMMUNE, COORDS, GENS, TRPS_NUM, REP, DIST) = (
        'zelda', 'Tanzania', 'TZA', 
        'Mwanza', (-2.5195,32.9046), 1000, 50, 0, 5000
    )
else:
    (USR, COUNTRY, CODE, COMMUNE, COORDS, GENS, TRPS_NUM, REP, DIST) = argv[1:]
    (COORDS, GENS, FRACTION, REP) = (
        tuple(map(float, COORDS.split(','))),
        int(GENS), int(TRPS_NUM), int(REP)
    )
(PROJ, FOOTPRINT, OVW, VERBOSE, WATER) = (
    ccrs.PlateCarree(), True, 
    {'dist': False, 'kernel': False},
    False,
    True
)
COST_PER_KM = 1.7
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
pthWtr = path.join(paths['data'], CODE, COMMUNE+'_WTR.bz')
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
if WATER:
    try:
        WTR = pkl.load(pthWtr)
    except:
        WTR = ox.geometries.geometries_from_point(
            COORDS, dist=DIST, tags={"natural": "water"}
        )
        pkl.dump(
            WTR, path.join(paths['data'], CODE, COMMUNE+'_WTR'), 
            compression='bz2'
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
dMat = rte.routeDistances(G, trpCds[0], trpCds[1])
rMat = rte.routeMatrix(G, nNodes)
# plt.matshow(dMat)
###############################################################################
# Optimize
###############################################################################
def create_data_model():
    data = {}
    data["distance_matrix"] = dMat.astype(int)
    data["num_vehicles"] = 1
    data["depot"] = 3
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

transitCallbackIx = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transitCallbackIx)
(slack, maxDistance, cumulZero, dimName) = (0, int(1e5), True, "Distance")
routing.AddDimension(transitCallbackIx, slack, maxDistance, cumulZero, dimName)
distance_dimension = routing.GetDimensionOrDie(dimName)
distance_dimension.SetGlobalSpanCostCoefficient(100)
search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
)
solution = routing.SolveWithParameters(search_parameters)
rte.print_solution(data, manager, routing, solution)
OSOL = rte.getSolution(data, manager, routing, solution)
(SOL_ROUTES, SOL_LENGTH) = (
    rte.ortoolToOsmnxRoute(data, G, OSOL, nNodes),
    rte.ortoolToOsmnxLength(data, G, OSOL, nNodes)
)
SOL_COST = (SOL_LENGTH)/1e3*COST_PER_KM
###############################################################################
# Plot Landscape
###############################################################################
(STYLE_GD, STYLE_BG, STYLE_TX, STYLE_CN, STYLE_BD, STYLE_RD) = cst.MAP_STYLE_D
ALL_ROUTES = False
IDS = False
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
    edge_alpha=STYLE_RD['alpha'], edge_linewidth=STYLE_RD['width']
)
ax.text(
    0.05, 0.05,
    f'Fitness: {fitness:.2f} days\nRoute: {SOL_LENGTH/1e3:.0f} km (${SOL_COST:.0f})', 
    transform=ax.transAxes, 
    horizontalalignment='left', verticalalignment='bottom', 
    color=STYLE_BD['color'], fontsize=15,
    alpha=0.75
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
if IDS:
    for ix in range(TRPS_NUM):
        ax.text(
            trpCds[0][ix], trpCds[1][ix], ix, 
            fontsize=20, ha='center', va='center', zorder=150,
            color=STYLE_BD['color']
        )
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
                route_color=cst.RCOLORS[ix], route_linewidth=5, 
                node_size=0, node_alpha=0, bgcolor='#00000000', 
                route_alpha=0.6
            )
if WATER:
    ax = WTR.plot(
        ax=ax, fc='#3C78BB77', markersize=0
    )
srv.plotClean(fig, ax, bbox=BBOX)
ax.set_facecolor(STYLE_BG['color'])
fig.savefig(
    path.join(paths['data'], CODE, fNameBase+'_RTE'), 
    transparent=False, facecolor=STYLE_BG['color'],
    bbox_inches='tight', pad_inches=PAD, dpi=DPI
)
# plt.close('all')
