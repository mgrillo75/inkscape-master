#!/usr/bin/env python3
"""
Busbar SVG Generator for SCADA/Perspective Projects
====================================================
Generates multiple busbar SVG variants inspired by modern SCADA displays.
These are designed to be imported into Inductive Automation Perspective
or any HTML5/CSS3 based SCADA system.

Usage:
    python generate_busbars.py

Output: ./output/*.svg
"""

import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── Shared SVG utilities ────────────────────────────────────────────────────

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"

def new_svg(width, height, viewbox=None):
    """Create a new SVG root element."""
    ET.register_namespace("", SVG_NS)
    ET.register_namespace("xlink", XLINK_NS)
    svg = ET.Element("svg", {
        "xmlns": SVG_NS,
        "xmlns:xlink": XLINK_NS,
        "width": str(width),
        "height": str(height),
        "viewBox": viewbox or f"0 0 {width} {height}",
    })
    return svg


def add_defs(svg):
    """Add a <defs> section and return it."""
    defs = ET.SubElement(svg, "defs")
    return defs


def add_glow_filter(defs, filter_id, color, std_dev=4):
    """Add a glow/drop-shadow filter."""
    f = ET.SubElement(defs, "filter", {
        "id": filter_id,
        "x": "-50%", "y": "-50%",
        "width": "200%", "height": "200%",
    })
    ET.SubElement(f, "feGaussianBlur", {
        "in": "SourceGraphic",
        "stdDeviation": str(std_dev),
        "result": "blur",
    })
    ET.SubElement(f, "feFlood", {
        "flood-color": color,
        "flood-opacity": "0.6",
        "result": "color",
    })
    ET.SubElement(f, "feComposite", {
        "in": "color",
        "in2": "blur",
        "operator": "in",
        "result": "shadow",
    })
    merge = ET.SubElement(f, "feMerge")
    ET.SubElement(merge, "feMergeNode", {"in": "shadow"})
    ET.SubElement(merge, "feMergeNode", {"in": "SourceGraphic"})
    return f


def add_gradient(defs, grad_id, color1, color2, x1="0%", y1="0%", x2="0%", y2="100%"):
    """Add a linear gradient."""
    g = ET.SubElement(defs, "linearGradient", {
        "id": grad_id, "x1": x1, "y1": y1, "x2": x2, "y2": y2,
    })
    ET.SubElement(g, "stop", {"offset": "0%", "style": f"stop-color:{color1};stop-opacity:1"})
    ET.SubElement(g, "stop", {"offset": "100%", "style": f"stop-color:{color2};stop-opacity:1"})
    return g


def rect(parent, x, y, w, h, **attrs):
    el = ET.SubElement(parent, "rect", {"x": str(x), "y": str(y), "width": str(w), "height": str(h), **attrs})
    return el


def line(parent, x1, y1, x2, y2, **attrs):
    el = ET.SubElement(parent, "line", {"x1": str(x1), "y1": str(y1), "x2": str(x2), "y2": str(y2), **attrs})
    return el


def circle(parent, cx, cy, r, **attrs):
    el = ET.SubElement(parent, "circle", {"cx": str(cx), "cy": str(cy), "r": str(r), **attrs})
    return el


def text(parent, x, y, content, **attrs):
    el = ET.SubElement(parent, "text", {"x": str(x), "y": str(y), **attrs})
    el.text = content
    return el


def group(parent, **attrs):
    return ET.SubElement(parent, "g", attrs)


def path(parent, d, **attrs):
    return ET.SubElement(parent, "path", {"d": d, **attrs})


def polygon(parent, points, **attrs):
    return ET.SubElement(parent, "polygon", {"points": points, **attrs})


def save_svg(svg, filename):
    """Save SVG with pretty formatting."""
    rough = ET.tostring(svg, encoding="unicode")
    parsed = minidom.parseString(rough)
    pretty = parsed.toprettyxml(indent="  ")
    # Remove the XML declaration minidom adds (we want clean SVG)
    lines = pretty.split("\n")
    if lines[0].startswith("<?xml"):
        lines = lines[1:]
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  [OK] {filepath}")
    return filepath


# ═══════════════════════════════════════════════════════════════════════════════
# VARIANT 1: Modern Dark-Theme Horizontal Busbar with Circuit Breakers
# ═══════════════════════════════════════════════════════════════════════════════
def generate_busbar_v1():
    """
    Inspired by Figure 18 (single-line diagram).
    Horizontal orange busbar with 5 feeder drop-downs,
    circuit breakers, and status indicators.
    Dark background, professional SCADA look.
    """
    W, H = 1200, 500
    svg = new_svg(W, H)
    defs = add_defs(svg)

    # Gradients
    add_gradient(defs, "busbarGrad", "#FF8C00", "#CC6600", x1="0%", y1="0%", x2="0%", y2="100%")
    add_gradient(defs, "bgGrad", "#0a1628", "#0d2137", x1="0%", y1="0%", x2="0%", y2="100%")
    add_gradient(defs, "panelGrad", "#142640", "#0d1f35", x1="0%", y1="0%", x2="0%", y2="100%")

    # Glow effects
    add_glow_filter(defs, "orangeGlow", "#FF8C00", 6)
    add_glow_filter(defs, "greenGlow", "#00FF88", 4)
    add_glow_filter(defs, "redGlow", "#FF3333", 4)

    # Background
    rect(svg, 0, 0, W, H, fill="url(#bgGrad)", rx="8", ry="8")

    # Title bar
    rect(svg, 0, 0, W, 36, fill="#0a3d62", opacity="0.8")
    text(svg, W // 2, 24, "MAIN BUSBAR - SINGLE LINE DIAGRAM",
         fill="#4FC3F7", **{"font-family": "Consolas, monospace", "font-size": "14",
                           "font-weight": "bold", "text-anchor": "middle"})

    # ── Main busbar (horizontal bar) ──
    bus_y = 100
    bus_h = 12
    bus_x1 = 60
    bus_x2 = W - 60

    # Busbar shadow
    rect(svg, bus_x1, bus_y + 2, bus_x2 - bus_x1, bus_h, fill="black", opacity="0.3",
         rx="2", ry="2", filter="url(#orangeGlow)")

    # Main busbar
    rect(svg, bus_x1, bus_y, bus_x2 - bus_x1, bus_h,
         fill="url(#busbarGrad)", rx="2", ry="2",
         filter="url(#orangeGlow)", stroke="#FFB74D", **{"stroke-width": "0.5"})

    # Bus label
    text(svg, 30, bus_y + 10, "BUS", fill="#FFB74D",
         **{"font-family": "Consolas, monospace", "font-size": "11", "font-weight": "bold"})

    # ── Feeders ──
    feeder_labels = ["471", "431", "432", "433", "434"]
    feeder_states = ["closed", "closed", "closed", "closed", "open"]  # CB states
    feeder_spacing = (bus_x2 - bus_x1 - 100) / (len(feeder_labels) - 1)

    for i, (label, state) in enumerate(zip(feeder_labels, feeder_states)):
        fx = bus_x1 + 50 + i * feeder_spacing
        fy_top = bus_y + bus_h
        fy_bot = 420

        g_feeder = group(svg, id=f"feeder_{label}")

        # Vertical feeder line (top portion)
        line(g_feeder, fx, fy_top, fx, fy_top + 60,
             stroke="#4FC3F7", **{"stroke-width": "3", "stroke-linecap": "round"})

        # ── Circuit Breaker symbol ──
        cb_y = fy_top + 60
        cb_size = 28
        is_closed = state == "closed"
        cb_color = "#00E676" if is_closed else "#FF1744"
        cb_glow = "url(#greenGlow)" if is_closed else "url(#redGlow)"

        # CB box
        rect(g_feeder, fx - cb_size / 2, cb_y, cb_size, cb_size,
             fill=cb_color, rx="4", ry="4", filter=cb_glow,
             stroke=cb_color, **{"stroke-width": "1", "opacity": "0.9"})

        # CB cross or line (closed = line, open = X)
        if is_closed:
            line(g_feeder, fx - 8, cb_y + cb_size / 2, fx + 8, cb_y + cb_size / 2,
                 stroke="white", **{"stroke-width": "2"})
        else:
            line(g_feeder, fx - 7, cb_y + 7, fx + 7, cb_y + cb_size - 7,
                 stroke="white", **{"stroke-width": "2"})
            line(g_feeder, fx + 7, cb_y + 7, fx - 7, cb_y + cb_size - 7,
                 stroke="white", **{"stroke-width": "2"})

        # CB label
        text(g_feeder, fx, cb_y - 6, f"CB{i+1}",
             fill="#B0BEC5", **{"font-family": "Consolas, monospace", "font-size": "10",
                                "text-anchor": "middle"})

        # Vertical feeder line (below CB)
        line(g_feeder, fx, cb_y + cb_size, fx, fy_bot - 70,
             stroke="#4FC3F7", **{"stroke-width": "3", "stroke-linecap": "round"})

        # ── Feeder number badge ──
        rect(g_feeder, fx - 22, fy_bot - 65, 44, 22,
             fill="#1A237E", rx="4", ry="4", stroke="#3F51B5", **{"stroke-width": "1"})
        text(g_feeder, fx, fy_bot - 50, label,
             fill="#E8EAF6", **{"font-family": "Consolas, monospace", "font-size": "13",
                                "font-weight": "bold", "text-anchor": "middle"})

        # ── Power readings panel ──
        panel_y = fy_bot - 35
        rect(g_feeder, fx - 45, panel_y, 90, 52,
             fill="url(#panelGrad)", rx="4", ry="4",
             stroke="#1E88E5", **{"stroke-width": "0.5"})

        # Simulated readings
        kw_val = [24.1, 24.1, 24.1, 24.1, 0][i]
        kvar_val = [62.3, 62.3, 62.3, 62.3, 0][i]
        pf_val = [75.7, 75.7, 75.7, 75.7, 0][i]

        readings = [
            (f"{kw_val:.1f} kW", "#4FC3F7"),
            (f"{kvar_val:.1f} kVAr", "#81C784"),
            (f"PF {pf_val:.1f}%", "#FFB74D"),
        ]
        for j, (val_text, color) in enumerate(readings):
            text(g_feeder, fx, panel_y + 15 + j * 15, val_text,
                 fill=color, **{"font-family": "Consolas, monospace", "font-size": "10",
                                "text-anchor": "middle"})

    # ── Legend ──
    legend_g = group(svg, id="legend")
    rect(legend_g, W - 200, H - 70, 180, 55, fill="#0d1f35", rx="4", ry="4",
         stroke="#1E88E5", **{"stroke-width": "0.5"})
    circle(legend_g, W - 180, H - 46, 6, fill="#00E676")
    text(legend_g, W - 168, H - 42, "Closed", fill="#B0BEC5",
         **{"font-family": "Consolas, monospace", "font-size": "11"})
    circle(legend_g, W - 180, H - 28, 6, fill="#FF1744")
    text(legend_g, W - 168, H - 24, "Open", fill="#B0BEC5",
         **{"font-family": "Consolas, monospace", "font-size": "11"})

    save_svg(svg, "busbar_v1_horizontal_sld.svg")


# ═══════════════════════════════════════════════════════════════════════════════
# VARIANT 2: Glowing Neon Busbar (Chinese SCADA / Cyberpunk style)
# ═══════════════════════════════════════════════════════════════════════════════
def generate_busbar_v2():
    """
    Inspired by the Chinese heating station SCADA screenshot.
    Dark background with neon cyan/magenta glow effects.
    """
    W, H = 1200, 400
    svg = new_svg(W, H)
    defs = add_defs(svg)

    # Gradients
    add_gradient(defs, "bgGrad2", "#0a0a1a", "#0d0d2b")
    add_gradient(defs, "busGrad2", "#00E5FF", "#0091EA", x1="0%", y1="0%", x2="100%", y2="0%")
    add_gradient(defs, "neonPink", "#FF1493", "#FF69B4", x1="0%", y1="0%", x2="0%", y2="100%")

    # Glow filters
    add_glow_filter(defs, "cyanGlow", "#00E5FF", 8)
    add_glow_filter(defs, "pinkGlow", "#FF1493", 6)
    add_glow_filter(defs, "whiteGlow", "#FFFFFF", 3)

    # Background
    rect(svg, 0, 0, W, H, fill="url(#bgGrad2)", rx="6", ry="6")

    # Grid lines (subtle)
    grid_g = group(svg, opacity="0.05")
    for gx in range(0, W, 40):
        line(grid_g, gx, 0, gx, H, stroke="#00E5FF", **{"stroke-width": "0.5"})
    for gy in range(0, H, 40):
        line(grid_g, 0, gy, W, gy, stroke="#00E5FF", **{"stroke-width": "0.5"})

    # Title
    text(svg, W // 2, 30, "MAIN BUS - 22kV",
         fill="#00E5FF", filter="url(#cyanGlow)",
         **{"font-family": "'Segoe UI', Arial, sans-serif", "font-size": "18",
            "font-weight": "bold", "text-anchor": "middle", "letter-spacing": "4"})

    # ── Primary busbar (double line style) ──
    bus_y = 80
    bus_x1 = 80
    bus_x2 = W - 80

    # Outer glow line
    line(svg, bus_x1, bus_y, bus_x2, bus_y,
         stroke="#00E5FF", filter="url(#cyanGlow)",
         **{"stroke-width": "6", "stroke-linecap": "round", "opacity": "0.4"})
    # Main line
    line(svg, bus_x1, bus_y, bus_x2, bus_y,
         stroke="url(#busGrad2)",
         **{"stroke-width": "4", "stroke-linecap": "round"})
    # Inner highlight
    line(svg, bus_x1, bus_y - 1, bus_x2, bus_y - 1,
         stroke="white", **{"stroke-width": "1", "opacity": "0.3"})

    # ── Secondary busbar ──
    bus2_y = bus_y + 30
    line(svg, bus_x1, bus2_y, bus_x2, bus2_y,
         stroke="#00E5FF", filter="url(#cyanGlow)",
         **{"stroke-width": "6", "stroke-linecap": "round", "opacity": "0.3"})
    line(svg, bus_x1, bus2_y, bus_x2, bus2_y,
         stroke="url(#busGrad2)",
         **{"stroke-width": "3", "stroke-linecap": "round", "opacity": "0.7"})

    # Bus labels
    text(svg, bus_x1 - 10, bus_y + 5, "BUS I", fill="#00E5FF",
         **{"font-family": "Consolas, monospace", "font-size": "10",
            "text-anchor": "end", "font-weight": "bold"})
    text(svg, bus_x1 - 10, bus2_y + 5, "BUS II", fill="#00BCD4",
         **{"font-family": "Consolas, monospace", "font-size": "10",
            "text-anchor": "end", "font-weight": "bold"})

    # ── Feeders with disconnect switches ──
    num_feeders = 6
    spacing = (bus_x2 - bus_x1 - 60) / (num_feeders - 1)
    feeder_names = ["F1-DG1", "F2-DG2", "F3-PV", "F4-BESS", "F5-WIND", "F6-LOAD"]
    feeder_colors = ["#FF6D00", "#FF6D00", "#FFEB3B", "#76FF03", "#00E5FF", "#FF1493"]

    for i in range(num_feeders):
        fx = bus_x1 + 30 + i * spacing
        fg = group(svg, id=f"feeder_v2_{i}")

        fc = feeder_colors[i]

        # Connection to bus 1
        line(fg, fx, bus_y, fx, bus_y + 15,
             stroke=fc, **{"stroke-width": "2"})

        # Disconnect switch (diamond shape)
        sw_y = bus_y + 15
        sw_size = 8
        polygon(fg, f"{fx},{sw_y} {fx + sw_size},{sw_y + sw_size} {fx},{sw_y + 2 * sw_size} {fx - sw_size},{sw_y + sw_size}",
                fill="none", stroke=fc, **{"stroke-width": "1.5"})

        # Connection to bus 2
        line(fg, fx, sw_y + 2 * sw_size, fx, bus2_y,
             stroke=fc, **{"stroke-width": "2"})

        # Vertical drop-down from bus 2
        drop_y = bus2_y + 10
        line(fg, fx, bus2_y, fx, drop_y + 80,
             stroke=fc, **{"stroke-width": "2.5", "opacity": "0.8"})

        # Glow dot at connection point
        circle(fg, fx, bus_y, 4, fill=fc, filter="url(#whiteGlow)", opacity="0.9")
        circle(fg, fx, bus2_y, 4, fill=fc, filter="url(#whiteGlow)", opacity="0.9")

        # ── Circuit breaker (stylized) ──
        cb_y = drop_y + 40
        # Two opposing triangles
        tri_h = 12
        path(fg, f"M{fx - 8},{cb_y - tri_h} L{fx + 8},{cb_y - tri_h} L{fx},{cb_y} Z",
             fill=fc, opacity="0.8")
        path(fg, f"M{fx - 8},{cb_y + tri_h} L{fx + 8},{cb_y + tri_h} L{fx},{cb_y} Z",
             fill=fc, opacity="0.8")

        # ── CT symbol (circles) ──
        ct_y = drop_y + 70
        circle(fg, fx, ct_y, 6, fill="none", stroke=fc, **{"stroke-width": "1.5"})
        circle(fg, fx, ct_y + 8, 6, fill="none", stroke=fc, **{"stroke-width": "1.5"})

        # ── Feeder label ──
        fn = feeder_names[i]

        # Label background
        label_y = drop_y + 110
        lbl_w = len(fn) * 8 + 16
        rect(fg, fx - lbl_w / 2, label_y - 12, lbl_w, 20,
             fill="#0a0a1a", rx="3", ry="3", stroke=fc, **{"stroke-width": "0.8"})
        text(fg, fx, label_y + 2, fn,
             fill=fc, **{"font-family": "Consolas, monospace", "font-size": "11",
                         "text-anchor": "middle", "font-weight": "bold"})

        # Drop line extension
        line(fg, fx, ct_y + 14, fx, label_y - 14,
             stroke=fc, **{"stroke-width": "2", "opacity": "0.6"})

    # ── Voltage / Frequency badges ──
    badge_g = group(svg, id="badges")
    badges = [("22.0 kV", 100, H - 50), ("50.0 Hz", 250, H - 50), ("Bus Tie: CLOSED", 450, H - 50)]
    for btext, bx, by in badges:
        rect(badge_g, bx - 50, by - 14, 100, 24,
             fill="#0a0a1a", rx="12", ry="12",
             stroke="#00E5FF", **{"stroke-width": "1"})
        text(badge_g, bx, by + 4, btext,
             fill="#00E5FF", **{"font-family": "Consolas, monospace", "font-size": "11",
                                "text-anchor": "middle"})

    save_svg(svg, "busbar_v2_neon_double.svg")


# ═══════════════════════════════════════════════════════════════════════════════
# VARIANT 3: Compact Modular Busbar Segment (Perspective component-ready)
# ═══════════════════════════════════════════════════════════════════════════════
def generate_busbar_v3():
    """
    A compact, reusable busbar segment designed to be used as a
    Perspective SVG component. Includes a single feeder with CB,
    disconnect switch, CT, and measurement panel.
    """
    W, H = 200, 480
    svg = new_svg(W, H)
    defs = add_defs(svg)

    add_gradient(defs, "bgGrad3", "#0C1929", "#152238")
    add_gradient(defs, "busGrad3", "#E65100", "#FF8F00")
    add_glow_filter(defs, "amberGlow", "#FF8F00", 5)
    add_glow_filter(defs, "statusGlow", "#00E676", 3)

    # Background
    rect(svg, 0, 0, W, H, fill="url(#bgGrad3)", rx="8", ry="8")

    cx = W // 2

    # ── Busbar (horizontal, spanning full width) ──
    bus_y = 40
    rect(svg, 10, bus_y, W - 20, 10, fill="url(#busGrad3)", rx="2", ry="2",
         filter="url(#amberGlow)")
    text(svg, cx, bus_y - 6, "22 kV BUS", fill="#FFB74D",
         **{"font-family": "'Segoe UI', sans-serif", "font-size": "11",
            "text-anchor": "middle", "font-weight": "bold"})

    # ── Disconnect switch (top) ──
    ds_y = bus_y + 10
    line(svg, cx, ds_y, cx, ds_y + 20, stroke="#4FC3F7", **{"stroke-width": "2.5"})
    # Switch blade
    rect(svg, cx - 10, ds_y + 20, 20, 8, fill="none", stroke="#4FC3F7",
         **{"stroke-width": "1.5"}, rx="2", ry="2")
    line(svg, cx - 6, ds_y + 24, cx + 6, ds_y + 24, stroke="#4FC3F7", **{"stroke-width": "1.5"})

    # ── Vertical line to CB ──
    line(svg, cx, ds_y + 28, cx, ds_y + 55, stroke="#4FC3F7", **{"stroke-width": "2.5"})

    # ── Circuit breaker ──
    cb_y = ds_y + 55
    cb_s = 32
    # CB housing
    rect(svg, cx - cb_s / 2, cb_y, cb_s, cb_s, fill="#00C853", rx="5", ry="5",
         filter="url(#statusGlow)", stroke="#00E676", **{"stroke-width": "1"})
    # CB symbol (closed = horizontal line)
    line(svg, cx - 10, cb_y + cb_s / 2, cx + 10, cb_y + cb_s / 2,
         stroke="white", **{"stroke-width": "2.5"})
    # CB label
    text(svg, cx, cb_y + cb_s + 14, "CB-01", fill="#B0BEC5",
         **{"font-family": "Consolas, monospace", "font-size": "10",
            "text-anchor": "middle"})

    # ── Vertical line to CT ──
    line(svg, cx, cb_y + cb_s, cx, cb_y + cb_s + 30,
         stroke="#4FC3F7", **{"stroke-width": "2.5"})

    # ── Current Transformer (CT) ──
    ct_y = cb_y + cb_s + 35
    circle(svg, cx, ct_y, 8, fill="none", stroke="#4FC3F7", **{"stroke-width": "1.5"})
    circle(svg, cx, ct_y + 10, 8, fill="none", stroke="#4FC3F7", **{"stroke-width": "1.5"})

    # ── Vertical line to load ──
    line(svg, cx, ct_y + 18, cx, ct_y + 50, stroke="#4FC3F7", **{"stroke-width": "2.5"})

    # ── Load / Equipment symbol ──
    load_y = ct_y + 55
    # Zigzag (impedance symbol)
    zz_points = f"M{cx},{load_y}"
    for k in range(4):
        zz_points += f" l8,10 l-16,10"
    zz_points += f" l8,10"
    path(svg, zz_points, fill="none", stroke="#FFB74D", **{"stroke-width": "2"})

    # ── Measurement panel ──
    panel_y = 340
    rect(svg, 15, panel_y, W - 30, 120, fill="#0d1f35", rx="6", ry="6",
         stroke="#1E88E5", **{"stroke-width": "0.8"})

    measurements = [
        ("P", "250.3", "kW", "#4FC3F7"),
        ("Q", "75.09", "kVAr", "#81C784"),
        ("I", "402.5", "A", "#FFB74D"),
        ("V", "22.1", "kV", "#CE93D8"),
        ("PF", "0.96", "", "#FF8A65"),
    ]
    for j, (label, val, unit, color) in enumerate(measurements):
        my = panel_y + 18 + j * 20
        text(svg, 30, my, label, fill="#78909C",
             **{"font-family": "Consolas, monospace", "font-size": "10", "font-weight": "bold"})
        text(svg, cx + 10, my, val, fill=color,
             **{"font-family": "Consolas, monospace", "font-size": "12",
                "text-anchor": "middle", "font-weight": "bold"})
        text(svg, W - 25, my, unit, fill="#546E7A",
             **{"font-family": "Consolas, monospace", "font-size": "9", "text-anchor": "end"})

    save_svg(svg, "busbar_v3_compact_feeder.svg")


# ═══════════════════════════════════════════════════════════════════════════════
# VARIANT 4: Vertical Busbar with Horizontal Feeders
# ═══════════════════════════════════════════════════════════════════════════════
def generate_busbar_v4():
    """
    Vertical busbar on the left with horizontal feeder taps branching right.
    Common in substation layouts. Dark theme with blue accents.
    """
    W, H = 900, 600
    svg = new_svg(W, H)
    defs = add_defs(svg)

    add_gradient(defs, "bgGrad4", "#0B1622", "#111E30")
    add_gradient(defs, "vBusGrad", "#D32F2F", "#F44336", x1="0%", y1="0%", x2="100%", y2="0%")
    add_glow_filter(defs, "redGlow4", "#F44336", 5)
    add_glow_filter(defs, "blueGlow4", "#2196F3", 4)

    # Background
    rect(svg, 0, 0, W, H, fill="url(#bgGrad4)", rx="8", ry="8")

    # Title
    text(svg, W // 2, 30, "SUBSTATION - VERTICAL BUSBAR ARRANGEMENT",
         fill="#64B5F6", **{"font-family": "'Segoe UI', sans-serif", "font-size": "15",
                           "font-weight": "bold", "text-anchor": "middle", "letter-spacing": "2"})

    # ── Vertical busbar ──
    vbus_x = 80
    vbus_y1 = 60
    vbus_y2 = H - 40
    vbus_w = 14

    # Shadow
    rect(svg, vbus_x + 2, vbus_y1 + 2, vbus_w, vbus_y2 - vbus_y1,
         fill="black", opacity="0.3", rx="3", ry="3")
    # Main bar
    rect(svg, vbus_x, vbus_y1, vbus_w, vbus_y2 - vbus_y1,
         fill="url(#vBusGrad)", rx="3", ry="3", filter="url(#redGlow4)",
         stroke="#EF5350", **{"stroke-width": "0.5"})

    # Bus voltage label
    text(svg, vbus_x + vbus_w / 2, vbus_y1 - 8, "11 kV", fill="#EF9A9A",
         **{"font-family": "Consolas, monospace", "font-size": "12",
            "text-anchor": "middle", "font-weight": "bold"})

    # ── Horizontal feeders ──
    feeder_labels = ["DG SET 1", "DG SET 2", "PV ARRAY", "BATTERY ESS", "WIND GEN", "MAIN LOAD"]
    feeder_icons = ["gen", "gen", "solar", "batt", "wind", "load"]
    num = len(feeder_labels)
    feeder_spacing = (vbus_y2 - vbus_y1 - 60) / (num - 1)

    for i in range(num):
        fy = vbus_y1 + 30 + i * feeder_spacing
        fg = group(svg, id=f"hfeed_{i}")

        # Horizontal line from bus
        h_end = 400
        line(fg, vbus_x + vbus_w, fy, h_end, fy,
             stroke="#42A5F5", **{"stroke-width": "2.5"})

        # Connection dot on bus
        circle(fg, vbus_x + vbus_w, fy, 4, fill="#F44336")

        # ── CB (at midpoint) ──
        cb_x = 200
        cb_s = 24
        rect(fg, cb_x - cb_s / 2, fy - cb_s / 2, cb_s, cb_s,
             fill="#00C853", rx="4", ry="4", stroke="#69F0AE", **{"stroke-width": "0.8"})
        # Closed symbol
        line(fg, cb_x - 7, fy, cb_x + 7, fy,
             stroke="white", **{"stroke-width": "2"})
        text(fg, cb_x, fy - cb_s / 2 - 5, f"CB{i + 1}",
             fill="#90A4AE", **{"font-family": "Consolas, monospace", "font-size": "9",
                                "text-anchor": "middle"})

        # ── CT ──
        ct_x = 300
        circle(fg, ct_x - 5, fy, 6, fill="none", stroke="#42A5F5", **{"stroke-width": "1.2"})
        circle(fg, ct_x + 5, fy, 6, fill="none", stroke="#42A5F5", **{"stroke-width": "1.2"})

        # ── Equipment box ──
        eq_x = 430
        eq_w = 160
        eq_h = 50
        rect(fg, eq_x, fy - eq_h / 2, eq_w, eq_h,
             fill="#0d1f35", rx="6", ry="6", stroke="#1565C0", **{"stroke-width": "1"})

        # Equipment name
        text(fg, eq_x + eq_w / 2, fy - 8, feeder_labels[i],
             fill="#64B5F6", **{"font-family": "'Segoe UI', sans-serif", "font-size": "12",
                                "text-anchor": "middle", "font-weight": "bold"})

        # Equipment readings
        pval = [250, 250, 150, 200, 100, 560][i]
        text(fg, eq_x + eq_w / 2, fy + 12, f"{pval} kW",
             fill="#4FC3F7", **{"font-family": "Consolas, monospace", "font-size": "11",
                                "text-anchor": "middle"})

        # ── Status indicator ──
        status_x = eq_x + eq_w + 20
        status_colors = ["#00E676", "#00E676", "#FFEB3B", "#00BCD4", "#00E676", "#FF9800"]
        status_texts = ["RUNNING", "RUNNING", "GENERATING", "CHARGING", "RUNNING", "ACTIVE"]
        circle(fg, status_x, fy - 5, 5, fill=status_colors[i])
        text(fg, status_x + 12, fy - 1, status_texts[i],
             fill=status_colors[i], **{"font-family": "Consolas, monospace", "font-size": "9"})

        # Power bar (visual gauge)
        bar_x = eq_x + eq_w + 15
        bar_max = 200
        bar_w = (pval / 600) * bar_max
        rect(fg, bar_x, fy + 8, bar_max, 6, fill="#1a2a3a", rx="3", ry="3")
        rect(fg, bar_x, fy + 8, bar_w, 6, fill=status_colors[i], rx="3", ry="3", opacity="0.8")

    save_svg(svg, "busbar_v4_vertical_feeders.svg")


# ═══════════════════════════════════════════════════════════════════════════════
# VARIANT 5: Microgrid Overview Busbar (inspired by Figure 17)
# ═══════════════════════════════════════════════════════════════════════════════
def generate_busbar_v5():
    """
    Microgrid-style overview showing a main bus ring connecting
    PV, Diesel, Wind, Battery, and Load zones.
    Inspired by Figure 17 overview display.
    """
    W, H = 1400, 650
    svg = new_svg(W, H)
    defs = add_defs(svg)

    add_gradient(defs, "bgGrad5", "#051225", "#0B1E36")
    add_gradient(defs, "busH", "#00ACC1", "#0097A7", x1="0%", y1="0%", x2="100%", y2="0%")
    add_gradient(defs, "busV", "#00ACC1", "#0097A7", x1="0%", y1="0%", x2="0%", y2="100%")
    add_glow_filter(defs, "tealGlow", "#00BCD4", 5)
    add_glow_filter(defs, "goldGlow", "#FFD600", 4)
    add_glow_filter(defs, "limeGlow", "#76FF03", 4)

    # Background
    rect(svg, 0, 0, W, H, fill="url(#bgGrad5)", rx="8", ry="8")

    # Title bar
    rect(svg, 0, 0, W, 44, fill="#063349", rx="8", ry="0")
    text(svg, W // 2, 28, "CON DAO ISLAND - MICROGRID OVERVIEW",
         fill="#4DD0E1", **{"font-family": "'Segoe UI', sans-serif", "font-size": "16",
                           "font-weight": "bold", "text-anchor": "middle", "letter-spacing": "3"})

    # System info badges
    badges_data = [("Freq", "50.0 Hz"), ("Voltage", "15.5 kV")]
    for bi, (blabel, bval) in enumerate(badges_data):
        bx = 100 + bi * 130
        rect(svg, bx - 50, 52, 110, 36, fill="#0a1e30", rx="6", ry="6",
             stroke="#00796B", **{"stroke-width": "1"})
        text(svg, bx + 5, 66, blabel, fill="#80CBC4",
             **{"font-family": "Consolas, monospace", "font-size": "9", "text-anchor": "middle"})
        text(svg, bx + 5, 82, bval, fill="#00E676",
             **{"font-family": "Consolas, monospace", "font-size": "13",
                "text-anchor": "middle", "font-weight": "bold"})

    # ══ Main bus ring ══
    # Top horizontal bus
    bus_top_y = 130
    bus_left = 100
    bus_right = W - 100
    bus_w = 8

    # Top bus
    rect(svg, bus_left, bus_top_y, bus_right - bus_left, bus_w,
         fill="url(#busH)", rx="2", ry="2", filter="url(#tealGlow)")

    # Bottom horizontal bus
    bus_bot_y = 480
    rect(svg, bus_left, bus_bot_y, bus_right - bus_left, bus_w,
         fill="url(#busH)", rx="2", ry="2", filter="url(#tealGlow)")

    # Left vertical bus
    rect(svg, bus_left, bus_top_y, bus_w, bus_bot_y - bus_top_y + bus_w,
         fill="url(#busV)", rx="2", ry="2", filter="url(#tealGlow)")

    # Right vertical bus
    rect(svg, bus_right - bus_w, bus_top_y, bus_w, bus_bot_y - bus_top_y + bus_w,
         fill="url(#busV)", rx="2", ry="2", filter="url(#tealGlow)")

    # ══ Source zones (on top bus) ══
    sources = [
        {"name": "PV PLANT", "power": "250.3 kW", "detail": "370W Panels", "color": "#FFD600",
         "glow": "url(#goldGlow)", "status": "GENERATING"},
        {"name": "BESS #1", "power": "120 kW", "detail": "SOC: 75%", "color": "#76FF03",
         "glow": "url(#limeGlow)", "status": "DISCHARGING"},
        {"name": "BESS #2", "power": "80 kW", "detail": "SOC: 62%", "color": "#76FF03",
         "glow": "url(#limeGlow)", "status": "CHARGING"},
    ]

    src_spacing = (bus_right - bus_left - 200) / (len(sources) - 1)
    for si, src in enumerate(sources):
        sx = bus_left + 100 + si * src_spacing
        sg = group(svg, id=f"source_{si}")

        # Connection line up from bus
        line(sg, sx, bus_top_y, sx, bus_top_y - 50,
             stroke=src["color"], **{"stroke-width": "2.5"})

        # Source box
        bw, bh = 140, 60
        rect(sg, sx - bw / 2, bus_top_y - 50 - bh, bw, bh,
             fill="#0a1e30", rx="6", ry="6", stroke=src["color"], **{"stroke-width": "1.2"})

        # Name
        text(sg, sx, bus_top_y - 50 - bh + 18, src["name"],
             fill=src["color"], **{"font-family": "'Segoe UI', sans-serif", "font-size": "12",
                                   "text-anchor": "middle", "font-weight": "bold"})
        # Power value
        text(sg, sx, bus_top_y - 50 - bh + 36, src["power"],
             fill="white", **{"font-family": "Consolas, monospace", "font-size": "14",
                              "text-anchor": "middle", "font-weight": "bold"})
        # Detail
        text(sg, sx, bus_top_y - 50 - bh + 50, src["detail"],
             fill="#78909C", **{"font-family": "Consolas, monospace", "font-size": "9",
                                "text-anchor": "middle"})

        # Connection dot
        circle(sg, sx, bus_top_y, 5, fill=src["color"], filter=src["glow"])

        # CB on connection
        cb_y = bus_top_y - 25
        rect(sg, sx - 10, cb_y - 10, 20, 20,
             fill="#00C853", rx="3", ry="3", opacity="0.85")
        line(sg, sx - 5, cb_y, sx + 5, cb_y,
             stroke="white", **{"stroke-width": "2"})

    # ══ Load zones (on bottom bus) ══
    loads = [
        {"name": "DG SET 1", "power": "402.5 kW", "status": "RUNNING", "color": "#FF6D00"},
        {"name": "DG SET 2", "power": "250.3 kW", "status": "RUNNING", "color": "#FF6D00"},
        {"name": "DG SET 3", "power": "0 kW", "status": "STANDBY", "color": "#78909C"},
        {"name": "DG SET 4", "power": "250.3 kW", "status": "RUNNING", "color": "#FF6D00"},
        {"name": "DG SET 5", "power": "0 kW", "status": "STANDBY", "color": "#78909C"},
    ]

    load_spacing = (bus_right - bus_left - 100) / (len(loads) - 1)
    for li, ld in enumerate(loads):
        lx = bus_left + 50 + li * load_spacing
        lg = group(svg, id=f"load_{li}")

        # Connection line down from bus
        line(lg, lx, bus_bot_y + bus_w, lx, bus_bot_y + bus_w + 50,
             stroke=ld["color"], **{"stroke-width": "2.5"})

        # CB
        cb_y = bus_bot_y + bus_w + 20
        is_on = ld["status"] == "RUNNING"
        cb_fill = "#00C853" if is_on else "#78909C"
        rect(lg, lx - 10, cb_y - 10, 20, 20,
             fill=cb_fill, rx="3", ry="3")
        if is_on:
            line(lg, lx - 5, cb_y, lx + 5, cb_y, stroke="white", **{"stroke-width": "2"})
        else:
            line(lg, lx - 5, cb_y - 5, lx + 5, cb_y + 5, stroke="white", **{"stroke-width": "1.5"})
            line(lg, lx + 5, cb_y - 5, lx - 5, cb_y + 5, stroke="white", **{"stroke-width": "1.5"})

        # Load box
        bw, bh = 130, 55
        rect(lg, lx - bw / 2, bus_bot_y + bus_w + 55, bw, bh,
             fill="#0a1e30", rx="6", ry="6", stroke=ld["color"], **{"stroke-width": "1"})

        text(lg, lx, bus_bot_y + bus_w + 75, ld["name"],
             fill=ld["color"], **{"font-family": "'Segoe UI', sans-serif", "font-size": "11",
                                  "text-anchor": "middle", "font-weight": "bold"})
        text(lg, lx, bus_bot_y + bus_w + 93, ld["power"],
             fill="white", **{"font-family": "Consolas, monospace", "font-size": "13",
                              "text-anchor": "middle", "font-weight": "bold"})
        text(lg, lx, bus_bot_y + bus_w + 107, ld["status"],
             fill=ld["color"], **{"font-family": "Consolas, monospace", "font-size": "9",
                                  "text-anchor": "middle"})

    # ══ Side zones (on vertical buses) ══
    # Wind on left
    wg = group(svg, id="wind_zone")
    wx = bus_left - 10
    wy = 300
    line(wg, bus_left, wy, wx - 60, wy, stroke="#00E5FF", **{"stroke-width": "2.5"})
    rect(wg, wx - 190, wy - 35, 130, 70,
         fill="#0a1e30", rx="6", ry="6", stroke="#00E5FF", **{"stroke-width": "1"})
    text(wg, wx - 125, wy - 12, "WIND FARM",
         fill="#00E5FF", **{"font-family": "'Segoe UI', sans-serif", "font-size": "12",
                           "text-anchor": "middle", "font-weight": "bold"})
    text(wg, wx - 125, wy + 8, "402.5 kW",
         fill="white", **{"font-family": "Consolas, monospace", "font-size": "14",
                          "text-anchor": "middle", "font-weight": "bold"})
    text(wg, wx - 125, wy + 24, "123.75 kVAr",
         fill="#4FC3F7", **{"font-family": "Consolas, monospace", "font-size": "10",
                           "text-anchor": "middle"})

    # Residential on right
    for ri, (rname, rpwr) in enumerate([("ZONE 1", "500 kW"), ("ZONE 2", "560 kW"), ("ZONE 3", "560 kW")]):
        rg = group(svg, id=f"res_{ri}")
        ry_pos = 200 + ri * 110
        rx = bus_right + 10

        line(rg, bus_right, ry_pos, rx + 60, ry_pos,
             stroke="#FF8A65", **{"stroke-width": "2.5"})

        rect(rg, rx + 65, ry_pos - 30, 120, 60,
             fill="#0a1e30", rx="6", ry="6", stroke="#FF8A65", **{"stroke-width": "1"})
        text(rg, rx + 125, ry_pos - 10, f"RESIDENTIAL",
             fill="#FF8A65", **{"font-family": "'Segoe UI', sans-serif", "font-size": "10",
                                "text-anchor": "middle", "font-weight": "bold"})
        text(rg, rx + 125, ry_pos + 5, rname,
             fill="#FFAB91", **{"font-family": "Consolas, monospace", "font-size": "11",
                                "text-anchor": "middle"})
        text(rg, rx + 125, ry_pos + 22, rpwr,
             fill="white", **{"font-family": "Consolas, monospace", "font-size": "12",
                              "text-anchor": "middle", "font-weight": "bold"})

    # ══ Total power summary ══
    summary_g = group(svg, id="summary")
    rect(summary_g, W // 2 - 120, 280, 240, 100,
         fill="#0a1e30", rx="8", ry="8", stroke="#00796B", **{"stroke-width": "1.2"})
    text(summary_g, W // 2, 305, "SYSTEM TOTALS",
         fill="#4DD0E1", **{"font-family": "'Segoe UI', sans-serif", "font-size": "12",
                           "text-anchor": "middle", "font-weight": "bold"})
    totals = [("Generation", "1153 kW", "#76FF03"), ("Load", "1620 kW", "#FF8A65"),
              ("Net Import", "467 kW", "#FFD600")]
    for ti, (tlabel, tval, tcolor) in enumerate(totals):
        ty = 325 + ti * 18
        text(summary_g, W // 2 - 80, ty, tlabel,
             fill="#78909C", **{"font-family": "Consolas, monospace", "font-size": "10"})
        text(summary_g, W // 2 + 80, ty, tval,
             fill=tcolor, **{"font-family": "Consolas, monospace", "font-size": "11",
                             "text-anchor": "end", "font-weight": "bold"})

    save_svg(svg, "busbar_v5_microgrid_overview.svg")


# ═══════════════════════════════════════════════════════════════════════════════
# VARIANT 6: Minimal Flat Busbar (clean Perspective style)
# ═══════════════════════════════════════════════════════════════════════════════
def generate_busbar_v6():
    """
    Ultra-clean, minimal flat design suitable for embedding in
    Perspective views. No glow effects - pure CSS-friendly styling.
    Uses class attributes for easy CSS targeting.
    """
    W, H = 1000, 300
    svg = new_svg(W, H)

    # Simple dark background
    rect(svg, 0, 0, W, H, fill="#1a1a2e", rx="4", ry="4")

    # ── Main busbar ──
    bus_y = 60
    bus_h = 6
    rect(svg, 40, bus_y, W - 80, bus_h, fill="#e94560", rx="1", ry="1",
         **{"class": "busbar-main"})

    # Section labels
    text(svg, 40, bus_y - 10, "BUS A - 480V", fill="#e94560",
         **{"font-family": "'Segoe UI', sans-serif", "font-size": "11",
            "font-weight": "600", "class": "bus-label"})

    # ── Feeders ──
    feeder_data = [
        ("MCC-1", "125A", True, "#00d2ff"),
        ("MCC-2", "200A", True, "#00d2ff"),
        ("XFMR-1", "500A", True, "#0fff50"),
        ("ATS-1", "300A", False, "#ff6b6b"),
        ("MCC-3", "150A", True, "#00d2ff"),
        ("SPARE", "—", False, "#555"),
    ]

    spacing = (W - 120) / len(feeder_data)
    for i, (fname, famp, closed, fcolor) in enumerate(feeder_data):
        fx = 80 + i * spacing
        fg = group(svg, **{"class": f"feeder feeder-{i}", "data-name": fname})

        # Vertical line
        line(fg, fx, bus_y + bus_h, fx, 160,
             stroke=fcolor if closed else "#333", **{"stroke-width": "2",
                                                      "class": "feeder-line"})

        # CB indicator (simple circle)
        cb_y = 110
        circle(fg, fx, cb_y, 8,
               fill=fcolor if closed else "#333",
               stroke=fcolor, **{"stroke-width": "1.5", "class": "cb-indicator"})
        # Inner state
        if closed:
            line(fg, fx - 4, cb_y, fx + 4, cb_y, stroke="white", **{"stroke-width": "1.5"})
        else:
            text(fg, fx, cb_y + 3.5, "x", fill="white",
                 **{"font-size": "8", "text-anchor": "middle", "font-weight": "bold"})

        # Feeder name
        text(fg, fx, 180, fname, fill=fcolor if closed else "#555",
             **{"font-family": "'Segoe UI', sans-serif", "font-size": "11",
                "text-anchor": "middle", "font-weight": "600", "class": "feeder-name"})

        # Amp rating
        text(fg, fx, 196, famp, fill="#888",
             **{"font-family": "Consolas, monospace", "font-size": "10",
                "text-anchor": "middle", "class": "feeder-rating"})

        # Status dot
        if fname != "SPARE":
            circle(fg, fx, 215, 3, fill=fcolor, **{"class": "status-dot"})

    # ── Bottom info bar ──
    rect(svg, 0, H - 40, W, 40, fill="#16213e", rx="0", ry="4")
    info_items = [("Total Load", "1,240 kW"), ("Power Factor", "0.96"),
                  ("Bus Voltage", "482V"), ("Frequency", "60.0 Hz")]
    for ii, (ilabel, ival) in enumerate(info_items):
        ix = 80 + ii * 240
        text(svg, ix, H - 18, ilabel, fill="#666",
             **{"font-family": "'Segoe UI', sans-serif", "font-size": "10"})
        text(svg, ix + 100, H - 18, ival, fill="#00d2ff",
             **{"font-family": "Consolas, monospace", "font-size": "11", "font-weight": "bold"})

    save_svg(svg, "busbar_v6_minimal_flat.svg")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("  BUSBAR SVG GENERATOR")
    print("  Generating SCADA-style busbar variants...")
    print("=" * 60)
    print()

    generators = [
        ("V1: Horizontal SLD (Dark, Orange Busbar)", generate_busbar_v1),
        ("V2: Neon Double Busbar (Cyberpunk)", generate_busbar_v2),
        ("V3: Compact Feeder Module (Component)", generate_busbar_v3),
        ("V4: Vertical Busbar + Feeders (Substation)", generate_busbar_v4),
        ("V5: Microgrid Overview (Ring Bus)", generate_busbar_v5),
        ("V6: Minimal Flat (Perspective-ready)", generate_busbar_v6),
    ]

    for name, gen_fn in generators:
        print(f"Generating {name}...")
        try:
            gen_fn()
        except Exception as e:
            print(f"  [ERROR] {e}")

    print()
    print("=" * 60)
    print(f"  All SVGs saved to: {OUTPUT_DIR}")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Open in Inkscape:  inkscape output/<file>.svg")
    print("  2. Export to PNG:     inkscape --export-type=png output/<file>.svg")
    print("  3. Import into Perspective as embedded SVG components")
    print()
