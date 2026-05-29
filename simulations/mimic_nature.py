import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from simulations.qho import solve_qho_1d

def mimic_nature_emergence(n_detections=2000):
    """
    Mimics the 'Nature' experience: we don't see the wavefunction, 
    we see discrete 'detections' (dots) that eventually reveal the quantum pattern.
    Example: 1D Quantum Harmonic Oscillator (n=3 state)
    """
    # 1. Get the "Source Code" (Wavefunction)
    omega = 1.0
    x, evals, evecs = solve_qho_1d(n_points=1000, x_max=6, omega=omega)
    
    # Let's pick the n=3 state (3rd excited) for a complex pattern
    n_state = 3
    psi = evecs[:, n_state]
    prob_density = np.abs(psi)**2
    prob_density /= np.sum(prob_density) # Normalize for sampling
    
    # 2. Mimic Nature's "Measurement": Sample discrete points
    # This is like an electron hitting a screen one by one
    detections = np.random.choice(x, size=n_detections, p=prob_density)
    
    # Setup plotting
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), height_ratios=[1, 2])
    
    # Bottom plot: Individual detections (the "experienced" nature)
    ax2.set_xlim(-4, 4)
    ax2.set_ylim(0, 0.1) # Small scatter
    dots, = ax2.plot([], [], 'ro', markersize=2, alpha=0.5, label='Detected Electrons')
    ax2.set_title(f'Nature as Experienced: Discrete Particle Detections ($n={n_state}$)')
    ax2.set_xlabel('Position $x$')
    ax2.legend()
    
    # Top plot: Emerging Histogram (the "revealed" physics)
    bins = np.linspace(-4, 4, 50)
    counts = np.zeros(len(bins)-1)
    bar_container = ax1.bar(bins[:-1], counts, width=np.diff(bins), 
                            align='edge', color='blue', alpha=0.3, label='Emergent Pattern')
    ax1.plot(x, prob_density * (n_detections/10), 'k--', label=r'Theoretical $|\psi|^2$ (The "Source Code")')
    ax1.set_xlim(-4, 4)
    ax1.set_title('Nature as Calculated: Emergent Probability Density')
    ax1.legend()

    x_data = []
    y_data = []

    def update(frame):
        # Add a new detection
        new_x = detections[frame]
        x_data.append(new_x)
        y_data.append(np.random.uniform(0, 0.08)) # Random height for scatter visibility
        
        dots.set_data(x_data, y_data)
        
        # Update histogram every 10 frames
        if frame % 10 == 0:
            hist, _ = np.histogram(x_data, bins=bins)
            for count, rect in zip(hist, bar_container):
                rect.set_height(count)
                
        return dots, *bar_container

    print(f"Mimicking Nature's emergence with {n_detections} events...")
    ani = FuncAnimation(fig, update, frames=n_detections, interval=1, blit=True)
    
    # Save a representative frame and the animation
    plt.savefig('simulations/nature_emergence_final.png')
    try:
        # Saving only first 500 frames for speed/size
        ani.save('simulations/nature_emergence.gif', writer='pillow', fps=40, frames=500)
        print("Animation saved to simulations/nature_emergence.gif")
    except:
        print("Animation save failed, static image preserved.")
    
    plt.close()

if __name__ == "__main__":
    mimic_nature_emergence()
