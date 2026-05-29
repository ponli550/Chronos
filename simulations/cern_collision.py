import numpy as np
import matplotlib.pyplot as plt

def simulate_lhc_event(energy_tev=13.6, n_particles=50):
    """
    Simulates a 'Toy' CERN LHC collision event.
    Proton-Proton collision resulting in 'Jets' of particles.
    """
    # 1. Collision Point (The Interaction Point)
    origin = np.array([0, 0, 0])
    
    # 2. Generate 'Jets' (Groups of particles moving in similar directions)
    # Most collisions at CERN produce 2 or 3 high-energy jets.
    n_jets = np.random.randint(2, 5)
    particle_data = []

    print(f"Simulating LHC Collision Event at {energy_tev} TeV ({n_jets} jets)...")

    for j in range(n_jets):
        # Pick a random direction for the jet (Theta, Phi)
        jet_theta = np.random.uniform(0.1*np.pi, 0.9*np.pi) # Avoid beam pipe
        jet_phi = np.random.uniform(0, 2*np.pi)
        
        # Jet direction vector
        jet_dir = np.array([
            np.sin(jet_theta) * np.cos(jet_phi),
            np.sin(jet_theta) * np.sin(jet_phi),
            np.cos(jet_theta)
        ])
        
        # Particles within the jet
        particles_in_jet = n_particles // n_jets
        for p in range(particles_in_jet):
            # Each particle has momentum P = P_jet + small_random_kick
            momentum_mag = np.random.exponential(energy_tev * 10) # Simple energy dist
            
            # Angular spread of the jet (conical)
            spread = 0.15
            p_dir = jet_dir + np.random.normal(0, spread, 3)
            p_dir /= np.linalg.norm(p_dir)
            
            momentum = momentum_mag * p_dir
            
            # Particle properties (Simplified: ID, Momentum)
            particle_data.append({
                'p': momentum,
                'id': np.random.choice(['pion', 'kaon', 'muon', 'photon']),
                'energy': momentum_mag
            })

    return particle_data

def plot_cern_event(particles):
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Color mapping for different particle types
    colors = {'pion': 'blue', 'kaon': 'green', 'muon': 'red', 'photon': 'orange'}
    
    for part in particles:
        p = part['p']
        # Draw a line representing the particle track
        # (LHC detectors track these curved paths)
        ax.plot([0, p[0]], [0, p[1]], [0, p[2]], 
                color=colors[part['id']], alpha=0.6, lw=1)
        
    ax.set_title('LHC Event Simulation: Particle Jets from p-p Collision')
    ax.set_xlabel('X (GeV)')
    ax.set_ylabel('Y (GeV)')
    ax.set_zlabel('Z (GeV)')
    
    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], color=c, lw=2, label=name) for name, c in colors.items()]
    ax.legend(handles=legend_elements)
    
    # Set limits to see the "Interaction Point" at center
    lim = 150
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_zlim(-lim, lim)
    
    plt.savefig('simulations/cern_lhc_event.png')
    print("Plot saved to simulations/cern_lhc_event.png")

if __name__ == "__main__":
    event = simulate_lhc_event()
    plot_cern_event(event)
