import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def simulate_gravatom_binary(N=512, L=30, dt=0.01, steps=1000, G_mass=150.0):
    """
    Simulates a 'Binary Gravatom' system.
    Two quantum wave packets interacting via their own gravitational fields.
    Mimics a 'New Elemental' state of matter where gravity is the primary bond.
    """
    x = np.linspace(-L, L, N)
    dx = x[1] - x[0]
    
    # Momentum space
    k = np.fft.fftfreq(N, d=dx) * 2 * np.pi
    k2 = k**2
    
    # Initial state: Two wave packets with opposite momentum (Binary system)
    sigma = 1.5
    dist = 8.0
    v0 = 2.0
    
    # Packet 1 (Left)
    psi1 = np.exp(-(x + dist)**2 / (2 * sigma**2)) * np.exp(1j * v0 * x)
    # Packet 2 (Right)
    psi2 = np.exp(-(x - dist)**2 / (2 * sigma**2)) * np.exp(-1j * v0 * x)
    
    psi = (psi1 + psi2).astype(complex)
    # Normalize to 2 "particles" (total weight)
    psi /= np.sqrt(np.sum(np.abs(psi)**2) * dx / 2.0)
    
    psi_history = []
    v_history = []
    
    print(f"Creating 'Binary Gravatom' (Total G*m={G_mass})...")
    
    for i in range(steps):
        # 1. Self-Gravity (Poisson Equation)
        rho = np.abs(psi)**2
        rho_k = np.fft.fft(rho)
        v_k = -4 * np.pi * G_mass * rho_k / (k2 + 1e-10)
        v_grav = np.real(np.fft.ifft(v_k))
        
        # 2. Time Evolution (Split-Step)
        psi *= np.exp(-0.5j * v_grav * dt)
        psi_k = np.fft.fft(psi)
        psi_k *= np.exp(-0.5j * k2 * dt)
        psi = np.fft.ifft(psi_k)
        psi *= np.exp(-0.5j * v_grav * dt)
        
        if i % 10 == 0:
            psi_history.append(np.abs(psi)**2)
            v_history.append(v_grav)

    return x, psi_history, v_history

def animate_gravatom(x, psi_hist, v_hist):
    fig, ax = plt.subplots(figsize=(10, 6))
    line, = ax.plot(x, psi_hist[0], color='purple', lw=3, label='Gravatom Binary Density')
    
    ax.set_ylim(0, 1.2)
    ax.set_xlim(-20, 20)
    ax.set_title("Synthesis of a New 'Elemental': The Binary Gravatom")
    ax.set_xlabel('Spatial Coordinate $x$')
    ax.set_ylabel('Quantum-Gravitational Density')
    ax.grid(True, alpha=0.2)
    ax.legend()
    
    def update(frame):
        line.set_ydata(psi_hist[frame])
        return line,
    
    print("Capturing the merge of the Gravatoms...")
    ani = FuncAnimation(fig, update, frames=len(psi_hist), blit=True)
    ani.save('simulations/new_elemental_gravatom.gif', writer='pillow', fps=30)
    plt.close()
    print("Elemental Synthesis saved to simulations/new_elemental_gravatom.gif")

if __name__ == "__main__":
    # Create the new element
    x, psi, v = simulate_gravatom_binary()
    animate_gravatom(x, psi, v)
