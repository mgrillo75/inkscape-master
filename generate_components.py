#!/usr/bin/env python3
"""
Individual SVG Component Generator
===================================
Generates standalone, modular SVG widgets inspired by modern dark-theme
SCADA/dashboard UIs. Each SVG is a single reusable component.
"""

import os
import math
import xml.etree.ElementTree as ET
from xml.dom import minidom

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "components")
os.makedirs(OUTPUT_DIR, exist_ok=True)

SVG_NS = "http://www.w3.org/2000/svg"

def new_svg(width, height):
    ET.register_namespace("", SVG_NS)
    svg = ET.Element("svg", {
        "xmlns": SVG_NS,
        "width": str(width),
        "height": str(height),
        "viewBox": f"0 0 {width} {height}",
    })
    return svg

def defs(svg):
    return ET.SubElement(svg, "defs")

def el(parent, tag, **attrs):
    """Generic element builder."""
    clean = {}
    for k, v in attrs.items():
        key = k.replace("_", "-") if k not in ("d", "id", "r", "x", "y", "cx", "cy", "rx", "ry", "x1", "y1", "x2", "y2", "fx", "fy", "dx", "dy") else k
        clean[key] = str(v)
    return ET.SubElement(parent, tag, clean)

def save(svg, filename):
    rough = ET.tostring(svg, encoding="unicode")
    parsed = minidom.parseString(rough)
    pretty = parsed.toprettyxml(indent="  ")
    lines = pretty.split("\n")
    if lines[0].startswith("<?xml"):
        lines = lines[1:]
    fp = os.path.join(OUTPUT_DIR, filename)
    with open(fp, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  [OK] {fp}")


# ─────────────────────────────────────────────────────────────────────────────
# 1. CIRCULAR GAUGE / RING PROGRESS
# ─────────────────────────────────────────────────────────────────────────────
def gen_ring_gauge():
    """Single ring gauge with percentage label. Transparent background."""
    S = 140
    svg = new_svg(S, S)
    d = defs(svg)

    # Glow filter
    f = el(d, "filter", id="glow", x="-50%", y="-50%", width="200%", height="200%")
    el(f, "feGaussianBlur", **{"in": "SourceGraphic", "stdDeviation": "3", "result": "b"})
    merge = el(f, "feMerge")
    el(merge, "feMergeNode", **{"in": "b"})
    el(merge, "feMergeNode", **{"in": "SourceGraphic"})

    cx, cy, r = 70, 70, 52
    stroke_w = 8
    pct = 72
    circumference = 2 * math.pi * r
    dash = circumference * pct / 100
    gap = circumference - dash

    # Track ring
    el(svg, "circle", cx=cx, cy=cy, r=r,
       fill="none", stroke="#1a2744", **{"stroke-width": str(stroke_w)})

    # Value arc (rotated -90 to start at top)
    arc = el(svg, "circle", cx=cx, cy=cy, r=r,
             fill="none", stroke="#00b4d8",
             **{"stroke-width": str(stroke_w),
                "stroke-dasharray": f"{dash:.1f} {gap:.1f}",
                "stroke-linecap": "round",
                "transform": f"rotate(-90 {cx} {cy})",
                "filter": "url(#glow)"})

    # Percentage text
    t = el(svg, "text", x=cx, y=cy + 2,
           fill="#e0f7fa", **{"font-family": "'Segoe UI', sans-serif",
                              "font-size": "28", "font-weight": "bold",
                              "text-anchor": "middle",
                              "dominant-baseline": "middle"})
    t.text = f"{pct}%"

    save(svg, "ring_gauge.svg")


# ─────────────────────────────────────────────────────────────────────────────
# 2. RADIAL TICK GAUGE (speedometer style)
# ─────────────────────────────────────────────────────────────────────────────
def gen_radial_tick_gauge():
    """Radial gauge with tick marks around the arc, like the 100% gauge in the reference."""
    S = 160
    svg = new_svg(S, S)
    d = defs(svg)

    f = el(d, "filter", id="glow2", x="-50%", y="-50%", width="200%", height="200%")
    el(f, "feGaussianBlur", **{"in": "SourceGraphic", "stdDeviation": "2.5", "result": "b"})
    m = el(f, "feMerge")
    el(m, "feMergeNode", **{"in": "b"})
    el(m, "feMergeNode", **{"in": "SourceGraphic"})

    cx, cy = 80, 80
    r_outer = 65
    r_inner = 50
    num_ticks = 40
    pct = 100
    active_ticks = int(num_ticks * pct / 100)

    start_angle = 135  # degrees
    sweep = 270

    for i in range(num_ticks):
        angle_deg = start_angle + (sweep * i / (num_ticks - 1))
        angle_rad = math.radians(angle_deg)
        x1 = cx + r_inner * math.cos(angle_rad)
        y1 = cy + r_inner * math.sin(angle_rad)
        x2 = cx + r_outer * math.cos(angle_rad)
        y2 = cy + r_outer * math.sin(angle_rad)

        if i < active_ticks:
            # Color gradient from cyan to blue
            frac = i / max(active_ticks - 1, 1)
            cr = int(0 + frac * 60)
            cg = int(180 - frac * 40)
            cb = int(216 + frac * 39)
            color = f"#{cr:02x}{cg:02x}{cb:02x}"
            opacity = "0.95"
            sw = "2.5"
            filt = "url(#glow2)"
        else:
            color = "#1a2744"
            opacity = "0.5"
            sw = "1.5"
            filt = ""

        attrs = {"x1": f"{x1:.1f}", "y1": f"{y1:.1f}",
                 "x2": f"{x2:.1f}", "y2": f"{y2:.1f}",
                 "stroke": color, "opacity": opacity,
                 "stroke-width": sw, "stroke-linecap": "round"}
        if filt:
            attrs["filter"] = filt
        ET.SubElement(svg, "line", attrs)

    # Center text
    t = el(svg, "text", x=cx, y=cy + 4,
           fill="#e0f7fa", **{"font-family": "'Segoe UI', sans-serif",
                              "font-size": "24", "font-weight": "bold",
                              "text-anchor": "middle",
                              "dominant-baseline": "middle"})
    t.text = f"{pct}%"

    save(svg, "radial_tick_gauge.svg")


# ─────────────────────────────────────────────────────────────────────────────
# 3. HORIZONTAL PROGRESS BAR
# ─────────────────────────────────────────────────────────────────────────────
def gen_horizontal_bar():
    """Single horizontal progress bar with label and glow."""
    W, H = 220, 32
    svg = new_svg(W, H)
    d = defs(svg)

    # Gradient
    g = el(d, "linearGradient", id="barGrad", x1="0%", y1="0%", x2="100%", y2="0%")
    el(g, "stop", offset="0%", style="stop-color:#0077b6;stop-opacity:1")
    el(g, "stop", offset="100%", style="stop-color:#00b4d8;stop-opacity:1")

    f = el(d, "filter", id="glow3", x="-20%", y="-50%", width="140%", height="200%")
    el(f, "feGaussianBlur", **{"in": "SourceGraphic", "stdDeviation": "2", "result": "b"})
    m = el(f, "feMerge")
    el(m, "feMergeNode", **{"in": "b"})
    el(m, "feMergeNode", **{"in": "SourceGraphic"})

    bar_x = 0
    bar_y = 10
    bar_w = 220
    bar_h = 10
    pct = 65
    fill_w = bar_w * pct / 100

    # Track
    el(svg, "rect", x=bar_x, y=bar_y, width=bar_w, height=bar_h,
       rx="5", ry="5", fill="#0d1b2a")

    # Fill
    el(svg, "rect", x=bar_x, y=bar_y, width=f"{fill_w:.0f}", height=bar_h,
       rx="5", ry="5", fill="url(#barGrad)", filter="url(#glow3)")

    # Bright tip
    if fill_w > 6:
        el(svg, "rect", x=f"{fill_w - 4:.0f}", y=bar_y, width="4", height=bar_h,
           rx="2", ry="2", fill="#90e0ef", opacity="0.7")

    save(svg, "horizontal_bar.svg")


# ─────────────────────────────────────────────────────────────────────────────
# 4. KPI VALUE CARD
# ─────────────────────────────────────────────────────────────────────────────
def gen_kpi_card():
    """Single KPI card with label, value, and subtle border glow."""
    W, H = 200, 100
    svg = new_svg(W, H)
    d = defs(svg)

    f = el(d, "filter", id="boxGlow", x="-10%", y="-10%", width="120%", height="120%")
    el(f, "feGaussianBlur", **{"in": "SourceAlpha", "stdDeviation": "4", "result": "b"})
    flood = el(f, "feFlood", **{"flood-color": "#0077b6", "flood-opacity": "0.3", "result": "c"})
    el(f, "feComposite", **{"in": "c", "in2": "b", "operator": "in", "result": "s"})
    m = el(f, "feMerge")
    el(m, "feMergeNode", **{"in": "s"})
    el(m, "feMergeNode", **{"in": "SourceGraphic"})

    # Card body
    el(svg, "rect", x="2", y="2", width=f"{W-4}", height=f"{H-4}",
       rx="8", ry="8", fill="#0a1628", stroke="#1a3a5c",
       **{"stroke-width": "1", "filter": "url(#boxGlow)"})

    # Label
    t1 = el(svg, "text", x="20", y="32", fill="#5c8aad",
            **{"font-family": "'Segoe UI', sans-serif", "font-size": "12",
               "font-weight": "600", "letter-spacing": "1"})
    t1.text = "POWER"

    # Value
    t2 = el(svg, "text", x="20", y="68", fill="#e0f7fa",
            **{"font-family": "'Segoe UI', sans-serif", "font-size": "32",
               "font-weight": "bold"})
    t2.text = "2,450"

    # Unit
    t3 = el(svg, "text", x="145", y="68", fill="#5c8aad",
            **{"font-family": "'Segoe UI', sans-serif", "font-size": "14"})
    t3.text = "kW"

    # Subtle accent line at bottom
    el(svg, "rect", x="20", y=f"{H - 14}", width="60", height="2",
       rx="1", ry="1", fill="#00b4d8", opacity="0.6")

    save(svg, "kpi_card.svg")


# ─────────────────────────────────────────────────────────────────────────────
# 5. ACTION BUTTON (check / accept)
# ─────────────────────────────────────────────────────────────────────────────
def gen_action_button():
    """Circular action button with icon (checkmark)."""
    S = 56
    svg = new_svg(S, S)
    d = defs(svg)

    f = el(d, "filter", id="btnGlow", x="-50%", y="-50%", width="200%", height="200%")
    el(f, "feGaussianBlur", **{"in": "SourceGraphic", "stdDeviation": "2", "result": "b"})
    m = el(f, "feMerge")
    el(m, "feMergeNode", **{"in": "b"})
    el(m, "feMergeNode", **{"in": "SourceGraphic"})

    cx, cy, r = 28, 28, 22

    # Outer ring
    el(svg, "circle", cx=cx, cy=cy, r=r,
       fill="none", stroke="#3a7bd5", **{"stroke-width": "2"}, filter="url(#btnGlow)")

    # Inner fill
    el(svg, "circle", cx=cx, cy=cy, r=f"{r - 4}",
       fill="#0d1b2a", opacity="0.8")

    # Checkmark path
    el(svg, "path", d="M19 28 L25 34 L37 22",
       fill="none", stroke="#00b4d8",
       **{"stroke-width": "2.5", "stroke-linecap": "round", "stroke-linejoin": "round"})

    save(svg, "button_check.svg")


# ─────────────────────────────────────────────────────────────────────────────
# 6. ACTION BUTTON (X / reject)
# ─────────────────────────────────────────────────────────────────────────────
def gen_action_button_x():
    """Circular action button with X icon."""
    S = 56
    svg = new_svg(S, S)
    d = defs(svg)

    f = el(d, "filter", id="btnGlow", x="-50%", y="-50%", width="200%", height="200%")
    el(f, "feGaussianBlur", **{"in": "SourceGraphic", "stdDeviation": "2", "result": "b"})
    m = el(f, "feMerge")
    el(m, "feMergeNode", **{"in": "b"})
    el(m, "feMergeNode", **{"in": "SourceGraphic"})

    cx, cy, r = 28, 28, 22
    el(svg, "circle", cx=cx, cy=cy, r=r,
       fill="none", stroke="#3a7bd5", **{"stroke-width": "2"}, filter="url(#btnGlow)")
    el(svg, "circle", cx=cx, cy=cy, r=f"{r - 4}",
       fill="#0d1b2a", opacity="0.8")

    # X
    el(svg, "line", x1="20", y1="20", x2="36", y2="36",
       stroke="#00b4d8", **{"stroke-width": "2.5", "stroke-linecap": "round"})
    el(svg, "line", x1="36", y1="20", x2="20", y2="36",
       stroke="#00b4d8", **{"stroke-width": "2.5", "stroke-linecap": "round"})

    save(svg, "button_x.svg")


# ─────────────────────────────────────────────────────────────────────────────
# 7. ACTION BUTTON (back arrow)
# ─────────────────────────────────────────────────────────────────────────────
def gen_action_button_back():
    S = 56
    svg = new_svg(S, S)
    d = defs(svg)
    f = el(d, "filter", id="btnGlow", x="-50%", y="-50%", width="200%", height="200%")
    el(f, "feGaussianBlur", **{"in": "SourceGraphic", "stdDeviation": "2", "result": "b"})
    m = el(f, "feMerge")
    el(m, "feMergeNode", **{"in": "b"})
    el(m, "feMergeNode", **{"in": "SourceGraphic"})

    cx, cy, r = 28, 28, 22
    el(svg, "circle", cx=cx, cy=cy, r=r,
       fill="none", stroke="#3a7bd5", **{"stroke-width": "2"}, filter="url(#btnGlow)")
    el(svg, "circle", cx=cx, cy=cy, r=f"{r - 4}",
       fill="#0d1b2a", opacity="0.8")

    # Back arrow
    el(svg, "path", d="M32 20 L22 28 L32 36",
       fill="none", stroke="#00b4d8",
       **{"stroke-width": "2.5", "stroke-linecap": "round", "stroke-linejoin": "round"})
    el(svg, "line", x1="22", y1="28", x2="38", y2="28",
       stroke="#00b4d8", **{"stroke-width": "2.5", "stroke-linecap": "round"})

    save(svg, "button_back.svg")


# ─────────────────────────────────────────────────────────────────────────────
# 8. ACTION BUTTON (refresh)
# ─────────────────────────────────────────────────────────────────────────────
def gen_action_button_refresh():
    S = 56
    svg = new_svg(S, S)
    d = defs(svg)
    f = el(d, "filter", id="btnGlow", x="-50%", y="-50%", width="200%", height="200%")
    el(f, "feGaussianBlur", **{"in": "SourceGraphic", "stdDeviation": "2", "result": "b"})
    m = el(f, "feMerge")
    el(m, "feMergeNode", **{"in": "b"})
    el(m, "feMergeNode", **{"in": "SourceGraphic"})

    cx, cy, r = 28, 28, 22
    el(svg, "circle", cx=cx, cy=cy, r=r,
       fill="none", stroke="#3a7bd5", **{"stroke-width": "2"}, filter="url(#btnGlow)")
    el(svg, "circle", cx=cx, cy=cy, r=f"{r - 4}",
       fill="#0d1b2a", opacity="0.8")

    # Refresh arc + arrowhead
    el(svg, "path",
       d="M34 20 A10 10 0 1 0 36 30",
       fill="none", stroke="#00b4d8",
       **{"stroke-width": "2.5", "stroke-linecap": "round"})
    el(svg, "path", d="M33 16 L35 21 L39 19",
       fill="none", stroke="#00b4d8",
       **{"stroke-width": "2", "stroke-linecap": "round", "stroke-linejoin": "round"})

    save(svg, "button_refresh.svg")


# ─────────────────────────────────────────────────────────────────────────────
# 9. VERTICAL BAR CHART SINGLE BAR
# ─────────────────────────────────────────────────────────────────────────────
def gen_bar_single():
    """Single vertical bar with glow tip, for composing bar charts."""
    W, H = 32, 120
    svg = new_svg(W, H)
    d = defs(svg)

    g = el(d, "linearGradient", id="barV", x1="0%", y1="100%", x2="0%", y2="0%")
    el(g, "stop", offset="0%", style="stop-color:#0077b6;stop-opacity:1")
    el(g, "stop", offset="100%", style="stop-color:#00b4d8;stop-opacity:1")

    f = el(d, "filter", id="tipGlow", x="-50%", y="-50%", width="200%", height="200%")
    el(f, "feGaussianBlur", **{"in": "SourceGraphic", "stdDeviation": "3", "result": "b"})
    m = el(f, "feMerge")
    el(m, "feMergeNode", **{"in": "b"})
    el(m, "feMergeNode", **{"in": "SourceGraphic"})

    pct = 75
    bar_h = H * pct / 100
    bar_w = 18
    bx = (W - bar_w) / 2

    # Bar body
    el(svg, "rect", x=f"{bx:.0f}", y=f"{H - bar_h:.0f}",
       width=f"{bar_w}", height=f"{bar_h:.0f}",
       rx="3", ry="3", fill="url(#barV)", opacity="0.85")

    # Glow tip
    el(svg, "rect", x=f"{bx:.0f}", y=f"{H - bar_h:.0f}",
       width=f"{bar_w}", height="4",
       rx="2", ry="2", fill="#90e0ef", filter="url(#tipGlow)")

    save(svg, "bar_single.svg")


# ─────────────────────────────────────────────────────────────────────────────
# 10. DOT MATRIX INDICATOR
# ─────────────────────────────────────────────────────────────────────────────
def gen_dot_matrix():
    """Dot matrix / LED-style indicator block (like the equalizer in the ref)."""
    cols, rows = 12, 7
    dot_r = 3
    spacing = 10
    W = cols * spacing + 8
    H = rows * spacing + 8
    svg = new_svg(W, H)
    d = defs(svg)

    f = el(d, "filter", id="dotGlow", x="-50%", y="-50%", width="200%", height="200%")
    el(f, "feGaussianBlur", **{"in": "SourceGraphic", "stdDeviation": "1.5", "result": "b"})
    m = el(f, "feMerge")
    el(m, "feMergeNode", **{"in": "b"})
    el(m, "feMergeNode", **{"in": "SourceGraphic"})

    # Simulated "waveform" heights per column
    heights = [3, 5, 7, 6, 4, 5, 7, 6, 3, 4, 6, 5]

    for c in range(cols):
        for r in range(rows):
            cx = 8 + c * spacing
            cy = 8 + r * spacing
            row_from_bottom = rows - 1 - r
            if row_from_bottom < heights[c]:
                el(svg, "circle", cx=cx, cy=cy, r=dot_r,
                   fill="#00b4d8", opacity="0.9", filter="url(#dotGlow)")
            else:
                el(svg, "circle", cx=cx, cy=cy, r=dot_r,
                   fill="#0d1b2a", opacity="0.5")

    save(svg, "dot_matrix.svg")


# ─────────────────────────────────────────────────────────────────────────────
# 11. MINI SPARKLINE
# ─────────────────────────────────────────────────────────────────────────────
def gen_sparkline():
    """Small sparkline / trend line widget."""
    W, H = 200, 60
    svg = new_svg(W, H)
    d = defs(svg)

    g = el(d, "linearGradient", id="sparkFill", x1="0%", y1="0%", x2="0%", y2="100%")
    el(g, "stop", offset="0%", style="stop-color:#00b4d8;stop-opacity:0.3")
    el(g, "stop", offset="100%", style="stop-color:#00b4d8;stop-opacity:0.02")

    f = el(d, "filter", id="lineGlow", x="-10%", y="-30%", width="120%", height="160%")
    el(f, "feGaussianBlur", **{"in": "SourceGraphic", "stdDeviation": "1.5", "result": "b"})
    m = el(f, "feMerge")
    el(m, "feMergeNode", **{"in": "b"})
    el(m, "feMergeNode", **{"in": "SourceGraphic"})

    # Data points
    pts = [38, 30, 35, 20, 25, 15, 22, 18, 28, 12, 20, 8, 15, 10, 18, 22, 14, 10, 16, 12]
    num = len(pts)
    step = W / (num - 1)

    # Build polyline coords
    coords = " ".join(f"{i * step:.1f},{pts[i]:.1f}" for i in range(num))

    # Fill area (polygon closing to bottom)
    fill_coords = f"0,{H} " + coords + f" {W},{H}"
    el(svg, "polygon", points=fill_coords, fill="url(#sparkFill)")

    # Line
    el(svg, "polyline", points=coords,
       fill="none", stroke="#00b4d8",
       **{"stroke-width": "2", "stroke-linejoin": "round",
          "stroke-linecap": "round", "filter": "url(#lineGlow)"})

    # End dot
    last_x = (num - 1) * step
    last_y = pts[-1]
    el(svg, "circle", cx=f"{last_x:.1f}", cy=f"{last_y:.1f}", r="3",
       fill="#90e0ef", filter="url(#lineGlow)")

    save(svg, "sparkline.svg")


# ─────────────────────────────────────────────────────────────────────────────
# 12. SEMI-CIRCULAR GAUGE (speedometer)
# ─────────────────────────────────────────────────────────────────────────────
def gen_semicircle_gauge():
    """Half-circle gauge like a speedometer/demand gauge."""
    W, H = 180, 110
    svg = new_svg(W, H)
    d = defs(svg)

    f = el(d, "filter", id="arcGlow", x="-30%", y="-30%", width="160%", height="160%")
    el(f, "feGaussianBlur", **{"in": "SourceGraphic", "stdDeviation": "3", "result": "b"})
    m = el(f, "feMerge")
    el(m, "feMergeNode", **{"in": "b"})
    el(m, "feMergeNode", **{"in": "SourceGraphic"})

    cx, cy = 90, 95
    r = 75
    stroke_w = 10
    pct = 68

    # Track arc (semicircle, from 180 to 360 degrees)
    # Using SVG arc: start at left, sweep to right
    el(svg, "path",
       d=f"M{cx - r},{cy} A{r},{r} 0 0 1 {cx + r},{cy}",
       fill="none", stroke="#1a2744", **{"stroke-width": str(stroke_w), "stroke-linecap": "round"})

    # Value arc
    angle = math.pi * pct / 100  # 0..pi mapped to semicircle
    ex = cx - r * math.cos(angle)
    ey = cy - r * math.sin(angle)
    large = "1" if pct > 50 else "0"

    el(svg, "path",
       d=f"M{cx - r},{cy} A{r},{r} 0 {large} 1 {ex:.1f},{ey:.1f}",
       fill="none", stroke="#00b4d8",
       **{"stroke-width": str(stroke_w), "stroke-linecap": "round",
          "filter": "url(#arcGlow)"})

    # Needle dot at current position
    el(svg, "circle", cx=f"{ex:.1f}", cy=f"{ey:.1f}", r="5",
       fill="#90e0ef", filter="url(#arcGlow)")

    # Value text
    t = el(svg, "text", x=cx, y=cy - 5,
           fill="#e0f7fa", **{"font-family": "'Segoe UI', sans-serif",
                              "font-size": "22", "font-weight": "bold",
                              "text-anchor": "middle"})
    t.text = f"{pct}%"

    save(svg, "semicircle_gauge.svg")


# ─────────────────────────────────────────────────────────────────────────────
# 13. STATUS INDICATOR (on/off pill)
# ─────────────────────────────────────────────────────────────────────────────
def gen_status_pill():
    """Small status indicator pill, ON state."""
    W, H = 72, 28
    svg = new_svg(W, H)
    d = defs(svg)

    f = el(d, "filter", id="pillGlow", x="-30%", y="-50%", width="160%", height="200%")
    el(f, "feGaussianBlur", **{"in": "SourceGraphic", "stdDeviation": "2", "result": "b"})
    m = el(f, "feMerge")
    el(m, "feMergeNode", **{"in": "b"})
    el(m, "feMergeNode", **{"in": "SourceGraphic"})

    # Pill body
    el(svg, "rect", x="1", y="1", width=f"{W-2}", height=f"{H-2}",
       rx="14", ry="14", fill="#0a1628", stroke="#00c853",
       **{"stroke-width": "1.5"})

    # Dot
    el(svg, "circle", cx="18", cy="14", r="5",
       fill="#00c853", filter="url(#pillGlow)")

    # Text
    t = el(svg, "text", x="42", y="18",
           fill="#00c853", **{"font-family": "Consolas, monospace",
                              "font-size": "11", "font-weight": "bold",
                              "text-anchor": "middle"})
    t.text = "ON"

    save(svg, "status_pill_on.svg")


def gen_status_pill_off():
    W, H = 72, 28
    svg = new_svg(W, H)

    el(svg, "rect", x="1", y="1", width=f"{W-2}", height=f"{H-2}",
       rx="14", ry="14", fill="#0a1628", stroke="#78909c",
       **{"stroke-width": "1.5"})
    el(svg, "circle", cx="18", cy="14", r="5", fill="#78909c")
    t = el(svg, "text", x="44", y="18",
           fill="#78909c", **{"font-family": "Consolas, monospace",
                              "font-size": "11", "font-weight": "bold",
                              "text-anchor": "middle"})
    t.text = "OFF"

    save(svg, "status_pill_off.svg")


# ─────────────────────────────────────────────────────────────────────────────
# 14. CIRCUIT BREAKER SYMBOL (closed)
# ─────────────────────────────────────────────────────────────────────────────
def gen_cb_closed():
    """Standalone circuit breaker symbol, closed state."""
    S = 48
    svg = new_svg(S, S)
    d = defs(svg)
    f = el(d, "filter", id="cbGlow", x="-50%", y="-50%", width="200%", height="200%")
    el(f, "feGaussianBlur", **{"in": "SourceGraphic", "stdDeviation": "2", "result": "b"})
    m = el(f, "feMerge")
    el(m, "feMergeNode", **{"in": "b"})
    el(m, "feMergeNode", **{"in": "SourceGraphic"})

    cx, cy = 24, 24
    # Vertical stubs
    el(svg, "line", x1=cx, y1="2", x2=cx, y2="14",
       stroke="#4fc3f7", **{"stroke-width": "2.5", "stroke-linecap": "round"})
    el(svg, "line", x1=cx, y1="34", x2=cx, y2="46",
       stroke="#4fc3f7", **{"stroke-width": "2.5", "stroke-linecap": "round"})

    # CB body
    el(svg, "rect", x="10", y="14", width="28", height="20",
       rx="4", ry="4", fill="#00c853", filter="url(#cbGlow)",
       stroke="#69f0ae", **{"stroke-width": "0.8"})

    # Closed symbol (horizontal bar)
    el(svg, "line", x1="16", y1=cy, x2="32", y2=cy,
       stroke="white", **{"stroke-width": "2.5", "stroke-linecap": "round"})

    save(svg, "cb_closed.svg")


def gen_cb_open():
    """Standalone circuit breaker symbol, open state."""
    S = 48
    svg = new_svg(S, S)
    d = defs(svg)
    f = el(d, "filter", id="cbGlow", x="-50%", y="-50%", width="200%", height="200%")
    el(f, "feGaussianBlur", **{"in": "SourceGraphic", "stdDeviation": "2", "result": "b"})
    m = el(f, "feMerge")
    el(m, "feMergeNode", **{"in": "b"})
    el(m, "feMergeNode", **{"in": "SourceGraphic"})

    cx, cy = 24, 24
    el(svg, "line", x1=cx, y1="2", x2=cx, y2="14",
       stroke="#4fc3f7", **{"stroke-width": "2.5", "stroke-linecap": "round"})
    el(svg, "line", x1=cx, y1="34", x2=cx, y2="46",
       stroke="#4fc3f7", **{"stroke-width": "2.5", "stroke-linecap": "round"})

    el(svg, "rect", x="10", y="14", width="28", height="20",
       rx="4", ry="4", fill="#d32f2f", filter="url(#cbGlow)",
       stroke="#ef5350", **{"stroke-width": "0.8"})

    # Open symbol (X)
    el(svg, "line", x1="17", y1="19", x2="31", y2="29",
       stroke="white", **{"stroke-width": "2", "stroke-linecap": "round"})
    el(svg, "line", x1="31", y1="19", x2="17", y2="29",
       stroke="white", **{"stroke-width": "2", "stroke-linecap": "round"})

    save(svg, "cb_open.svg")


# ─────────────────────────────────────────────────────────────────────────────
# 15. BUSBAR SEGMENT (horizontal, standalone)
# ─────────────────────────────────────────────────────────────────────────────
def gen_busbar_segment():
    """Plain horizontal busbar segment with connection points."""
    W, H = 300, 24
    svg = new_svg(W, H)
    d = defs(svg)

    g = el(d, "linearGradient", id="busG", x1="0%", y1="0%", x2="0%", y2="100%")
    el(g, "stop", offset="0%", style="stop-color:#ff8f00;stop-opacity:1")
    el(g, "stop", offset="100%", style="stop-color:#e65100;stop-opacity:1")

    f = el(d, "filter", id="busGlow", x="-5%", y="-50%", width="110%", height="200%")
    el(f, "feGaussianBlur", **{"in": "SourceGraphic", "stdDeviation": "3", "result": "b"})
    m = el(f, "feMerge")
    el(m, "feMergeNode", **{"in": "b"})
    el(m, "feMergeNode", **{"in": "SourceGraphic"})

    # Busbar body
    el(svg, "rect", x="0", y="7", width=f"{W}", height="10",
       rx="2", ry="2", fill="url(#busG)", filter="url(#busGlow)",
       stroke="#ffb74d", **{"stroke-width": "0.5"})

    # Connection stubs (vertical ticks at ends and middle)
    for px in [0, W // 4, W // 2, 3 * W // 4, W - 1]:
        el(svg, "line", x1=f"{px}", y1="4", x2=f"{px}", y2="20",
           stroke="#ffb74d", **{"stroke-width": "1.5", "stroke-linecap": "round", "opacity": "0.6"})

    save(svg, "busbar_segment.svg")


# ─────────────────────────────────────────────────────────────────────────────
# 16. BUSBAR SEGMENT (vertical)
# ─────────────────────────────────────────────────────────────────────────────
def gen_busbar_segment_v():
    """Vertical busbar segment."""
    W, H = 24, 300
    svg = new_svg(W, H)
    d = defs(svg)

    g = el(d, "linearGradient", id="busGV", x1="0%", y1="0%", x2="100%", y2="0%")
    el(g, "stop", offset="0%", style="stop-color:#d32f2f;stop-opacity:1")
    el(g, "stop", offset="100%", style="stop-color:#f44336;stop-opacity:1")

    f = el(d, "filter", id="busGlow", x="-50%", y="-5%", width="200%", height="110%")
    el(f, "feGaussianBlur", **{"in": "SourceGraphic", "stdDeviation": "3", "result": "b"})
    m = el(f, "feMerge")
    el(m, "feMergeNode", **{"in": "b"})
    el(m, "feMergeNode", **{"in": "SourceGraphic"})

    el(svg, "rect", x="7", y="0", width="10", height=f"{H}",
       rx="2", ry="2", fill="url(#busGV)", filter="url(#busGlow)",
       stroke="#ef5350", **{"stroke-width": "0.5"})

    for py in [0, H // 4, H // 2, 3 * H // 4, H - 1]:
        el(svg, "line", x1="4", y1=f"{py}", x2="20", y2=f"{py}",
           stroke="#ef9a9a", **{"stroke-width": "1.5", "stroke-linecap": "round", "opacity": "0.6"})

    save(svg, "busbar_segment_vertical.svg")


# ─────────────────────────────────────────────────────────────────────────────
# 17. CURRENT TRANSFORMER (CT) SYMBOL
# ─────────────────────────────────────────────────────────────────────────────
def gen_ct_symbol():
    S = 36
    svg = new_svg(S, S)
    cx = 18

    el(svg, "line", x1=cx, y1="0", x2=cx, y2="10",
       stroke="#4fc3f7", **{"stroke-width": "2", "stroke-linecap": "round"})
    el(svg, "circle", cx=cx, cy="15", r="5",
       fill="none", stroke="#4fc3f7", **{"stroke-width": "1.5"})
    el(svg, "circle", cx=cx, cy="23", r="5",
       fill="none", stroke="#4fc3f7", **{"stroke-width": "1.5"})
    el(svg, "line", x1=cx, y1="28", x2=cx, y2="36",
       stroke="#4fc3f7", **{"stroke-width": "2", "stroke-linecap": "round"})

    save(svg, "ct_symbol.svg")


# ─────────────────────────────────────────────────────────────────────────────
# 18. DISCONNECT SWITCH SYMBOL
# ─────────────────────────────────────────────────────────────────────────────
def gen_disconnect_switch():
    W, H = 36, 48
    svg = new_svg(W, H)
    cx = 18

    el(svg, "line", x1=cx, y1="0", x2=cx, y2="14",
       stroke="#4fc3f7", **{"stroke-width": "2", "stroke-linecap": "round"})

    # Blade (angled line = open, straight = closed) -- showing closed
    el(svg, "line", x1=cx, y1="14", x2=cx, y2="34",
       stroke="#00c853", **{"stroke-width": "2.5", "stroke-linecap": "round"})

    # Pivot circles
    el(svg, "circle", cx=cx, cy="14", r="3",
       fill="none", stroke="#4fc3f7", **{"stroke-width": "1.5"})
    el(svg, "circle", cx=cx, cy="34", r="3",
       fill="none", stroke="#4fc3f7", **{"stroke-width": "1.5"})

    el(svg, "line", x1=cx, y1="34", x2=cx, y2="48",
       stroke="#4fc3f7", **{"stroke-width": "2", "stroke-linecap": "round"})

    save(svg, "disconnect_switch_closed.svg")


# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("  COMPONENT SVG GENERATOR")
    print("  Building individual reusable SVG widgets...")
    print("=" * 60)
    print()

    components = [
        ("Ring gauge", gen_ring_gauge),
        ("Radial tick gauge", gen_radial_tick_gauge),
        ("Horizontal bar", gen_horizontal_bar),
        ("KPI card", gen_kpi_card),
        ("Button: check", gen_action_button),
        ("Button: X", gen_action_button_x),
        ("Button: back", gen_action_button_back),
        ("Button: refresh", gen_action_button_refresh),
        ("Bar single", gen_bar_single),
        ("Dot matrix", gen_dot_matrix),
        ("Sparkline", gen_sparkline),
        ("Semicircle gauge", gen_semicircle_gauge),
        ("Status pill ON", gen_status_pill),
        ("Status pill OFF", gen_status_pill_off),
        ("CB closed", gen_cb_closed),
        ("CB open", gen_cb_open),
        ("Busbar segment (H)", gen_busbar_segment),
        ("Busbar segment (V)", gen_busbar_segment_v),
        ("CT symbol", gen_ct_symbol),
        ("Disconnect switch", gen_disconnect_switch),
    ]

    for name, fn in components:
        print(f"  {name}...")
        fn()

    print()
    print(f"  {len(components)} components generated in {OUTPUT_DIR}")
    print("=" * 60)
