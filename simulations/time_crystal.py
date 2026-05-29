import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

def simulate_discrete_time_crystal(n_qubits=4, steps=30, g_error=0.1):
    """
    Simulates a Discrete Time Crystal (DTC) using a Kicked Ising Model.
    The system is driven by a periodic sequence of gates.
    In the DTC phase, the period of the observables is DOUBLE the drive period.
    """
    # Parameters for the 'Kicked' dynamics
    # Step 1: Pi-pulse (X rotation) with slight error g_error
    theta_flip = np.pi * (1 - g_error)
    
    # Step 2: Ising interaction (ZZ)
    theta_interaction = np.pi / 2
    
    # Step 3: Longitudinal field (Z)
    theta_field = 0.5
    
    magnetizations = []
    simulator = AerSimulator()

    print(f"Simulating Discrete Time Crystal for {steps} drive cycles...")

    for step in range(steps):
        qc = QuantumCircuit(n_qubits)
        # Initial state: Product state |0000...>
        
        # Apply the DTC drive 'step' times
        for _ in range(step):
            # 1. Flip step (quasi-pi pulse)
            for i in range(n_qubits):
                qc.rx(theta_flip, i)
            
            # 2. Interaction step (ZZ)
            for i in range(n_qubits - 1):
                qc.rzz(theta_interaction, i, i + 1)
            
            # 3. Disorder/Field step (Z)
            for i in range(n_qubits):
                qc.rz(theta_field, i)
        
        qc.measure_all()
        
        # Run
        job = simulator.run(transpile(qc, simulator), shots=1024)
        counts = job.result().get_counts()
        
        # Calculate total Z-magnetization
        total_z = 0
        for bitstr, count in counts.items():
            # bitstr is like '1010'
            z_val = sum(1 if b == '0' else -1 for b in bitstr)
            total_z += z_val * count
            
        magnetizations.append(total_z / (1024 * n_qubits))
        
        if step % 5 == 0:
            print(f"Cycle {step} complete...")

    return range(steps), magnetizations

def plot_dtc(cycles, mag):
    plt.figure(figsize=(10, 6))
    plt.plot(cycles, mag, 'bo-', lw=2, label='Magnetization $\langle Z(t) \\rangle$')
    
    # Highlight the sub-harmonic oscillations (period 2)
    plt.title('Discrete Time Crystal: Breaking Time-Translation Symmetry')
    plt.xlabel('Drive Cycle (Time)')
    plt.ylabel('Average Magnetization')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig('simulations/discrete_time_crystal.png')
    print("Plot saved to simulations/discrete_time_crystal.png")

if __name__ == "__main__":
    t, m = simulate_discrete_time_crystal()
    plot_dtc(t, m)
