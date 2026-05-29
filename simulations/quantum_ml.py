import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from scipy.optimize import minimize

def quantum_feature_map(x):
    """Encodes a classical 1D value x into a quantum state using rotation gates."""
    qc = QuantumCircuit(1)
    qc.ry(x, 0)
    return qc

def variational_circuit(params):
    """A parameterized quantum circuit (the 'model' to be trained)."""
    qc = QuantumCircuit(1)
    qc.rz(params[0], 0)
    qc.ry(params[1], 0)
    return qc

def objective_function(params, X, Y):
    """Loss function: mean squared error between quantum measurement and target label."""
    simulator = AerSimulator()
    total_loss = 0
    
    for x, y_target in zip(X, Y):
        # Build circuit: Feature Map + Variational Model
        qc = quantum_feature_map(x)
        qc.compose(variational_circuit(params), inplace=True)
        qc.measure_all()
        
        # Run simulation
        job = simulator.run(qc, shots=100)
        counts = job.result().get_counts()
        
        # Predicted value = probability of measuring |0>
        # (Mapped from [0, 1] to [-1, 1] label range)
        p0 = counts.get('0', 0) / 100
        y_pred = 2 * p0 - 1
        
        total_loss += (y_pred - y_target)**2
        
    return total_loss / len(X)

def train_qml():
    # 1. Create a non-linear dataset: Y = sign(sin(X))
    X_train = np.linspace(0, np.pi, 10)
    Y_train = np.sign(np.sin(2 * X_train)) # Non-linear pattern
    
    # 2. Initial random parameters
    initial_params = np.random.rand(2) * 2 * np.pi
    
    print("Training Variational Quantum Classifier (VQC)...")
    res = minimize(objective_function, initial_params, args=(X_train, Y_train), method='COBYLA', options={'maxiter': 30})
    
    optimized_params = res.x
    print(f"Optimal Parameters: {optimized_params}")
    
    # 3. Test and Plot
    X_test = np.linspace(0, np.pi, 50)
    Y_test = np.sign(np.sin(2 * X_test))
    Y_pred = []
    
    simulator = AerSimulator()
    for x in X_test:
        qc = quantum_feature_map(x)
        qc.compose(variational_circuit(optimized_params), inplace=True)
        qc.measure_all()
        job = simulator.run(qc, shots=200)
        p0 = job.result().get_counts().get('0', 0) / 200
        Y_pred.append(2 * p0 - 1)
        
    plt.figure(figsize=(10, 6))
    plt.plot(X_test, Y_test, 'k--', label='True Pattern (Nature)')
    plt.plot(X_test, Y_pred, 'r-', label='Quantum Model Prediction')
    plt.scatter(X_train, Y_train, c='blue', label='Training Data')
    plt.title('Quantum Machine Learning: Variational Classifier learning sin(x)')
    plt.xlabel('Input Value $x$')
    plt.ylabel('Class Label $y$')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('simulations/quantum_ml_classifier.png')
    print("Plot saved to simulations/quantum_ml_classifier.png")

def simulate_quantum_ml():
    train_qml()

if __name__ == "__main__":
    train_qml()
