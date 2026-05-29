import numpy as np
import matplotlib.pyplot as plt

def simulate_muon_proof(v_over_c=0.999):
    """
    Empirical Proof of Time Dilation: The Muon Decay Experiment.
    Muons are created 10km up in the atmosphere.
    Mean lifetime (tau) = 2.2 microseconds.
    Speed (v) approx c.
    """
    # Constants
    h = 10000 # Altitude (m)
    c = 3e8   # Speed of light (m/s)
    tau = 2.2e-6 # Mean lifetime (s)
    
    v = v_over_c * c
    
    # 1. CLASSICAL PREDICTION (Newtonian)
    # Time to travel 10km
    t_travel = h / v
    # Probability of survival: P = exp(-t / tau)
    prob_classical = np.exp(-t_travel / tau)
    
    # 2. RELATIVISTIC REALITY (Einstein)
    # Time in the muon's frame is dilated: t' = t_travel / gamma
    gamma = 1.0 / np.sqrt(1 - v_over_c**2)
    t_prime = t_travel / gamma
    prob_relativistic = np.exp(-t_prime / tau)
    
    print(f"--- Empirical Proof: Muon Decay ---")
    print(f"Muon Velocity: {v_over_c}c (Gamma = {gamma:.2f})")
    print(f"Time to travel 10km (Ground Frame): {t_travel*1e6:.2f} microseconds")
    print(f"Time experienced by Muon (Dilated): {t_prime*1e6:.2f} microseconds")
    print(f"\nSurvival Probability:")
    print(f"CLASSICAL: {prob_classical*100:.6f}% (Almost zero)")
    print(f"RELATIVISTIC: {prob_relativistic*100:.2f}% (Measurable!)")

    # Visualization
    v_range = np.linspace(0.9, 0.9999, 100)
    gamma_range = 1 / np.sqrt(1 - v_range**2)
    p_rel = np.exp(-(h / (v_range * c)) / (gamma_range * tau))
    
    plt.figure(figsize=(10, 6))
    plt.plot(v_range, p_rel * 100, label='Relativistic Survival %', color='blue', lw=2)
    plt.axhline(prob_classical * 100, color='red', linestyle='--', label='Classical Prediction (~0%)')
    
    plt.plot(v_over_c, prob_relativistic * 100, 'ko')
    plt.annotate('Nature follows this line!', xy=(v_over_c, prob_relativistic*100), 
                 xytext=(v_over_c-0.05, prob_relativistic*100+10),
                 arrowprops=dict(facecolor='black', shrink=0.05))
    
    plt.title('Evidence for Relativity: Muon Survival vs Velocity')
    plt.xlabel('Velocity (Fraction of c)')
    plt.ylabel('Percentage of Muons reaching the Ground')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.savefig('simulations/muon_decay_proof.png')
    print("\nNumerical proof saved to simulations/muon_decay_proof.png")

if __name__ == "__main__":
    simulate_muon_proof()
