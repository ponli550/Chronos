import numpy as np
import matplotlib.pyplot as plt

def simulate_cmb_power_spectrum():
    """
    Simulates the CMB Power Spectrum (Cl coefficients).
    The peaks represent 'Acoustic Oscillations' in the early universe plasma.
    """
    l = np.linspace(2, 2500, 1000)
    
    # 1. The First Peak (Scale of the Universe)
    # Determined by the sound horizon at recombination
    peak1_pos = 220
    peak1_amp = 5000
    peak1_width = 100
    c1 = peak1_amp * np.exp(-(l - peak1_pos)**2 / (2 * peak1_width**2))
    
    # 2. Subsequent Acoustic Peaks (Baryon Loading)
    # The ratio of peak heights tells us about the amount of normal matter (Baryons)
    peak2_pos = 540
    peak2_amp = 2500
    c2 = peak2_amp * np.exp(-(l - peak2_pos)**2 / (2 * 150**2))
    
    peak3_pos = 800
    peak3_amp = 2000
    c3 = peak3_amp * np.exp(-(l - peak3_pos)**2 / (2 * 200**2))
    
    # 3. Silk Damping (High-l tail)
    # Photons wash out small-scale fluctuations
    damping = np.exp(-(l / 1200)**1.5)
    
    # 4. Integrated Sachs-Wolfe (Low-l tail)
    # Effect of Dark Energy on photon paths
    low_l = 1000 / (l + 2)
    
    # Combined Power Spectrum Cl * l(l+1) / 2pi
    Cl_scaled = (c1 + c2 + c3 + low_l) * damping
    
    print("Predicting Cosmic Microwave Background (CMB) Power Spectrum...")
    print(f"Primary Acoustic Peak located at l ~ {peak1_pos}")
    
    plt.figure(figsize=(10, 6))
    plt.plot(l, Cl_scaled, color='darkblue', lw=2, label='Simulated CMB Spectrum')
    
    # Theoretical Significance markers
    plt.annotate('1st Peak: Spatial Curvature', xy=(220, 5000), xytext=(500, 5500),
                 arrowprops=dict(arrowstyle="->"))
    plt.annotate('2nd Peak: Baryon Density', xy=(540, 2500), xytext=(800, 3500),
                 arrowprops=dict(arrowstyle="->"))
    
    plt.title('Cosmology: The Fingerprint of the Big Bang (CMB Power Spectrum)')
    plt.xlabel('Multipole Moment $l$ (Angular Scale)')
    plt.ylabel(r'$D_l = l(l+1)C_l / 2\pi$ [$\mu K^2$]')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.savefig('simulations/cosmology_cmb.png')
    print("Prediction saved to simulations/cosmology_cmb.png")

if __name__ == "__main__":
    simulate_cmb_power_spectrum()
