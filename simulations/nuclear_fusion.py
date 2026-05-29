import numpy as np
import matplotlib.pyplot as plt

def simulate_nuclear_fusion(T_millions=15):
    """
    Simulates the probability of Nuclear Fusion (Proton-Proton) at a given temperature.
    Calculates the Gamow Factor (Tunneling Probability).
    V(r) = e^2 / (4*pi*epsilon0 * r)
    """
    # Constants (Atomic units/Relative)
    k_B = 8.617e-11 # MeV/K
    T = T_millions * 1e6
    E_avg = 1.5 * k_B * T # Average thermal energy (MeV)
    
    # Range of energies in the plasma (Maxwell-Boltzmann)
    E = np.linspace(0.001, 0.1, 1000) # MeV
    prob_thermal = E * np.exp(-E / (k_B * T))
    
    # 1. The Gamow Factor (Tunneling through Coulomb barrier)
    # P ~ exp(-sqrt(Eg / E))
    # Eg = 2 * pi^2 * Z1^2 * Z2^2 * alpha^2 * mc^2 / 2
    E_gamow = 0.491 # MeV for p-p fusion
    prob_tunnel = np.exp(-np.sqrt(E_gamow / E))
    
    # 2. The Fusion Window (Gamow Peak)
    # The actual fusion rate is the product of thermal probability and tunneling probability
    fusion_rate = prob_thermal * prob_tunnel
    
    print(f"--- Nuclear Fusion Analysis (T = {T_millions} Million K) ---")
    print(f"Average Thermal Energy: {E_avg*1000:.2f} keV")
    print(f"Gamow Peak Energy: {E[np.argmax(fusion_rate)]*1000:.2f} keV")

    plt.figure(figsize=(10, 6))
    plt.plot(E * 1000, prob_thermal / np.max(prob_thermal), label='Thermal Distribution (Maxwell-Boltzmann)', color='red')
    plt.plot(E * 1000, prob_tunnel, label='Quantum Tunneling Prob. (Gamow Factor)', color='blue', linestyle='--')
    plt.plot(E * 1000, fusion_rate / np.max(fusion_rate), label='Fusion Window (The Gamow Peak)', color='purple', lw=3)
    
    plt.fill_between(E * 1000, 0, fusion_rate / np.max(fusion_rate), color='purple', alpha=0.2)
    
    plt.title(f'Nuclear Fusion: Why Stars Burn at {T_millions}M K')
    plt.xlabel('Particle Energy (keV)')
    plt.ylabel('Relative Probability')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.annotate('The Miracle:\nQuantum Tunneling allows fusion\nat energies 100x lower than the barrier', 
                 xy=(E[np.argmax(fusion_rate)]*1000, 0.5), xytext=(20, 0.7),
                 arrowprops=dict(facecolor='black', shrink=0.05))

    plt.savefig('simulations/nuclear_fusion_gamow.png')
    print("Fusion analysis saved to simulations/nuclear_fusion_gamow.png")

if __name__ == "__main__":
    simulate_nuclear_fusion(T_millions=15) # Core of the Sun
