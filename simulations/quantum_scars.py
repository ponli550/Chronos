import numpy as np
import matplotlib.pyplot as plt
from qiskit.quantum_info import SparsePauliOp
from scipy.linalg import expm

def simulate_pxp_model_scars(L=10, t_final=20.0, steps=200):
    """
    Simulates Quantum Many-Body Scars in the PXP model.
    H = sum_i P_{i-1} X_i P_{i+1} where P = |0><0| (Projector to ground state).
    This model prevents adjacent excitations (Rydberg Blockade).
    The 'Z2' state (|101010...>) exhibits persistent oscillations (Scars).
    """
    from qiskit.quantum_info import Operator
    
    # 1. Build PXP Hamiltonian
    # PXP_i = I...I P_{i-1} X_i P_{i+1} I...I
    # We use periodic boundary conditions
    pauli_list = []
    
    # Define P = (I + Z)/2
    # X = X
    # PXP = 1/4 * (I+Z)X(I+Z) = 1/4 * (X + ZX + XZ + ZXZ)
    
    def get_pxp_term(i):
        # i is the site being flipped (X)
        # neighbors are (i-1) and (i+1)
        im1 = (i - 1) % L
        ip1 = (i + 1) % L
        
        terms = []
        for op_m1 in ['I', 'Z']:
            for op_p1 in ['I', 'Z']:
                s = ['I'] * L
                s[im1] = op_m1
                s[i] = 'X'
                s[ip1] = op_p1
                terms.append(("".join(s[::-1]), 0.25))
        return terms

    all_terms = []
    for i in range(L):
        all_terms.extend(get_pxp_term(i))
        
    H_mat = SparsePauliOp.from_list(all_terms).to_matrix()
    
    # 2. Initial State: |Z2> state = |1010101010>
    # This state is a 'Scar' state that should oscillate.
    psi_z2 = np.zeros(2**L)
    idx_z2 = int("10" * (L//2), 2)
    psi_z2[idx_z2] = 1.0
    
    # 3. Time Evolution
    times = np.linspace(0, t_final, steps)
    dt = times[1] - times[0]
    
    # Observable: Fidelity with initial Z2 state
    fidelities = []
    psi = psi_z2.copy()
    
    # Use Matrix Exponential for the unitary
    U = expm(-1j * H_mat * dt)
    
    print(f"Simulating PXP Scars for L={L} sites...")
    for t in times:
        fidelity = np.abs(np.vdot(psi_z2, psi))**2
        fidelities.append(fidelity)
        psi = U @ psi

    plt.figure(figsize=(10, 6))
    plt.plot(times, fidelities, color='darkgreen', lw=2, label='Z2 State Fidelity')
    plt.title('Quantum Many-Body Scars: Non-Thermal Oscillations (PXP Model)')
    plt.xlabel('Time $t$')
    plt.ylabel('Fidelity $|\langle \psi(0) | \psi(t) \\rangle|^2$')
    plt.grid(True, alpha=0.3)
    
    plt.annotate('Scar Revivals:\nSystem refuses to thermalize', xy=(t_final/2, 0.4), xytext=(t_final/2+2, 0.6),
                 arrowprops=dict(facecolor='black', shrink=0.05))
    
    plt.savefig('simulations/quantum_scars_pxp.png')
    print("Scar simulation saved to simulations/quantum_scars_pxp.png")

if __name__ == "__main__":
    simulate_pxp_model_scars()
