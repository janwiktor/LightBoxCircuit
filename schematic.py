#!/usr/bin/env python3
"""
LightBoxCircuit — ESP32 3-Channel LED Controller Schematic Generator
Run:  python3 schematic.py
Out:  schematic.svg  schematic.png
"""
import matplotlib
matplotlib.use('Agg')
import schemdraw
import schemdraw.elements as elm

# ── Colour palette (white background) ─────────────────────────────────────────
C12  = '#e65100'   # 12 V rail  (orange)
C33  = '#c62828'   # 3.3 V rail (red)
CGND = '#546e7a'   # GND        (grey)
CPWM = '#2e7d32'   # PWM signal (green)
CDRN = '#1565c0'   # LED drain  (blue)
CBLK = '#212121'   # components

# ── Layout constants ───────────────────────────────────────────────────────────
UNIT  = 3.0   # schemdraw default element length

Y_12V = 12.0  # 12 V bus — drawn as an explicit horizontal line at this y

# NFet geometry (default orientation: drain=start, source 1.5 below, gate 1.37 right)
# Placed via .anchor('gate'):  drain_x = gate_x - 1.37,  drain_y = gate_y + 0.75
NFET_GATE_DX = 1.37
NFET_GATE_DY = 0.75
NFET_DS_H    = 1.50

# Gate-network geometry: PWM_label ─ stub ─ R_series ─ stub ─ junction ─ stub ─ gate
STUB          = 0.30
PWM_TO_GATE_X = STUB + UNIT + STUB + STUB   # 3.9

# Gate y-level (same for all three channels)
GATE_Y  = 7.0
DRAIN_Y = GATE_Y + NFET_GATE_DY   # 7.75

# PWM-label x positions; drain x follows from NFet geometry
PWM_X   = [20.0, 27.0, 34.0]
GATE_X  = [x + PWM_TO_GATE_X        for x in PWM_X]   # [23.9, 30.9, 37.9]
DRAIN_X = [gx  - NFET_GATE_DX       for gx in GATE_X]  # [22.53, 29.53, 36.53]

# ── 12 V bus x-positions (all fixed, so dots sit exactly on the bus) ──────────
X_U1      =  3.0   # U1 VOUT tap
X_C1      =  8.0   # C1 tap  (5 units from U1 — clear space between U1 body and C1)
X_U2      = 13.5   # U2 VIN tap (5.5 units from C1 — no overlap with C1 drop)
X_BUS_END = DRAIN_X[-1] + 2.0   # ≈ 38.5

CHANNELS = [
    # (Q, R_series, R_pulldown, LED)
    ('Q1', 'R1', 'R4', 'LED1'),
    ('Q2', 'R2', 'R5', 'LED2'),
    ('Q3', 'R3', 'R6', 'LED3'),
]


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1  —  Power Input & Regulation
# ══════════════════════════════════════════════════════════════════════════════
def draw_power_section(d):
    """
    12 V bus is drawn first as one horizontal line at exactly Y_12V.
    All junction dots are placed at (x, Y_12V) — guaranteed on the bus.
    U1 and U2 hang below the bus (VOUT/VIN pins on top side).
    """

    # ── 12 V bus ─────────────────────────────────────────────────────────────
    d.add(elm.Line()
          .at((0.5, Y_12V)).right().length(X_BUS_END - 0.5)
          .color(C12))
    d.add(elm.Label().at((X_BUS_END, Y_12V)).label('12 V', loc='right').color(C12))

    # Junction dots at every tap — all at exact Y_12V
    for x in [X_U1, X_C1, X_U2] + list(DRAIN_X):
        d.add(elm.Dot().at((x, Y_12V)).color(C12))

    # ── U1: USB-C PD module ──────────────────────────────────────────────────
    # VOUT pin on top → IC body hangs below the 12 V bus
    u1 = d.add(elm.Ic(
        pins=[
            elm.IcPin(name='USB',  side='left',   pin='A', anchorname='USB'),
            elm.IcPin(name='VOUT', side='top',    pin='1', anchorname='VOUT'),
            elm.IcPin(name='GND',  side='bottom', pin='2', anchorname='GND'),
        ],
        edgepadH=0.5, edgepadW=0.9, pinspacing=1.0,
        label='U1\nHailege H-1-1765\n(USB-C PD → 12 V)',
    ).at((X_U1, Y_12V)).anchor('VOUT'))

    d.add(elm.Line().at(u1.USB).left().length(0.8).color(CBLK))
    d.add(elm.Label().label('USB-C\n5–20 V PD', loc='left'))
    d.add(elm.Line().at(u1.GND).down().length(0.5).color(CGND))
    d.add(elm.Ground().color(CGND))

    # ── C1: 1000 µF / 25 V ───────────────────────────────────────────────────
    d.add(elm.Capacitor2()
          .at((X_C1, Y_12V)).down().length(UNIT)
          .label('C1\n1000 µF\n25 V', loc='right').color(C12))
    d.add(elm.Ground().color(CGND))

    # ── U2: LM2596S buck converter ───────────────────────────────────────────
    # Short wire from 12 V tap down to U2 VIN:
    #   • separates the IC body from the bus (pin-1 label no longer overlays the rail)
    #   • lowers the 3.3 V rail so U3 has vertical clearance from the 12 V line
    d.add(elm.Line().at((X_U2, Y_12V)).down().length(2.0).color(C12))
    u2 = d.add(elm.Ic(
        pins=[
            elm.IcPin(name='VIN',  side='top',   pin='1', anchorname='VIN'),
            elm.IcPin(name='VOUT', side='right', pin='2', anchorname='VOUT'),
            elm.IcPin(name='GND',  side='left',  pin='3', anchorname='GND'),
        ],
        edgepadH=0.5, edgepadW=0.9, pinspacing=1.0,
        label='U2\nLM2596S\n12 V → 3.3 V',
    ).anchor('VIN'))

    d.add(elm.Line().at(u2.GND).left().length(0.5).color(CGND))
    d.add(elm.Ground().color(CGND))

    # ── 3.3 V bus from U2 ────────────────────────────────────────────────────
    d.add(elm.Line().at(u2.VOUT).right().length(0.6).color(C33))
    junc_c2 = d.add(elm.Dot().color(C33))
    d.add(elm.Line().right().length(2.0).color(C33))
    junc_c3 = d.add(elm.Dot().color(C33))
    d.add(elm.Line().right().length(2.5).color(C33))
    junc_u3 = d.add(elm.Dot().color(C33))

    # ── C2: 100 µF / 16 V ────────────────────────────────────────────────────
    d.push()
    d.add(elm.Capacitor2()
          .at(junc_c2.start).down().length(UNIT)
          .label('C2\n100 µF\n16 V', loc='right').color(C33))
    d.add(elm.Ground().color(CGND))
    d.pop()

    # ── C3: 100 nF ceramic ───────────────────────────────────────────────────
    d.push()
    d.add(elm.Capacitor()
          .at(junc_c3.start).down().length(UNIT)
          .label('C3\n100 nF', loc='right').color(C33))
    d.add(elm.Ground().color(CGND))
    d.pop()

    return junc_u3


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2  —  MCU: ESP32
# ══════════════════════════════════════════════════════════════════════════════
def draw_esp32(d, v33_anchor):
    """Draw U3 (ESP32). NTC omitted — GPIO25/26/27 only."""
    u3 = d.add(elm.Ic(
        pins=[
            elm.IcPin(name='V33',    side='left',  pin='1', anchorname='V33'),
            elm.IcPin(name='EGND',   side='left',  pin='2', anchorname='EGND'),
            elm.IcPin(name='GPIO25', side='right', pin='3', anchorname='GPIO25'),
            elm.IcPin(name='GPIO26', side='right', pin='4', anchorname='GPIO26'),
            elm.IcPin(name='GPIO27', side='right', pin='5', anchorname='GPIO27'),
        ],
        edgepadH=0.5, edgepadW=1.0, pinspacing=0.9,
        label='U3\nESP32 DevKit C V4',
    ).at(v33_anchor.start).anchor('V33'))

    d.add(elm.Line().at(u3.EGND).left().length(0.5).color(CGND))
    d.add(elm.Ground().color(CGND))

    for pin_name, gpio_num, ch in [('GPIO25', 25, 1),
                                    ('GPIO26', 26, 2),
                                    ('GPIO27', 27, 3)]:
        pin = getattr(u3, pin_name)
        d.add(elm.Line().at(pin).right().length(0.5).color(CPWM))
        d.add(elm.Label()
              .label(f'PWM{ch}  (GPIO{gpio_num})', loc='right')
              .color(CPWM))


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3  —  MOSFET channel  (one per call, drawn left → right)
# ══════════════════════════════════════════════════════════════════════════════
def draw_channel(d, pwm_x, q_name, rs_name, rp_name, led_name, ch_num):
    """
    Left-to-right signal flow:

      PWM_label ── R_series ── junction ── gate
                                  |         [NFet Q]
                               R_pulldown  drain ── LED strip (from 12V bus above)
                                  |        source
                                 GND         |
                                            GND
    """
    gate_x  = pwm_x + PWM_TO_GATE_X
    gate_y  = GATE_Y
    drain_x = gate_x - NFET_GATE_DX
    drain_y = gate_y + NFET_GATE_DY
    src_x   = drain_x
    src_y   = drain_y - NFET_DS_H
    junc_x  = gate_x - STUB

    # ── Gate network ─────────────────────────────────────────────────────────
    d.add(elm.Label()
          .at((pwm_x, gate_y))
          .label(f'PWM{ch_num}  (GPIO{24 + ch_num})', loc='left')
          .color(CPWM))

    d.add(elm.Line().at((pwm_x, gate_y)).right().length(STUB).color(CPWM))
    d.add(elm.Resistor()
          .right().length(UNIT)
          .label(f'{rs_name}  100 Ω', loc='top').color(CPWM))
    d.add(elm.Line().right().length(STUB).color(CPWM))

    d.add(elm.Dot().at((junc_x, gate_y)).color(CPWM))

    d.push()
    d.add(elm.Resistor()
          .at((junc_x, gate_y)).down().length(UNIT)
          .label(f'{rp_name}  10 kΩ', loc='right').color(CGND))
    d.add(elm.Ground().color(CGND))
    d.pop()

    d.add(elm.Line().at((junc_x, gate_y)).right().length(STUB).color(CPWM))

    q = d.add(elm.NFet()
              .at((gate_x, gate_y)).anchor('gate')
              .label(f'{q_name}\nIRLZ44N', loc='right')
              .color(CBLK))

    # ── LED strip: 12V bus → drain ───────────────────────────────────────────
    # Junction dot on 12V bus was placed in draw_power_section at (drain_x, Y_12V)
    led_len = Y_12V - drain_y
    d.add(elm.Line()
          .at((drain_x, Y_12V)).down().length(led_len)
          .label(f'{led_name}\n12 V LED strip', loc='right')
          .color(CDRN))
    d.add(elm.Dot().at((drain_x, drain_y)).color(CDRN))

    # ── Source → GND ─────────────────────────────────────────────────────────
    d.add(elm.Line().at((src_x, src_y)).down().length(0.6).color(CGND))
    d.add(elm.Ground().color(CGND))


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    with schemdraw.Drawing(fontsize=9, show=False) as d:
        d.config(unit=UNIT)

        v33_node = draw_power_section(d)
        draw_esp32(d, v33_node)

        for i, (q, rs, rp, led) in enumerate(CHANNELS):
            draw_channel(d, PWM_X[i], q, rs, rp, led, i + 1)

        d.save('schematic.svg')
        d.save('schematic.png', dpi=300)
        print("Saved: schematic.svg  schematic.png")


if __name__ == '__main__':
    main()
