import numpy as np
import matplotlib.pyplot as plt

def simulate_invisibility_cloak(n_rays=20, L=10, R_inner=2.0, R_outer=5.0):
    """
    Simulates an Invisibility Cloak using Transformation Optics (Ray Tracing).
    The metamaterial bends light rays around a hidden inner region R_inner.
    """
    # 1. Setup rays starting from the left
    y_starts = np.linspace(-L*0.8, L*0.8, n_rays)
    dt = 0.05
    steps = 400
    
    plt.figure(figsize=(10, 10))
    
    # 2. Draw the Cloak Boundaries
    circle_inner = plt.Circle((0, 0), R_inner, color='gray', alpha=0.3, label='Hidden Region')
    circle_outer = plt.Circle((0, 0), R_outer, color='blue', fill=False, linestyle='--', label='Cloak Boundary')
    plt.gca().add_patch(circle_inner)
    plt.gca().add_patch(circle_outer)

    print(f"Simulating light rays through a Metamaterial Invisibility Cloak...")

    for y0 in y_starts:
        x, y = -L, y0
        vx, vy = 1.0, 0.0 # Moving right
        
        x_hist = [x]
        y_hist = [y]
        
        for _ in range(steps):
            r = np.sqrt(x**2 + y**2)
            
            # The 'Transformation' Law:
            # Inside the cloak (R_inner < r < R_outer), the index of refraction 
            # is engineered to compress space.
            if R_inner < r < R_outer:
                # Radial transformation: r' = R_inner + r * (R_outer - R_inner) / R_outer
                # We simulate the bending by applying a force toward the edges
                # (Simple ray-tracing approximation for visualization)
                
                # Normal vector from origin
                nx, ny = x/r, y/r
                
                # Bending force to steer around the inner radius
                # The closer to the inner boundary, the stronger the push
                factor = (R_outer - r) / (r - R_inner + 0.1)
                vx += nx * factor * 0.05
                vy += ny * factor * 0.05
                
                # Normalize velocity to keep speed c constant
                v_mag = np.sqrt(vx**2 + vy**2)
                vx /= v_mag
                vy /= v_mag
            
            # Move
            x += vx * dt
            y += vy * dt
            
            x_hist.append(x)
            y_hist.append(y)
            
            if x > L: break

        plt.plot(x_hist, y_hist, color='cyan', alpha=0.6, lw=1)

    plt.title('Transformation Optics: An Invisibility Cloak Metamaterial')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.xlim(-L, L)
    plt.ylim(-L, L)
    plt.grid(True, alpha=0.1)
    plt.legend()
    plt.savefig('simulations/invisibility_cloak.png')
    print("Invisibility simulation saved to simulations/invisibility_cloak.png")

if __name__ == "__main__":
    simulate_invisibility_cloak()
