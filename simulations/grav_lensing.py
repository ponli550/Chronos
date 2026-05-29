import numpy as np
import matplotlib.pyplot as plt

def simulate_gravitational_lensing(mass=1.0, b_min=0.5, b_max=5.0):
    """
    Simulates Gravitational Lensing (Ray Tracing in curved spacetime).
    Deflection angle alpha = 4GM / (bc^2)
    This creates the 'Einstein Ring' effect seen in Interstellar and Hubble photos.
    """
    # Grid of light rays (impact parameters)
    n_rays = 1000
    b = np.linspace(b_min, b_max, n_rays)
    
    # 1. Calculate Deflection Angle (alpha)
    # Using Einstein's formula for a point mass
    # (Normalized units: G=c=1)
    alpha = 4 * mass / b
    
    # 2. Map Image Position (theta) to Source Position (beta)
    # Lens equation: beta = theta - alpha(theta) * Dls / Ds
    # Assuming Dls / Ds approx 0.5 (source is far behind lens)
    d_ratio = 0.5
    theta = b # Angular position on sky is proportional to impact parameter
    beta = theta - alpha * d_ratio
    
    # 3. Visualization: The Einstein Ring
    # We plot the mapping from sky position to source position
    plt.figure(figsize=(10, 6))
    plt.plot(theta, beta, color='blue', label='Sky Mapping')
    plt.axhline(0, color='k', linestyle='--', alpha=0.3)
    
    # Highlight the Einstein Ring position (where beta = 0)
    # i.e., theta_E = sqrt(4GM * Dls / (Dl * Ds))
    theta_E = np.sqrt(4 * mass * d_ratio)
    plt.axvline(theta_E, color='red', linestyle='--', label=r'Einstein Ring ($\Theta_E$)')
    
    plt.title('Gravitational Lensing: Light Bending in Spacetime')
    plt.xlabel(r'Observed Angle $\Theta$')
    plt.ylabel(r'Source Angle $\beta$')
    plt.legend()
    plt.grid(True, alpha=0.2)
    
    plt.savefig('simulations/gravitational_lensing.png')
    print("Lensing analysis saved to simulations/gravitational_lensing.png")
    
    # 4. Generate 2D Visualization (The Ring)
    # We take a background star and 'lens' it
    res = 400
    sky = np.linspace(-b_max, b_max, res)
    SKY_X, SKY_Y = np.meshgrid(sky, sky)
    THETA = np.sqrt(SKY_X**2 + SKY_Y**2)
    
    # Source position for every pixel
    BETA = THETA - (4 * mass / (THETA + 1e-5)) * d_ratio
    
    # Define a small source at the origin (a distant star)
    source_mask = BETA < 0.2
    
    plt.figure(figsize=(8, 8))
    plt.imshow(source_mask, extent=[-b_max, b_max, -b_max, b_max], cmap='inferno')
    plt.title('Cosmic Lens: The Einstein Ring Visualization')
    plt.axis('off')
    plt.savefig('simulations/einstein_ring.png')
    print("Einstein Ring image saved to simulations/einstein_ring.png")

if __name__ == "__main__":
    simulate_gravitational_lensing(mass=2.0)
