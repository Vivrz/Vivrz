"""
fetch_contributions.py
Pulls your public GitHub contribution calendar (no token needed) and
writes data/contributions.json with per-day data + derived stats.
"""

import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

CONTRIB_URL = "https://github.com/users/{username}/contributions"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def resolve_username(argv):
    if len(argv) > 1 and argv[1].strip():
        return argv[1].strip()
    env = os.environ.get("GITHUB_USERNAME", "").strip()
    if env:
        return env
    raise SystemExit("Usage: python scripts/fetch_contributions.py <username>")


def fetch_days(username):
    url = CONTRIB_URL.format(username=username)
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    cells = soup.select("td.ContributionCalendar-day") or soup.select("[data-date]")
    if not cells:
        raise RuntimeError("Could not find contribution cells -- GitHub markup may have changed.")

    days = []
    for cell in cells:
        d = cell.get("data-date")
        if not d:
            continue
        level = int(cell.get("data-level", 0))
        label = cell.get("aria-label") or ""
        if not label and cell.get("id"):
            tt = soup.find("tool-tip", attrs={"for": cell.get("id")})
            if tt:
                label = tt.get_text(" ", strip=True)
        m = re.search(r"([\d,]+)\s+contribution", label)
        count = int(m.group(1).replace(",", "")) if m else 0
        days.append({"date": d, "count": count, "level": level})

    days.sort(key=lambda x: x["date"])
    return days


def compute_stats(days):
    total = sum(d["count"] for d in days)
    longest = running = current = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0
    for d in reversed(days):
        if d["count"] > 0:
            current += 1
        else:
            break
    best_day = max(days, key=lambda x: x["count"], default=None)
    monthly = defaultdict(int)
    for d in days:
        monthly[d["date"][:7]] += d["count"]
    return {
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best_day,
        "monthly_totals": dict(sorted(monthly.items())),
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def main():
    username = resolve_username(sys.argv)
    days = fetch_days(username)
    stats = compute_stats(days)
    payload = {"username": username, "days": days, "stats": stats}
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote {len(days)} days for {username} -> {OUT_PATH}")
    print(f"Total: {stats['total']}  Current streak: {stats['current_streak']}  Longest streak: {stats['longest_streak']}")


if __name__ == "__main__":
    main()
