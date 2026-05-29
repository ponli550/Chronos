import numpy as np
import matplotlib.pyplot as plt

# WARNING: DO NOT COMMIT YOUR API KEY TO GITHUB
# To break the 'Museum of Shadows', paste your real IBM Quantum Token below.
IBM_QUANTUM_TOKEN = "PASTE_YOUR_TOKEN_HERE"

try:
    from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2 as Estimator
    _HAVE_IBM = True
except ImportError:
    _HAVE_IBM = False


def run_on_real_hardware():
    """
    Instructions to move from Simulation to Reality.
    1. Save your IBM account.
    2. Select a least-busy backend (e.g., 'ibm_brisbane').
    3. Execute your VQE or circuit on real superconducting qubits.
    """
    if not _HAVE_IBM:
        print("\n[!] qiskit-ibm-runtime not installed. Run: pip install qiskit-ibm-runtime")
        return
    if IBM_QUANTUM_TOKEN == "PASTE_YOUR_TOKEN_HERE":
        print("\n[!] Reality Check Failed: No API key found.")
        print("To break the simulation limit, follow these steps:")
        print("1. Create an account at quantum.ibm.com")
        print("2. Copy your API Token.")
        print("3. Paste it into the 'IBM_QUANTUM_TOKEN' variable in this script.")
        return

    # 1. Initialize the Service
    try:
        service = QiskitRuntimeService(channel="ibm_quantum", token=IBM_QUANTUM_TOKEN)
        backend = service.least_busy(operational=True, simulator=False)
        print(f"Connected to Real Quantum Hardware: {backend.name}")

        # 2. To run, simply replace 'AerSimulator' or 'StatevectorEstimator'
        # with 'backend' and 'Estimator(mode=backend)'.
        print("The bridge is open. You are now communicating with a real quantum universe.")

    except Exception as e:
        print(f"Error connecting to hardware: {e}")


def simulate_hardware_bridge():
    steps = ["Create IBM Quantum Account", "Get API Token", "Install qiskit-ibm-runtime",
             "Connect to Backend", "Run Circuit on Real Hardware", "Measure Results"]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis("off")
    for i, s in enumerate(steps):
        ax.text(0.1, 0.85 - i*0.12, f"Step {i+1}: {s}", fontsize=12, verticalalignment="center")
    ax.set_title("Bridge from Simulation to Reality", fontsize=14)
    plt.tight_layout()
    plt.savefig("simulations/hardware_bridge.png")
    plt.close()
    print("Reality bridge blueprint saved to simulations/hardware_bridge.png")


if __name__ == "__main__":
    run_on_real_hardware()
