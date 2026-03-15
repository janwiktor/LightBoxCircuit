# LightBoxCircuit

Publication-quality schematic for an **ESP32-driven 3-channel 12 V LED light box** controller, generated from a Python script using [`schemdraw`](https://schemdraw.readthedocs.io).

## Schematic walkthrough

### U1 — Power Input (Hailege H-1-1765, USB-C PD module)

The leftmost block. It takes USB power (5–20 V via USB-C Power Delivery negotiation) on its `USB` pin (left side) and outputs a regulated **12 V DC** on its `VOUT` pin (top). That VOUT pin connects directly up to the orange **12 V rail** — the horizontal line running the full width of the schematic. Its `GND` pin (bottom) drops straight down to a GND symbol.

---

### 12 V rail (orange line)

The horizontal orange line is the backbone of the schematic. Everything that needs 12 V taps off it. Junction dots (filled circles) mark every tap point:
- at U1 VOUT
- at C1
- at U2 VIN
- at the drain of each MOSFET channel (three dots, one per LED strip)

---

### C1 — Bulk decoupling, 1000 µF / 25 V electrolytic

Hangs vertically from the 12 V rail down to GND. Its job is to absorb sudden current demands from the LED strips so the USB-C module doesn't see large transient spikes. Rated 25 V (not 16 V) because USB-C PD can momentarily negotiate higher voltages during handshake — the extra headroom protects it.

---

### U2 — LM2596S Buck Converter (12 V → 3.3 V)

Drops from the 12 V rail via a short vertical orange wire into its `VIN` pin (top, pin 1). Internally it switches to produce a lower regulated voltage:
- `VOUT` (bottom, pin 3) — outputs **3.3 V**, exits to the right as the red **3.3 V bus**
- `GND` (bottom, pin 2) — exits down-left to a GND symbol

---

### C2 — 100 µF / 16 V electrolytic, and C3 — 100 nF ceramic

Both hang from the 3.3 V bus (red) down to GND, placed between U2 and U3. They serve two different purposes:
- **C2** (larger, electrolytic): bulk energy reservoir — handles slower, larger current transients as the ESP32 wakes up radios, etc.
- **C3** (smaller, ceramic): high-frequency decoupling — kills the fast noise spikes that C2's inductance is too slow to absorb.

Together they keep the 3.3 V rail clean for the ESP32.

---

### U3 — ESP32 DevKit C V4

Powered by the 3.3 V bus on its `V33` pin (left side). `EGND` (left side) connects down to GND. On the right side it exposes three PWM outputs:
- `GPIO25` → PWM channel 1
- `GPIO26` → PWM channel 2
- `GPIO27` → PWM channel 3

Each GPIO drives a green wire rightward into its respective gate network.

---

### Gate network (R1/R4, R2/R5, R3/R6 — repeated ×3)

Each channel has the same two-resistor network between the ESP32 GPIO and the MOSFET gate:

1. **R1/R2/R3 (100 Ω series resistor)** — in line between GPIO and gate. Limits the current spike when the gate capacitance charges/discharges, dampens ringing, and protects the ESP32 output if something goes wrong.

2. **Junction dot** — the node between R_series and the gate has two paths: forward to the gate, and downward through the pull-down.

3. **R4/R5/R6 (10 kΩ pull-down)** — from the gate node down to GND. This is critical: during ESP32 boot the GPIO pins are floating or tristated for a brief moment. Without the pull-down, the gate floats high → MOSFET turns on → LEDs flash. The 10 kΩ holds the gate firmly at 0 V until the GPIO actively drives it.

---

### Q1/Q2/Q3 — IRLZ44N N-channel MOSFETs

Each MOSFET is a **low-side switch** — it sits in the GND path of the LED strip, not the 12 V path:

- **Gate** — receives the signal from the gate network above
- **Drain** — connects upward (blue wire) to the LED strip's negative terminal, and also up to the 12 V bus tap
- **Source** — connects down to GND

When the ESP32 drives the gate high (3.3 V PWM), the MOSFET turns on, completing the circuit through the LED strip. When gate = 0 V, MOSFET is off, LED strip is dark. IRLZ44N specifically (vs IRFZ44N) is a logic-level variant that fully saturates at 3.3 V gate — a standard IRFZ44N would only partially turn on at 3.3 V, causing heat and reduced brightness.

---

### LED1/LED2/LED3 — 12 V Full-Spectrum LED Strips

Each strip is wired the same way:
- **Positive terminal (LED+)** — connects to the 12 V rail (via the junction dot and the blue vertical wire going up)
- **Negative terminal (LED−)** — connects to the MOSFET drain

Current flows: 12 V rail → LED strip → MOSFET drain → through MOSFET channel → source → GND. The MOSFET controls whether that path is open or closed.

All three strips are **in parallel** — each gets its own independent MOSFET, so you can dim each channel separately via PWM.

---

## Colour coding

| Colour | Rail |
|--------|------|
| Orange `#e65100` | 12 V power |
| Red `#c62828` | 3.3 V power |
| Grey `#546e7a` | GND |
| Green `#2e7d32` | PWM / gate signals |
| Blue `#1565c0` | LED drain side |

## Output files

| File | Description |
|------|-------------|
| `schematic.svg` | Vector schematic (web / Inkscape) |
| `schematic.png` | 300 DPI raster for print |

## Regenerate

```bash
pip install schemdraw matplotlib
python3 schematic.py
```
