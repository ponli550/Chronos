import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import eigsh
from scipy import sparse

def simulate_mbl(L=12, disorder_strength=10.0):
    """
    Simulates Many-Body Localization in a 1D Spin Chain.
    We look at the 'Level Statistics' to see if the system is Ergodic or Localized.
    H = sum_i (Z_i Z_{i+1} + h_i Z_i + g X_i)
    h_i is random disorder.
    """
    from qiskit.quantum_info import SparsePauliOp
    
    # 1. Construct the disordered Hamiltonian
    pauli_list = []
    # Interaction: Z_i Z_{i+1}
    for i in range(L - 1):
        chars = ['I'] * L
        chars[i] = 'Z'
        chars[i+1] = 'Z'
        pauli_list.append(("".join(chars[::-1]), 1.0))
        
    # Transverse Field: g X_i
    g = 0.5
    for i in range(L):
        chars = ['I'] * L
        chars[i] = 'X'
        pauli_list.append(("".join(chars[::-1]), g))
        
    # Disorder: h_i Z_i (Random field)
    h_vals = np.random.uniform(-disorder_strength, disorder_strength, L)
    for i in range(L):
        chars = ['I'] * L
        chars[i] = 'Z'
        pauli_list.append(("".join(chars[::-1]), h_vals[i]))
        
    H = SparsePauliOp.from_list(pauli_list).to_matrix()
    
    print(f"Solving {L}-site MBL chain (Matrix size: {2**L}x{2**L})...")
    evals = np.linalg.eigvalsh(H)
    
    # 2. Level Statistics: r-parameter
    # r = min(delta_n, delta_{n+1}) / max(delta_n, delta_{n+1})
    diffs = np.diff(evals)
    r_vals = []
    for i in range(len(diffs) - 1):
        r = min(diffs[i], diffs[i+1]) / max(diffs[i], diffs[i+1])
        r_vals.append(r)
        
    mean_r = np.mean(r_vals)
    return evals, r_vals, mean_r

def plot_mbl(evals, r_vals, mean_r, W):
    plt.figure(figsize=(10, 6))
    plt.hist(r_vals, bins=30, density=True, alpha=0.6, color='purple')
    
    # Theoretical limits
    # Poisson (Localized): r approx 0.386
    # GOE (Ergodic): r approx 0.531
    plt.axvline(0.386, color='r', linestyle='--', label='Poisson (Localized, r=0.386)')
    plt.axvline(0.531, color='g', linestyle='--', label='GOE (Ergodic, r=0.531)')
    plt.axvline(mean_r, color='k', lw=2, label=f'System Mean r={mean_r:.3f}')
    
    plt.title(f'Many-Body Localization: Level Statistics (Disorder W={W})')
    plt.xlabel('Level Spacing Ratio $r$')
    plt.ylabel('Probability Density')
    plt.legend()
    plt.grid(True, alpha=0.2)
    plt.savefig(f'simulations/mbl_statistics_W{W}.png')
    print(f"MBL stats saved to simulations/mbl_statistics_W{W}.png")

if __name__ == "__main__":
    # Test Ergodic (Low disorder)
    print("Simulating Ergodic Phase...")
    e1, r1, m1 = simulate_mbl(L=10, disorder_strength=0.5)
    plot_mbl(e1, r1, m1, 0.5)
    
    # Test MBL (High disorder)
    print("\nSimulating MBL Phase...")
    e2, r2, m2 = simulate_mbl(L=10, disorder_strength=15.0)
    plot_mbl(e2, r2, m2, 15.0)
