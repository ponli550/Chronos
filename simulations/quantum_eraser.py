import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

def simulate_quantum_eraser():
    """
    Simulates the logic of the Delayed Choice Quantum Eraser.
    Qubits:
    0: The Signal Photon (resembles the position on the screen)
    1: The Idler Photon (carries the which-path information)
    2: The Eraser (determines if we erase or keep the path info)
    """
    simulator = AerSimulator()
    
    # 1. No Erasure: Which-path information is available
    # This should show NO interference (particle-like behavior)
    qc_no_erase = QuantumCircuit(2, 1)
    qc_no_erase.h(0) # Signal photon in superposition (two paths)
    qc_no_erase.cx(0, 1) # Entangle with Idler (Idler now knows the path)
    
    # Interference check: Rotate basis of qubit 0 and measure
    # If there is interference, Ry(theta) will show a fringe.
    # Without erasure, it should be a flat 50/50.
    angles = np.linspace(0, 2*np.pi, 20)
    counts_no_erase = []
    
    for theta in angles:
        temp_qc = qc_no_erase.copy()
        temp_qc.ry(theta, 0)
        temp_qc.measure(0, 0)
        job = simulator.run(transpile(temp_qc, simulator), shots=1000)
        counts_no_erase.append(job.result().get_counts().get('0', 0) / 1000)
        
    # 2. With Erasure: Which-path information is destroyed
    # This should restore the interference (wave-like behavior)
    counts_erase = []
    for theta in angles:
        # 3-qubit circuit: Signal, Idler, Eraser
        qc_erase = QuantumCircuit(2, 1)
        qc_erase.h(0)
        qc_erase.cx(0, 1)
        
        # THE ERASER: Perform a Hadamard on the Idler
        # This puts the Idler into a basis where we can't tell which path it took.
        qc_erase.h(1)
        
        # We perform a "Coincidence Count" (Post-selection)
        # We only look at cases where the Idler is measured as |0>
        # (This is the crucial step that 'restores' the pattern in the data)
        qc_erase.ry(theta, 0)
        qc_erase.measure_all() # Measure both to post-select
        
        job = simulator.run(transpile(qc_erase, simulator), shots=2000)
        raw_counts = job.result().get_counts()
        
        # Post-select: Look at Signal (bit 1) only when Idler (bit 0) is '0'
        # Bit order in Qiskit counts is 'Idler Signal'
        n_idler0_sig0 = raw_counts.get('00', 0)
        n_idler0_sig1 = raw_counts.get('01', 0)
        
        prob = n_idler0_sig0 / (n_idler0_sig0 + n_idler0_sig1 + 1e-10)
        counts_erase.append(prob)

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(angles, counts_no_erase, 'ro--', label='No Erasure (Information Exists)')
    plt.plot(angles, counts_erase, 'b-', lw=2, label='Eraser Active (Information Destroyed)')
    
    plt.title('The Quantum Eraser: Restoring Wave-Like Interference')
    plt.xlabel('Screen Position (Phase $\\theta$)')
    plt.ylabel('Probability of Detection')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.annotate('No Fringe: Particle Behavior', xy=(1, 0.5), xytext=(1.5, 0.3),
                 arrowprops=dict(facecolor='red', shrink=0.05))
    plt.annotate('Fringe Restored: Wave Behavior', xy=(np.pi, 1.0), xytext=(4, 0.9),
                 arrowprops=dict(facecolor='blue', shrink=0.05))

    plt.savefig('simulations/quantum_eraser.png')
    print("Plot saved to simulations/quantum_eraser.png")

if __name__ == "__main__":
    simulate_quantum_eraser()
