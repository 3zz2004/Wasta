from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from textpath import GlyphBook, Run, font  # noqa: E402

W, H = 1280, 640
SLOT = 3.2
EXAMPLES = 5
T = SLOT * EXAMPLES

AR_B = font("arabic", "700Bold")
AR_SB = font("arabic", "600SemiBold")
AR_R = font("arabic", "400Regular")
SANS_XB = font("sans", "800ExtraBold")
SANS_M = font("sans", "500Medium")
SANS_R = font("sans", "400Regular")
SANS_SB = font("sans", "600SemiBold")
MONO = font("mono", "400Regular")
MONO_M = font("mono", "500Medium")

THEMES = {
    "dark": dict(
        bg="#09090B",
        dots="#1F1F24",
        text="#F4F4F5",
        muted="#8A8A93",
        faint="#3F3F46",
        accent="#E8B04B",
        glow="#E8B04B",
        glow_op="0.10",
        card="#111114",
        border="#26262C",
        input="#A1A1AA",
        strike="#52525B",
    ),
    "light": dict(
        bg="#FAFAF9",
        dots="#E2E0DD",
        text="#0C0A09",
        muted="#6B6560",
        faint="#C9C5C0",
        accent="#B4761A",
        glow="#E8B04B",
        glow_op="0.16",
        card="#FFFFFF",
        border="#E5E2DE",
        input="#57534E",
        strike="#D6D3D1",
    ),
}


def kt(points: list[tuple[float, str]]) -> tuple[str, str]:
    """Turn (seconds, value) pairs into SMIL keyTimes/values over one loop."""
    pts = sorted(points)
    if pts[0][0] > 0:
        pts.insert(0, (0, pts[0][1]))
    if pts[-1][0] < T:
        pts.append((T, pts[-1][1]))
    return ";".join(f"{t / T:.4f}" for t, _ in pts), ";".join(v for _, v in pts)


def animate(attr: str, points: list[tuple[float, str]]) -> str:
    times, values = kt(points)
    return f'<animate attributeName="{attr}" dur="{T}s" repeatCount="indefinite" keyTimes="{times}" values="{values}"/>'


def translate(points: list[tuple[float, str]]) -> str:
    times, values = kt(points)
    return (
        f'<animateTransform attributeName="transform" type="translate" dur="{T}s" '
        f'repeatCount="indefinite" keyTimes="{times}" values="{values}"/>'
    )


def window(start: float, fade_in: float, end: float, fade_out: float = 0.3) -> list[tuple[float, str]]:
    return [(start, "0"), (start + fade_in, "1"), (end - fade_out, "1"), (end, "0")]


CX, CY, CW, CH = 704, 128, 488, 384  # card
PAD = 36
LEFT, RIGHT = CX + PAD, CX + CW - PAD


def text_line(book: GlyphBook, color: str, runs: list[Run], x: float, y: float, size: float, anchor="start") -> str:
    return f'<g fill="{color}">{book.draw_runs(runs, x, y, size, anchor)}</g>'


def examples(book: GlyphBook, th: dict) -> list[dict]:
    """Each example: function name, input line(s), output line(s)."""
    out = th["text"]
    m = th["muted"]
    return [
        dict(
            fn="parsePhone()",
            input=[(Run("٠١٠ ٠١٢٣ ٤٥٦٧", AR_R), "start")],
            output=[
                (out, [Run("+201001234567", MONO_M)], 36, "start"),
                (m, [Run("vodafone  ·  010", MONO)], 20, "start"),
            ],
        ),
        dict(
            fn="tafqeet()",
            input=[(Run("1500.25", MONO), "start")],
            output=[
                (out, [Run("ألف وخمسمائة جنيه", AR_SB)], 34, "end"),
                (out, [Run("وخمسة وعشرون قرشًا", AR_SB)], 34, "end"),
            ],
        ),
        dict(
            fn="parseNationalId()",
            input=[(Run("29905211201538", MONO), "start")],
            output=[
                (out, [Run("1999-05-21", MONO_M)], 36, "start"),
                (m, [Run("male  ·  ", MONO), Run("الدقهلية", AR_R)], 22, "start"),
            ],
        ),
        dict(
            fn="findGovernorate()",
            input=[(Run("محافظة كفرالشيخ", AR_R), "end")],
            output=[(out, [Run("Kafr El Sheikh", SANS_SB)], 38, "start"), (m, [Run("code 15", MONO)], 20, "start")],
        ),
        dict(
            fn="normalizeArabic()",
            input=[(Run("إِسْلَامٌ ومَدرسـة", AR_R), "end")],
            output=[
                (out, [Run("اسلام ومدرسه", AR_SB)], 38, "end"),
                (m, [Run("search keys, not display text", MONO)], 18, "start"),
            ],
        ),
    ]


def build(theme: str) -> str:
    th = THEMES[theme]
    book = GlyphBook(prefix=f"{theme[0]}")
    body: list[str] = []

    # Background: dot grid that fades towards the edges, and a warm glow behind the card.
    body.append(f'<rect width="{W}" height="{H}" fill="{th["bg"]}"/>')
    body.append(f'<rect width="{W}" height="{H}" fill="url(#dots)" mask="url(#fade)"/>')
    body.append(f'<ellipse cx="{CX + CW / 2}" cy="{CY + CH / 2}" rx="420" ry="300" fill="url(#glow)"/>')

    # Left column.
    x0 = 88
    body.append(text_line(book, th["accent"], [Run("واسطة", AR_B)], x0 + 4, 168, 58))
    body.append(f'<g fill="{th["text"]}">{book.draw(SANS_XB, "wasta", x0, 318, 172, -0.045)}</g>')
    caret_x = x0 + SANS_XB.width("wasta", 172, -0.045) + 10
    body.append(
        f'<rect x="{caret_x:.1f}" y="200" width="14" height="118" rx="2" fill="{th["accent"]}">'
        '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" '
        'repeatCount="indefinite"/></rect>'
    )
    body.append(text_line(book, th["text"], [Run("Every Egyptian app needs a little wasta.", SANS_M)], x0, 386, 30))
    body.append(
        text_line(
            book,
            th["muted"],
            [Run("Phones · National IDs · Tafqeet · Governorates · Arabic text", SANS_R)],
            x0,
            428,
            19,
        )
    )

    y_cmd = 512
    for i, command in enumerate(("npm i @3zz2004/wasta", "pip install wasta")):
        y = y_cmd + i * 32
        body.append(text_line(book, th["accent"], [Run("$ ", MONO)], x0, y, 21))
        body.append(text_line(book, th["text"], [Run(command, MONO)], x0 + MONO.width("$ ", 21), y, 21))
    body.append(
        text_line(book, th["muted"], [Run("JavaScript & Python · zero dependencies", SANS_R)], x0, y_cmd + 76, 17)
    )

    # Card.
    body.append(
        f'<rect x="{CX}" y="{CY}" width="{CW}" height="{CH}" rx="22" fill="{th["card"]}" stroke="{th["border"]}"'
        + (' filter="url(#shadow)"' if theme == "light" else "")
        + "/>"
    )
    body.append(text_line(book, th["muted"], [Run("INPUT", MONO_M)], LEFT, CY + 104, 13))
    body.append(text_line(book, th["muted"], [Run("OUTPUT", MONO_M)], LEFT, CY + 214, 13))
    div_y = CY + 166
    body.append(f'<line x1="{LEFT}" y1="{div_y}" x2="{RIGHT}" y2="{div_y}" stroke="{th["border"]}"/>')

    for i, ex in enumerate(examples(book, th)):
        s0, s1 = i * SLOT, (i + 1) * SLOT
        first = i == 0
        parts = []
        parts.append(text_line(book, th["accent"], [Run(ex["fn"], MONO_M)], LEFT, CY + 58, 20))
        for run, anchor in ex["input"]:
            x = RIGHT if anchor == "end" else LEFT
            parts.append(text_line(book, th["input"], [run], x, CY + 142, 26, anchor))
        # The gold line that "processes" the input.
        length = RIGHT - LEFT
        parts.append(
            f'<line x1="{LEFT}" y1="{div_y}" x2="{RIGHT}" y2="{div_y}" stroke="{th["accent"]}" stroke-width="2" '
            f'stroke-dasharray="{length}" stroke-dashoffset="{0 if first else length}">'
            + animate("stroke-dashoffset", [(s0, str(length)), (s0 + 0.45, str(length)), (s0 + 1.0, "0"), (s1, "0")])
            + "</line>"
        )
        outs = []
        y = CY + 262
        for color, runs, size, anchor in ex["output"]:
            x = RIGHT if anchor == "end" else LEFT
            outs.append(text_line(book, color, runs, x, y, size, anchor))
            y += size * 1.45
        parts.append(
            f'<g opacity="{1 if first else 0}">'
            + animate("opacity", window(s0 + 0.85, 0.3, s1, 0.3))
            + f"<g>{translate([(s0, '0 10'), (s0 + 0.85, '0 10'), (s0 + 1.2, '0 0'), (s1, '0 0')])}"
            + "".join(outs)
            + "</g></g>"
        )
        body.append(
            f'<g opacity="{1 if first else 0}">'
            + animate("opacity", window(s0, 0.3, s1, 0.3))
            + "".join(parts)
            + "</g>"
        )

    # Progress dots.
    for i in range(EXAMPLES):
        cx = LEFT + 4 + i * 30
        s0, s1 = i * SLOT, (i + 1) * SLOT
        body.append(f'<rect x="{cx - 4}" y="{CY + CH - 40}" width="8" height="8" rx="4" fill="{th["faint"]}"/>')
        body.append(
            f'<rect x="{cx - 4}" y="{CY + CH - 40}" height="8" rx="4" fill="{th["accent"]}" '
            f'width="20" opacity="{1 if i == 0 else 0}">' + animate("opacity", window(s0, 0.2, s1, 0.2)) + "</rect>"
        )
    body.append(text_line(book, th["faint"], [Run("live from the test suite", MONO)], RIGHT, CY + CH - 32, 13, "end"))

    defs = (
        f'<pattern id="dots" width="28" height="28" patternUnits="userSpaceOnUse">'
        f'<circle cx="2" cy="2" r="1.3" fill="{th["dots"]}"/></pattern>'
        f'<radialGradient id="fadeg" cx="50%" cy="45%" r="70%"><stop offset="0" stop-color="#fff"/>'
        f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
        f'<mask id="fade"><rect width="{W}" height="{H}" fill="url(#fadeg)"/></mask>'
        f'<radialGradient id="glow"><stop offset="0" stop-color="{th["glow"]}" stop-opacity="{th["glow_op"]}"/>'
        f'<stop offset="1" stop-color="{th["glow"]}" stop-opacity="0"/></radialGradient>'
        + '<filter id="shadow" x="-20%" y="-20%" width="140%" height="150%">'
        '<feDropShadow dx="0" dy="18" stdDeviation="22" flood-color="#78350f" flood-opacity="0.10"/></filter>'
        + book.svg_defs()
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="wasta: Egyptian phone numbers, national IDs, tafqeet, governorates and Arabic text, '
        f'for JavaScript and Python">'
        f"<defs>{defs}</defs>{''.join(body)}</svg>\n"
    )


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        (out / f"banner-{theme}.svg").write_text(build(theme), encoding="utf-8")
