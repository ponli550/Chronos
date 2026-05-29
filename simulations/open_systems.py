import numpy as np
import matplotlib.pyplot as plt
from qutip import basis, sigmax, sigmaz, mesolve, thermal_dm, destroy

def simulate_open_system_decoherence(gamma=0.1, n_thermal=0.1, t_max=20.0):
    """
    Simulates a two-level system (qubit) interacting with a thermal environment.
    This demonstrates 'The Noise' (Decoherence) and 'Temperature'.
    gamma: Relaxation rate (interaction strength with environment)
    n_thermal: Average number of thermal excitations (represents temperature)
    """
    # Hamiltonian: Simple energy splitting (sigma_z)
    H = 0.5 * 2 * np.pi * sigmaz()
    
    # Initial state: Pure excited state |0> (using QuTiP basis(2, 0))
    # In nature, nothing stays pure for long.
    psi0 = basis(2, 0)
    
    # Collapse operators (Lindblad operators) representing the environment
    # 1. Relaxation to ground state (spontaneous emission)
    # Rate = gamma * (1 + n_thermal)
    c_ops = [np.sqrt(gamma * (1 + n_thermal)) * destroy(2)]
    
    # 2. Excitation from ground state (thermal absorption)
    # Rate = gamma * n_thermal
    if n_thermal > 0:
        c_ops.append(np.sqrt(gamma * n_thermal) * destroy(2).dag())
        
    tlist = np.linspace(0, t_max, 500)
    
    # Operators to monitor: Population of excited state
    e_ops = [basis(2, 0) * basis(2, 0).dag()]
    
    # Solve Master Equation
    result = mesolve(H, psi0, tlist, c_ops=c_ops, e_ops=e_ops)
    
    return tlist, result.expect[0]

def plot_open_system(tlist, population, gamma, n_thermal):
    plt.figure(figsize=(10, 6))
    plt.plot(tlist, population, label='Excited State Population', lw=2)
    
    # Theoretical steady state: P_e = n_thermal / (2 * n_thermal + 1)
    p_steady = n_thermal / (2 * n_thermal + 1)
    plt.axhline(p_steady, color='r', linestyle='--', label=f'Thermal Steady State ($T > 0$)')
    
    plt.title(r'Decoherence: Qubit in a Thermal Bath ($\gamma=' + f'{gamma}' + r'$, $n_{th}=' + f'{n_thermal}' + r'$)')
    plt.xlabel('Time')
    plt.ylabel('Population')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(-0.05, 1.05)
    plt.savefig('simulations/decoherence_noise.png')
    print(f"Plot saved to simulations/decoherence_noise.png")

if __name__ == "__main__":
    # Simulate a system that is "noisy" and "warm"
    gamma_rate = 0.2
    temp_excitations = 0.2 # n_thermal > 0 means T > 0K
    
    print(f"Simulating Open System with Decoherence (Gamma={gamma_rate}, n_th={temp_excitations})...")
    t, pop = simulate_open_system_decoherence(gamma=gamma_rate, n_thermal=temp_excitations)
    plot_open_system(t, pop, gamma_rate, temp_excitations)
