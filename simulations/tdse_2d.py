import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.integrate import trapezoid

def simulate_2d_tdse(N=256, L=20, dt=0.005, steps=500):
    """
    Simulates the 2D Time-Dependent Schrodinger Equation using the Split-Step Fourier Method.
    This pushes local memory and CPU limits due to the O(N^2 log N) complexity per step.
    Units: hbar = m = 1
    """
    # Grid setup
    x = np.linspace(-L, L, N)
    y = np.linspace(-L, L, N)
    X, Y = np.meshgrid(x, y)
    dx = x[1] - x[0]

    # Momentum space setup
    k = np.fft.fftfreq(N, d=dx) * 2 * np.pi
    KX, KY = np.meshgrid(k, k)
    K2 = KX**2 + KY**2

    # Initial Wave Packet: 2D Gaussian
    x0, y0 = -7, 0
    px0, py0 = 8, 0
    sigma = 1.0
    psi = np.exp(-0.5 * (((X - x0)**2 + (Y - y0)**2) / sigma**2)) * np.exp(1j * (px0 * X + py0 * Y))
    
    # Normalize
    norm = np.sqrt(trapezoid(trapezoid(np.abs(psi)**2, x, axis=1), y))
    psi /= norm

    # Potential: Double Slit or Multiple Barriers
    V = np.zeros((N, N))
    # Vertical wall with two slits
    wall_x_idx = (X > 0) & (X < 1.0)
    V[wall_x_idx] = 50.0 # High barrier
    # Slit openings
    slit_width = 1.0
    slit_spacing = 2.0
    V[wall_x_idx & (np.abs(Y - slit_spacing) < slit_width)] = 0
    V[wall_x_idx & (np.abs(Y + slit_spacing) < slit_width)] = 0

    # Propagators
    U_V = np.exp(-0.5j * V * dt) # Half step potential
    U_K = np.exp(-0.5j * K2 * dt) # Full step kinetic

    # Complex Absorbing Potential (CAP)
    # This prevents waves from wrapping around the periodic boundary.
    # It acts as a "sponge" at the edges.
    cap_width = 3.0
    cap_strength = 2.0
    mask = np.zeros((N, N))
    # Add absorbing buffers at all 4 edges
    mask[X < (-L + cap_width)] = cap_strength * ((-L + cap_width - X[X < (-L + cap_width)]) / cap_width)**2
    mask[X > (L - cap_width)] = cap_strength * ((X[X > (L - cap_width)] - (L - cap_width)) / cap_width)**2
    mask[Y < (-L + cap_width)] += cap_strength * ((-L + cap_width - Y[Y < (-L + cap_width)]) / cap_width)**2
    mask[Y > (L - cap_width)] += cap_strength * ((Y[Y > (L - cap_width)] - (L - cap_width)) / cap_width)**2
    
    U_ABC = np.exp(-mask * dt) # Absorbing propagator

    psi_history = []
    
    print(f"Starting 2D TDSE Simulation with ABC (Grid: {N}x{N}, Steps: {steps})...")
    
    for i in range(steps):
        # 1. Potential half-step + ABC
        psi *= U_V * U_ABC
        
        # 2. Kinetic step
        psi_k = np.fft.fft2(psi)
        psi_k *= U_K
        psi = np.fft.ifft2(psi_k)
        
        # 3. Potential half-step + ABC
        psi *= U_V * U_ABC
        
        if i % 10 == 0:
            psi_history.append(np.abs(psi)**2)
            if i % 100 == 0:
                print(f"Step {i}/{steps} complete...")

    return X, Y, V, psi_history

def animate_2d_tdse(X, Y, V, psi_history):
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Plot potential as background
    ax.contour(X, Y, V, levels=[1], colors='white', alpha=0.5, linewidths=2)
    
    im = ax.imshow(psi_history[0], extent=[X.min(), X.max(), Y.min(), Y.max()],
                   origin='lower', cmap='magma', vmax=np.max(psi_history[0])*1.2)
    
    ax.set_title('2D Quantum Double-Slit Interference')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    plt.colorbar(im, label='Probability Density')

    def update(frame):
        im.set_array(psi_history[frame])
        return [im]

    print("Generating 2D Animation (this may take a few minutes)...")
    ani = FuncAnimation(fig, update, frames=len(psi_history), blit=True)
    ani.save('simulations/tdse_2d_double_slit.gif', writer='pillow', fps=20)
    plt.close()
    print("Animation saved to simulations/tdse_2d_double_slit.gif")

if __name__ == "__main__":
    # N=256 is a good balance for local "limit" pushing. 
    # N=512 or 1024 would likely require GPU or long wait times.
    X, Y, V, history = simulate_2d_tdse(N=256, steps=400)
    animate_2d_tdse(X, Y, V, history)
