from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

def simulate_bell_state():
    """
    Creates a Bell state |Phi+> = (|00> + |11>) / sqrt(2) using a Hadamard and CNOT gate.
    Demonstrates quantum entanglement.
    """
    # Create a Quantum Circuit with 2 qubits and 2 classical bits
    qc = QuantumCircuit(2, 2)

    # Add a Hadamard gate on qubit 0 (puts it into superposition)
    qc.h(0)

    # Add a CX (CNOT) gate on control qubit 0 and target qubit 1
    # This entangles the two qubits
    qc.cx(0, 1)

    # Measure both qubits
    qc.measure([0, 1], [0, 1])

    # Use Aer's AerSimulator
    simulator = AerSimulator()

    # Execute the circuit on the qasm simulator
    job = simulator.run(qc, shots=1024)

    # Grab results from the job
    result = job.result()

    # Returns counts
    counts = result.get_counts(qc)
    print("\nTotal counts for 00 and 11 are:", counts)

    # Draw the circuit
    qc.draw(output='mpl', filename='simulations/bell_state_circuit.png')
    print("Circuit diagram saved to simulations/bell_state_circuit.png")

    # Plot histogram
    plot_histogram(counts)
    plt.title("Bell State Measurement Results (1024 shots)")
    plt.savefig('simulations/bell_state_histogram.png')
    print("Histogram saved to simulations/bell_state_histogram.png")

if __name__ == "__main__":
    simulate_bell_state()
