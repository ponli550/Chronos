import numpy as np
import matplotlib.pyplot as plt

def simulate_gravitational_wave(M1=30, M2=30, dist_mpc=400):
    """
    Simulates the 'Chirp' signal of a Binary Black Hole merger.
    Using the Post-Newtonian expansion for the frequency and strain.
    M1, M2: Masses in solar masses.
    """
    # Total mass and Chirp mass
    M = M1 + M2
    mu = (M1 * M2) / M
    M_chirp = (mu**(3/5)) * (M**(2/5))
    
    # Constants (in normalized units)
    t_merger = 0.5
    time = np.linspace(0, t_merger - 0.001, 2000)
    tau = t_merger - time # Time to merger
    
    # 1. Instantaneous Frequency: f(tau) ~ tau^(-3/8)
    # Frequency increases as the objects spiral in
    freq = (5 / 256)**(3/8) * (1 / np.pi) * (M_chirp * 4.9e-6)**(-5/8) * tau**(-3/8)
    
    # 2. Phase: phi(tau) = -2 * integral(f(tau') dtau')
    phase = -2 * np.pi * freq * tau / (5/8) # Integration of tau^-3/8
    
    # 3. Strain Amplitude: h(tau) ~ f^(2/3) ~ tau^(-1/4)
    # Amplitude grows as they get closer
    amplitude = (tau + 0.05)**(-1/4) 
    
    # The Gravitational Wave Signal h(t)
    h_t = amplitude * np.cos(phase)
    
    print(f"Simulating Gravitational Wave 'Chirp' (M1={M1}, M2={M2})...")
    
    plt.figure(figsize=(12, 6))
    plt.plot(time, h_t, color='black', lw=1, alpha=0.8)
    
    # Visualization markers
    plt.axvline(t_merger, color='red', linestyle='--', label='Inspiral/Merger Point')
    plt.title(f'General Relativity: Gravitational Wave Signal $h(t)$')
    plt.xlabel('Time (s)')
    plt.ylabel('Strain Amplitude')
    plt.grid(True, alpha=0.2)
    plt.legend()
    
    plt.savefig('simulations/gravitational_waves.png')
    print("Waveform saved to simulations/gravitational_waves.png")

if __name__ == "__main__":
    simulate_gravitational_wave()
