import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def simulate_hawking_radiation(N=512, L=20, dt=0.01, steps=800):
    """
    Simulates a toy model of Hawking Radiation.
    We create a vacuum fluctuation (particle-antiparticle pair) near a Horizon.
    The 'Negative Energy' partner is sucked in, while the 'Positive' partner escapes.
    """
    x = np.linspace(-L, L, N)
    dx = x[1] - x[0]
    
    # Horizon position at x = 0
    # Potential: Attraction towards the left (inside BH)
    V = np.zeros_like(x)
    V[x < 0] = -5.0 * np.exp(x[x < 0]) # Gravitational pull towards the singularity
    
    # Initial state: A fluctuation at the horizon (x=0)
    # Represented as two Gaussian packets with opposite momentum
    sigma = 0.5
    # Particle (moving right/escape)
    psi_p = np.exp(-(x - 0.2)**2 / (2 * sigma**2)) * np.exp(1j * 5.0 * x)
    # Anti-particle (moving left/in)
    psi_a = np.exp(-(x + 0.2)**2 / (2 * sigma**2)) * np.exp(-1j * 5.0 * x)
    
    psi = (psi_p + psi_a).astype(complex)
    psi /= np.sqrt(np.sum(np.abs(psi)**2) * dx)
    
    psi_history = []
    
    print("Simulating Hawking Radiation (Horizon at x=0)...")
    
    # Momentum space
    k = np.fft.fftfreq(N, d=dx) * 2 * np.pi
    k2 = k**2
    
    for i in range(steps):
        # Split-Step Fourier
        psi *= np.exp(-0.5j * V * dt)
        psi_k = np.fft.fft(psi)
        psi_k *= np.exp(-0.5j * k2 * dt)
        psi = np.fft.ifft(psi_k)
        psi *= np.exp(-0.5j * V * dt)
        
        if i % 10 == 0:
            psi_history.append(np.abs(psi)**2)
            
    return x, V, psi_history

def animate_hawking(x, V, history):
    fig, ax = plt.subplots(figsize=(10, 6))
    line, = ax.plot(x, history[0], color='orange', lw=2, label='Quantum Fluctuation')
    
    # Draw the Event Horizon
    ax.axvline(0, color='black', lw=3, label='Event Horizon')
    ax.fill_between(x, -1, 1, where=(x < 0), color='black', alpha=0.2, label='Black Hole Interior')
    
    ax.set_ylim(0, 1.2)
    ax.set_xlim(-15, 15)
    ax.set_title('Hawking Radiation Toy Model: Particle-Pair Splitting at the Horizon')
    ax.set_xlabel('x')
    ax.set_ylabel('Probability Density')
    ax.legend()
    
    def update(frame):
        line.set_ydata(history[frame])
        return line,
    
    ani = FuncAnimation(fig, update, frames=len(history), blit=True)
    ani.save('simulations/hawking_radiation.gif', writer='pillow', fps=30)
    plt.close()
    print("Animation saved to simulations/hawking_radiation.gif")

if __name__ == "__main__":
    x, V, hist = simulate_hawking_radiation()
    animate_hawking(x, V, hist)
