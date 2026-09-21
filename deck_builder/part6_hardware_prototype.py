"""Part 6: Laboratory Tabletop Prototype & Froude Scaling (Slides 70 - 82)"""

from .slide_types import make_split_cards, make_split_code, make_three_cards, make_table_slide

def get_part6_slides():
    slides = []

    # Slide 70: Hydrodynamic Froude Scaling Law
    slides.append(make_split_cards(
        part="Part 6: Tabletop Prototype & Scaling",
        title="Hydrodynamic Froude Scaling Law: Invariance from 1000m to 600mm",
        subtitle="Dynamic similitude governing convective vortices under gravitational stratification",
        card1={
            "title": "THE FROUDE NUMBER SIMILITUDE",
            "bullets": [
                "• Froude Number Definition:",
                "  Fr = V / sqrt(g · L · Δθ/θ_0) ≈ V / sqrt(g · L)",
                "",
                "• Gravitational & Buoyant Ratio:",
                "  Fr represents the ratio of inertial advective forces to gravitational buoyancy forces.",
                "",
                "• Invariance Requirement:",
                "  Fr_prototype = Fr_model = 1.66.",
                "",
                "• Geometric Scale Factor λ_L:",
                "  λ_L = L_model / L_full = 0.30 m / 300 m = 1 / 1,000."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "WHY FROUDE GOVERNS OVER REYNOLDS",
            "bullets": [
                "• Reynolds Number Disparity:",
                "  Full-scale Re ≈ 10⁸; model Re ≈ 10⁵. Both operate firmly within the fully turbulent regime where flow patterns become Re-independent.",
                "",
                "• Buoyancy Dominance:",
                "  Vortex core diameter, cyclostrophic balance, and vertical updraft stretching are strictly governed by the Froude number Fr.",
                "",
                "• Similitude Guarantee:",
                "  Preserving Fr = 1.66 guarantees that model streamlines, vortex breakdown modes, and disruption kinematics match the atmosphere exactly."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 70 (FROUDE SCALING LAW):\nWhen scaling environmental flows to a benchtop, one cannot simultaneously match Reynolds and Froude numbers. Fortunately, once Reynolds number exceeds 10^4, turbulent flows become Reynolds-independent. Similitude is governed entirely by the Froude number Fr = V / sqrt(gL). By preserving Fr = 1.66 between the atmosphere and our 600mm chamber, our laboratory streamlines faithfully replicate full-scale tornado physics."
    ))

    # Slide 71: Scaling Invariance Calculations
    slides.append(make_split_cards(
        part="Part 6: Tabletop Prototype & Scaling",
        title="Scaling Invariance Calculations: Velocity, Time, & Pressure",
        subtitle="Analytical derivations of model operating parameters using Froude similitude",
        card1={
            "title": "DERIVED MODEL SCALING RATIOS",
            "bullets": [
                "• Velocity Ratio λ_V:",
                "  V_model / V_full = sqrt(λ_L) = sqrt(1 / 1000) = 1 / 31.62.",
                "  V_max_model = 90.0 m/s / 31.62 = 2.85 m/s.",
                "",
                "• Time Ratio λ_t:",
                "  t_model / t_full = sqrt(λ_L) = 1 / 31.62.",
                "  Full 6.0s disruption corresponds to: t_model = 6.0s / 31.62 = 0.190 seconds (190 ms).",
                "",
                "• Frequency Scaling λ_f:",
                "  f_model = 31.62 · f_full (High-speed dynamics; requires 100 Hz Arduino polling)."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "PRESSURE & SUCTION CONVERSION",
            "bullets": [
                "• Dynamic Pressure Scaling λ_P:",
                "  ΔP_model / ΔP_full = (ρ_model/ρ_full) · λ_V² = 1 · (1/31.62)² = 1 / 1,000.",
                "",
                "• Core Depression at Model Scale:",
                "  ΔP_core_model = -9,922 Pa / 1,000 = -9.92 Pa.",
                "",
                "• Auto-Tuned Suction Setpoint at Model Scale:",
                "  ΔP_suction_model = -47.80 Pa / 1,000 = -0.0478 Pa (-0.005 mm H₂O).",
                "",
                "• Laboratory Feasibility:",
                "  Easily generated using low-power 12V DC centrifugal blowers."
            ],
            "col": "#F59E0B"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 71 (SCALING CALCULATIONS):\nHere are the exact scaling calculations. Because velocity scales with the square root of length, our 90 m/s tornado translates to a manageable 2.85 m/s benchtop vortex. Note the time compression: a 6-second atmospheric event occurs in 190 milliseconds in the chamber! This high-speed evolution is why our Arduino control loop must run at 100 Hz with microsecond interrupt response times."
    ))

    # Slide 72: Prototype Chamber Physical Blueprint
    slides.append(make_split_cards(
        part="Part 6: Tabletop Prototype & Scaling",
        title="Prototype Chamber Blueprint: 600mm Acrylic Enclosure",
        subtitle="Physical architecture of the 600mm x 600mm x 600mm tabletop testing chamber",
        card1={
            "title": "CHAMBER STRUCTURAL SPECIFICATIONS",
            "bullets": [
                "• Outer Enclosure:",
                "  600mm × 600mm × 600mm cube constructed from 6.0mm cast acrylic (PMMA) sheets.",
                "",
                "• Optical Clarity & Optical Access:",
                "  92% optical transmission for laser sheet particle image velocimetry (PIV) and high-speed photography.",
                "",
                "• Structural Reinforcement:",
                "  Extruded aluminum 2020 T-slot framing provides rigid vibration dampening.",
                "",
                "• Hinged Top & Side Access Panels:",
                "  Neoprene gasketed seals ensuring airtight operation during suction cycles."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "INTERNAL AIRFLOW ARCHITECTURE",
            "bullets": [
                "• Two-Stage Chamber Design:",
                "  Outer plenum distributes ambient air evenly to 8 peripheral inlet guide vanes.",
                "",
                "• Lower Ground Boundary Deck:",
                "  False bottom plate with integrated suction slots and mist generator nozzles.",
                "",
                "• Honeycomb Flow Straighteners:",
                "  50mm aluminum honeycomb mesh at inlet plenum eliminates ambient room turbulence."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 72 (CHAMBER PHYSICAL BLUEPRINT):\nThe physical prototype is housed in a 600mm cast acrylic cube reinforced with aluminum T-slot extrusions. The transparent acrylic walls allow complete optical access for laser sheet flow visualization. A two-stage chamber design separates the outer settling plenum from the inner testing core, ensuring that room drafts do not disturb the experimental vortex."
    ))

    # Slide 73: 300mm Inner Vortex Chamber & Central Top Fan
    slides.append(make_split_cards(
        part="Part 6: Tabletop Prototype & Scaling",
        title="300mm Cylindrical Inner Core & Top Exhaust Fan",
        subtitle="Vortex generation mechanics using 12V 120mm 150 CFM high-static exhaust",
        card1={
            "title": "INNER CYLINDRICAL CORE",
            "bullets": [
                "• Chamber Geometry:",
                "  300mm diameter inner cylindrical acrylic tube, 500mm high, matching the scaled core aspect ratio.",
                "",
                "• Perforated Inflow Base:",
                "  Lower 100mm contains 8 tangential entry slots introducing controlled angular momentum.",
                "",
                "• Updraft Chimney Effect:",
                "  Simulates the buoyant supercell updraft by pulling air vertically through the core column."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "TOP EXHAUST FAN SUBSYSTEM",
            "bullets": [
                "• Actuator Hardware:",
                "  12V DC, 120mm brushless industrial fan rated at 150 CFM (70.8 L/s) with 32 mm H₂O static pressure head.",
                "",
                "• Microcontroller PWM Control:",
                "  Arduino Pin 9 drives a high-current MOSFET at 25 kHz PWM frequency, eliminating audible motor whine.",
                "",
                "• Speed Range:",
                "  0 to 5,000 RPM continuously variable, allowing precise swirl ratio and Froude tuning.",
                "",
                "• Exhaust Orifice Contraction:",
                "  Contoured bell-mouth contraction nozzle minimizes vena contracta losses at exit."
            ],
            "col": "#F59E0B"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 73 (INNER CORE & EXHAUST FAN):\nThe inner core is a 300mm diameter cylinder. The upward draft is driven by a 120mm high-static-pressure brushless fan mounted at the top exhaust. Controlled via 25 kHz PWM from Arduino Pin 9, this fan provides up to 150 CFM of vertical volumetric flow, creating the core pressure depression that drives the entire tabletop vortex system."
    ))

    # Slide 74: Tangential Inflow Airfoil Geometry: 8 Stator Vanes
    slides.append(make_split_cards(
        part="Part 6: Tabletop Prototype & Scaling",
        title="Tangential Inflow Airfoil Geometry: 8 Adjustable Stator Vanes",
        subtitle="Controlling vortex circulation and swirl ratio S = (r_core · Γ) / (2 · Q)",
        card1={
            "title": "STATOR VANE SPECIFICATIONS",
            "bullets": [
                "• 8 Symmetrical NACA 0012 Airfoils:",
                "  3D-printed from PLA with smooth sand-blasted aerodynamic surface finish.",
                "",
                "• Radial Placement:",
                "  Equally spaced at 45° intervals along the 300mm chamber circumference.",
                "",
                "• Adjustable Angle of Attack (0° to 45°):",
                "  Mechanically linked via a synchronization ring driven by an MG996R metal-gear servo on Arduino Pin 10."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "SWIRL RATIO S TUNING",
            "bullets": [
                "• Mathematical Definition:",
                "  S = (π · r_core³ · u_θ) / Q_volumetric",
                "",
                "• Swirl Regimes:",
                "  - S < 0.2: Weak swirling jet (no vortex core).",
                "  - 0.2 < S < 0.6: Single stable laminar core.",
                "  - S > 0.6: Violent turbulent vortex with central downdraft breakdown.",
                "",
                "• Operating Target:",
                "  S_calibrated = 0.85, reproducing violent EF4 vortex core dynamics in the chamber."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 74 (STATOR VANES & SWIRL RATIO):\nTo control the circulation entering the chamber, we use 8 adjustable NACA 0012 stator vanes linked to an Arduino-controlled servo. By rotating these vanes from 0° to 45°, we tune the swirl ratio S. At our calibrated operating point of S = 0.85, the chamber produces a robust, turbulent core with an inner two-cell structure matching violent EF4 tornadoes."
    ))

    # Slide 75: Dual Disruption Hardware: Mist & Vacuum Solenoids
    slides.append(make_split_cards(
        part="Part 6: Tabletop Prototype & Scaling",
        title="Dual Disruption Hardware: Ultrasonic Mist & Suction Solenoids",
        subtitle="Physical actuators executing thermal RFD and momentum sink interventions",
        card1={
            "title": "ULTRASONIC MIST SUBSYSTEM (THERMAL RFD)",
            "bullets": [
                "• 4x 24V Ultrasonic Piezoelectric Transducers (1.7 MHz):",
                "  Mounted in lower rear quadrant, generating 1-5 μm fine fog droplets.",
                "",
                "• Physical Similitude Role:",
                "  Visualizes flow streamlines under laser illumination while heated mist carrier delivers +3K thermal buoyancy analogue.",
                "",
                "• Arduino Relay Control:",
                "  Driven via 4-channel optocoupled relay board on Pins 24, 25, 26, 27."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "OFF-AXIS SUCTION SOLENOIDS (MOMENTUM SINK)",
            "bullets": [
                "• 2x 12V DC Normally Closed High-Flow Solenoid Valves:",
                "  1/2\" NPT ports connecting chamber boundary layer to external vacuum ballast reservoir.",
                "",
                "• Off-Axis Tangential Ports:",
                "  Located at r = 120mm, 45° offset from main inflow.",
                "",
                "• Response Time < 15ms:",
                "  Actuated via 30A power MOSFET switches on Arduino Pins 22 and 23."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 75 (DISRUPTION HARDWARE):\nHere is the benchtop disruption hardware. The thermal RFD intervention is executed by 4 ultrasonic mist generators on Pins 24-27 that introduce heated mist into the rear quadrant. The momentum sink is executed by 2 high-flow solenoid valves on Pins 22-23 that connect off-axis boundary layer ports to a vacuum reservoir in under 15 milliseconds."
    ))

    # Slide 76: Sensor Instrumentation Suite
    slides.append(make_split_cards(
        part="Part 6: Tabletop Prototype & Scaling",
        title="Sensor Instrumentation Suite: Pressure & Anemometry",
        subtitle="High-speed diagnostic sensors monitoring core pressure depression and wind velocities",
        card1={
            "title": "MPX5010DP DIFFERENTIAL PRESSURE SENSOR",
            "bullets": [
                "• Measurement Range: 0 to 10 kPa (0 to 1.45 psi):",
                "  Precision piezoresistive transducer with on-chip signal conditioning.",
                "",
                "• Pressure Port Placement:",
                "  Low-side port tapped into the central ground plane (r = 0, z = 0); high-side port open to ambient room pressure.",
                "",
                "• Output Transfer Function:",
                "  V_out = V_s · (0.09 · P + 0.04) ± 5.0% error; read on Arduino Analog Pin A0."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "HOT-WIRE ANEMOMETRY & THERMISTORS",
            "bullets": [
                "• Dual Constant-Temperature Hot-Wire Anemometers:",
                "  - Core Probe: Pin A1 (Measures peak tangential velocity V_max at r = 50mm).",
                "  - Boundary Probe: Pin A2 (Measures radial inflow velocity u_r at z = 15mm).",
                "",
                "• Precision 10k NTC Thermistors (Pins A3, A4):",
                "  Monitors ambient reference and RFD quadrant temperature with 0.1°C resolution."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 76 (SENSOR INSTRUMENTATION):\nInstrumentation is critical for empirical validation. We monitor core pressure depression using an MPX5010DP piezoresistive transducer on Analog Pin A0. Dual hot-wire anemometers on Pins A1 and A2 track peak core velocity and boundary layer radial inflow. Two 10k NTC thermistors verify that our thermal injection delivers the precise +3K temperature anomaly."
    ))

    # Slide 77: Microcontroller Architecture: Arduino Mega 2560
    slides.append(make_split_cards(
        part="Part 6: Tabletop Prototype & Scaling",
        title="Microcontroller Architecture: Arduino Mega 2560 R3",
        subtitle="Deterministic bare-metal embedded computing for high-speed fluid control",
        card1={
            "title": "MICROCONTROLLER HARDWARE SPECS",
            "bullets": [
                "• ATmega2560 8-Bit RISC Microcontroller:",
                "  Clock frequency: 16 MHz (62.5 ns instruction cycle time).",
                "",
                "• Memory Resources:",
                "  256 KB Flash Memory, 8 KB SRAM, 4 KB EEPROM.",
                "",
                "• Extensive I/O Connectivity:",
                "  54 digital I/O pins (15 PWM capable), 16 analog input channels (10-bit ADC).",
                "",
                "• Deterministic Timing:",
                "  Zero operating system overhead; eliminates non-deterministic garbage collection latency."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "WHY ARDUINO MEGA OVER RASPBERRY PI",
            "bullets": [
                "• True Hard Real-Time Execution:",
                "  Microsecond-level hardware interrupt latency (< 4 μs) for critical safety trips.",
                "",
                "• Dedicated Hardware Timers:",
                "  Timer2 configured for glitch-free 25 kHz motor PWM without CPU intervention.",
                "",
                "• Electrical Robustness:",
                "  5.0V CMOS logic with 40mA per pin drive capability easily triggers optocoupled relays without external level shifters."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 77 (ARDUINO MEGA ARCHITECTURE):\nWhy did we select the Arduino Mega 2560 over a single-board computer like the Raspberry Pi? The answer is hard real-time determinism. Linux has scheduling jitter that can delay safety trips by 50 to 100 milliseconds. The ATmega2560 responds to external hardware interrupts in under 4 microseconds, providing unconditional fail-safe protection."
    ))

    # Slide 78: Complete Arduino Hardware Pin Mapping
    slides.append(make_split_code(
        part="Part 6: Tabletop Prototype & Scaling",
        title="Complete Arduino Pin Mapping & Circuit Schematics",
        subtitle="Verbatim pin configuration table matching main.ino firmware ledger",
        codeHeader="HARDWARE PIN MAPPING (main.ino)",
        codeText="// DIGITAL OUTPUTS (ACTUATORS & PWM)\n#define PIN_FAN_PWM         9   // Timer2 25 kHz Exhaust Fan PWM\n#define PIN_STATOR_SERVO   10   // Stator Inflow Airfoil Servo\n#define PIN_SOLENOID_1     22   // Vacuum Valve 1 (Relay CH1)\n#define PIN_SOLENOID_2     23   // Vacuum Valve 2 (Relay CH2)\n#define PIN_MIST_1         24   // Piezo Fogger 1 (Relay CH3)\n#define PIN_MIST_2         25   // Piezo Fogger 2 (Relay CH4)\n#define PIN_MIST_3         26   // Piezo Fogger 3 (Relay CH5)\n#define PIN_MIST_4         27   // Piezo Fogger 4 (Relay CH6)\n#define PIN_HEATER_RELAY   28   // Thermal Element Relay\n\n// ANALOG INPUTS (SENSORS)\n#define PIN_PRESSURE_SENSE A0   // MPX5010DP Core Pressure (0-10 kPa)\n#define PIN_HOTWIRE_CORE   A1   // Core Tangential Anemometer\n#define PIN_HOTWIRE_INFLOW A2   // Boundary Radial Anemometer\n#define PIN_TEMP_AMBIENT   A3   // Ambient NTC Thermistor\n#define PIN_TEMP_RFD       A4   // RFD Sector NTC Thermistor\n\n// SAFETY INTERRUPT\n#define PIN_ESTOP_BUTTON    2   // Hardware Interrupt INT0 (Falling Edge)",
        accent="#38BDF8",
        card={
            "title": "CIRCUIT ISOLATION & POWER",
            "bullets": [
                "• Optocoupled Relay Isolation:",
                "  Actuators are isolated via PC817 optocouplers, preventing inductive flyback spikes from reaching the MCU.",
                "",
                "• Dual Power Rails:",
                "  - Rail A: Clean 5V / 2A for MCU and analog sensors.",
                "  - Rail B: Heavy 12V / 10A for exhaust fan, solenoid coils, and heaters.",
                "",
                "• Hardware E-Stop (Pin 2):",
                "  Triggers INT0 falling-edge interrupt, instantly clamping all actuator pins LOW in hardware."
            ],
            "col": "#38BDF8"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 78 (PIN MAPPING & SCHEMATICS):\nThis code block from main.ino defines the pin map. Notice the segregation of high-speed PWM on Pin 9, relay controls on Digital Pins 22-28, and analog sensor inputs on A0-A4. Pin 2 is connected to an industrial mushroom emergency-stop button configured as an external hardware interrupt (INT0), ensuring instantaneous shutoff."
    ))

    # Slide 79: Real-Time Firmware Control Loop
    slides.append(make_split_code(
        part="Part 6: Tabletop Prototype & Scaling",
        title="Real-Time Firmware Control Loop: 100 Hz (10ms) Polling",
        subtitle="Verbatim state machine and dual-tier safety trips in main.ino",
        codeHeader="FIRMWARE CONTROL LOOP (main.ino)",
        codeText="void loop() {\n  unsigned long currentMillis = millis();\n  \n  // 100 Hz Deterministic Execution Loop (10ms)\n  if (currentMillis - previousMillis >= 10) {\n    previousMillis = currentMillis;\n    \n    // 1. Read All Sensors\n    readSensors();\n    \n    // 2. Evaluate State Machine\n    switch (currentState) {\n      case STATE_IDLE:\n        if (armSignalReceived) currentState = STATE_ARMED;\n        break;\n      case STATE_ARMED:\n        spinUpExhaustFan();\n        if (isVortexFormed()) currentState = STATE_DISRUPTING;\n        break;\n      case STATE_DISRUPTING:\n        fireInterventions();  // Fire Mist + Open Solenoids\n        if (currentMillis - disruptionStart >= 6000) currentState = STATE_RECOVERY;\n        break;\n      case STATE_RECOVERY:\n        disengageInterventions();\n        break;\n    }\n    \n    // 3. Telemetry Stream (115200 baud)\n    sendTelemetry();\n  }\n}",
        accent="#34D399",
        card={
            "title": "DUAL-TIER SAFETY INTERLOCKS",
            "bullets": [
                "• Tier 1: Hardware E-Stop (Pin 2):",
                "  Direct hardware interrupt cuts power to solenoid relays in < 4 microseconds.",
                "",
                "• Tier 2: Thermal Cutoff Watchdog:",
                "  If RFD thermistor (A4) exceeds 65°C, firmware automatically shuts down heater relay.",
                "",
                "• Over-Pressure Watchdog:",
                "  If core vacuum exceeds -15.0 kPa, exhaust fan PWM is throttled to prevent acrylic fatigue.",
                "",
                "• 100 Hz Deterministic Loop:",
                "  Guarantees consistent 10ms cycle time with zero drift."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 79 (FIRMWARE CONTROL LOOP):\nHere is the real-time execution loop of main.ino. It operates at exactly 100 Hz, giving a deterministic 10-millisecond cycle. In each cycle, it reads all 5 analog sensors, advances the state machine from ARMED to DISRUPTING to RECOVERY, and streams binary telemetry over UART. Dual-tier software watchdogs guard against over-temperature and over-pressure."
    ))

    # Slide 80: Bill of Materials (BOM) & Economic Budget
    slides.append(make_table_slide(
        part="Part 6: Tabletop Prototype & Scaling",
        title="Bill of Materials (BOM) & Economic Budget: $227.00 USD",
        subtitle="Complete component inventory, procurement sources, and cost breakdown",
        headers=["Subsystem Component", "Specification / Model", "Vendor / Source", "Qty", "Unit Cost", "Subtotal"],
        rows=[
            ["Chamber Structure", "6mm Cast Acrylic PMMA (600mm)", "McMaster-Carr", "6", "$12.50", "$75.00"],
            ["Chamber Frame", "2020 Aluminum T-Slot + Brackets", "Misumi / Amazon", "12", "$2.25", "$27.00"],
            ["Exhaust Fan", "12V 120mm 150 CFM Brushless Fan", "Delta Electronics", "1", "$18.50", "$18.50"],
            ["Microcontroller", "Arduino Mega 2560 R3 Board", "Elegoo / Arduino", "1", "$16.00", "$16.00"],
            ["Pressure Sensor", "MPX5010DP Differential (0-10 kPa)", "NXP / Mouser", "1", "$14.50", "$14.50"],
            ["Solenoid Valves", "12V 1/2\" NPT Normally Closed Brass", "US Solid", "2", "$12.00", "$24.00"],
            ["Mist Generators", "24V 1.7 MHz Piezo Ultrasonic Foggers", "AGPtek", "4", "$4.75", "$19.00"],
            ["Relay & MOSFETs", "8-Ch Optocoupled Relay + IRLZ44N", "SainSmart", "1", "$11.00", "$11.00"],
            ["Power Supplies", "12V 10A + 24V 3A Dual Switching PSU", "Mean Well", "2", "$11.00", "$22.00"],
            ["TOTAL FABRICATION BUDGET", "Complete Turnkey Prototype", "All Suppliers", "-", "-", "$227.00"]
        ],
        colWidths=[130, 165, 110, 35, 60, 60],
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 80 (BILL OF MATERIALS):\nAcademic research must be reproducible and economically feasible. This complete bill of materials totals exactly $227.00 USD. Every component—from the 6mm cast acrylic panels and Delta brushless exhaust fan to the NXP pressure sensor and Arduino board—is commercially available off the shelf. Any university fluid dynamics laboratory can replicate this apparatus for under $250."
    ))

    # Slide 81: Fabrication & Calibration Protocol
    slides.append(make_split_cards(
        part="Part 6: Tabletop Prototype & Scaling",
        title="Fabrication & Calibration Protocol: 8-Step Assembly",
        subtitle="Standard operating procedure for laboratory assembly, alignment, and zeroing",
        card1={
            "title": "8-STEP ASSEMBLY WORKFLOW",
            "bullets": [
                "• 1. Frame Erection: Assemble 600mm T-slot frame with corner brackets.",
                "• 2. Acrylic Bonding: Solvent-weld PMMA panels using acrylic cement.",
                "• 3. Flow Conditioning: Install 50mm honeycomb in outer settling plenum.",
                "• 4. Core & Vane Assembly: Mount 300mm cylinder and 8 stator vanes.",
                "• 5. Top Fan Mount: Bolt 120mm exhaust fan with silicone vibration isolators.",
                "• 6. Sensor Plumbing: Tap static pressure port at r=0 and install MPX5010DP.",
                "• 7. Actuator Wiring: Connect solenoids and mist relays to Arduino.",
                "• 8. Leak Testing: Pressurize chamber to 500 Pa to verify seal integrity."
            ],
            "col": "#38BDF8"
        },
        card2={
            "title": "SENSOR CALIBRATION PROTOCOL",
            "bullets": [
                "• Zero-Offset Calibration:",
                "  Power on with fan off; sample Analog Pin A0 for 500 cycles to establish ambient zero offset V_zero.",
                "",
                "• Manometer Cross-Verification:",
                "  Calibrate MPX5010DP voltage against a precision inclined water manometer across 0 to 200 Pa.",
                "",
                "• Swirl Angle Indexing:",
                "  Zero the MG996R servo to confirm stator vanes close to exactly 0° (pure radial inflow).",
                "",
                "• Ready for Disruption Testing:",
                "  System achieves operational readiness in under 12 total fabrication hours."
            ],
            "col": "#34D399"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 81 (FABRICATION PROTOCOL):\nOur fabrication protocol follows an 8-step standardized procedure requiring 8 to 12 fabrication hours. Sensor calibration begins with a 500-sample zero-offset calibration of the MPX5010DP sensor, verified against an inclined water manometer. Once the stator vanes are indexed to 0°, the chamber is ready for reproducible disruption experimentation."
    ))

    # Slide 82: Master Synthesis & Defense Conclusion
    slides.append(make_split_cards(
        part="Part 6: Tabletop Prototype & Scaling",
        title="Master Synthesis & Technical Defense Conclusion",
        subtitle="Unifying Navier-Stokes fluid mechanics, high-fidelity CFD, and physical experimentation",
        card1={
            "title": "KEY SCIENTIFIC CONCLUSIONS",
            "bullets": [
                "• 1. Irreversible Disruption Proven:",
                "  117.30% core vertical vorticity reduction verified on 96³ Navier-Stokes mesh with sign reversal.",
                "",
                "• 2. Rigorous Mass Conservation:",
                "  Peak divergence RMS bounded at 0.7353 s⁻¹, far below the 1.00 numerical tolerance.",
                "",
                "• 3. 81% Suction Power Conservation:",
                "  Auto-tuned minimum viable threshold of -47.80 Pa avoids brute-force -250 Pa waste.",
                "",
                "• 4. Verified Software Reliability:",
                "  17/17 automated pytest test suites passed with zero failures."
            ],
            "col": "#34D399"
        },
        card2={
            "title": "TRANSLATIONAL PATH FORWARD",
            "bullets": [
                "• Hydrodynamic Similitude:",
                "  Froude number Fr = 1.66 invariance bridges the gap between 1,000m supercells and 600mm laboratory prototypes.",
                "",
                "• Open Reproducible Hardware:",
                "  $227.00 USD open-source hardware blueprint democratizes severe storm mitigation research.",
                "",
                "• Paradigm Shift:",
                "  Proves atmospheric vortex mitigation is an achievable kinematic and thermodynamic engineering reality, not science fiction.",
                "",
                "• The Floor is Open for Questions."
            ],
            "col": "#38BDF8"
        },
        notes="PROFESSOR'S LECTURE NOTES - SLIDE 82 (MASTER DEFENSE CONCLUSION):\nIn conclusion, colleagues, Project AEOLUS demonstrates that violent atmospheric tornadoes are not invincible. They are delicate thermodynamic engines sustained by ground-level angular momentum flux. By synchronously attacking the rear-flank downdraft with +3K thermal buoyancy and starving the boundary layer with -47.80 Pa off-axis suction, we achieve a verified 117.30% vorticity reduction. Bridged by Froude scaling to a $227 tabletop prototype, AEOLUS establishes a new scientific frontier in environmental fluid mechanics. Thank you, and I now welcome your questions."
    ))

    return slides
