# Quantum Simulations

This directory contains Python simulations for various quantum mechanical systems.

## Available Simulations

### 1. Hydrogen Atom (`hydrogen_atom.py`)
- **Method**: Radial Finite Difference.
- **Features**: 
    - Solves for energy levels and radial wavefunctions.
    - 3D visualization of orbital probability densities ($s$, $p$, $d$, etc.).
- **Results**: Verified against the Bohr model.

### 2. Quantum Harmonic Oscillator (`qho.py`)
- **Method**: 1D Finite Difference.
- **Features**:
    - Calculates eigenvalues and eigenvectors for $V(x) = \frac{1}{2}\omega^2 x^2$.
    - Visualizes wavefunctions shifted by their corresponding energy levels.
- **Results**: Verified against the analytical solution $E_n = (n + 1/2)\hbar\omega$.

### 3. Helium Atom (`helium_atom.py`)
- **Method**: Variational Method.
- **Features**:
    - Uses an effective nuclear charge ($Z_{eff}$) as a variational parameter.
    - Demonstrates electron-electron repulsion effects.
- **Results**: Estimated Ground State Energy $\approx -2.848$ Hartrees (within 2% of experimental value).

### 4. Quantum Tunneling (`tunneling.py`)
- **Method**: Split-Step Fourier Method (SSFM).
- **Features**:
    - Simulates the time evolution of a Gaussian wave packet.
    - Demonstrates tunneling through a rectangular potential barrier.
- **Results**: Produces an animation (`tunneling.gif`) showing reflection and transmission.

### 5. Solid State Physics (`solid_state.py`)
- **Method**: Bloch's Theorem + Finite Difference.
- **Features**:
    - Calculates the dispersion relation $E(k)$ for a periodic potential.
    - Demonstrates the formation of energy bands and forbidden gaps.
- **Results**: Visualizes the first 4 energy bands in the first Brillouin zone.

### 6. Quantum Computing (`quantum_computing.py`)
- **Library**: Qiskit.
- **Features**:
    - Constructs a 2-qubit circuit with Hadamard and CNOT gates.
    - Demonstrates quantum entanglement by creating a Bell State.
- **Results**: Histogram of measurements (`bell_state_histogram.png`) showing 00 and 11 outcomes.

### 7. Quantum Field Theory (`qft_klein_gordon.py`)
- **Equation**: 1+1D Klein-Gordon ($\partial_t^2 \phi - \partial_x^2 \phi + m^2 \phi = 0$).
- **Features**:
    - Simulates the propagation of a massive scalar field.
    - Uses a leapfrog finite-difference scheme.
- **Results**: Animation (`klein_gordon.gif`) showing dispersion and propagation.

### 8. Many-Body Physics (`exchange_interaction.py`)
- **Concept**: Indistinguishable particles and Spin Statistics.
- **Features**:
    - Compares Distinguishable particles, Bosons, and Fermions.
    - Visualizes the "Exchange Hole" for Fermions.
- **Results**: Spatial density plot (`exchange_interaction.png`).

### 9. Relativistic Fermions (`dirac_equation.py`)
- **Equation**: 1+1D Dirac Equation.
- **Features**:
    - Combines Relativity, Quantum Mechanics, and Spin.
    - Demonstrates the coupling between particle and **Anti-particle** components.
- **Results**: Animation (`dirac_antimatter.gif`) showing the evolution of a spinor field.

### 10. Open Quantum Systems (`open_systems.py`)
- **Method**: Lindblad Master Equation (QuTiP).
- **Features**:
    - Simulates interaction with a **Thermal Bath**.
    - Models Decoherence, Relaxation, and Finite Temperature.
- **Results**: Plot of population decay into a thermal steady state (`decoherence_noise.png`).

### 11. Quantum Algorithms (`qft.py`)
- **Algorithm**: Quantum Fourier Transform (QFT).
- **Features**:
    - Implements the recursive gate structure for QFT.
    - Demonstrates frequency encoding in the quantum phase.
- **Results**: Visualizes the uniform probability and periodic phase of a transformed basis state.

### 12. Fault-Tolerant Computing (`qec.py`)
- **Method**: 3-Qubit Bit-Flip Code.
- **Features**:
    - Protects a logical qubit through physical redundancy.
    - Uses **Syndrome Measurement** with ancilla qubits to detect and fix errors.
- **Results**: Proof of successful correction even after a hardware bit-flip.

### 13. Topological Matter (`ssh_topology.py`)
- **Model**: Su-Schrieffer-Heeger (SSH).
- **Features**:
    - Demonstrates topological vs trivial phases in a 1D chain.
    - Visualizes **Edge States** which are robust against local disorder.
- **Results**: Plot of the energy spectrum showing a "gap" and zero-energy edge modes.

### 14. Quantum Biology (`quantum_biology.py`)
- **Complex**: Fenna-Matthews-Olson (FMO).
- **Features**:
    - Simulates coherent energy transfer (excitons) in photosynthesis.
    - Demonstrates how environment-assisted tunneling makes nature efficient.
- **Results**: Time-evolution of energy density moving from input site to the reaction center.

### 15. Topological Fields (`aharonov_bohm.py`)
- **Effect**: Aharonov-Bohm (A-B).
- **Features**:
    - Demonstrates that the **Vector Potential** A has physical effects even where B=0.
    - Visualizes the phase shift of a wave packet passing a solenoid.
- **Results**: Animation (`aharonov_bohm.gif`) showing interference pattern shifts.

### 16. Black Hole Thermodynamics (`hawking_radiation.py`)
- **Model**: Hawking Radiation Toy Model.
- **Features**:
    - Simulates vacuum fluctuations (particle pairs) at an **Event Horizon**.
    - Shows the 'splitting' process: one partner falls in, the other escapes.
- **Results**: Animation (`hawking_radiation.gif`) of emergent radiation from a horizon.

### 17. Nuclear Physics (`beta_decay.py`)
- **Theory**: Fermi's Theory of Beta Decay.
- **Features**:
    - Predicts the energy spectrum of emitted electrons/positrons.
    - Demonstrates the **Weak Nuclear Force**.
- **Results**: Visualizes the continuous spectrum that led to the discovery of the **Neutrino**.

### 17. Information Physics (`mbl_localization.py`)
- **Concept**: Many-Body Localization (MBL).
- **Features**:
    - Simulates a disordered spin chain.
    - Demonstrates the transition from **Thermal/Ergodic** behavior to **Localized** behavior.
- **Results**: Histogram of level-spacing ratios ($r$) proving the localization of information.

### 18. Theoretical Symmetries (`susy_quantum.py`)
- **Theory**: Supersymmetric Quantum Mechanics (SUSY QM).
- **Features**:
    - Constructs two "Partner Hamiltonians" ($H_+$ and $H_-$).
    - Demonstrates the perfect pairing of energy spectra between Bosons and Fermions.
- **Results**: Spectrum plot showing the degeneracy of partner states.

### 19. Quantum Thermodynamics (`quantum_engine.py`)
- **Model**: Single-Qubit Otto Cycle.
- **Features**:
    - Simulates an engine that extracts work from thermal gradients using quantum coherence.
    - Compares quantum efficiency to the classical Carnot limit.
- **Results**: Energy-Frequency diagram of the work-extraction cycle.

### 20. Topological Hardware (`majorana_fermions.py`)
- **Model**: Kitaev Chain (p-wave Superconductor).
- **Features**:
    - Solves for **Majorana Zero Modes** at the ends of a 1D wire.
    - Demonstrates the topological protection of edge modes.
- **Results**: Spatial distribution plot showing particles 'localized' at the boundaries.

### 21. Origin of Mass (`higgs_mechanism.py`)
- **Model**: Spontaneous Symmetry Breaking.
- **Features**:
    - Simulates the 'Mexican Hat' potential of the Higgs Field.
    - Visualizes the non-zero vacuum expectation value (VEV) that gives particles mass.
- **Results**: 3D surface plot and 2D density plot of the vacuum ring (`higgs_mechanism.png`).

### 22. Holographic Quantum Gravity (`syk_holography.py`)
- **Model**: Sachdev-Ye-Kitaev (SYK) Model.
- **Features**:
    - All-to-all interacting Majorana fermions modeling 'Maximal Chaos'.
    - Demonstrates the AdS/CFT correspondence (holographic dual to a 1D black hole).
- **Results**: Density of states histogram matching black hole thermodynamics.

### 23. Lattice Gauge Theory (`lattice_gauge.py`)
- **Model**: Toy Toric Code ($Z_2$ Spin Liquid).
- **Features**:
    - Demonstrates true Topological Order.
    - Ground state is a macroscopic superposition of string loops.
- **Results**: Energy spectrum showing the topologically protected ground state manifold.

### 24. Time Crystals (`time_crystal.py`)
- **Concept**: Discrete Time Crystal (DTC).
- **Features**:
    - Simulates a **Floquet** driven many-body system.
    - Demonstrates the breaking of Time-Translation Symmetry.
- **Results**: Magnetization plot showing sub-harmonic oscillations (Period-2 response).

### 25. Quantum AI Research (`qcnn_research.py`)
- **Architecture**: Quantum Convolutional Neural Network (QCNN).
- **Features**:
    - Implements quantum convolutional and pooling layers.
    - Designed to classify topological phases of matter.
- **Results**: Successfully distinguishes between entangled and product states via measurement.

### 26. Precision Cosmology (`cosmology_cmb.py`)
- **Observation**: Cosmic Microwave Background (CMB) Power Spectrum.
- **Features**:
    - Simulates the acoustic oscillations of the early universe.
    - Demonstrates how peak positions reveal curvature, baryon density, and dark matter.
- **Results**: Visualizes the $D_l$ power spectrum from multipole $l=2$ to $2500$.

### 27. Gravitational Waves (`gravitational_waves.py`)
- **Event**: Binary Black Hole Merger (Inspiral Phase).
- **Features**:
    - Calculates the 'Chirp' signal using Post-Newtonian expansion.
    - Models the increasing frequency and amplitude as objects spiral inward.
- **Results**: Plot of the strain signal $h(t)$ identical to the LIGO detections.

### 28. Multiverse Theory (`multiverse.py`)
- **Concept**: Many-Worlds Interpretation (MWI).
- **Features**:
    - Simulates the exponential branching of realities during quantum measurements.
    - Demonstrates **Decoherence** as the mechanism that separates branches.
- **Results**: Visual representation of the 'Multiverse Tree' showing $2^N$ parallel histories.

### 29. The Quantum Eraser (`quantum_eraser.py`)
- **Concept**: Information-Reality Link.
- **Features**:
    - Simulates the **Delayed Choice** logic where 'which-path' information determines behavior.
    - Demonstrates that erasing information *after* detection can restore interference fringes in correlated data.
- **Results**: Plot comparing 'No Erasure' (Particle behavior) vs 'Eraser Active' (Wave behavior).

### 30. Invisibility Cloaking (`invisibility_cloak.py`)
- **Method**: Transformation Optics (Ray Tracing).
- **Features**:
    - Simulates a **Metamaterial** with an engineered refractive index.
    - Demonstrates bending light rays around a hidden central region.
- **Results**: Ray-trace diagram showing light 'cloaking' an object.

### 31. The Star Engine (`nuclear_fusion.py`)
- **Concept**: Quantum Tunneling in Fusion (Gamow Peak).
- **Features**:
    - Models the balance between thermal energy and the Coulomb barrier.
    - Predicts the **Gamow Window**—the specific energy where stars fuse atoms.
- **Results**: Plot showing how tunneling makes life possible at lower-than-expected temperatures.

### 30. Wormhole Teleportation (`wormhole_epr.py`)
- **Concept**: ER=EPR Conjecture.
- **Features**:
    - Simulates a **Traversable Wormhole** on a quantum circuit (Google Sycamore Protocol).
    - Demonstrates the connection between entanglement and spacetime shortcuts.
- **Results**: Transmission of a qubit from 'Left' to 'Right' side via a gravitational bridge.

### 31. Information Thermodynamics (`maxwell_demon.py`)
- **Model**: Maxwell's Demon.
- **Features**:
    - Simulates a microscopic entity that sorts particles to reduce entropy.
    - Demonstrates **Landauer's Principle**: information erasure has a physical cost.
- **Results**: Plot showing total entropy remains constant/increases when info cost is included.

### 32. Quantum Game Theory (`quantum_game_theory.py`)
- **Model**: Quantum Prisoners' Dilemma (EWL Protocol).
- **Features**:
    - Demonstrates how **Entanglement** changes the rules of strategic interaction.
    - Shows the 'Quantum Miracle' where cooperation becomes a dominant strategy.
- **Results**: Payoff calculation proving quantum strategies beat classical ones.

### 33. Non-Hermitian Physics (`non_hermitian.py`)
- **Concept**: Exceptional Points ($EP$).
- **Features**:
    - Simulates a system with Gain and Loss (PT-symmetry).
    - Demonstrates the merging of energy levels at a specific point.
- **Results**: Plot showing the real and imaginary spectrum of a non-Hermitian Hamiltonian.

### 34. The "Speed Force" (`flash_physics.py`)
- **Theory**: Special Relativity (The 50th Module).
- **Features**:
    - Calculates **Time Dilation** and **Relativistic Doppler Shift**.
    - Models the physics of a runner approaching the speed of light.
- **Results**: Visualization of the Lorentz Factor ($\gamma$) and color shifts from green to UV/Infrared.

### 35. New Technology: Topological Quantum Battery (`tech_quantum_battery.py`)
- **Concept**: Sustainable Quantum Energy Storage.
- **Features**:
    - Uses **Topological Edge States** to store energy robustly.
    - Demonstrates 'Topological Protection'—energy refuses to leak into the bulk material.
- **Results**: Charging curve showing zero-degradation energy retention.

### 36. Agentic AI: Quantum Autonomous Controller (`agentic_ai_qac.py`)
- **Architecture**: Variational Quantum Circuit (VQC) Agent.
- **Features**:
    - An AI agent with a **Quantum Brain** that learns to control a physical environment.
    - Autonomously stabilizes a decaying quantum system (Qubit) against noise.
- **Results**: Comparative plot showing the agent 'fighting entropy' to maintain system vitality.

### 37. Space Technology: Quantum Satellite (`quantum_satellite.py`)
- **Protocol**: BB84 (Quantum Key Distribution).
- **Features**:
    - Simulates secure key exchange between a satellite and a ground station.
    - Models **Atmospheric Loss** and random basis choices.
- **Results**: Successfully generates an unbreakable encryption key across space.

## Running Simulations
Ensure the virtual environment is activated:
```bash
./quantum_physics_python/.venv/bin/python simulations/<filename>.py
```
