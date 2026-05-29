import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import eigsh
from scipy import sparse

def solve_susy_qm(N=1000, L=5):
    """
    Simulates Supersymmetric Quantum Mechanics (SUSY QM).
    H_minus = A_dag A, H_plus = A A_dag
    These two Hamiltonians share identical spectra (except for the ground state).
    """
    x = np.linspace(-L, L, N)
    dx = x[1] - x[0]
    
    # Superpotential W(x)
    # Example: Harmonic Oscillator W(x) = x
    W = x
    dW_dx = np.ones_like(x)
    
    # Hamiltonian components
    # H_minus = -1/2 * d^2/dx^2 + 1/2 * (W^2 - dW/dx)
    # H_plus  = -1/2 * d^2/dx^2 + 1/2 * (W^2 + dW/dx)
    
    diag = np.ones(N)
    D2 = sparse.spdiags([diag, -2*diag, diag], [-1, 0, 1], N, N) / dx**2
    T = -0.5 * D2
    
    V_minus = 0.5 * (W**2 - dW_dx)
    V_plus  = 0.5 * (W**2 + dW_dx)
    
    H_minus = T + sparse.diags(V_minus)
    H_plus  = T + sparse.diags(V_plus)
    
    print("Solving SUSY Partner Hamiltonians...")
    evals_m, evecs_m = eigsh(H_minus, k=5, which='SA')
    evals_p, evecs_p = eigsh(H_plus, k=4, which='SA') # H_plus has one less state
    
    return evals_m, evals_p

def plot_susy(evals_m, evals_p):
    plt.figure(figsize=(10, 6))
    
    # Plot Energy levels
    plt.plot(np.zeros_like(evals_m), evals_m, 'bo', label='H- Spectrum (Bosonic)')
    plt.plot(np.ones_like(evals_p), evals_p, 'ro', label='H+ Spectrum (Fermionic)')
    
    # Connect degenerate levels
    for i in range(len(evals_p)):
        plt.plot([0, 1], [evals_m[i+1], evals_p[i]], 'k--', alpha=0.3)
        
    plt.title('Supersymmetric Quantum Mechanics: Spectrum Pairing')
    plt.ylabel('Energy $E$')
    plt.xticks([0, 1], ['Boson (Partner -)', 'Fermion (Partner +)'])
    plt.legend()
    plt.grid(True, alpha=0.2)
    plt.savefig('simulations/susy_spectrum.png')
    print("Plot saved to simulations/susy_spectrum.png")

if __name__ == "__main__":
    em, ep = solve_susy_qm()
    print(f"H- Energies: {em}")
    print(f"H+ Energies: {ep}")
    plot_susy(em, ep)
