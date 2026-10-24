"""Basic correctness checks for the FIT3144 Qiskit prototype."""

import unittest
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, Statevector

from quantum_information import (
    pairwise_qmi,
    reduced_density_matrix,
    von_neumann_entropy,
)
from edge_weights import dimensionality_weight
from graph_construction import (
    build_weighted_graph,
    maximum_spanning_tree,
    bron_kerbosch_maximal_cliques,
)


def product_state():
    return DensityMatrix(Statevector.from_label("00"))


def bell_state():
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    return DensityMatrix(Statevector.from_instruction(circuit))


def ghz_state():
    circuit = QuantumCircuit(3)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.cx(0, 2)
    return DensityMatrix(Statevector.from_instruction(circuit))


class TestQuantumInformation(unittest.TestCase):
    def test_product_state_qmi_is_zero(self):
        self.assertAlmostEqual(pairwise_qmi(product_state(), 0, 1), 0.0, places=8)

    def test_bell_state_qmi_is_two_bits(self):
        self.assertAlmostEqual(pairwise_qmi(bell_state(), 0, 1), 2.0, places=8)

    def test_bell_reduced_state_entropy_is_one_bit(self):
        rho_a = reduced_density_matrix(bell_state(), [0])
        self.assertAlmostEqual(von_neumann_entropy(rho_a), 1.0, places=8)

    def test_ghz_pairwise_qmi_is_one_bit(self):
        # Each two-qubit reduction of a 3-qubit GHZ state is classically correlated.
        self.assertAlmostEqual(pairwise_qmi(ghz_state(), 0, 1), 1.0, places=8)

    def test_dimensionality_weight_for_qubits_is_two(self):
        self.assertAlmostEqual(dimensionality_weight(product_state(), 0, 1), 2.0)


class TestGraphConstruction(unittest.TestCase):
    def test_complete_graph_edge_count(self):
        graph = build_weighted_graph(bell_state(), "qmi")
        self.assertEqual(graph.number_of_nodes(), 2)
        self.assertEqual(graph.number_of_edges(), 1)

    def test_mst_has_n_minus_one_edges(self):
        graph = build_weighted_graph(ghz_state(), "qmi")
        tree = maximum_spanning_tree(graph)
        self.assertEqual(tree.number_of_edges(), tree.number_of_nodes() - 1)

    def test_bron_kerbosch_on_triangle(self):
        import networkx as nx
        graph = nx.complete_graph(3)
        cliques = bron_kerbosch_maximal_cliques(graph)
        self.assertEqual(cliques, [[0, 1, 2]])


if __name__ == "__main__":
    unittest.main()
