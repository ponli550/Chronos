import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import eigh

def solve_kitaev_chain(n_sites=40, t=1.0, delta=1.0, mu=0.0):
    """
    Simulates the Kitaev Chain: a 1D p-wave superconductor.
    H = sum_j [ -t (c_j_dag c_{j+1} + h.c.) - mu (c_j_dag c_j - 1/2) 
               + delta (c_j c_{j+1} + h.c.) ]
    If mu < 2t, the system has Majorana Zero Modes at the edges.
    Using the Bogoliubov-de Gennes (BdG) formalism.
    """
    # Matrix size is 2*n_sites (particle-hole space)
    dim = 2 * n_sites
    H = np.zeros((dim, dim), dtype=complex)
    
    for i in range(n_sites):
        # On-site chemical potential (Particle and Hole diagonals)
        H[i, i] = -mu
        H[i + n_sites, i + n_sites] = mu
        
        if i < n_sites - 1:
            # Hopping t
            H[i, i + 1] = -t
            H[i + 1, i] = -t
            H[i + n_sites, i + n_sites + 1] = t
            H[i + n_sites + 1, i + n_sites] = t
            
            # Superconducting Pairing delta
            H[i, i + n_sites + 1] = delta
            H[i + 1, i + n_sites] = -delta
            H[i + n_sites + 1, i] = delta
            H[i + n_sites, i + 1] = -delta
            
    evals, evecs = eigh(H)
    return evals, evecs

def plot_majoranas(evals, evecs, n_sites):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # 1. Energy Spectrum
    ax1.plot(evals, 'ko', markersize=4)
    ax1.set_title('Kitaev Chain Spectrum (Topological Phase)')
    ax1.set_ylabel('Energy $E$')
    ax1.set_xlabel('State Index')
    ax1.grid(True, alpha=0.3)
    
    # Highlight the Majorana Zero Modes
    zero_idx = np.where(np.abs(evals) < 1e-5)[0]
    if len(zero_idx) > 0:
        ax1.plot(zero_idx, evals[zero_idx], 'ro', label='Majorana Zero Modes')
        ax1.legend()
        
        # 2. Visualize the Spatial Distribution of a Majorana Mode
        # The mode is spread across particle and hole components
        # Majorana operator gamma = sum_j (u_j c_j + v_j c_j_dag)
        # We plot |u_j|^2 + |v_j|^2
        mode_idx = zero_idx[len(zero_idx)//2]
        u = evecs[:n_sites, mode_idx]
        v = evecs[n_sites:, mode_idx]
        density = np.abs(u)**2 + np.abs(v)**2
        
        ax2.bar(range(n_sites), density, color='purple', alpha=0.7)
        ax2.set_title('Spatial Distribution of a Majorana Zero Mode')
        ax2.set_xlabel('Site Index $j$')
        ax2.set_ylabel('$|u_j|^2 + |v_j|^2$')
    
    plt.savefig('simulations/majorana_fermions.png')
    print("Plot saved to simulations/majorana_fermions.png")

if __name__ == "__main__":
    # Topological Phase: mu < 2t
    sites = 40
    E, psi = solve_kitaev_chain(n_sites=sites, t=1.0, delta=1.0, mu=0.5)
    plot_majoranas(E, psi, sites)
