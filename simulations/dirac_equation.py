import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def simulate_dirac_1d(N=400, L=20, dt=0.01, steps=500, mass=1.0):
    """
    Simulates the 1+1D Dirac Equation: i * d(psi)/dt = (-i * alpha * d/dx + beta * m) * psi
    psi is a 2-component spinor (representing particle and anti-particle components).
    alpha and beta are the Dirac matrices (Pauli matrices in 1D).
    """
    x = np.linspace(-L, L, N)
    dx = x[1] - x[0]
    
    # Stability: dt < dx
    if dt >= dx:
        dt = dx * 0.5

    # Dirac Matrices in 1D
    # alpha = sigma_x, beta = sigma_z
    alpha = np.array([[0, 1], [1, 0]])
    beta = np.array([[1, 0], [0, -1]])
    
    # Initial state: Gaussian wave packet in the "upper" component (particle)
    psi = np.zeros((N, 2), dtype=complex)
    sigma = 1.0
    x0 = -5
    p0 = 5
    psi[:, 0] = np.exp(-0.5 * ((x - x0) / sigma)**2) * np.exp(1j * p0 * x)
    
    # Normalize
    norm = np.sqrt(np.sum(np.abs(psi)**2) * dx)
    psi /= norm
    
    psi_history = []
    
    # Time evolution using a split-operator-like or central difference scheme
    # Here we use a simple finite difference for the spatial derivative
    for i in range(steps):
        # Calculate d(psi)/dx using central difference
        dpsi_dx = (np.roll(psi, -1, axis=0) - np.roll(psi, 1, axis=0)) / (2 * dx)
        
        # Hamiltonian: H * psi = -i * alpha * dpsi/dx + beta * m * psi
        # Term 1: -i * alpha * dpsi/dx
        term1 = -1j * (dpsi_dx @ alpha.T)
        # Term 2: beta * m * psi
        term2 = mass * (psi @ beta.T)
        
        H_psi = term1 + term2
        
        # Update: psi_new = psi - i * dt * H_psi
        psi = psi - 1j * dt * H_psi
        
        # Re-normalize to prevent numerical drift
        norm = np.sqrt(np.sum(np.abs(psi)**2) * dx)
        psi /= norm
        
        if i % 5 == 0:
            # Store density of particle (0) and anti-particle (1) components
            psi_history.append(np.abs(psi)**2)
            
    return x, psi_history

def animate_dirac(x, psi_history, mass):
    fig, ax = plt.subplots(figsize=(10, 6))
    line1, = ax.plot(x, psi_history[0][:, 0], label='Particle Density ($e^-$)', lw=2)
    line2, = ax.plot(x, psi_history[0][:, 1], label='Anti-particle Density ($e^+$)', lw=2, linestyle='--')
    
    ax.set_ylim(-0.1, 1.0)
    ax.set_title(f'1+1D Dirac Equation: Particle & Anti-matter (m={mass})')
    ax.set_xlabel('x')
    ax.set_ylabel('Probability Density')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    def update(frame):
        line1.set_ydata(psi_history[frame][:, 0])
        line2.set_ydata(psi_history[frame][:, 1])
        return line1, line2

    print("Simulating Relativistic Electron (Dirac Equation)...")
    ani = FuncAnimation(fig, update, frames=len(psi_history), blit=True)
    ani.save('simulations/dirac_antimatter.gif', writer='pillow', fps=30)
    plt.close()
    print("Animation saved to simulations/dirac_antimatter.gif")

if __name__ == "__main__":
    m = 2.0
    x, history = simulate_dirac_1d(mass=m, steps=600)
    animate_dirac(x, history, m)
