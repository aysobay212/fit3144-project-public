"""Weighted graph, maximum spanning tree, and Bron–Kerbosch helpers."""

from __future__ import annotations

import networkx as nx
from edge_weights import WEIGHT_METHODS
from quantum_information import as_density_matrix, number_of_qubits


def build_weighted_graph(rho, method: str = "qmi"):
    """
    Build a complete weighted graph using the selected edge-weight method.
    """
    
    if method not in WEIGHT_METHODS:
        valid = ", ".join(WEIGHT_METHODS)
        raise ValueError(f"Unknown method {method!r}. Choose one of: {valid}.")

    rho = as_density_matrix(rho)
    n = number_of_qubits(rho)
    weight_fn = WEIGHT_METHODS[method]
    graph = nx.Graph()
    graph.add_nodes_from(range(n))

    for i in range(n):
        for j in range(i + 1, n):
            graph.add_edge(i, j, weight=float(weight_fn(rho, i, j)))

    return graph


def maximum_spanning_tree(graph: nx.Graph) -> nx.Graph:
    """
    Return a maximum spanning tree of a connected weighted graph.
    """
    
    if graph.number_of_nodes() == 0:
        raise ValueError("Cannot construct a spanning tree of an empty graph.")
        
    if not nx.is_connected(graph):
        raise ValueError("The input graph must be connected.")
        
    return nx.maximum_spanning_tree(graph, weight="weight", algorithm="kruskal") # Kruskal is the default, this can be changed


def bron_kerbosch_maximal_cliques(graph: nx.Graph) -> list[list[int]]:
    """
    Find maximal cliques using the Bron–Kerbosch algorithm with pivoting (refer to pseudo-code)

    Returns a list of sorted vertex lists. The order of cliques is not guaranteed.
    """
    if graph.is_directed():
        raise ValueError("Bron–Kerbosch requires an undirected graph.")

    neighbours = {v: set(graph.neighbors(v)) for v in graph.nodes}
    cliques = []

    def visit(R, P, X):
        if not P and not X:
            cliques.append(sorted(R))
            return

        union_px = P | X
        pivot = max(union_px, key=lambda u: len(P & neighbours[u])) if union_px else None
        candidates = P - (neighbours[pivot] if pivot is not None else set())

        for v in list(candidates):
            visit(R | {v}, P & neighbours[v], X & neighbours[v])
            P.remove(v)
            X.add(v)

    visit(set(), set(graph.nodes), set())
    cliques.sort(key=lambda c: (len(c), c))
    return cliques


def tree_weight(tree: nx.Graph) -> float:
    """Sum edge weights in a weighted tree."""
    return float(sum(data.get("weight", 1.0) for _, _, data in tree.edges(data=True)))
