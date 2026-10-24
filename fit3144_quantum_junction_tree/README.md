# FIT3144 Quantum Graph Construction Prototype (Qiskit)

This is a runnable research prototype for comparing three pairwise edge-weighting approaches:

1. **Hilbert-space dimensionality**: `log2(dim(H_i tensor H_j))`. For equally sized qubits this is constant, so it is only a structural baseline and cannot distinguish edges.
2. **Pairwise von Neumann entropy**: `S(rho_ij)`. This measures uncertainty in the joint state of the pair; it is not itself a measure of correlation.
3. **Quantum mutual information (QMI)**: `S(rho_i) + S(rho_j) - S(rho_ij)`. This measures total correlations between the two subsystems.

The program builds a complete weighted graph, computes a maximum spanning tree for each method, and lists maximal cliques in the complete weighted graph. It also runs validation tests for product, Bell, and GHZ states.

## Important scope note

A maximum spanning tree over individual qubits is a Chow–Liu-style tree, **not a quantum junction tree**. The project does not yet implement clique-tree construction, separator consistency, quantum Markov conditions, or exact junction-tree inference. Maximal cliques are reported for the input graph only; since the pairwise graph is complete in this prototype, its only maximal clique is normally the full vertex set. For useful clique-tree experiments, a separate sparse graph / triangulation stage will be needed.

## Requirements

- Python 3.10+
- Qiskit
- NumPy
- NetworkX

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the demo:

```bash
python main.py
```

Run tests:

```bash
python -m unittest -v tests.py
```

## Files

- `main.py`: demonstration using product, Bell, and GHZ states.
- `quantum_information.py`: partial trace, von Neumann entropy, and QMI using Qiskit's quantum information classes.
- `edge_weights.py`: the three edge-weighting approaches.
- `graph_construction.py`: weighted graph, maximum spanning tree, and Bron–Kerbosch maximal-clique search.
- `tests.py`: unit tests for basic mathematical properties.

## Qiskit subsystem ordering

Qiskit uses little-endian conventions for computational-basis indexing. The functions here use Qiskit's `partial_trace` and consistently refer to subsystem labels by their Qiskit qubit indices. When comparing a printed matrix against hand calculations, remember that basis ordering convention.
