"""Generate clean, brand-consistent SVG product illustrations (trademark-safe).

Writes 400x400 SVGs into app/seed/images/. Each is a soft light tile with a
line+fill illustration of the part in the brand-blue palette. Run:  python -m app.seed.gen_images
"""

from __future__ import annotations

import math
from pathlib import Path

IMAGES_DIR = Path(__file__).resolve().parent / "images"

ST = "#153259"  # stroke — TRUCK CENTER navy
F1 = "#e6ebf3"  # light fill
F2 = "#b7c4d9"  # mid fill
AC = "#e5182e"  # accent — TRUCK CENTER red
WH = "#ffffff"


def frame(inner: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" width="400" height="400">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f4f7fb"/><stop offset="1" stop-color="#e4ebf4"/>
    </linearGradient>
    <radialGradient id="sh" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#153259" stop-opacity="0.16"/>
      <stop offset="1" stop-color="#153259" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <!-- Light tile is intentional: these stand in for product photos, which read as
       light images in both themes (same as any photo-based catalog). -->
  <rect width="400" height="400" fill="url(#bg)"/>
  <ellipse cx="200" cy="322" rx="118" ry="24" fill="url(#sh)"/>
  <g fill="none" stroke="{ST}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round">
    {inner}
  </g>
</svg>
"""


def _ring(cx, cy, r, n, rr, fill):
    out = []
    for i in range(n):
        a = (i / n) * 2 * math.pi - math.pi / 2
        out.append(
            f'<circle cx="{cx + r * math.cos(a):.1f}" cy="{cy + r * math.sin(a):.1f}" r="{rr}" fill="{fill}" stroke="{ST}" stroke-width="4"/>'
        )
    return "".join(out)


def oil_filter(cap=F2):
    return f"""
    <rect x="150" y="82" width="100" height="30" rx="9" fill="{cap}"/>
    <rect x="140" y="106" width="120" height="212" rx="22" fill="{F1}"/>
    <path d="M162 150h76M162 184h76M162 218h76M162 252h76" stroke="{F2}" stroke-width="7"/>
    <rect x="140" y="106" width="120" height="212" rx="22"/>
    <ellipse cx="200" cy="106" rx="60" ry="14" fill="{WH}"/>
    """


def fuel_filter():
    return f"""
    <rect x="108" y="150" width="184" height="100" rx="50" fill="{F1}"/>
    <path d="M170 150v100M212 150v100" stroke="{F2}" stroke-width="6"/>
    <rect x="108" y="150" width="184" height="100" rx="50"/>
    <rect x="78" y="184" width="34" height="32" rx="8" fill="{F2}"/>
    <rect x="288" y="184" width="34" height="32" rx="8" fill="{F2}"/>
    """


def brake_pads():
    return f"""
    <rect x="118" y="118" width="164" height="58" rx="14" fill="{F2}"/>
    <rect x="118" y="176" width="164" height="26" rx="8" fill="{AC}" stroke="none"/>
    <rect x="118" y="118" width="164" height="84" rx="14"/>
    <rect x="132" y="238" width="136" height="52" rx="12" fill="{F1}"/>
    <circle cx="150" cy="147" r="7" fill="{ST}" stroke="none"/>
    <circle cx="250" cy="147" r="7" fill="{ST}" stroke="none"/>
    """


def brake_disc():
    holes = _ring(200, 200, 34, 5, 6, WH)
    ticks = "".join(
        f'<line x1="{200 + 74 * math.cos(i / 24 * 2 * math.pi):.1f}" y1="{200 + 74 * math.sin(i / 24 * 2 * math.pi):.1f}" x2="{200 + 102 * math.cos(i / 24 * 2 * math.pi):.1f}" y2="{200 + 102 * math.sin(i / 24 * 2 * math.pi):.1f}" stroke="{F2}" stroke-width="4"/>'
        for i in range(24)
    )
    return f"""
    <circle cx="200" cy="200" r="112" fill="{F1}"/>
    {ticks}
    <circle cx="200" cy="200" r="112"/>
    <circle cx="200" cy="200" r="72" fill="{F2}"/>
    <circle cx="200" cy="200" r="40" fill="{WH}"/>
    {holes}
    <circle cx="200" cy="200" r="11" fill="{AC}" stroke="none"/>
    """


def gasket():
    big = "".join(f'<circle cx="200" cy="{125 + i * 62}" r="26" fill="{WH}"/>' for i in range(3))
    bolts = "".join(
        f'<circle cx="{x}" cy="{y}" r="6" fill="{F2}"/>'
        for x in (140, 260)
        for y in (110, 172, 234, 296)
    )
    return f"""
    <rect x="120" y="86" width="160" height="228" rx="22" fill="{F1}"/>
    {big}{bolts}
    <rect x="120" y="86" width="160" height="228" rx="22"/>
    """


def air_spring():
    bellows = "".join(
        f'<ellipse cx="200" cy="{150 + i * 44}" rx="{74 - (i % 2) * 10}" ry="26" fill="{F1}"/>'
        for i in range(3)
    )
    return f"""
    <rect x="150" y="92" width="100" height="26" rx="8" fill="{F2}"/>
    {bellows}
    <ellipse cx="200" cy="150" rx="74" ry="26"/>
    <ellipse cx="200" cy="194" rx="64" ry="26"/>
    <ellipse cx="200" cy="238" rx="74" ry="26"/>
    <rect x="160" y="286" width="80" height="30" rx="8" fill="{F2}"/>
    """


def shock():
    return f"""
    <circle cx="200" cy="86" r="24" fill="{F1}"/><circle cx="200" cy="86" r="9" fill="{WH}"/>
    <rect x="192" y="104" width="16" height="70" rx="6" fill="{F2}"/>
    <rect x="168" y="168" width="64" height="128" rx="18" fill="{F1}"/>
    <path d="M176 196h48M176 224h48M176 252h48" stroke="{F2}" stroke-width="6"/>
    <rect x="168" y="168" width="64" height="128" rx="18"/>
    <circle cx="200" cy="314" r="20" fill="{F1}"/><circle cx="200" cy="314" r="8" fill="{WH}"/>
    """


def starter():
    return f"""
    <rect x="120" y="150" width="150" height="110" rx="40" fill="{F1}"/>
    <path d="M150 150v110M180 150v110M210 150v110M240 150v110" stroke="{F2}" stroke-width="5"/>
    <rect x="120" y="150" width="150" height="110" rx="40"/>
    <rect x="150" y="110" width="90" height="42" rx="16" fill="{F2}"/>
    <circle cx="292" cy="205" r="34" fill="{F2}"/>
    <circle cx="292" cy="205" r="12" fill="{WH}"/>
    <circle cx="292" cy="205" r="34"/>
    """


def oil_canister():
    return f"""
    <rect x="176" y="86" width="34" height="24" rx="4" fill="{F2}"/>
    <path d="M150 150c0-14 10-24 24-24h38c14 0 24 10 24 24v140c0 14-10 24-24 24h-38c-14 0-24-10-24-24z" fill="{F1}"/>
    <rect x="163" y="180" width="74" height="70" rx="8" fill="{WH}"/>
    <path d="M175 200h50M175 218h50M175 236h34" stroke="{F2}" stroke-width="6"/>
    <path d="M150 150c0-14 10-24 24-24h38c14 0 24 10 24 24v140c0 14-10 24-24 24h-38c-14 0-24-10-24-24z"/>
    """


def belt():
    return (
        f"""
    <path d="M150 120h100a56 56 0 0 1 0 112H150a56 56 0 0 1 0-112z" fill="{F1}"/>
    <path d="M150 150h100a26 26 0 0 1 0 52H150a26 26 0 0 1 0-52z" fill="{WH}"/>
    <path d="M150 120h100a56 56 0 0 1 0 112H150a56 56 0 0 1 0-112z"/>
    <path d="M150 150h100a26 26 0 0 1 0 52H150a26 26 0 0 1 0-52z"/>
    <g stroke="{F2}" stroke-width="4">
    """
        + "".join(f'<line x1="{x}" y1="124" x2="{x}" y2="140" />' for x in range(160, 250, 12))
        + "</g>"
    )


def bearing():
    balls = _ring(200, 200, 86, 10, 13, F2)
    return f"""
    <circle cx="200" cy="200" r="112" fill="{F1}"/>
    <circle cx="200" cy="200" r="112"/>
    <circle cx="200" cy="200" r="98" fill="{WH}"/>
    {balls}
    <circle cx="200" cy="200" r="60" fill="{F1}"/>
    <circle cx="200" cy="200" r="60"/>
    <circle cx="200" cy="200" r="46" fill="{WH}"/>
    """


PARTS = {
    "oil-filter": oil_filter(),
    "oil-filter-b": oil_filter(cap=F1),
    "fuel-filter": fuel_filter(),
    "brake-pads": brake_pads(),
    "brake-disc": brake_disc(),
    "gasket": gasket(),
    "air-spring": air_spring(),
    "shock": shock(),
    "starter": starter(),
    "oil-canister": oil_canister(),
    "belt": belt(),
    "bearing": bearing(),
}


def main() -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    for name, art in PARTS.items():
        (IMAGES_DIR / f"{name}.svg").write_text(frame(art), encoding="utf-8")
    print(f"Wrote {len(PARTS)} SVGs to {IMAGES_DIR}")


if __name__ == "__main__":
    main()
