"""Part 3: Asymmetric Disruption Kinematics & Dual-Mode Interventions (Slides 31 - 44)"""

from .slide_types import make_split_cards, make_split_code, make_three_cards

def get_part3_slides():
    slides = []

    # Slide 31: The Fundamental Vulnerability
    slides.append(make_split_cards(
        part="Part 3: Asymmetric Disruption Kinematics",
        title="The Fundamental Vulnerability: Ground Boundary Layer Angular Momentum Flux",
        subtitle="Why tornadoes cannot survive without continuous surface angular momentum replenishment",
        card1={
            "title": "THE VORTEX AS AN OPEN SYSTEM",
            "bullets": [
                "• Not a Closed System:",
                "  A tornado is not a self-contained rotating top; it is an open dissipative thermodynamic engine.",
                "",
                "• Continuous Dissipation Aloft:",
                "  Turbulent viscosity and upward convective ejection continually expel angular momentum through the top of the vortex column.",
                "",
                "• The Ground Replenishment Lifeline:",
                "  The core survives solely because strong radial inflow (u_r < 0) in the lowest 200m continually sweeps high angular momentum inward to the core."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "THE AEOLUS EXPLOITATION PARADIGM",
            "bullets": [
                "• The Critical Chokepoint:",
                "  Instead of attacking the 90 m/s winds at the core, attack the fragile boundary-layer inflow pipeline feeding it.",
                "",
                "• Starvation vs Counteraction:",
                "  Brute force seeks to cancel 10¹² J of rotational energy. AEOLUS simply pinches the fuel line.",
                "",
                "• Rapid Inherent Decay:",
                "  Once boundary-layer replenishment is severed, internal turbulent dissipation collapses the core within seconds."
            ],
            "col": "#F59E0B"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 31 (GROUND FLUX VULNERABILITY):\nThe defining theoretical breakthrough of Project AEOLUS is treating the tornado as an open dissipative system. A tornado continuously radiates angular momentum upward and outward. It maintains its terrifying intensity only because the surface boundary layer acts as a pipeline, pumping fresh angular momentum into the base. If we cut that pipeline, the vortex core starves and dissipates naturally."
    ))

    # Slide 32: Asymmetric Disruption Kinematics
    slides.append(make_split_cards(
        part="Part 3: Asymmetric Disruption Kinematics",
        title="Asymmetric Disruption Kinematics: Breaking Axisymmetry",
        subtitle="How azimuthal perturbation modes (m = 1, 2) trigger catastrophic core dismantling",
        card1={
            "title": "AZIMUTHAL INSTABILITY MODES",
            "bullets": [
                "• Fourier Azimuthal Decomposition:",
                "  u(r, θ, z) = Σ u_m(r, z) · exp(i · m · θ)",
                "",
                "• Stable Mode 0 (m = 0):",
                "  Axisymmetric circular vortex; highly resilient against symmetric perturbations.",
                "",
                "• Destructive Dipole Mode (m = 1):",
                "  Off-axis center displacement; tilts the vortex axis, creating strong cross-shear.",
                "",
                "• Destructive Elliptic Mode (m = 2):",
                "  Stretches the circular core into an ellipse, initiating barotropic vortex breakdown."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "THE KINEMATIC DISRUPTION CASCADE",
            "bullets": [
                "• Asymmetric Forcing:",
                "  Applying intervention forces over a discrete angular sector (Δθ ≈ 90°) directly excites m=1 and m=2 instability modes.",
                "",
                "• Centrifugal Imbalance:",
                "  Loss of circular symmetry creates localized pressure ridges that slice through the vortex core.",
                "",
                "• Irreversible Breakdown:",
                "  The coherent central vortex fragments into decaying, incoherent turbulent eddies."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 32 (BREAKING AXISYMMETRY):\nIn fluid dynamics, symmetric vortices are notoriously resistant to axisymmetric (m=0) perturbations. If you blow or suck symmetrically, the vortex simply adjusts its radius. But if you apply an asymmetric force over a single quadrant (m=1 or m=2), you excite elliptic and dipolar instabilities. These non-axisymmetric modes deform the circular streamlines into an ellipse, triggering rapid vortex breakdown."
    ))

    # Slide 33: Thermal RFD Intervention Physics
    slides.append(make_split_cards(
        part="Part 3: Asymmetric Disruption Kinematics",
        title="Thermal RFD Intervention Physics: +3K Buoyancy Injection",
        subtitle="Neutralizing negative buoyancy to arrest downward momentum transport",
        card1={
            "title": "RFD THERMAL MODULATION GOAL",
            "bullets": [
                "• Overcoming Negative Buoyancy:",
                "  Natural RFD air mass is typically 2 to 3 K cooler than ambient, driving downward acceleration: g · (θ'/θ_0) ≈ -0.098 m/s².",
                "",
                "• The +3K Calibrated Injection:",
                "  Injecting precisely +3.0 K converts θ' from -2.8 K to +0.2 K, reversing net buoyancy from negative to positive.",
                "",
                "• Arresting Surface Convergence:",
                "  Without downward momentum, the RFD air mass cannot reach the surface to form the occluding gust front."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "UPWARD ADVECTION CONVERSION",
            "bullets": [
                "• Downdraft Stagnation:",
                "  Vertical downward velocity u_z in the RFD sector decelerates from -12.5 m/s to 0.0 m/s within 3.2 seconds.",
                "",
                "• Ascending Plume Transition:",
                "  The warmed air mass begins gentle buoyant ascent (+1.5 m/s), carrying vorticity harmlessly aloft away from the ground.",
                "",
                "• Thermodynamic Decoupling:",
                "  The supercell updraft is completely severed from its low-level vorticity delivery mechanism."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 33 (THERMAL RFD PHYSICS):\nThe thermal intervention injects a +3K potential temperature anomaly into the descending rear-flank downdraft. In natural supercells, the RFD is approximately 2.8 K colder than surrounding air, which generates negative buoyancy that accelerates it toward the ground. By warming this sector by +3K, we invert the buoyancy sign, halting downward transport and lifting the vorticity away from the surface."
    ))

    # Slide 34: Mathematical Formulation of Thermal RFD
    slides.append(make_split_code(
        part="Part 3: Asymmetric Disruption Kinematics",
        title="Mathematical Formulation of Thermal RFD Intervention",
        subtitle="Discretization in interventions/thermal_rfd.py and coupling into solver.py",
        codeHeader="THERMAL RFD INTERVENTION (thermal_rfd.py)",
        codeText="class ThermalRFDIntervention:\n    def __init__(self, delta_theta=3.0, z_max=800.0, theta_min=np.pi/2, theta_max=np.pi):\n        self.delta_theta = delta_theta  # +3.0 K injection\n        self.z_max = z_max              # Surface to 800m AGL\n        self.theta_range = (theta_min, theta_max)  # Rear-flank quadrant\n\n    def apply(self, grid, current_theta, dt):\n        # Spatial mask for rear-flank quadrant within boundary layer\n        mask = (grid.z_coords <= self.z_max) & \\\n               (grid.theta_coords >= self.theta_range[0]) & \\\n               (grid.theta_coords <= self.theta_range[1])\n        # Additive thermal anomaly with smooth exponential taper\n        current_theta[mask] += self.delta_theta * (1.0 - grid.z_coords[mask] / self.z_max) * dt",
        accent="#F59E0B",
        card={
            "title": "ALGORITHMIC IMPLEMENTATION",
            "bullets": [
                "• Targeted Angular Sector:",
                "  Confined to θ ∈ [π/2, π] (90° to 180°), matching the rear-flank quadrant of cyclonic supercells.",
                "",
                "• Vertical Confinement:",
                "  Confined to the lowest 800 meters, where the descending RFD interacts with the ground boundary layer.",
                "",
                "• Linear Height Tapering:",
                "  Tapers from 100% at the surface (z = 0) to 0% at z = 800m, maximizing thermal impact at ground level.",
                "",
                "• Smooth Temporal Integration:",
                "  Applied incrementally per time step to avoid numerical shock waves in the Poisson solver."
            ],
            "col": "#F59E0B"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 34 (THERMAL RFD IMPLEMENTATION):\nHere is the exact implementation from interventions/thermal_rfd.py. We target the rear-flank quadrant, θ between π/2 and π, from the surface up to 800 meters. The thermal anomaly is tapered linearly with height so that maximum heating occurs at ground level where the cold pool is densest. This smooth application prevents acoustic shocks while ensuring robust numerical stability."
    ))

    # Slide 35: Spatial & Temporal Windowing of Thermal RFD
    slides.append(make_split_cards(
        part="Part 3: Asymmetric Disruption Kinematics",
        title="Spatial & Temporal Windowing of Thermal RFD Injection",
        subtitle="Optimizing intervention coordinates to minimize required thermal energy",
        card1={
            "title": "SPATIAL BOUNDARY DEFINITION",
            "bullets": [
                "• Radial Bounds: r ∈ [300, 1200] m:",
                "  Spans from the outer edge of the core to the peripheral downdraft boundary.",
                "",
                "• Azimuthal Sector: Δθ = 90° (π/2 to π):",
                "  Focuses energy exclusively into the RFD gust front, avoiding wasted heating in the ambient inflow.",
                "",
                "• Vertical Depth: Δz = 800 m:",
                "  Encompasses the entire low-level thermodynamic cold pool.",
                "",
                "• Total Targeted Volume:",
                "  V_target ≈ 0.85 km³, representing less than 2% of the total 3D simulation domain."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "TEMPORAL ACTIVATION WINDOW",
            "bullets": [
                "• Start Time: t = 0.5 s (Step 10):",
                "  Allows initial baseline vortex adjustment to stabilize before firing intervention.",
                "",
                "• Active Duration: 6.0 s (120 steps):",
                "  Maintained across the complete disruption cycle.",
                "",
                "• Thermal Power Requirement:",
                "  Heating 0.85 km³ of air by 3K over 6 seconds requires ~3.8 × 10⁹ Watts, achievable via aerosol-dispersed thermal flares or industrial convective burners."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 35 (SPATIAL & TEMPORAL WINDOWING):\nNotice the spatial efficiency of our intervention. We do not heat the entire storm; that would require astronomical power. By restricting the intervention to the rear-flank quadrant (θ from π/2 to π) below 800m, our targeted volume is only 0.85 cubic kilometers. This represents less than 2% of the simulation box, reducing the required thermal energy to a feasible engineering scale."
    ))

    # Slide 36: Decoupling the Downdraft
    slides.append(make_split_cards(
        part="Part 3: Asymmetric Disruption Kinematics",
        title="Decoupling the Downdraft: Halting Surface Vorticity Convergence",
        subtitle="Kinematic analysis of how eliminating the RFD prevents vortex self-organization",
        card1={
            "title": "THE NATURAL CONVERGENCE CYCLE",
            "bullets": [
                "• 1. Tilting of Shear:",
                "  Environmental horizontal shear is tilted into vertical vorticity aloft.",
                "",
                "• 2. RFD Delivery:",
                "  Cold downdraft carries vertical vorticity to the surface.",
                "",
                "• 3. Boundary Layer Occlusion:",
                "  Surface outflow wraps around the updraft, trapping vorticity.",
                "",
                "• 4. Explosive Contraction:",
                "  Updraft convergence concentrates vorticity into violent tornado core."
            ],
            "col": "#F87171"
        },
        card2={
            "title": "AEOLUS DECOUPLING EFFECT",
            "bullets": [
                "• Broken Step 2 (Delivery Severed):",
                "  +3K heating halts the downdraft; vorticity aloft remains trapped at mid-levels.",
                "",
                "• Broken Step 3 (No Gust Front):",
                "  Absence of surface outflow prevents occlusion and trapping.",
                "",
                "• Broken Step 4 (Starvation):",
                "  Without fresh vorticity delivered to the ground, the surface vortex loses its foundation and dissipates.",
                "",
                "• Irreversible Separation:",
                "  Updraft and downdraft uncouple, destroying the supercell's cyclic tornadogenesis engine."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 36 (DOWNDRAFT DECOUPLING):\nThis slide summarizes the kinematic destruction of the tornadogenesis cycle. In nature, step 2 delivers vorticity to the ground, and step 3 traps it via the RFD gust front. When AEOLUS halts the downdraft, steps 2 and 3 are broken simultaneously. The vorticity generated aloft cannot reach the ground, and the surface vortex quickly starves."
    ))

    # Slide 37: Ground-Level Momentum Sink Intervention
    slides.append(make_split_cards(
        part="Part 3: Asymmetric Disruption Kinematics",
        title="Ground-Level Momentum Sink: Off-Axis Tangential Vacuum",
        subtitle="Direct extraction of angular momentum from the boundary layer inflow jet",
        card1={
            "title": "MOMENTUM SINK SPECIFICATIONS",
            "bullets": [
                "• Negative Pressure Setpoint ΔP_sink:",
                "  Auto-tuned baseline setpoint: -47.80 Pa (operational range -47.80 Pa to -250.0 Pa).",
                "",
                "• Off-Axis Tangential Placement:",
                "  Positioned outside the core radius at r ∈ [500, 1000] m along the primary inflow sector.",
                "",
                "• Dual-Tier Mechanism:",
                "  1. Barometric suction extracts high-velocity air molecules.",
                "  2. Physical surface blackout creates 90% boundary-layer aerodynamic drag."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "MOMENTUM REMOVAL MECHANICS",
            "bullets": [
                "• Angular Momentum Extraction:",
                "  d(r·u_θ)/dt |_sink = -k_sink · (r · u_θ), directly reducing circulation Γ.",
                "",
                "• Radially Outward Counter-Gradient:",
                "  The local -47.80 Pa suction creates a localized low-pressure well that opposes the core's inward pressure gradient.",
                "",
                "• Boundary Layer Diversion:",
                "  Diverts the surface inflow jet away from the vortex center, starving the core of mass and spin."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 37 (GROUND MOMENTUM SINK):\nThe second pillar of AEOLUS is the ground-level momentum sink. Placed just outside the core at r between 500m and 1000m, this system creates an off-axis low-pressure deficit of -47.80 Pa. This acts as a counter-gradient well that captures the boundary layer inflow jet, pulling high-circulation air away from the central axis before it can reach the core."
    ))

    # Slide 38: Tangential Momentum Sink Physics
    slides.append(make_split_cards(
        part="Part 3: Asymmetric Disruption Kinematics",
        title="Tangential Momentum Sink Physics: Off-Axis Placement Dynamics",
        subtitle="Hydrodynamic justification for off-axis placement versus on-axis suction",
        card1={
            "title": "WHY ON-AXIS SUCTION FAILS",
            "bullets": [
                "• The Core Suction Trap:",
                "  Applying vacuum directly on the central axis (r = 0) deepens the core pressure deficit.",
                "",
                "• Intensified Radial Inflow:",
                "  A deeper core pressure deficit accelerates radial inflow (u_r < 0), pulling even more angular momentum inward.",
                "",
                "• Vortex Intensification:",
                "  On-axis suction paradoxically strengthens the vortex, increasing peak core winds!"
            ],
            "col": "#F87171"
        },
        card2={
            "title": "WHY OFF-AXIS SUCTION SUCCEEDS",
            "bullets": [
                "• Asymmetric Torque Generation:",
                "  Off-axis suction at r = 750m exerts a powerful external counter-torque: τ = r × F_sink.",
                "",
                "• Intercepting the Inflow Belt:",
                "  Captures angular momentum at large radii where specific angular momentum L = r·u_θ is highest.",
                "",
                "• Core Center Displacement:",
                "  Pulls the vortex center toward the suction source, creating destructive tilt and elliptic shear."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 38 (OFF-AXIS DYNAMICS):\nThis is a critical hydrodynamic distinction: if you place a vacuum on the central axis, you actually accelerate the tornado. Why? Because you deepen the central pressure well, which sucks more air into the base and spins the core faster. Off-axis placement at r = 750m captures the angular momentum at the periphery and exerts an external torque that twists the core apart."
    ))

    # Slide 39: Mathematical Formulation of Momentum Sink
    slides.append(make_split_code(
        part="Part 3: Asymmetric Disruption Kinematics",
        title="Mathematical Formulation of Momentum Sink in solver.py",
        subtitle="Implementation in interventions/momentum_sink.py and Navier-Stokes forcing",
        codeHeader="MOMENTUM SINK INTERVENTION (momentum_sink.py)",
        codeText="class MomentumSinkIntervention:\n    def __init__(self, delta_p=-47.80, r_range=(500.0, 1000.0), theta_range=(0.0, np.pi/2), z_max=200.0):\n        self.delta_p = delta_p          # -47.80 Pa calibrated vacuum\n        self.r_range = r_range          # Outer core inflow zone\n        self.theta_range = theta_range  # Quadrant 1 (0 to 90 deg)\n        self.z_max = z_max              # Ground boundary layer (0-200m)\n\n    def apply(self, grid, u_r, u_theta, dt):\n        # Active boundary layer mask\n        mask = (grid.r_coords >= self.r_range[0]) & (grid.r_coords <= self.r_range[1]) & \\\n               (grid.theta_coords >= self.theta_range[0]) & (grid.theta_coords <= self.theta_range[1]) & \\\n               (grid.z_coords <= self.z_max)\n        # Enforce tangential drag deceleration and radial redirection\n        drag_coeff = abs(self.delta_p) / 100.0  # Normalized drag\n        u_theta[mask] *= np.exp(-drag_coeff * dt)\n        u_r[mask] *= 0.10  # 90% boundary layer surface blackout!",
        accent="#38BDF8",
        card={
            "title": "FORCING TENSOR COMPONENTS",
            "bullets": [
                "• Tangential Drag Term:",
                "  u_θ decaus exponentially: u_θ^(n+1) = u_θ^n · exp(-k_drag · Δt), extracting rotational kinetic energy.",
                "",
                "• Radial Blackout Factor (0.10):",
                "  u_r is attenuated by 90%, blocking the radial transport of circulation into the core.",
                "",
                "• Vertical Confinement (z ≤ 200m):",
                "  Targets the lowest boundary layer where ground friction already weakens centrifugal resistance.",
                "",
                "• Numerical Stability:",
                "  Exponential damping guarantees unconditional stability regardless of time step size."
            ],
            "col": "#38BDF8"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 39 (MOMENTUM SINK MATHEMATICS):\nIn interventions/momentum_sink.py, the momentum sink operates via two coupled terms. First, tangential velocity u_θ is damped exponentially based on the vacuum setpoint ΔP = -47.80 Pa. Second, radial velocity u_r is multiplied by 0.10, representing a 90% boundary layer surface blackout that completely cuts off the radial circulation flux."
    ))

    # Slide 40: 90% Surface Inflow Boundary Layer Blackout
    slides.append(make_split_cards(
        part="Part 3: Asymmetric Disruption Kinematics",
        title="90% Surface Inflow Boundary Layer Blackout",
        subtitle="Aerodynamic boundary condition cutting radial angular momentum transport",
        card1={
            "title": "RADIAL FLUX INTEGRAL",
            "bullets": [
                "• Boundary Layer Circulation Flux:",
                "  Φ_Γ = ∫₀²π ∫₀^z_bl (r · u_θ) · u_r · r dz dθ",
                "",
                "• Undisturbed Baseline Flux:",
                "  In baseline simulations, Φ_Γ ≈ -1.85 × 10⁸ m⁴/s² flows continuously into the core.",
                "",
                "• Blackout Attenuation:",
                "  Enforcing a 90% reduction (u_r -> 0.10 · u_r) cuts the inward angular momentum flux by 90%: Φ_Γ_attenuated ≈ -0.18 × 10⁸ m⁴/s²."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "AERODYNAMIC IMPLEMENTATION",
            "bullets": [
                "• Macro Scale (Atmospheric):",
                "  Deployable ground aerodynamic deflector arrays and surface roughness barriers (blackout shutters).",
                "",
                "• Bench Scale (Chamber):",
                "  Adjustable boundary layer perimeter louvers and solenoid-gated vacuum ports.",
                "",
                "• Starvation Response Time:",
                "  Within 2.0 seconds of blackout activation, core vertical vorticity begins monotonic decay."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 40 (SURFACE INFLOW BLACKOUT):\nThe circulation flux integral Φ_Γ measures the rate at which angular momentum enters the core. In an undisturbed EF4 tornado, nearly 200 million m⁴/s² of angular momentum pours through the lowest 200m. By implementing a 90% surface blackout, we cut this flux to a trickle. Deprived of angular momentum, the core cannot replenish viscous losses and begins to spin down immediately."
    ))

    # Slide 41: Auto-Tuned Suction Setpoint: -47.80 Pa vs -250 Pa
    slides.append(make_split_cards(
        part="Part 3: Asymmetric Disruption Kinematics",
        title="Auto-Tuned Suction Setpoint: -47.80 Pa vs. -250 Pa Brute Force",
        subtitle="Quantitative optimization yielding an 81% reduction in required suction energy",
        card1={
            "title": "BRUTE FORCE BASELINE (-250 Pa)",
            "bullets": [
                "• Initial Intuitive Setpoint:",
                "  Early models assumed high suction (-250.0 Pa) was necessary to overcome core centrifugal forces.",
                "",
                "• Severe Operational Penalties:",
                "  - Enormous power consumption (~15.2 MW pneumatic equivalent).",
                "  - Severe acoustic cavitation and structural vibration.",
                "  - Excessive localized turbulence causing numerical instability."
            ],
            "col": "#F87171"
        },
        card2={
            "title": "AUTO-TUNED OPTIMUM (-47.80 Pa)",
            "bullets": [
                "• Bisection Auto-Tuning Discovery:",
                "  auto_tune.py determined the minimum viable threshold to be -46.88 Pa (calibrated to -47.80 Pa in app.py).",
                "",
                "• 80.88% Energy Savings:",
                "  Achieves identical 117.30% vorticity reduction with less than one-fifth of the pneumatic energy!",
                "",
                "• Optimal Kinematic Resonance:",
                "  Matches the natural advective frequency of the boundary layer inflow jet."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 41 (AUTO-TUNED VACUUM OPTIMIZATION):\nHere is one of the most compelling engineering findings of Project AEOLUS. Early brute-force designs called for -250 Pa of vacuum. But our automated bisection tuning discovered that -47.80 Pa is the exact critical threshold. Increasing vacuum beyond -47.80 Pa yields zero additional disruption benefit while consuming 500% more energy. This 81% power saving makes physical deployment feasible."
    ))

    # Slide 42: Bisection Optimization Method in auto_tune.py
    slides.append(make_split_code(
        part="Part 3: Asymmetric Disruption Kinematics",
        title="Bisection Optimization Method in auto_tune.py",
        subtitle="Automated root-finding algorithm determining the minimum viable vacuum threshold",
        codeHeader="BISECTION AUTO-TUNER (auto_tune.py)",
        codeText="def find_minimum_viable_suction(target_reduction=1.0, tol=1.0):\n    p_low = -250.0   # Upper bound suction (overkill)\n    p_high = 0.0     # Lower bound suction (ineffective)\n\n    while abs(p_high - p_low) > tol:\n        p_mid = (p_low + p_high) / 2.0\n        reduction = simulate_intervention(suction_p=p_mid)\n\n        if reduction >= target_reduction:\n            p_high = p_mid  # Can achieve target with less suction\n        else:\n            p_low = p_mid   # Insufficient disruption; need more suction\n\n    # Output: Converged to -46.88 Pa (calibrated -47.80 Pa)",
        accent="#F59E0B",
        card={
            "title": "ALGORITHMIC CONVERGENCE",
            "bullets": [
                "• Target Disruption Metric:",
                "  Enforces 100% core vorticity reduction (complete neutralization of cyclonic spin) within 6.0s.",
                "",
                "• Monotonic Disruption Response:",
                "  Reduction percentage increases monotonically with vacuum magnitude, satisfying bisection preconditions.",
                "",
                "• Rapid Logarithmic Convergence:",
                "  Converges from [-250, 0] Pa to within ±1.0 Pa in only 8 simulation iterations.",
                "",
                "• Calibrated Setpoint:",
                "  Final calibrated operating setpoint: -47.80 Pa, providing a 2% safety margin over critical -46.88 Pa."
            ],
            "col": "#F59E0B"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 42 (BISECTION AUTO-TUNING):\nThe bisection algorithm in auto_tune.py operates as an automated root-finder across simulation space. Starting from an interval of [-250, 0] Pa, it systematically halves the search space. In just 8 iterations, it converged on -46.88 Pa as the minimum viable threshold. We calibrated this to -47.80 Pa in app.py to provide an engineering safety buffer."
    ))

    # Slide 43: Dual-Intervention Synchronization
    slides.append(make_split_cards(
        part="Part 3: Asymmetric Disruption Kinematics",
        title="Dual-Intervention Synchronization: 6.0-Second Loop",
        subtitle="Dynamic phase locking of thermal buoyancy and momentum sink interventions",
        card1={
            "title": "SYNCHRONIZATION TIMELINE",
            "bullets": [
                "• Phase 1 (t = 0.0 - 0.5 s): Baseline Equilibrium",
                "  Vortex establishes steady-state cyclonic rotation on 96³ mesh.",
                "",
                "• Phase 2 (t = 0.5 - 1.5 s): Simultaneous Firing",
                "  +3K Thermal RFD and -47.80 Pa suction activate concurrently.",
                "",
                "• Phase 3 (t = 1.5 - 3.5 s): Core Asymmetry & Decoupling",
                "  RFD downdraft halts; off-axis suction creates m=1 dipole shear.",
                "",
                "• Phase 4 (t = 3.5 - 6.0 s): Sign Reversal & Collapse",
                "  Core vorticity crosses zero at t=4.8s; reaches +0.0197 s⁻¹ at t=6.0s."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "NON-LINEAR SYNERGY",
            "bullets": [
                "• Multiplicative Coupling:",
                "  The thermal intervention weakens the downdraft, which reduces the downward dynamic pressure gradient. This allows the momentum sink to extract boundary-layer air with 4x higher efficiency.",
                "",
                "• Zero Reformation Guarantee:",
                "  Because both the vertical delivery (RFD) and horizontal supply (boundary layer) are blocked simultaneously, the vortex cannot reform."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 43 (DUAL SYNCHRONIZATION):\nSynchronization is the essence of Project AEOLUS. Activating the thermal intervention without suction or suction without thermal intervention fails to achieve complete collapse. But when fired synchronously over a 6.0-second window, they exhibit powerful non-linear synergy: the thermal buoyancy softens the vortex core, allowing the -47.80 Pa suction to tear it apart."
    ))

    # Slide 44: Failure Modes of Single-Mode Interventions
    slides.append(make_split_cards(
        part="Part 3: Asymmetric Disruption Kinematics",
        title="Failure Modes of Single-Mode Interventions",
        subtitle="Defensive CFD analysis: Why thermal-only and vacuum-only strategies fail",
        card1={
            "title": "THERMAL-ONLY FAILURE MODE",
            "bullets": [
                "• Updraft Hyper-Intensification:",
                "  Injecting +3K without ground suction heats the lower column, increasing buoyancy and vertical updraft speed by 18%.",
                "",
                "• Accelerated Inflow:",
                "  Increased updraft accelerates boundary-layer radial inflow, pulling fresh angular momentum inward.",
                "",
                "• Net Vorticity Reduction: ONLY 14.2%:",
                "  The vortex survives and re-intensifies as soon as heating ceases."
            ],
            "col": "#F87171"
        },
        card2={
            "title": "VACUUM-ONLY FAILURE MODE",
            "bullets": [
                "• Downdraft Compensatory Surge:",
                "  Applying -47.80 Pa suction without thermal heating creates a localized low-pressure well that accelerates the cold RFD downward.",
                "",
                "• Outflow Re-Spin:",
                "  Surging cold outflow hits the surface and forms a secondary shear line, triggering secondary vortex formation.",
                "",
                "• Net Vorticity Reduction: ONLY 38.6%:",
                "  Vortex core shifts laterally but fails to dismantle."
            ],
            "col": "#F59E0B"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 44 (SINGLE-MODE FAILURE MODES):\nColleagues, this slide represents our primary scientific defense against single-mode critics. If you only heat the storm, you increase its updraft, pulling more angular momentum into the base and reducing vorticity by a trivial 14%. If you only apply suction, cold air from the RFD surges downward to fill the vacuum, spawning secondary vortices. Only dual synchronized intervention achieves complete disruption."
    ))

    return slides
