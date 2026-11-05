"""Quantum information helpers built on Qiskit's quantum_info module."""

from __future__ import annotations

import numpy as np
from qiskit.quantum_info import DensityMatrix, partial_trace


def as_density_matrix(state) -> DensityMatrix:
    """
    Convert a Qiskit Statevector/DensityMatrix-like object to DensityMatrix
    """
    
    rho = state if isinstance(state, DensityMatrix) else DensityMatrix(state)
    data = np.asarray(rho.data, dtype=complex)

    if data.ndim != 2 or data.shape[0] != data.shape[1]:
        raise ValueError("The input must represent a square density matrix.")
        
    dim = data.shape[0]
    n_qubits = int(round(np.log2(dim)))

    # Checks for a valid matrix input
    if 2**n_qubits != dim:
        raise ValueError("The density-matrix dimension must be a power of two.")
        
    if not np.allclose(data, data.conj().T, atol=1e-9):
        raise ValueError("The density matrix must be Hermitian.") # meaning is not explicitly covered in the SLR
        
    if not np.isclose(np.trace(data), 1.0, atol=1e-8):
        raise ValueError("The density matrix must have trace one.")
        
    if np.min(np.linalg.eigvalsh((data + data.conj().T) / 2)) < -1e-8:
        raise ValueError("The density matrix must be positive semidefinite.")
    return rho


def number_of_qubits(rho) -> int:
    """
    Return the number of qubits represented by a density matrix
    """
    rho = as_density_matrix(rho)
    return int(round(np.log2(rho.data.shape[0])))


def reduced_density_matrix(rho, keep: list[int]) -> DensityMatrix:
    """
    Return the reduced density operator on the qubits in "keep"

    "keep" uses Qiskit qubit indices. The other qubits are traced out.
    The order of the retained subsystems follows Qiskit's partial_trace behavior.
    """
    
    rho = as_density_matrix(rho)
    n = number_of_qubits(rho)
    keep = list(keep)

    if len(set(keep)) != len(keep):
        raise ValueError("The `keep` list cannot contain duplicate qubit indices.")
        
    if any(q < 0 or q >= n for q in keep):
        raise ValueError(f"Qubit indices must be between 0 and {n - 1}.")
        
    if not keep:
        raise ValueError("At least one qubit must be retained.")

    traced_out = [q for q in range(n) if q not in keep]
    if not traced_out:
        return rho
        
    return partial_trace(rho, traced_out)


def von_neumann_entropy(rho, base: float = 2.0, tol: float = 1e-12) -> float:
    """
    Calculate S(rho) = -Tr(rho log_base(rho)).
    
    Returns entropy in bits by default.
    """
    rho = as_density_matrix(rho)
    if base <= 0 or np.isclose(base, 1.0):
        raise ValueError("The logarithm base must be positive and not equal to one.")

    # Hermitian symmetrisation suppresses tiny numerical asymmetries. Minor debugging.
    matrix = (np.asarray(rho.data) + np.asarray(rho.data).conj().T) / 2
    eigenvalues = np.linalg.eigvalsh(matrix).real
    eigenvalues = np.clip(eigenvalues, 0.0, None)
    eigenvalues = eigenvalues[eigenvalues > tol]
    if eigenvalues.size == 0:
        return 0.0
    return float(-np.sum(eigenvalues * np.log(eigenvalues) / np.log(base)))


def pairwise_qmi(rho, i: int, j: int, base: float = 2.0) -> float:
    """
    Calculate I(i:j) = S(rho_i) + S(rho_j) - S(rho_ij), in bits by default.
    """
    
    if i == j:
        raise ValueError("QMI requires two distinct subsystems.")
        
    rho = as_density_matrix(rho)
    n = number_of_qubits(rho)
    
    if not (0 <= i < n and 0 <= j < n):
        raise ValueError(f"Qubit indices must be between 0 and {n - 1}.")

    rho_i = reduced_density_matrix(rho, [i])
    rho_j = reduced_density_matrix(rho, [j])
    rho_ij = reduced_density_matrix(rho, [i, j])
    value = (
        von_neumann_entropy(rho_i, base=base)
        + von_neumann_entropy(rho_j, base=base)
        - von_neumann_entropy(rho_ij, base=base)
    )
    
    # QMI is nonnegative mathematically; remove tiny negative roundoff. Minor debugging
    if value < 0 and value > -1e-8:
        value = 0.0
    return float(value)
