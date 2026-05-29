import numpy as np
import matplotlib.pyplot as plt

def simulate_berry_phase(t_max=10.0, steps=1000):
    """
    Simulates the Berry Phase (Geometric Phase) in a 2-level system.
    We rotate a magnetic field in a circle and watch the wavefunction 
    acquire a phase that depends only on the geometry (solid angle).
    """
    # Time grid
    t = np.linspace(0, t_max, steps)
    dt = t[1] - t[0]
    
    # Path in parameter space (a circle on the Bloch sphere)
    # Theta (tilt) is constant, Phi (rotation) goes from 0 to 2*pi
    theta = np.pi / 4 # 45 degrees
    phi = 2 * np.pi * t / t_max
    
    # Hamiltonian: H(t) = B(t) . sigma
    # B = (sin(theta)cos(phi), sin(theta)sin(phi), cos(theta))
    def get_H(p):
        Bx = np.sin(theta) * np.cos(p)
        By = np.sin(theta) * np.sin(p)
        Bz = np.cos(theta)
        return 0.5 * np.array([[Bz, Bx - 1j*By], [Bx + 1j*By, -Bz]])

    # Initial state: Instantaneous ground state of H(0)
    H0 = get_H(0)
    evals, evecs = np.linalg.eigh(H0)
    psi = evecs[:, 0] # Start in ground state
    
    phases = []
    dynamic_phases = []
    
    for i in range(steps):
        H = get_H(phi[i])
        
        # Time evolution: psi(t+dt) = exp(-i*H*dt) * psi(t)
        # Using a simple matrix exponential for precision
        from scipy.linalg import expm
        U = expm(-1j * H * dt)
        psi = U @ psi
        
        # Track total phase
        # Phase = Arg(psi[0])
        phases.append(np.angle(psi[0]))
        
        # Calculate expected Dynamic Phase: integral E(t) dt
        # For this setup, E = -0.5 (ground state energy is constant)
        dynamic_phases.append(-(-0.5 * t[i]))

    phases = np.array(phases)
    dynamic_phases = np.array(dynamic_phases)
    
    # The Berry Phase is the Total Phase minus the Dynamic Phase
    berry_phase_evol = phases - dynamic_phases
    # Wrap to [-pi, pi]
    berry_phase_evol = (berry_phase_evol + np.pi) % (2 * np.pi) - np.pi

    plt.figure(figsize=(10, 6))
    plt.plot(t, phases, label='Total Phase')
    plt.plot(t, dynamic_phases, '--', label='Dynamic Phase (Expected)')
    plt.plot(t, berry_phase_evol, label='Emergent Berry Phase (Geometric)')
    
    plt.title(r'Geometric Law: The Berry Phase ($\theta = \pi/4$)')
    plt.xlabel('Time (Rotation)')
    plt.ylabel('Phase (radians)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('simulations/berry_phase.png')
    print(f"Plot saved to simulations/berry_phase.png")
    print(f"Final Geometric Phase: {berry_phase_evol[-1]:.4f} rad")
    print(f"Theoretical Berry Phase (Solid Angle): {-np.pi * (1 - np.cos(theta)):.4f} rad")

if __name__ == "__main__":
    simulate_berry_phase()
