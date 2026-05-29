import numpy as np
import matplotlib.pyplot as plt
from scipy import sparse
from scipy.sparse.linalg import eigsh
from scipy.integrate import trapezoid

def solve_hartree_fock_1d(n_electrons=3, n_points=500, L=10, max_iter=20, tol=1e-5):
    """
    Solves a 1D multi-electron atom model using the Hartree-Fock (Self-Consistent Field) method.
    The electrons interact via a screened Coulomb-like potential in 1D.
    """
    x = np.linspace(-L, L, n_points)
    dx = x[1] - x[0]
    
    # 1. Kinetic energy matrix
    diag = np.ones(n_points)
    D2 = sparse.spdiags([diag, -2*diag, diag], [-1, 0, 1], n_points, n_points) / dx**2
    T = -0.5 * D2

    # 2. External Potential (The Nucleus, Z = n_electrons)
    # Using a softened Coulomb potential to avoid 1D singularity: -Z / sqrt(x^2 + a^2)
    Z = n_electrons
    a = 0.5 # softening parameter
    V_nuc = -Z / np.sqrt(x**2 + a**2)
    
    # 3. Initial Guess
    H_initial = T + sparse.diags(V_nuc)
    evals, evecs = eigsh(H_initial, k=n_electrons, which='SA')
    
    # Orbitals and Density
    orbitals = evecs.copy()
    density = np.sum(np.abs(orbitals)**2, axis=1)
    density *= (n_electrons / (trapezoid(density, x) + 1e-10))
    
    E_old = 0
    alpha_mix = 0.5 # Mixing parameter (Damping)
    
    print(f"Starting SCF iterations for {n_electrons}-electron atom with Damping...")

    for iteration in range(max_iter):
        # Calculate Hartree Potential from CURRENT density
        V_hartree = np.zeros_like(x)
        for i in range(n_points):
            kernel = 1.0 / np.sqrt((x[i] - x)**2 + a**2)
            V_hartree[i] = trapezoid(density * kernel, x)
            
        # Solve for new orbitals using the Hartree-Field
        H_eff = T + sparse.diags(V_nuc + V_hartree)
        evals, new_orbitals = eigsh(H_eff, k=n_electrons, which='SA')
        
        # Sort and update orbitals
        idx = evals.argsort()
        evals = evals[idx]
        new_orbitals = new_orbitals[:, idx]
        
        # Calculate NEW density
        new_density = np.sum(np.abs(new_orbitals)**2, axis=1)
        new_density *= (n_electrons / (trapezoid(new_density, x) + 1e-10))
        
        # MIX densities (Damping) to ensure stability
        # rho_next = alpha * rho_new + (1 - alpha) * rho_old
        density = alpha_mix * new_density + (1 - alpha_mix) * density
        orbitals = new_orbitals # For next step
        
        E_total = np.sum(evals)
        diff = abs(E_total - E_old)
        print(f"Iteration {iteration}: Total Energy = {E_total:.6f}, Delta = {diff:.6f}")
        
        if diff < tol:
            print("SCF Converged!")
            break
        E_old = E_total
        
    return x, evals, orbitals, density

def plot_atom(x, evals, orbitals, density, n_e):
    plt.figure(figsize=(10, 6))
    plt.plot(x, density, 'k-', lw=3, label='Total Electron Density')
    
    for i in range(n_e):
        psi_sq = np.abs(orbitals[:, i])**2
        psi_sq /= np.max(psi_sq) # Scale for visibility
        plt.fill_between(x, 0, psi_sq, alpha=0.3, label=f'Orbital {i+1} (E={evals[i]:.2f})')
        
    plt.title(f'Self-Consistent Field (Hartree-Fock) Atom with {n_e} Electrons')
    plt.xlabel('x')
    plt.ylabel('Density / Orbitals')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(f'simulations/complex_atom_{n_e}e.png')
    print(f"Plot saved to simulations/complex_atom_{n_e}e.png")

if __name__ == "__main__":
    n_e = 4 # Beryllium-like
    x, E, psi, rho = solve_hartree_fock_1d(n_electrons=n_e)
    plot_atom(x, E, psi, rho, n_e)
