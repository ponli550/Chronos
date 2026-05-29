import numpy as np
import matplotlib.pyplot as plt

def simulate_path_integral(n_paths=5000, n_slices=50, t_final=1.0):
    """
    Simulates the 1D Feynman Path Integral for a free particle.
    The kernel K(x_f, x0, T) is the sum over ALL possible paths.
    Using Path Integral Monte Carlo (Metropolis algorithm).
    """
    x0 = 0.0
    xf = 1.0
    dt = t_final / n_slices
    
    # Initial path: Straight line from x0 to xf
    path = np.linspace(x0, xf, n_slices + 1)
    
    def get_action(p):
        """Action S = integral (1/2 * m * v^2 - V) dt"""
        # Kinetic part: 1/2 * sum((dx/dt)^2) * dt
        v = np.diff(p) / dt
        S = 0.5 * np.sum(v**2) * dt
        return S

    # Metropolis Algorithm: Mutate the path to sample the distribution exp(iS)
    # Note: In imaginary time (Euclidean PI), we sample exp(-S) which is easier.
    # Here we use Euclidean PI to find the ground state/kernel shape.
    history = []
    current_action = get_action(path)
    
    print(f"Sampling {n_paths} paths using Path Integral Monte Carlo...")
    
    for i in range(n_paths):
        # Pick a random point on the path (excluding ends) and move it
        idx = np.random.randint(1, n_slices)
        old_val = path[idx]
        path[idx] += np.random.normal(0, 0.1)
        
        new_action = get_action(path)
        
        # Accept/Reject based on exp(-delta_S)
        if np.random.rand() < np.exp(-(new_action - current_action)):
            current_action = new_action
        else:
            path[idx] = old_val # Reject
            
        if i % 10 == 0:
            history.append(path.copy())
            
    return history

def plot_paths(history, n_slices):
    plt.figure(figsize=(10, 6))
    
    # Plot a subset of paths to show the "Sum over Histories"
    for p in history[::20]:
        plt.plot(np.linspace(0, 1, n_slices+1), p, color='blue', alpha=0.05)
        
    # The "Classical" path
    plt.plot([0, 1], [0, 1], 'r--', lw=2, label='Classical Path (Least Action)')
    
    plt.title('Feynman Path Integral: The Sum Over All Possible Histories')
    plt.xlabel('Time $t$')
    plt.ylabel('Position $x$')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('simulations/path_integral_histories.png')
    print("Plot saved to simulations/path_integral_histories.png")

if __name__ == "__main__":
    hist = simulate_path_integral()
    plot_paths(hist, 50)
