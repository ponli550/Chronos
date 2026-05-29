import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

def simulate_quantum_satellite_qkd(n_bits=100, loss_rate=0.2):
    """
    Simulates Quantum Key Distribution (QKD) via a Satellite using the BB84 Protocol.
    n_bits: Number of photons sent from the satellite.
    loss_rate: Probability of a photon being lost in the atmosphere.
    """
    simulator = AerSimulator()
    
    # 1. ALICE (Satellite) prepares random bits and random bases
    alice_bits = np.random.randint(2, size=n_bits)
    alice_bases = np.random.randint(2, size=n_bits) # 0 for Z-basis, 1 for X-basis
    
    # 2. BOB (Ground Station) chooses random measurement bases
    bob_bases = np.random.randint(2, size=n_bits)
    
    bob_results = []
    photons_received = []

    print(f"Satellite is transmitting {n_bits} quantum bits to the Ground Station...")

    for i in range(n_bits):
        # Atmosphere Simulation: Photon might be lost
        if np.random.rand() < loss_rate:
            bob_results.append(None)
            photons_received.append(False)
            continue
        
        photons_received.append(True)
        qc = QuantumCircuit(1, 1)
        
        # Alice prepares the state
        if alice_bits[i] == 1:
            qc.x(0)
        if alice_bases[i] == 1: # X-basis
            qc.h(0)
            
        # Bob measures in his chosen basis
        if bob_bases[i] == 1: # X-basis
            qc.h(0)
        qc.measure(0, 0)
        
        # Run simulation
        job = simulator.run(transpile(qc, simulator), shots=1)
        res = list(job.result().get_counts().keys())[0]
        bob_results.append(int(res))

    # 3. SIFTING (Alice and Bob compare bases over a classical link)
    final_key_alice = []
    final_key_bob = []
    
    for i in range(n_bits):
        if photons_received[i] and alice_bases[i] == bob_bases[i]:
            final_key_alice.append(alice_bits[i])
            final_key_bob.append(bob_results[i])
            
    print(f"\n--- Satellite QKD Results ---")
    print(f"Photons Lost in Atmosphere: {n_bits - sum(photons_received)}")
    print(f"Bits with Matching Bases: {len(final_key_alice)}")
    
    # Error Check (Security)
    if len(final_key_alice) > 0:
        errors = sum(1 for a, b in zip(final_key_alice, final_key_bob) if a != b)
        error_rate = errors / len(final_key_alice)
        print(f"Quantum Bit Error Rate (QBER): {error_rate:.2%}")
        if error_rate < 0.11: # Standard security threshold
            print("Link SECURE: Encryption Key generated successfully.")
        else:
            print("Link COMPROMISED: Eavesdropping or extreme noise detected.")

    # Visualization
    plt.figure(figsize=(10, 6))
    plt.step(range(len(final_key_alice)), final_key_alice, label='Alice Key (Satellite)', where='post')
    plt.step(range(len(final_key_bob)), final_key_bob, '--', label='Bob Key (Ground)', where='post')
    
    plt.title('Quantum Satellite Technology: Secure Key Generation (BB84)')
    plt.xlabel('Key Bit Index')
    plt.ylabel('Bit Value (0 or 1)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.savefig('simulations/quantum_satellite_qkd.png')
    print("QKD Analysis saved to simulations/quantum_satellite_qkd.png")

if __name__ == "__main__":
    simulate_quantum_satellite_qkd()
