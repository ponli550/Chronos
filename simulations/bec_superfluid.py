import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def simulate_bec_2d(N=128, L=10, dt=0.01, steps=600, g_interaction=100.0):
    """
    Simulates a 2D Bose-Einstein Condensate (BEC) using the Gross-Pitaevskii Equation (GPE).
    i * d(psi)/dt = (-1/2 * del^2 + V_ext + g * |psi|^2) * psi
    """
    x = np.linspace(-L, L, N)
    dx = x[1] - x[0]
    X, Y = np.meshgrid(x, x)
    
    # K-space
    k = np.fft.fftfreq(N, d=dx) * 2 * np.pi
    KX, KY = np.meshgrid(k, k)
    K2 = KX**2 + KY**2
    
    # 1. External Potential: Harmonic Trap V = 1/2 * (x^2 + y^2)
    V_ext = 0.5 * (X**2 + Y**2)
    
    # 2. Initial State: Ground state of harmonic oscillator + some "stirring"
    # We add angular momentum to see vortices
    psi = np.exp(-(X**2 + Y**2) / 2)
    L_z_operator = (X * (1j * KY) - Y * (1j * KX)) # Simplified stirring
    # Give it an initial "kick" to rotate
    psi = psi * np.exp(1j * 2.0 * np.arctan2(Y, X)) 
    
    # Normalize
    psi /= np.sqrt(np.sum(np.abs(psi)**2) * dx**2)
    
    psi_history = []
    
    print(f"Simulating Superfluid BEC (Interaction g={g_interaction})...")
    
    # Propagators
    exp_K = np.exp(-0.5j * K2 * dt)
    
    for i in range(steps):
        # Gross-Pitaevskii Step (Split-Step)
        # Non-linear term depends on |psi|^2
        V_eff = V_ext + g_interaction * np.abs(psi)**2
        
        # Potential half-step
        psi *= np.exp(-0.5j * V_eff * dt)
        
        # Kinetic full-step
        psi_k = np.fft.fft2(psi)
        psi_k *= exp_K
        psi = np.fft.ifft2(psi_k)
        
        # Potential half-step (re-calculate V_eff for consistency)
        V_eff = V_ext + g_interaction * np.abs(psi)**2
        psi *= np.exp(-0.5j * V_eff * dt)
        
        # Re-normalize (GPE conserves mass/particle number)
        psi /= np.sqrt(np.sum(np.abs(psi)**2) * dx**2)
        
        if i % 10 == 0:
            psi_history.append(np.abs(psi)**2)
            
    return X, Y, psi_history

def animate_bec(X, Y, history):
    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(history[0], extent=[X.min(), X.max(), Y.min(), Y.max()],
                   origin='lower', cmap='viridis', interpolation='bilinear')
    
    ax.set_title('BEC Superfluid Dynamics: Emergent Quantum Vortices')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    plt.colorbar(im, label='Condensate Density')

    def update(frame):
        im.set_array(history[frame])
        return [im]

    print("Generating BEC Animation...")
    ani = FuncAnimation(fig, update, frames=len(history), blit=True)
    ani.save('simulations/bec_superfluid.gif', writer='pillow', fps=30)
    plt.close()
    print("Animation saved to simulations/bec_superfluid.gif")

if __name__ == "__main__":
    # Strong interaction (g=200) makes the superfluid "stiff" and prone to vortex formation
    X, Y, hist = simulate_bec_2d(g_interaction=200.0, steps=800)
    animate_bec(X, Y, hist)
