import numpy as np
import matplotlib.pyplot as plt

def simulate_maxwell_demon(n_particles=100, steps=1000):
    """
    Simulates Maxwell's Demon: A microscopic entity that sorts particles by speed.
    This reduces entropy without apparent work.
    We track Entropy and the 'Information Cost' to save the 2nd Law.
    """
    # Initialize particles in two boxes (Left and Right)
    # v_x follows a Maxwell-Boltzmann distribution
    velocities = np.random.normal(0, 1.0, n_particles)
    positions = np.zeros(n_particles) # 0 for Left, 1 for Right
    
    # Half on left, half on right
    positions[n_particles//2:] = 1
    
    entropy_history = []
    info_cost_history = []
    
    current_info_bits = 0

    print(f"Maxwell's Demon starting the sort of {n_particles} particles...")

    for i in range(steps):
        # 1. Calculate Entropy: S = -sum(p * log(p))
        # Based on temperature (variance of velocities) in each box
        v_left = velocities[positions == 0]
        v_right = velocities[positions == 1]
        
        # Approximate entropy as the variance (T) log
        s_left = np.log(np.var(v_left) + 1e-5) if len(v_left) > 0 else 0
        s_right = np.log(np.var(v_right) + 1e-5) if len(v_right) > 0 else 0
        total_s = (s_left + s_right)
        entropy_history.append(total_s)
        
        # 2. THE DEMON'S ACTION: Sort a random particle
        # If speed > average, move to Right box. If speed < average, move to Left box.
        idx = np.random.randint(0, n_particles)
        v = velocities[idx]
        
        # The demon MUST know the speed (Information Acquisition)
        current_info_bits += 1 # 1 bit of info used to sort
        info_cost_history.append(current_info_bits * 0.01) # Scale to match S units
        
        if v > 0: # Fast
            positions[idx] = 1 # Move to Right
        else: # Slow
            positions[idx] = 0 # Move to Left

    plt.figure(figsize=(10, 6))
    plt.plot(entropy_history, color='blue', label='Physical Entropy (Decreasing!)')
    plt.plot(info_cost_history, color='red', label='Information Entropy (Landauer Cost)')
    
    # The Total Entropy (Physical + Information) never decreases
    total_entropy = np.array(entropy_history) + np.array(info_cost_history)
    plt.plot(total_entropy, color='black', lw=2, label='Total Entropy (Physical + Info)')
    
    plt.title("Maxwell's Demon: Information as Fuel for the 2nd Law")
    plt.xlabel('Demon Sorting Actions')
    plt.ylabel('Entropy $S$ / Information $I$')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.annotate('Violation?', xy=(200, entropy_history[200]), xytext=(300, entropy_history[200]-2),
                 arrowprops=dict(facecolor='blue', shrink=0.05))
    plt.annotate('Saved by Landauer!', xy=(500, total_entropy[500]), xytext=(100, total_entropy[500]+2),
                 arrowprops=dict(facecolor='black', shrink=0.05))

    plt.savefig('simulations/maxwell_demon.png')
    print("Plot saved to simulations/maxwell_demon.png")

if __name__ == "__main__":
    simulate_maxwell_demon()
