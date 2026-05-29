import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import eigsh
from scipy import sparse

def solve_quark_confinement(kappa=1.0, sigma=2.0, N=1000, r_max=10):
    """
    Simulates the 'Strong Force' (QCD toy model) using a linear confinement potential.
    V(r) = -kappa/r + sigma*r
    The linear term (sigma*r) ensures quarks can never be separated.
    """
    r = np.linspace(1e-5, r_max, N)
    dr = r[1] - r[0]
    
    # Kinetic energy matrix (Radial)
    diag = np.ones(N)
    D2 = sparse.spdiags([diag, -2*diag, diag], [-1, 0, 1], N, N) / dr**2
    T = -0.5 * D2
    
    # Potential energy: Coulombic + Linear (Confinement)
    V = -kappa / r + sigma * r
    U = sparse.diags(V, 0)
    
    H = T + U
    
    print(f"Solving Quark Confinement model (sigma={sigma})...")
    evals, evecs = eigsh(H, k=5, which='SA')
    
    return r, V, evals, evecs

def plot_quarks(r, V, evals, evecs):
    from scipy.integrate import trapezoid
    plt.figure(figsize=(10, 6))
    plt.plot(r, V, 'k--', alpha=0.3, label=r'Potential $V(r) \sim \sigma r$')
    
    for i in range(len(evals)):
        u = evecs[:, i]
        u /= np.sqrt(trapezoid(u**2, r))
        plt.plot(r, u + evals[i], label=f'State {i+1} (E={evals[i]:.2f})')
        
    plt.ylim(evals[0]-2, evals[-1]+5)
    plt.xlim(0, 8)
    plt.title('Quark Confinement: Bound States in a Linear Potential')
    plt.xlabel('Distance $r$')
    plt.ylabel(r'Energy / $\psi(r) + E$')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('simulations/quark_confinement.png')
    print("Plot saved to simulations/quark_confinement.png")

if __name__ == "__main__":
    r, V, E, psi = solve_quark_confinement()
    plot_quarks(r, V, E, psi)
