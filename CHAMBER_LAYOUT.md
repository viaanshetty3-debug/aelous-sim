# Project AEOLUS: Tabletop Chamber Fabrication Map

**Document Status:** Engineering Fabrication Specification  
**System Target:** 600mm Tabletop Vortex Disruption Chamber  
**Associated Documents:** [`HARDWARE_PLAN.md`](file:///home/aeolus_sim/HARDWARE_PLAN.md), [`main.ino`](file:///home/aeolus_sim/main.ino)  

---

## 1. System Dimensional Specifications

| Parameter | Dimension | Notes & Tolerances |
| :--- | :--- | :--- |
| **Total Chamber Height** | 600 mm | Top of exhaust flange to baseplate bottom |
| **Chamber Footprint** | 600 mm × 600 mm | Extruded aluminum outer frame envelope |
| **Core Cylinder Diameter** | 300 mm | Working vortex core zone |
| **Outer Wall Diameter** | 600 mm | 6mm cast acrylic cylinder or square enclosure |
| **Base Vent Zone Height** | 200 mm | Z = 0 mm to Z = 200 mm |
| **Main Vortex Core Zone** | 250 mm | Z = 200 mm to Z = 450 mm |
| **Thermal Grid Zone** | 50 mm | Z = 450 mm to Z = 500 mm |
| **Exhaust Plenum Zone** | 100 mm | Z = 500 mm to Z = 600 mm |

---

## 2. Vertical Z-Axis Layout

```
Z (mm)
 600 ┌────────────────────────────────────────────────────────┐ Top Exhaust Plenum
     │  Top Plate: 12mm Birch Ply / Aluminum Face             │
     │  Exhaust Fan Port: 120mm Ø (3000 CFM Blower Mount)     │
 500 ├────────────────────────────────────────────────────────┤
     │  THERMAL RFD GRID ZONE (450mm – 500mm)                 │
     │  • Bank A (5x 300W Ceramic) | Bank B (5x 300W Ceramic) │
     │  • Hot-air secondary circulation blowers               │
     │  • Chamber reference temperature sensor tap            │
 450 ├────────────────────────────────────────────────────────┤
     │  MAIN VORTEX OBSERVATION CHAMBER (200mm – 450mm)       │
     │  • 360° Clear acrylic view window (6mm)                │
     │  • Pressure transducer sampling tap at Z = 325mm       │
     │  • Optical vorticity tracking grid                     │
 200 ├────────────────────────────────────────────────────────┤
     │  TANGENTIAL BASE INFLOW ZONE (0mm – 200mm)             │
     │  • 8x Tangential angled slots (45° pitch, 200mm high)  │
     │  • Ultrasonic mist injection nozzles at Z = 50mm       │
   0 ├────────────────────────────────────────────────────────┤
     │  Base Plate: 12mm Seal Plate                           │
     │  Suction Port: Dual 75mm Ø ports (-250 Pa Sink)        │
     └────────────────────────────────────────────────────────┘
```

---

## 3. Plan View & Port Geometry

### 3.1 Top View (Cross-Section at Z = 100mm - Base Inlets)

```
                       [North]
                     Inlet Slot 1
                         │ ↗ (45° angle)
                  ┌──────┴──────┐
      Inlet Slot 8│  ┌───────┐  │ Inlet Slot 2
           ▲      │  │ Core  │  │      ▲
           │      │  │ 300mm │  │      │
 [West] ───┼──────┤  │   Ø   │  ├──────┼─── [East]
           │      │  │       │  │      │
      Inlet Slot 7│  └───────┘  │ Inlet Slot 3
                  └──────┬──────┘
                         │ ↙
                     Inlet Slot 5
                       [South]

* 8 tangential slots pitched at 45° to initiate cyclonic rotation.
* Dual 75mm Ø suction ports located in base plate offset 100mm from centerline.
* Mist nozzles injected tangentially into slots 2, 4, 6, and 8.
```

### 3.2 Port Details & Offsets

- **Tangential Inflow Slots (8 Slots):**
  - Dimensions: 200 mm high × 25 mm wide.
  - Spacing: Evenly distributed every 45° azimuth (0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°).
  - Vane Angle: Fixed 45° inward deflector angle for cyclonic swirling.
- **Suction Port (Momentum Sink):**
  - **Port Offset:** Dual 75 mm Ø circular cutouts positioned at **R = 100 mm offset** from chamber center (180° opposed at North-South azimuth) to prevent core stall while evacuating boundary layer angular momentum.
  - Fitting: PVC bulkhead union, 75 mm (3") slip fit with silicone compression washer.
- **Mist Injection Ports:**
  - Elevation: Z = 50 mm (offset 50 mm from chamber floor).
  - Fitting: 1/2" barbed push-to-connect mist nozzles aimed along the tangential vector.
- **Sensor Taps:**
  - Static Pressure Tap (BME680): Z = 325 mm (core midplane), 1/4" NPT threaded port.
  - Chamber Thermocouple / DS18B20: Z = 475 mm (aligned directly above the thermal grid).

---

## 4. Bill of Structural Materials & Cutting Schedule

| Part | Description | Dimensions / Spec | Qty |
| :--- | :--- | :--- | :--- |
| **Corner Columns** | Aluminum T-Slot Profile | 45 mm × 45 mm × 600 mm | 4 |
| **Horizontal Rails**| Aluminum T-Slot Profile | 45 mm × 45 mm × 510 mm | 8 |
| **Chamber Windows** | Cast Acrylic (Clear) | 510 mm × 600 mm × 6 mm | 3 |
| **Access Panel**    | Cast Acrylic (Removable)| 510 mm × 600 mm × 6 mm | 1 |
| **Top Plate**       | Marine/Birch Plywood | 600 mm × 600 mm × 12 mm | 1 |
| **Bottom Plate**    | Marine/Birch Plywood | 600 mm × 600 mm × 12 mm | 1 |
| **Inlet Vanes**     | 3D Printed PETG / Acrylic | 200 mm × 50 mm × 4 mm (45° angle) | 8 |
| **Corner Brackets** | Heavy-duty Gusset Brackets | M6 T-slot hardware | 16 |
| **Gaskets**         | High-temp silicone strip | 15 mm wide × 3 mm thick | 10 m |

---

## 5. Fabrication & Machining Steps

### Step 1: Baseplate & Top Plate Machining
1. Cut two 600 mm × 600 mm square blanks from 12 mm plywood.
2. On **Top Plate**:
   - Hole-saw a central 120 mm Ø hole for the 3000 CFM exhaust blower.
   - Drill 4× M6 clearance holes for the blower isolation flange.
3. On **Base Plate**:
   - Machine two 75 mm Ø suction ports at **X = ±100 mm, Y = 0 mm** (100 mm radial offset from center).
   - Drill four 1/2" through-holes at 45° diagonals for mist feedlines.

### Step 2: Inflow Vanes & Acrylic Walls
1. Cut the 8 air guide slots (200 mm tall × 25 mm wide) in the lower section of the wall panels.
2. Affix 45° guide vanes over each slot using acrylic solvent weld (Weld-On 4).
3. Tap 1/4" NPT hole at Z = 325 mm on the south acrylic wall for the static pressure sensor.

### Step 3: Frame Assembly & Sealing
1. Fasten the 45×45 mm aluminum extrusion frame with M6 button-head bolts and corner gussets. Verify diagonal squareness (< 1 mm deviation).
2. Install baseplate with continuous bead of food-grade RTV silicone sealant.
3. Slide acrylic panels into extrusion T-slots cushioned with neoprene gaskets.
4. Mount top plate and secure with clamp latches to allow maintenance access to the thermal grid.

### Step 4: Quality & Pressure Validation
- **Leakage Test:** Seal the 8 lower slots with temporary magnetic covers. Pull -300 Pa using the vacuum motor. Pressure decay must be < 5 Pa over 60 seconds.
- **Thermal Shroud Check:** Verify that heater element mounts maintain > 30 mm air gap from acrylic walls to prevent thermal softening.
