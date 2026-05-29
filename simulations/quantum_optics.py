import numpy as np
import matplotlib.pyplot as plt
from qutip import basis, destroy, tensor, qeye, mesolve

def simulate_jaynes_cummings(g=1.0, kappa=0.05, gamma=0.05, n_max=15, t_max=30.0):
    """
    Simulates the Jaynes-Cummings model: An atom interacting with a quantized cavity field.
    H = hbar * omega_c * a_dag * a + 0.5 * hbar * omega_a * sigma_z + hbar * g * (a_dag * sigma_minus + a * sigma_plus)
    """
    # Parameters
    omega_c = 1.0 * 2 * np.pi  # Cavity frequency
    omega_a = 1.0 * 2 * np.pi  # Atom frequency (resonant)
    
    # Operators
    a = tensor(destroy(n_max), qeye(2)) # Cavity annihilation
    sm = tensor(qeye(n_max), destroy(2)) # Atom lowering operator
    
    # Hamiltonian
    H = omega_c * a.dag() * a + 0.5 * omega_a * tensor(qeye(n_max), basis(2,0)*basis(2,0).dag() - basis(2,1)*basis(2,1).dag())
    # Interaction term (Rotating Wave Approximation)
    H_int = g * (a.dag() * sm + a * sm.dag())
    H_total = H + H_int
    
    # Initial state: Cavity has 5 photons, Atom is in ground state |1>
    n_photons = 5
    psi0 = tensor(basis(n_max, n_photons), basis(2, 1))
    
    # Dissipation (Optional but realistic)
    c_ops = []
    if kappa > 0:
        c_ops.append(np.sqrt(kappa) * a) # Cavity leakage
    if gamma > 0:
        c_ops.append(np.sqrt(gamma) * sm) # Atomic decay
        
    tlist = np.linspace(0, t_max, 1000)
    
    # Solve Master Equation
    result = mesolve(H_total, psi0, tlist, c_ops=c_ops, e_ops=[])
    
    # Expectation values: Cavity photon number and Atom excited state population
    n_curr = [tensor(basis(n_max, i)*basis(n_max, i).dag(), qeye(2)) for i in range(n_max)]
    p_excited_op = tensor(qeye(n_max), basis(2, 0)*basis(2, 0).dag())
    
    # Calculate excited state population over time
    p_excited = [ (p_excited_op * state).tr().real for state in result.states ]
    
    return tlist, p_excited

def plot_jc_results(tlist, p_excited, g):
    plt.figure(figsize=(10, 6))
    plt.plot(tlist, p_excited, label='Excited State Population')
    
    plt.title(f'Jaynes-Cummings Model: Collapse and Revival ($g={g}$)')
    plt.xlabel('Time')
    plt.ylabel('Excited State Population')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('simulations/quantum_optics_jc.png')
    print(f"Plot saved to simulations/quantum_optics_jc.png")

if __name__ == "__main__":
    coupling_g = 2.0 # Strong coupling
    print(f"Simulating Light-Matter Interaction (Jaynes-Cummings, g={coupling_g})...")
    t, pe = simulate_jaynes_cummings(g=coupling_g)
    plot_jc_results(t, pe, coupling_g)
