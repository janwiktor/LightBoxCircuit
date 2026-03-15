# ESP32 LED Light Box — Schematic Generator
## Claude Code Session Prompt
---

## Project Instructions

Generate a clean, legible, professional electronics schematic using Python
`schemdraw` (https://schemdraw.readthedocs.io). Save output as both SVG and PNG.
The schematic should be publication-quality and re-runnable as a Python script.

Treat it as a dev project - meaning all changes and specs should be committed to a repository & pushed to remote on Github.

Before starting, analyze the circuit specification and double check if the design looks acceptable.

## Install dependencies first

```
pip install schemdraw matplotlib
```

schemdraw uses matplotlib as a backend. For SVG output use:
```python
import schemdraw
schemdraw.use('svg')  # or 'matplotlib' for PNG
```

---

## Circuit Specification

### Components

| Ref  | Part                          | Description                                      |
|------|-------------------------------|--------------------------------------------------|
| U1   | Hailege H-1-1765              | USB-C Power Delivery module, outputs 12V DC      |
| U2   | AZDelivery LM2596S            | DC-DC Buck converter, 12V → 3.3V, max 3A         |
| U3   | AZDelivery ESP32 DevKit C V4  | MCU, dual-core, WiFi+BT, 3.3V logic              |
| Q1–3 | IRLZ44N                       | Logic-level N-Ch MOSFET, VGS(th)≈1.5V, TO-220   |
| C1   | 1000µF / 25V electrolytic     | Bulk decoupling on 12V rail                      |
| C2   | 100µF / 16V electrolytic      | Bulk decoupling on 3.3V rail near ESP32          |
| C3   | 100nF ceramic                 | HF decoupling on 3.3V rail near ESP32            |
| R1–3 | 100Ω                          | MOSFET gate series resistors (one per channel)   |
| R4–6 | 10kΩ                          | MOSFET gate pull-down resistors (gate to GND)    |
| D1–3 | 1N4007                        | Flyback diodes across each LED strip channel     |
| LED1–3 | 12V Full Spectrum LED Strip | Load, parallel connected to 12V rail             |
| NTC  | 10kΩ NTC thermistor (optional)| Temperature sensor, voltage divider to GPIO13    |

---

## Circuit Topology / Netlist

### Power rails
- **12V rail**: USB-C PD module VOUT+ → C1 (to GND) → splits to:
  - LM2596S VIN+
  - All LED strip positive terminals (parallel)
- **3.3V rail**: LM2596S VOUT+ → C2 (to GND) → C3 (to GND) → ESP32 3V3 pin
- **GND**: Common bus connecting all component grounds

### Signal / switching
- ESP32 GPIO25 → R1 (100Ω) → Q1 Gate; R4 (10kΩ) from Q1 Gate to GND
- ESP32 GPIO26 → R2 (100Ω) → Q2 Gate; R5 (10kΩ) from Q2 Gate to GND
- ESP32 GPIO27 → R3 (100Ω) → Q3 Gate; R6 (10kΩ) from Q3 Gate to GND
- Q1/Q2/Q3 are low-side switches:
  - Drain connects to LED strip negative terminal
  - Source connects to GND bus
- Each LED strip: positive to 12V rail, negative to MOSFET drain
- D1/D2/D3: anode to MOSFET drain (LED−), cathode to 12V rail (LED+)
  — flyback protection across each strip

### Optional
- NTC thermistor: one leg to 3.3V via 10kΩ resistor, other leg to GND
  Centre tap → ESP32 GPIO13 (ADC input)

---

## Layout guidance for schemdraw

Lay out the schematic left to right in these zones:

1. **Power input** (leftmost): USB-C module U1, C1
2. **Regulation**: LM2596S U2 below the 12V bus, with 3.3V rail going right
3. **Decoupling**: C2, C3 on the 3.3V rail between U2 and U3
4. **MCU**: ESP32 U3 as a box with labelled GPIO pins on the right side
5. **Gate network**: R1–R3 (series), R4–R6 (pull-downs to GND), one column per channel
6. **MOSFETs**: Q1/Q2/Q3 stacked vertically, one per channel
7. **Load**: LED strips to the right of MOSFETs, D1–D3 flyback diodes in parallel

Use `schemdraw.elements`:
- `elm.IcPin` or custom boxes for ICs (U1, U2, U3)
- `elm.Resistor` for R1–R6
- `elm.Capacitor` / `elm.PolarCapacitor` for C1–C3
- `elm.Diode` for D1–D3
- `elm.BjtNpn` or a labelled box for MOSFETs (schemdraw has no MOSFET symbol built-in; use a labelled rectangle or `elm.NFet` if available in your version)
- `elm.Ground` for GND symbols
- `elm.Dot` for junction dots on shared nets
- `elm.Label` for net labels (12V, 3.3V, GND, PWM)

---

## Colour scheme (matplotlib / SVG)

Use a dark background (`#0d1117`) with these wire colours:
- 12V rail:  `#ffa657` (orange)
- 3.3V rail: `#f85149` (red)
- GND:       `#8b949e` (grey)
- PWM signal:`#3fb950` (green)
- LED drain: `#58a6ff` (blue)

Or generate with a white background for maximum print legibility — user's preference.

---

## Output files

Save the following to the repo root:
- `schematic.py`       — the main generation script
- `schematic.svg`      — vector output (scalable, web-friendly)
- `schematic.png`      — raster output at 300 DPI for print
- `README.md`          — brief project description and how to regenerate

---

## Repository structure to create

```
LightBoxCircuit/
├── schematic.py          # main schemdraw script
├── schematic.svg         # generated SVG output
├── schematic.png         # generated PNG output
├── README.md             # project description
└── CLAUDE_CODE_PROMPT.md # this file (for re-bootstrapping sessions)
```

---

## Design decisions already made (do not re-ask)

- IRLZ44N chosen over IRFZ44N: logic-level variant, fully saturates at 3.3V gate
- ESP32 powered from 3.3V pin (from buck), not VIN
- All LED strips wired in parallel (not series) to 12V rail
- Low-side MOSFET switching (MOSFETs switch the GND path, not the 12V path)
- Gate pull-down resistors (R4–R6) are mandatory to prevent boot-time LED flash
- C1 rated 25V minimum (not 16V) due to USB-C PD transients on 12V rail
- C2 can be 16V or higher (3.3V rail, ample headroom)
- PWM via ESP32 LEDC peripheral, GPIO 25/26/27, frequency 1–5 kHz

---

## Follow-up improvements to consider in Claude Code

Once the base schematic is generated and looks correct:

1. Add a `--channel N` CLI argument to highlight a single channel
2. Export a KiCad netlist from the component/net data
3. Add a bill-of-materials CSV generator alongside the schematic
4. Parameterise number of LED channels (default 3, configurable)
