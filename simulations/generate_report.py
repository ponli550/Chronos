import json
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

def generate_report(log_path):
    if not os.path.exists(log_path):
        print(f"Error: Log file {log_path} not found.")
        return

    with open(log_path, 'r') as f:
        data = json.load(f)

    if not data:
        print("Error: Log file is empty.")
        return

    # Extract metrics
    timestamps = [d['timestamp'] for d in data]
    t_start = timestamps[0]
    time_s = [(t - t_start) / 1000 for t in timestamps]
    
    speed = [d['speed_kmh'] for d in data]
    gamma = [d['gamma'] for d in data]
    dilation = [d['time_dilation_ns'] for d in data]
    alt = [d.get('altitude', 0) for d in data]

    # Create high-fidelity plot
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Project Chronos-X: Relativistic Trip Report', fontsize=20, fontweight='bold', color='#00cfd5')
    plt.style.use('dark_background')

    # 1. Velocity Profile
    axs[0, 0].plot(time_s, speed, color='cyan', lw=2)
    axs[0, 0].set_title('Velocity Profile')
    axs[0, 0].set_ylabel('Speed (km/h)')
    axs[0, 0].grid(alpha=0.2)

    # 2. Lorentz Factor (Gamma)
    axs[0, 1].plot(time_s, gamma, color='orange', lw=2)
    axs[0, 1].set_title('Lorentz Factor ($\gamma$)')
    axs[0, 1].set_ylabel('$\gamma$ Value')
    axs[0, 1].grid(alpha=0.2)

    # 3. Time Dilation (Twin Paradox)
    cumulative_ns = np.cumsum(dilation) * 0.5 # 0.5s sampling
    axs[1, 0].fill_between(time_s, cumulative_ns, color='pink', alpha=0.3)
    axs[1, 0].plot(time_s, cumulative_ns, color='pink', lw=2)
    axs[1, 0].set_title('Cumulative Time Divergence')
    axs[1, 0].set_ylabel('Total ns Saved')
    axs[1, 0].grid(alpha=0.2)

    # 4. Altitude GR Profile
    axs[1, 1].plot(time_s, alt, color='lime', lw=2)
    axs[1, 1].set_title('Gravitational Geodesic (Altitude)')
    axs[1, 1].set_ylabel('Altitude (m)')
    axs[1, 1].grid(alpha=0.2)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    report_name = f"research_report_{int(t_start)}.png"
    plt.savefig(report_name)
    print(f"\n[STATION LOG] Research report generated: {report_name}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        generate_report(sys.argv[1])
    else:
        print("Usage: python generate_report.py <path_to_logbook.json>")
