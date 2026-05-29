import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact, FloatSlider, IntSlider
from simulations.qho import solve_qho_1d

def interactive_qho(omega=1.0, x_max=10.0):
    x, evals, evecs = solve_qho_1d(n_points=500, x_max=x_max, omega=omega)
    
    plt.figure(figsize=(10, 6))
    V = 0.5 * (omega**2) * (x**2)
    plt.plot(x, V, 'k--', alpha=0.3)
    
    for i in range(min(4, len(evals))):
        psi = evecs[:, i]
        psi /= np.sqrt(np.trapezoid(psi**2, x))
        plt.plot(x, psi + evals[i], label=f'n={i}')
        plt.axhline(evals[i], color='gray', linestyle='--', alpha=0.3)
        
    plt.ylim(-0.5, evals[3] + 1.0 if len(evals)>3 else 5)
    plt.xlim(-x_max/2, x_max/2)
    plt.title(f'Interactive QHO ($\omega = {omega:.2f}$)')
    plt.legend()
    plt.show()

def start_lab():
    print("Starting Interactive Quantum Lab...")
    interact(interactive_qho, 
             omega=FloatSlider(value=1.0, min=0.1, max=5.0, step=0.1, description='Omega:'),
             x_max=FloatSlider(value=10.0, min=5.0, max=20.0, step=1.0, description='X Range:'))

if __name__ == "__main__":
    # This part is for when running in a Jupyter kernel
    start_lab()
