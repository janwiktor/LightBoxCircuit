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
CBLK = '#212121'   # components / borders

# ── Layout constants ───────────────────────────────────────────────────────────
#   All in schemdraw internal units (unit=3.0 → default resistor/line length = 3)
UNIT       = 3.0
# Power-section y-coordinates
Y_12V      = 10.0   # 12 V bus level
Y_33V      =  4.0   # 3.3 V bus level
Y_GND      =  0.0   # GND level (symbolic; Ground elements are used throughout)
# Channel x-centres (3 identical channels, side by side)
CH_X       = [24.0, 30.0, 36.0]
CH_DRAIN_Y =  8.5   # drain tie-point (junction between LED strip and NFet drain)
CH_LOAD_H  =  3.5   # height of LED+diode load section above drain


def net_label(d, pos, text, color, side='right'):
    """Add a small net-name flag at an explicit position."""
    d.add(elm.Label().at(pos).label(text, loc=side).color(color))


def gnd_at(d, pos):
    """Drop a GND symbol at a given (x,y)."""
    d.add(elm.Ground().at(pos).color(CGND))


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1  —  Power Input & Regulation (left side)
# ══════════════════════════════════════════════════════════════════════════════
def draw_power_section(d):
    """Draw U1, 12 V bus, C1, U2, 3.3 V bus, C2, C3."""

    # ── U1: USB-C PD module ──────────────────────────────────────────────────
    u1 = d.add(elm.Ic(
        pins=[
            elm.IcPin(name='USB',  side='left',  pin='A', anchorname='USB'),
            elm.IcPin(name='VOUT', side='right', pin='1', anchorname='VOUT'),
            elm.IcPin(name='GND',  side='right', pin='2', anchorname='GND'),
        ],
        edgepadH=0.6, edgepadW=0.9, pinspacing=1.4,
        label='U1\nHailege H-1-1765\n(USB-C PD → 12 V)',
    ).at((1.5, Y_12V - 0.7)).anchor('center'))

    # USB-C input label
    d.add(elm.Line().at(u1.USB).left().length(0.8).color(CBLK))
    d.add(elm.Label().label('USB-C\n5–20 V PD', loc='left'))

    # GND from U1
    d.add(elm.Line().at(u1.GND).right().length(0.6).color(CGND))
    d.add(elm.Ground().color(CGND))

    # ── 12 V bus (horizontal) ────────────────────────────────────────────────
    d.add(elm.Line().at(u1.VOUT).right().length(0.6).color(C12))
    # Extend 12 V bus to the right (two segments with junction taps)
    junc_c1  = d.add(elm.Dot().color(C12))
    d.add(elm.Line().right().length(3.5).color(C12))
    junc_u2  = d.add(elm.Dot().color(C12))
    d.add(elm.Line().right().length(12.0).color(C12))
    # Arrowhead / net label at right end of 12 V bus
    d.add(elm.Label().label('→ 12 V (to LED channels)', loc='right').color(C12))

    # ── C1: 1000 µF / 25 V ──────────────────────────────────────────────────
    d.push()
    d.add(elm.Capacitor2()
          .at(junc_c1.start).down().length(UNIT)
          .label('C1\n1000 µF\n25 V', loc='right').color(C12))
    d.add(elm.Ground().color(CGND))
    d.pop()

    # ── U2: LM2596S buck converter ───────────────────────────────────────────
    d.add(elm.Line().at(junc_u2.start).down().length(1.8).color(C12))
    u2 = d.add(elm.Ic(
        pins=[
            elm.IcPin(name='VIN',  side='top',    pin='1', anchorname='VIN'),
            elm.IcPin(name='VOUT', side='right',  pin='2', anchorname='VOUT'),
            elm.IcPin(name='GND',  side='bottom', pin='3', anchorname='GND'),
        ],
        edgepadH=0.5, edgepadW=0.9, pinspacing=1.0,
        label='U2\nLM2596S\n12 V → 3.3 V',
    ).anchor('VIN'))

    d.add(elm.Line().at(u2.GND).down().length(0.6).color(CGND))
    d.add(elm.Ground().color(CGND))

    # ── 3.3 V bus ────────────────────────────────────────────────────────────
    d.add(elm.Line().at(u2.VOUT).right().length(0.6).color(C33))
    junc_c2  = d.add(elm.Dot().color(C33))
    d.add(elm.Line().right().length(2.0).color(C33))
    junc_c3  = d.add(elm.Dot().color(C33))
    d.add(elm.Line().right().length(2.5).color(C33))
    junc_u3  = d.add(elm.Dot().color(C33))

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

    return junc_u3   # anchor for ESP32 3V3 pin


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2  —  MCU: ESP32
# ══════════════════════════════════════════════════════════════════════════════
def draw_esp32(d, v33_anchor):
    """Draw U3 (ESP32), connecting its 3V3 pin to v33_anchor."""
    u3 = d.add(elm.Ic(
        pins=[
            elm.IcPin(name='V33',    side='left',  pin='1',  anchorname='V33'),
            elm.IcPin(name='EGND',   side='left',  pin='2',  anchorname='EGND'),
            elm.IcPin(name='GPIO25', side='right', pin='3',  anchorname='GPIO25'),
            elm.IcPin(name='GPIO26', side='right', pin='4',  anchorname='GPIO26'),
            elm.IcPin(name='GPIO27', side='right', pin='5',  anchorname='GPIO27'),
            elm.IcPin(name='GPIO13', side='right', pin='6',  anchorname='GPIO13'),
        ],
        edgepadH=0.6, edgepadW=1.0, pinspacing=0.9,
        label='U3\nESP32 DevKit C V4',
    ).at(v33_anchor.start).anchor('V33'))

    # GND
    d.add(elm.Line().at(u3.EGND).left().length(0.6).color(CGND))
    d.add(elm.Ground().color(CGND))

    # PWM output labels
    for pin_name, gpio_num, ch in [('GPIO25', 25, 1),
                                    ('GPIO26', 26, 2),
                                    ('GPIO27', 27, 3)]:
        pin = getattr(u3, pin_name)
        d.add(elm.Line().at(pin).right().length(0.5).color(CPWM))
        d.add(elm.Label()
              .label(f'PWM{ch}  (GPIO{gpio_num})', loc='right')
              .color(CPWM))

    # NTC ADC
    d.add(elm.Line().at(u3.GPIO13).right().length(0.5).color(CPWM))
    d.add(elm.Label().label('NTC (GPIO13 ADC)', loc='right').color(CPWM))

    return u3


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3  —  MOSFET channels  (3 identical, drawn side by side)
# ══════════════════════════════════════════════════════════════════════════════
# NFet geometry (default orientation, drain=start, source 1.5 u below,
#               gate 1.37 u to the right at mid-height):
NFET_DS_H   = 1.5   # drain-to-source height
NFET_GATE_X = 1.37  # gate stub x-offset from drain x
NFET_GATE_DY = 0.75 # gate y-offset below drain (i.e. gate is at drain_y - 0.75)

CHANNELS = [
    # (Q, R_series, R_pulldown, D, LED, GPIO_label, PWM_label)
    ('Q1', 'R1', 'R4', 'D1', 'LED1', 'GPIO25', 'PWM1'),
    ('Q2', 'R2', 'R5', 'D2', 'LED2', 'GPIO26', 'PWM2'),
    ('Q3', 'R3', 'R6', 'D3', 'LED3', 'GPIO27', 'PWM3'),
]


def draw_channel(d, x_c, q_name, rs, rp, d_name, led_name, gpio_lbl, pwm_lbl):
    """
    Draw one MOSFET switching channel centred at x_c.

    Vertical stack (top → bottom):
      "12V" net label
          |  (wire, 1 unit)
          |  ← LED strip label (on wire)
          |  (wire)
      drain junction  (also D_flyback anode)
      [NFet Q]
      source
          |
         GND

    Gate network (extends to the right from NFet gate stub):
      gate ─ wire ─ junction ─ R_series ─ "PWMn" net label
                    |
                  R_pulldown
                    |
                   GND
    """
    drain_y  = CH_DRAIN_Y
    top_y    = drain_y + CH_LOAD_H      # 12 V net label y
    source_y = drain_y - NFET_DS_H      # source y
    gate_x   = x_c + NFET_GATE_X       # gate x
    gate_y   = drain_y - NFET_GATE_DY  # gate y

    # ── 12 V net label at top ────────────────────────────────────────────────
    d.add(elm.Label().at((x_c, top_y)).label('12 V', loc='top').color(C12))

    # ── Wire from 12 V down through LED strip to drain ───────────────────────
    d.add(elm.Line().at((x_c, top_y)).down().length(0.5).color(C12))
    # LED strip section (labelled wire)
    d.add(elm.Line().down().length(2.0)
          .label(f'{led_name}\n(12 V LED strip)', loc='right').color(CDRN))
    d.add(elm.Line().down().length(1.0).color(CDRN))   # wire to drain

    drain_junc = d.add(elm.Dot().color(CDRN))           # drain junction dot

    # ── NFet (drain at drain_y) ──────────────────────────────────────────────
    q = d.add(elm.NFet().at((x_c, drain_y))
              .label(f'{q_name}\nIRLZ44N', loc='right').color(CBLK))

    # ── Source → GND ─────────────────────────────────────────────────────────
    d.add(elm.Line().at(q.source).down().length(0.6).color(CGND))
    d.add(elm.Ground().color(CGND))

    # ── Gate network ─────────────────────────────────────────────────────────
    # Short stub already part of NFet symbol; connect at q.gate
    d.add(elm.Line().at(q.gate).right().length(0.5).color(CPWM))
    gate_junc = d.add(elm.Dot().color(CPWM))

    # R_pulldown (10 kΩ) from junction to GND
    d.push()
    d.add(elm.Resistor()
          .at(gate_junc.start).down().length(UNIT)
          .label(f'{rp}\n10 kΩ', loc='right').color(CGND))
    d.add(elm.Ground().color(CGND))
    d.pop()

    # R_series (100 Ω) from junction going right → PWM net label
    d.add(elm.Resistor()
          .at(gate_junc.start).right().length(UNIT)
          .label(f'{rs}\n100 Ω', loc='top').color(CPWM))
    d.add(elm.Label()
          .label(f'{pwm_lbl}\n({gpio_lbl})', loc='right')
          .color(CPWM))

    # ── Flyback diode  D1–D3  (1N4007) ──────────────────────────────────────
    # Anode at drain, cathode at 12 V — drawn to the LEFT of the LED path
    diode_x = x_c - 1.2   # offset left to avoid overlap with LED strip
    d.add(elm.Line().at(drain_junc.start)
          .left().length(1.2).color(CDRN))                  # drain → left node
    d.add(elm.Diode()
          .up().length(CH_LOAD_H)
          .label(f'{d_name}\n1N4007', loc='left').color(CDRN))   # anode↑→cathode
    d.add(elm.Label().label('12 V', loc='top').color(C12))   # net label at cathode


# ══════════════════════════════════════════════════════════════════════════════
# MAIN DRAWING
# ══════════════════════════════════════════════════════════════════════════════
def main():
    with schemdraw.Drawing(fontsize=9, show=False) as d:
        d.config(unit=UNIT)

        # Section 1: power
        v33_node = draw_power_section(d)

        # Section 2: ESP32
        draw_esp32(d, v33_node)

        # Section 3: three MOSFET channels
        for x_c, (q, rs, rp, dn, ln, gp, pm) in zip(CH_X, CHANNELS):
            draw_channel(d, x_c, q, rs, rp, dn, ln, gp, pm)

        d.save('schematic.svg')
        d.save('schematic.png', dpi=300)
        print("Saved: schematic.svg  schematic.png")


if __name__ == '__main__':
    main()
