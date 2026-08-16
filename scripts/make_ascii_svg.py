"""
make_ascii_svg.py
Converts source-prepped.png into a monochrome, self-typing ASCII-art SVG.
Each row wipes in left-to-right, staggered top to bottom, then freezes.
"""

import os
from PIL import Image
from xml.sax.saxutils import escape

IN_PATH = "source-prepped.png"
OUT_PATH = "avi-ascii.svg"

RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense)

COLS = 100
ROWS = 53
CHAR_W = 6.2
CHAR_H = 11
FONT_SIZE = 11
COLOR = "#c9d1d9"


def image_to_ascii_grid(path, cols, rows):
    img = Image.open(path).convert("L")
    img = img.resize((cols, rows))
    pixels = list(img.getdata())

    grid = []
    ramp_len = len(RAMP)
    for r in range(rows):
        row_chars = []
        for c in range(cols):
            brightness = pixels[r * cols + c]  # 0=black, 255=white
            # invert so bright -> sparse (start of ramp), dark -> dense
            idx = int((255 - brightness) / 255 * (ramp_len - 1))
            row_chars.append(RAMP[idx])
        grid.append("".join(row_chars))
    return grid


def render(grid):
    width = COLS * CHAR_W
    height = ROWS * CHAR_H

    svg = [f'<svg viewBox="0 0 {width:.0f} {height:.0f}" xmlns="http://www.w3.org/2000/svg" font-family="Consolas, Menlo, monospace">']
    svg.append(f'<rect width="{width:.0f}" height="{height:.0f}" fill="none"/>')

    svg.append("<defs>")
    for r in range(ROWS):
        y = r * CHAR_H
        svg.append(
            f'<clipPath id="clip{r}"><rect x="0" y="{y:.1f}" width="0" height="{CHAR_H}">'
            f'<animate attributeName="width" from="0" to="{width:.0f}" '
            f'begin="{r * 0.05:.2f}s" dur="0.35s" fill="freeze"/>'
            f'</rect></clipPath>'
        )
    svg.append("</defs>")

    svg.append(f'<style>text{{font-size:{FONT_SIZE}px; fill:{COLOR};}}</style>')

    for r, row in enumerate(grid):
        y = (r + 1) * CHAR_H - 2
        line = escape(row)
        svg.append(f'<g clip-path="url(#clip{r})">')
        svg.append(f'<text x="0" y="{y:.1f}" xml:space="preserve">{line}</text>')
        svg.append("</g>")

    svg.append("</svg>")
    return "\n".join(svg)


def main():
    if not os.path.exists(IN_PATH):
        raise SystemExit(f"{IN_PATH} not found -- run prep_photo.py first.")
    grid = image_to_ascii_grid(IN_PATH, COLS, ROWS)
    svg = render(grid)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH} ({COLS}x{ROWS} chars)")


if __name__ == "__main__":
    main()