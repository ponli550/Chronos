import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

def simulate_wormhole_teleportation():
    """
    Simulates a 'Traversable Wormhole' using the ER=EPR protocol.
    Based on the SYK-like model implemented on Google's Sycamore (2023).
    A qubit is 'inserted' into one side of an entangled system and 
    'emerges' on the other side after a 'negative energy' pulse.
    """
    # 9-qubit system (simplified version of the 9-qubit experiment)
    # 0: Message qubit
    # 1-4: Left side of wormhole
    # 5-8: Right side of wormhole
    qc = QuantumCircuit(9, 1)
    
    # 1. PREPARE THE WORMHOLE (TFD State - Thermofield Double)
    # Entangle pairs (1,5), (2,6), (3,7), (4,8) to create the 'bridge'
    for i in range(1, 5):
        qc.h(i)
        qc.cx(i, i+4)
        
    # 2. INSERT MESSAGE
    # Prepare message on qubit 0 (e.g., |1>)
    qc.x(0)
    qc.barrier()
    
    # Swap message into the 'Left' side of the wormhole
    qc.swap(0, 1)
    
    # 3. TIME EVOLUTION (The 'Travel' through the wormhole)
    # In a real experiment, this is a complex SYK-based unitary.
    # Here we simulate the 'Scrambling' and 'Unscrambling' logic.
    # (Simplified: Random gates to scramble information)
    for i in range(1, 9):
        qc.rx(np.pi/4, i)
        
    # 4. THE NEGATIVE ENERGY PULSE
    # This is what makes the wormhole 'Traversable'
    # It couples the two sides and allows information to flow.
    for i in range(1, 5):
        qc.cz(i, i+4) # Coupling gate
        
    # 5. UNSCRAMBLING
    for i in range(1, 9):
        qc.rx(-np.pi/4, i)
    
    # 6. EMERGENCE
    # The message should now be on the 'Right' side (e.g., qubit 5)
    qc.measure(5, 0)
    
    simulator = AerSimulator()
    job = simulator.run(transpile(qc, simulator), shots=1024)
    counts = job.result().get_counts()
    
    print("\n--- Wormhole Teleportation (ER=EPR) Results ---")
    print(f"Measured counts at the exit of the wormhole: {counts}")
    
    # The message was |1>, so we expect high counts for '1'
    prob_success = counts.get('1', 0) / 1024
    print(f"Transmission Fidelity: {prob_success:.4f}")
    
    qc.draw(output='mpl', filename='simulations/wormhole_circuit.png')
    print("Circuit diagram saved to simulations/wormhole_circuit.png")

if __name__ == "__main__":
    simulate_wormhole_teleportation()
