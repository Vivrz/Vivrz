"""
render_heatmap_svg.py
Reads data/contributions.json and draws the 53-week x 7-day contribution
calendar as an animated SVG (boxes reveal diagonally, then freeze).
"""

import json
import os
from datetime import datetime, timedelta

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "contrib-heatmap.svg")

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL = 11
GAP = 3
LEFT_PAD = 30
TOP_PAD = 20
MONTH_LABEL_H = 16


def load_data():
    with open(DATA_PATH) as f:
        return json.load(f)


def build_weeks(days):
    by_date = {d["date"]: d for d in days}
    if not days:
        return []
    first = datetime.strptime(days[0]["date"], "%Y-%m-%d").date()
    last = datetime.strptime(days[-1]["date"], "%Y-%m-%d").date()
    start = first - timedelta(days=(first.weekday() + 1) % 7)

    weeks = []
    cursor = start
    week = []
    while cursor <= last:
        week.append(by_date.get(cursor.isoformat()))
        if len(week) == 7:
            weeks.append(week)
            week = []
        cursor += timedelta(days=1)
    if week:
        while len(week) < 7:
            week.append(None)
        weeks.append(week)
    return weeks


def month_labels(weeks):
    labels = {}
    seen_month = None
    for i, week in enumerate(weeks):
        first_real = next((d for d in week if d), None)
        if not first_real:
            continue
        dt = datetime.strptime(first_real["date"], "%Y-%m-%d")
        if dt.month != seen_month:
            labels[i] = dt.strftime("%b")
            seen_month = dt.month
    return labels


def render(data):
    days = data["days"]
    stats = data["stats"]
    weeks = build_weeks(days)
    best_date = stats["best_day"]["date"] if stats.get("best_day") else None

    n_weeks = len(weeks)
    width = LEFT_PAD + n_weeks * (CELL + GAP) + 160
    height = TOP_PAD + MONTH_LABEL_H + 7 * (CELL + GAP) + 50

    svg = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" font-family="Consolas, Menlo, monospace">']
    svg.append(
        "<style>.cbox{opacity:0;transform:translateY(-6px);"
        "animation:reveal .35s ease-out forwards;}"
        "@keyframes reveal{to{opacity:1;transform:translateY(0);}}"
        "text{fill:#8b949e;}</style>"
    )
    svg.append(f'<rect width="{width}" height="{height}" fill="none"/>')

    for wi, label in month_labels(weeks).items():
        x = LEFT_PAD + wi * (CELL + GAP)
        svg.append(f'<text x="{x}" y="{TOP_PAD}" font-size="10">{label}</text>')

    for row, label in {1: "Mon", 3: "Wed", 5: "Fri"}.items():
        y = TOP_PAD + MONTH_LABEL_H + row * (CELL + GAP) + CELL - 2
        svg.append(f'<text x="0" y="{y}" font-size="9">{label}</text>')

    for wi, week in enumerate(weeks):
        for di, day in enumerate(week):
            if day is None:
                continue
            x = LEFT_PAD + wi * (CELL + GAP)
            y = TOP_PAD + MONTH_LABEL_H + di * (CELL + GAP)
            level = day.get("level", 0)
            color = PALETTE[min(level, 4)]
            if best_date and day["date"] == best_date and day["count"] > 0:
                color = PALETTE[5]
            delay = (wi + di) * 0.006
            svg.append(
                f'<rect class="cbox" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="2" ry="2" fill="{color}" style="animation-delay:{delay:.3f}s">'
                f'<title>{day["count"]} contributions on {day["date"]}</title></rect>'
            )

    legend_y = TOP_PAD + MONTH_LABEL_H + 7 * (CELL + GAP) + 18
    svg.append(f'<text x="{LEFT_PAD}" y="{legend_y}" font-size="10">Less</text>')
    lx = LEFT_PAD + 32
    for c in PALETTE[:5]:
        svg.append(f'<rect x="{lx}" y="{legend_y - 9}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>')
        lx += CELL + GAP
    svg.append(f'<text x="{lx + 4}" y="{legend_y}" font-size="10">More</text>')

    footer = (
        f'{stats["total"]:,} contributions in the last year &#183; '
        f'current streak {stats["current_streak"]}d &#183; '
        f'longest streak {stats["longest_streak"]}d'
    )
    svg.append(f'<text x="{LEFT_PAD}" y="{legend_y + 20}" font-size="11" fill="#c9d1d9">{footer}</text>')
    svg.append("</svg>")
    return "\n".join(svg)


def main():
    data = load_data()
    svg = render(data)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()