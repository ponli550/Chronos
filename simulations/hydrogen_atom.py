import numpy as np
from scipy import sparse
from scipy.sparse.linalg import eigsh
import matplotlib.pyplot as plt

def solve_hydrogen_radial(n_points=2000, r_max=100, l=0):
    """
    Solves the radial Schrodinger equation for the hydrogen atom using the finite difference method.
    Units: Atomic units (hbar = m = e = 1)
    """
    # Grid in r (staggered grid or avoid r=0)
    # We use r from dr to r_max to avoid the singularity at r=0
    dr = r_max / n_points
    r = np.linspace(dr, r_max, n_points)

    # Hamiltonian Construction (Radial part)
    # Kinetic energy matrix (2nd derivative using finite difference)
    diag = np.ones(n_points)
    diags = np.array([-2*diag, diag, diag])
    D2 = sparse.spdiags(diags, [0, -1, 1], n_points, n_points) / dr**2
    T = -0.5 * D2

    # Potential energy matrix
    V_total = -1.0 / r + l * (l + 1) / (2 * r**2)
    U = sparse.diags(V_total, 0)

    # Hamiltonian
    H = T + U

    # Solve for eigenvalues and eigenvectors
    evals, evecs = eigsh(H, k=4, which='SA')
    return r, evals, evecs

def plot_results(r, evals, evecs, l):
    from scipy.integrate import trapezoid
    plt.figure(figsize=(10, 6))
    
    # Sort evals and evecs
    idx = evals.argsort()
    evals = evals[idx]
    evecs = evecs[:, idx]

    for i in range(len(evals)):
        u = evecs[:, i]
        # Normalize u(r) such that integral |u|^2 dr = 1
        norm = np.sqrt(trapezoid(u**2, r))
        u = u / norm
        
        n = i + l + 1
        e_theory = -1.0 / (2 * n**2)
        
        plt.plot(r, u, label=f'n={n}, l={l} (E={evals[i]:.4f}, Theory={e_theory:.4f})')

    plt.title(f'Radial Wavefunctions u(r) for Hydrogen (l={l})')
    plt.xlabel('r (atomic units $a_0$)')
    plt.ylabel('u(r)')
    plt.xlim(0, 30)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('simulations/hydrogen_radial.png')
    print(f"Plot saved to simulations/hydrogen_radial.png")

def plot_3d_density(r, evals, evecs, n_idx, l, m=0):
    try:
        from scipy.special import sph_harm
    except ImportError:
        # SciPy 1.15+ uses sph_harm_y
        from scipy.special import sph_harm_y as sph_harm
    
    # Sort evals and evecs
    idx = evals.argsort()
    u = evecs[:, idx[n_idx]]
    
    # Normalize u(r)
    from scipy.integrate import trapezoid
    norm = np.sqrt(trapezoid(u**2, r))
    u = u / norm
    
    # Radial wavefunction R(r) = u(r)/r
    R = u / r
    
    # Create 3D grid
    size = 20
    num = 50
    _x = np.linspace(-size, size, num)
    _y = np.linspace(-size, size, num)
    _z = np.linspace(-size, size, num)
    X, Y, Z = np.meshgrid(_x, _y, _z)
    
    R_grid = np.sqrt(X**2 + Y**2 + Z**2)
    Theta_grid = np.arccos(Z / (R_grid + 1e-10))
    Phi_grid = np.arctan2(Y, X)
    
    # Interpolate radial part
    R_interp = np.interp(R_grid, r, R, right=0)
    
    # Angular part
    # Note: sph_harm(m, l, phi, theta) in old scipy
    # sph_harm_y(l, m, theta, phi) in new scipy
    try:
        Y_lm = sph_harm(m, l, Phi_grid, Theta_grid)
    except:
        # Fallback to new API if names were swapped or different
        Y_lm = sph_harm(l, m, Theta_grid, Phi_grid)
    
    # Full wavefunction
    Psi = R_interp * Y_lm
    Density = np.abs(Psi)**2
    
    # Visualization using Matplotlib (Isosurface-like scatter or slices)
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Filter points for better visibility
    mask = Density > (Density.max() * 0.05)
    ax.scatter(X[mask], Y[mask], Z[mask], c=Density[mask], cmap='magma', s=1, alpha=0.1)
    
    n = n_idx + l + 1
    ax.set_title(f'Probability Density (n={n}, l={l}, m={m})')
    plt.savefig(f'simulations/hydrogen_3d_n{n}_l{l}.png')
    print(f"3D Plot saved to simulations/hydrogen_3d_n{n}_l{l}.png")

if __name__ == "__main__":
    l_value = 0
    r, evals, evecs = solve_hydrogen_radial(l=l_value)
    
    print(f"Solving for l={l_value}...")
    for i, e in enumerate(evals):
        n = i + l_value + 1
        e_theory = -1.0 / (2 * n**2)
        print(f"n={n}: Numerical E = {e:.6f}, Theoretical E = {e_theory:.6f}")
    
    plot_results(r, evals, evecs, l_value)
    
    # Plot 3D for n=2, l=0
    plot_3d_density(r, evals, evecs, n_idx=1, l=0)
    
    # Solve for p-orbitals (l=1)
    r1, evals1, evecs1 = solve_hydrogen_radial(l=1)
    plot_3d_density(r1, evals1, evecs1, n_idx=0, l=1, m=0) # 2p state
