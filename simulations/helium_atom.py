import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

def helium_ground_state_variational():
    """
    Estimates the ground state energy of the Helium atom using the Variational Method.
    Trial wavefunction: psi(r1, r2) = (Z_eff^3 / pi) * exp(-Z_eff * (r1 + r2))
    Units: Atomic units (Energy in Hartrees)
    """
    
    def energy_functional(Z_eff):
        """
        Energy E(Z_eff) = <psi|H|psi> / <psi|psi>
        For Helium (Z=2):
        E(Z_eff) = Z_eff^2 - 2*Z*Z_eff + (5/8)*Z_eff
        """
        Z = 2.0
        # Kinetic energy: Z_eff^2
        # Nucleus-Electron potential: -2 * Z * Z_eff
        # Electron-Electron repulsion: (5/8) * Z_eff
        E = Z_eff**2 - 2 * Z * Z_eff + (5/8) * Z_eff
        return E

    # Initial guess for Z_eff (Z=2)
    initial_guess = 2.0
    res = minimize(energy_functional, initial_guess)
    
    Z_eff_opt = res.x[0]
    E_min = res.fun
    
    return Z_eff_opt, E_min

if __name__ == "__main__":
    Z_eff, E_min = helium_ground_state_variational()
    
    # Experimental ground state energy of Helium is approx -2.903 Hartrees
    E_exp = -2.9033
    
    print("--- Helium Ground State (Variational Method) ---")
    print(f"Optimal Effective Charge (Z_eff): {Z_eff:.4f}")
    print(f"Calculated Energy: {E_min:.4f} Hartrees")
    print(f"Experimental Energy: {E_exp:.4f} Hartrees")
    print(f"Error: {abs(E_min - E_exp)/abs(E_exp)*100:.2f}%")
    
    # Plot E(Z_eff)
    Z_vals = np.linspace(1.0, 2.5, 100)
    E_vals = [Z**2 - 2*2.0*Z + (5/8)*Z for Z in Z_vals]
    
    plt.figure(figsize=(8, 6))
    plt.plot(Z_vals, E_vals, label='$E(Z_{eff})$')
    plt.plot(Z_eff, E_min, 'ro', label=f'Minimum: $Z_{{eff}}={Z_eff:.3f}$')
    plt.axhline(E_exp, color='g', linestyle='--', label='Experimental Energy')
    plt.title('Variational Principle for Helium Ground State')
    plt.xlabel('Effective Nuclear Charge $Z_{eff}$')
    plt.ylabel('Energy (Hartrees)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('simulations/helium_variational.png')
    print(f"Plot saved to simulations/helium_variational.png")
