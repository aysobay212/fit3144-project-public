from __future__ import annotations

import math
from quantum_information import (as_density_matrix, number_of_qubits, reduced_density_matrix, von_neumann_entropy, pairwise_qmi)


def dimensionality_weight(rho, i: int, j: int) -> float:
    """
    Structural baseline, log2(dim(H_i tensor H_j))

    For n qubits, each subsystem has dimension 2, so this equals 2 for every
    pair. It is intentionally a baseline: it does not encode correlations.
    """
    
    if i == j:
        raise ValueError("An edge must connect two distinct subsystems.")
    rho = as_density_matrix(rho)
    
    n = number_of_qubits(rho)
    
    if not (0 <= i < n and 0 <= j < n):
        raise ValueError(f"Qubit indices must be between 0 and {n - 1}.")
    
    # As the qubit is in a two dimensional Hilbert space
    dim_i = 2 
    dim_j = 2
    return math.log2(dim_i * dim_j)


def pairwise_entropy_weight(rho, i: int, j: int, base: float = 2.0) -> float:
    """
    Heuristic edge weight S(rho_ij), the entropy of the joint two-qubit state

    This measures joint uncertainty, not correlation. A larger value is not
    necessarily a stronger relationship between the qubits.
    """
    
    if i == j:
        raise ValueError("An edge must connect two distinct subsystems.")
        
    rho_ij = reduced_density_matrix(rho, [i, j])
    
    return von_neumann_entropy(rho_ij, base=base)


def qmi_weight(rho, i: int, j: int, base: float = 2.0) -> float:
    """
    Edge weight equal to the quantum mutual information I(i:j)
    """
    
    return pairwise_qmi(rho, i, j, base=base)

# The three different approaches being implemented
WEIGHT_METHODS = {
    "dimensionality": dimensionality_weight,
    "pairwise_entropy": pairwise_entropy_weight,
    "qmi": qmi_weight,
}
