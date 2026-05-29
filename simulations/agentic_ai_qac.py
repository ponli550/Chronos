import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import SparsePauliOp
from qutip import basis, destroy, mesolve, sigmaz, sigmax

class QuantumEnvironment:
    """A 1-qubit environment with decay (Decoherence)."""
    def __init__(self, gamma=0.2):
        self.gamma = gamma
        self.state = basis(2, 1) # Start in ground state
        self.dt = 0.5 # Time step
        
    def step(self, action):
        """
        Action 0: Do nothing
        Action 1: Apply X-pulse (flip qubit)
        """
        # 1. Apply Action
        H = 0.0 * sigmaz()
        if action == 1:
            # Short pi-pulse
            self.state = sigmax() * self.state
            
        # 2. Let the system decay (Environmental Noise)
        c_ops = [np.sqrt(self.gamma) * destroy(2)]
        tlist = [0, self.dt]
        result = mesolve(H, self.state, tlist, c_ops=c_ops, e_ops=[])
        self.state = result.states[-1]
        
        # 3. Calculate Reward: population of excited state
        # We want the agent to keep the qubit excited |0>
        reward = np.abs(self.state[0,0])**2
        return reward

class QuantumAgent:
    """An AI agent with a Quantum Brain (Variational Circuit)."""
    def __init__(self, n_params=2):
        self.params = np.random.rand(n_params) * 2 * np.pi
        self.simulator = AerSimulator()

    def get_action(self, state_obs):
        """Uses a quantum circuit to decide the next action."""
        # Map observation (current energy) to a rotation
        qc = QuantumCircuit(1, 1)
        qc.ry(state_obs, 0) # Feature map
        
        # Variational Brain
        qc.ry(self.params[0], 0)
        qc.rz(self.params[1], 0)
        
        qc.measure(0, 0)
        
        job = self.simulator.run(transpile(qc, self.simulator), shots=1)
        res = job.result().get_counts()
        
        # Return 0 or 1 based on quantum measurement
        return 1 if '1' in res else 0

    def train(self, env, episodes=20, steps_per_ep=10):
        """Simple 'Quantum Evolution' to optimize the brain."""
        print(f"Agent is learning to survive in a noisy environment...")
        
        best_reward = -np.inf
        
        for ep in range(episodes):
            # Mutate params (Quantum Neuro-evolution)
            old_params = self.params.copy()
            self.params += np.random.normal(0, 0.5, len(self.params))
            
            total_reward = 0
            env.state = basis(2, 1) # Reset
            
            for _ in range(steps_per_ep):
                obs = np.abs(env.state[0,0])**2 # Current population
                action = self.get_action(obs)
                total_reward += env.step(action)
                
            if total_reward > best_reward:
                best_reward = total_reward
                print(f"Episode {ep}: New Best Reward = {best_reward:.2f}")
            else:
                self.params = old_params # Revert

def simulate_agentic_ai_control():
    env = QuantumEnvironment(gamma=0.3)
    agent = QuantumAgent()
    
    # 1. Train the Agent
    agent.train(env)
    
    # 2. Test the Optimized Agent
    print("\nTesting the Quantum Agentic Controller (QAC)...")
    history = []
    env.state = basis(2, 1)
    for i in range(30):
        obs = np.abs(env.state[0,0])**2
        action = agent.get_action(obs)
        reward = env.step(action)
        history.append(reward)
        
    # Compare with 'No Control' (Classical baseline)
    no_control_history = []
    env_baseline = QuantumEnvironment(gamma=0.3)
    env_baseline.state = basis(2, 1)
    for i in range(30):
        reward = env_baseline.step(0) # Do nothing
        no_control_history.append(reward)

    plt.figure(figsize=(10, 6))
    plt.plot(history, 'b-', lw=2, label='Quantum Agent Control (Active Survival)')
    plt.plot(no_control_history, 'r--', label='Passive Decay (No AI)')
    
    plt.title('Agentic AI: Quantum Autonomous Controller (QAC)')
    plt.xlabel('Time Step')
    plt.ylabel('System Vitality (Excited State Population)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.annotate('Agent Fights Entropy:\nUses quantum logic to\ncorrect decay in real-time', 
                 xy=(15, history[15]), xytext=(5, 0.2),
                 arrowprops=dict(facecolor='black', shrink=0.05))

    plt.savefig('simulations/agentic_ai_qac.png')
    print("Agentic AI Technology saved to simulations/agentic_ai_qac.png")

if __name__ == "__main__":
    simulate_agentic_ai_control()
