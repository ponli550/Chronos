import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from scipy.integrate import trapezoid

def simulate_tunneling(n_points=1024, x_max=50, dt=0.01, steps=1000):
    """
    Simulates a wave packet hitting a potential barrier using the Split-Step Fourier Method.
    Units: Atomic units (hbar = m = 1)
    """
    x = np.linspace(-x_max, x_max, n_points)
    dx = x[1] - x[0]
    
    # K-space (momentum space)
    k = np.fft.fftfreq(n_points, d=dx) * 2 * np.pi
    
    # Initial Wave Packet: Gaussian
    x0 = -15
    p0 = 5
    sigma = 2
    psi = np.exp(-0.5 * ((x - x0) / sigma)**2) * np.exp(1j * p0 * x)
    psi /= np.sqrt(trapezoid(np.abs(psi)**2, x))
    
    # Potential Barrier
    V0 = 15  # Height of barrier
    width = 2
    V = np.zeros_like(x)
    V[(x > 0) & (x < width)] = V0
    
    # Propagators
    # Kinetic propagator (in k-space)
    U_k = np.exp(-0.5j * (k**2) * dt)
    # Potential propagator (in x-space)
    # Correcting U_v application in the loop below
    
    psi_history = []
    for i in range(steps):
        # 1. Potential half-step
        psi *= np.exp(-0.5j * V * dt)
        # 2. Kinetic step (Fourier transform to k-space)
        psi_k = np.fft.fft(psi)
        psi_k *= U_k
        psi = np.fft.ifft(psi_k)
        # 3. Potential half-step
        psi *= np.exp(-0.5j * V * dt)
        
        if i % 10 == 0:
            psi_history.append(np.abs(psi)**2)
            
    return x, V, psi_history

def plot_tunneling(x, V, psi_history):
    fig, ax = plt.subplots(figsize=(10, 6))
    line, = ax.plot(x, psi_history[0], label=r'$|\psi(x,t)|^2$', lw=2)
    ax.fill_between(x, 0, V / V.max() * 0.5 if V.max() > 0 else 1, color='gray', alpha=0.3, label='Barrier (scaled)')
    
    ax.set_xlim(-25, 25)
    ax.set_ylim(0, 0.6)
    ax.set_title('Quantum Tunneling: Time Evolution of a Wave Packet')
    ax.set_xlabel('x')
    ax.set_ylabel('Probability Density')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    def update(frame):
        line.set_ydata(psi_history[frame])
        return line,
    
    # Create static plot of the final state if animation fails or just for quick reference
    plt.savefig('simulations/tunneling_static.png')
    
    # Attempt animation
    try:
        ani = FuncAnimation(fig, update, frames=len(psi_history), blit=True)
        ani.save('simulations/tunneling.gif', writer='pillow', fps=30)
        print("Animation saved to simulations/tunneling.gif")
    except Exception as e:
        print(f"Animation failed (likely missing ffmpeg/pillow): {e}")

if __name__ == "__main__":
    print("Simulating Quantum Tunneling...")
    x, V, psi_history = simulate_tunneling()
    plot_tunneling(x, V, psi_history)
