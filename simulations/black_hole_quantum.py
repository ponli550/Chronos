import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def simulate_black_hole_quantum(N=1024, r_max=40.0, dt=0.01, steps=1000, M=5.0):
    """
    Simulates a quantum wave packet in the gravitational potential of a 
    Schwarzschild Black Hole.
    V_eff = -G*M/r + L^2/(2*r^2) - G*M*L^2/(c^2 * r^3)
    (Using a semi-classical approximation)
    """
    r = np.linspace(2.1, r_max, N) # Stay outside Event Horizon (r > 2*M)
    dr = r[1] - r[0]
    
    # Grid in k-space
    k = np.fft.fftfreq(N, d=dr) * 2 * np.pi
    k2 = k**2
    
    # Effective Potential (General Relativity correction term -1/r^3)
    L_ang = 5.0 # Angular momentum
    V_eff = -M/r + L_ang**2/(2*r**2) - M*L_ang**2/r**3
    
    # Initial state: Gaussian wave packet orbiting
    r0 = 20.0
    p0 = -2.0 # Moving towards the BH
    sigma = 2.0
    psi = np.exp(-0.5 * ((r - r0) / sigma)**2) * np.exp(1j * p0 * r)
    from scipy.integrate import trapezoid
    psi /= np.sqrt(trapezoid(np.abs(psi)**2, r))
    
    psi_history = []
    
    print(f"Simulating Quantum Wave Packet near Schwarzschild Black Hole (M={M})...")
    
    for i in range(steps):
        # Split-Step Fourier
        psi *= np.exp(-0.5j * V_eff * dt)
        psi_k = np.fft.fft(psi)
        psi_k *= np.exp(-0.5j * k2 * dt)
        psi = np.fft.ifft(psi_k)
        psi *= np.exp(-0.5j * V_eff * dt)
        
        if i % 10 == 0:
            psi_history.append(np.abs(psi)**2)
            
    return r, V_eff, psi_history

def animate_black_hole(r, V, history):
    fig, ax = plt.subplots(figsize=(10, 6))
    line, = ax.plot(r, history[0], lw=2, label='Quantum Wave Packet')
    ax_v = ax.twinx()
    ax_v.plot(r, V, 'r--', alpha=0.3, label='GR Effective Potential')
    
    ax.set_ylim(0, 0.6)
    ax.set_xlim(2, 40)
    ax.set_title('Quantum Dynamics in Curved Spacetime (Schwarzschild)')
    ax.set_xlabel('Radius $r$')
    ax.set_ylabel('Probability Density')
    ax_v.set_ylabel('Potential Energy', color='red')
    
    def update(frame):
        line.set_ydata(history[frame])
        return line,
    
    ani = FuncAnimation(fig, update, frames=len(history), blit=True)
    ani.save('simulations/black_hole_quantum.gif', writer='pillow', fps=30)
    plt.close()
    print("Animation saved to simulations/black_hole_quantum.gif")

if __name__ == "__main__":
    r, V, hist = simulate_black_hole_quantum()
    animate_black_hole(r, V, hist)
