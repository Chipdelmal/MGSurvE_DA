
import osmnx as ox
import numpy as np
import networkx as nx

###############################################################################
# Routing
###############################################################################
def routeDistancesMatrix(G, nNodes, weight='length'):
    TRPS_NUM = len(nNodes)
    dMatrix = np.zeros((TRPS_NUM, TRPS_NUM), dtype=float)
    for row in range(TRPS_NUM):
        cnode = nNodes[row]
        for col in range(TRPS_NUM):
            tnode = nNodes[col]
            dMatrix[row, col] = nx.shortest_path_length(
                G=G, source=cnode, target=tnode, weight=weight
            )
    return dMatrix


def routeMatrix(G, nNodes, weight='length'):
    TRPS_NUM = len(nNodes)
    dMatrix = []
    for row in range(TRPS_NUM):
        cnode = nNodes[row]
        dRow = []
        for col in range(TRPS_NUM):
            tnode = nNodes[col]
            route = nx.shortest_path(
                G=G, source=cnode, target=tnode, weight=weight
            )
            dRow.append(route)
        dMatrix.append(dRow)
    return dMatrix


def routeDistances(G, trpsX, trpsY):
    (nNodes, dNodes) = ox.nearest_nodes(G, trpsX, trpsY, return_dist=True)
    dMat = routeDistancesMatrix(G, nNodes)
    return dMat


def print_solution(data, manager, routing, solution):
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


def generateDataModel(distanceMatrix, vehiclesNumber=1, depot=1):
    data = {}
    data["distance_matrix"] = distanceMatrix.astype(int)
    data["num_vehicles"] = vehiclesNumber
    data["depot"] = depot
    return data


def getSolution(data, manager, routing, solution):
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


def distanceCallback(from_index, to_index, manager, data):
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return data["distance_matrix"][from_node][to_node]


def ortoolToOsmnxRoute(data, G, rtoolSolution, oxmnxNodes, weight='length'):
    SOL_ROUTES = []
    for j in range(data["num_vehicles"]):
        rtes = [
            ox.shortest_path(
                G, 
                oxmnxNodes[rtoolSolution[j][i]], 
                oxmnxNodes[rtoolSolution[j][i+1]], 
                weight=weight
            )
            for i in range(len(rtoolSolution[j])-1)
        ]
        SOL_ROUTES.append(rtes)
    return SOL_ROUTES

def ortoolToOsmnxLength(data, G, rtoolSolution, oxmnxNodes, weight='length'):
    SOL_LENGTH = np.sum([
        np.sum([
            nx.shortest_path_length(
                G=G, 
                source=oxmnxNodes[rtoolSolution[j][i]], 
                target=oxmnxNodes[rtoolSolution[j][i+1]], 
                weight=weight
            )
            for i in range(len(rtoolSolution[j])-1)
        ]) for j in range(data["num_vehicles"])
    ])
    return SOL_LENGTH

# def optimizeRoute(
#         distanceMatrix,
#         vehiclesNumber=1, depot=1,
#         maxTravelDistance=100000
#     ):
    