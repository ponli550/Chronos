import numpy as np
import matplotlib.pyplot as plt

def simulate_flash_speed_dilation(v_over_c=0.99):
    """
    Simulates the 'The Flash' effect using Special Relativity.
    Calculates Time Dilation (Gamma) and the Relativistic Doppler Shift.
    v_over_c: Velocity as a fraction of the speed of light.
    """
    # 1. The Lorentz Factor (Gamma)
    # gamma = 1 / sqrt(1 - v^2/c^2)
    # This determines how much time "slows down" for the runner.
    gamma = 1.0 / np.sqrt(1 - v_over_c**2)
    
    # 2. Relativistic Doppler Shift (Color Shift)
    # f_observed = f_source * sqrt((1 + v/c) / (1 - v/c)) for approaching
    # We'll calculate the wavelength shift for visible light (e.g., 550nm green)
    lambda_source = 550 # nm (Green)
    # Approaching (Blueshift)
    lambda_approaching = lambda_source * np.sqrt((1 - v_over_c) / (1 + v_over_c))
    # Receding (Redshift)
    lambda_receding = lambda_source * np.sqrt((1 + v_over_c) / (1 - v_over_c))
    
    print(f"--- The Flash Physics (v = {v_over_c}c) ---")
    print(f"Lorentz Factor (Gamma): {gamma:.4f}")
    print(f"Time Dilation: 1 second for Flash = {gamma:.2f} seconds for the world.")
    print(f"Color Shift (Green -> ?): Approaching = {lambda_approaching:.2f}nm, Receding = {lambda_receding:.2f}nm")

    # 3. Visualizing Time Dilation over Velocity
    v_vals = np.linspace(0, 0.999, 500)
    gamma_vals = 1.0 / np.sqrt(1 - v_vals**2)
    
    plt.figure(figsize=(10, 6))
    plt.plot(v_vals, gamma_vals, color='red', lw=2, label=r'Time Dilation Factor ($\gamma$)')
    plt.fill_between(v_vals, 1, gamma_vals, color='red', alpha=0.1)
    
    # Highlight the Flash's speed
    plt.plot(v_over_c, gamma, 'ko')
    plt.annotate(f'Flash at {v_over_c}c\nTime slows by {gamma:.1f}x', 
                 xy=(v_over_c, gamma), xytext=(v_over_c-0.3, gamma+10),
                 arrowprops=dict(facecolor='black', shrink=0.05))
    
    plt.title('Special Relativity: The "Speed Force" (Time Dilation)')
    plt.xlabel('Velocity (Fraction of c)')
    plt.ylabel(r'Time Dilation Factor $\gamma$')
    plt.ylim(1, 30)
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.savefig('simulations/flash_relativity.png')
    print("Relativity analysis saved to simulations/flash_relativity.png")

if __name__ == "__main__":
    # If Flash runs at 99.9% the speed of light
    simulate_flash_speed_dilation(v_over_c=0.995)
