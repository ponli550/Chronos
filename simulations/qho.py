import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh
import matplotlib.pyplot as plt
from scipy.integrate import trapezoid

def solve_qho_1d(n_points=1000, x_max=10, omega=1.0):
    """
    Solves the 1D Quantum Harmonic Oscillator Schrodinger equation.
    Units: Atomic units (hbar = m = 1)
    """
    x = np.linspace(-x_max, x_max, n_points)
    dx = x[1] - x[0]

    # Kinetic energy matrix (2nd derivative)
    diag = np.ones(n_points)
    diags = np.array([-2*diag, diag, diag])
    D2 = sparse.spdiags(diags, [0, -1, 1], n_points, n_points) / dx**2
    T = -0.5 * D2

    # Potential energy matrix V(x) = 1/2 * m * omega^2 * x^2
    V = 0.5 * (omega**2) * (x**2)
    U = sparse.diags(V, 0)

    # Hamiltonian
    H = T + U

    # Solve for eigenvalues and eigenvectors
    evals, evecs = eigsh(H, k=6, which='SA')
    
    return x, evals, evecs

def plot_qho(x, evals, evecs, omega):
    plt.figure(figsize=(10, 8))
    
    # Sort evals and evecs
    idx = evals.argsort()
    evals = evals[idx]
    evecs = evecs[:, idx]

    # Plot potential
    V = 0.5 * (omega**2) * (x**2)
    plt.plot(x, V, 'k--', label='Potential $V(x)$', alpha=0.5)

    for i in range(len(evals)):
        psi = evecs[:, i]
        # Normalize
        norm = np.sqrt(trapezoid(psi**2, x))
        psi = psi / norm
        
        # Shift wavefunction by its energy for visualization
        plt.plot(x, psi + evals[i], label=f'n={i} (E={evals[i]:.3f})')
        plt.axhline(evals[i], color='gray', linestyle='--', alpha=0.3)

    plt.title('1D Quantum Harmonic Oscillator Wavefunctions')
    plt.xlabel('x')
    plt.ylabel(r'Energy / $\psi(x) + E$')
    plt.ylim(-0.5, evals.max() + 1.5)
    plt.xlim(-6, 6)
    plt.legend()
    plt.grid(True, alpha=0.2)
    plt.savefig('simulations/qho_1d.png')
    print(f"Plot saved to simulations/qho_1d.png")

if __name__ == "__main__":
    omega = 1.0
    x, evals, evecs = solve_qho_1d(omega=omega)
    
    print(f"Solving 1D QHO with omega = {omega}...")
    for n, e in enumerate(evals):
        e_theory = omega * (n + 0.5)
        print(f"n={n}: Numerical E = {e:.6f}, Theoretical E = {e_theory:.6f}")
    
    plot_qho(x, evals, evecs, omega)
