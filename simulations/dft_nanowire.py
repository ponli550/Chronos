import numpy as np
import matplotlib.pyplot as plt
from scipy import sparse
from scipy.sparse.linalg import eigsh
from scipy.integrate import trapezoid

def solve_dft_1d(n_electrons=6, n_points=600, L=15, max_iter=30, tol=1e-6):
    """
    Solves for a 1D 'Quantum Nanowire' (Atomic Chain) using Density Functional Theory (DFT).
    Includes the Local Density Approximation (LDA) for Exchange-Correlation.
    """
    x = np.linspace(-L, L, n_points)
    dx = x[1] - x[0]
    
    # 1. Kinetic Energy
    e = np.ones(n_points)
    T = -0.5 * sparse.spdiags([e, -2*e, e], [-1, 0, 1], n_points, n_points) / dx**2

    # 2. External Potential: A chain of atoms (Z=1 each)
    # Positions of atoms
    atom_pos = np.array([-4, -2, 0, 2, 4])
    V_ext = np.zeros_like(x)
    soft_a = 0.6
    for pos in atom_pos:
        V_ext -= 1.0 / np.sqrt((x - pos)**2 + soft_a**2)
    
    # 3. LDA Exchange-Correlation Functional (Toy 1D version)
    def get_v_xc(rho):
        # Local Density Approximation for 1D exchange
        # V_xc approx -rho^(1/3)
        return - (3/np.pi * rho)**(1/3)

    # Initial Guess: uniform density
    rho = np.ones_like(x) * (n_electrons / (2 * L))
    
    E_old = 0
    alpha = 0.4 # Mixing (Damping)
    
    print(f"Starting DFT iterations for {len(atom_pos)}-atom chain ({n_electrons} electrons)...")

    for i in range(max_iter):
        # Hartree Potential (Repulsion)
        V_h = np.zeros_like(x)
        for j in range(n_points):
            kernel = 1.0 / np.sqrt((x[j] - x)**2 + soft_a**2)
            V_h[j] = trapezoid(rho * kernel, x)
            
        # Exchange-Correlation Potential
        V_xc = get_v_xc(rho)
        
        # Total Kohn-Sham Hamiltonian
        H_ks = T + sparse.diags(V_ext + V_h + V_xc)
        
        # Solve for Orbitals (Occupying n_electrons/2 spatial levels due to spin)
        n_levels = int(np.ceil(n_electrons / 2))
        evals, evecs = eigsh(H_ks, k=n_levels, which='SA')
        
        # New Density
        new_rho = np.zeros_like(x)
        for n in range(n_levels):
            occ = 2 if n < n_electrons // 2 else (n_electrons % 2)
            new_rho += occ * np.abs(evecs[:, n])**2
        
        new_rho *= (n_electrons / (trapezoid(new_rho, x) + 1e-10))
        
        # Convergence check
        E_total = np.sum(evals)
        if abs(E_total - E_old) < tol:
            print(f"DFT Converged at iteration {i}!")
            break
            
        # Update density with mixing
        rho = alpha * new_rho + (1 - alpha) * rho
        E_old = E_total
        if i % 5 == 0:
            print(f"Iteration {i}: Energy = {E_total:.6f}")

    return x, evals, evecs, rho, V_ext

def plot_dft(x, evals, orbitals, rho, V_ext):
    plt.figure(figsize=(12, 6))
    plt.plot(x, V_ext, 'k--', alpha=0.2, label='Atomic Potential (Nuclei)')
    plt.plot(x, rho, 'r-', lw=2, label='Total Electron Density (DFT)')
    
    # Fill orbitals
    for i in range(orbitals.shape[1]):
        plt.fill_between(x, 0, np.abs(orbitals[:,i])**2 * 5, alpha=0.2, label=f'KS-Orbital {i+1}')
        
    plt.title('DFT Simulation of a 1D Quantum Nanowire (5 Atoms)')
    plt.xlabel('Position $x$')
    plt.ylabel('Density / Potential')
    plt.legend(loc='upper right', fontsize='small')
    plt.grid(True, alpha=0.3)
    plt.savefig('simulations/dft_nanowire.png')
    print("Plot saved to simulations/dft_nanowire.png")

if __name__ == "__main__":
    x, E, psi, rho, V = solve_dft_1d()
    plot_dft(x, E, psi, rho, V)
