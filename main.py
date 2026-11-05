"""Run a small Qiskit demonstration of the three edge-weighting approaches."""

from __future__ import annotations

from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, Statevector

from graph_construction import (build_weighted_graph, maximum_spanning_tree, bron_kerbosch_maximal_cliques, tree_weight)
from quantum_information import pairwise_qmi, von_neumann_entropy


def make_example_states():
    """
    "Return small, known test states as Qiskit DensityMatrix objects.
    """
    
    # Four-qubit product state |0000>
    product = DensityMatrix(Statevector.from_label("0000"))

    # Bell state on qubits 0 and 1; qubits 2 and 3 remain |0>.
    bell_circuit = QuantumCircuit(4)
    bell_circuit.h(0)
    bell_circuit.cx(0, 1)
    bell = DensityMatrix(Statevector.from_instruction(bell_circuit))

    # Four-qubit GHZ state: (|0000> + |1111>) /root(2).
    ghz_circuit = QuantumCircuit(4)
    ghz_circuit.h(0)
    
    for q in range(1, 4):
        ghz_circuit.cx(0, q)
        
    ghz = DensityMatrix(Statevector.from_instruction(ghz_circuit))

    return {
        "product |0000>": product,
        "Bell(0,1) plus |00>": bell,
        "4-qubit GHZ": ghz,
    }


def print_graph(graph):
    """
    Outputs the graph
    """
    for i, j, data in sorted(graph.edges(data=True)):
        print(f"  ({i}, {j}): {data['weight']:.6f}")


def main():
    states = make_example_states()
    methods = ["dimensionality", "pairwise_entropy", "qmi"]

    for state_name, rho in states.items():
        print("\n" + "=" * 72)
        print(state_name)
        print(f"Global von Neumann entropy: {von_neumann_entropy(rho):.6f} bits")
        print(f"QMI between qubits 0 and 1: {pairwise_qmi(rho, 0, 1):.6f} bits")

        for method in methods:
            graph = build_weighted_graph(rho, method)
            tree = maximum_spanning_tree(graph)
            print(f"\nMethod: {method}")
            print("Complete graph edge weights:")
            print_graph(graph)
            print("Maximum spanning tree edges:")
            print_graph(tree)
            print(f"Total tree weight: {tree_weight(tree):.6f}")

        qmi_graph = build_weighted_graph(rho, "qmi")
        print("\nMaximal cliques in the complete QMI graph:")
        print(bron_kerbosch_maximal_cliques(qmi_graph))
        print(
            "Note: this graph is complete by construction, so its maximal clique "
            "is normally the set of all vertices. This is not yet a junction tree."
        )


if __name__ == "__main__":
    main()
