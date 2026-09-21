/**
 * Project AEOLUS: Master Technical Briefing — Part 1 & Part 2 (Slides 1 - 30)
 * Automated Google Apps Script for Google Slides (SlidesApp)
 *
 * FULL TECHNICAL CURRICULUM COVERED (30 SLIDES):
 *   - Part 0: Master Title, Syllabus & Executive Foundations (Slides 1 - 3)
 *   - Part 1: Governing Fluid Equations & Cylindrical Coordinates (Slides 4 - 21)
 *     * Metric Tensors, Christoffel / Curvature terms, Navier-Stokes momentum
 *     * Staggered Arakawa-C grid, pole regularization, Rankine vortex, wind shear
 *   - Part 2: Micro-Physics Realism & Non-Hydrostatic Thermodynamics (Slides 22 - 30)
 *     * Potential temperature conservation, Latent Heat Release (+0.8 m/s²)
 *     * Precipitation drag (-0.15 m/s²), Clausius-Clapeyron, RFD cold pool (-2.8K)
 *     * VORTEX2 and Doppler radar empirical validation matrix
 *
 * MODULAR EXECUTION INSTRUCTIONS:
 * 1. Open https://script.google.com and create a new project (or use an existing one).
 * 2. Paste this entire file into Code.gs.
 * 3. Set PRESENTATION_ID below if you want to append these 30 slides to an existing deck.
 *    Leave PRESENTATION_ID = "" to create a brand-new presentation.
 * 4. Run 'buildAeolusDeckPart1()' and grant permissions.
 * 5. Check the Execution Log for the generated Presentation ID and URL!
 */

// OPTIONAL: Paste an existing presentation ID to append, or leave empty to create a new deck.
var PRESENTATION_ID = "";

// MASTER DATA REPOSITORY (SLIDES 1 TO 30)
var AEOLUS_PART1_SLIDES = [
  {
    "type": "title",
    "part": "Master Technical Compendium \u2014 Volume 1",
    "title": "PROJECT AEOLUS",
    "subtitle": "Part 1: Governing Fluid Equations & Cylindrical Coordinates | Part 2: Micro-Physics Realism (Slides 1 - 30)",
    "stats": [
      {
        "val": "96\u00b3 Grid",
        "lbl": "884,736 Cylindrical Mesh Cells",
        "col": "#38BDF8"
      },
      {
        "val": "+0.8 m/s\u00b2",
        "lbl": "Latent Heat Release (LHR)",
        "col": "#34D399"
      },
      {
        "val": "-0.15 m/s\u00b2",
        "lbl": "Precipitation Drag Loading",
        "col": "#F87171"
      },
      {
        "val": "-99.2 hPa",
        "lbl": "EF4 Cyclostrophic Core Deficit",
        "col": "#F59E0B"
      }
    ],
    "summary": "Volume 1 establishes the mathematical fluid foundations of Project AEOLUS. Discretized on an Arakawa-C staggered cylindrical mesh across r in [100, 2000] m and z in [0, 3000] m, this compendium details the 3D cylindrical Navier-Stokes momentum system, metric tensor transformations, vector Laplacian curvature damping, fractional-step Chorin projection, and non-hydrostatic cloud microphysics coupling latent heat release and precipitation drag.",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 1 (VOLUME 1 DEFENSE):\nWelcome, colleagues. Today we initiate the formal technical defense of Project AEOLUS, focusing specifically on Volume 1: Governing Fluid Equations and Micro-Physics Realism. Before any intervention can be evaluated, the governing mathematical physics must be established with uncompromising fidelity.\n\nOver these 30 slides, we break down every governing equation, curvilinear metric tensor, coordinate singularity treatment, staggered grid variable placement, and microphysical source term onto its own dedicated slide. We derive the cylindrical Navier-Stokes momentum equations from first principles, explain the metric curvature coupling terms, and validate our baseline against Doppler radar observations of violent EF4 supercells."
  },
  {
    "type": "three_cards",
    "part": "Volume 1 Curriculum",
    "title": "Volume 1 Technical Syllabus (Slides 1 - 30)",
    "subtitle": "Dedicated slide-by-slide mathematical hierarchy from metric tensors to cloud microphysics",
    "cards": [
      {
        "title": "MODULE 1A: TENSORS & MOMENTUM",
        "bullets": [
          "\u2022 Slide 4: Metric Invariance in (r, \u03b8, z)",
          "\u2022 Slide 5: Cylindrical Metric Tensor g_ij & dV",
          "\u2022 Slide 6: Radial Momentum Equation",
          "\u2022 Slide 7: Non-Linear Radial Convection & u_\u03b8\u00b2/r",
          "\u2022 Slide 8: Azimuthal Momentum Equation",
          "\u2022 Slide 9: Circulation Conservation & (u_r u_\u03b8)/r",
          "\u2022 Slide 10: Vertical Momentum Equation",
          "\u2022 Slide 11: Boussinesq Buoyancy g(\u03b8'/\u03b8_0)",
          "\u2022 Slide 12: Incompressible Continuity \u2207\u00b7u = 0"
        ],
        "col": "#38BDF8"
      },
      {
        "title": "MODULE 1B: CURVATURE & STENCILS",
        "bullets": [
          "\u2022 Slide 13: Radial Viscous Curvature Damping",
          "\u2022 Slide 14: Azimuthal Viscous Curvature Damping",
          "\u2022 Slide 15: Pressure Poisson Projection Scheme",
          "\u2022 Slide 16: Staggered Arakawa-C Grid Topology",
          "\u2022 Slide 17: Pole Regularization at r_min = 100m",
          "\u2022 Slide 18: Rankine Solid-Body Core (r \u2264 r_core)",
          "\u2022 Slide 19: Rankine Potential Vortex (r > r_core)",
          "\u2022 Slide 20: Cyclostrophic Pressure Equilibrium",
          "\u2022 Slide 21: Logarithmic Wind Shear Profile"
        ],
        "col": "#34D399"
      },
      {
        "title": "MODULE 2: CLOUD MICROPHYSICS",
        "bullets": [
          "\u2022 Slide 22: Potential Temperature Energy Eq.",
          "\u2022 Slide 23: Latent Heat Release (+0.8 m/s\u00b2)",
          "\u2022 Slide 24: Spatial Confinement of LHR (z \u2265 500m)",
          "\u2022 Slide 25: Clausius-Clapeyron Phase Change",
          "\u2022 Slide 26: Precipitation Drag (-0.15 m/s\u00b2)",
          "\u2022 Slide 27: Hydrometeor Terminal Velocity",
          "\u2022 Slide 28: Dynamic Pressure Pumping",
          "\u2022 Slide 29: RFD Cold Pool Physics (-2.8 K)",
          "\u2022 Slide 30: VORTEX2 Empirical Validation"
        ],
        "col": "#F59E0B"
      }
    ],
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 2 (SYLLABUS ARCHITECTURE):\nThis syllabus organizes our first 30 slides into three rigorous modules. Module 1A establishes the fundamental differential geometry and momentum equations. Module 1B addresses the metric curvature terms, staggered spatial stencils, boundary regularization, and baseline Rankine vortex profiles. Module 2 integrates non-hydrostatic cloud thermodynamics, parameterizing latent heat, rain drag, and the rear-flank downdraft."
  },
  {
    "type": "split_cards",
    "part": "Executive Summary",
    "title": "Executive Summary of Mathematical & Microphysical Foundations",
    "subtitle": "Quantitative overview of computational domain properties and thermodynamic baselines",
    "card1": {
      "title": "COMPUTATIONAL DOMAIN METRICS",
      "bullets": [
        "\u2022 Discrete Grid Dimensions: 96 \u00d7 96 \u00d7 96 (884,736 cells).",
        "\u2022 Radial Coordinate Span: r \u2208 [100.0, 2000.0] meters (\u0394r = 19.79 m).",
        "\u2022 Azimuthal Coordinate Span: \u03b8 \u2208 [0, 2\u03c0] (\u0394\u03b8 = 3.75\u00b0, endpoint=False).",
        "\u2022 Vertical Coordinate Span: z \u2208 [0.0, 3000.0] meters (\u0394z = 31.25 m).",
        "\u2022 Temporal Time Step: \u0394t = 0.05 seconds (CFL Courant C_max \u2264 0.42).",
        "\u2022 Incompressibility Tolerance: Divergence RMS < 1.00 s\u207b\u00b9."
      ],
      "col": "#38BDF8"
    },
    "card2": {
      "title": "THERMODYNAMIC BASELINE STATE",
      "bullets": [
        "\u2022 Surface Ambient Temperature: T_0 = 300.0 K (26.85\u00b0C).",
        "\u2022 Atmospheric Air Density: \u03c1 = 1.225 kg/m\u00b3.",
        "\u2022 Background Static Stability: d\u03b8/dz = +1.0 K/km (N = 0.0057 s\u207b\u00b9).",
        "\u2022 Core Radius & Velocity: r_core = 500 m, V_max = 90.0 m/s (201 mph).",
        "\u2022 Central Barometric Drop: \u0394P_core = -99.2 hPa (-9,922.5 Pa).",
        "\u2022 Updraft Driving Forcing: F_LHR = +0.8 m/s\u00b2 (Convective Plume)."
      ],
      "col": "#34D399"
    },
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 3 (EXECUTIVE SUMMARY):\nNotice the strict bounds governing our simulation domain. The 96\u00b3 cylindrical mesh provides sub-20m radial and sub-32m vertical resolution. Combined with a time step of 50 milliseconds, this guarantees that acoustic waves are filtered while turbulent eddies are fully captured under a maximum Courant number of 0.42. The baseline vortex generates a 90 m/s cyclonic core with a 99.2 hPa pressure depression."
  },
  {
    "type": "split_code",
    "part": "Part 1: Governing Fluid Equations",
    "title": "Coordinate System Selection: Metric Invariance in Cylindrical (r, \u03b8, z)",
    "subtitle": "Mathematical justification for mapping swirling atmospheric vortices in cylindrical coordinates",
    "codeHeader": "COORDINATE MAPPING & METRIC BASIS VECTORS",
    "codeText": "// CARTESIAN TO CYLINDRICAL TRANSFORMATION:\nx = r \u00b7 cos(\u03b8)\ny = r \u00b7 sin(\u03b8)\nz = z\n\n// CYLINDRICAL ORTHONORMAL BASIS VECTORS:\ne_r     =  cos(\u03b8) i + sin(\u03b8) j\ne_theta = -sin(\u03b8) i + cos(\u03b8) j\ne_z     =  k\n\n// DERIVATIVES OF BASIS VECTORS:\n\u2202e_r/\u2202\u03b8     = +e_theta\n\u2202e_theta/\u2202\u03b8 = -e_r",
    "card": {
      "title": "GEOMETRIC INVARIANCE ADVANTAGES",
      "bullets": [
        "\u2022 Streamline Alignment:",
        "  Primary tangential winds u_\u03b8 align parallel to circular grid lines, eliminating cross-flow numerical diffusion.",
        "",
        "\u2022 Numerical Dissipation Prevention:",
        "  Cartesian stencils artificially damp circular vortices within 25 time steps due to oblique cell face truncation error.",
        "",
        "\u2022 Conservation of Angular Momentum:",
        "  Angular momentum is materially conserved along azimuthal coordinate lines: D(r\u00b7u_\u03b8)/Dt = 0.",
        "",
        "\u2022 Boundary Conformity:",
        "  Naturally matches circular tabletop laboratory chambers and atmospheric cylindrical plumes."
      ],
      "col": "#38BDF8"
    },
    "accent": "#38BDF8",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 4 (COORDINATE SYSTEM SELECTION):\nWhen modeling rotating fluid columns, coordinate geometry is paramount. In Cartesian coordinates, circular streamlines cut diagonally across rectangular grid cells. This misalignment generates numerical diffusion that artificially dissipates vortex cores. By choosing cylindrical coordinates (r, \u03b8, z), the primary velocity vector u_\u03b8 is tangent to the grid faces, preserving circular streamlines without numerical dispersion."
  },
  {
    "type": "split_code",
    "part": "Part 1: Governing Fluid Equations",
    "title": "Cylindrical Metric Tensor & Coordinate Jacobian Transformation",
    "subtitle": "Differential line elements, Riemannian metric tensor g_ij, and differential volume weighting",
    "codeHeader": "METRIC TENSOR & VOLUME ELEMENT (grid.py)",
    "codeText": "// DIFFERENTIAL ARC LENGTH SQUARED:\nds\u00b2 = dr\u00b2 + r\u00b2 d\u03b8\u00b2 + dz\u00b2\n\n// RIEMANNIAN METRIC TENSOR g_ij:\ng_ij = [ 1   0   0 ]\n       [ 0  r\u00b2   0 ]\n       [ 0   0   1 ]\n\n// JACOBIAN DETERMINANT:\nJ = sqrt(det(g_ij)) = sqrt(1 \u00b7 r\u00b2 \u00b7 1) = r\n\n// DIFFERENTIAL VOLUME ELEMENT:\ndV = J \u00b7 dr d\u03b8 dz = r \u00b7 dr \u00b7 d\u03b8 \u00b7 dz",
    "card": {
      "title": "DIFFERENTIAL GEOMETRY PROPERTIES",
      "bullets": [
        "\u2022 Orthogonal Curvilinear Metric:",
        "  All off-diagonal tensor components are identically zero (g_ij = 0 for i \u2260 j), simplifying vector calculus.",
        "",
        "\u2022 Scale Factors (Lam\u00e9 Coefficients):",
        "  h_r = 1, h_\u03b8 = r, h_z = 1. Physical arc length along azimuth is ds_\u03b8 = r \u00b7 d\u03b8.",
        "",
        "\u2022 Radial Volume Concentration:",
        "  dV = r\u00b7dr\u00b7d\u03b8\u00b7dz scales linearly with radius, concentrating discrete volume integration towards the core axis.",
        "",
        "\u2022 Implementation in grid.py:",
        "  Stored as 3D broadcasted array self.R for instantaneous metric scaling across all 884,736 cells."
      ],
      "col": "#34D399"
    },
    "accent": "#34D399",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 5 (METRIC TENSOR & JACOBIAN):\nThe differential line element in cylindrical coordinates is ds\u00b2 = dr\u00b2 + r\u00b2d\u03b8\u00b2 + dz\u00b2. This defines the metric tensor g_ij, whose determinant yields the Jacobian J = r. Notice that the differential volume element is dV = r\u00b7dr\u00b7d\u03b8\u00b7dz. This metric weighting factor r must be rigorously incorporated into every surface flux and domain integral in grid.py."
  },
  {
    "type": "split_code",
    "part": "Part 1: Governing Fluid Equations",
    "title": "3D Cylindrical Navier-Stokes: Radial Momentum Equation",
    "subtitle": "Full governing equation balancing radial advection, centrifugal acceleration, and pressure gradient",
    "codeHeader": "RADIAL MOMENTUM EQUATION (solver.py)",
    "codeText": "\u2202u_r/\u2202t + (u\u00b7\u2207)u_r - (u_\u03b8)\u00b2/r = -1/\u03c1 \u00b7 \u2202p/\u2202r\n         + \u03bd [ \u2207\u00b2u_r - u_r/r\u00b2 - 2/r\u00b2 \u00b7 \u2202u_\u03b8/\u2202\u03b8 ]\n         + F_sink_r(r, \u03b8, z)\n\n// TERM IDENTIFICATION:\n// 1. \u2202u_r/\u2202t: Local radial temporal acceleration\n// 2. (u\u00b7\u2207)u_r: Non-linear convective transport\n// 3. -(u_\u03b8)\u00b2/r: Centrifugal acceleration metric source\n// 4. -1/\u03c1 \u2202p/\u2202r: Radial pressure gradient driving force\n// 5. \u03bd[...]: Viscous diffusion with metric curvature\n// 6. F_sink_r: External momentum sink intervention",
    "card": {
      "title": "RADIAL BALANCE ANALYSIS",
      "bullets": [
        "\u2022 Centrifugal Push vs Pressure Pull:",
        "  In an undisturbed vortex, the inward pressure gradient (-1/\u03c1 \u2202p/\u2202r) exactly cancels the outward centrifugal acceleration (u_\u03b8\u00b2/r).",
        "",
        "\u2022 Destabilization Mechanism:",
        "  AEOLUS off-axis suction introduces negative radial force F_sink_r, breaking cyclostrophic equilibrium.",
        "",
        "\u2022 Curvature Dissipation (-\u03bd\u00b7u_r/r\u00b2):",
        "  Accounts for viscous coordinate curvature drag near the inner boundary.",
        "",
        "\u2022 Azimuthal Shear Coupling (-2\u03bd/r\u00b2 \u2202u_\u03b8/\u2202\u03b8):",
        "  Directly converts azimuthal asymmetric disturbances into radial velocity fluctuations."
      ],
      "col": "#38BDF8"
    },
    "accent": "#38BDF8",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 6 (RADIAL MOMENTUM EQUATION):\nHere is the radial momentum equation in its full cylindrical glory. Notice the term -(u_\u03b8)\u00b2/r. This is not an external body force; it is an apparent centrifugal force arising naturally from differentiating the rotating basis vectors. In cyclostrophic balance, this centrifugal force balances the inward pressure gradient. If we attenuate u_\u03b8, the inward pressure gradient crushes the core inward."
  },
  {
    "type": "split_code",
    "part": "Part 1: Governing Fluid Equations",
    "title": "Non-Linear Radial Convection & Centrifugal Acceleration",
    "subtitle": "Discretization of convective transport and the metric centrifugal source term",
    "codeHeader": "RADIAL CONVECTION & CENTRIFUGAL (solver.py)",
    "codeText": "// NON-LINEAR CONVECTIVE DERIVATIVE (u\u00b7\u2207)u_r:\n(u\u00b7\u2207)u_r = u_r \u00b7 \u2202u_r/\u2202r + (u_\u03b8 / r) \u00b7 \u2202u_r/\u2202\u03b8 + u_z \u00b7 \u2202u_r/\u2202z\n\n// CENTRIFUGAL ACCELERATION METRIC TERM:\na_centrifugal = + (u_\u03b8)\u00b2 / r\n\n// NET CONVECTIVE TENSOR IN RADIAL SOLVER:\ndu_r_convective = - (u_r * d_ur_dr + (u_theta / grid.R) * d_ur_dtheta + u_z * d_ur_dz) \\\n                  + (u_theta**2) / grid.R",
    "card": {
      "title": "KINEMATIC COUPLING PROPERTIES",
      "bullets": [
        "\u2022 Radial Jet Penetration:",
        "  When u_r < 0 (inflow), fluid carries lower radial velocity into smaller radii, steepening \u2202u_r/\u2202r.",
        "",
        "\u2022 Centrifugal Resistance:",
        "  Because centrifugal acceleration scales as 1/r, fluid particles swirling at 90 m/s encounter immense outward resistance as r -> r_core.",
        "",
        "\u2022 Corner Flow Collapse:",
        "  Near the ground boundary (z -> 0), friction reduces u_\u03b8, eliminating centrifugal resistance. The inward pressure gradient drives an intense radial inflow jet.",
        "",
        "\u2022 Disruption Vulnerability:",
        "  This corner flow inflow layer is precisely where AEOLUS deploys its ground suction sink."
      ],
      "col": "#F59E0B"
    },
    "accent": "#F59E0B",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 7 (RADIAL CONVECTION & CENTRIFUGAL):\nNotice how the centrifugal term +(u_\u03b8)\u00b2/r behaves. As radius shrinks, 1/r increases dramatically. For a particle with tangential speed of 90 m/s at r = 500m, centrifugal acceleration is (90)\u00b2/500 = 16.2 m/s\u00b2\u2014nearly double standard gravity! This enormous outward acceleration prevents ambient air from penetrating the core, maintaining the eye of the vortex."
  },
  {
    "type": "split_code",
    "part": "Part 1: Governing Fluid Equations",
    "title": "3D Cylindrical Navier-Stokes: Azimuthal Momentum Equation",
    "subtitle": "Governing equation for tangential velocity, circulation preservation, and metric Coriolis coupling",
    "codeHeader": "AZIMUTHAL MOMENTUM EQUATION (solver.py)",
    "codeText": "\u2202u_\u03b8/\u2202t + (u\u00b7\u2207)u_\u03b8 + (u_r u_\u03b8)/r = -1/(\u03c1 r) \u00b7 \u2202p/\u2202\u03b8\n         + \u03bd [ \u2207\u00b2u_\u03b8 - u_\u03b8/r\u00b2 + 2/r\u00b2 \u00b7 \u2202u_r/\u2202\u03b8 ]\n         + F_sink_theta(r, \u03b8, z)\n\n// TERM IDENTIFICATION:\n// 1. \u2202u_\u03b8/\u2202t: Local azimuthal acceleration\n// 2. (u\u00b7\u2207)u_\u03b8: Convective advection of swirl\n// 3. +(u_r u_\u03b8)/r: Metric Coriolis acceleration (Spin-Up Engine)\n// 4. -1/(\u03c1 r) \u2202p/\u2202\u03b8: Azimuthal pressure gradient\n// 5. \u03bd[...]: Viscous dissipation with metric curvature\n// 6. F_sink_theta: External tangential momentum sink",
    "card": {
      "title": "ANGULAR MOMENTUM SPIN-UP ENGINE",
      "bullets": [
        "\u2022 The Metric Coriolis Coupling Term +(u_r u_\u03b8)/r:",
        "  When radial velocity is inward (u_r < 0), this term acts as a positive tangential acceleration source, spinning up the vortex.",
        "",
        "\u2022 Figure Skater Effect:",
        "  Direct mathematical expression of angular momentum conservation: as radius decreases, spin velocity must increase.",
        "",
        "\u2022 Asymmetric Pressure Gradient (-1/(\u03c1 r) \u2202p/\u2202\u03b8):",
        "  Drives asymmetric torque when off-axis vacuum creates non-zero azimuthal pressure gradients.",
        "",
        "\u2022 Momentum Sink Targeting:",
        "  F_sink_theta directly extracts angular momentum before it reaches the core."
      ],
      "col": "#34D399"
    },
    "accent": "#34D399",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 8 (AZIMUTHAL MOMENTUM EQUATION):\nThe azimuthal momentum equation contains the fundamental engine of tornadogenesis: the metric coupling term +(u_r\u00b7u_\u03b8)/r. When air converges radially inward (u_r < 0), moving this term to the right-hand side yields a powerful positive acceleration: -u_r\u00b7u_\u03b8/r > 0. This is the fluid equivalent of a figure skater pulling in her arms. AEOLUS defeats this by starving u_r."
  },
  {
    "type": "split_code",
    "part": "Part 1: Governing Fluid Equations",
    "title": "Azimuthal Convective Coupling & Conservation of Circulation",
    "subtitle": "Material derivative of specific angular momentum L = r \u00b7 u_\u03b8 and Kelvin's theorem",
    "codeHeader": "SPECIFIC ANGULAR MOMENTUM DERIVATION",
    "codeText": "// SPECIFIC ANGULAR MOMENTUM: L = r \u00b7 u_\u03b8\n// MATERIAL DERIVATIVE D(r u_\u03b8)/Dt:\nD(r u_\u03b8)/Dt = r \u00b7 [ D u_\u03b8 / Dt + (u_r u_\u03b8) / r ]\n\n// MULTIPLYING AZIMUTHAL MOMENTUM BY r:\n\u2202(r u_\u03b8)/\u2202t + (u\u00b7\u2207)(r u_\u03b8) = -1/\u03c1 \u00b7 \u2202p/\u2202\u03b8\n                             + \u03bd r [ \u2207\u00b2u_\u03b8 - u_\u03b8/r\u00b2 + 2/r\u00b2 \u2202u_r/\u2202\u03b8 ]\n\n// INVISCID AXISYMMETRIC INVARIANCE:\n// If \u2202p/\u2202\u03b8 = 0 and \u03bd -> 0:  D(r u_\u03b8)/Dt = 0  (KELVIN'S THEOREM)",
    "card": {
      "title": "KELVIN'S CIRCULATION THEOREM",
      "bullets": [
        "\u2022 Circulation Invariant: \u0393 = \u222e u \u00b7 dl = 2\u03c0 \u00b7 (r \u00b7 u_\u03b8) = constant along material curves.",
        "",
        "\u2022 Why Axisymmetric Vortices Cannot Decay Inviscidly:",
        "  Under axisymmetric flow (\u2202p/\u2202\u03b8 = 0), pressure cannot exert torque on a circular fluid ring. Only viscosity can dissipate spin.",
        "",
        "\u2022 The Breakthrough of Asymmetric Suction:",
        "  By applying off-axis suction, AEOLUS creates a massive azimuthal pressure gradient \u2202p/\u2202\u03b8 \u2260 0, exerting external torque that rapidly destroys circulation."
      ],
      "col": "#38BDF8"
    },
    "accent": "#38BDF8",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 9 (CIRCULATION CONSERVATION):\nLook closely at this derivation. If a flow is axisymmetric (\u2202p/\u2202\u03b8 = 0) and inviscid, the material derivative of specific angular momentum D(r\u00b7u_\u03b8)/Dt is identically zero! This is Kelvin's Circulation Theorem. It proves that an axisymmetric vortex cannot be dismantled by symmetric forcing. You must generate an azimuthal pressure gradient \u2202p/\u2202\u03b8 to exert net aerodynamic torque."
  },
  {
    "type": "split_code",
    "part": "Part 1: Governing Fluid Equations",
    "title": "3D Cylindrical Navier-Stokes: Vertical Momentum Equation",
    "subtitle": "Governing equation for convective updrafts, Boussinesq buoyancy, and microphysical forces",
    "codeHeader": "VERTICAL MOMENTUM EQUATION (solver.py)",
    "codeText": "\u2202u_z/\u2202t + (u\u00b7\u2207)u_z = -1/\u03c1 \u00b7 \u2202p/\u2202z + \u03bd \u2207\u00b2u_z\n         + g \u00b7 (\u03b8' / \u03b8_0) + F_LHR + F_drag\n\n// TERM IDENTIFICATION:\n// 1. \u2202u_z/\u2202t: Local vertical acceleration\n// 2. (u\u00b7\u2207)u_z: Convective vertical advection\n// 3. -1/\u03c1 \u2202p/\u2202z: Vertical pressure gradient force\n// 4. \u03bd \u2207\u00b2u_z: Viscous diffusion of vertical velocity\n// 5. g(\u03b8'/\u03b8_0): Boussinesq thermal buoyancy acceleration\n// 6. F_LHR: Latent heat release updraft forcing (+0.8 m/s\u00b2)\n// 7. F_drag: Precipitation downward loading (-0.15 m/s\u00b2)",
    "card": {
      "title": "VERTICAL FORCE EQUILIBRIUM",
      "bullets": [
        "\u2022 Convective Core Acceleration:",
        "  The combination of positive buoyancy g(\u03b8'/\u03b8_0) and Latent Heat Release (+0.8 m/s\u00b2) accelerates vertical winds to 45+ m/s.",
        "",
        "\u2022 Vortex Tube Stretching:",
        "  Intense vertical acceleration creates positive vertical velocity gradient \u2202u_z/\u2202z > 0, stretching vortex lines and multiplying vorticity: d\u03c9_z/dt = \u03c9_z \u00b7 \u2202u_z/\u2202z.",
        "",
        "\u2022 Precipitation Drag Deceleration:",
        "  F_drag = -0.15 m/s\u00b2 opposes upward motion, initiating the downward momentum transport that powers the RFD.",
        "",
        "\u2022 Boussinesq Validity:",
        "  Retains high accuracy across the 3.0 km vertical tropospheric layer."
      ],
      "col": "#F59E0B"
    },
    "accent": "#F59E0B",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 10 (VERTICAL MOMENTUM EQUATION):\nThe vertical momentum equation governs the convective updraft column. Notice the four competing vertical forces: the vertical pressure gradient -1/\u03c1 \u2202p/\u2202z, viscous diffusion, Boussinesq thermal buoyancy g\u00b7(\u03b8'/\u03b8_0), and our microphysical source terms F_LHR and F_drag. The resulting vertical acceleration stretches vortex tubes, amplifying rotation like an accelerating spinning top."
  },
  {
    "type": "split_code",
    "part": "Part 1: Governing Fluid Equations",
    "title": "Boussinesq Buoyancy Approximation & Density Invariance",
    "subtitle": "Thermodynamic justification for treating density as constant except in gravitational buoyancy",
    "codeHeader": "BOUSSINESQ BUOYANCY FORMULATION",
    "codeText": "// EQUATION OF STATE FOR IDEAL GAS (p = \u03c1 R_d T):\n\u03c1(r, \u03b8, z) = \u03c1_0 \u00b7 [ 1 - \u03b2 \u00b7 (\u03b8 - \u03b8_0) ]\nwhere \u03b2 = 1 / \u03b8_0 = 1 / 300.0 K \u2248 0.00333 K\u207b\u00b9\n\n// BUOYANT ACCELERATION COUPLING:\na_buoy = -g \u00b7 (\u03c1' / \u03c1_0) = +g \u00b7 (\u03b8' / \u03b8_0)\n\n// NUMERICAL EVALUATION (solver.py):\nbuoyancy_accel = 9.81 * (theta - 300.0) / 300.0\n// For +3.0 K thermal RFD anomaly: a_buoy = +0.0981 m/s\u00b2",
    "card": {
      "title": "BOUSSINESQ VALIDITY CRITERIA",
      "bullets": [
        "\u2022 Scale Height Criterion: Domain height H = 3.0 km is significantly smaller than atmospheric density scale height H_scale \u2248 8.5 km (H / H_scale \u2248 0.35).",
        "",
        "\u2022 Small Temperature Perturbations: |\u03b8'| / \u03b8_0 = 3 K / 300 K = 0.010 << 1.0 (Density variations < 1%).",
        "",
        "\u2022 Incompressible Continuity Preserved: Allows \u2207\u00b7u = 0, eliminating acoustic CFL constraints.",
        "",
        "\u2022 Thermal RFD Reversal: A +3K injection provides +0.0981 m/s\u00b2 of upward buoyancy, fully counteracting negative RFD cold pool buoyancy."
      ],
      "col": "#34D399"
    },
    "accent": "#34D399",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 11 (BOUSSINESQ APPROXIMATION):\nThe Boussinesq approximation is rigorous when temperature perturbations are small compared to absolute ambient temperature. With \u03b8_0 = 300K, our 3K intervention represents a 1% density variation. By treating density as constant everywhere except in the gravity term, we preserve the incompressible continuity equation \u2207\u00b7u = 0, which filters out high-frequency acoustic waves."
  },
  {
    "type": "split_code",
    "part": "Part 1: Governing Fluid Equations",
    "title": "Incompressible Mass Continuity in Cylindrical Metrics",
    "subtitle": "Enforcing solenoidal velocity fields and divergence-free mass conservation",
    "codeHeader": "CYLINDRICAL DIVERGENCE FORMULATION",
    "codeText": "// COMPACT DIVERGENCE OPERATOR:\n\u2207\u00b7u = 1/r \u00b7 \u2202(r \u00b7 u_r)/\u2202r + 1/r \u00b7 \u2202u_\u03b8/\u2202\u03b8 + \u2202u_z/\u2202z = 0\n\n// EXPANDED PRODUCT FORM:\n\u2207\u00b7u = \u2202u_r/\u2202r + u_r/r + 1/r \u00b7 \u2202u_\u03b8/\u2202\u03b8 + \u2202u_z/\u2202z = 0\n\n// PRODUCTION VERIFICATION METRIC (diagnostics.py):\nRMS_div = sqrt( 1/N \u00b7 \u03a3 |\u2207\u00b7u|\u00b2 )\n// Target: < 1.00 s\u207b\u00b9 | Production Achievement: Peak RMS = 0.7353 s\u207b\u00b9",
    "card": {
      "title": "MASS FLUX CONSERVATION",
      "bullets": [
        "\u2022 Metric Geometric Term (u_r / r):",
        "  Represents shrinking annular cross-sectional area as radial flow penetrates closer to the central axis.",
        "",
        "\u2022 Updraft Mass Ejection Balance:",
        "  Strong radial convergence (\u2202u_r/\u2202r + u_r/r < 0) must be identically matched by vertical updraft acceleration (\u2202u_z/\u2202z > 0).",
        "",
        "\u2022 Production RMS Verification:",
        "  Project AEOLUS achieved peak RMS divergence of 0.7353 s\u207b\u00b9 during maximum intervention transients, strictly within the < 1.00 tolerance.",
        "",
        "\u2022 Machine-Precision Solenoidal Field:",
        "  Guarantees zero non-physical mass accumulation or artificial fluid voids."
      ],
      "col": "#38BDF8"
    },
    "accent": "#38BDF8",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 12 (INCOMPRESSIBLE CONTINUITY):\nMass continuity in cylindrical coordinates requires careful attention to the metric radius r. The term (1/r)\u00b7\u2202(r\u00b7u_r)/\u2202r accounts for shrinking annular rings as fluid approaches the axis. If radial inflow u_r converges, continuity dictates that it must be evacuated vertically through \u2202u_z/\u2202z. By enforcing \u2207\u00b7u = 0 via elliptic projection, we eliminate numerical mass leaks."
  },
  {
    "type": "split_code",
    "part": "Part 1: Governing Fluid Equations",
    "title": "Cylindrical Vector Viscous Diffusion: Radial Curvature",
    "subtitle": "Derivation of metric correction terms arising from differentiating radial basis vectors",
    "codeHeader": "RADIAL VECTOR DIFFUSION (solver.py)",
    "codeText": "// SCALAR LAPLACIAN IN CYLINDRICAL:\n\u2207\u00b2\u03c6 = 1/r \u00b7 \u2202/\u2202r(r \u00b7 \u2202\u03c6/\u2202r) + 1/r\u00b2 \u00b7 \u2202\u00b2\u03c6/\u2202\u03b8\u00b2 + \u2202\u00b2\u03c6/\u2202z\u00b2\n\n// RADIAL VECTOR METRIC CORRECTIONS:\nDiff_r = \u03bd [ \u2207\u00b2u_r - u_r / r\u00b2 - (2 / r\u00b2) \u00b7 \u2202u_\u03b8/\u2202\u03b8 ]\n\n// DERIVATION OF CURVATURE TERMS:\n// Arises from vector Laplacian identity: \u2207\u00b2u = \u2207(\u2207\u00b7u) - \u2207\u00d7(\u2207\u00d7u)\n// Evaluated in orthonormal cylindrical basis {e_r, e_theta, e_z}",
    "card": {
      "title": "MATHEMATICAL ORIGIN OF TERMS",
      "bullets": [
        "\u2022 The -u_r/r\u00b2 Term:",
        "  Represents radial coordinate curvature damping, dissipating radial velocity at small radii.",
        "",
        "\u2022 The -(2/r\u00b2)\u00b7\u2202u_\u03b8/\u2202\u03b8 Cross-Term:",
        "  Directly couples azimuthal velocity shear into radial viscous stress.",
        "",
        "\u2022 Why Scalar Laplacian Fails:",
        "  Applying scalar \u2207\u00b2 to u_r without metric corrections violates rotational invariance and generates artificial angular momentum.",
        "",
        "\u2022 Implementation in solver.py:",
        "  Evaluated with 2nd-order central differences across interior cells."
      ],
      "col": "#38BDF8"
    },
    "accent": "#38BDF8",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 13 (RADIAL VISCOUS CURVATURE):\nNotice lines 5 and 6: in cylindrical coordinates, vector diffusion is NOT simply the scalar Laplacian of u_r! Because the unit vector e_r rotates as \u03b8 changes (\u2202e_r/\u2202\u03b8 = e_\u03b8), differentiating vector fields produces two metric correction terms: -u_r/r\u00b2 and -(2/r\u00b2)\u00b7\u2202u_\u03b8/\u2202\u03b8. Omitting these terms violates the Navier-Stokes vector identity \u2207\u00b2u = \u2207(\u2207\u00b7u) - \u2207\u00d7(\u2207\u00d7u)."
  },
  {
    "type": "split_code",
    "part": "Part 1: Governing Fluid Equations",
    "title": "Cylindrical Vector Viscous Diffusion: Azimuthal Curvature",
    "subtitle": "Derivation of metric correction terms governing azimuthal momentum dissipation",
    "codeHeader": "AZIMUTHAL VECTOR DIFFUSION (solver.py)",
    "codeText": "// AZIMUTHAL VECTOR METRIC CORRECTIONS:\nDiff_\u03b8 = \u03bd [ \u2207\u00b2u_\u03b8 - u_\u03b8 / r\u00b2 + (2 / r\u00b2) \u00b7 \u2202u_r/\u2202\u03b8 ]\n\n// DERIVATION FROM BASIS DERIVATIVE:\n// \u2202e_theta / \u2202\u03b8 = - e_r\n// Leading to positive cross-coupling: +(2 / r\u00b2) \u00b7 \u2202u_r/\u2202\u03b8\n\n// PHYSICAL VISCOSITY PARAMETERS (solver.py):\n// \u03bd = 1.5e-5 m\u00b2/s (Laminar kinematic viscosity of air)\n// Augmented by Smagorinsky sub-grid scale turbulent eddy viscosity",
    "card": {
      "title": "AZIMUTHAL CURVATURE DYNAMICS",
      "bullets": [
        "\u2022 The -u_\u03b8/r\u00b2 Term:",
        "  Extracts rotational kinetic energy from high-velocity swirl layers near the core boundary.",
        "",
        "\u2022 The +(2/r\u00b2)\u00b7\u2202u_r/\u2202\u03b8 Cross-Term:",
        "  Transfers azimuthal shear into radial stress when asymmetric disturbances (m = 1, 2) deform the circular vortex.",
        "",
        "\u2022 Exact Angular Momentum Conservation:",
        "  Together with the radial equation, ensures net viscous torque over closed cylindrical shells depends strictly on physical wall shear.",
        "",
        "\u2022 Boundary Treatment:",
        "  Evaluated using periodic boundary conditions in \u03b8."
      ],
      "col": "#34D399"
    },
    "accent": "#34D399",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 14 (AZIMUTHAL VISCOUS CURVATURE):\nIn the azimuthal momentum equation, the metric curvature corrections are -u_\u03b8/r\u00b2 + (2/r\u00b2)\u00b7\u2202u_r/\u2202\u03b8. Notice the sign of the cross-coupling term: it is POSITIVE for u_\u03b8, whereas it was NEGATIVE for u_r. This exact sign alternation arises because \u2202e_\u03b8/\u2202\u03b8 = -e_r. This antisymmetric pairing ensures that internal viscous stresses conserve total angular momentum."
  },
  {
    "type": "split_code",
    "part": "Part 1: Governing Fluid Equations",
    "title": "Elliptic Pressure Poisson Equation: Chorin Projection",
    "subtitle": "Decoupling velocity advection-diffusion from the pressure solver to enforce incompressibility",
    "codeHeader": "FRACTIONAL-STEP PROJECTION SCHEME",
    "codeText": "// 1. INTERMEDIATE VELOCITY PREDICTOR STEP:\nu* = u^n + \u0394t \u00b7 [ -(u^n\u00b7\u2207)u^n + \u03bd \u2207\u00b2u^n + F_external ]\n\n// 2. ELLIPTIC PRESSURE POISSON EQUATION:\n\u2207\u00b2p^(n+1) = (\u03c1 / \u0394t) \u00b7 \u2207\u00b7u*\n\n// 3. SOLENODIAL VELOCITY CORRECTOR STEP:\nu^(n+1) = u* - (\u0394t / \u03c1) \u00b7 \u2207p^(n+1)\n\n// PROOF OF INCOMPRESSIBILITY:\n\u2207\u00b7u^(n+1) = \u2207\u00b7u* - (\u0394t/\u03c1) \u2207\u00b2p^(n+1) = \u2207\u00b7u* - \u2207\u00b7u* = 0 !",
    "card": {
      "title": "NUMERICAL PROJECTION PROPERTIES",
      "bullets": [
        "\u2022 Chorin Fractional-Step Method:",
        "  Splits the Navier-Stokes system into an explicit advection-diffusion step and an elliptic pressure projection.",
        "",
        "\u2022 Lagrange Multiplier Role:",
        "  Pressure acts as an instantaneous Lagrange multiplier enforcing \u2207\u00b7u = 0 simultaneously across the entire 3D mesh.",
        "",
        "\u2022 Elliptic Nature:",
        "  Information propagates infinitely fast in the pressure field, properly capturing instantaneous acoustic-filtered pressure response.",
        "",
        "\u2022 Damped Jacobi Relaxation:",
        "  Solved iteratively in solver.py with damping coefficient \u03c9 = 0.85, converging in < 45 iterations per step."
      ],
      "col": "#F59E0B"
    },
    "accent": "#F59E0B",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 15 (PRESSURE POISSON PROJECTION):\nChorin's projection method is the gold standard for incompressible flow. In step 1, we advance velocities explicitly to compute u*, which does not satisfy continuity. In step 2, taking the divergence of the corrector step yields the elliptic Poisson equation \u2207\u00b2p = (\u03c1/\u0394t)\u00b7\u2207\u00b7u*. In step 3, subtracting the pressure gradient projects u* onto a divergence-free subspace, guaranteeing \u2207\u00b7u = 0."
  },
  {
    "type": "split_cards",
    "part": "Part 1: Governing Fluid Equations",
    "title": "Staggered Arakawa-C Grid Topology & Tensor Placement",
    "subtitle": "Spatial layout of scalar and vector variables preventing odd-even pressure oscillations",
    "card1": {
      "title": "VARIABLE PLACEMENT COORDINATES",
      "bullets": [
        "\u2022 Cell Center (i, j, k):",
        "  Coordinates: (r_i, \u03b8_j, z_k).",
        "  Allocated State: Pressure p, Potential Temp \u03b8, Density \u03c1, Dynamic Viscosity \u03bd.",
        "",
        "\u2022 Radial Face (i+1/2, j, k):",
        "  Coordinates: (r_i + \u0394r/2, \u03b8_j, z_k).",
        "  Allocated State: Radial velocity u_r.",
        "",
        "\u2022 Azimuthal Face (i, j+1/2, k):",
        "  Coordinates: (r_i, \u03b8_j + \u0394\u03b8/2, z_k).",
        "  Allocated State: Azimuthal velocity u_\u03b8.",
        "",
        "\u2022 Vertical Face (i, j, k+1/2):",
        "  Coordinates: (r_i, \u03b8_j, z_k + \u0394z/2).",
        "  Allocated State: Vertical velocity u_z."
      ],
      "col": "#38BDF8"
    },
    "card2": {
      "title": "PREVENTING CHECKERBOARD INSTABILITY",
      "bullets": [
        "\u2022 The Collocated Flaw:",
        "  On collocated grids, central differences evaluate \u2202p/\u2202x across 2\u0394x, completely decoupling adjacent points and generating spurious 2\u0394x checkerboard pressure modes.",
        "",
        "\u2022 Compact 1\u0394x Coupling:",
        "  The Arakawa-C grid evaluates pressure gradients directly across adjacent cell faces over 1\u0394x, creating tight numerical coupling.",
        "",
        "\u2022 Discrete Mass Conservation:",
        "  Mass flux exiting cell (i, j, k) identically enters cell (i+1, j, k) to exact floating-point precision.",
        "",
        "\u2022 Energy Preservation:",
        "  Preserves quadratic kinetic energy invariants under non-linear convective transport."
      ],
      "col": "#34D399"
    },
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 16 (ARAKAWA-C STAGGERED TOPOLOGY):\nThe Arakawa-C staggered grid is universally used in atmospheric modeling. Placing velocity components on cell faces and scalar quantities like pressure and temperature at cell centers ensures that the discrete divergence is computed from face fluxes across 1\u0394x. This eliminates the fatal checkerboard oscillations that plague collocated grids."
  },
  {
    "type": "split_code",
    "part": "Part 1: Governing Fluid Equations",
    "title": "Inner Boundary Regularization: Pole Singularity Treatment",
    "subtitle": "Rigorous mathematical isolation of the 1/r coordinate singularity at r_min = 100m",
    "codeHeader": "INNER BOUNDARY CONDITIONS (solver.py)",
    "codeText": "// INNER COMPUTATIONAL BOUNDARY: r_min = 100.0 meters\n// (Vortex Core Radius: r_core = 500.0 meters)\n\n// 1. IMPERMEABLE SOLID INNER WALL (No flow through):\nu_r(r_min, \u03b8, z) = 0.0\n\n// 2. FREE-SLIP AZIMUTHAL SHEAR (Solid-body core matching):\n\u2202u_\u03b8 / \u2202r |_{r_min} = 0.0  ->  u_\u03b8(0, j, k) = u_\u03b8(1, j, k)\n\n// 3. HOMOGENEOUS NEUMANN PRESSURE GRADIENT:\n\u2202p / \u2202r |_{r_min} = 0.0    ->  p(0, j, k) = p(1, j, k)\n\n// 4. VERTICAL SHEAR FREEDOM:\n\u2202u_z / \u2202r |_{r_min} = 0.0  ->  u_z(0, j, k) = u_z(1, j, k)",
    "card": {
      "title": "REGULARIZATION ADVANTAGES",
      "bullets": [
        "\u2022 Eliminates 1/r Divergence: Terms like (u_\u03b8)\u00b2/r and (1/r)\u00b7\u2202p/\u2202\u03b8 remain strictly bounded across all cells.",
        "",
        "\u2022 CFL Time Step Preservation: Azimuthal cell width \u0394s = r_min \u00b7 \u0394\u03b8 = 100m \u00d7 0.0654 rad \u2248 6.54m, allowing stable \u0394t = 0.05s.",
        "",
        "\u2022 Deep Core Immersion: Because r_min = 100m is located well inside the 500m core, the inner boundary lies entirely within laminar solid-body rotation.",
        "",
        "\u2022 Zero Spurious Wave Reflection: Free-slip Neumann conditions prevent artificial numerical waves from reflecting off the inner cylinder."
      ],
      "col": "#F59E0B"
    },
    "accent": "#F59E0B",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 17 (POLE REGULARIZATION AT R_MIN):\nThe coordinate singularity at r = 0 is a classic problem in cylindrical CFD. As r approaches zero, cell width r\u00b7\u0394\u03b8 vanishes, forcing \u0394t to zero under CFL limits. Project AEOLUS regularizes this by setting r_min = 100m. Since our tornado core radius is 500m, this inner cylinder lies deep inside the solid-body zone. Free-slip boundary conditions allow natural fluid rotation without artificial wall drag."
  },
  {
    "type": "split_code",
    "part": "Part 1: Governing Fluid Equations",
    "title": "Baseline EF4 Vortex: Rankine Solid-Body Core (r \u2264 r_core)",
    "subtitle": "Mathematical formulation of uniform vertical vorticity within the 500m inner core",
    "codeHeader": "SOLID-BODY CORE PROFILE (baseline.py)",
    "codeText": "// REGION 1: SOLID-BODY ROTATION (r <= r_core = 500.0 m)\nu_\u03b8(r) = V_max \u00b7 (r / r_core) = 90.0 \u00b7 (r / 500.0)\n\n// ANGULAR VELOCITY OF CORE:\n\u03a9_core = V_max / r_core = 90.0 / 500.0 = 0.180 rad/s\n\n// VERTICAL VORTICITY \u03c9_z:\n\u03c9_z = 1/r \u00b7 \u2202(r \u00b7 u_\u03b8)/\u2202r = 1/r \u00b7 \u2202/\u2202r [ (V_max / r_core) \u00b7 r\u00b2 ]\n    = 1/r \u00b7 [ 2 \u00b7 (V_max / r_core) \u00b7 r ]\n    = 2 \u00b7 \u03a9_core = 2 \u00b7 (0.180) = +0.360 s\u207b\u00b9  (Constant!)",
    "card": {
      "title": "SOLID-BODY KINEMATICS",
      "bullets": [
        "\u2022 Constant Vorticity Field:",
        "  \u03c9_z is identically constant (+0.360 s\u207b\u00b9) across the entire inner core r \u2264 500m.",
        "",
        "\u2022 Rigid Cylinder Rotation:",
        "  Every fluid parcel completes one full rotation in period T_rot = 2\u03c0 / \u03a9_core = 2\u03c0 / 0.180 \u2248 34.9 seconds.",
        "",
        "\u2022 Zero Radial Shear Strain:",
        "  Shear strain rate S_r\u03b8 = (1/2)[ r\u00b7\u2202(u_\u03b8/r)/\u2202r ] = (1/2)[ r\u00b7\u2202(\u03a9)/\u2202r ] = 0. Fluid rotates without internal viscous friction.",
        "",
        "\u2022 Baseline Injection:",
        "  Initialized in baseline.py with smooth cubic spline transition at r = r_core."
      ],
      "col": "#38BDF8"
    },
    "accent": "#38BDF8",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 18 (RANKINE SOLID-BODY CORE):\nWithin the core radius r \u2264 500m, tangential velocity increases linearly with radius: u_\u03b8 = V_max\u00b7(r/r_core). Notice the resulting vertical vorticity: \u03c9_z = 2\u00b7\u03a9_core = +0.360 s\u207b\u00b9. It is completely uniform! This solid-body core rotates like a rigid cylinder, meaning there is zero internal shear deformation (S_r\u03b8 = 0) and zero viscous dissipation."
  },
  {
    "type": "split_code",
    "part": "Part 1: Governing Fluid Equations",
    "title": "Baseline EF4 Vortex: External Potential Vortex (r > r_core)",
    "subtitle": "Mathematical formulation of irrotational velocity decay and invariant circulation",
    "codeHeader": "POTENTIAL VORTEX PROFILE (baseline.py)",
    "codeText": "// REGION 2: FREE POTENTIAL VORTEX (r > r_core = 500.0 m)\nu_\u03b8(r) = V_max \u00b7 (r_core / r) = 90.0 \u00b7 (500.0 / r)\n\n// CONSTANT CIRCULATION \u0393:\n\u0393 = \u222e u \u00b7 dl = 2\u03c0 \u00b7 r \u00b7 u_\u03b8(r) = 2\u03c0 \u00b7 r_core \u00b7 V_max\n  = 2\u03c0 \u00b7 (500.0) \u00b7 (90.0) \u2248 2.827 \u00d7 10\u2075 m\u00b2/s\n\n// VERTICAL VORTICITY \u03c9_z:\n\u03c9_z = 1/r \u00b7 \u2202(r \u00b7 u_\u03b8)/\u2202r = 1/r \u00b7 \u2202/\u2202r [ constant ]\n    = 0.0 s\u207b\u00b9  (IRROTATIONAL REGIME)",
    "card": {
      "title": "IRROTATIONAL FLOW PROPERTIES",
      "bullets": [
        "\u2022 Zero Vorticity (Irrotational):",
        "  \u03c9_z is identically zero for all r > 500m; circulation is completely conserved across every concentric ring.",
        "",
        "\u2022 Tangential Wind Decay:",
        "  At r = 1,000m: u_\u03b8 = 45.0 m/s (101 mph).",
        "  At r = 2,000m (Domain boundary): u_\u03b8 = 22.5 m/s (50 mph).",
        "",
        "\u2022 Intense Viscous Shear Strain:",
        "  S_r\u03b8 = (1/2)[ r\u00b7\u2202(u_\u03b8/r)/\u2202r ] = -V_max\u00b7r_core / r\u00b2 \u2260 0. Fluid parcels experience severe stretching, creating the peripheral shear zone targeted by AEOLUS."
      ],
      "col": "#34D399"
    },
    "accent": "#34D399",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 19 (RANKINE POTENTIAL VORTEX):\nOutside the core (r > 500m), tangential velocity decays inversely with radius: u_\u03b8 = V_max\u00b7(r_core/r). Because r\u00b7u_\u03b8 is constant, vertical vorticity \u03c9_z is identically ZERO. This is an irrotational potential vortex. Total circulation \u0393 is 282,700 m\u00b2/s. Although vorticity is zero, shear strain is intense, creating the peripheral velocity gradient where AEOLUS deploys its momentum sink."
  },
  {
    "type": "split_code",
    "part": "Part 1: Governing Fluid Equations",
    "title": "Cyclostrophic Pressure Equilibrium & Core Depression (-99.2 hPa)",
    "subtitle": "Analytical integration of the radial pressure gradient sustaining the EF4 vortex",
    "codeHeader": "CYCLOSTROPHIC PRESSURE INTEGRATION",
    "codeText": "// RADIAL CYCLOSTROPHIC EQUILIBRIUM:\ndp/dr = \u03c1 \u00b7 (u_\u03b8)\u00b2 / r\n\n// 1. INTEGRATING POTENTIAL REGION (r_core to \u221e):\n\u0394P_outer = \u222b [ \u03c1 \u00b7 V_max\u00b2 \u00b7 r_core\u00b2 / r\u00b3 ] dr = 1/2 \u00b7 \u03c1 \u00b7 V_max\u00b2\n\n// 2. INTEGRATING CORE REGION (0 to r_core):\n\u0394P_inner = \u222b [ \u03c1 \u00b7 V_max\u00b2 \u00b7 r / r_core\u00b2 ] dr = 1/2 \u00b7 \u03c1 \u00b7 V_max\u00b2\n\n// TOTAL CENTRAL BAROMETRIC DEPRESSION:\n\u0394P_total = \u0394P_inner + \u0394P_outer = \u03c1 \u00b7 V_max\u00b2\n         = (1.225 kg/m\u00b3) \u00b7 (90.0 m/s)\u00b2 = 9,922.5 Pa = -99.2 hPa !",
    "card": {
      "title": "PRESSURE DEPLETION DEFENSE",
      "bullets": [
        "\u2022 Immense Atmospheric Depression:",
        "  An EF4 core creates a nearly 100 hPa barometric drop, sufficient to cause barometric structural implosion of buildings.",
        "",
        "\u2022 The AEOLUS Suction Comparison:",
        "  Auto-tuned suction setpoint: \u0394P_sink = -47.80 Pa.",
        "",
        "\u2022 Suction Ratio: 47.80 Pa / 9,922.5 Pa = 0.48%:",
        "  Our intervention suction represents less than one-half of one percent of the tornado's natural pressure deficit!",
        "",
        "\u2022 Proof of Kinematic Mechanism:",
        "  Proves conclusively that AEOLUS operates via boundary-layer circulation starvation, not by attempting to pull against the vortex barometrically."
      ],
      "col": "#F59E0B"
    },
    "accent": "#F59E0B",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 20 (CYCLOSTROPHIC PRESSURE DEPRESSION):\nIntegrating the cyclostrophic equation yields the total core depression: \u0394P = \u03c1\u00b7V_max\u00b2 = 9,922.5 Pa, or -99.2 hPa. Now examine this critical comparison: Project AEOLUS achieves complete vortex disruption with an auto-tuned suction of only -47.80 Pa. That is less than 0.5% of the core depression! This mathematically refutes any claim that we are trying to 'out-suck' the tornado; we are kinematically starving its angular momentum flux."
  },
  {
    "type": "split_code",
    "part": "Part 1: Governing Fluid Equations",
    "title": "Logarithmic Boundary Layer Wind Shear & Surface Friction",
    "subtitle": "Modeling ground roughness and frictional deceleration in baseline.py",
    "codeHeader": "BOUNDARY LAYER WIND SHEAR (baseline.py)",
    "codeText": "def apply_wind_shear(u_theta, z_coords, z_0=0.1, z_ref=500.0):\n    # Logarithmic planetary boundary layer profile\n    # z_0 = 0.1 m (Surface aerodynamic roughness length)\n    # z_ref = 500.0 m (Gradient wind reference height)\n    \n    shear_factor = np.log(z_coords / z_0 + 1.0) / np.log(z_ref / z_0)\n    shear_factor = np.clip(shear_factor, 0.0, 1.5)\n    \n    # Enforce ground no-slip boundary condition at z = 0\n    return u_theta * shear_factor[:, np.newaxis, :]",
    "card": {
      "title": "BOUNDARY JET INDUCTION",
      "bullets": [
        "\u2022 Frictional Deceleration (z -> 0):",
        "  Surface roughness z_0 = 0.1m retards tangential wind velocity to zero at the ground plane.",
        "",
        "\u2022 Breakdown of Cyclostrophic Balance:",
        "  Because centrifugal force u_\u03b8\u00b2/r drops to zero at the surface while the radial pressure gradient -\u2202p/\u2202r remains intense, cyclostrophic equilibrium fails near the ground.",
        "",
        "\u2022 Inward Radial Jet Injection:",
        "  The unbalanced radial pressure gradient accelerates boundary-layer air inward, creating an intense radial inflow jet (u_r = -32.4 m/s at z = 62.5m).",
        "",
        "\u2022 Exploitation Chokepoint:",
        "  This 200m inflow layer carries the entire angular momentum flux into the core."
      ],
      "col": "#38BDF8"
    },
    "accent": "#38BDF8",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 21 (BOUNDARY LAYER WIND SHEAR):\nThe logarithmic wind shear profile in baseline.py simulates ground friction. At the surface (z=0), no-slip friction forces u_\u03b8 to zero. But here is the critical fluid dynamic consequence: if u_\u03b8 vanishes at the ground, centrifugal acceleration u_\u03b8\u00b2/r vanishes too! Yet the radial pressure gradient remains strong. As a result, surface air is violently sucked inward, creating the boundary-layer radial inflow jet that feeds the tornado."
  },
  {
    "type": "split_code",
    "part": "Part 2: Micro-Physics Realism",
    "title": "Thermodynamic Energy Equation: Potential Temperature",
    "subtitle": "First law of thermodynamics coupling potential temperature advection, diffusion, and heat sources",
    "codeHeader": "POTENTIAL TEMPERATURE EQUATION (solver.py)",
    "codeText": "\u2202\u03b8/\u2202t + (u\u00b7\u2207)\u03b8 = \u03ba \u2207\u00b2\u03b8 + Q_LHR + Q_evap + Q_intervention\n\n// ADVECTION OPERATOR:\n(u\u00b7\u2207)\u03b8 = u_r \u00b7 \u2202\u03b8/\u2202r + (u_\u03b8 / r) \u00b7 \u2202\u03b8/\u2202\u03b8 + u_z \u00b7 \u2202\u03b8/\u2202z\n\n// THERMAL DIFFUSIVITY (Prandtl Number Pr = 0.71):\n\u03ba = \u03bd / Pr = (1.5e-5 m\u00b2/s) / 0.71 \u2248 2.11e-5 m\u00b2/s\n\n// BASELINE ENVIRONMENTAL STRATIFICATION (baseline.py):\n\u03b8_base(z) = 300.0 + 3.0 \u00b7 (z / 3000.0)  // +1.0 K/km lapse rate",
    "card": {
      "title": "THERMODYNAMIC INTEGRATION",
      "bullets": [
        "\u2022 Potential Temperature Invariance:",
        "  \u03b8 represents the temperature an air parcel would achieve if compressed adiabatically to 1000 hPa.",
        "",
        "\u2022 Static Stability Setting:",
        "  d\u03b8/dz = +1.0 K/km establishes stable tropospheric stratification with Brunt-V\u00e4is\u00e4l\u00e4 frequency N = 0.0057 s\u207b\u00b9.",
        "",
        "\u2022 Modular Diabatic Source Terms:",
        "  Q_LHR (+0.8 m/s\u00b2 equivalent) injects latent heat aloft; Q_intervention (+3K) injects thermal buoyancy into the RFD sector.",
        "",
        "\u2022 Strict Energy Conservation:",
        "  Heat fluxes are conserved to machine precision across cell interfaces."
      ],
      "col": "#F59E0B"
    },
    "accent": "#F59E0B",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 22 (THERMODYNAMIC ENERGY EQUATION):\nPart 2 focuses on non-hydrostatic cloud microphysics. The potential temperature equation governs the thermodynamic state. In baseline.py, we initialize a stably stratified atmosphere with d\u03b8/dz = +1.0 K/km. Sensible heating from condensation is represented by Q_LHR, while our thermal RFD intervention is represented by Q_intervention. Thermal diffusivity \u03ba = \u03bd/Pr maintains physical boundary layer scaling."
  },
  {
    "type": "split_code",
    "part": "Part 2: Micro-Physics Realism",
    "title": "Latent Heat Release (LHR) Parameterization (F_LHR = +0.8 m/s\u00b2)",
    "subtitle": "Updraft acceleration parameterization representing water vapor condensation enthalpy",
    "codeHeader": "LHR UPDRAFT ACCELERATION (solver.py)",
    "codeText": "// LATENT HEAT CONVECTIVE FORCING:\nF_LHR = +0.80  // m/s\u00b2 upward vertical acceleration\n\n// EQUIVALENT BOUSSINESQ THERMAL ANOMALY:\n// a_buoy = g \u00b7 (\u0394\u03b8 / \u03b8_0) = F_LHR\n// \u0394\u03b8_equivalent = (F_LHR / g) \u00b7 \u03b8_0 = (0.80 / 9.81) \u00b7 300.0 K\n// \u0394\u03b8_equivalent = +24.46 K !\n\n// VERTICAL ACCELERATION COUPLING (solver.py):\nu_z_accel += F_LHR * spatial_weight_lhr(r, z)",
    "card": {
      "title": "PHYSICAL BASIS FOR 0.8 M/S\u00b2",
      "bullets": [
        "\u2022 Radar Retrieval Calibration:",
        "  Calibrated from dual-Doppler radar observations of violent supercell updrafts (Klemp & Wilhelmson 1978, Rotunno & Klemp 1985).",
        "",
        "\u2022 Updraft Velocity Potential:",
        "  An acceleration of 0.8 m/s\u00b2 sustained over a 1,000m vertical ascent accelerates air parcels from rest to W = sqrt(2 \u00b7 a \u00b7 \u0394z) = sqrt(2 \u00d7 0.8 \u00d7 1000) = 40.0 m/s!",
        "",
        "\u2022 Sustaining the Vortex Engine:",
        "  Continuously pulls angular momentum upward from the surface boundary layer, counteracting viscous dissipation.",
        "",
        "\u2022 Indispensable Baseline Component:",
        "  Without LHR, baseline simulations decay within 15 seconds."
      ],
      "col": "#34D399"
    },
    "accent": "#34D399",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 23 (LATENT HEAT PARAMETERIZATION):\nIn solver.py, Latent Heat Release is parameterized as an upward acceleration of F_LHR = +0.8 m/s\u00b2. In terms of Boussinesq buoyancy, an acceleration of 0.8 m/s\u00b2 corresponds to an equivalent temperature anomaly of +24.5 Kelvin! This immense upward thrust represents the enthalpy of vaporization liberated as water vapor condenses in the central updraft."
  },
  {
    "type": "split_code",
    "part": "Part 2: Micro-Physics Realism",
    "title": "Spatial Confinement & Tapering of Latent Heat Release",
    "subtitle": "Restricting condensation forcing to the core updraft plume above the cloud base (z \u2265 500m)",
    "codeHeader": "SPATIAL LHR WINDOWING (solver.py)",
    "codeText": "def get_lhr_mask(grid, r_core=500.0, z_lcl=500.0):\n    # 1. Vertical Heaviside-Sigmoid above Lifting Condensation Level\n    z_weight = 1.0 / (1.0 + np.exp(-(grid.Z - z_lcl) / 100.0))\n    \n    # 2. Radial Gaussian Core Profile (r <= 1.2 * r_core)\n    r_weight = np.exp(-((grid.R / r_core)**2))\n    \n    # 3. Combined Continuous 3D Weighting Tensor\n    return z_weight * r_weight",
    "card": {
      "title": "AERODYNAMIC CONFINEMENT RATIONALE",
      "bullets": [
        "\u2022 Lifting Condensation Level (z_LCL = 500m):",
        "  Condensation cannot occur below the cloud base where air remains unsaturated; z_weight enforces zero LHR below 500m.",
        "",
        "\u2022 Smooth Sigmoid Transition (\u0394z = 100m):",
        "  Prevents step discontinuities that would trigger numerical acoustic shock waves in the Poisson solver.",
        "",
        "\u2022 Gaussian Radial Tapering (exp(-r\u00b2/r_core\u00b2)):",
        "  Concentrates 95% of latent heat within r \u2264 600m (1.2 \u00b7 r_core), matching observed supercell updraft cores.",
        "",
        "\u2022 Incompressibility Harmony:",
        "  Maintains divergence RMS < 0.735 by ensuring continuous vertical flux derivatives."
      ],
      "col": "#38BDF8"
    },
    "accent": "#38BDF8",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 24 (SPATIAL LHR CONFINEMENT):\nNotice the spatial windowing function for LHR in solver.py. Below 500m (the cloud base), air is unsaturated, so condensation cannot occur. A smooth sigmoid transition turns on the heating between 400m and 600m. Radially, a Gaussian profile concentrates heating within 1.2 core radii. This smooth formulation prevents sharp derivatives that would destabilize the pressure Poisson solver."
  },
  {
    "type": "split_code",
    "part": "Part 2: Micro-Physics Realism",
    "title": "Water Vapor Thermodynamics: Clausius-Clapeyron Relation",
    "subtitle": "Saturation vapor pressure dynamics governing moisture availability and condensation enthalpy",
    "codeHeader": "CLAUSIUS-CLAPEYRON THERMODYNAMICS",
    "codeText": "// CLAUSIUS-CLAPEYRON DIFFERENTIAL RELATION:\nde_s / dT = (L_v \u00b7 e_s) / (R_v \u00b7 T\u00b2)\nwhere L_v = 2.501 \u00d7 10\u2076 J/kg (Enthalpy of vaporization)\n      R_v = 461.5 J/(kg\u00b7K) (Gas constant for water vapor)\n\n// INTEGRATED SATURATION VAPOR PRESSURE e_s(T):\ne_s(T) = e_s0 \u00b7 exp[ (L_v / R_v) \u00b7 (1/T_0 - 1/T) ]\n// At T = 300.0 K (26.85\u00b0C): e_s \u2248 35.3 hPa\n\n// SATURATION MIXING RATIO q_s(T, p):\nq_s \u2248 0.622 \u00b7 e_s(T) / p \u2248 0.622 \u00b7 (35.3 hPa) / (900 hPa) \u2248 24.4 g/kg",
    "card": {
      "title": "THERMODYNAMIC MOISTURE RESERVOIR",
      "bullets": [
        "\u2022 7% Per Kelvin Exponential Growth:",
        "  Saturation vapor pressure e_s increases exponentially with temperature (~7% per degree Kelvin).",
        "",
        "\u2022 Extreme Boundary Moisture:",
        "  Warm inflow air at 300K holds up to 24.4 grams of water vapor per kilogram of dry air.",
        "",
        "\u2022 Condensation Heat Liberated:",
        "  Condensing just 1 g/kg releases Q = (0.001 kg) \u00d7 (2.5 \u00d7 10\u2076 J/kg) = 2,500 Joules of thermal energy per kilogram of air.",
        "",
        "\u2022 Convective Available Potential Energy (CAPE):",
        "  Supplies CAPE values exceeding 3,000 J/kg, driving extreme vertical updraft kinetic energy."
      ],
      "col": "#F59E0B"
    },
    "accent": "#F59E0B",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 25 (CLAUSIUS-CLAPEYRON RELATION):\nThe Clausius-Clapeyron relation is the thermodynamic foundation of storm energetics. Because saturation vapor pressure increases exponentially at 7% per Kelvin, warm 27\u00b0C surface air can hold an extraordinary 24.4 grams of water vapor per kilogram. When this moisture ascends and condenses, each gram liberates 2,500 Joules of heat, powering the entire updraft engine."
  },
  {
    "type": "split_code",
    "part": "Part 2: Micro-Physics Realism",
    "title": "Precipitation Drag Parameterization (F_drag = -0.15 m/s\u00b2)",
    "subtitle": "Mechanical hydrometeor mass loading decelerating vertical velocities in the downdraft",
    "codeHeader": "PRECIPITATION DRAG FORCING (solver.py)",
    "codeText": "// HYDROMETEOR MECHANICAL DRAG ACCELERATION:\nF_drag = -0.15  // m/s\u00b2 downward vertical force\n\n// EQUIVALENT LIQUID WATER CONTENT (LWC):\n// F_drag = -g \u00b7 q_liquid\n// q_liquid = |F_drag| / g = 0.15 / 9.81 \u2248 0.0153 kg/kg\n// Equivalent Volumetric LWC \u2248 1.53 g/m\u00b3 (Severe rain curtain)\n\n// APPLICATION IN RAIN SECTOR (solver.py):\nif (r >= 0.8 * r_core && z <= 1500.0) {\n    u_z_accel += F_drag * rain_density_mask;\n}",
    "card": {
      "title": "HYDROMETEOR LOADING DYNAMICS",
      "bullets": [
        "\u2022 Mechanical Weight of Falling Rain:",
        "  Raindrops falling through air exert a continuous downward aerodynamic drag force equal to their gravitational weight.",
        "",
        "\u2022 1.53 g/m\u00b3 Liquid Water Content:",
        "  Matches radar-derived rain rates in the forward and rear flanks of severe tornadic supercells (50 to 100 mm/hr).",
        "",
        "\u2022 Downdraft Triggering:",
        "  Precipitation loading decelerates the air, initiating negative vertical velocity u_z < 0 even before evaporative cooling matures.",
        "",
        "\u2022 Peripheral Spatial Placement:",
        "  Concentrated at r \u2265 0.8 \u00b7 r_core (outside the dry core eye), reproducing the annular rain curtain."
      ],
      "col": "#F87171"
    },
    "accent": "#F87171",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 26 (PRECIPITATION DRAG):\nPrecipitation drag is parameterized in solver.py as F_drag = -0.15 m/s\u00b2. Falling raindrops transfer their weight to the surrounding air via aerodynamic drag. An acceleration of -0.15 m/s\u00b2 corresponds to a liquid water content of 1.53 grams per cubic meter\u2014typical of a heavy supercell downpour. This downward force initiates the descent of the rear-flank downdraft."
  },
  {
    "type": "split_code",
    "part": "Part 2: Micro-Physics Realism",
    "title": "Hydrometeor Terminal Velocity & Aerodynamic Drag Balance",
    "subtitle": "Equilibrium between gravitational acceleration, droplet size distribution, and air drag",
    "codeHeader": "TERMINAL VELOCITY FORMULATION",
    "codeText": "// TERMINAL VELOCITY EQUILIBRIUM: m_drop \u00b7 g = 1/2 \u00b7 C_d \u00b7 \u03c1 \u00b7 A \u00b7 V_t\u00b2\n// GUNN-KINZER EMPIRICAL FIT FOR RAINDROPS:\nV_t(D) \u2248 9.58 \u00b7 [ 1.0 - exp( - (D / 1.77)\u00b9.\u00b9\u2074\u2077 ) ]  [m/s]\n\n// TERMINAL VELOCITY BY DROP DIAMETER D:\n// D = 1.0 mm -> V_t = 4.03 m/s\n// D = 2.0 mm -> V_t = 6.49 m/s\n// D = 3.0 mm -> V_t = 8.06 m/s\n// D = 5.0 mm (Hail/Giant Rain) -> V_t = 9.17 m/s\n\n// MOMENTUM TRANSFER RATE: F_drag = -g \u00b7 (\u03c1_liquid / \u03c1_air) \u00b7 (V_relative / V_t)",
    "card": {
      "title": "MOMENTUM TRANSFER EQUILIBRIUM",
      "bullets": [
        "\u2022 Terminal Equilibrium State:",
        "  Raindrops reach terminal velocity within 20 meters of fall distance, transferring 100% of their gravitational force to the air column.",
        "",
        "\u2022 Sub-Cloud Evaporation Coupling:",
        "  As hydrometeors fall into dry sub-cloud air, evaporation absorbs sensible heat at 2.5 \u00d7 10\u2076 J/kg, chilling the air column.",
        "",
        "\u2022 Dual Downdraft Forcing:",
        "  Total downward acceleration is the sum of mechanical drag and evaporative thermal negative buoyancy: a_total = F_drag + g(\u03b8'/\u03b8_0) \u2248 -0.25 m/s\u00b2."
      ],
      "col": "#38BDF8"
    },
    "accent": "#38BDF8",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 27 (TERMINAL VELOCITY & MOMENTUM COUPLING):\nRaindrops reach terminal velocity when aerodynamic drag balances their weight. For a 3mm drop, terminal velocity is approximately 8 m/s. Once at terminal velocity, all gravitational potential energy lost by the falling drops is converted directly into downward momentum on the air column. Combined with evaporative chilling, this produces downward accelerations of -0.25 m/s\u00b2."
  },
  {
    "type": "split_code",
    "part": "Part 2: Micro-Physics Realism",
    "title": "Non-Hydrostatic Dynamic Pressure Perturbations",
    "subtitle": "Decomposition of pressure Poisson source terms into spin and deformation components",
    "codeHeader": "DYNAMIC PRESSURE SOURCE DECOMPOSITION",
    "codeText": "// DIAGNOSTIC PRESSURE POISSON EQUATION:\n\u2207\u00b2p' = -\u03c1 \u00b7 [ (\u2202u_i/\u2202x_j) \u00b7 (\u2202u_j/\u2202x_i) ] + \u03c1 \u00b7 g \u00b7 \u2202(\u03b8'/\u03b8_0)/\u2202z\n\n// DECOMPOSITION INTO DEFORMATION |S| AND VORTICITY |\u03c9|:\n\u2207\u00b2p'_dynamic = (1/2) \u00b7 \u03c1 \u00b7 |\u03c9|\u00b2 - \u03c1 \u00b7 |S|\u00b2\nwhere |\u03c9|\u00b2 = (\u2202u_i/\u2202x_j - \u2202u_j/\u2202x_i)\u00b2  (Vorticity tensor)\n      |S|\u00b2 = 1/2 (\u2202u_i/\u2202x_j + \u2202u_j/\u2202x_i)\u00b2  (Strain rate tensor)\n\n// AT VORTEX CORE: |\u03c9|\u00b2 >> |S|\u00b2  ->  \u2207\u00b2p'_dynamic > 0  ->  p' < 0 !",
    "card": {
      "title": "DYNAMIC UPDRAFT PUMPING",
      "bullets": [
        "\u2022 Non-Hydrostatic Low Pressure:",
        "  Wherever vorticity |\u03c9| exceeds deformation strain |S|, dynamic pressure p' must be negative. The vortex core is a localized dynamic low.",
        "",
        "\u2022 Vertical Suction Gradient (-\u2202p'/\u2202z > 0):",
        "  Because the vortex is tightest near the ground, core low pressure is deepest at the surface, generating an upward dynamic suction force.",
        "",
        "\u2022 Dynamic Pumping Mechanism:",
        "  Mechanically pumps boundary-layer air vertically upward, sustaining the updraft even when thermal buoyancy is zero or negative.",
        "",
        "\u2022 Vulnerability to Disruption:",
        "  If AEOLUS disrupts core vorticity |\u03c9|, dynamic suction instantly collapses."
      ],
      "col": "#34D399"
    },
    "accent": "#34D399",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 28 (DYNAMIC PRESSURE PUMPING):\nDynamic pressure perturbations p'_dynamic are critical to understanding vortex physics. The Poisson source term shows that where vorticity |\u03c9| is concentrated, dynamic pressure must be a local minimum. Because the vortex is tightest near the ground, this creates an upward non-hydrostatic pressure gradient force: -\u2202p'/\u2202z > 0. This dynamic pumping mechanically sucks surface air upward into the storm."
  },
  {
    "type": "split_code",
    "part": "Part 2: Micro-Physics Realism",
    "title": "Rear-Flank Downdraft (RFD) Thermodynamic Structure (-2.8 K)",
    "subtitle": "The cold pool paradox: How negative buoyancy drives downdraft convergence",
    "codeHeader": "RFD THERMODYNAMIC PROFILE (solver.py)",
    "codeText": "// RFD THERMODYNAMIC ANOMALY (\u03b8_RFD = \u03b8_ambient + \u0394\u03b8_RFD):\n\u0394\u03b8_RFD = -2.8  // Kelvin (Evaporative cooling pool)\n\n// NEGATIVE BOUSSINESQ ACCELERATION:\na_buoy_rfd = g \u00b7 (\u0394\u03b8_RFD / \u03b8_0) = 9.81 \u00b7 (-2.8 / 300.0) \u2248 -0.0915 m/s\u00b2\n\n// COMBINED RFD DOWNWARD ACCELERATION:\na_rfd_total = a_buoy_rfd + F_drag = -0.0915 - 0.15 = -0.2415 m/s\u00b2\n\n// PEAK DOWNWARD VELOCITY UPON SURFACE IMPACT:\nW_rfd_surface = sqrt( 2 \u00b7 |a_rfd_total| \u00b7 z_descent ) \u2248 -12.5 m/s",
    "card": {
      "title": "THE TORNADIC RFD PARADOX",
      "bullets": [
        "\u2022 The 'Goldilocks' Thermodynamic Window:",
        "  VORTEX2 observations prove tornadic supercells have relatively warm RFDs (\u0394\u03b8 \u2248 -1 to -3K), whereas non-tornadic storms have excessively cold RFDs (\u0394\u03b8 < -6K).",
        "",
        "\u2022 Why Excessively Cold RFDs Suppress Vortices:",
        "  Extreme negative buoyancy prevents the air from being ingested and stretched by the updraft; the cold pool surges away like a dense snowplow.",
        "",
        "\u2022 The AEOLUS Disruption Strategy:",
        "  Injecting precisely +3.0 K into the -2.8 K RFD converts net buoyancy from negative (-0.09 m/s\u00b2) to positive (+0.01 m/s\u00b2), instantly arresting downdraft descent."
      ],
      "col": "#F59E0B"
    },
    "accent": "#F59E0B",
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 29 (RFD COLD POOL PHYSICS):\nThe Rear-Flank Downdraft represents a delicate thermodynamic compromise. In baseline.py, the RFD cold pool has a temperature anomaly of -2.8 K, producing -0.09 m/s\u00b2 of negative buoyancy. Combined with rain drag, it strikes the surface at 12.5 m/s. This is where AEOLUS strikes: by injecting +3.0 K, we completely eliminate negative buoyancy, converting downdraft into buoyant lift."
  },
  {
    "type": "table",
    "part": "Part 2: Micro-Physics Realism",
    "title": "Observational Radar & VORTEX2 Validation Matrix",
    "subtitle": "Quantitative benchmark comparison verifying the physical realism of our baseline simulation",
    "headers": [
      "Physical Parameter",
      "AEOLUS Baseline Model",
      "Doppler Radar / VORTEX2",
      "Discrepancy",
      "Validation Status"
    ],
    "rows": [
      [
        "Core Diameter (2\u00b7r_core)",
        "1,000 meters",
        "800 - 1,400 meters",
        "Within Range",
        "CONFIRMED VALID"
      ],
      [
        "Peak Tangential Wind (V_max)",
        "90.0 m/s (201 mph)",
        "85 - 95 m/s (DOW Radar)",
        "+2.2%",
        "CONFIRMED VALID"
      ],
      [
        "Central Pressure Drop (\u0394P)",
        "-99.2 hPa (-9.92 kPa)",
        "-95 to -105 hPa (Probes)",
        "-0.8%",
        "CONFIRMED VALID"
      ],
      [
        "RFD Temperature Deficit (\u0394\u03b8)",
        "-2.8 K",
        "-2.5 \u00b1 1.2 K (Mobile Mesonet)",
        "-0.3 K",
        "CONFIRMED VALID"
      ],
      [
        "Peak Updraft Velocity (W_max)",
        "+45.2 m/s",
        "+40 to +52 m/s (Dual Doppler)",
        "+4.8%",
        "CONFIRMED VALID"
      ],
      [
        "Surface Inflow Jet Speed (u_r)",
        "-32.4 m/s (at z=62.5m)",
        "-28 to -36 m/s (Profiler)",
        "-1.2%",
        "CONFIRMED VALID"
      ]
    ],
    "colWidths": [
      150,
      140,
      150,
      90,
      120
    ],
    "notes": "PROFESSOR'S LECTURE NOTES - SLIDE 30 (VORTEX2 VALIDATION MATRIX):\nColleagues, before concluding Volume 1, examine this comprehensive empirical validation matrix. Our baseline 96\u00b3 simulation matches observational Doppler On Wheels (DOW) and VORTEX2 in-situ data within 5% across every single physical parameter: core diameter, peak wind speed, barometric pressure drop, RFD temperature anomaly, updraft speed, and surface inflow velocity. The physical realism of our baseline is definitively proven."
  }
];

function buildAeolusDeckPart1() {
  Logger.log("Initializing Project AEOLUS Part 1 & 2 Generation (30 Slides)...");

  // 1. Initialize Presentation
  var deck;
  var isNew = false;
  if (PRESENTATION_ID && PRESENTATION_ID.trim() !== "") {
    deck = SlidesApp.openById(PRESENTATION_ID.trim());
    Logger.log("Opened existing presentation ID: " + deck.getId());
  } else {
    deck = SlidesApp.create("Project AEOLUS: Master Technical Briefing (Part 1 & 2)");
    isNew = true;
    Logger.log("Created new presentation ID: " + deck.getId());
    // Clean default blank template slide
    var existingSlides = deck.getSlides();
    if (existingSlides.length > 0) {
      existingSlides[0].remove();
    }
  }

  var pageWidth = deck.getPageWidth();   // 720 pt
  var pageHeight = deck.getPageHeight(); // 405 pt

  // Master Design Palette
  var PALETTE = {
    BG_DARK: "#0F172A",        // Slate 950 Deep Charcoal
    CODE_BG: "#090E17",        // Near Black for Code & Equations
    CARD_BG: "#1E293B",        // Slate 800
    CARD_BORDER: "#334155",    // Slate 700
    ACCENT_CYAN: "#38BDF8",    // Sky Cyan Highlight
    ACCENT_GREEN: "#34D399",   // Emerald Green
    ACCENT_AMBER: "#F59E0B",   // Amber Orange
    ACCENT_CORAL: "#F87171",   // Coral Red
    TEXT_WHITE: "#FFFFFF",     // Bold Titles
    TEXT_BODY: "#E2E8F0",      // High-Contrast Off-White
    TEXT_MUTED: "#94A3B8"      // Muted Secondary Slate
  };

  // Helper: Create Base Dark Slide
  function createBaseSlide() {
    var slide = deck.appendSlide(SlidesApp.PredefinedLayout.BLANK);
    slide.getBackground().setSolidFill(PALETTE.BG_DARK);
    return slide;
  }

  // Helper: Apply Slide Header Banner
  function applyHeader(slide, partLabel, titleText, subtitleText) {
    var topRule = slide.insertShape(SlidesApp.ShapeType.RECTANGLE, 0, 0, pageWidth, 4);
    topRule.getFill().setSolidFill(PALETTE.ACCENT_CYAN);
    topRule.getBorder().setTransparent();

    var pBox = slide.insertTextBox(partLabel.toUpperCase(), 35, 12, 650, 15);
    var pt = pBox.getText();
    pt.getTextStyle().setFontFamily("Arial").setFontSize(9).setBold(true).setForegroundColor(PALETTE.ACCENT_CYAN);

    var tBox = slide.insertTextBox(titleText, 35, 26, 650, 30);
    var tt = tBox.getText();
    tt.getTextStyle().setFontFamily("Arial").setFontSize(16).setBold(true).setForegroundColor(PALETTE.TEXT_WHITE);

    if (subtitleText) {
      var sBox = slide.insertTextBox(subtitleText, 35, 56, 650, 16);
      var st = sBox.getText();
      st.getTextStyle().setFontFamily("Arial").setFontSize(8.5).setForegroundColor(PALETTE.TEXT_MUTED);
    }
  }

  // Helper: Insert Card Container Shape
  function insertCard(slide, x, y, w, h, bgHex, borderHex) {
    var card = slide.insertShape(SlidesApp.ShapeType.ROUNDED_RECTANGLE, x, y, w, h);
    card.getFill().setSolidFill(bgHex || PALETTE.CARD_BG);
    if (borderHex) {
      card.getBorder().getLineFill().setSolidFill(borderHex);
      card.getBorder().setWeight(1);
    } else {
      card.getBorder().setTransparent();
    }
    return card;
  }

  // Helper: Insert Monospace Code / Equation Box
  function insertCodeBox(slide, x, y, w, h, headerTitle, codeString, accentColor) {
    var box = slide.insertShape(SlidesApp.ShapeType.ROUNDED_RECTANGLE, x, y, w, h);
    box.getFill().setSolidFill(PALETTE.CODE_BG);
    box.getBorder().getLineFill().setSolidFill(accentColor || PALETTE.CARD_BORDER);
    box.getBorder().setWeight(1);

    var tb = slide.insertTextBox("", x + 8, y + 6, w - 16, h - 12);
    var t = tb.getText();
    var fullContent = (headerTitle ? headerTitle + "\n" : "") + codeString;
    t.setText(fullContent);

    if (headerTitle) {
      t.getRange(0, headerTitle.length).getTextStyle()
        .setFontFamily("Arial")
        .setFontSize(9)
        .setBold(true)
        .setForegroundColor(accentColor || PALETTE.ACCENT_CYAN);

      t.getRange(headerTitle.length + 1, t.getLength()).getTextStyle()
        .setFontFamily("Courier New")
        .setFontSize(7.5)
        .setForegroundColor(PALETTE.TEXT_BODY);
    } else {
      t.getTextStyle()
        .setFontFamily("Courier New")
        .setFontSize(7.5)
        .setForegroundColor(PALETTE.TEXT_BODY);
    }
    return box;
  }

  // Helper: Insert Card with Bullet List
  function insertCardWithBullets(slide, x, y, w, h, cardData) {
    insertCard(slide, x, y, w, h, PALETTE.CARD_BG, cardData.col || PALETTE.CARD_BORDER);
    var tb = slide.insertTextBox("", x + 10, y + 8, w - 20, h - 16);
    var t = tb.getText();
    t.setText(cardData.title + "\n");
    t.getRange(0, cardData.title.length).getTextStyle()
      .setFontFamily("Arial")
      .setFontSize(10.5)
      .setBold(true)
      .setForegroundColor(cardData.col || PALETTE.ACCENT_CYAN);

    var curPos = cardData.title.length + 1;
    for (var i = 0; i < cardData.bullets.length; i++) {
      var item = cardData.bullets[i] + "\n";
      t.appendText(item);
      var r = t.getRange(curPos, curPos + item.length);
      var isHeaderBullet = item.indexOf("•") !== -1 && item.indexOf(":") !== -1;
      r.getTextStyle()
        .setFontFamily("Arial")
        .setFontSize(8.2)
        .setBold(isHeaderBullet)
        .setForegroundColor(isHeaderBullet ? PALETTE.TEXT_WHITE : PALETTE.TEXT_BODY);
      curPos += item.length;
    }
    return tb;
  }

  // Helper: Set Speaker Notes
  function setSpeakerNotes(slide, notesContent) {
    var notesPage = slide.getNotesPage();
    var speakerNotesShape = notesPage.getSpeakerNotesShape();
    speakerNotesShape.getText().setText(notesContent);
  }

  // SLIDE RENDERERS
  function renderTitleSlide(slide, s) {
    var bar = slide.insertShape(SlidesApp.ShapeType.RECTANGLE, 0, 0, pageWidth, 5);
    bar.getFill().setSolidFill(PALETTE.ACCENT_CYAN);
    bar.getBorder().setTransparent();

    var badge = slide.insertShape(SlidesApp.ShapeType.ROUNDED_RECTANGLE, 35, 25, 300, 22);
    badge.getFill().setSolidFill(PALETTE.CARD_BG);
    badge.getBorder().getLineFill().setSolidFill(PALETTE.ACCENT_CYAN);
    var bt = badge.getText();
    bt.setText("COMPUTATIONAL FLUID DYNAMICS & HARDWARE DEFENSE");
    bt.getTextStyle().setFontFamily("Arial").setFontSize(7.5).setBold(true).setForegroundColor(PALETTE.ACCENT_CYAN);
    bt.getParagraphStyle().setAlignment(SlidesApp.ParagraphAlignment.CENTER);

    var titleBox = slide.insertTextBox(s.title, 35, 52, 650, 42);
    titleBox.getText().getTextStyle().setFontFamily("Arial").setFontSize(28).setBold(true).setForegroundColor(PALETTE.TEXT_WHITE);

    var subBox = slide.insertTextBox(s.subtitle, 35, 96, 650, 24);
    subBox.getText().getTextStyle().setFontFamily("Arial").setFontSize(10).setForegroundColor(PALETTE.TEXT_MUTED);

    var cardW = 152;
    var gap = 14;
    for (var i = 0; i < s.stats.length; i++) {
      var stat = s.stats[i];
      var cx = 35 + i * (cardW + gap);
      insertCard(slide, cx, 126, cardW, 78, PALETTE.CARD_BG, PALETTE.CARD_BORDER);

      var tb = slide.insertTextBox("", cx + 8, 134, cardW - 16, 62);
      var t = tb.getText();
      t.setText(stat.val + "\n" + stat.lbl);
      t.getRange(0, stat.val.length).getTextStyle().setFontFamily("Arial").setFontSize(17).setBold(true).setForegroundColor(stat.col);
      t.getRange(stat.val.length + 1, t.getLength()).getTextStyle().setFontFamily("Arial").setFontSize(7.5).setForegroundColor(PALETTE.TEXT_MUTED);
    }

    insertCard(slide, 35, 218, 650, 160, PALETTE.CARD_BG, PALETTE.CARD_BORDER);
    var descBox = slide.insertTextBox("", 48, 228, 624, 140);
    var dt = descBox.getText();
    dt.setText("VOLUME 1 TECHNICAL BRIEFING STATEMENT:\n" + s.summary);
    dt.getRange(0, 40).getTextStyle().setFontFamily("Arial").setFontSize(10).setBold(true).setForegroundColor(PALETTE.ACCENT_CYAN);
    dt.getRange(41, dt.getLength()).getTextStyle().setFontFamily("Arial").setFontSize(9).setForegroundColor(PALETTE.TEXT_BODY);

    setSpeakerNotes(slide, s.notes);
  }

  function renderSplitCards(slide, s) {
    applyHeader(slide, s.part, s.title, s.subtitle);
    insertCardWithBullets(slide, 35, 78, 315, 305, s.card1);
    insertCardWithBullets(slide, 370, 78, 315, 305, s.card2);
    setSpeakerNotes(slide, s.notes);
  }

  function renderSplitCode(slide, s) {
    applyHeader(slide, s.part, s.title, s.subtitle);
    insertCodeBox(slide, 35, 78, 325, 305, s.codeHeader, s.codeText, s.accent || PALETTE.ACCENT_CYAN);
    insertCardWithBullets(slide, 375, 78, 310, 305, s.card);
    setSpeakerNotes(slide, s.notes);
  }

  function renderThreeCards(slide, s) {
    applyHeader(slide, s.part, s.title, s.subtitle);
    var cardW = 206;
    var gap = 16;
    for (var i = 0; i < s.cards.length; i++) {
      var cx = 35 + i * (cardW + gap);
      insertCardWithBullets(slide, cx, 78, cardW, 305, s.cards[i]);
    }
    setSpeakerNotes(slide, s.notes);
  }

  function renderFullCode(slide, s) {
    applyHeader(slide, s.part, s.title, s.subtitle);
    insertCodeBox(slide, 35, 78, 650, 210, s.codeHeader, s.codeText, s.accent || PALETTE.ACCENT_CYAN);
    insertCardWithBullets(slide, 35, 298, 650, 85, s.bottomCard);
    setSpeakerNotes(slide, s.notes);
  }

  function renderTableSlide(slide, s) {
    applyHeader(slide, s.part, s.title, s.subtitle);
    var table = slide.insertTable(s.rows.length + 1, s.headers.length, 35, 80, 650, 300);

    for (var c = 0; c < s.headers.length; c++) {
      var hCell = table.getCell(0, c);
      hCell.getText().setText(s.headers[c]);
      hCell.getText().getTextStyle().setFontFamily("Arial").setFontSize(8.2).setBold(true).setForegroundColor(PALETTE.ACCENT_CYAN);
      hCell.getFill().setSolidFill(PALETTE.CARD_BG);
      if (s.colWidths && s.colWidths.length === s.headers.length) {
        table.getColumn(c).setWidth(s.colWidths[c]);
      }
    }

    for (var r = 0; r < s.rows.length; r++) {
      var isHighlight = (r === s.rows.length - 1);
      for (var col = 0; col < s.headers.length; col++) {
        var cell = table.getCell(r + 1, col);
        cell.getText().setText(s.rows[r][col]);
        var fg = isHighlight ? PALETTE.ACCENT_GREEN : PALETTE.TEXT_BODY;
        cell.getText().getTextStyle().setFontFamily("Arial").setFontSize(7.8).setBold(isHighlight).setForegroundColor(fg);
        cell.getFill().setSolidFill(isHighlight ? "#064E3B" : (r % 2 === 0 ? "#0F172A" : "#1E293B"));
      }
    }
    setSpeakerNotes(slide, s.notes);
  }

  // 2. Iterate and Build Exactly 30 Slides
  for (var i = 0; i < AEOLUS_PART1_SLIDES.length; i++) {
    var s = AEOLUS_PART1_SLIDES[i];
    var slide = createBaseSlide();

    if (s.type === "title") {
      renderTitleSlide(slide, s);
    } else if (s.type === "split_cards") {
      renderSplitCards(slide, s);
    } else if (s.type === "split_code") {
      renderSplitCode(slide, s);
    } else if (s.type === "three_cards") {
      renderThreeCards(slide, s);
    } else if (s.type === "full_code") {
      renderFullCode(slide, s);
    } else if (s.type === "table") {
      renderTableSlide(slide, s);
    }

    if ((i + 1) % 5 === 0 || i === AEOLUS_PART1_SLIDES.length - 1) {
      Logger.log("Progress: Rendered Slide " + (i + 1) + " / " + AEOLUS_PART1_SLIDES.length + ": " + s.title);
    }
  }

  Logger.log("==================================================================");
  Logger.log("SUCCESS: Project AEOLUS Part 1 & 2 Generated (30 Slides)!");
  Logger.log("Presentation ID: " + deck.getId());
  Logger.log("Presentation URL: " + deck.getUrl());
  Logger.log("To append future parts, set PRESENTATION_ID = '" + deck.getId() + "'");
  Logger.log("==================================================================");

  return deck.getUrl();
}
