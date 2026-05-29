import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

C = 299792458

VEHICLES = {
    "car":       {"label": "Sports Car",     "speed_kmh": 120,   "color": "#3b82f6"},
    "jet":       {"label": "Fighter Jet",    "speed_kmh": 2400,  "color": "#f59e0b"},
    "rocket":    {"label": "Space Rocket",   "speed_kmh": 28000, "color": "#ef4444"},
    "warp":      {"label": "Warp Drive",     "speed_kmh": None,  "color": "#a855f7"},
}

def simulate_relativistic_dashboard(vehicle="car", speed_kmh=0, distance_km=100, duration_s=60):
    if vehicle == "warp":
        v = 0.95 * C
    elif speed_kmh > 0:
        v = speed_kmh / 3.6
    else:
        v = VEHICLES[vehicle]["speed_kmh"] / 3.6

    label = VEHICLES[vehicle]["label"] if vehicle in VEHICLES else "Custom"
    color = VEHICLES[vehicle]["color"] if vehicle in VEHICLES else "#10b981"

    dest_m = distance_km * 1000
    t = np.linspace(0, duration_s, max(100, duration_s * 2))
    beta = v / C
    gamma = 1.0 / np.sqrt(1.0 - beta**2) if beta < 1.0 else float("inf")
    time_dilation_ns = (1.0 - 1.0 / gamma) * 1e9 if gamma != float("inf") else 1e9
    contracted_m = dest_m / gamma if gamma != float("inf") else 0

    proper_time_s = t / gamma if gamma != float("inf") else np.zeros_like(t)
    classical_time_s = dest_m / v if v > 0 else float("inf")
    relativistic_time_s = classical_time_s / gamma if gamma != float("inf") else 0

    # Quantum ETA
    delta_v = v * 0.05
    delta_t = (dest_m / (v**2)) * delta_v if v > 0 else 1
    eta_grid = np.linspace(0, classical_time_s * 2, 200)
    eta_prob = np.exp(-((eta_grid - classical_time_s) ** 2) / (2 * delta_t**2))
    eta_prob /= np.trapezoid(eta_prob, eta_grid)

    fig = plt.figure(figsize=(14, 8), facecolor="#0f172a")
    gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.30)

    # -- Top-left: Gamma + Time Dilation --
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor("#1e293b")
    ax1.plot(t, np.full_like(t, gamma), color=color, lw=2.5, label=f"γ = {gamma:.4f}")
    ax1.fill_between(t, 0, np.full_like(t, gamma), color=color, alpha=0.08)
    ax1_twin = ax1.twinx()
    ax1_twin.plot(t, np.full_like(t, time_dilation_ns), color="#f472b6", lw=2, ls="--",
                  label=f"Dilation {time_dilation_ns:.2f} ns/s")
    ax1.set_title("Lorentz Factor & Time Dilation", color="white", fontsize=11)
    ax1.set_xlabel("Coordinate Time (s)", color="#94a3b8", fontsize=9)
    ax1.set_ylabel("γ", color=color, fontsize=10)
    ax1_twin.set_ylabel("ns / s", color="#f472b6", fontsize=10)
    ax1.tick_params(colors="#94a3b8"); ax1_twin.tick_params(colors="#94a3b8")
    for spine in ax1.spines.values(): spine.set_color("#334155")
    for spine in ax1_twin.spines.values(): spine.set_color("#334155")

    # -- Top-center: Length Contraction --
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.set_facecolor("#1e293b")
    ax2.bar(["Classical", "Relativistic"], [dest_m / 1000, contracted_m / 1000],
            color=["#475569", color], width=0.5, edgecolor="white", linewidth=0.5)
    ax2.set_title("Length Contraction", color="white", fontsize=11)
    ax2.set_ylabel("Distance (km)", color="#94a3b8", fontsize=10)
    ax2.tick_params(colors="#94a3b8")
    for spine in ax2.spines.values(): spine.set_color("#334155")
    ax2.text(0, dest_m / 1000 * 1.05, f"{dest_m/1000:.0f} km", ha="center", color="#94a3b8", fontsize=9)
    ax2.text(1, contracted_m / 1000 * 1.05, f"{contracted_m/1000:.1f} km", ha="center", color=color, fontsize=9)

    # -- Top-right: Travel Time Comparison --
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.set_facecolor("#1e293b")
    classical_m, relativistic_m = classical_time_s / 60, relativistic_time_s / 60
    ax3.bar(["Classical", "Relativistic"], [classical_m, relativistic_m],
            color=["#475569", color], width=0.5, edgecolor="white", linewidth=0.5)
    ax3.set_title("Travel Time to Destination", color="white", fontsize=11)
    ax3.set_ylabel("Minutes", color="#94a3b8", fontsize=10)
    ax3.tick_params(colors="#94a3b8")
    for spine in ax3.spines.values(): spine.set_color("#334155")
    saved = classical_m - relativistic_m
    ax3.text(1, relativistic_m * 1.05, f"{relativistic_m:.2f} min", ha="center", color=color, fontsize=9)
    ax3.text(0.5, max(classical_m, relativistic_m) * 0.7,
             f"You save\n{saved:.2f} min", ha="center", color="#fbbf24", fontsize=11, fontweight="bold")

    # -- Bottom-left: Proper Time Accumulation --
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.set_facecolor("#1e293b")
    ax4.plot(t, proper_time_s, color="#34d399", lw=2)
    ax4.fill_between(t, 0, proper_time_s, color="#34d399", alpha=0.1)
    ax4.set_title("Proper Time Elapsed", color="white", fontsize=11)
    ax4.set_xlabel("Coordinate Time (s)", color="#94a3b8", fontsize=9)
    ax4.set_ylabel("Proper Time (s)", color="#94a3b8", fontsize=10)
    ax4.tick_params(colors="#94a3b8")
    for spine in ax4.spines.values(): spine.set_color("#334155")

    # -- Bottom-center: Quantum ETA --
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.set_facecolor("#1e293b")
    ax5.plot(eta_grid / 60, eta_prob, color="#c084fc", lw=2)
    ax5.fill_between(eta_grid / 60, 0, eta_prob, color="#c084fc", alpha=0.15)
    ax5.axvline(classical_time_s / 60, color="#f87171", ls="--", lw=1, label="Classical ETA")
    ax5.set_title("Quantum ETA Probability", color="white", fontsize=11)
    ax5.set_xlabel("Arrival Time (min)", color="#94a3b8", fontsize=9)
    ax5.set_ylabel("Probability Density", color="#94a3b8", fontsize=10)
    ax5.tick_params(colors="#94a3b8")
    for spine in ax5.spines.values(): spine.set_color("#334155")
    ax5.legend(fontsize=7, labelcolor="#94a3b8")

    # -- Bottom-right: Info Panel --
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.axis("off")
    ax6.set_facecolor("#1e293b")
    info = [
        f"Vehicle:  {label}",
        f"Speed:    {v*3.6:.0f} km/h" if v*3.6 < 1e6 else f"Speed:    {v/C:.4f} c",
        f"Beta:     {beta:.6f}",
        f"Gamma:    {gamma:.4f}",
        f"Distance: {distance_km} km",
        f"Time Dilation:   {time_dilation_ns:.4f} ns/s",
        f"Length Contr.:   {dest_m - contracted_m:.1f} m",
        f"Time Saved:     {saved:.2f} min",
        f"Proper/Coord:   {1/gamma:.6f}" if gamma != float("inf") else "",
    ]
    ax6.text(0.05, 0.95, "\n".join(info), transform=ax6.transAxes,
             fontfamily="monospace", fontsize=10, color="#cbd5e1",
             verticalalignment="top", linespacing=1.6)

    fig.suptitle(f"Chronos-X Relativistic Dashboard — {label}",
                 color="white", fontsize=14, fontweight="bold", y=0.98)
    fig.savefig("simulations/relativistic_dashboard.png", dpi=150, bbox_inches="tight",
                facecolor="#0f172a")
    plt.close()

    return {
        "gamma": gamma,
        "beta": beta,
        "speed_ms": v,
        "time_dilation_ns": time_dilation_ns,
        "contracted_km": contracted_m / 1000,
        "classical_time_min": classical_time_s / 60,
        "relativistic_time_min": relativistic_time_s / 60,
        "time_saved_min": saved,
    }

if __name__ == "__main__":
    import sys
    vehicle = sys.argv[1] if len(sys.argv) > 1 else "car"
    simulate_relativistic_dashboard(vehicle=vehicle)
