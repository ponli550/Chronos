import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_bloch_multivector

def qft_circuit(n):
    """Returns a circuit performing the Quantum Fourier Transform on n qubits."""
    qc = QuantumCircuit(n)
    for j in range(n):
        qc.h(j)
        for k in range(j + 1, n):
            qc.cp(np.pi / 2**(k - j), k, j)
    
    # Swaps to reverse order (standard QFT convention)
    for i in range(n // 2):
        qc.swap(i, n - i - 1)
    return qc

def simulate_qft():
    """
    Simulates the QFT on a 3-qubit state.
    We prepare a state |5> (101) and apply QFT.
    """
    n_qubits = 3
    qc = QuantumCircuit(n_qubits)
    
    # Prepare state |5> = |101>
    # In Qiskit, index 0 is least significant bit
    qc.x(0)
    qc.x(2)
    
    # Apply QFT
    qc.append(qft_circuit(n_qubits).to_gate(label="QFT"), range(n_qubits))
    
    # Observe state
    qc.save_statevector()
    
    simulator = AerSimulator()
    qc_transpiled = transpile(qc, simulator)
    result = simulator.run(qc_transpiled).result()
    statevector = result.get_statevector()
    
    print("\n--- Quantum Fourier Transform (QFT) Results ---")
    print(f"Statevector after QFT on |101>:")
    # Expected: Periodic phase shift across the computational basis
    # We'll plot the amplitudes
    
    plt.figure(figsize=(10, 6))
    plt.bar(range(2**n_qubits), np.abs(statevector)**2)
    plt.title("QFT Output Probabilities (Should be uniform for a basis state)")
    plt.xlabel("Computational Basis State")
    plt.ylabel("Probability")
    plt.savefig('simulations/qft_probabilities.png')
    print("Probability plot saved to simulations/qft_probabilities.png")
    
    # Plot phases
    phases = np.angle(statevector)
    plt.figure(figsize=(10, 6))
    plt.stem(range(2**n_qubits), phases)
    plt.title("QFT Output Phases (Periodic pattern encoded in phase)")
    plt.xlabel("Computational Basis State")
    plt.ylabel("Phase (rad)")
    plt.savefig('simulations/qft_phases.png')
    print("Phase plot saved to simulations/qft_phases.png")

if __name__ == "__main__":
    simulate_qft()
