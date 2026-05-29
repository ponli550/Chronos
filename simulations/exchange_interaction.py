import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import trapezoid

def simulate_two_particle_exchange():
    """
    Demonstrates the effect of Spin (Exchange Interaction) on two identical particles in a 1D well.
    Bosons (Symmetric) vs Fermions (Anti-symmetric).
    """
    N = 200
    x = np.linspace(-5, 5, N)
    X1, X2 = np.meshgrid(x, x)
    
    # Ground state and first excited state wavefunctions for a single particle in a well
    # (Approximated as Hermite-Gaussians for simplicity)
    phi0 = lambda x: np.exp(-x**2 / 2)
    phi1 = lambda x: x * np.exp(-x**2 / 2)
    
    # Two particles: one in ground state (phi0), one in first excited (phi1)
    # 1. Distinguishable Particles: Psi = phi0(x1) * phi1(x2)
    psi_dist = phi0(X1) * phi1(X2)
    
    # 2. Bosons (Symmetric): Psi = 1/sqrt(2) * (phi0(x1)phi1(x2) + phi1(x1)phi0(x2))
    psi_boson = (phi0(X1) * phi1(X2) + phi1(X1) * phi0(X2)) / np.sqrt(2)
    
    # 3. Fermions (Anti-symmetric): Psi = 1/sqrt(2) * (phi0(x1)phi1(x2) - phi1(x1)phi0(x2))
    psi_fermion = (phi0(X1) * phi1(X2) - phi1(X1) * phi0(X2)) / np.sqrt(2)
    
    # Densities
    rho_dist = np.abs(psi_dist)**2
    rho_boson = np.abs(psi_boson)**2
    rho_fermion = np.abs(psi_fermion)**2
    
    # Plotting
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    titles = ['Distinguishable', 'Bosons (Symmetric)', 'Fermions (Anti-Symmetric)']
    densities = [rho_dist, rho_boson, rho_fermion]
    
    for ax, rho, title in zip(axes, densities, titles):
        im = ax.imshow(rho, extent=[-5, 5, -5, 5], origin='lower', cmap='viridis')
        ax.set_title(title)
        ax.set_xlabel('$x_1$')
        ax.set_ylabel('$x_2$')
        plt.colorbar(im, ax=ax)
        
        # Draw the x1 = x2 line
        ax.plot([-5, 5], [-5, 5], 'r--', alpha=0.5, label='$x_1 = x_2$')
        
    plt.suptitle('Exchange Interaction: Effect of Spin Statistics on Spatial Probability')
    plt.tight_layout()
    plt.savefig('simulations/exchange_interaction.png')
    print("Plot saved to simulations/exchange_interaction.png")

if __name__ == "__main__":
    simulate_two_particle_exchange()
