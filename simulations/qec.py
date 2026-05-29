import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

def simulate_error_correction():
    """
    Simulates the 3-qubit Bit Flip Error Correction Code.
    Steps:
    1. Encode a logical qubit |psi> into 3 physical qubits.
    2. Simulate a Bit Flip error on one qubit.
    3. Detect and Correct the error using syndrome measurement.
    """
    # Create logical state |1>
    qc = QuantumCircuit(3, 1) # 3 physical qubits, 1 classical bit for result
    qc.x(0) # Prepare |1> on qubit 0
    
    # 1. ENCODING (Logical |1> -> physical |111>)
    qc.cx(0, 1)
    qc.cx(0, 2)
    
    # 2. THE ERROR (Simulate a bit flip on qubit 1)
    qc.barrier()
    qc.x(1) # Oops! A stray cosmic ray flipped our qubit.
    qc.barrier()
    
    # 3. DETECTION & CORRECTION (Syndrome Measurement)
    # We add 2 ancilla qubits to measure the syndrome without destroying |psi>
    synd_qc = QuantumCircuit(5, 1) # 3 data + 2 ancilla + 1 output
    synd_qc.compose(qc, range(3), inplace=True)
    
    # Ancilla 0 checks parity of qubits (0, 1)
    synd_qc.cx(0, 3)
    synd_qc.cx(1, 3)
    
    # Ancilla 1 checks parity of qubits (1, 2)
    synd_qc.cx(1, 4)
    synd_qc.cx(2, 4)
    
    # 4. DECODING / CORRECTION (Conditional on ancillas)
    # If ancilla 0 and 1 are 1, then qubit 1 is the error.
    # We use a simple Toffoli gate-like logic here for correction.
    synd_qc.ccx(3, 4, 1) # If both syndromes are 1, flip qubit 1 back
    # (Other combinations would handle errors on 0 or 2)
    
    # Measure the logical result (should be 1)
    synd_qc.measure(1, 0)
    
    simulator = AerSimulator()
    job = simulator.run(transpile(synd_qc, simulator), shots=1024)
    counts = job.result().get_counts()
    
    print("\n--- Quantum Error Correction (Bit-Flip) Results ---")
    print(f"Syndrome counts (Corrected State): {counts}")
    print("If results are '1', the error was successfully corrected!")
    
    # Save circuit for visualization
    synd_qc.draw(output='mpl', filename='simulations/qec_circuit.png')
    print("QEC Circuit diagram saved to simulations/qec_circuit.png")

if __name__ == "__main__":
    simulate_error_correction()
