import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def simulate_newton_schrodinger(N=512, L=20, dt=0.01, steps=800, G_mass=50.0):
    """
    Simulates the 1D Newton-Schrödinger Equation:
    i * d(psi)/dt = -1/2 * d^2(psi)/dx^2 + V_grav * psi
    where d^2(V_grav)/dx^2 = 4 * pi * G * |psi|^2 (Poisson Equation)
    
    This mimics a "Self-Gravitating" quantum particle.
    """
    x = np.linspace(-L, L, N)
    dx = x[1] - x[0]
    
    # Momentum space
    k = np.fft.fftfreq(N, d=dx) * 2 * np.pi
    k2 = k**2
    
    # Initial state: Broad Gaussian wave packet
    # Without gravity, this would disperse quickly.
    psi = np.exp(-x**2 / (2 * 2.0**2))
    psi = psi.astype(complex)
    psi /= np.sqrt(np.sum(np.abs(psi)**2) * dx)
    
    psi_history = []
    v_history = []
    
    print(f"Simulating Self-Gravitating Quantum Matter (G*m={G_mass})...")
    
    for i in range(steps):
        # 1. Solve Poisson Equation for V_grav using FFT
        # rho = |psi|^2
        rho = np.abs(psi)**2
        rho_k = np.fft.fft(rho)
        
        # Poisson in k-space: -k^2 * V_k = 4 * pi * G * rho_k
        # V_k = -4 * pi * G * rho_k / k^2
        # Use a small epsilon to avoid division by zero at k=0
        v_k = -4 * np.pi * G_mass * rho_k / (k2 + 1e-10)
        v_grav = np.real(np.fft.ifft(v_k))
        
        # 2. Time step (Split-Step Fourier Method)
        # Half step potential
        psi *= np.exp(-0.5j * v_grav * dt)
        
        # Full step kinetic
        psi_k = np.fft.fft(psi)
        psi_k *= np.exp(-0.5j * k2 * dt)
        psi = np.fft.ifft(psi_k)
        
        # Half step potential
        psi *= np.exp(-0.5j * v_grav * dt)
        
        if i % 10 == 0:
            psi_history.append(np.abs(psi)**2)
            v_history.append(v_grav)

    return x, psi_history, v_history

def animate_gravity(x, psi_history, v_history):
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx()
    
    line1, = ax1.plot(x, psi_history[0], color='blue', lw=2, label=r'Quantum Density $|\psi|^2$')
    line2, = ax2.plot(x, v_history[0], color='red', linestyle='--', alpha=0.5, label='Gravitational Potential $V_{grav}$')
    
    ax1.set_ylim(0, 0.6)
    ax1.set_xlim(-10, 10)
    ax1.set_title('Newton-Schrödinger: Self-Gravitating Quantum Matter')
    ax1.set_xlabel('x')
    ax1.set_ylabel('Probability Density', color='blue')
    ax2.set_ylabel('Potential Energy', color='red')
    
    # Combined legend
    lines = [line1, line2]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper right')
    
    def update(frame):
        line1.set_ydata(psi_history[frame])
        line2.set_ydata(v_history[frame])
        return line1, line2
    
    print("Generating Gravity Animation...")
    ani = FuncAnimation(fig, update, frames=len(psi_history), blit=True)
    ani.save('simulations/quantum_gravity.gif', writer='pillow', fps=30)
    plt.close()
    print("Animation saved to simulations/quantum_gravity.gif")

if __name__ == "__main__":
    # G_mass = 0 -> Pure dispersion (Schrodinger)
    # G_mass > 0 -> Self-contraction (Newton-Schrodinger)
    x, psi_hist, v_hist = simulate_newton_schrodinger(G_mass=80.0)
    animate_gravity(x, psi_hist, v_hist)
