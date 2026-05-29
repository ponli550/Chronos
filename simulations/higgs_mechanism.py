import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import eigsh
from scipy import sparse

def simulate_higgs_mechanism(N=100, L=3.0, mu_sq=2.0, lam=1.0):
    """
    Simulates the Spontaneous Symmetry Breaking of a complex scalar field (The Higgs Mechanism).
    V(phi) = -mu^2 |phi|^2 + lambda |phi|^4
    """
    # Create a 2D grid representing the complex plane of the field phi = Re(phi) + i Im(phi)
    x = np.linspace(-L, L, N)
    dx = x[1] - x[0]
    X, Y = np.meshgrid(x, x)
    
    # 1. The "Mexican Hat" Potential
    R2 = X**2 + Y**2
    V = -mu_sq * R2 + lam * R2**2
    
    # 2. Find the Quantum Ground State of this field
    # We solve the Schrödinger equation for the field's wavefunction
    diag = np.ones(N)
    D1 = sparse.spdiags([diag, -2*diag, diag], [-1, 0, 1], N, N)
    D2 = sparse.kronsum(D1, D1) / dx**2
    T = -0.5 * D2
    
    H = T + sparse.diags(V.flatten())
    
    print("Solving for the Higgs Vacuum State...")
    evals, evecs = eigsh(H, k=3, which='SA')
    
    psi_ground = evecs[:, 0].reshape((N, N))
    
    return X, Y, V, psi_ground

def plot_higgs(X, Y, V, psi):
    fig = plt.figure(figsize=(14, 6))
    
    # 1. Plot the Mexican Hat Potential
    ax1 = fig.add_subplot(121, projection='3d')
    ax1.plot_surface(X, Y, V, cmap='coolwarm', alpha=0.8, edgecolor='none')
    ax1.set_title('The Higgs Potential (Mexican Hat)')
    ax1.set_xlabel(r'Re($\phi$)')
    ax1.set_ylabel(r'Im($\phi$)')
    ax1.set_zlabel(r'V($\phi$)')
    ax1.set_zlim(np.min(V), np.max(V)/3)
    
    # 2. Plot the Vacuum State (Spontaneous Symmetry Breaking)
    ax2 = fig.add_subplot(122)
    density = np.abs(psi)**2
    im = ax2.imshow(density, extent=[X.min(), X.max(), Y.min(), Y.max()], origin='lower', cmap='inferno')
    
    # The ground state forms a "ring" in the valley. The universe randomly picks ONE 
    # point on this ring to settle into, breaking the circular symmetry and giving particles mass.
    ax2.set_title('Quantum Vacuum State (Symmetry Broken Ring)')
    ax2.set_xlabel(r'Re($\phi$)')
    ax2.set_ylabel(r'Im($\phi$)')
    plt.colorbar(im, ax=ax2, label='Vacuum Probability Density')
    
    plt.tight_layout()
    plt.savefig('simulations/higgs_mechanism.png')
    print("Plot saved to simulations/higgs_mechanism.png")

if __name__ == "__main__":
    X, Y, V, psi = simulate_higgs_mechanism()
    plot_higgs(X, Y, V, psi)
