"""Part 1: Governing Fluid Equations & Cylindrical Coordinates (Slides 4 - 17)"""

from .slide_types import make_split_cards, make_split_code, make_three_cards

def get_part1_slides():
    slides = []

    # Slide 4: Classical Atmospheric Vortex Mechanics & Energetics
    slides.append(make_split_cards(
        part="Part 1: Governing Fluid Equations",
        title="Classical Atmospheric Vortex Mechanics & Energetics",
        subtitle="Kinematic hierarchy from dust devils to violent EF4/EF5 supercell tornadoes",
        card1={
            "title": "VORTEX SCALE CLASSIFICATION",
            "bullets": [
                "• Enhanced Fujita Scale Hierarchy:",
                "  - EF0/EF1: 29-49 m/s, localized boundary layer damage.",
                "  - EF2/EF3: 50-73 m/s, significant structural devastation.",
                "  - EF4/EF5: 74-135+ m/s, violent ground-scouring vortex cores.",
                "",
                "• Project AEOLUS EF4 Baseline Target:",
                "  - Core radius: r_core = 500 meters.",
                "  - Peak tangential velocity: V_max = 90.0 m/s (324 km/h).",
                "  - Central pressure drop: ΔP_core ≈ -99.2 hPa."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "ENERGY DISSIPATION CHALLENGE",
            "bullets": [
                "• Kinetic Energy Inventory:",
                "  An EF4 supercell column contains ~10¹² Joules of rotational kinetic energy.",
                "",
                "• Why Thermal Energy Injection Alone Fails:",
                "  Heating without kinematic starvation merely increases convective updraft, accelerating low-level radial inflow and intensifying spin.",
                "",
                "• The AEOLUS Solution:",
                "  Thermodynamic buoyancy injection must be paired with boundary-layer momentum extraction to induce destructive core asymmetry."
            ],
            "col": "#F59E0B"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 4 (ATMOSPHERIC ENERGETICS):\nTo contextualize the problem: an EF4 tornado possesses approximately one terajoule of organized kinetic energy. This immense rotational store is sustained by a continuous flux of angular momentum entering through the surface boundary layer. Any intervention that fails to cut off this ground flux will simply be consumed by the vortex engine."
    ))

    # Slide 5: Coordinate System Selection
    slides.append(make_split_cards(
        part="Part 1: Governing Fluid Equations",
        title="Coordinate Systems: Cartesian vs. Cylindrical Coordinates",
        subtitle="Mathematical justification for adopting a cylindrical (r, θ, z) reference frame",
        card1={
            "title": "CARTESIAN LIMITATIONS (x, y, z)",
            "bullets": [
                "• Geometric Misalignment:",
                "  Circular streamline curvature cannot align with orthogonal Cartesian grid faces, introducing severe numerical diffusion.",
                "",
                "• Spurious Vorticity Dissipation:",
                "  Standard Cartesian stencils numerically damp circular vortex cores within 20 to 30 time steps.",
                "",
                "• Inefficient Boundary Resolution:",
                "  Resolving a 500m core in a 4km square box requires millions of wasted cells in the quiescent far-field corners."
            ],
            "col": "#F87171"
        },
        card2={
            "title": "CYLINDRICAL ADVANTAGES (r, θ, z)",
            "bullets": [
                "• Exact Streamline Alignment:",
                "  Primary swirling velocity u_θ aligns directly with grid lines, virtually eliminating numerical cross-flow diffusion.",
                "",
                "• Natural Core Focusing:",
                "  Cell volumes naturally concentrate toward small radii (dV = r·dr·dθ·dz), providing adaptive spatial resolution at the vortex core.",
                "",
                "• Analytical Symmetry Representation:",
                "  Axisymmetric Rankine base states require zero azimuthal derivatives (∂/∂θ = 0), dramatically improving solver stability."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 5 (COORDINATE SYSTEM SELECTION):\nWhen solving rotating fluid problems, coordinate choice dictates numerical accuracy. In Cartesian grids, circular vortex lines cut diagonally across square cells, generating artificial numerical diffusion that rapidly dissolves the core. In cylindrical coordinates (r, θ, z), the primary azimuthal velocity u_θ is tangent to the grid lines, completely preserving angular momentum."
    ))

    # Slide 6: Radial Momentum Equation
    slides.append(make_split_code(
        part="Part 1: Governing Fluid Equations",
        title="3D Cylindrical Navier-Stokes: Radial Momentum Equation",
        subtitle="Balance of non-linear radial convection, centrifugal acceleration, and pressure gradient",
        codeHeader="RADIAL MOMENTUM FORMULATION (solver.py)",
        codeText="∂u_r/∂t + (u·∇)u_r - (u_θ)²/r = -1/ρ ∂p/∂r\n         + ν [ ∇²u_r - u_r/r² - 2/r² ∂u_θ/∂θ ]\n         + F_sink(r, θ, z)\n\n// METRIC SOURCE TERM: -(u_θ)² / r\n// Represents centrifugal acceleration directing fluid\n// outward in opposition to the inward pressure gradient.",
        accent="#38BDF8",
        card={
            "title": "RADIAL DYNAMICS & BALANCE",
            "bullets": [
                "• Cyclostrophic Equilibrium:",
                "  Under baseline conditions, the inward radial pressure gradient (-1/ρ ∂p/∂r) is precisely balanced by outward centrifugal acceleration (u_θ²/r).",
                "",
                "• F_sink Suction Forcing:",
                "  Our ground momentum sink introduces a negative radial force term F_sink, destabilizing cyclostrophic equilibrium.",
                "",
                "• Viscous Curvature Dissipation:",
                "  The term -ν·u_r/r² accounts for coordinate curvature drag near the inner boundary.",
                "",
                "• 2/r² ∂u_θ/∂θ Coupling:",
                "  Directly couples azimuthal velocity perturbations into radial acceleration during asymmetric disruption."
            ],
            "col": "#38BDF8"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 6 (RADIAL MOMENTUM):\nNotice the geometric source terms in the radial momentum equation. The term -(u_θ)²/r is the centrifugal acceleration. In an undisturbed tornado, this balances the inward radial pressure gradient in cyclostrophic balance: 1/ρ ∂p/∂r = u_θ²/r. When AEOLUS introduces asymmetric suction, this delicate balance collapses, triggering catastrophic radial flow restructuring."
    ))

    # Slide 7: Centrifugal Acceleration & Cyclostrophic Balance
    slides.append(make_split_cards(
        part="Part 1: Governing Fluid Equations",
        title="Centrifugal Acceleration & Cyclostrophic Balance",
        subtitle="Analysis of the radial force balance sustaining low-pressure tornadic cores",
        card1={
            "title": "CYCLOSTROPHIC BALANCE DYNAMICS",
            "bullets": [
                "• The Governing Force Balance:",
                "  (1/ρ) · (dp/dr) = (u_θ)² / r",
                "",
                "• High Swirl Ratio Regime:",
                "  Because tornadic winds exceed 80 m/s at small radii (r < 500m), centrifugal acceleration dwarfs Coriolis acceleration by three orders of magnitude (Rossby number Ro >> 100).",
                "",
                "• Inner Pressure Depression:",
                "  Integrating from ambient boundary r_max to core radius r_core yields the deep cyclostrophic pressure deficit ΔP ≈ -100 hPa."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "DESTABILIZATION BY ASYMMETRIC DRAG",
            "bullets": [
                "• Breaking Axisymmetry:",
                "  When off-axis suction extracts u_θ over an angular sector Δθ, the centrifugal term (u_θ)²/r drops precipitously in that sector.",
                "",
                "• Unbalanced Inward Pumping:",
                "  The ambient radial pressure gradient instantly overwhelms the reduced centrifugal force, driving an asymmetric radial jet directly through the core.",
                "",
                "• Core Cross-Shear Induction:",
                "  This induced jet creates violent cross-core shear, triggering rapid vortex breakdown."
            ],
            "col": "#F59E0B"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 7 (CYCLOSTROPHIC BALANCE):\nAt atmospheric vortex scales, the Rossby number is enormous (Ro >> 100), meaning the Earth's Coriolis acceleration is utterly negligible compared to the local centrifugal acceleration (u_θ²/r). The vortex survives only because centrifugal force prevents ambient high pressure from rushing into the core. If we locally deplete u_θ, ambient pressure surges inward and crushes the vortex column."
    ))

    # Slide 8: Azimuthal Momentum Equation
    slides.append(make_split_code(
        part="Part 1: Governing Fluid Equations",
        title="Azimuthal Momentum Equation & Angular Momentum",
        subtitle="Conservation of circulation and the metric Coriolis coupling term",
        codeHeader="AZIMUTHAL MOMENTUM EQUATION (solver.py)",
        codeText="∂u_θ/∂t + (u·∇)u_θ + (u_r u_θ)/r = -1/(ρ r) ∂p/∂θ\n         + ν [ ∇²u_θ - u_θ/r² + 2/r² ∂u_r/∂θ ]\n         + F_sink_theta\n\n// METRIC COUPLING TERM: +(u_r u_θ) / r\n// Represents angular momentum conservation during radial\n// contraction (r decreasing -> u_θ increasing).",
        accent="#34D399",
        card={
            "title": "ANGULAR MOMENTUM MECHANICS",
            "bullets": [
                "• Specific Angular Momentum L = r · u_θ:",
                "  In inviscid, axisymmetric flow, L is materially conserved along streamlines: D(r·u_θ)/Dt = 0.",
                "",
                "• The Spin-Up Mechanism:",
                "  As fluid converges radially inward (u_r < 0), the metric term +(u_r·u_θ)/r acts as a massive tangential acceleration source, spinning up the vortex core.",
                "",
                "• Curvature Damping Term:",
                "  -ν·u_θ/r² extracts angular momentum through fluid friction near the inner boundary.",
                "",
                "• Momentum Sink Targeting:",
                "  F_sink_theta directly removes angular momentum before it reaches the core radius."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 8 (AZIMUTHAL MOMENTUM):\nThe term +(u_r·u_θ)/r is the engine of tornadogenesis. When air converges radially inward (u_r < 0), conservation of angular momentum requires u_θ to accelerate inversely with radius. This is why boundary-layer radial inflow is so dangerous. By placing our momentum sink in the path of this inflow, we eliminate the angular momentum supply feeding the core."
    ))

    # Slide 9: Vertical Momentum Equation & Boussinesq Approximation
    slides.append(make_split_code(
        part="Part 1: Governing Fluid Equations",
        title="Vertical Momentum Equation & Boussinesq Buoyancy",
        subtitle="Thermal updraft acceleration, buoyancy forcing, and microphysics sink terms",
        codeHeader="VERTICAL MOMENTUM EQUATION (solver.py)",
        codeText="∂u_z/∂t + (u·∇)u_z = -1/ρ ∂p/∂z + ν ∇²u_z\n         + g · (θ' / θ_0) + F_LHR + F_drag\n\n// BOUSSINESQ BUOYANCY: g · (θ' / θ_0)\n// θ' = θ - θ_base(z): Potential temperature perturbation\n// θ_0 = 300 K: Reference environmental state\n// F_LHR = +0.8 m/s²: Latent heat release updraft\n// F_drag = -0.15 m/s²: Precipitation drag loading",
        accent="#F59E0B",
        card={
            "title": "THERMODYNAMIC ACCELERATION",
            "bullets": [
                "• Boussinesq Validity:",
                "  Density variations are neglected except in the gravity term, which is highly accurate for vertical domains under 3 km (Mach number Ma < 0.3).",
                "",
                "• Buoyancy Coupling:",
                "  A warm perturbation (θ' > 0) accelerates upward; a cold pool (θ' < 0) drives sinking downdrafts.",
                "",
                "• The Rear-Flank Downdraft (RFD):",
                "  Evaporative cooling creates a negative θ' anomaly, generating a dense downdraft that wraps around the core.",
                "",
                "• AEOLUS Thermal Intervention:",
                "  Injects +3K directly into the RFD, turning negative buoyancy positive and halting downdraft convergence."
            ],
            "col": "#F59E0B"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 9 (VERTICAL MOMENTUM & BOUSSINESQ):\nThe Boussinesq approximation couples thermodynamics to kinematics through the buoyancy acceleration term g·(θ'/θ_0). For a 300K reference state, each 1 Kelvin temperature perturbation produces approximately 0.0327 m/s² of vertical acceleration. Our +3K intervention provides an upward acceleration of nearly 0.1 m/s², completely canceling the precipitation drag of -0.15 m/s²."
    ))

    # Slide 10: Incompressible Mass Continuity Constraint
    slides.append(make_split_code(
        part="Part 1: Governing Fluid Equations",
        title="Incompressible Mass Continuity in Cylindrical Coordinates",
        subtitle="Conservation of mass enforcing divergence-free velocity fields",
        codeHeader="CYLINDRICAL CONTINUITY CONSTRAINT",
        codeText="∇·u = 1/r · ∂(r · u_r)/∂r + 1/r · ∂u_θ/∂θ + ∂u_z/∂z = 0\n\n// EXPANDED METRIC FORM:\n∂u_r/∂r + u_r / r + 1/r · ∂u_θ/∂θ + ∂u_z/∂z = 0\n\n// INCOMPRESSIBILITY RMS METRIC (diagnostics.py):\nRMS_div = sqrt( 1/N · Σ |∇·u|² )  < 1.00 tolerance",
        accent="#38BDF8",
        card={
            "title": "MASS CONSERVATION PRINCIPLES",
            "bullets": [
                "• Geometric Flux Divergence:",
                "  The metric factor (1/r)·∂(r·u_r)/∂r accounts for shrinking annular cell areas as fluid approaches the central axis.",
                "",
                "• Acoustic Wave Elimination:",
                "  Enforcing ∇·u = 0 filters out high-frequency acoustic waves, allowing a computational time step Δt = 0.05s dictated solely by convective CFL limits.",
                "",
                "• Divergence Bounding Target:",
                "  Project AEOLUS enforces a strict production acceptance limit of divergence RMS < 1.00 s⁻¹ across all 120 time steps.",
                "",
                "• Verification Result:",
                "  Our 96³ dual-intervention run achieved a peak divergence RMS of only 0.7353."
            ],
            "col": "#38BDF8"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 10 (CONTINUITY CONSTRAINT):\nMass continuity in cylindrical coordinates requires careful accounting of the metric radius r. The term (1/r)·∂(r·u_r)/∂r ensures that as radial inflow penetrates deeper into smaller radii, it must either accelerate or divert into the vertical updraft ∂u_z/∂z. By enforcing ∇·u = 0 via elliptic projection, we eliminate numerical mass accumulation."
    ))

    # Slide 11: Cylindrical Laplacian & Metric Viscous Diffusion
    slides.append(make_split_cards(
        part="Part 1: Governing Fluid Equations",
        title="Cylindrical Laplacian & Metric Viscous Diffusion",
        subtitle="Viscous dissipation operator accounting for curvilinear coordinate stresses",
        card1={
            "title": "CYLINDRICAL SCALAR LAPLACIAN",
            "bullets": [
                "• General Scalar Formula:",
                "  ∇²φ = (1/r) · ∂/∂r [ r · ∂φ/∂r ] + (1/r²) · ∂²φ/∂θ² + ∂²φ/∂z²",
                "",
                "• Radial Curvature Expansion:",
                "  ∇²φ = ∂²φ/∂r² + (1/r) · ∂φ/∂r + (1/r²) · ∂²φ/∂θ² + ∂²φ/∂z²",
                "",
                "• Physical Role:",
                "  Governs viscous diffusion of temperature θ and momentum components across shear layers."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "VECTOR VELOCITY METRIC CORRECTIONS",
            "bullets": [
                "• Radial Diffusion Metric Corrections:",
                "  Diff_r = ν [ ∇²u_r - u_r/r² - (2/r²) · ∂u_θ/∂θ ]",
                "",
                "• Azimuthal Diffusion Metric Corrections:",
                "  Diff_θ = ν [ ∇²u_θ - u_θ/r² + (2/r²) · ∂u_r/∂θ ]",
                "",
                "• Physical Meaning:",
                "  The terms -u/r² and ±(2/r²)·∂u/∂θ arise because unit vectors e_r and e_θ rotate with azimuth θ, coupling radial and tangential stresses."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 11 (METRIC VISCOUS DIFFUSION):\nIn cylindrical coordinates, vector diffusion is not simply the scalar Laplacian applied to each velocity component. Because the unit vectors e_r and e_θ rotate with angle θ, differentiating vector components introduces metric correction terms: -u_r/r² - (2/r²)·∂u_θ/∂θ for radial velocity, and -u_θ/r² + (2/r²)·∂u_r/∂θ for azimuthal velocity. Omitting these terms violates momentum conservation."
    ))

    # Slide 12: Elliptic Pressure Poisson Equation Derivation
    slides.append(make_split_code(
        part="Part 1: Governing Fluid Equations",
        title="Elliptic Pressure Poisson Equation Derivation",
        subtitle="Enforcing incompressibility via projection of intermediate velocity field u*",
        codeHeader="PRESSURE POISSON EQUATION (solver.py)",
        codeText="// 1. PREDICTOR STEP (Advection + Diffusion):\nu* = u^n + Δt · [ -(u^n·∇)u^n + ν ∇²u^n + F_ext ]\n\n// 2. PRESSURE POISSON EQUATION:\n∇²p^(n+1) = (ρ / Δt) · ∇·u*\n\n// 3. CORRECTOR STEP (Velocity Projection):\nu^(n+1) = u* - (Δt / ρ) · ∇p^(n+1)\n\n// GUARANTEE: ∇·u^(n+1) = ∇·u* - (Δt/ρ) ∇²p = 0",
        accent="#F59E0B",
        card={
            "title": "CHORIN FRACTIONAL-STEP PROJECTION",
            "bullets": [
                "• Fractional Step Scheme:",
                "  Decouples velocity advection-diffusion from the elliptic pressure solver, reducing computational complexity.",
                "",
                "• Elliptic Nature:",
                "  Pressure acts as an instantaneous Lagrange multiplier enforcing mass conservation ∇·u = 0 everywhere simultaneously.",
                "",
                "• Iterative Relaxation:",
                "  Solved via damped Jacobi or Successive Over-Relaxation (SOR) with spectral radius control.",
                "",
                "• Numerical Stability:",
                "  Damped Jacobi iterations guarantee monotonic convergence without high-frequency grid decoupling."
            ],
            "col": "#F59E0B"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 12 (PRESSURE POISSON PROJECTION):\nThe Chorin projection method is the cornerstone of incompressible CFD. In the predictor step, we compute an intermediate velocity u* considering advection, diffusion, and body forces. Because u* is not divergence-free, we solve the elliptic Poisson equation ∇²p = (ρ/Δt)·∇·u* for the pressure field p. Subtracting ∇p in the corrector step projects u* onto the space of divergence-free vector fields."
    ))

    # Slide 13: Staggered Arakawa-C Grid Discretization
    slides.append(make_split_cards(
        part="Part 1: Governing Fluid Equations",
        title="Staggered Arakawa-C Grid Spatial Discretization",
        subtitle="Preventing checkerboard pressure oscillations via face-centered velocity fluxes",
        card1={
            "title": "VARIABLE TOPOLOGY & PLACEMENT",
            "bullets": [
                "• Cell Center (i, j, k):",
                "  Pressure p, Potential Temperature θ, Dynamic Viscosity ν, Density ρ.",
                "",
                "• Radial Face (i+1/2, j, k):",
                "  Radial velocity component u_r.",
                "",
                "• Azimuthal Face (i, j+1/2, k):",
                "  Azimuthal velocity component u_θ.",
                "",
                "• Vertical Face (i, j, k+1/2):",
                "  Vertical velocity component u_z."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "NUMERICAL BENEFITS OVER COLLOCATED",
            "bullets": [
                "• Checkerboard Suppression:",
                "  Collocated grids allow non-physical high-frequency 2Δx pressure oscillations. The Arakawa-C grid tightly couples pressure to adjacent velocity differences, eliminating spurious modes.",
                "",
                "• Exact Discrete Conservation:",
                "  Mass and kinetic energy fluxes are conserved exactly to machine precision on the discrete mesh.",
                "",
                "• Compact Differencing:",
                "  Central differences across cell faces achieve 2nd-order accuracy using a compact 2-point stencil."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 13 (ARAKAWA-C STAGGERED TOPOLOGY):\nThe choice of grid topology is vital. In collocated grids, where velocities and pressure share the same grid points, central differences evaluate pressure gradients across 2Δx, completely decoupling odd and even points and spawning checkerboard oscillations. The Arakawa-C grid places normal velocities directly on cell faces, ensuring that the pressure gradient ∂p/∂x is computed across 1Δx."
    ))

    # Slide 14: Coordinate Metric Singularity & Regularization
    slides.append(make_split_cards(
        part="Part 1: Governing Fluid Equations",
        title="Cylindrical Coordinate Metric Singularity & Regularization",
        subtitle="Rigorous treatment of the 1/r pole singularity at the inner computational radius",
        card1={
            "title": "THE 1/r POLE SINGULARITY PROBLEM",
            "bullets": [
                "• Metric Division by Zero:",
                "  Terms like (u_θ)²/r, (u_r·u_θ)/r, and (1/r)·∂p/∂θ diverge to infinity as r -> 0.",
                "",
                "• Severe CFL Restriction:",
                "  Azimuthal cell width Δs = r·Δθ shrinks toward zero, driving the Courant time step limit Δt < r·Δθ / |u_θ| to zero.",
                "",
                "• Spurious Pole Waves:",
                "  Unresolved azimuthal modes reflect off r=0, destabilizing the entire numerical domain."
            ],
            "col": "#F87171"
        },
        card2={
            "title": "AEOLUS INNER CORE REGULARIZATION",
            "bullets": [
                "• Non-Zero Inner Radius r_min = 100 m:",
                "  Our 96³ mesh sets r ∈ [100.0, 2000.0] meters, placing the inner boundary well inside the 500m core while avoiding r = 0.",
                "",
                "• Free-Slip Inner Boundary Conditions:",
                "  ∂u_θ/∂r = 0, u_r = 0 at r = r_min, perfectly mimicking solid-body core behavior.",
                "",
                "• Stable Time Stepping:",
                "  Preserves a robust operational CFL time step of Δt = 0.05s across all 120 production steps."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 14 (METRIC SINGULARITY & REGULARIZATION):\nThe 1/r coordinate singularity is a notorious obstacle in cylindrical CFD. If the domain extends to r = 0, azimuthal cell width Δs = r·Δθ vanishes, forcing Δt to zero under CFL stability. Project AEOLUS regularizes this by setting an inner computational boundary at r_min = 100m. Since our vortex core radius is 500m, this inner cutoff lies well within the laminar solid-body zone."
    ))

    # Slide 15: Baseline EF4 Vortex Formulation: Modified Rankine
    slides.append(make_split_code(
        part="Part 1: Governing Fluid Equations",
        title="Baseline EF4 Vortex: Modified Rankine Vortex Formulation",
        subtitle="Mathematical synthesis of solid-body rotation core and external potential vortex",
        codeHeader="RANKINE VORTEX FORMULATION (baseline.py)",
        codeText="def rankine_vortex(r, r_core=500.0, V_max=90.0):\n    u_theta = np.zeros_like(r)\n    # Region 1: Solid-body core (r <= r_core)\n    mask_inner = r <= r_core\n    u_theta[mask_inner] = V_max * (r[mask_inner] / r_core)\n    # Region 2: Free potential vortex (r > r_core)\n    mask_outer = r > r_core\n    u_theta[mask_outer] = V_max * (r_core / r[mask_outer])\n    return u_theta",
        accent="#38BDF8",
        card={
            "title": "VORTICITY & CIRCULATION PROFILE",
            "bullets": [
                "• Analytical Vertical Vorticity ω_z:",
                "  ω_z(r) = (1/r) · ∂(r · u_θ)/∂r",
                "",
                "• Inside Core (r ≤ r_core):",
                "  ω_z = (1/r) · ∂/∂r [ r · V_max(r/r_core) ] = 2 · (V_max / r_core) = +0.360 s⁻¹.",
                "",
                "• Outside Core (r > r_core):",
                "  ω_z = (1/r) · ∂/∂r [ r · V_max(r_core/r) ] = 0.0 s⁻¹ (Irrotational).",
                "",
                "• Mathematical Singularity at r_core:",
                "  A step discontinuity exists at r = r_core; in our 96³ mesh, this is smoothly resolved across 3 grid cells via viscous diffusion."
            ],
            "col": "#38BDF8"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 15 (RANKINE MODEL FORMULATION):\nThe Rankine vortex is the classical foundational model of tornadic winds. Within r ≤ r_core, circulation increases quadratically with radius, yielding constant vertical vorticity: ω_z = 2·V_max/r_core. Outside r_core, circulation is invariant (Γ = const), so vorticity is identically zero. This gives an idealized profile against which disruption metrics can be evaluated."
    ))

    # Slide 16: EF4 Scale Parameters: Core Radius & Peak Velocity
    slides.append(make_split_cards(
        part="Part 1: Governing Fluid Equations",
        title="EF4 Scale Parameters: Core Radius & Peak Velocity",
        subtitle="Justification of physical parameters chosen for high-fidelity disruption benchmarking",
        card1={
            "title": "EF4 PARAMETER SPECIFICATIONS",
            "bullets": [
                "• Core Radius r_core = 500 meters:",
                "  Corresponds to a 1.0 km damage swath diameter, typical of violent EF4 tornadoes observed in the American Great Plains.",
                "",
                "• Peak Tangential Velocity V_max = 90.0 m/s:",
                "  Equivalent to 201 mph (324 km/h), placing the vortex firmly within the violent EF4 category (166-200 mph).",
                "",
                "• Ambient Pressure P_amb = 900 hPa:",
                "  Representative of high-elevation supercell tornadogenesis environments."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "CYCLOSTROPHIC PRESSURE GRADIENT",
            "bullets": [
                "• Analytical Pressure Deficit:",
                "  dp/dr = ρ · u_θ² / r",
                "",
                "• Integration Yields:",
                "  ΔP_total = -ρ · V_max² = -(1.225 kg/m³) · (90 m/s)² ≈ -9,922.5 Pa (-99.2 hPa).",
                "",
                "• Ground Suction Comparison:",
                "  AEOLUS's auto-tuned suction of -47.80 Pa represents less than 0.5% of the total core pressure deficit, proving starvation is kinematic rather than barometric."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 16 (EF4 SCALE PARAMETERS):\nNotice the extraordinary disparity: an EF4 tornado creates a central barometric depression of nearly -100 hPa (-10,000 Pa). Yet Project AEOLUS achieves disruption with an auto-tuned suction deficit of only -47.80 Pa. This proves conclusively that our mechanism does not attempt to counteract the tornado's pressure field by brute suction; it starves the kinetic angular momentum flux."
    ))

    # Slide 17: Logarithmic Boundary Layer Wind Shear Profile
    slides.append(make_split_code(
        part="Part 1: Governing Fluid Equations",
        title="Logarithmic Boundary Layer Wind Shear Profile",
        subtitle="Modeling ground friction and environmental wind shear in baseline vortex initialization",
        codeHeader="WIND SHEAR MODEL (baseline.py)",
        codeText="def apply_wind_shear(u_theta, z_coords, z_0=0.1, z_ref=500.0):\n    # Logarithmic planetary boundary layer profile\n    shear_factor = np.log(z_coords / z_0 + 1.0) / np.log(z_ref / z_0)\n    # Bound factor between 0.0 and 1.5 aloft\n    shear_factor = np.clip(shear_factor, 0.0, 1.5)\n    return u_theta * shear_factor[:, np.newaxis, :]",
        accent="#F59E0B",
        card={
            "title": "BOUNDARY LAYER AERODYNAMICS",
            "bullets": [
                "• Surface Roughness Length z_0 = 0.1 m:",
                "  Represents realistic open terrain with scattered trees and low structures.",
                "",
                "• Ground Deceleration (z -> 0):",
                "  Frictional drag forces u_θ to zero at the surface, breaking cyclostrophic equilibrium.",
                "",
                "• Radial Inflow Induction:",
                "  Because centrifugal force u_θ²/r drops faster near the ground than the radial pressure gradient, an intense radial inflow jet (u_r < 0) develops within the lowest 200m.",
                "",
                "• The Vulnerability Zone:",
                "  This near-surface inflow layer is precisely where AEOLUS deploys its 90% surface blackout shutters."
            ],
            "col": "#F59E0B"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 17 (BOUNDARY LAYER WIND SHEAR):\nThe logarithmic wind shear profile in baseline.py models the turbulent boundary layer. Friction retards the tangential velocity at low levels, causing cyclostrophic balance to fail. The inward radial pressure gradient then drives strong radial inflow at the surface. This inflow carries high angular momentum inward to spin up the core, identifying the exact boundary layer vulnerability targeted by AEOLUS."
    ))

    return slides
