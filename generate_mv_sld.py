#!/usr/bin/env python3
"""
MV SLD Component SVG Generator
================================
Individual, standalone SVG building blocks for a Medium Voltage
Single Line Diagram (SLD) / Power Management Screen.

Color coding per spec:
  Running/Closed/Energized = Red (#ef4444 / #dc2626)
  Stopped/Open/Deenergized = Green (#22c55e / #15803d)
  Starting/Synchronizing   = Blue (#3b82f6 / #1d4ed8)
  Stopping/Alarm           = Yellow blink (#eab308)

Palette based on VoltaGrid / Tailwind Slate dark theme.
"""

import os, math
import xml.etree.ElementTree as ET
from xml.dom import minidom

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "mv_sld")
os.makedirs(OUT, exist_ok=True)

NS = "http://www.w3.org/2000/svg"

# ── VoltaGrid Palette ─────────────────────────────────────────────────────────
SLATE_950 = "#020617"
SLATE_900 = "#0f172a"
SLATE_850 = "#1e2533"
SLATE_800 = "#1e293b"
SLATE_700 = "#334155"
GRAY_400  = "#9CA3AF"
GRAY_500  = "#6b7280"
GRAY_600  = "#4b5563"

RED_400   = "#f87171"
RED_500   = "#ef4444"
RED_600   = "#dc2626"
RED_700   = "#991b1c"

GREEN_400 = "#4ade80"
GREEN_500 = "#22c55e"
GREEN_600 = "#65a30d"
GREEN_700 = "#15803d"
GREEN_800 = "#166534"

BLUE_400  = "#60a5fa"
BLUE_500  = "#3b82f6"
BLUE_700  = "#1d4ed8"

YELLOW_500 = "#eab308"
YELLOW_600 = "#ca8a04"

EMERALD_700 = "#047857"
EMERALD_800 = "#065f46"

WHITE     = "#f0f0f0"
WIRE      = "#60a5fa"  # blue-400 for connection wires


# ── Helpers ───────────────────────────────────────────────────────────────────

def svg(w, h):
    ET.register_namespace("", NS)
    return ET.Element("svg", {"xmlns": NS, "width": str(w), "height": str(h),
                               "viewBox": f"0 0 {w} {h}"})

def de(parent, tag="defs"):
    return ET.SubElement(parent, tag)

def el(parent, tag, **kw):
    a = {}
    for k, v in kw.items():
        key = k.replace("__", ":").replace("_", "-") if len(k) > 2 and k not in (
            "d", "id", "r", "x", "y", "cx", "cy", "rx", "ry",
            "x1", "y1", "x2", "y2", "fx", "fy", "dx", "dy") else k
        a[key] = str(v)
    return ET.SubElement(parent, tag, a)

def txt(parent, x, y, content, **kw):
    t = el(parent, "text", x=x, y=y, **kw)
    t.text = content
    return t

def lg(defs, gid, c1, c2, x1="0%", y1="0%", x2="0%", y2="100%"):
    g = el(defs, "linearGradient", id=gid, x1=x1, y1=y1, x2=x2, y2=y2)
    el(g, "stop", offset="0%", style=f"stop-color:{c1}")
    el(g, "stop", offset="100%", style=f"stop-color:{c2}")

def rg(defs, gid, c_inner, c_outer):
    g = el(defs, "radialGradient", id=gid, cx="50%", cy="50%", r="50%")
    el(g, "stop", offset="0%", style=f"stop-color:{c_inner}")
    el(g, "stop", offset="100%", style=f"stop-color:{c_outer}")

def glow(defs, fid, color, sd=3):
    f = el(defs, "filter", id=fid, x="-50%", y="-50%", width="200%", height="200%")
    el(f, "feGaussianBlur", **{"in": "SourceGraphic", "stdDeviation": str(sd), "result": "b"})
    el(f, "feFlood", **{"flood-color": color, "flood-opacity": "0.5", "result": "c"})
    el(f, "feComposite", **{"in": "c", "in2": "b", "operator": "in", "result": "s"})
    m = el(f, "feMerge")
    el(m, "feMergeNode", **{"in": "s"})
    el(m, "feMergeNode", **{"in": "SourceGraphic"})

def save(s, name):
    rough = ET.tostring(s, encoding="unicode")
    parsed = minidom.parseString(rough)
    pretty = parsed.toprettyxml(indent="  ")
    lines = pretty.split("\n")
    if lines[0].startswith("<?xml"):
        lines = lines[1:]
    fp = os.path.join(OUT, name)
    with open(fp, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  [OK] {name}")

FONT = "'Inter', 'Segoe UI', sans-serif"
MONO = "'JetBrains Mono', Consolas, monospace"


# ═══════════════════════════════════════════════════════════════════════════════
#  1. GENERATOR (GENSET) SYMBOL
# ═══════════════════════════════════════════════════════════════════════════════
def gen_genset(state="running"):
    """
    Standard IEC generator symbol: circle with 'G' inside.
    States: running (red), stopped (green), starting (blue)
    """
    S = 80
    s = svg(S, S)
    d = de(s)

    colors = {
        "running":  (RED_500, RED_600, RED_400),
        "stopped":  (GREEN_500, GREEN_700, GREEN_400),
        "starting": (BLUE_500, BLUE_700, BLUE_400),
    }
    c_fill, c_dark, c_light = colors[state]

    lg(d, "genBg", SLATE_800, SLATE_900)
    lg(d, "genRing", c_light, c_dark)
    glow(d, "genGlow", c_fill, 4)

    cx, cy, r = 40, 44, 28

    # Outer housing (rounded rect background)
    el(s, "rect", x=4, y=8, width=72, height=68, rx=10, ry=10,
       fill=f"url(#genBg)", stroke=SLATE_700, stroke_width="1")

    # Connection stub (top - to busbar)
    el(s, "line", x1=cx, y1=0, x2=cx, y2=cy - r,
       stroke=WIRE, stroke_width="2.5", stroke_linecap="round")

    # Generator circle
    el(s, "circle", cx=cx, cy=cy, r=r,
       fill="none", stroke=f"url(#genRing)", stroke_width="3",
       filter="url(#genGlow)")

    # Inner fill
    el(s, "circle", cx=cx, cy=cy, r=f"{r - 6}",
       fill=c_fill, opacity="0.15")

    # "G" letter
    txt(s, cx, cy + 1, "G",
        fill=c_light, font_family=FONT, font_size="22", font_weight="700",
        text_anchor="middle", dominant_baseline="middle")

    # Small status bar at bottom
    el(s, "rect", x=20, y=74, width=40, height=3, rx=1.5, ry=1.5,
       fill=c_fill, opacity="0.8")

    suffix = {"running": "closed", "stopped": "open", "starting": "sync"}[state]
    save(s, f"genset_{suffix}.svg")


# ═══════════════════════════════════════════════════════════════════════════════
#  2. DER (Distributed Energy Resource) SYMBOL
# ═══════════════════════════════════════════════════════════════════════════════
def gen_der(state="running"):
    S = 80
    s = svg(S, S)
    d = de(s)

    colors = {
        "running":  (RED_500, RED_600, RED_400),
        "stopped":  (GREEN_500, GREEN_700, GREEN_400),
        "starting": (BLUE_500, BLUE_700, BLUE_400),
    }
    c_fill, c_dark, c_light = colors[state]

    lg(d, "derBg", SLATE_800, SLATE_900)
    lg(d, "derRing", c_light, c_dark)
    glow(d, "derGlow", c_fill, 4)

    cx, cy, r = 40, 44, 28

    el(s, "rect", x=4, y=8, width=72, height=68, rx=10, ry=10,
       fill=f"url(#derBg)", stroke=SLATE_700, stroke_width="1")

    # Connection stub top
    el(s, "line", x1=cx, y1=0, x2=cx, y2=cy - r,
       stroke=WIRE, stroke_width="2.5", stroke_linecap="round")

    # DER circle with sine wave
    el(s, "circle", cx=cx, cy=cy, r=r,
       fill="none", stroke=f"url(#derRing)", stroke_width="3",
       filter="url(#derGlow)")
    el(s, "circle", cx=cx, cy=cy, r=f"{r-6}", fill=c_fill, opacity="0.12")

    # Sine wave inside (~)
    el(s, "path",
       d=f"M{cx-14},{cy} Q{cx-7},{cy-12} {cx},{cy} Q{cx+7},{cy+12} {cx+14},{cy}",
       fill="none", stroke=c_light, stroke_width="2.5", stroke_linecap="round")

    el(s, "rect", x=20, y=74, width=40, height=3, rx=1.5, ry=1.5,
       fill=c_fill, opacity="0.8")

    suffix = {"running": "closed", "stopped": "open", "starting": "sync"}[state]
    save(s, f"der_{suffix}.svg")


# ═══════════════════════════════════════════════════════════════════════════════
#  3. CIRCUIT BREAKER (GCB / ICB / FCB)
# ═══════════════════════════════════════════════════════════════════════════════
def gen_breaker(state="closed", label="CB"):
    """
    Circuit breaker: square symbol with state color.
    closed=Red, open=Green, sync=Blue
    """
    W, H = 48, 72
    s = svg(W, H)
    d = de(s)

    colors = {
        "closed": (RED_500, RED_600, RED_400, "#closed"),
        "open":   (GREEN_500, GREEN_700, GREEN_400, "#open"),
        "sync":   (BLUE_500, BLUE_700, BLUE_400, "#sync"),
    }
    c_fill, c_dark, c_light, _ = colors[state]

    lg(d, "cbGrad", c_light, c_dark)
    glow(d, "cbGlow", c_fill, 3)

    cx = W // 2

    # Top wire
    el(s, "line", x1=cx, y1=0, x2=cx, y2=18,
       stroke=WIRE, stroke_width="2.5", stroke_linecap="round")

    # Breaker body
    bw, bh = 32, 32
    bx = cx - bw // 2
    by = 20
    el(s, "rect", x=bx, y=by, width=bw, height=bh, rx=6, ry=6,
       fill=f"url(#cbGrad)", filter="url(#cbGlow)",
       stroke=c_light, stroke_width="0.8")

    # State icon inside
    if state == "closed":
        # Horizontal line (closed contact)
        el(s, "line", x1=cx - 9, y1=by + bh // 2, x2=cx + 9, y2=by + bh // 2,
           stroke="white", stroke_width="2.5", stroke_linecap="round")
    elif state == "open":
        # X mark (open contact)
        off = 7
        el(s, "line", x1=cx - off, y1=by + bh // 2 - off, x2=cx + off, y2=by + bh // 2 + off,
           stroke="white", stroke_width="2", stroke_linecap="round")
        el(s, "line", x1=cx + off, y1=by + bh // 2 - off, x2=cx - off, y2=by + bh // 2 + off,
           stroke="white", stroke_width="2", stroke_linecap="round")
    else:
        # Sync arrows (rotating)
        el(s, "path",
           d=f"M{cx+6},{by+10} A8,8 0 1 0 {cx+8},{by+bh//2+2}",
           fill="none", stroke="white", stroke_width="2", stroke_linecap="round")
        el(s, "path", d=f"M{cx+4},{by+7} L{cx+7},{by+11} L{cx+10},{by+8}",
           fill="none", stroke="white", stroke_width="1.5", stroke_linecap="round",
           stroke_linejoin="round")

    # Bottom wire
    el(s, "line", x1=cx, y1=by + bh, x2=cx, y2=H,
       stroke=WIRE, stroke_width="2.5", stroke_linecap="round")

    save(s, f"breaker_{state}.svg")


# ═══════════════════════════════════════════════════════════════════════════════
#  4. TRANSFORMER (XFMR)
# ═══════════════════════════════════════════════════════════════════════════════
def gen_transformer(state="energized"):
    """IEC transformer: two overlapping circles."""
    W, H = 64, 100
    s = svg(W, H)
    d = de(s)

    colors = {
        "energized":   (RED_500, RED_600, RED_400),
        "deenergized": (GREEN_500, GREEN_700, GREEN_400),
    }
    c_fill, c_dark, c_light = colors[state]

    lg(d, "xfBg", SLATE_800, SLATE_900)
    glow(d, "xfGlow", c_fill, 3)

    cx = W // 2

    # Housing
    el(s, "rect", x=4, y=14, width=56, height=74, rx=8, ry=8,
       fill="url(#xfBg)", stroke=SLATE_700, stroke_width="1")

    # Top wire
    el(s, "line", x1=cx, y1=0, x2=cx, y2=28,
       stroke=WIRE, stroke_width="2.5", stroke_linecap="round")

    # Top coil
    el(s, "circle", cx=cx, cy=40, r=14,
       fill="none", stroke=c_light, stroke_width="2.5", filter="url(#xfGlow)")

    # Bottom coil
    el(s, "circle", cx=cx, cy=60, r=14,
       fill="none", stroke=c_light, stroke_width="2.5", filter="url(#xfGlow)")

    # Bottom wire
    el(s, "line", x1=cx, y1=74, x2=cx, y2=100,
       stroke=WIRE, stroke_width="2.5", stroke_linecap="round")

    # Voltage ratio text
    txt(s, cx, 94, "MV", fill=GRAY_400, font_family=MONO, font_size="8",
        text_anchor="middle", font_weight="600")

    suffix = "closed" if state == "energized" else "open"
    save(s, f"transformer_{suffix}.svg")


# ═══════════════════════════════════════════════════════════════════════════════
#  5. SWITCHGEAR (SWGR) BUS SECTION
# ═══════════════════════════════════════════════════════════════════════════════
def gen_switchgear():
    """Switchgear panel represented as a labeled section marker."""
    W, H = 120, 40
    s = svg(W, H)
    d = de(s)

    lg(d, "swBg", SLATE_800, SLATE_900)

    el(s, "rect", x=0, y=0, width=W, height=H, rx=8, ry=8,
       fill="url(#swBg)", stroke=SLATE_700, stroke_width="1")

    # Accent stripe
    el(s, "rect", x=0, y=0, width=4, height=H, rx=2, ry=0,
       fill=BLUE_500)

    txt(s, 14, 16, "MV SWGR", fill=GRAY_400, font_family=MONO, font_size="9",
        font_weight="600")
    txt(s, 14, 30, "SECTION A", fill=WHITE, font_family=FONT, font_size="12",
        font_weight="700")

    save(s, "switchgear_label.svg")


# ═══════════════════════════════════════════════════════════════════════════════
#  6. BUSBAR SEGMENTS
# ═══════════════════════════════════════════════════════════════════════════════
def gen_busbar_h(state="energized"):
    """Horizontal busbar segment with modern gradient."""
    W, H = 300, 16
    s = svg(W, H)
    d = de(s)

    if state == "energized":
        lg(d, "busG", RED_500, RED_600, x1="0%", y1="0%", x2="0%", y2="100%")
        glow(d, "busGlow", RED_500, 4)
        sc = RED_400
    else:
        lg(d, "busG", GREEN_500, GREEN_700, x1="0%", y1="0%", x2="0%", y2="100%")
        glow(d, "busGlow", GREEN_500, 4)
        sc = GREEN_400

    # Main bar
    el(s, "rect", x=0, y=3, width=W, height=10, rx=2, ry=2,
       fill="url(#busG)", filter="url(#busGlow)", stroke=sc, stroke_width="0.5")

    # Highlight stripe
    el(s, "rect", x=0, y=3, width=W, height=2, rx=1, ry=1,
       fill="white", opacity="0.12")

    suffix = "energized" if state == "energized" else "deenergized"
    save(s, f"busbar_h_{suffix}.svg")


def gen_busbar_v(state="energized"):
    """Vertical busbar segment."""
    W, H = 16, 300
    s = svg(W, H)
    d = de(s)

    if state == "energized":
        lg(d, "busG", RED_500, RED_600, x1="0%", y1="0%", x2="100%", y2="0%")
        glow(d, "busGlow", RED_500, 4)
        sc = RED_400
    else:
        lg(d, "busG", GREEN_500, GREEN_700, x1="0%", y1="0%", x2="100%", y2="0%")
        glow(d, "busGlow", GREEN_500, 4)
        sc = GREEN_400

    el(s, "rect", x=3, y=0, width=10, height=H, rx=2, ry=2,
       fill="url(#busG)", filter="url(#busGlow)", stroke=sc, stroke_width="0.5")
    el(s, "rect", x=3, y=0, width=2, height=H, rx=1, ry=1,
       fill="white", opacity="0.12")

    suffix = "energized" if state == "energized" else "deenergized"
    save(s, f"busbar_v_{suffix}.svg")


def gen_bus_tee():
    """T-junction piece for busbar connections (horizontal bus with vertical drop)."""
    S = 40
    s = svg(S, S)
    d = de(s)
    lg(d, "teeG", RED_500, RED_600, x1="0%", y1="0%", x2="0%", y2="100%")
    glow(d, "teeGlow", RED_500, 3)

    # Horizontal bar
    el(s, "rect", x=0, y=3, width=S, height=10, rx=2, ry=2,
       fill="url(#teeG)", filter="url(#teeGlow)", stroke=RED_400, stroke_width="0.5")

    # Vertical drop
    el(s, "rect", x=15, y=8, width=10, height=32, rx=2, ry=2,
       fill="url(#teeG)", filter="url(#teeGlow)", stroke=RED_400, stroke_width="0.5")

    save(s, "bus_tee.svg")


# ═══════════════════════════════════════════════════════════════════════════════
#  7. OPERATING MODE INDICATORS
# ═══════════════════════════════════════════════════════════════════════════════
def gen_mode_blocked():
    """Green square = Blocked mode."""
    S = 28
    s = svg(S, S)
    d = de(s)
    glow(d, "mGlow", GREEN_500, 2)

    el(s, "rect", x=4, y=4, width=20, height=20, rx=4, ry=4,
       fill=GREEN_500, stroke=GREEN_400, stroke_width="1", filter="url(#mGlow)")

    save(s, "mode_blocked.svg")


def gen_mode_auto():
    """Green play arrow = Auto mode."""
    S = 28
    s = svg(S, S)
    d = de(s)
    glow(d, "mGlow", GREEN_500, 2)

    # Play triangle
    el(s, "path", d="M8,4 L24,14 L8,24 Z",
       fill=GREEN_500, stroke=GREEN_400, stroke_width="1", filter="url(#mGlow)")

    save(s, "mode_auto.svg")


def gen_mode_manual():
    """Green circle = Manual mode."""
    S = 28
    s = svg(S, S)
    d = de(s)
    glow(d, "mGlow", GREEN_500, 2)

    el(s, "circle", cx=14, cy=14, r=10,
       fill=GREEN_500, stroke=GREEN_400, stroke_width="1", filter="url(#mGlow)")

    save(s, "mode_manual.svg")


def gen_mode_alarm():
    """Blinking yellow variants of each mode shape."""
    S = 28
    for shape, name, draw_fn in [
        ("square", "alarm_blocked", lambda s2: el(s2, "rect", x=4, y=4, width=20, height=20, rx=4, ry=4,
            fill=YELLOW_500, stroke=YELLOW_600, stroke_width="1", filter="url(#mGlow)")),
        ("play", "alarm_auto", lambda s2: el(s2, "path", d="M8,4 L24,14 L8,24 Z",
            fill=YELLOW_500, stroke=YELLOW_600, stroke_width="1", filter="url(#mGlow)")),
        ("circle", "alarm_manual", lambda s2: el(s2, "circle", cx=14, cy=14, r=10,
            fill=YELLOW_500, stroke=YELLOW_600, stroke_width="1", filter="url(#mGlow)")),
    ]:
        s2 = svg(S, S)
        d2 = de(s2)
        glow(d2, "mGlow", YELLOW_500, 3)

        # Add CSS blink animation
        style = el(d2, "style")
        style.text = "@keyframes blink{0%,100%{opacity:1}50%{opacity:0.2}} .blink{animation:blink 1s infinite}"

        g = el(s2, "g")
        g.set("class", "blink")
        # Re-draw inside group
        if shape == "square":
            el(g, "rect", x=4, y=4, width=20, height=20, rx=4, ry=4,
               fill=YELLOW_500, stroke=YELLOW_600, stroke_width="1", filter="url(#mGlow)")
        elif shape == "play":
            el(g, "path", d="M8,4 L24,14 L8,24 Z",
               fill=YELLOW_500, stroke=YELLOW_600, stroke_width="1", filter="url(#mGlow)")
        else:
            el(g, "circle", cx=14, cy=14, r=10,
               fill=YELLOW_500, stroke=YELLOW_600, stroke_width="1", filter="url(#mGlow)")

        save(s2, f"mode_{name}.svg")


# ═══════════════════════════════════════════════════════════════════════════════
#  8. TELEMETRY READOUT PANEL
# ═══════════════════════════════════════════════════════════════════════════════
def gen_telemetry_panel():
    """Compact readout panel showing P, Q, V, F values."""
    W, H = 140, 100
    s = svg(W, H)
    d = de(s)
    lg(d, "panBg", SLATE_800, SLATE_900)

    # Card
    el(s, "rect", x=0, y=0, width=W, height=H, rx=8, ry=8,
       fill="url(#panBg)", stroke=SLATE_700, stroke_width="1")

    readings = [
        ("P", "402.5", "kW",  BLUE_400),
        ("Q", "120.8", "kVAr", GREEN_400),
        ("V", "13.8",  "kV",  RED_400),
        ("F", "60.0",  "Hz",  YELLOW_500),
    ]

    for i, (label, val, unit, color) in enumerate(readings):
        ry = 18 + i * 21

        # Label
        txt(s, 12, ry, label, fill=GRAY_500, font_family=MONO,
            font_size="10", font_weight="700")

        # Value
        txt(s, 80, ry, val, fill=color, font_family=MONO,
            font_size="12", font_weight="700", text_anchor="end")

        # Unit
        txt(s, 86, ry, unit, fill=GRAY_500, font_family=MONO,
            font_size="9")

        # Separator line
        if i < len(readings) - 1:
            el(s, "line", x1=10, y1=ry + 7, x2=W - 10, y2=ry + 7,
               stroke=SLATE_700, stroke_width="0.5")

    save(s, "telemetry_panel.svg")


# ═══════════════════════════════════════════════════════════════════════════════
#  9. ALARM BANNER
# ═══════════════════════════════════════════════════════════════════════════════
def gen_alarm_banner():
    """Top alarm banner component."""
    W, H = 400, 40
    s = svg(W, H)
    d = de(s)
    lg(d, "alBg", SLATE_850, SLATE_900)
    glow(d, "alGlow", YELLOW_500, 2)

    # Banner body
    el(s, "rect", x=0, y=0, width=W, height=H, rx=8, ry=8,
       fill="url(#alBg)", stroke=SLATE_700, stroke_width="1")

    # Warning icon (triangle)
    el(s, "path", d="M18,8 L28,28 L8,28 Z",
       fill="none", stroke=YELLOW_500, stroke_width="1.5",
       stroke_linejoin="round", filter="url(#alGlow)")
    txt(s, 18, 25, "!", fill=YELLOW_500, font_family=FONT, font_size="12",
        font_weight="800", text_anchor="middle")

    # Alarm text
    txt(s, 40, 18, "MOST RECENT ALARM", fill=GRAY_500, font_family=MONO,
        font_size="8", font_weight="600", letter_spacing="1")
    txt(s, 40, 32, "GEN-01 Overcurrent Trip", fill=YELLOW_500, font_family=FONT,
        font_size="12", font_weight="600")

    # ACK button
    el(s, "rect", x=W - 100, y=8, width=60, height=24, rx=6, ry=6,
       fill=EMERALD_700, stroke=EMERALD_800, stroke_width="1")
    txt(s, W - 70, 24, "ACK", fill=WHITE, font_family=MONO,
        font_size="10", font_weight="700", text_anchor="middle")

    # Expand arrow
    el(s, "path", d=f"M{W - 20},{16} L{W - 14},{22} L{W - 8},{16}",
       fill="none", stroke=GRAY_400, stroke_width="1.5",
       stroke_linecap="round", stroke_linejoin="round")

    save(s, "alarm_banner.svg")


# ═══════════════════════════════════════════════════════════════════════════════
#  10. NAVIGATION BUTTON
# ═══════════════════════════════════════════════════════════════════════════════
def gen_nav_button(label="MV PMS", active=False):
    """Single nav bar button."""
    W, H = 100, 36
    s = svg(W, H)
    d = de(s)

    if active:
        lg(d, "navBg", BLUE_700, BLUE_500)
        text_color = WHITE
        stroke_c = BLUE_400
    else:
        lg(d, "navBg", SLATE_800, SLATE_900)
        text_color = GRAY_400
        stroke_c = SLATE_700

    el(s, "rect", x=0, y=0, width=W, height=H, rx=8, ry=8,
       fill="url(#navBg)", stroke=stroke_c, stroke_width="1")

    txt(s, W // 2, H // 2 + 1, label, fill=text_color, font_family=FONT,
        font_size="11", font_weight="600", text_anchor="middle",
        dominant_baseline="middle")

    suffix = "active" if active else "inactive"
    # Sanitize label for filename
    fn_label = label.lower().replace(" ", "_").replace("/", "_")
    save(s, f"nav_{fn_label}_{suffix}.svg")


# ═══════════════════════════════════════════════════════════════════════════════
#  11. WIRE / CONNECTION LINE SEGMENTS
# ═══════════════════════════════════════════════════════════════════════════════
def gen_wire_h():
    """Horizontal wire segment."""
    W, H = 120, 8
    s = svg(W, H)
    el(s, "line", x1=0, y1=4, x2=W, y2=4,
       stroke=WIRE, stroke_width="2.5", stroke_linecap="round")
    save(s, "wire_horizontal.svg")


def gen_wire_v():
    """Vertical wire segment."""
    W, H = 8, 120
    s = svg(W, H)
    el(s, "line", x1=4, y1=0, x2=4, y2=H,
       stroke=WIRE, stroke_width="2.5", stroke_linecap="round")
    save(s, "wire_vertical.svg")


def gen_wire_elbow():
    """L-shaped wire corner."""
    S = 24
    s = svg(S, S)
    el(s, "path", d=f"M{S//2},0 L{S//2},{S//2} L{S},{S//2}",
       fill="none", stroke=WIRE, stroke_width="2.5",
       stroke_linecap="round", stroke_linejoin="round")
    save(s, "wire_elbow.svg")


# ═══════════════════════════════════════════════════════════════════════════════
#  12. GROUND SYMBOL
# ═══════════════════════════════════════════════════════════════════════════════
def gen_ground():
    S = 32
    s = svg(S, S)
    cx = S // 2

    el(s, "line", x1=cx, y1=0, x2=cx, y2=14,
       stroke=WIRE, stroke_width="2.5", stroke_linecap="round")
    # Three horizontal lines, decreasing width
    for i, (w, y) in enumerate([(20, 14), (14, 20), (8, 26)]):
        el(s, "line", x1=cx - w // 2, y1=y, x2=cx + w // 2, y2=y,
           stroke=WIRE, stroke_width="2", stroke_linecap="round")

    save(s, "ground.svg")


# ═══════════════════════════════════════════════════════════════════════════════
#  13. METER / PT SYMBOL
# ═══════════════════════════════════════════════════════════════════════════════
def gen_meter():
    """Potential transformer / metering point."""
    W, H = 36, 48
    s = svg(W, H)
    d = de(s)
    glow(d, "mtGlow", BLUE_400, 2)
    cx = W // 2

    el(s, "line", x1=cx, y1=0, x2=cx, y2=12,
       stroke=WIRE, stroke_width="2", stroke_linecap="round")

    el(s, "circle", cx=cx, cy=24, r=12,
       fill="none", stroke=BLUE_400, stroke_width="2", filter="url(#mtGlow)")

    txt(s, cx, 28, "V", fill=BLUE_400, font_family=MONO, font_size="12",
        font_weight="700", text_anchor="middle")

    el(s, "line", x1=cx, y1=36, x2=cx, y2=48,
       stroke=WIRE, stroke_width="2", stroke_linecap="round")

    save(s, "meter_vt.svg")


# ═══════════════════════════════════════════════════════════════════════════════
#  14. CT (Current Transformer) SYMBOL
# ═══════════════════════════════════════════════════════════════════════════════
def gen_ct():
    W, H = 28, 48
    s = svg(W, H)
    d = de(s)
    glow(d, "ctGlow", BLUE_400, 2)
    cx = W // 2

    el(s, "line", x1=cx, y1=0, x2=cx, y2=14,
       stroke=WIRE, stroke_width="2", stroke_linecap="round")

    el(s, "circle", cx=cx, cy=20, r=7,
       fill="none", stroke=BLUE_400, stroke_width="1.5", filter="url(#ctGlow)")
    el(s, "circle", cx=cx, cy=28, r=7,
       fill="none", stroke=BLUE_400, stroke_width="1.5", filter="url(#ctGlow)")

    el(s, "line", x1=cx, y1=35, x2=cx, y2=48,
       stroke=WIRE, stroke_width="2", stroke_linecap="round")

    save(s, "ct.svg")


# ═══════════════════════════════════════════════════════════════════════════════
#  15. STATUS BADGE (Running/Stopped/etc.)
# ═══════════════════════════════════════════════════════════════════════════════
def gen_status_badge(state="running"):
    W, H = 80, 24
    s = svg(W, H)
    d = de(s)

    labels_colors = {
        "running":  ("RUNNING",  RED_500,    RED_600),
        "stopped":  ("STOPPED",  GREEN_500,  GREEN_700),
        "starting": ("SYNCING",  BLUE_500,   BLUE_700),
        "alarm":    ("ALARM",    YELLOW_500, YELLOW_600),
    }
    label_text, c_fill, c_dark = labels_colors[state]

    if state == "alarm":
        glow(d, "badgeGlow", YELLOW_500, 2)
        style = el(d, "style")
        style.text = "@keyframes blink{0%,100%{opacity:1}50%{opacity:0.3}} .blink{animation:blink 0.8s infinite}"

    el(s, "rect", x=0, y=0, width=W, height=H, rx=12, ry=12,
       fill=SLATE_900, stroke=c_fill, stroke_width="1")

    # Dot
    dot_g = el(s, "g")
    if state == "alarm":
        dot_g.set("class", "blink")
        el(dot_g, "circle", cx=14, cy=12, r=4, fill=c_fill, filter="url(#badgeGlow)")
    else:
        el(dot_g, "circle", cx=14, cy=12, r=4, fill=c_fill)

    txt(s, 24, 16, label_text, fill=c_fill, font_family=MONO,
        font_size="9", font_weight="700")

    save(s, f"status_{state}.svg")


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("  MV SLD COMPONENT GENERATOR")
    print("  VoltaGrid palette / modern gradient style")
    print("=" * 60)
    print()

    tasks = [
        # Gensets (3 states)
        ("Genset - Running/Closed",  lambda: gen_genset("running")),
        ("Genset - Stopped/Open",    lambda: gen_genset("stopped")),
        ("Genset - Starting/Sync",   lambda: gen_genset("starting")),
        # DERs (3 states)
        ("DER - Running/Closed",     lambda: gen_der("running")),
        ("DER - Stopped/Open",       lambda: gen_der("stopped")),
        ("DER - Starting/Sync",      lambda: gen_der("starting")),
        # Breakers (3 states)
        ("Breaker - Closed (Red)",   lambda: gen_breaker("closed")),
        ("Breaker - Open (Green)",   lambda: gen_breaker("open")),
        ("Breaker - Sync (Blue)",    lambda: gen_breaker("sync")),
        # Transformer
        ("Transformer - Energized",  lambda: gen_transformer("energized")),
        ("Transformer - Deenergized",lambda: gen_transformer("deenergized")),
        # Switchgear
        ("Switchgear Label",         gen_switchgear),
        # Busbars
        ("Busbar H - Energized",     lambda: gen_busbar_h("energized")),
        ("Busbar H - Deenergized",   lambda: gen_busbar_h("deenergized")),
        ("Busbar V - Energized",     lambda: gen_busbar_v("energized")),
        ("Busbar V - Deenergized",   lambda: gen_busbar_v("deenergized")),
        ("Bus T-Junction",           gen_bus_tee),
        # Mode indicators
        ("Mode - Blocked",           gen_mode_blocked),
        ("Mode - Auto",              gen_mode_auto),
        ("Mode - Manual",            gen_mode_manual),
        ("Mode - Alarm (blink)",     gen_mode_alarm),
        # Telemetry
        ("Telemetry Panel",          gen_telemetry_panel),
        # Alarm banner
        ("Alarm Banner",             gen_alarm_banner),
        # Nav buttons
        ("Nav - MV PMS (active)",    lambda: gen_nav_button("MV PMS", True)),
        ("Nav - LV PMS",             lambda: gen_nav_button("LV PMS", False)),
        ("Nav - Alarms",             lambda: gen_nav_button("Alarms", False)),
        ("Nav - Trending",           lambda: gen_nav_button("Trending", False)),
        # Wires
        ("Wire - Horizontal",        gen_wire_h),
        ("Wire - Vertical",          gen_wire_v),
        ("Wire - Elbow",             gen_wire_elbow),
        # Misc symbols
        ("Ground Symbol",            gen_ground),
        ("Meter (VT)",               gen_meter),
        ("CT Symbol",                gen_ct),
        # Status badges
        ("Status - Running",         lambda: gen_status_badge("running")),
        ("Status - Stopped",         lambda: gen_status_badge("stopped")),
        ("Status - Syncing",         lambda: gen_status_badge("starting")),
        ("Status - Alarm",           lambda: gen_status_badge("alarm")),
    ]

    for name, fn in tasks:
        print(f"  {name}...")
        fn()

    print()
    print(f"  {len(tasks)} components => {OUT}")
    print("=" * 60)
