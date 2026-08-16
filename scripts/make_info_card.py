"""
make_info_card.py
Hand-authors a neofetch-style SVG panel. Lines fade + slide in with a
short stagger. Set STATIC=1 to emit a frozen (non-animated) frame.
"""

import os
from xml.sax.saxutils import escape

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "info-card.svg")

# ---- Edit this section with your own info ----
TITLE = "vivrz@github"
ROWS = [
    ("Now", "Building cool stuff with python & JS and exploring AI , RAG ."),
    ("Prev", "Previously worked at Hestabit Technologies as an Assocaite Software developer (Build an internal tool - HestaWiki ent-to-end)"),
    ("Stack", "Python, JavaScript, Langchain , Langraph , RAG , Agentic AI , Docker , Nginx "),
    ("Highlights", "Solved around 500 problems on Leetcode ."),
]
# ------------------------------------------------

WIDTH = 490
ROW_H = 26
TOP_PAD = 50
LEFT_PAD = 20

STATIC = os.environ.get("STATIC", "0") == "1"


def render():
    height = TOP_PAD + len(ROWS) * ROW_H + 30
    svg = [f'<svg viewBox="0 0 {WIDTH} {height}" xmlns="http://www.w3.org/2000/svg" font-family="Consolas, Menlo, monospace">']

    svg.append(f'<rect width="{WIDTH}" height="{height}" rx="8" fill="#0d1117" stroke="#30363d"/>')

    # title bar
    svg.append(f'<rect x="0" y="0" width="{WIDTH}" height="34" rx="8" fill="#161b22"/>')
    svg.append('<circle cx="18" cy="17" r="5" fill="#ff5f56"/>')
    svg.append('<circle cx="36" cy="17" r="5" fill="#ffbd2e"/>')
    svg.append('<circle cx="54" cy="17" r="5" fill="#27c93f"/>')
    svg.append(f'<text x="{WIDTH/2}" y="21" text-anchor="middle" font-size="12" fill="#8b949e">{TITLE}</text>')

    if not STATIC:
        svg.append(
            "<style>"
            ".line{opacity:0;animation:fadeslide .4s ease-out forwards;}"
            "@keyframes fadeslide{from{opacity:0;transform:translateX(-8px);}"
            "to{opacity:1;transform:translateX(0);}}"
            "</style>"
        )

    for i, (key, value) in enumerate(ROWS):
        y = TOP_PAD + i * ROW_H
        delay = 0.15 + i * 0.12
        cls = "line" if not STATIC else ""
        style = f' style="animation-delay:{delay:.2f}s"' if not STATIC else ""
        svg.append(
            f'<text class="{cls}"{style} x="{LEFT_PAD}" y="{y}" font-size="13">'
            f'<tspan fill="#39d353">{escape(key)}</tspan>'
            f'<tspan fill="#8b949e" dx="8">{escape(value)}</tspan>'
            f'</text>'
        )

    svg.append("</svg>")
    return "\n".join(svg)


def main():
    with open(OUT_PATH, "w") as f:
        f.write(render())
    print(f"Wrote {OUT_PATH} (STATIC={STATIC})")


if __name__ == "__main__":
    main()
