import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

def verify_bells_theorem(n_shots=4000):
    """
    Simulates the CHSH inequality violation to prove non-locality.
    S = E(a, b) - E(a, b') + E(a', b) + E(a', b')
    Classical limit: |S| <= 2
    Quantum limit: |S| = 2*sqrt(2) approx 2.82
    """
    simulator = AerSimulator()
    
    # Angles for measurement (CHSH optimal angles)
    # a = 0, a' = pi/2
    # b = pi/4, b' = -pi/4
    angles = {
        'ab':  (0, np.pi/4),
        'abp': (0, -np.pi/4),
        'apb': (np.pi/2, np.pi/4),
        'apbp':(np.pi/2, -np.pi/4)
    }
    
    correlations = {}
    
    print(f"Running CHSH Bell Inequality test ({n_shots} shots per setting)...")
    
    for setting, (theta_a, theta_b) in angles.items():
        qc = QuantumCircuit(2, 2)
        # 1. Create Bell state |Psi-> = (|01> - |10>) / sqrt(2) 
        # (Using Psi- for easier rotation logic)
        qc.h(0)
        qc.cx(0, 1)
        qc.z(1)
        qc.x(1)
        
        # 2. Measurement in the chosen basis
        qc.ry(theta_a, 0)
        qc.ry(theta_b, 1)
        
        qc.measure([0, 1], [0, 1])
        
        job = simulator.run(qc, shots=n_shots)
        counts = job.result().get_counts()
        
        # Calculate Correlation E = (N00 + N11 - N01 - N10) / Total
        n00 = counts.get('00', 0)
        n11 = counts.get('11', 0)
        n01 = counts.get('01', 0)
        n10 = counts.get('10', 0)
        
        E = (n00 + n11 - n01 - n10) / n_shots
        correlations[setting] = E
        
    # Calculate Bell Parameter S
    # S = E(a, b) - E(a, b') + E(a', b) + E(a', b')
    S = correlations['ab'] - correlations['abp'] + correlations['apb'] + correlations['apbp']
    
    print("\n--- Bell's Theorem Results ---")
    print(f"Correlations: {correlations}")
    print(f"Bell Parameter |S| = {abs(S):.4f}")
    print(f"Classical Limit: |S| <= 2")
    print(f"Quantum Violation: {abs(S) > 2}")
    
    return S

if __name__ == "__main__":
    verify_bells_theorem()
