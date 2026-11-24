"""Text to SVG paths, with proper Arabic shaping via HarfBuzz.

GitHub renders README SVGs as images in a sandbox, so web fonts never load.
Converting text to outlines is the only way the Arabic shows up correctly
for everyone.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONTS = Path(__file__).parent / "fonts"
ARABIC_LETTER = re.compile("[\u0621-\u064a\u066e-\u06d3\ufb50-\ufdff\ufe70-\ufefc]")


class Font:
    def __init__(self, path: str | Path) -> None:
        data = Path(path).read_bytes()
        self.hb_font = hb.Font(hb.Face(data))
        self.tt = TTFont(path)
        self.glyphs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        self.upem = self.tt["head"].unitsPerEm

    def shape(self, text: str, rtl: bool | None = None):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        if rtl is None:
            rtl = bool(ARABIC_LETTER.search(text))
        buf.direction = "rtl" if rtl else "ltr"
        hb.shape(self.hb_font, buf, {"kern": True, "liga": True})
        return list(zip(buf.glyph_infos, buf.glyph_positions, strict=True))

    def width(self, text: str, size: float, tracking: float = 0) -> float:
        shaped = self.shape(text)
        return sum(p.x_advance for _, p in shaped) * size / self.upem + tracking * size * len(shaped)


@dataclass
class Run:
    text: str
    font: Font


def runs_width(runs: list[Run], size: float) -> float:
    return sum(r.font.width(r.text, size) for r in runs)


def font(family: str, weight: str) -> Font:
    folder = {
        "arabic": "ibm-plex-sans-arabic",
        "mono": "jetbrains-mono",
        "sans": "inter-tight",
    }[family]
    stem = {
        "arabic": "IBMPlexSansArabic",
        "mono": "JetBrainsMono",
        "sans": "InterTight",
    }[family]
    return Font(FONTS / folder / weight / f"{stem}_{weight}.ttf")


class GlyphBook:
    """Collects each glyph outline once in <defs> and places it with <use>,
    which keeps text-heavy SVGs small."""

    def __init__(self, prefix: str = "g") -> None:
        self.prefix = prefix
        self.defs: dict[tuple[int, str], str] = {}

    def _ref(self, f: Font, name: str) -> str | None:
        key = (id(f), name)
        if key not in self.defs:
            pen = SVGPathPen(f.glyphs, ntos=lambda v: f"{round(v):g}")
            f.glyphs[name].draw(TransformPen(pen, (1, 0, 0, -1, 0, 0)))
            d = pen.getCommands()
            self.defs[key] = f'<path id="{self.prefix}{len(self.defs)}" d="{d}"/>' if d else ""
        el = self.defs[key]
        return el.split('"')[1] if el else None

    def draw(self, f: Font, text: str, x: float, y: float, size: float, tracking: float = 0) -> str:
        scale = size / f.upem
        out, cursor = [], 0.0
        for info, pos in f.shape(text):
            ref = self._ref(f, f.order[info.codepoint])
            if ref:
                gx = x + (cursor + pos.x_offset) * scale
                gy = y - pos.y_offset * scale
                out.append(f'<use href="#{ref}" transform="translate({gx:.1f} {gy:.1f}) scale({scale:.5f})"/>')
            cursor += pos.x_advance + tracking * f.upem
        return "".join(out)

    def draw_runs(self, runs: list[Run], x: float, y: float, size: float, anchor: str = "start") -> str:
        total = runs_width(runs, size)
        if anchor == "middle":
            x -= total / 2
        elif anchor == "end":
            x -= total
        out = []
        for r in runs:
            out.append(self.draw(r.font, r.text, x, y, size))
            x += r.font.width(r.text, size)
        return "".join(out)

    def svg_defs(self) -> str:
        return "".join(v for v in self.defs.values() if v)
