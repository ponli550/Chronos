import numpy as np
import matplotlib.pyplot as plt
from qutip import basis, sigmax, sigmaz, mesolve

def simulate_quantum_otto_cycle(omega_low=1.0, omega_high=3.0, T_hot=5.0, T_cold=0.1):
    """
    Simulates a Quantum Otto Cycle using a single qubit.
    1. Isentropic Compression (Increase Omega)
    2. Isochoric Heating (Contact with hot bath)
    3. Isentropic Expansion (Decrease Omega)
    4. Isochoric Cooling (Contact with cold bath)
    """
    # Define qubit basis
    psi0 = basis(2, 1) # Start in ground state
    
    # 1. Heating Phase (Contact with hot bath at omega_high)
    H_hot = 0.5 * omega_high * sigmaz()
    # Thermal state at T_hot: rho = exp(-H/T) / Z
    from qutip import thermal_dm
    rho_hot = thermal_dm(2, n=1/(np.exp(omega_high/T_hot)-1))
    
    # 2. Cooling Phase (Contact with cold bath at omega_low)
    rho_cold = thermal_dm(2, n=1/(np.exp(omega_low/T_cold)-1))
    
    # Calculate Internal Energies
    # E = Tr(rho * H)
    E1 = (rho_cold * (0.5 * omega_low * sigmaz())).tr().real
    E2 = (rho_cold * (0.5 * omega_high * sigmaz())).tr().real
    E3 = (rho_hot * (0.5 * omega_high * sigmaz())).tr().real
    E4 = (rho_hot * (0.5 * omega_low * sigmaz())).tr().real
    
    # Work and Heat
    # W_comp = E2 - E1 (Work in)
    # Q_in = E3 - E2 (Heat from hot bath)
    # W_exp = E4 - E3 (Work out)
    # Q_out = E1 - E4 (Heat to cold bath)
    
    Net_Work = -( (E2 - E1) + (E4 - E3) ) # Negative means work extracted
    Efficiency = Net_Work / (E3 - E2)
    Carnot = 1 - T_cold/T_hot
    
    print("\n--- Quantum Otto Engine Results ---")
    print(f"Net Work Extracted: {Net_Work:.4f}")
    print(f"Quantum Efficiency: {Efficiency:.4f}")
    print(f"Carnot Limit: {Carnot:.4f}")
    
    # Visualization of the Cycle on Energy-Frequency diagram
    plt.figure(figsize=(8, 6))
    omegas = [omega_low, omega_high, omega_high, omega_low, omega_low]
    energies = [E1, E2, E3, E4, E1]
    plt.plot(omegas, energies, 'ro-', lw=2)
    plt.fill(omegas, energies, color='red', alpha=0.1)
    
    plt.annotate('Heating', xy=(omega_high, (E2+E3)/2), xytext=(omega_high+0.2, (E2+E3)/2), arrowprops=dict(arrowstyle="->"))
    plt.annotate('Expansion', xy=((omega_low+omega_high)/2, E3), verticalalignment='bottom')
    
    plt.title('Quantum Otto Cycle: Extracting Work from a Qubit')
    plt.xlabel('Frequency $\omega$')
    plt.ylabel('Internal Energy $\langle H \\rangle$')
    plt.grid(True, alpha=0.3)
    plt.savefig('simulations/quantum_otto_engine.png')
    print("Plot saved to simulations/quantum_otto_engine.png")

if __name__ == "__main__":
    simulate_quantum_otto_cycle()
