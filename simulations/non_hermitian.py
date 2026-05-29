import numpy as np
import matplotlib.pyplot as plt

def simulate_exceptional_point():
    """
    Simulates a 2x2 Non-Hermitian system (PT-symmetric).
    H = [[i*gamma, kappa], [kappa, -i*gamma]]
    This shows an 'Exceptional Point' at kappa = gamma.
    """
    kappa = 1.0 # Coupling constant
    gamma_vals = np.linspace(0, 2.0, 500) # Loss/Gain parameter
    
    real_evals = []
    imag_evals = []
    
    for gamma in gamma_vals:
        # H = [[i*gamma, kappa], [kappa, -i*gamma]]
        H = np.array([[1j*gamma, kappa], [kappa, -1j*gamma]])
        evals = np.linalg.eigvals(H)
        
        # Sort for consistency
        idx = np.argsort(np.real(evals))
        evals = evals[idx]
        
        real_evals.append(np.real(evals))
        imag_evals.append(np.imag(evals))
        
    real_evals = np.array(real_evals)
    imag_evals = np.array(imag_evals)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
    
    # Real part of eigenvalues
    ax1.plot(gamma_vals, real_evals[:, 0], 'b-', label='E1 Real')
    ax1.plot(gamma_vals, real_evals[:, 1], 'r-', label='E2 Real')
    ax1.axvline(kappa, color='k', linestyle='--', label='Exceptional Point ($EP$)')
    ax1.set_title('Non-Hermitian Physics: Real Energy Spectrum')
    ax1.set_ylabel('Re(E)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Imaginary part of eigenvalues
    ax2.plot(gamma_vals, imag_evals[:, 0], 'b--', label='E1 Imag (Loss)')
    ax2.plot(gamma_vals, imag_evals[:, 1], 'r--', label='E2 Imag (Gain)')
    ax2.axvline(kappa, color='k', linestyle='--')
    ax2.set_title('Non-Hermitian Physics: Imaginary Energy Spectrum')
    ax2.set_xlabel('Loss/Gain Parameter $\gamma$')
    ax2.set_ylabel('Im(E)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('simulations/exceptional_point.png')
    print("Plot saved to simulations/exceptional_point.png")

if __name__ == "__main__":
    simulate_exceptional_point()
