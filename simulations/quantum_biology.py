import numpy as np
import matplotlib.pyplot as plt
from qutip import basis, mesolve, destroy, qeye, tensor

def simulate_quantum_biology_fmo():
    """
    Simulates exciton transfer in the Fenna-Matthews-Olson (FMO) complex.
    This mimics how nature uses quantum coherence for ultra-efficient photosynthesis.
    Using a simplified 3-site model of the pigment-protein complex.
    """
    # 1. Hamiltonian (Site energies and couplings in cm^-1, converted to relative units)
    # Site 1 (BChl 1) - Site 2 (BChl 2) - Site 3 (Reaction Center)
    E1, E2, E3 = 200, 150, 0
    V12, V23 = 100, 100
    
    H = np.array([
        [E1, V12, 0],
        [V12, E2, V23],
        [0, V23, E3]
    ])
    
    from qutip import Qobj
    H_q = Qobj(H)
    
    # 2. Initial State: Exciton starts at Site 1
    psi0 = basis(3, 0)
    
    # 3. Environmental Noise (Dephasing)
    # Nature isn't perfectly isolated; noise actually HELPS the transfer.
    gamma = 20.0 # Dephasing rate
    # Collapse operators for each site
    c_ops = [np.sqrt(gamma) * (basis(3, i) * basis(3, i).dag()) for i in range(3)]
    
    tlist = np.linspace(0, 5.0, 500)
    
    # Solve Master Equation
    result = mesolve(H_q, psi0, tlist, c_ops=c_ops, e_ops=[basis(3, i) * basis(3, i).dag() for i in range(3)])
    
    # 4. Results
    p1, p2, p3 = result.expect
    
    plt.figure(figsize=(10, 6))
    plt.plot(tlist, p1, label='Site 1 (Input)')
    plt.plot(tlist, p2, label='Site 2 (Intermediate)')
    plt.plot(tlist, p3, label='Site 3 (Reaction Center)', lw=3, color='g')
    
    plt.title('Quantum Biology: Exciton Transfer in Photosynthesis (FMO)')
    plt.xlabel('Time')
    plt.ylabel('Population (Energy Probability)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('simulations/quantum_biology_fmo.png')
    print("Plot saved to simulations/quantum_biology_fmo.png")

if __name__ == "__main__":
    simulate_quantum_biology_fmo()
