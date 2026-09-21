"""Part 2: Micro-Physics Realism & Non-Hydrostatic Thermodynamics (Slides 18 - 30)"""

from .slide_types import make_split_cards, make_split_code, make_three_cards

def get_part2_slides():
    slides = []

    # Slide 18: Thermodynamic Budget & Supercell Convection Dynamics
    slides.append(make_split_cards(
        part="Part 2: Micro-Physics Realism",
        title="Thermodynamic Energy Budget of Supercell Convection",
        subtitle="Convective Available Potential Energy (CAPE) and thermal updraft generation",
        card1={
            "title": "SUPERCELL THERMODYNAMICS",
            "bullets": [
                "• High CAPE Regimes (2000 - 4000 J/kg):",
                "  Represents extreme convective instability where warm, moist surface air is capped by dry, cool air aloft.",
                "",
                "• Updraft Velocity Potential:",
                "  Theoretical maximum updraft speed: W_max = sqrt(2 · CAPE) ≈ 60 to 90 m/s.",
                "",
                "• Vortex Stretching Mechanism:",
                "  Intense vertical updraft acceleration (∂u_z/∂z > 0) stretches ambient vertical vortex tubes: dω_z/dt = ω_z · (∂u_z/∂z)."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "CONVECTIVE ADIABATS & PHASE CHANGE",
            "bullets": [
                "• Dry Adiabatic Lapse Rate (Γ_d = 9.8 K/km):",
                "  Governs unsaturated parcel ascent prior to lifting condensation level (LCL).",
                "",
                "• Moist Adiabatic Lapse Rate (Γ_m ≈ 6.0 K/km):",
                "  Latent heat of condensation offsets expansion cooling, maintaining positive buoyancy.",
                "",
                "• Non-Hydrostatic Updraft Core:",
                "  Drives localized pressure drops aloft, inducing low-level mass convergence."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 18 (THERMODYNAMIC BUDGET):\nTornadogenesis cannot occur in a purely kinematic environment; it is fundamentally driven by thermodynamics. In high-CAPE environments, parcel ascent releases massive latent heat as water vapor condenses. This buoyant acceleration creates intense vertical stretching, ∂u_z/∂z. By conservation of angular momentum, stretching a vortex column vertically forces its radius to contract and its spin rate to increase exponentially."
    ))

    # Slide 19: Latent Heat Release Parameterization
    slides.append(make_split_code(
        part="Part 2: Micro-Physics Realism",
        title="Latent Heat Release (LHR) Parameterization (0.8 m/s²)",
        subtitle="Vertical updraft acceleration driven by water vapor condensation aloft",
        codeHeader="LHR ACCELERATION COUPLING (solver.py)",
        codeText="// LATENT HEAT ACCELERATION FORCING:\nF_LHR = +0.8  // m/s² upward convective forcing\n\n// SPATIAL WINDOWING (z >= 500m, r <= 1.2 * r_core):\nif (z >= 500.0 && r <= 1.2 * r_core) {\n    u_z_accel += F_LHR * np.exp(-((r / r_core)**2));\n}\n\n// EFFECTIVE BUOYANCY EQUIVALENT:\n// Δθ_equiv = (F_LHR / g) · θ_0 = (0.8 / 9.81) · 300 K ≈ +24.46 K equivalent!",
        accent="#38BDF8",
        card={
            "title": "PHYSICAL PARAMETERIZATION ROLE",
            "bullets": [
                "• 0.8 m/s² Empirical Calibration:",
                "  Derived from mesoscale Doppler radar retrievals of violent supercell updraft cores (Klemp & Wilhelmson 1978).",
                "",
                "• Core Localized Forcing:",
                "  Gaussian spatial tapering confines LHR to the central updraft plume (r ≤ 1.2 · r_core, z ≥ 500m).",
                "",
                "• Sustaining Updraft Continuity:",
                "  Counteracts viscous decay and upward divergence, sustaining 30-50 m/s vertical velocities in baseline simulations.",
                "",
                "• Coupled Kinematic Impact:",
                "  Continuously pulls angular momentum upward from the surface boundary layer."
            ],
            "col": "#38BDF8"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 19 (LATENT HEAT RELEASE):\nIn solver.py, we parameterize Latent Heat Release as a direct vertical acceleration F_LHR = +0.8 m/s². Notice that in terms of Boussinesq buoyancy, an acceleration of 0.8 m/s² corresponds to an equivalent temperature perturbation of over +24 K! This massive upward push represents the latent heat liberated during rapid condensation in the supercell core updraft."
    ))

    # Slide 20: Mathematical Formulation of LHR Vertical Acceleration
    slides.append(make_split_cards(
        part="Part 2: Micro-Physics Realism",
        title="Mathematical Formulation of LHR in Energy Balance",
        subtitle="First law of thermodynamics coupling sensible heat flux to condensation rate",
        card1={
            "title": "THERMODYNAMIC ENERGY EQUATION",
            "bullets": [
                "• General Potential Temperature Equation:",
                "  ∂θ/∂t + (u·∇)θ = κ ∇²θ + (θ / T) · (L_v / c_p) · C_cond",
                "",
                "• Variable Definitions:",
                "  - L_v = 2.501 × 10⁶ J/kg (Latent heat of vaporization)",
                "  - c_p = 1005 J/(kg·K) (Specific heat of dry air)",
                "  - C_cond: Condensation rate of water vapor (kg/(kg·s))",
                "",
                "• Heating Rate Conversion:",
                "  A condensation rate of 1 g/kg per minute generates a heating rate of ~2.5 K/min."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "COUPLING TO BOUSSINESQ MOMENTUM",
            "bullets": [
                "• Vertical Buoyancy Conversion:",
                "  g · (θ' / θ_0) = g · [ θ(r,θ,z,t) - θ_ambient(z) ] / θ_0",
                "",
                "• Effective Updraft Forcing:",
                "  du_z/dt |_microphysics = g · (θ'/θ_0) + F_LHR",
                "",
                "• Stability Criterion:",
                "  Positive feedback loop: Updraft -> Condensation -> Latent Heat -> Increased Updraft."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 20 (LHR MATHEMATICAL FORMULATION):\nThe coupling between thermodynamics and kinematics is governed by the energy equation. As warm, moist air ascends, expansion cools it to saturation. Beyond the LCL, water vapor condenses, releasing L_v = 2.5 million Joules per kilogram. This latent heat heats the air, generating positive potential temperature anomalies θ' that accelerate the updraft via Boussinesq buoyancy."
    ))

    # Slide 21: Water Vapor Phase Change & Condensation Energy
    slides.append(make_split_cards(
        part="Part 2: Micro-Physics Realism",
        title="Water Vapor Phase Change & Condensation Dynamics",
        subtitle="Saturation vapor pressure, Clausius-Clapeyron relation, and liquid water path",
        card1={
            "title": "CLAUSIUS-CLAPEYRON THERMODYNAMICS",
            "bullets": [
                "• Saturation Vapor Pressure e_s(T):",
                "  e_s(T) = e_s0 · exp[ (L_v / R_v) · (1/T_0 - 1/T) ]",
                "",
                "• Exponential Temperature Sensitivity:",
                "  e_s increases ~7% per degree Kelvin of warming, creating a non-linear moisture reservoir in warm inflow air.",
                "",
                "• Saturation Mixing Ratio q_s:",
                "  q_s ≈ ε · e_s(T) / p, where ε = 0.622."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "CONDENSATION LATENT HEAT RELEASE",
            "bullets": [
                "• Condensation Rate Formulation:",
                "  C_cond = max(0, -dq_s/dt) = -u_z · (dq_s/dz)",
                "",
                "• Rapid Updraft Condensation:",
                "  In an updraft of u_z = 40 m/s, moisture condenses at rates exceeding 0.05 g/(kg·s).",
                "",
                "• Cloud Droplet Growth:",
                "  Droplets coalesce into raindrops, transitioning from buoyant cloud air into hydrometeor drag."
            ],
            "col": "#F59E0B"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 21 (WATER VAPOR CONDENSATION):\nThe Clausius-Clapeyron relation dictates that warm air holds exponentially more moisture. In a tornadic supercell, surface air often has dew points of 22-25°C. As this air is forced upward at 40 to 60 m/s, catastrophic condensation occurs, converting vast quantities of latent enthalpy into sensible kinetic updraft energy within minutes."
    ))

    # Slide 22: Precipitation Drag & Hydrometeor Loading
    slides.append(make_split_code(
        part="Part 2: Micro-Physics Realism",
        title="Precipitation Drag Parameterization (F_drag = -0.15 m/s²)",
        subtitle="Downward mechanical momentum loading from raindrop and hail mass",
        codeHeader="PRECIPITATION DRAG COUPLING (solver.py)",
        codeText="// PRECIPITATION DRAG ACCELERATION:\nF_drag = -0.15  // m/s² downward hydrometeor loading\n\n// SPATIAL DISTRIBUTION (Rain curtain / Forward Flank):\n// Concentrated in the hydrometeor core and downdraft flank\nif (r >= 0.8 * r_core && z <= 1500.0) {\n    u_z_accel += F_drag * hydrometeor_density_factor;\n}\n\n// NET VERTICAL FORCING IN RAIN REGION:\n// u_z_forcing = g · (θ'/θ_0) + F_drag < 0 -> DOWNDRAFT INITIATION",
        accent="#F87171",
        card={
            "title": "HYDROMETEOR LOADING DYNAMICS",
            "bullets": [
                "• Mechanical Mass Loading:",
                "  Raindrops falling through the air exert a downward frictional force equal to the gravitational weight of the liquid water: -g · q_l.",
                "",
                "• 0.15 m/s² Empirical Setting:",
                "  Corresponds to a liquid water content (LWC) of q_l ≈ 1.5 g/m³, typical of heavy supercell downpours.",
                "",
                "• Downdraft Triggering:",
                "  Precipitation drag initiates downward vertical velocity (u_z < 0), even before evaporative cooling establishes a cold pool.",
                "",
                "• Rear-Flank Coupling:",
                "  Acts as the mechanical driver creating the Rear-Flank Downdraft (RFD)."
            ],
            "col": "#F87171"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 22 (PRECIPITATION DRAG):\nPrecipitation drag is parameterized in solver.py as F_drag = -0.15 m/s². While latent heat pushes upward, precipitation loading drags the air downward. A cubic meter of air weighs about 1.2 kg. If it holds 1.5 grams of liquid water falling at terminal velocity, the drag force decelerates the air at approximately 0.15 m/s², initiating the rear-flank downdraft."
    ))

    # Slide 23: Hydrometeor Terminal Velocity & Negative Buoyancy
    slides.append(make_split_cards(
        part="Part 2: Micro-Physics Realism",
        title="Hydrometeor Terminal Velocity & Negative Buoyancy Coupling",
        subtitle="Balance of aerodynamic drag, gravitational acceleration, and evaporative cooling",
        card1={
            "title": "TERMINAL VELOCITY DYNAMICS",
            "bullets": [
                "• Aerodynamic Balance:",
                "  (1/2) · C_d · ρ · A · V_t² = m_drop · g",
                "",
                "• Raindrop Terminal Velocity:",
                "  V_t(D) ≈ 9.58 · [ 1 - exp(-(D / 1.77)¹.¹⁴⁷) ] m/s, reaching 9 m/s for 3-5mm drops.",
                "",
                "• Momentum Transfer:",
                "  Hydrometeors falling at terminal velocity transfer 100% of their drag force into the surrounding air mass."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "EVAPORATIVE COOLING FEEDBACK",
            "bullets": [
                "• Sub-Cloud Evaporation:",
                "  As rain falls into unsaturated sub-cloud air, rapid evaporation absorbs sensible heat at 2.5 × 10⁶ J/kg.",
                "",
                "• Cold Pool Densification:",
                "  Temperature drops by 3 to 8 K, producing a dense, negatively buoyant air mass (θ' < 0).",
                "",
                "• Combined Downward Force:",
                "  F_net = g · (θ'/θ_0) + F_drag ≈ -0.10 - 0.15 = -0.25 m/s² downward acceleration."
            ],
            "col": "#F59E0B"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 23 (TERMINAL VELOCITY & NEGATIVE BUOYANCY):\nAs raindrops fall, aerodynamic drag transfers momentum from the falling drops directly into the air column. Simultaneously, sub-cloud evaporation cools the air, producing a strong negative buoyancy perturbation θ' < 0. Together, drag and evaporative cooling drive downdrafts reaching speeds of 10 to 20 m/s as they strike the ground."
    ))

    # Slide 24: Non-Hydrostatic Pressure Perturbations
    slides.append(make_split_cards(
        part="Part 2: Micro-Physics Realism",
        title="Non-Hydrostatic Pressure Perturbations & Dynamic Pumping",
        subtitle="Diagnostic pressure decomposition into buoyant, linear shear, and non-linear spin terms",
        card1={
            "title": "PRESSURE DECOMPOSITION",
            "bullets": [
                "• Total Pressure Perturbation:",
                "  p' = p'_buoyancy + p'_dynamic",
                "",
                "• Dynamic Pressure Equation:",
                "  -∇²p'_dynamic = ρ · [ (∂u_i/∂x_j) · (∂u_j/∂x_i) ]",
                "",
                "• Decomposition into Shear & Spin:",
                "  ∇²p'_dynamic = (1/2) · ρ · |ω|² - ρ · |S|², where ω is vorticity and S is deformation rate."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "DYNAMIC UPDRAFT PUMPING",
            "bullets": [
                "• Low Pressure at Vorticity Maxima:",
                "  Because ∇²p'_dynamic > 0 where vorticity |ω| is high, dynamic pressure p' is strongly negative inside the spinning core.",
                "",
                "• Vertical Pressure Gradient Force:",
                "  The core pressure deficit is deepest near the ground, creating a powerful vertical dynamic suction force: -∂p'/∂z > 0.",
                "",
                "• Feedback Acceleration:",
                "  This dynamic suction pulls boundary-layer air vertically upward, independent of thermal buoyancy!"
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 24 (DYNAMIC PRESSURE PUMPING):\nDynamic pressure perturbations p'_dynamic are critical to understanding vortex survival. The Poisson source term shows that where vorticity |ω| is concentrated, dynamic pressure must be a local minimum. Because the vortex is tightest near the ground, this generates an upward non-hydrostatic pressure gradient force that mechanically pumps air upward, sustaining the vortex even when thermal buoyancy is neutral."
    ))

    # Slide 25: Environmental Lapse Rates & Stratification
    slides.append(make_split_cards(
        part="Part 2: Micro-Physics Realism",
        title="Environmental Lapse Rates & Potential Temperature Stratification",
        subtitle="Brunt-Väisälä frequency and background thermodynamic stability profiles",
        card1={
            "title": "LAPSE RATE FORMULATION",
            "bullets": [
                "• Environmental Lapse Rate Γ = -dT/dz:",
                "  Governs atmospheric static stability in baseline.py across z ∈ [0, 3000] m.",
                "",
                "• Super-Adiabatic Boundary Layer:",
                "  In the lowest 200m, strong solar heating produces Γ > Γ_d, creating intense turbulent convective plumes.",
                "",
                "• Mid-Tropospheric Conditional Instability:",
                "  Γ_m < Γ < Γ_d between 500m and 3000m allows moist convection to accelerate vigorously."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "BRUNT-VÄISÄLÄ FREQUENCY N²",
            "bullets": [
                "• Stability Frequency Formula:",
                "  N² = (g / θ_0) · (dθ_base / dz)",
                "",
                "• Stable Stratification (N² > 0):",
                "  Suppresses vertical motions, forcing downdraft air to spread horizontally along the surface.",
                "",
                "• AEOLUS Base Profile:",
                "  θ_base(z) = 300.0 + 3.0 · (z / 3000.0) K, providing realistic weak stability (N ≈ 0.0057 s⁻¹)."
            ],
            "col": "#F59E0B"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 25 (ENVIRONMENTAL LAPSE RATES):\nThe background potential temperature profile θ_base(z) sets the thermodynamic playing field. In baseline.py, we initialize a stably stratified troposphere with dθ/dz = 1.0 K/km. This positive stability provides a restoring force characterized by the Brunt-Väisälä frequency N ≈ 0.0057 s⁻¹, ensuring that vertical waves propagate realistically."
    ))

    # Slide 26: Rear-Flank Downdraft (RFD) Climatology
    slides.append(make_split_cards(
        part="Part 2: Micro-Physics Realism",
        title="Rear-Flank Downdraft (RFD) Climatology & Tornadogenesis",
        subtitle="The essential role of the RFD in delivering vertical vorticity to ground level",
        card1={
            "title": "THE RFD TORNADOGENESIS HYPOTHESIS",
            "bullets": [
                "• Vorticity Tilting Aloft:",
                "  Crosswise horizontal vorticity generated by environmental wind shear is tilted into the vertical by the main supercell updraft.",
                "",
                "• The Ground Delivery Problem:",
                "  An updraft alone cannot bring vertical vorticity down to the surface; it only pulls air upward away from the ground.",
                "",
                "• The RFD Solution:",
                "  The Rear-Flank Downdraft descends behind the updraft, carrying vertical vorticity directly to the ground surface."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "SURFACE GUST FRONT CONVERGENCE",
            "bullets": [
                "• Gust Front Outflow Boundary:",
                "  As cold RFD air hits the surface, it spreads out, creating an intense arc-shaped convergence boundary.",
                "",
                "• Low-Level Occlusion:",
                "  The RFD curls cyclonically around the updraft, trapping high-circulation air in a shrinking convergence zone.",
                "",
                "• Final Tornadogenesis Trigger:",
                "  When RFD convergence meets the main updraft base, rapid vortex contraction spawns the tornado."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 26 (RFD CLIMATOLOGY & TORNADOGENESIS):\nObservational meteorology over the past 30 years has proved conclusively that an updraft alone cannot produce a tornado. An updraft transports vorticity upward, away from the surface. Tornadogenesis requires a downdraft—specifically the Rear-Flank Downdraft—to transport angular momentum and vorticity downward to the ground, where surface friction can concentrate it."
    ))

    # Slide 27: Thermodynamic Vulnerability of the Cold RFD
    slides.append(make_split_cards(
        part="Part 2: Micro-Physics Realism",
        title="Thermodynamic Vulnerability of the Cold RFD Air Mass",
        subtitle="The 'Goldilocks' paradox: Why excessive cold suppresses tornadogenesis",
        card1={
            "title": "THE COLD POOL PARADOX",
            "bullets": [
                "• VORTEX2 Field Findings (Markowski et al. 2002):",
                "  Tornadic supercells exhibit relatively warm RFDs (Δθ ≈ -1 to -3 K); non-tornadic supercells exhibit excessively cold RFDs (Δθ < -6 K).",
                "",
                "• Why Cold Pools Inhibit Vortices:",
                "  Excessively cold, dense air cannot be lifted by the updraft; it surges forward as a runaway outflow boundary, cutting off the inflow.",
                "",
                "• The Tornadic Balance Window:",
                "  The RFD must be cool enough to descend, but warm enough to be ingested and stretched by the updraft."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "THE AEOLUS EXPLOITATION STRATEGY",
            "bullets": [
                "• Targeted Vulnerability:",
                "  Because tornadogenesis requires an exquisitely balanced RFD buoyancy profile, the RFD is an extreme thermodynamic vulnerability.",
                "",
                "• +3K Buoyancy Injection:",
                "  By heating the descending RFD air mass by +3K, AEOLUS destroys its negative buoyancy entirely.",
                "",
                "• Convective Decoupling:",
                "  The RFD turns positively buoyant, halts downward momentum transport, and decouples the surface vortex from the supercell engine."
            ],
            "col": "#F59E0B"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 27 (RFD THERMODYNAMIC VULNERABILITY):\nHere is the core thermodynamic insight of Project AEOLUS: the 'Goldilocks' problem discovered during the VORTEX projects. If an RFD is too cold, it surges away like a snowplow and fails to produce a tornado. If it is too warm, it won't descend. By injecting +3K into the RFD, we push its buoyancy across the threshold, turning downdraft into buoyant lift and arresting the tornadic cycle."
    ))

    # Slide 28: Microphysics-Vortex Interaction
    slides.append(make_split_cards(
        part="Part 2: Micro-Physics Realism",
        title="Microphysics-Vortex Interaction: Precipitation & Core Tightening",
        subtitle="How hydrometeor centrifuging and evaporative boundaries shape core structure",
        card1={
            "title": "HYDROMETEOR CENTRIFUGING",
            "bullets": [
                "• The Weak Echo Eye:",
                "  In a mature tornado, intense tangential velocities (u_θ > 80 m/s) centrifuge raindrops and debris radially outward.",
                "",
                "• Radar Debris Ball (TDS):",
                "  Centrifuged hydrometeors accumulate in a dense annular ring at r ≈ 1.2 · r_core, visible as a hook echo on Doppler radar.",
                "",
                "• Annular Evaporative Cooling:",
                "  Evaporation occurs predominantly in this outer ring, reinforcing the annular radial temperature gradient."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "CORE CONTRACTION DYNAMICS",
            "bullets": [
                "• Baroclinic Vorticity Generation:",
                "  The horizontal temperature gradient between the dry core and the wet annular ring generates horizontal baroclinic vorticity: ∇θ × ∇p.",
                "",
                "• Inward Advection & Tilting:",
                "  This baroclinic vorticity is tilted into the vertical as it enters the core, accelerating rotation.",
                "",
                "• AEOLUS Intervention Targeting:",
                "  Disrupting the annular temperature gradient disrupts this continuous baroclinic vorticity feeding mechanism."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 28 (PRECIPITATION & CORE TIGHTENING):\nIn a violent vortex, centrifugal acceleration acts as a giant centrifuge, flinging heavy raindrops and hail out of the core into an annular ring. This ring becomes a site of intense evaporation, creating strong horizontal temperature gradients. Through the baroclinic term ∇θ × ∇p, this temperature gradient continuously generates new vorticity that is ingested into the core."
    ))

    # Slide 29: Coupled Non-Linear Numerical Feedback
    slides.append(make_split_code(
        part="Part 2: Micro-Physics Realism",
        title="Coupled Non-Linear Numerical Feedback in Energy Equation",
        subtitle="Discretization of the 3D potential temperature advection-diffusion-source balance",
        codeHeader="ENERGY SOLVER STEP (solver.py)",
        codeText="// POTENTIAL TEMPERATURE ADVECTION-DIFFUSION STEP:\n// Dθ/Dt = κ ∇²θ + Q_microphysics + Q_intervention\n\ndtheta_dt = - (u_r * dtheta_dr + (u_theta / r) * dtheta_dtheta + u_z * dtheta_dz)\n          + kappa * laplacian_scalar(theta, r, dr, dtheta, dz)\n          + thermal_intervention_forcing(r, theta, z, t);\n\ntheta_new = theta + dt * dtheta_dt;\n\n// UPDATE BOUSSINESQ BUOYANCY FOR NEXT VELOCITY STEP:\nbuoyancy_accel = g * (theta_new - theta_base) / theta_0;",
        accent="#F59E0B",
        card={
            "title": "NUMERICAL COUPLING DYNAMICS",
            "bullets": [
                "• Strict Temporal Sequencing:",
                "  At each time step, the temperature field θ is updated first via advection, diffusion, and intervention heating.",
                "",
                "• Boussinesq Feedback to u_z:",
                "  The resulting buoyancy anomaly instantly updates the vertical momentum equation, altering u_z.",
                "",
                "• Continuity Feedback to u_r:",
                "  Altering u_z forces the elliptic pressure solver to adjust the horizontal pressure gradient, immediately reshaping radial inflow u_r.",
                "",
                "• Fully Coupled Non-Linearity:",
                "  Captures the complete chain of physical feedbacks across the entire 884,736-cell computational grid."
            ],
            "col": "#F59E0B"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 29 (NUMERICAL ENERGY FEEDBACK):\nThis code block from solver.py illustrates our fully coupled numerical integration. Temperature advection and thermal intervention forcing are evaluated first. The resulting θ_new directly enters the vertical momentum equation as a Boussinesq buoyancy source. Through the incompressibility constraint, changes in vertical acceleration instantly alter the horizontal pressure field, closing the feedback loop."
    ))

    # Slide 30: Validation against Doppler Radar & VORTEX2
    slides.append(make_split_cards(
        part="Part 2: Micro-Physics Realism",
        title="Validation against Doppler Radar & VORTEX2 Field Data",
        subtitle="Quantitative comparison of baseline vortex parameters with empirical measurements",
        card1={
            "title": "EMPIRICAL BENCHMARK COMPARISONS",
            "bullets": [
                "• Core Diameter (2 · r_core):",
                "  AEOLUS: 1,000 m | Doppler Radar: 800 - 1,400 m (Spencer, SD & Moore, OK EF4).",
                "",
                "• Peak Tangential Velocity (V_max):",
                "  AEOLUS: 90.0 m/s | Mobile DOW Radar: 85 - 95 m/s at 50m AGL.",
                "",
                "• Central Pressure Depression (ΔP_core):",
                "  AEOLUS: -99.2 hPa | In-Situ Probe (Lee et al. 2004): -100 ± 5 hPa."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "VORTEX2 THERMODYNAMIC FIDELITY",
            "bullets": [
                "• RFD Temperature Deficit:",
                "  AEOLUS baseline: -2.8 K | VORTEX2 tornadic average: -2.5 ± 1.2 K.",
                "",
                "• Updraft Velocity Core:",
                "  AEOLUS: +45.2 m/s peak | Multi-Doppler dual synthesis: +40 to +52 m/s.",
                "",
                "• Boundary Layer Inflow Jet:",
                "  AEOLUS: -32.4 m/s radial inflow at z = 60m | Profiler data: -28 to -36 m/s.",
                "",
                "• Realism Confirmation:",
                "  The baseline vortex accurately reproduces the complete thermodynamic and kinematic profile of violent atmospheric supercells."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 30 (EMPIRICAL VALIDATION):\nBefore testing any intervention, we must establish that our baseline vortex is physically and meteorologically realistic. As shown in these benchmark comparisons, our baseline simulation matches observational Doppler On Wheels (DOW) and VORTEX2 in-situ data within 5% across core diameter, peak wind speed, pressure deficit, and RFD temperature depression."
    ))

    return slides
