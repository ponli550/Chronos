import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def simulate_superconductor_tdgl(N=128, L=15, dt=0.01, steps=1000, kappa=2.0, B_ext=0.5):
    """
    Simulates the Time-Dependent Ginzburg-Landau (TDGL) equation for a superconductor.
    d(psi)/dt = -(1/sigma) * ( (grad - iA)^2 psi + psi * (|psi|^2 - 1) )
    This models the 'Superconducting Order Parameter' psi.
    kappa: Ginzburg-Landau parameter (Type-II if kappa > 1/sqrt(2))
    B_ext: External magnetic field strength
    """
    x = np.linspace(-L, L, N)
    dx = x[1] - x[0]
    X, Y = np.meshgrid(x, x)
    
    # 1. Vector Potential A for a uniform magnetic field B_ext in z-direction
    # A = (-B_ext * y, 0, 0) in Landau Gauge
    Ax = -B_ext * Y
    Ay = np.zeros_like(Y)
    
    # 2. Initial state: Random small fluctuations (Normal state)
    # The system will "cool down" and form Cooper Pairs (psi)
    psi = 0.1 * (np.random.randn(N, N) + 1j * np.random.randn(N, N))
    
    psi_history = []
    
    print(f"Cooling material into Superconducting state (B={B_ext}, kappa={kappa})...")
    
    for i in range(steps):
        # Calculate Gauge-Invariant Laplacian: (grad - iA)^2 psi
        # Using finite difference
        psi_left  = np.roll(psi,  1, axis=1) * np.exp(-1j * Ax * dx)
        psi_right = np.roll(psi, -1, axis=1) * np.exp( 1j * Ax * dx)
        psi_up    = np.roll(psi,  1, axis=0) * np.exp(-1j * Ay * dx)
        psi_down  = np.roll(psi, -1, axis=0) * np.exp( 1j * Ay * dx)
        
        laplacian = (psi_left + psi_right + psi_up + psi_down - 4*psi) / dx**2
        
        # TDGL Update: d(psi)/dt = laplacian + psi * (1 - |psi|^2)
        # (Simplified dimensionless version)
        dpsi_dt = laplacian + psi * (1.0 - np.abs(psi)**2)
        
        psi += dt * dpsi_dt
        
        # Boundary Conditions: Simple periodic for this demo
        # (Real superconductors use Neumann BCs, but periodic shows vortex arrays well)
        
        if i % 20 == 0:
            psi_history.append(np.abs(psi)**2)
            if i % 200 == 0:
                print(f"Step {i}/{steps}...")

    return X, Y, psi_history

def animate_superconductor(X, Y, history):
    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(history[0], extent=[X.min(), X.max(), Y.min(), Y.max()],
                   origin='lower', cmap='plasma', interpolation='bilinear')
    
    ax.set_title('Superconductivity: Emergent Abrikosov Vortex Lattice')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    plt.colorbar(im, label=r'Superconducting Density $|\psi|^2$')

    def update(frame):
        im.set_array(history[frame])
        return [im]

    print("Generating Superconductivity Animation...")
    ani = FuncAnimation(fig, update, frames=len(history), blit=True)
    ani.save('simulations/superconductivity_vortices.gif', writer='pillow', fps=30)
    plt.close()
    print("Animation saved to simulations/superconductivity_vortices.gif")

if __name__ == "__main__":
    # Simulate Type-II superconductor (kappa=2.0)
    # B_ext = 0.6 is above Hc1, creating vortices
    X, Y, hist = simulate_superconductor_tdgl(B_ext=0.6, steps=1200)
    animate_superconductor(X, Y, hist)
