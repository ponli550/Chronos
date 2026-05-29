import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import eigh

def solve_ssh_model(n_cells=20, v=0.6, w=1.0):
    """
    Simulates the Su-Schrieffer-Heeger (SSH) model of a 1D topological insulator.
    H = sum_n (v * |n,A><n,B| + w * |n,B><n+1,A| + h.c.)
    v: intra-cell hopping, w: inter-cell hopping
    If |v| < |w|, the system is Topological and has Edge States.
    """
    n_sites = 2 * n_cells
    H = np.zeros((n_sites, n_sites))
    
    for i in range(n_cells):
        # Intra-cell hopping (A-B)
        H[2*i, 2*i + 1] = v
        H[2*i + 1, 2*i] = v
        
        # Inter-cell hopping (B-A)
        if i < n_cells - 1:
            H[2*i + 1, 2*i + 2] = w
            H[2*i + 2, 2*i + 1] = w
            
    evals, evecs = eigh(H)
    return evals, evecs

def plot_ssh(evals, evecs, v, w):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # 1. Energy Spectrum
    ax1.plot(evals, 'ko', markersize=4)
    ax1.set_title(f'SSH Spectrum (v={v}, w={w})')
    ax1.set_ylabel('Energy $E$')
    ax1.set_xlabel('State Index')
    ax1.grid(True, alpha=0.3)
    
    # Highlight the zero-energy edge states if they exist
    zero_idx = np.where(np.abs(evals) < 1e-5)[0]
    if len(zero_idx) > 0:
        ax1.plot(zero_idx, evals[zero_idx], 'ro', label='Topological Edge States')
        ax1.legend()
        
        # 2. Visualize an Edge State
        edge_state = np.abs(evecs[:, zero_idx[0]])**2
        ax2.bar(range(len(edge_state)), edge_state, color='red', alpha=0.6)
        ax2.set_title('Spatial Density of an Edge State')
        ax2.set_xlabel('Site Index')
        ax2.set_ylabel('$|\psi|^2$')
        ax2.set_ylim(0, np.max(edge_state)*1.2)
    else:
        ax2.text(0.5, 0.5, 'Trivial Phase (No Edge States)', ha='center')
        
    plt.savefig(f'simulations/ssh_topology_v{v}_w{w}.png')
    print(f"Plot saved to simulations/ssh_topology_v{v}_w{w}.png")

if __name__ == "__main__":
    # Topological Phase (v < w)
    print("Simulating Topological Phase (v < w)...")
    evals_topo, evecs_topo = solve_ssh_model(v=0.4, w=1.0)
    plot_ssh(evals_topo, evecs_topo, 0.4, 1.0)
    
    # Trivial Phase (v > w)
    # print("Simulating Trivial Phase (v > w)...")
    # evals_triv, evecs_triv = solve_ssh_model(v=1.2, w=0.5)
    # plot_ssh(evals_triv, evecs_triv, 1.2, 0.5)
