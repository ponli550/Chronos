import numpy as np
import matplotlib.pyplot as plt

def simulate_many_worlds_branching(depth=8):
    """
    Simulates the branching of 'Realities' in the Many-Worlds Interpretation.
    Each quantum event (measurement) splits the universe into two non-interacting branches.
    """
    # We represent the Multiverse as a Binary Tree
    # x: branch position, y: time/depth
    tree_x = [[0]]
    tree_y = [[0]]
    
    print(f"Simulating the Branching of {2**depth} Parallel Realities...")

    for d in range(1, depth + 1):
        prev_x = tree_x[-1]
        new_x = []
        new_y = []
        
        # Every node in the previous level splits into two
        # The 'separation' between branches grows over time (Decoherence)
        offset = 1.0 / (2**d)
        
        for x in prev_x:
            new_x.append(x - offset) # Branch A (e.g., Qubit |0>)
            new_x.append(x + offset) # Branch B (e.g., Qubit |1>)
            new_y.append(d)
            new_y.append(d)
            
        tree_x.append(new_x)
        tree_y.append(new_y)

    # Plotting the "Multiverse Tree"
    plt.figure(figsize=(12, 10))
    
    for d in range(depth):
        xs_curr = tree_x[d]
        xs_next = tree_x[d+1]
        y_curr = tree_y[d][0]
        y_next = tree_y[d+1][0]
        
        for i, x in enumerate(xs_curr):
            # Connect to left child
            plt.plot([x, xs_next[2*i]], [y_curr, y_next], color='blue', alpha=0.5, lw=1)
            # Connect to right child
            plt.plot([x, xs_next[2*i+1]], [y_curr, y_next], color='red', alpha=0.5, lw=1)

    plt.title(f'The Many-Worlds Multiverse: Branching of {2**depth} Realities')
    plt.xlabel('State Space (Decoherence Separation)')
    plt.ylabel('Time / Measurement Events')
    
    # Textual proof of concept
    plt.annotate('Single History (Classical)', xy=(0, 0), xytext=(-0.4, -0.5),
                 arrowprops=dict(facecolor='black', shrink=0.05))
    plt.annotate('Infinite Possible Universes', xy=(0, depth), xytext=(0.1, depth+0.5),
                 ha='center')

    plt.ylim(-1, depth + 1)
    plt.grid(False)
    plt.axis('off')
    
    plt.savefig('simulations/multiverse_branching.png')
    print(f"Multiverse Model saved to simulations/multiverse_branching.png")

if __name__ == "__main__":
    simulate_many_worlds_branching()
