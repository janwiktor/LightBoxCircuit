# LightBoxCircuit

Publication-quality schematic for an **ESP32-driven 3-channel 12 V LED light box** controller, generated from a Python script using [`schemdraw`](https://schemdraw.readthedocs.io).

## Circuit overview

| Block | Part | Notes |
|-------|------|-------|
| U1 – Power input | Hailege H-1-1765 | USB-C PD module, outputs 12 V DC |
| U2 – Regulation | AZDelivery LM2596S | Buck converter 12 V → 3.3 V, max 3 A |
| U3 – MCU | AZDelivery ESP32 DevKit C V4 | 3.3 V logic, PWM via LEDC peripheral |
| Q1–Q3 | IRLZ44N | Logic-level N-ch MOSFET, fully on at 3.3 V gate |
| C1 | 1000 µF / 25 V electrolytic | Bulk decoupling on 12 V rail |
| C2 | 100 µF / 16 V electrolytic | Bulk decoupling on 3.3 V rail |
| C3 | 100 nF ceramic | HF decoupling on 3.3 V rail |
| R1–R3 | 100 Ω | Gate series resistors (one per channel) |
| R4–R6 | 10 kΩ | Gate pull-down resistors (prevent boot-flash) |
| D1–D3 | 1N4007 | Flyback diodes across each LED strip channel |
| LED1–3 | 12 V Full-Spectrum LED Strip | Parallel load, low-side switched |

### Key design decisions

- **IRLZ44N** (not IRFZ44N): logic-level variant — fully saturates at 3.3 V gate.
- **Low-side switching**: MOSFETs switch the GND path; LED+ stays on 12 V.
- **Gate pull-downs** (R4–R6) are mandatory — prevent LEDs flashing during ESP32 boot.
- **C1 rated 25 V** (not 16 V) to handle USB-C PD transients on the 12 V rail.
- **PWM** via ESP32 LEDC peripheral on GPIO 25, 26, 27 (1–5 kHz).
- NTC thermistor (optional) on GPIO13 as ADC input for temperature monitoring.

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

Both `schematic.svg` and `schematic.png` are written to the repo root.

## Colour coding

| Colour | Rail |
|--------|------|
| Orange `#e65100` | 12 V power |
| Red `#c62828` | 3.3 V power |
| Grey `#546e7a` | GND |
| Green `#2e7d32` | PWM / gate signals |
| Blue `#1565c0` | LED drain side |
