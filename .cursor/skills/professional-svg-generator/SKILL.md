---
name: professional-svg-generator
description: Generates high-quality, professional-grade 2D and isometric SVGs for industrial components, strictly adhering to the quality and stylistic standards found in the example-svgs/ directory.
---

# Professional SVG Generator

This skill guides the agent in generating high-quality, professional-grade 2D and isometric SVGs. All generated SVGs must strictly adhere to the quality and stylistic standards found in the `example-svgs/` directory.

## 1. Strict Quality Directives

- **NO LEGACY SCRIPTS**: You are explicitly forbidden from using older, low-quality scripts (e.g., `generate_motor_svg.py`) or previously generated low-quality SVGs as references.
- **REFERENCE ONLY `example-svgs/`**: Base all stylistic choices (colors, gradients, stroke widths, layering) *only* on the provided high-quality examples (e.g., `compressor_iso_blue.svg`, `gasturbineengine_1.svg`).
- **INDUSTRIAL AESTHETIC**: The output must look professional, precise, and technical. Avoid cartoonish or overly simplistic styles.

## 2. Decision Matrix: Raw SVG vs. Python Script

When asked to generate an SVG, first decide the best approach based on the complexity and requirements of the request:

### Approach A: Raw SVG (Direct XML Generation)
**Use when:**
- The request is for a simpler 2D icon or flat design.
- Specific, intricate vector paths are provided or needed.
- The design relies heavily on complex gradients and shading rather than repetitive geometry.

**Instructions:**
- Generate the raw SVG code directly in your response or write it to a `.svg` file.
- Heavily utilize `<linearGradient>` and `<radialGradient>` to simulate lighting and volume.
- Group elements logically using `<g>` tags.

### Approach B: Python Script Generation
**Use when:**
- The request is for a complex isometric structure.
- The design contains repetitive geometric patterns (e.g., cooling fins, grilles, arrays of pipes).
- Parameterized designs are required where mathematical precision (like 30-degree isometric projections) is necessary.

**Instructions:**
- Write a Python script that generates the SVG file.
- The script must implement the strict color palettes and shading techniques defined in the style guide.
- Ensure the script outputs clean, well-formatted XML.

## 3. Stylistic Requirements

You must follow the detailed styling rules outlined in the style guide.

**Key Requirements:**
- **Depth and Volume**: Use lighting, shading, and gradients to give 2D shapes a 3D or volumetric appearance.
- **Layering**: Use semantic `<g>` tags to organize components logically (e.g., `<g id="motor_housing">`).
- **Color Palettes**: Utilize professional industrial palettes (e.g., deep blues, steel grays, copper/orange highlights).
- **Precision**: Ensure crisp edges, consistent stroke widths, and proper alignment.

> **Important:** Always read `references/svg-style-guide.md` before generating an SVG or a Python script to ensure you are using the correct color codes and shading techniques.

## 4. Workflow

1. **Analyze Request**: Determine if the request requires a Raw SVG or a Python Script based on the Decision Matrix.
2. **Read Style Guide**: Review `references/svg-style-guide.md` for the approved color palettes and shading techniques.
3. **Draft/Generate**:
   - If Raw SVG: Draft the SVG structure, apply gradients/colors, and output the file.
   - If Python Script: Write the script, ensuring it uses the approved colors and isometric/geometric logic, then execute it to generate the SVG.
4. **Review**: Ensure the output matches the professional industrial aesthetic of the `example-svgs/` directory.
