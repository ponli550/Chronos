import numpy as np
import matplotlib.pyplot as plt

def fermi_beta_distribution(E_kin, Q, Z, mass_electron=0.511):
    """
    Calculates the probability distribution of beta particle kinetic energy.
    E_kin: Kinetic energy of the electron (MeV)
    Q: Endpoint energy (MeV)
    Z: Atomic number of the daughter nucleus
    """
    # Total energy including rest mass
    E_total = E_kin + mass_electron
    # Momentum of the electron
    p = np.sqrt(E_total**2 - mass_electron**2)
    
    # 1. Phase Space Factor (Statistical factor)
    # P(E) ~ p * E * (Q - E_kin)^2
    phase_space = p * E_total * (Q - E_kin)**2
    
    # 2. Fermi Function F(Z, E) - Coulomb correction
    # Simplest approximation for light nuclei
    eta = (Z * (1/137.036) * E_total) / p
    # F(Z, E) = (2 * pi * eta) / (1 - exp(-2 * pi * eta))
    fermi_factor = (2 * np.pi * eta) / (1 - np.exp(-2 * np.pi * eta))
    
    return phase_space * fermi_factor

def simulate_beta_decay(isotope="Tritium"):
    """
    Predicts the beta particle spectrum for a specific isotope.
    """
    if isotope == "Tritium":
        Q = 0.0186 # 18.6 keV endpoint for Tritium
        Z = 2      # Becomes Helium-3
    elif isotope == "Carbon-14":
        Q = 0.156  # 156 keV
        Z = 7      # Becomes Nitrogen-14
    else:
        Q = 1.0
        Z = 10
        
    E_vals = np.linspace(0.001, Q - 0.001, 500)
    probabilities = [fermi_beta_distribution(e, Q, Z) for e in E_vals]
    probabilities = np.array(probabilities)
    from scipy.integrate import trapezoid
    probabilities /= trapezoid(probabilities, E_vals) # Normalize
    
    print(f"Predicting Beta Particle Spectrum for {isotope}...")
    print(f"Endpoint Energy (Q): {Q*1000:.1f} keV")
    
    plt.figure(figsize=(10, 6))
    plt.plot(E_vals * 1000, probabilities, lw=3, color='blue', label='Predicted Spectrum')
    plt.fill_between(E_vals * 1000, 0, probabilities, alpha=0.2, color='blue')
    
    # The "Harsh Truth" of Beta Decay
    # If the neutrino didn't exist, the particle would ALWAYS have energy Q (the red line).
    plt.axvline(Q * 1000, color='red', linestyle='--', label='Classical Expectation (No Neutrino)')
    
    plt.title(f'Nuclear Physics: Beta Particle Energy Spectrum ({isotope})')
    plt.xlabel('Kinetic Energy (keV)')
    plt.ylabel('Relative Probability')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.annotate('The Neutrino Evidence:\nEnergy is shared, not fixed', 
                 xy=(Q*500, np.max(probabilities)/2), 
                 xytext=(Q*600, np.max(probabilities)*0.8),
                 arrowprops=dict(facecolor='black', shrink=0.05))

    plt.savefig(f'simulations/beta_decay_{isotope}.png')
    print(f"Prediction saved to simulations/beta_decay_{isotope}.png")

if __name__ == "__main__":
    simulate_beta_decay("Tritium")
