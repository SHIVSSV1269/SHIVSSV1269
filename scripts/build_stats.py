#!/usr/bin/env python3
"""Generate assets/stats.svg from the GitHub GraphQL API.

Self-hosted replacement for github-readme-stats / streak-stats, which are
third-party services that go down (503) and take the profile down with them.
Standard library only. Run locally with GH_TOKEN=$(gh auth token), or let
.github/workflows/update-stats.yml run it on a schedule.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USER = os.environ.get("STATS_USER", "SHIVSSV1269")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
OUT = Path(__file__).resolve().parent.parent / "assets" / "stats.svg"

INK, GOLD, GOLD_HI, JADE, IVORY, SLATE, TRACK = (
    "#0c1117", "#e3b873", "#f6e3b4", "#63d2a5", "#eae3d4", "#6f8697", "#1b2530",
)

# Colours for the language ring. Deliberately inside our palette rather than
# GitHub's language colours, so the card stays one piece of art.
RING = ["#e3b873", "#63d2a5", "#c98f42", "#9ec7b6", "#a8271c", "#4d6a80"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    name
    followers { totalCount }
    following { totalCount }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalRepositoriesWithContributedCommits
      contributionCalendar { totalContributions }
    }
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC,
                 orderBy: {field: STARGAZERS, direction: DESC}) {
      totalCount
      nodes {
        stargazerCount
        forkCount
        isFork
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}
"""


def graphql(query, variables):
    if not TOKEN:
        sys.exit("no token: set GH_TOKEN (locally: GH_TOKEN=$(gh auth token))")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={
            "Authorization": f"bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": f"{USER}-profile-stats",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.load(resp)
    except urllib.error.HTTPError as exc:
        sys.exit(f"github api {exc.code}: {exc.read().decode()[:400]}")
    if "errors" in payload:
        sys.exit(f"graphql errors: {payload['errors']}")
    return payload["data"]


def collect():
    user = graphql(QUERY, {"login": USER})["user"]
    contrib = user["contributionsCollection"]
    repos = user["repositories"]["nodes"]

    stars = sum(r["stargazerCount"] for r in repos)
    forks = sum(r["forkCount"] for r in repos)

    sizes = {}
    for repo in repos:
        if repo["isFork"]:
            continue
        for edge in repo["languages"]["edges"]:
            sizes[edge["node"]["name"]] = sizes.get(edge["node"]["name"], 0) + edge["size"]
    total_bytes = sum(sizes.values()) or 1
    langs = sorted(sizes.items(), key=lambda kv: -kv[1])[:5]
    top = [(name, size / total_bytes) for name, size in langs]
    shown = sum(share for _, share in top)
    if shown < 0.999:
        top.append(("Other", 1 - shown))

    return {
        "name": user["name"] or USER,
        "commits": contrib["totalCommitContributions"],
        "prs": contrib["totalPullRequestContributions"],
        "issues": contrib["totalIssueContributions"],
        "contributions": contrib["contributionCalendar"]["totalContributions"],
        "touched": contrib["totalRepositoriesWithContributedCommits"],
        "repos": user["repositories"]["totalCount"],
        "stars": stars,
        "forks": forks,
        "followers": user["followers"]["totalCount"],
        "languages": top,
    }


def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def render(d):
    """Left column: counters that slide in. Right: an animated language ring."""
    tiles = [
        ("commits this year", d["commits"]),
        ("total contributions", d["contributions"]),
        ("stars earned", d["stars"]),
        ("public repositories", d["repos"]),
        ("pull requests opened", d["prs"]),
        ("followers", d["followers"]),
    ]

    rows = []
    for i, (label, value) in enumerate(tiles):
        x = 44 + (i % 2) * 210
        y = 116 + (i // 2) * 76
        delay = 0.25 + i * 0.11
        rows.append(f'''
  <g class="tile" style="animation-delay:{delay:.2f}s">
    <text class="num" x="{x}" y="{y}">{value:,}</text>
    <text class="lbl" x="{x}" y="{y + 20}">{esc(label)}</text>
    <path d="M{x} {y + 30} H{x + 150}" stroke="{GOLD}" stroke-opacity=".14"/>
  </g>''')

    # Language ring: one arc per language, drawn on with stroke-dashoffset.
    cx, cy, r = 700, 214, 92
    circumference = 2 * 3.141592653589793 * r
    arcs, legend = [], []
    offset = 0.0
    for i, (name, share) in enumerate(d["languages"]):
        colour = RING[i % len(RING)]
        length = share * circumference
        gap = circumference - length
        arcs.append(f'''
    <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{colour}" stroke-width="17"
            stroke-dasharray="{length:.2f} {gap:.2f}" stroke-dashoffset="{-offset:.2f}"
            stroke-linecap="butt" opacity=".92" transform="rotate(-90 {cx} {cy})">
      <animate attributeName="stroke-dasharray" from="0 {circumference:.2f}"
               to="{length:.2f} {gap:.2f}" dur="1.1s" begin="{0.3 + i * 0.16:.2f}s"
               fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>
    </circle>''')
        ly = 132 + i * 26
        legend.append(f'''
    <g class="tile" style="animation-delay:{0.5 + i * 0.16:.2f}s">
      <rect x="472" y="{ly - 9}" width="10" height="10" rx="2" fill="{colour}"/>
      <text class="leg" x="492" y="{ly}">{esc(name)}</text>
      <text class="legpct" x="592" y="{ly}">{share * 100:.1f}%</text>
    </g>''')
        offset += length

    stamp = datetime.now(timezone.utc).strftime("%d %b %Y").upper()

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 430" width="860" height="430" role="img" aria-label="GitHub statistics for {esc(USER)}">
<defs>
  <linearGradient id="sbg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{INK}"/><stop offset="100%" stop-color="#10161e"/>
  </linearGradient>
  <linearGradient id="gold" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{GOLD}"/><stop offset="100%" stop-color="{GOLD_HI}"/>
  </linearGradient>
  <filter id="sglow" x="-60%" y="-60%" width="220%" height="220%">
    <feGaussianBlur stdDeviation="2.6" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>
<style><![CDATA[
  .m  {{ font-family:"Georgia","Iowan Old Style","Times New Roman",serif; }}
  .mo {{ font-family:"JetBrains Mono","SF Mono","Consolas",monospace; }}
  .num {{ font-family:"Georgia",serif; font-size:30px; fill:url(#gold); }}
  .lbl {{ font-family:"Georgia",serif; font-size:12px; fill:{SLATE}; letter-spacing:1.4px; }}
  .leg {{ font-family:"Georgia",serif; font-size:13px; fill:{IVORY}; }}
  .legpct {{ font-family:"JetBrains Mono","Consolas",monospace; font-size:12px; fill:{SLATE}; text-anchor:end; }}
  @keyframes slide {{ from {{ opacity:0; transform: translateY(10px); }} to {{ opacity:1; transform: none; }} }}
  @keyframes spin  {{ to {{ transform: rotate(360deg); }} }}
  @keyframes pulse {{ 0%,100% {{ opacity:.30; }} 50% {{ opacity:.75; }} }}
  .tile {{ opacity:0; animation: slide .7s ease-out forwards; }}
  .yy   {{ animation: spin 24s linear infinite; transform-origin: {cx}px {cy}px; }}
  .halo {{ animation: pulse 5s ease-in-out infinite; }}
  @media (prefers-reduced-motion: reduce) {{
    .tile {{ opacity:1; animation:none; }} .yy,.halo {{ animation:none; }}
  }}
]]></style>

<rect width="860" height="430" rx="14" fill="url(#sbg)" stroke="{GOLD}" stroke-opacity=".22"/>

<text class="m" x="36" y="50" font-size="22" fill="{GOLD}" letter-spacing="5">THE RECORD</text>
<text class="mo" x="824" y="49" font-size="11" fill="#4f6376" text-anchor="end">SELF-HOSTED &#183; {stamp}</text>
<path d="M36 64 H824" stroke="{GOLD}" stroke-opacity=".18"/>
{''.join(rows)}

<!-- language ring -->
<circle class="halo" cx="{cx}" cy="{cy}" r="{r + 22}" fill="none" stroke="{GOLD}" stroke-width=".7" opacity=".3"/>
<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{TRACK}" stroke-width="17"/>
<g filter="url(#sglow)">{''.join(arcs)}</g>
<g class="yy">
  <g transform="translate({cx},{cy}) scale(0.33)">
    <circle r="100" fill="{IVORY}"/>
    <path d="M 0,-100 A 100,100 0 0,1 0,100 A 50,50 0 0,1 0,0 A 50,50 0 0,0 0,-100 Z" fill="#10151c"/>
    <circle cx="0" cy="-50" r="16" fill="#10151c"/>
    <circle cx="0" cy="50"  r="16" fill="{IVORY}"/>
    <circle r="100" fill="none" stroke="{GOLD}" stroke-width="4" opacity=".9"/>
  </g>
</g>
<text class="m" x="472" y="100" font-size="12" fill="{SLATE}" letter-spacing="3">ELEMENTS WIELDED</text>
{''.join(legend)}

<text class="m" x="36" y="404" font-size="12" fill="#4f6376">measured, not boasted &#183; regenerated daily by a workflow in this repo</text>
</svg>
'''


def main():
    data = collect()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(data), encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"  commits={data['commits']} contributions={data['contributions']} "
          f"stars={data['stars']} repos={data['repos']} followers={data['followers']}")
    print(f"  languages={[(n, f'{s:.1%}') for n, s in data['languages']]}")


if __name__ == "__main__":
    main()
