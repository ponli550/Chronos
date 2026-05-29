import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import eigsh
from scipy import sparse

def solve_bloch_bands(n_cells=20, n_per_cell=100, V0=10, width=1.0):
    """
    Solves for the energy bands of a 1D periodic potential (Kronig-Penney-like).
    Uses Bloch's theorem by solving the TISE with periodic boundary conditions.
    """
    a = 2.0  # Lattice constant (cell width)
    x_cell = np.linspace(-a/2, a/2, n_per_cell)
    dx = x_cell[1] - x_cell[0]
    
    # Potential in one cell
    V_cell = np.zeros_like(x_cell)
    V_cell[np.abs(x_cell) < width/2] = V0
    
    # K-points in the first Brillouin zone [-pi/a, pi/a]
    k_points = np.linspace(-np.pi/a, np.pi/a, 50)
    
    all_energies = []
    
    for k in k_points:
        # Kinetic energy matrix with Bloch boundary conditions
        # The operator is (p + hbar*k)^2 / 2m
        # In position space: -1/2 * (d/dx + i*k)^2 = -1/2 * (d^2/dx^2 + 2ik*d/dx - k^2)
        
        diag = np.ones(n_per_cell)
        
        # d^2/dx^2
        D2 = sparse.spdiags([diag, -2*diag, diag], [-1, 0, 1], n_per_cell, n_per_cell)
        # Periodic BCs for D2
        D2 = D2.tocsr()
        D2[0, -1] = 1
        D2[-1, 0] = 1
        D2 /= dx**2
        
        # d/dx (central difference)
        D1 = sparse.spdiags([-0.5*diag, 0.5*diag], [-1, 1], n_per_cell, n_per_cell)
        # Periodic BCs for D1
        D1 = D1.tocsr()
        D1[0, -1] = -0.5
        D1[-1, 0] = 0.5
        D1 /= dx
        
        # Hamiltonian H_k
        H_k = -0.5 * (D2 + 2j * k * D1 - k**2 * sparse.eye(n_per_cell)) + sparse.diags(V_cell)
        
        # Solve for lowest eigenvalues
        evals = eigsh(H_k, k=4, which='SA', return_eigenvectors=False)
        all_energies.append(np.sort(evals))
        
    return k_points, np.array(all_energies)

def plot_bands(k_points, energies, a):
    plt.figure(figsize=(8, 6))
    for i in range(energies.shape[1]):
        plt.plot(k_points, energies[:, i], label=f'Band {i+1}')
        
    plt.axvline(-np.pi/a, color='k', linestyle='--')
    plt.axvline(np.pi/a, color='k', linestyle='--')
    plt.title('Energy Bands in a 1D Periodic Potential')
    plt.xlabel('Wave vector $k$')
    plt.ylabel('Energy $E$')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig('simulations/bloch_bands.png')
    print("Plot saved to simulations/bloch_bands.png")

if __name__ == "__main__":
    print("Solving Bloch Energy Bands...")
    a = 2.0
    k, E = solve_bloch_bands()
    plot_bands(k, E, a)
