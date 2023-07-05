from scipy.sparse import csr_matrix

from dtcc_model.roadnetwork import RoadNetwork


def to_matrix(road_network: RoadNetwork):
    """
    Converts a road network to a sparse matrix.
    @param road_network : RoadNetwork The road network to convert.

    @return csr_matrix The sparse matrix.
    """

    road_graph = []

    for road in road_network.roads:
        road_graph.append((road.road_vertices[0], road.road_vertices[-1], road.length))
    start_nodes, end_nodes, weights = list(zip(*road_graph))
    road_matrix = csr_matrix(
        (weights, (start_nodes, end_nodes)),
        shape=(len(road_network.roads), len(road_network.roads)),
    )
