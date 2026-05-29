import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

def simulate_quantum_sensing_heisenberg_limit(n_qubits=4, theta_true=0.1):
    """
    Simulates Quantum Sensing using an entangled GHZ state.
    Classical Limit (Standard Quantum Limit): Uncertainty delta_theta ~ 1/sqrt(N)
    Heisenberg Limit: Uncertainty delta_theta ~ 1/N
    """
    simulator = AerSimulator()
    
    # 1. GHZ State Preparation: (|000> + |111>) / sqrt(2)
    # This state is extremely sensitive to phase shifts.
    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(0)
    for i in range(n_qubits - 1):
        qc.cx(i, i + 1)
    
    # 2. PHASE SHIFT (The parameter to be sensed)
    # Each qubit picks up a phase theta: |1> -> exp(i * theta) |1>
    for i in range(n_qubits):
        qc.rz(theta_true, i)
        
    # 3. INTERFEROMETRY
    for i in range(n_qubits - 1, 0, -1):
        qc.cx(i - 1, i)
    qc.h(0)
    
    qc.measure(range(n_qubits), range(n_qubits))
    
    # Run
    shots = 2000
    job = simulator.run(transpile(qc, simulator), shots=shots)
    counts = job.result().get_counts()
    
    # Probability of the |00...0> state
    p0 = counts.get('0' * n_qubits, 0) / shots
    
    print(f"--- Quantum Sensing Result (N={n_qubits}) ---")
    print(f"True Phase Shift: {theta_true:.4f}")
    print(f"Measured Probability of All-Zero state: {p0:.4f}")
    print(f"Theoretical Expectation cos^2(N*theta/2): {np.cos(n_qubits * theta_true / 2)**2:.4f}")

    # Plot Comparison
    n_range = np.arange(1, 11)
    sql_limit = 1 / np.sqrt(n_range)
    heisenberg_limit = 1 / n_range
    
    plt.figure(figsize=(10, 6))
    plt.loglog(n_range, sql_limit, 'r--', label=r'Classical Limit (1/$\sqrt{N}$)')
    plt.loglog(n_range, heisenberg_limit, 'b-', lw=2, label='Heisenberg Limit (1/N) - Your Lab')
    
    plt.title('Quantum Sensing: Surpassing the Classical Limit')
    plt.xlabel('Number of Qubits (Resources) $N$')
    plt.ylabel(r'Measurement Uncertainty $\Delta \Theta$')
    plt.legend()
    plt.grid(True, which="both", ls="-", alpha=0.2)
    
    plt.savefig('simulations/quantum_sensing_limit.png')
    print("Sensing analysis saved to simulations/quantum_sensing_limit.png")

if __name__ == "__main__":
    simulate_quantum_sensing_heisenberg_limit(n_qubits=6)
