# Professional SVG Style Guide

This document defines the stylistic standards, color palettes, and structural patterns required for generating professional-grade industrial SVGs. These standards are derived strictly from the high-quality reference files in the `example-svgs/` directory.

## 1. Core Principles

- **Industrial Aesthetic**: Designs must look professional, precise, and technical. Avoid cartoonish or overly simplistic styles.
- **Depth and Volume**: Use lighting, shading, and gradients to give 2D shapes a 3D or volumetric appearance (isometric or flat-shaded).
- **Clean Structure**: Use semantic grouping (`<g>`) to organize components logically.
- **Precision**: Ensure crisp edges, consistent stroke widths, and proper alignment.

## 2. Shading Techniques

### Technique A: Flat Isometric Shading (e.g., `compressor_iso_blue.svg`)
Used for complex 3D isometric structures without gradients. Depth is achieved by applying a strict 3-tone color logic to the faces of objects:
- **Top Faces (Light)**: Receives the most light. Use the lightest shade in the palette.
- **Front Faces (Mid)**: Receives ambient light. Use the base/mid shade.
- **Side Faces (Dark)**: In shadow. Use the darkest shade.

### Technique B: Gradient Volume Shading (e.g., `gasturbineengine_1.svg`)
Used for 2D flat designs that need to simulate cylindrical or metallic volumes.
- **Cylinders/Pipes**: Use `<linearGradient>` perpendicular to the cylinder's axis.
- **Metallic Reflection**: Gradients should have multiple stops to simulate highlights and shadows.
  - *Example Structure*: Dark Edge (0%) -> Bright Highlight (70-85%) -> Mid Edge (100%).

## 3. Approved Color Palettes

### Industrial Blue (Primary Machinery)
- **Highlight / Top**: `#64A9D4`, `#A2D3F2`, `#4091C2`
- **Mid / Front**: `#306D91`, `#377CA6`
- **Shadow / Side**: `#255470`, `#2C5B91`
- **Deep Accent**: `#035DC4`

### Silver / Steel (Pipes, Casings, Mounts)
- **Highlight**: `#FFFFFF`
- **Mid**: `#CCCCCC`
- **Shadow**: `#808080`, `#999999`
- *Gradient Example*: `#808080` (0%) -> `#FFFFFF` (77%) -> `#CCCCCC` (100%)

### Copper / Bronze (Coils, Heat Exchangers, Accents)
- **Highlight**: `#FFBB66`, `#F2A54C`
- **Mid**: `#F0943A`, `#E48E30`
- **Shadow**: `#D2700C`, `#CC6600`
- *Gradient Example*: `#F0943A` (0%) -> `#FFBB66` (15%) -> `#F2A54C` (23%) -> `#CC6600` (99%)

### Reddish Copper / Rust (Valves, Specialized Components)
- **Highlight**: `#C18184`
- **Shadow**: `#5C393A`

## 4. Structural Patterns

- **Grouping**: Group related elements together (e.g., `<g id="motor_housing">`, `<g id="cooling_fins">`).
- **Gradients**: Define all gradients in a `<defs>` block at the top of the SVG.
- **Strokes**: Use subtle strokes (e.g., `#255470` or `#000000` with low opacity) to define edges where colors blend together, but rely primarily on fill colors for structure.
- **Scale**: Design within a consistent `viewBox` (e.g., `0 0 400 400`) and use relative sizing.
