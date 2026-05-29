import numpy as np
import matplotlib.pyplot as plt
from qutip import basis, sigmax, sigmaz, mesolve, expect

def simulate_rabi_oscillations(omega=1.0, delta=0.0, t_max=10.0):
    """
    Simulates Rabi oscillations in a two-level system using QuTiP.
    H = (delta/2) * sigma_z + (omega/2) * sigma_x
    """
    # Define Hamiltonian components
    H0 = 0.5 * delta * sigmaz()
    H1 = 0.5 * omega * sigmax()
    H = H0 + H1

    # Initial state: Ground state |1> (QuTiP basis(2, 1))
    psi0 = basis(2, 1)

    # Time points
    tlist = np.linspace(0, t_max, 500)

    # Solve the Master Equation (Schrodinger equation since no collapse operators)
    result = mesolve(H, psi0, tlist, c_ops=[], e_ops=[basis(2, 0) * basis(2, 0).dag(), basis(2, 1) * basis(2, 1).dag()])

    # Population of ground and excited states
    p_excited = result.expect[0]
    p_ground = result.expect[1]

    return tlist, p_ground, p_excited

def plot_rabi(tlist, p_ground, p_excited, omega, delta):
    plt.figure(figsize=(10, 6))
    plt.plot(tlist, p_ground, label='Ground State Population')
    plt.plot(tlist, p_excited, label='Excited State Population')
    
    # Analytical Rabi frequency: Omega = sqrt(omega^2 + delta^2)
    Omega = np.sqrt(omega**2 + delta**2)
    plt.title(r'Rabi Oscillations ($\Omega_R = ' + f'{Omega:.2f}' + r'$)')
    plt.xlabel('Time')
    plt.ylabel('Population')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('simulations/rabi_oscillations.png')
    print(f"Plot saved to simulations/rabi_oscillations.png")

if __name__ == "__main__":
    omega_rabi = 2.0 * np.pi * 0.5  # 0.5 Hz
    detuning = 0.0
    
    print(f"Simulating Rabi Oscillations with Omega={omega_rabi:.2f}, Delta={detuning:.2f}...")
    t, pg, pe = simulate_rabi_oscillations(omega=omega_rabi, delta=detuning)
    plot_rabi(t, pg, pe, omega_rabi, detuning)
