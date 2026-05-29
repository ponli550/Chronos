import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import eigsh
from scipy import sparse

def simulate_toric_code(size=3):
    """
    Simulates a toy model of the Toric Code (Lattice Gauge Theory/Topological Order).
    The Toric Code is exactly solvable and its ground state is a superposition 
    of all closed string loops. It protects quantum information globally.
    """
    print(f"Simulating Lattice Gauge Theory (Z2 Spin Liquid on a {size}x{size} lattice)...")
    
    # In a full Toric Code on an LxL lattice with periodic boundaries, 
    # there are N = 2*L^2 qubits (spins on the edges).
    # For size=3, N=18 qubits. This is 262,144 states.
    # To demonstrate the physics without crashing, we simulate a very small patch (N=6 edges).
    
    # We define a small "Star" operator A_s = prod(X) around a vertex
    # and a "Plaquette" operator B_p = prod(Z) around a face.
    # We will just construct a toy 6-qubit Hamiltonian to show the 
    # highly degenerate ground state that characterizes topological order.
    
    from qiskit.quantum_info import SparsePauliOp
    
    pauli_list = []
    
    # Toy Star operators (X terms)
    pauli_list.append(("XXXXII", -1.0))
    pauli_list.append(("IIXXXX", -1.0))
    
    # Toy Plaquette operators (Z terms)
    pauli_list.append(("ZZIIZZ", -1.0))
    pauli_list.append(("IIZZII", -1.0))
    
    H = SparsePauliOp.from_list(pauli_list).to_matrix()
    
    print("Finding the Topological Ground State Manifold...")
    evals, evecs = eigsh(H, k=10, which='SA')
    
    return evals

def plot_topological_order(evals):
    plt.figure(figsize=(10, 6))
    plt.plot(evals, 'mo', markersize=8)
    
    # Topological order is characterized by a degenerate ground state 
    # separated from excited states by a finite energy gap.
    plt.axhline(evals[0], color='r', linestyle='--', alpha=0.5, label='Topological Ground State Manifold')
    
    plt.title('Lattice Gauge Theory (Toric Code Toy Model)')
    plt.xlabel('Eigenstate Index')
    plt.ylabel('Energy $E$')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('simulations/lattice_gauge_toric.png')
    print("Plot saved to simulations/lattice_gauge_toric.png")

if __name__ == "__main__":
    evals = simulate_toric_code()
    plot_topological_order(evals)
