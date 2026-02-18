#!/usr/bin/env python3
"""Generate Logo_color.png from Logo.svg by replacing CSS variable placeholders with hardcoded colors.

Requires: pip install cairosvg
"""

import os
import sys

SVG_PATH = os.path.join(os.path.dirname(__file__), "../frontend/src/assets/Logo.svg")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "../frontend/src/assets/Logo_color.svg")

COLORS = {
    "var(--primary-start)": "#a8edea",
    "var(--primary-mid)": "#686de0",
    "var(--primary-end)": "#4834d4",
}

with open(SVG_PATH) as f:
    svg = f.read()

for placeholder, color in COLORS.items():
    svg = svg.replace(placeholder, color)

with open(OUTPUT_PATH, "w") as f:
    f.write(svg)
print(f"Generated {OUTPUT_PATH}")
