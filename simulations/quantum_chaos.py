import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import eigsh
from scipy import sparse

def solve_quantum_billiard(N=128):
    """
    Simulates a 'Quantum Billiard' (Bunimovich Stadium).
    This demonstrates Quantum Chaos where the shape of the boundary 
    determines the 'chaotic' nature of the eigenstates.
    """
    x = np.linspace(-1, 1, N)
    dx = x[1] - x[0]
    X, Y = np.meshgrid(x, x)
    
    # Define a Stadium Shape: Two semi-circles connected by a rectangle
    # r = 0.5, length = 0.5
    mask = np.zeros((N, N), dtype=bool)
    # Rectangle part
    mask[(np.abs(X) < 0.25) & (np.abs(Y) < 0.5)] = True
    # Circle parts
    mask[((X - 0.25)**2 + Y**2 < 0.5**2)] = True
    mask[((X + 0.25)**2 + Y**2 < 0.5**2)] = True
    
    # Flatten mask for matrix operations
    mask_flat = mask.flatten()
    indices = np.where(mask_flat)[0]
    n_valid = len(indices)
    
    # 2D Finite Difference Laplacian on the stadium grid
    # We only solve for points inside the stadium (Dirichlet boundary)
    diag = np.ones(n_valid)
    
    # To keep it simple, we'll use a sparse matrix on the full grid and then slice it
    # Or just use the 2D Laplacian operator
    e = np.ones(N)
    D1 = sparse.spdiags([e, -2*e, e], [-1, 0, 1], N, N)
    D2 = sparse.kronsum(D1, D1) / dx**2
    
    # Slice the Laplacian to only include valid (inside stadium) points
    H = -0.5 * D2.tocsr()[indices, :][:, indices]
    
    print(f"Solving Quantum Stadium Billiard ({n_valid} interior points)...")
    evals, evecs = eigsh(H, k=20, which='SA')
    
    return X, Y, mask, evals, evecs, indices

def plot_chaos(X, Y, mask, evals, evecs, indices):
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    for i, idx_state in enumerate([0, 9, 19]):
        psi_full = np.zeros(mask.shape)
        psi_full.flat[indices] = evecs[:, idx_state]
        
        im = axes[i].imshow(np.abs(psi_full)**2, extent=[-1, 1, -1, 1], cmap='hot', origin='lower')
        axes[i].set_title(f'State {idx_state+1} (E={evals[idx_state]:.2f})')
        axes[i].axis('off')
        
    plt.suptitle('Quantum Chaos: Eigenstates of a Bunimovich Stadium')
    plt.savefig('simulations/quantum_chaos_stadium.png')
    print("Plot saved to simulations/quantum_chaos_stadium.png")

if __name__ == "__main__":
    X, Y, mask, evals, evecs, indices = solve_quantum_billiard()
    plot_chaos(X, Y, mask, evals, evecs, indices)
