import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def simulate_klein_gordon(N=200, L=20, dt=0.05, steps=400, mass=1.0):
    """
    Simulates the 1+1D Klein-Gordon equation: (d^2/dt^2 - d^2/dx^2 + m^2) phi = 0
    Using a central difference leapfrog scheme.
    """
    x = np.linspace(-L, L, N)
    dx = x[1] - x[0]
    
    # Stability condition: dt < dx
    if dt >= dx:
        dt = dx * 0.5
        
    # Initial conditions
    # Gaussian pulse
    phi = np.exp(-x**2 / 2)
    # Velocity is zero initially
    phi_old = phi.copy()
    
    phi_history = []
    
    # Time evolution
    for i in range(steps):
        # Second derivative in x
        d2_phi_dx2 = (np.roll(phi, 1) - 2*phi + np.roll(phi, -1)) / dx**2
        
        # Klein-Gordon update: phi_new = 2*phi - phi_old + dt^2 * (d2_phi_dx2 - m^2 * phi)
        phi_new = 2*phi - phi_old + dt**2 * (d2_phi_dx2 - mass**2 * phi)
        
        phi_old = phi.copy()
        phi = phi_new
        
        if i % 5 == 0:
            phi_history.append(phi.copy())
            
    return x, phi_history

def animate_klein_gordon(x, phi_history, mass):
    fig, ax = plt.subplots(figsize=(10, 6))
    line, = ax.plot(x, phi_history[0], lw=2)
    
    ax.set_ylim(-1.2, 1.2)
    ax.set_title(f'1+1D Klein-Gordon Field (Mass m = {mass})')
    ax.set_xlabel('x')
    ax.set_ylabel(r'$\phi(x,t)$')
    ax.grid(True, alpha=0.3)
    
    def update(frame):
        line.set_ydata(phi_history[frame])
        return line,
    
    ani = FuncAnimation(fig, update, frames=len(phi_history), blit=True)
    ani.save('simulations/klein_gordon.gif', writer='pillow', fps=30)
    plt.close()
    print("Animation saved to simulations/klein_gordon.gif")

if __name__ == "__main__":
    print("Simulating Klein-Gordon Field...")
    m = 1.0
    x, history = simulate_klein_gordon(mass=m)
    animate_klein_gordon(x, history, m)
