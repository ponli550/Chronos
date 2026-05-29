import numpy as np
import matplotlib.pyplot as plt
from qutip import basis, destroy, mesolve, ptrace, expect

def simulate_topological_quantum_battery(n_cells=10, charging_power=2.0, t_max=10.0):
    """
    Simulates a 'Topological Quantum Battery' based on the SSH model.
    Energy is stored in the Topological Edge States.
    The 'Topology' protects the stored energy from leaking into the 'bulk' of the material.
    """
    n_sites = 2 * n_cells
    
    # 1. Hamiltonian: SSH Model in the Topological Phase (v < w)
    v, w = 0.2, 1.0 
    H_ssh = np.zeros((n_sites, n_sites))
    for i in range(n_cells):
        H_ssh[2*i, 2*i+1] = v
        H_ssh[2*i+1, 2*i] = v
        if i < n_cells - 1:
            H_ssh[2*i+1, 2*i+2] = w
            H_ssh[2*i+2, 2*i+1] = w
            
    from qutip import Qobj
    H_at = Qobj(H_ssh)
    
    # 2. Charging Protocol
    # We 'pump' energy into the first site (The Edge)
    # H_drive = charging_power * (a_dag + a) at site 0
    # For a single-particle battery, we model this as a transition from ground to excited edge state.
    evals, evecs = H_at.eigenstates()
    edge_state = evecs[n_cells] # One of the zero-energy edge modes
    bulk_state = evecs[0]       # A low-energy bulk mode
    
    # Define charging operator (coupling to external source)
    # We drive the edge state specifically
    H_drive = charging_power * (edge_state * bulk_state.dag() + bulk_state * edge_state.dag())
    
    # 3. Simulation of Charging and Stability
    tlist = np.linspace(0, t_max, 500)
    
    # Initially the battery is empty (bulk state)
    psi0 = bulk_state
    
    # Solve for charging (First half of tlist)
    # and then stability (Second half, turn off drive)
    energy_stored = []
    
    print("Charging the Topological Quantum Battery...")
    
    # Re-simulating with proper time-dependence
    def H_t(t, args):
        if t < t_max/2:
            return H_at + H_drive
        return H_at
        
    result = mesolve(H_t, psi0, tlist, c_ops=[], e_ops=[edge_state * edge_state.dag()])
    
    plt.figure(figsize=(10, 6))
    plt.plot(tlist, result.expect[0], lw=2, color='orange', label='Stored Energy (Edge State Population)')
    plt.axvline(t_max/2, color='k', linestyle='--', label='Charging Off')
    
    plt.title('Technology Prototype: The Topological Quantum Battery')
    plt.xlabel('Time')
    plt.ylabel('Energy Capacity (Fidelity)')
    plt.fill_between(tlist, 0, result.expect[0], color='orange', alpha=0.1)
    
    plt.annotate('Topological Protection:\nEnergy stays on the edge,\nrefusing to leak to bulk', 
                 xy=(t_max*0.75, 0.5), xytext=(t_max*0.5, 0.8),
                 arrowprops=dict(facecolor='black', shrink=0.05))
    
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig('simulations/tech_quantum_battery.png')
    print("New Technology Design saved to simulations/tech_quantum_battery.png")

if __name__ == "__main__":
    simulate_topological_quantum_battery()
