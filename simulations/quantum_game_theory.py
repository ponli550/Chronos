import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

def simulate_quantum_prisoners_dilemma():
    """
    Simulates the Eisert-Wilkens-Lewenstein (EWL) protocol for the Quantum Prisoners' Dilemma.
    Classical Nash Equilibrium: (Defect, Defect) -> Payoff (1, 1)
    Quantum 'Miracle' Strategy: (Q, Q) -> Payoff (3, 3) (Cooperation)
    """
    simulator = AerSimulator()
    
    # Payoff Matrix (Standard PD)
    # (3,3) for CC, (1,1) for DD, (0,5) for CD, (5,0) for DC
    payoff = {
        '00': (3, 3), # CC
        '11': (1, 1), # DD
        '01': (0, 5), # CD
        '10': (5, 0)  # DC
    }
    
    # We will test two cases: 
    # 1. Both players play Classical 'Defect'
    # 2. Both players play Quantum 'Q' strategy (Unique to quantum)
    
    cases = ['Classical Defect', 'Quantum Miracle']
    results = {}

    print("Running Quantum Prisoners' Dilemma...")

    for case in cases:
        # EWL Protocol:
        # 1. Initial State |00>
        # 2. J gate (Entanglement)
        # 3. Player strategies (Local unitaries)
        # 4. J_dag gate (Disentanglement)
        # 5. Measurement
        
        qc = QuantumCircuit(2, 2)
        
        # Step 1: Entangling Gate J
        # J = exp(i * gamma/2 * sigma_x \otimes sigma_x)
        gamma = np.pi / 2 # Maximal entanglement
        qc.rx(gamma, 0)
        qc.ry(gamma, 1)
        qc.cx(0, 1)
        
        # Step 2: Player Strategies
        if case == 'Classical Defect':
            # Defect = X rotation (Bit flip)
            qc.x(0)
            qc.x(1)
        else:
            # Quantum 'Q' strategy: Ry(pi/2)
            qc.ry(np.pi/2, 0)
            qc.ry(np.pi/2, 1)
            
        # Step 3: Disentangle (J_dag)
        qc.cx(0, 1)
        qc.ry(-gamma, 1)
        qc.rx(-gamma, 0)
        
        qc.measure([0, 1], [0, 1])
        
        job = simulator.run(transpile(qc, simulator), shots=1000)
        counts = job.result().get_counts()
        
        # Calculate Average Payoffs
        avg_p1 = 0
        avg_p2 = 0
        for bitstr, count in counts.items():
            p1, p2 = payoff[bitstr]
            avg_p1 += p1 * (count/1000)
            avg_p2 += p2 * (count/1000)
            
        results[case] = (avg_p1, avg_p2)
        print(f"{case} Payoffs: Player 1 = {avg_p1:.2f}, Player 2 = {avg_p2:.2f}")

    return results

if __name__ == "__main__":
    simulate_quantum_prisoners_dilemma()
