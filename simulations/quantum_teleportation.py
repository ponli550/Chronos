import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector

def simulate_quantum_teleportation():
    """
    Simulates the Quantum Teleportation Protocol.
    Transfers the state of qubit 0 to qubit 2 using an entangled pair (1,2).
    """
    # 1. Setup
    # Qubit 0: The state to be teleported (Alice's secret)
    # Qubit 1: Alice's half of the Bell pair
    # Qubit 2: Bob's half of the Bell pair (The destination)
    qc = QuantumCircuit(3, 3)
    
    # 2. PREPARE THE SECRET STATE (on Qubit 0)
    # Let's teleport a complex state: |psi> = cos(theta/2)|0> + e^{i*phi}sin(theta/2)|1>
    theta = np.pi / 3 # 60 degrees
    phi = np.pi / 4   # 45 degrees
    qc.ry(theta, 0)
    qc.rz(phi, 0)
    qc.barrier()
    
    # Capture the initial state for comparison
    initial_sv = Statevector.from_instruction(qc)
    
    # 3. CREATE ENTANGLEMENT (The 'Transporter Link')
    # Create Bell state |Phi+> between qubit 1 and 2
    qc.h(1)
    qc.cx(1, 2)
    qc.barrier()
    
    # 4. ALICE'S OPERATIONS (Teleportation)
    qc.cx(0, 1)
    qc.h(0)
    qc.barrier()
    
    # 5. MEASUREMENT (Alice measures 0 and 1)
    qc.measure(0, 0)
    qc.measure(1, 1)
    qc.barrier()
    
    # 6. BOB'S CORRECTIONS (Based on Alice's measurements)
    # If M1=1, apply Z. If M2=1, apply X.
    # Correct syntax for conditional gates in Qiskit
    with qc.if_test((0, 1)):
        qc.z(2)
    with qc.if_test((1, 1)):
        qc.x(2)
    
    # Bob's qubit (2) should now be in the exact state Alice started with.
    
    print("\n--- Quantum Teleportation Result ---")
    simulator = AerSimulator()
    
    # Run the circuit
    # Note: To verify the state, we usually perform tomography. 
    # Here we'll check the final statevector directly in the simulator.
    qc_save = qc.copy()
    qc_save.save_statevector()
    
    # Use standard transpile but avoid unrolling if_test for direct simulator run
    # Aer supports ControlFlow (if_test)
    result = simulator.run(qc_save).result()
    final_sv = result.get_statevector()
    
    # Compare Alice's initial state (qubit 0) with Bob's final state (qubit 2)
    # (Tracing out the other qubits)
    from qiskit.quantum_info import partial_trace
    rho_bob = partial_trace(final_sv, [0, 1])
    
    print(f"Alice's Initial State (Density Matrix):\n{initial_sv.to_operator().data[:2, :2]}")
    print(f"Bob's Final State (Density Matrix):\n{rho_bob.data}")
    
    # Visualizing the circuit
    qc.draw(output='mpl', filename='simulations/teleportation_circuit.png')
    print("Transporter circuit saved to simulations/teleportation_circuit.png")

if __name__ == "__main__":
    simulate_quantum_teleportation()
