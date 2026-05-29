import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.quantum_info import SparsePauliOp
from qiskit_aer import AerSimulator

from qiskit import transpile

def simulate_quantum_heisenberg(n_qubits=3, t_final=2.0, steps=10):
    """
    Simulates the time evolution of a 1D Heisenberg Spin Chain on a quantum circuit.
    H = sum( X_i X_{i+1} + Y_i Y_{i+1} + Z_i Z_{i+1} )
    Using Trotterization (time-slicing).
    """
    # 1. Define the Heisenberg Hamiltonian
    pauli_list = []
    for i in range(n_qubits - 1):
        for op in ['X', 'Y', 'Z']:
            chars = ['I'] * n_qubits
            chars[i] = op
            chars[i+1] = op
            pauli_list.append(("".join(chars[::-1]), 1.0))
            
    H = SparsePauliOp.from_list(pauli_list)
    
    times = np.linspace(0, t_final, steps)
    simulator = AerSimulator()
    z0_expectations = []

    print(f"Running {steps} Trotter steps on Quantum Simulator...")
    
    for t in times:
        qc = QuantumCircuit(n_qubits)
        qc.x(0) # Initial state
        
        if t > 0:
            evolution_gate = PauliEvolutionGate(H, time=t)
            qc.append(evolution_gate, range(n_qubits))
        
        # TRANSPILE the circuit into simulator-native gates (CNOT, Rz, etc.)
        # This resolves the 'unknown instruction: PauliEvolution' error.
        qc_basis = transpile(qc, simulator)
        qc_basis.measure_all()
        
        result = simulator.run(qc_basis, shots=2000).result()
        counts = result.get_counts()
        
        n0 = sum(count for bitstr, count in counts.items() if bitstr[-1] == '0')
        n1 = sum(count for bitstr, count in counts.items() if bitstr[-1] == '1')
        z0_expectations.append((n0 - n1) / (n0 + n1))

    return times, z0_expectations

def plot_quantum_sim(times, z_vals):
    plt.figure(figsize=(10, 6))
    plt.plot(times, z_vals, 'o-', label=r'Magnetization $\langle Z_0(t) \rangle$')
    plt.axhline(0, color='k', linestyle='--', alpha=0.3)
    
    plt.title('Quantum Native Simulation: Heisenberg Spin Chain (Trotterized)')
    plt.xlabel('Time $t$')
    plt.ylabel('Magnetization')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('simulations/quantum_native_heisenberg.png')
    print("Plot saved to simulations/quantum_native_heisenberg.png")

if __name__ == "__main__":
    t, z = simulate_quantum_heisenberg(n_qubits=3, steps=15)
    plot_quantum_sim(t, z)
