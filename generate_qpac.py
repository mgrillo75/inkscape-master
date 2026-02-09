#!/usr/bin/env python3
"""
Isometric (2.5D) QPAC Enclosure SVG Generator
===============================================
Generates a single isometric SVG of an empty QPAC power unit enclosure.
The QPAC is a large industrial container housing 4 gensets, with:
  - Base skid
  - Lower enclosed equipment bays (louvered panels)
  - Upper structural frame (open steel)
  - Roof canopy with corrugation
  - Yellow exhaust duct manifold + vertical stacks + rain caps
  - Access stairs & walkway
"""

import os, math
import xml.etree.ElementTree as ET
from xml.dom import minidom

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "mv_sld")
os.makedirs(OUT, exist_ok=True)
NS = "http://www.w3.org/2000/svg"

# ── Isometric math ────────────────────────────────────────────────────────────
COS30 = math.cos(math.radians(30))
SIN30 = math.sin(math.radians(30))

OX, OY = 500, 420  # screen offset

def iso(x, y, z=0):
    return (OX + (x - y) * COS30,
            OY + (x + y) * SIN30 - z)

def quad_pts(corners):
    return " ".join(f"{iso(*c)[0]:.1f},{iso(*c)[1]:.1f}" for c in corners)

def face_top(x, y, z, w, d):
    return quad_pts([(x,y,z), (x+w,y,z), (x+w,y+d,z), (x,y+d,z)])

def face_front(x, y, z, w, h):
    """Front = right in iso (facing viewer at y=const, low y)."""
    return quad_pts([(x,y,z), (x+w,y,z), (x+w,y,z-h), (x,y,z-h)])

def face_side(x, y, z, d, h):
    """Side = left in iso (facing viewer at x=const, low x)."""
    return quad_pts([(x,y,z), (x,y+d,z), (x,y+d,z-h), (x,y,z-h)])


# ── SVG helpers ───────────────────────────────────────────────────────────────
def new_svg(w, h):
    ET.register_namespace("", NS)
    return ET.Element("svg", {"xmlns": NS, "width": str(w), "height": str(h),
                               "viewBox": f"0 0 {w} {h}"})

def el(p, tag, **kw):
    a = {}
    for k, v in kw.items():
        key = k.replace("_", "-") if len(k) > 2 and k not in (
            "d","id","r","x","y","cx","cy","rx","ry","x1","y1","x2","y2") else k
        a[key] = str(v)
    return ET.SubElement(p, tag, a)

def poly(p, pts, **kw):
    return el(p, "polygon", points=pts, **kw)

def iline(p, p1, p2, **kw):
    s1, s2 = iso(*p1), iso(*p2)
    return el(p, "line", x1=f"{s1[0]:.1f}", y1=f"{s1[1]:.1f}",
              x2=f"{s2[0]:.1f}", y2=f"{s2[1]:.1f}", **kw)

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
    print(f"  [OK] {fp}")


# ── Palette ───────────────────────────────────────────────────────────────────
# Designed for DARK backgrounds (Ignition Perspective / SCADA).
# All colors are bright/light enough to pop against #0f172a-style backgrounds.
# NO low-opacity fills -- everything is solid and visible.

S_TOP    = "#e2e8f0"    # Slate-200 (bright for tops)
S_FRONT  = "#cbd5e1"    # Slate-300
S_SIDE   = "#d6dce4"    # Slate-250
S_DARK   = "#94a3b8"    # Slate-400
S_EDGE   = "#475569"    # Slate-600 (strong edge)

# Lower panels
P_FRONT  = "#c0c9d4"    # lighter panel fronts
P_SIDE   = "#d0d8e2"
P_LOUVER = "#8896a5"    # darker louver grooves
P_HILITE = "#eef1f5"    # bright louver highlights

# Frame beams
F_LIGHT  = "#f1f5f9"    # Slate-100 (very bright beams)
F_MID    = "#e2e8f0"    # Slate-200
F_DARK   = "#94a3b8"    # Slate-400

# Base skid
B_TOP    = "#64748b"    # Slate-500
B_FRONT  = "#475569"    # Slate-600
B_SIDE   = "#5a6a7e"

# Yellow exhaust ducts (already bright, keep as-is)
Y_TOP    = "#fde047"    # yellow-300
Y_FRONT  = "#eab308"    # yellow-500
Y_SIDE   = "#f5d44e"
Y_DARK   = "#a16207"    # yellow-700
Y_HILITE = "#fef9c3"    # yellow-100

# Caps
C_TOP    = "#e2e8f0"
C_SIDE   = "#b0bcc8"

# Roof
R_TOP    = "#d6dce6"
R_FRONT  = "#94a3b8"
R_SIDE   = "#aab5c2"

EW = "1"  # edge stroke width (thicker for visibility)


# ── QPAC dimensions ──────────────────────────────────────────────────────────
W  = 380    # width (x)
D  = 190    # depth (y)
BH = 18     # base height
LH = 130    # lower section height
UH = 105    # upper frame height
RH = 10     # roof thickness

BAYS = 4
DUCTS = 5


def generate_qpac():
    svg = new_svg(1050, 780)
    defs = el(svg, "defs")

    # ── IMPORTANT: explicit background so it shows on ANY Ignition view ──
    # Remove or change this rect if you want transparent background.
    el(svg, "rect", x="0", y="0", width="1050", height="780",
       fill="#0f172a", rx="0", ry="0")  # Slate-900 dark bg

    z0 = 0           # ground
    z1 = BH           # top of base
    z2 = z1 + LH      # top of lower section
    z3 = z2 + UH      # top of upper frame
    z4 = z3 + RH      # top of roof

    # ══════════════════════════════════════════════════════════════════════
    # LAYER 1: BASE SKID
    # ══════════════════════════════════════════════════════════════════════
    g_base = el(svg, "g", id="base")

    poly(g_base, face_top(0, 0, z1, W, D),
         fill=B_TOP, stroke=S_EDGE, stroke_width=EW)
    poly(g_base, face_front(0, 0, z1, W, BH),
         fill=B_FRONT, stroke=S_EDGE, stroke_width=EW)
    poly(g_base, face_side(0, 0, z1, D, BH),
         fill=B_SIDE, stroke=S_EDGE, stroke_width=EW)

    # Skid rails (two horizontal beams on bottom front)
    for ry in [15, D - 15]:
        poly(g_base, face_front(0, ry, z1 - 3, W, 6),
             fill="#2d3748", stroke=S_EDGE, stroke_width="0.4")

    # ══════════════════════════════════════════════════════════════════════
    # LAYER 2: LOWER EQUIPMENT SECTION (enclosed, louvered)
    # ══════════════════════════════════════════════════════════════════════
    g_lower = el(svg, "g", id="lower_section")

    bay_w = W / BAYS

    # -- BACK WALL (drawn first, behind everything) --
    poly(g_lower, face_front(0, D, z2, W, LH),
         fill=S_DARK, stroke=S_EDGE, stroke_width=EW)

    # -- LEFT SIDE WALL (full panel) --
    poly(g_lower, face_side(0, 0, z2, D, LH),
         fill=P_SIDE, stroke=S_EDGE, stroke_width=EW)

    # Side louvers
    n_louv = 12
    for li in range(n_louv):
        lz = z2 - (li + 1) * (LH / (n_louv + 1))
        iline(g_lower, (0, 8, lz), (0, D - 8, lz),
              stroke=P_LOUVER, stroke_width="1.2")
        iline(g_lower, (0, 8, lz + 2.5), (0, D - 8, lz + 2.5),
              stroke=P_HILITE, stroke_width="0.5")

    # -- FRONT FACE (4 bay panels with louvers) --
    for i in range(BAYS):
        bx = i * bay_w
        bg = el(g_lower, "g", id=f"bay_{i}")

        # Panel background
        poly(bg, face_front(bx + 3, 0, z2, bay_w - 6, LH),
             fill=P_FRONT, stroke=S_EDGE, stroke_width=EW)

        # Louver slats
        for li in range(n_louv):
            lz = z2 - (li + 1) * (LH / (n_louv + 1))
            iline(bg, (bx + 8, 0, lz), (bx + bay_w - 8, 0, lz),
                  stroke=P_LOUVER, stroke_width="1.3")
            iline(bg, (bx + 8, 0, lz + 2.5), (bx + bay_w - 8, 0, lz + 2.5),
                  stroke=P_HILITE, stroke_width="0.6")

        # Bay divider post (structural column between bays)
        if i > 0:
            pw = 6
            poly(bg, face_front(bx - pw/2, 0, z2, pw, LH),
                 fill=F_LIGHT, stroke=S_EDGE, stroke_width="0.4")

    # Corner columns on front
    cw = 8
    poly(g_lower, face_front(0, 0, z2, cw, LH),
         fill=F_LIGHT, stroke=S_EDGE, stroke_width="0.4")
    poly(g_lower, face_front(W - cw, 0, z2, cw, LH),
         fill=F_LIGHT, stroke=S_EDGE, stroke_width="0.4")

    # Top edge trim (horizontal beam at top of lower section)
    trim_h = 5
    poly(g_lower, face_front(0, 0, z2, W, trim_h),
         fill=F_LIGHT, stroke=S_EDGE, stroke_width="0.4")
    poly(g_lower, face_side(0, 0, z2, D, trim_h),
         fill=F_MID, stroke=S_EDGE, stroke_width="0.4")

    # Floor plate between lower and upper (visible top face)
    poly(g_lower, face_top(0, 0, z2, W, D),
         fill=S_DARK, stroke=S_EDGE, stroke_width=EW)

    # ══════════════════════════════════════════════════════════════════════
    # LAYER 3: UPPER STRUCTURAL FRAME (open steel)
    # ══════════════════════════════════════════════════════════════════════
    g_upper = el(svg, "g", id="upper_frame")

    bw = 6  # beam width

    # -- Columns --
    # Back columns (draw first)
    for cx in [0, W - bw]:
        poly(g_upper, face_front(cx, D - bw, z3, bw, UH),
             fill=S_DARK, stroke=S_EDGE, stroke_width="0.6")

    # Intermediate columns on back
    for i in range(1, BAYS):
        poly(g_upper, face_front(i * bay_w - bw/2, D - bw, z3, bw, UH),
             fill=S_DARK, stroke=S_EDGE, stroke_width="0.6")

    # Back horizontal beams
    for bz in [z3, z2 + UH * 0.45]:
        poly(g_upper, face_front(0, D - bw, bz, W, bw),
             fill=S_DARK, stroke=S_EDGE, stroke_width="0.5")

    # Side (left) columns
    poly(g_upper, face_side(0, 0, z3, bw, UH),
         fill=F_MID, stroke=S_EDGE, stroke_width="0.6")
    poly(g_upper, face_side(0, D - bw, z3, bw, UH),
         fill=S_DARK, stroke=S_EDGE, stroke_width="0.6")

    # Side horizontal beams
    for bz in [z3, z2 + UH * 0.45]:
        poly(g_upper, face_side(0, 0, bz, D, bw),
             fill=F_MID, stroke=S_EDGE, stroke_width="0.6")

    # Side cross-bracing
    iline(g_upper, (0, 10, z3 - 10), (0, D - 10, z2 + 10),
          stroke=F_DARK, stroke_width="1.5")
    iline(g_upper, (0, 10, z2 + 10), (0, D - 10, z3 - 10),
          stroke=F_DARK, stroke_width="1.5")

    # Front columns (draw on top)
    for cx in [0, W - bw]:
        poly(g_upper, face_front(cx, 0, z3, bw, UH),
             fill=F_LIGHT, stroke=S_EDGE, stroke_width="0.5")
        poly(g_upper, face_side(cx, 0, z3, bw, UH),
             fill=F_MID, stroke=S_EDGE, stroke_width="0.4")

    # Intermediate front columns
    for i in range(1, BAYS):
        cx = i * bay_w - bw / 2
        poly(g_upper, face_front(cx, 0, z3, bw, UH),
             fill=F_LIGHT, stroke=S_EDGE, stroke_width="0.5")

    # Front horizontal beams
    for bz in [z3, z2 + UH * 0.45]:
        poly(g_upper, face_front(0, 0, bz, W, bw),
             fill=F_LIGHT, stroke=S_EDGE, stroke_width="0.5")

    # Front cross-bracing (per bay)
    for i in range(BAYS):
        x0 = i * bay_w + 10
        x1_brace = (i + 1) * bay_w - 10
        iline(g_upper, (x0, 0, z3 - 10), (x1_brace, 0, z2 + 10),
              stroke=F_DARK, stroke_width="1.2")
        iline(g_upper, (x0, 0, z2 + 10), (x1_brace, 0, z3 - 10),
              stroke=F_DARK, stroke_width="1.2")

    # Right side columns + beams (far side, partly visible)
    poly(g_upper, face_front(W - bw, 0, z3, bw, UH),
         fill=F_LIGHT, stroke=S_EDGE, stroke_width="0.4")

    # ══════════════════════════════════════════════════════════════════════
    # LAYER 4: EXHAUST DUCTS (yellow)
    # ══════════════════════════════════════════════════════════════════════
    g_ducts = el(svg, "g", id="exhaust_ducts")

    duct_r = 16  # half-width of each duct
    duct_yc = D * 0.45  # y center of duct row
    duct_z_bot = z2 + 15
    duct_z_top = z4 + 30  # poke above roof

    # Horizontal collector manifold
    coll_h = 24
    coll_z = z2 + 20

    # Collector front face
    poly(g_ducts, face_front(25, duct_yc - coll_h/2, coll_z + coll_h, W - 50, coll_h),
         fill=Y_FRONT, stroke=Y_DARK, stroke_width="0.8")
    # Collector top face
    poly(g_ducts, face_top(25, duct_yc - coll_h/2, coll_z + coll_h, W - 50, coll_h),
         fill=Y_TOP, stroke=Y_DARK, stroke_width="0.5")
    # Collector highlight
    poly(g_ducts, face_front(28, duct_yc - coll_h/2, coll_z + coll_h, W - 56, 3),
         fill=Y_HILITE, stroke="none")

    # Vertical stack stubs (below roof only -- rest drawn above roof in layer 6)
    for i in range(DUCTS):
        dx = 35 + i * (W - 70) / (DUCTS - 1)
        stub_top = z3  # up to roof level only
        poly(g_ducts, face_front(dx - duct_r, duct_yc - duct_r, stub_top,
                                  duct_r * 2, stub_top - coll_z - coll_h),
             fill=Y_FRONT, stroke=Y_DARK, stroke_width="0.7")
        poly(g_ducts, face_side(dx - duct_r, duct_yc - duct_r, stub_top,
                                 duct_r * 2, stub_top - coll_z - coll_h),
             fill=Y_SIDE, stroke=Y_DARK, stroke_width="0.7")

    # ══════════════════════════════════════════════════════════════════════
    # LAYER 5: ROOF / CANOPY
    # ══════════════════════════════════════════════════════════════════════
    g_roof = el(svg, "g", id="roof")

    ov = 22  # overhang
    rx, ry_ = -ov, -ov
    rw, rd = W + ov * 2, D + ov * 2

    # Roof top face (solid - ducts poke through above it)
    poly(g_roof, face_top(rx, ry_, z4, rw, rd),
         fill=R_TOP, stroke=S_EDGE, stroke_width=EW)

    # Corrugation lines on roof
    for ci in range(14):
        frac = (ci + 1) / 15
        cy_c = ry_ + frac * rd
        iline(g_roof, (rx + 5, cy_c, z4), (rx + rw - 5, cy_c, z4),
              stroke=S_EDGE, stroke_width="0.5")

    # Front edge of roof
    poly(g_roof, face_front(rx, ry_, z4, rw, RH),
         fill=R_FRONT, stroke=S_EDGE, stroke_width=EW)
    # Side edge of roof
    poly(g_roof, face_side(rx, ry_, z4, rd, RH),
         fill=R_SIDE, stroke=S_EDGE, stroke_width=EW)

    # Overhang support brackets (front)
    for bi in range(6):
        bx = ov + bi * (W / 5)
        # Bracket: vertical + diagonal
        iline(g_roof, (bx, -ov, z3), (bx, 0, z3),
              stroke=F_LIGHT, stroke_width="1.5")
        iline(g_roof, (bx, 0, z3), (bx, -ov * 0.5, z4 - 2),
              stroke=F_LIGHT, stroke_width="1")

    # Overhang support brackets (side)
    for bi in range(4):
        by = ov + bi * (D / 3)
        iline(g_roof, (0, by, z3), (-ov, by, z3),
              stroke=F_MID, stroke_width="1.2")

    # ══════════════════════════════════════════════════════════════════════
    # LAYER 6: EXHAUST STACKS + CAPS (above roof)
    # ══════════════════════════════════════════════════════════════════════
    g_caps = el(svg, "g", id="exhaust_above_roof")
    cap_h = 22
    cap_s = duct_r * 2 + 12  # slightly wider than duct

    for i in range(DUCTS):
        dx = 35 + i * (W - 70) / (DUCTS - 1)

        # Vertical stack portion ABOVE roof
        poly(g_caps, face_front(dx - duct_r, duct_yc - duct_r, duct_z_top,
                                 duct_r * 2, duct_z_top - z4),
             fill=Y_FRONT, stroke=Y_DARK, stroke_width="0.8")
        poly(g_caps, face_side(dx - duct_r, duct_yc - duct_r, duct_z_top,
                                duct_r * 2, duct_z_top - z4),
             fill=Y_SIDE, stroke=Y_DARK, stroke_width="0.8")
        poly(g_caps, face_top(dx - duct_r, duct_yc - duct_r, duct_z_top,
                               duct_r * 2, duct_r * 2),
             fill=Y_TOP, stroke=Y_DARK, stroke_width="0.6")

        # Rain cap on top
        cap_z = duct_z_top + cap_h
        poly(g_caps, face_front(dx - cap_s/2, duct_yc - cap_s/2, cap_z, cap_s, cap_h),
             fill=C_SIDE, stroke=S_EDGE, stroke_width="0.6")
        poly(g_caps, face_side(dx - cap_s/2, duct_yc - cap_s/2, cap_z, cap_s, cap_h),
             fill="#b8c4d0", stroke=S_EDGE, stroke_width="0.6")
        poly(g_caps, face_top(dx - cap_s/2 + 2, duct_yc - cap_s/2 + 2, cap_z,
                               cap_s - 4, cap_s - 4),
             fill=C_TOP, stroke=S_EDGE, stroke_width="0.6")

    # ══════════════════════════════════════════════════════════════════════
    # LAYER 7: ACCESS STAIRS & WALKWAY
    # ══════════════════════════════════════════════════════════════════════
    g_stairs = el(svg, "g", id="stairs")

    # Platform walkway along left side
    walk_w = 22
    poly(g_stairs, face_top(-walk_w, 0, z2, walk_w, D),
         fill=S_TOP, stroke=S_EDGE, stroke_width="0.8")
    # Walkway edge
    poly(g_stairs, face_side(-walk_w, 0, z2, D, 4),
         fill=F_MID, stroke=S_EDGE, stroke_width="0.4")

    # Railing along walkway
    rail_h = 38
    iline(g_stairs, (-walk_w, 0, z2 + rail_h), (-walk_w, D, z2 + rail_h),
          stroke=F_LIGHT, stroke_width="1.3")
    # Railing posts
    for rp in range(5):
        py = rp * (D / 4)
        iline(g_stairs, (-walk_w, py, z2), (-walk_w, py, z2 + rail_h),
              stroke=F_LIGHT, stroke_width="1")

    # Staircase
    sx = -walk_w - 5
    sd = 30
    sy = 55
    num_steps = 9
    step_h = LH / num_steps

    for si in range(num_steps):
        sz = z1 + si * step_h
        # Tread (top)
        poly(g_stairs, face_top(sx, sy, sz + step_h, 18, sd),
             fill=S_TOP, stroke=S_EDGE, stroke_width="0.4")
        # Riser (side)
        poly(g_stairs, face_side(sx, sy, sz + step_h, sd, step_h),
             fill=S_SIDE, stroke=S_EDGE, stroke_width="0.4")

    # Stair handrails
    iline(g_stairs, (sx, sy, z2 + rail_h), (sx, sy, z1 + 20),
          stroke=F_LIGHT, stroke_width="1.3")
    iline(g_stairs, (sx, sy + sd, z2 + rail_h), (sx, sy + sd, z1 + 20),
          stroke=F_LIGHT, stroke_width="1.3")
    iline(g_stairs, (sx, sy, z2 + rail_h), (sx, sy + sd, z2 + rail_h),
          stroke=F_LIGHT, stroke_width="1.3")

    save(svg, "qpac_empty.svg")


# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("  QPAC ISOMETRIC SVG GENERATOR")
    print("=" * 60)
    generate_qpac()
    print("  Done!")
    print("=" * 60)
