from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from textpath import GlyphBook, font  # noqa: E402

MONO = font("mono", "400Regular")
MONO_M = font("mono", "500Medium")
AR = font("arabic", "400Regular")

W = 960
SIZE = 17
AR_SIZE = 18.5
LINE = 29
TOP = 84
LEFT = 28
CHAR = MONO.width("x", SIZE)

C = dict(
    bg="#0D0D10",
    bar="#151519",
    border="#26262C",
    text="#E4E4E7",
    dim="#6B6B74",
    prompt="#E8B04B",
    string="#A7D7A0",
    fn="#8CC5FF",
    num="#F0A868",
    err="#F87171",
    tab_on="#26262C",
    tab_text="#E4E4E7",
)

# A line is a list of (text, color). Arabic inside a segment is shaped with an Arabic font.
JS = [
    (
        "in",
        [
            ("> ", "prompt"),
            ("const ", "dim"),
            ("w", "text"),
            (" = ", "dim"),
            ("require", "fn"),
            ("(", "dim"),
            ('"@3zz2004/wasta"', "string"),
            (")", "dim"),
        ],
    ),
    ("out", [("undefined", "dim")]),
    ("in", [("> ", "prompt"), ("w.", "text"), ("tafqeet", "fn"), ("(", "dim"), ("1500.25", "num"), (")", "dim")]),
    ("out", [("'فقط ألف وخمسمائة جنيه وخمسة وعشرون قرشًا لا غير'", "string")]),
    (
        "in",
        [
            ("> ", "prompt"),
            ("w.", "text"),
            ("parsePhone", "fn"),
            ("(", "dim"),
            ('"٠١٠ ٠١٢٣ ٤٥٦٧"', "string"),
            (").value.e164", "text"),
        ],
    ),
    ("out", [("'+201001234567'", "string")]),
    (
        "in",
        [
            ("> ", "prompt"),
            ("w.", "text"),
            ("parseNationalId", "fn"),
            ("(", "dim"),
            ('"29905211201538"', "string"),
            (").value.birthDate", "text"),
        ],
    ),
    ("out", [("'1999-05-21'", "string")]),
    (
        "in",
        [
            ("> ", "prompt"),
            ("w.", "text"),
            ("findGovernorate", "fn"),
            ("(", "dim"),
            ('"محافظة كفرالشيخ"', "string"),
            (").nameEn", "text"),
        ],
    ),
    ("out", [("'Kafr El Sheikh'", "string")]),
]

PY = [
    (
        "in",
        [
            (">>> ", "prompt"),
            ("from ", "dim"),
            ("wasta ", "text"),
            ("import ", "dim"),
            ("tafqeet, parse_national_id, parse_phone", "text"),
        ],
    ),
    ("in", [(">>> ", "prompt"), ("tafqeet", "fn"), ("(", "dim"), ("2000", "num"), (")", "dim")]),
    ("out", [("'فقط ألفا جنيه لا غير'", "string")]),
    ("in", [(">>> ", "prompt"), ("tafqeet", "fn"), ("(", "dim"), ('"11500"', "string"), (")", "dim")]),
    ("out", [("'فقط أحد عشر ألفًا وخمسمائة جنيه لا غير'", "string")]),
    (
        "in",
        [
            (">>> ", "prompt"),
            ("parse_national_id", "fn"),
            ("(", "dim"),
            ('"29905211201538"', "string"),
            (").governorate.name_ar", "text"),
        ],
    ),
    ("out", [("'الدقهلية'", "string")]),
    ("in", [(">>> ", "prompt"), ("parse_phone", "fn"), ("(", "dim"), ('"0223456789"', "string"), (")", "dim")]),
    ("out", [("Traceback (most recent call last):", "dim")]),
    ("out", [("  ...", "dim")]),
    ("out", [("wasta.InvalidPhoneError", "err"), (": Not a mobile number: '0223456789'", "text")]),
]

H = TOP + max(len(JS), len(PY)) * LINE + 34

ARABIC_CHUNK = re.compile(r"([\u0600-\u06ff][\u0600-\u06ff\s]*[\u0600-\u06ff]|[\u0600-\u06ff])")


def runs_of(text: str) -> list[tuple[str, bool]]:
    return [(p, bool(ARABIC_CHUNK.fullmatch(p))) for p in ARABIC_CHUNK.split(text) if p]


def measure(seg: str, arabic: bool) -> float:
    return AR.width(seg, AR_SIZE) if arabic else MONO.width(seg, SIZE)


def draw_line(book: GlyphBook, segments, y: float) -> tuple[str, list[float]]:
    """Returns the SVG and the x position after each typed 'keystroke'."""
    out, stops, x = [], [], LEFT
    for text, color in segments:
        parts = []
        for piece, arabic in runs_of(text):
            f, size = (AR, AR_SIZE) if arabic else (MONO, SIZE)
            parts.append(book.draw(f, piece, x, y, size))
            if arabic:
                width = measure(piece, True)
                steps = max(1, len(piece.replace(" ", "")))
                stops += [x + width * (k + 1) / steps for k in range(steps)]
                x += width
            else:
                for _ in piece:
                    x += CHAR
                    stops.append(x)
        out.append(f'<g fill="{C[color]}">{"".join(parts)}</g>')
    return "".join(out), stops


def kt(points, total):
    pts = sorted(points)
    if pts[0][0] > 0:
        pts.insert(0, (0, pts[0][1]))
    if pts[-1][0] < total:
        pts.append((total, pts[-1][1]))
    return ";".join(f"{t / total:.5f}" for t, _ in pts), ";".join(str(v) for _, v in pts)


def anim(attr, points, total, discrete=False):
    times, values = kt(points, total)
    mode = ' calcMode="discrete"' if discrete else ""
    return (
        f'<animate attributeName="{attr}" dur="{total:.2f}s" repeatCount="indefinite"{mode} '
        f'keyTimes="{times}" values="{values}"/>'
    )


def build() -> str:
    book = GlyphBook("t")
    TYPE, AFTER_TYPE, AFTER_OUT, HOLD = 0.032, 0.28, 0.75, 2.6

    # Plan the timeline first so every animation can share one loop length.
    t = 0.7
    sessions = []
    for name, lines in (("node", JS), ("python", PY)):
        start = t
        rows = []
        for i, (kind, segs) in enumerate(lines):
            y = TOP + i * LINE
            svg, stops = draw_line(book, segs, y)
            if kind == "in":
                prompt_len = len(segs[0][0])
                typed = stops[prompt_len - 1 :]
                t0 = t + 0.15
                times = [t0 + k * TYPE for k in range(len(typed))]
                rows.append(
                    dict(kind="in", svg=svg, y=y, start=t, stops=typed, times=times, x0=LEFT + CHAR * prompt_len)
                )
                t = times[-1] + AFTER_TYPE
            else:
                rows.append(dict(kind="out", svg=svg, y=y, start=t))
                nxt = lines[i + 1][0] if i + 1 < len(lines) else None
                t += AFTER_OUT if nxt == "in" else 0.06
        end = t + HOLD
        sessions.append(dict(name=name, rows=rows, start=start, end=end))
        t = end + 0.45
    total = t + 0.1

    body = []
    body.append(
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="{C["bg"]}" stroke="{C["border"]}"/>'
    )
    body.append(
        f'<path d="M14.5 0.5H{W - 14.5}A14 14 0 0 1 {W - 0.5} 14.5V44.5H0.5V14.5A14 14 0 0 1 14.5 0.5Z" '
        f'fill="{C["bar"]}" stroke="{C["border"]}"/>'
    )
    for i, color in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        body.append(f'<circle cx="{24 + i * 20}" cy="22.5" r="6" fill="{color}"/>')

    tab_x = 100
    for s in sessions:
        label = s["name"]
        w = MONO.width(label, 14) + 28
        on = [(s["start"] - 0.3, 1), (s["end"], 1), (s["end"] + 0.3, 0)]
        off_first = 1 if s is sessions[0] else 0
        body.append(
            f'<rect x="{tab_x}" y="11" width="{w:.1f}" height="23" rx="6" fill="{C["tab_on"]}" opacity="{off_first}">'
            + anim("opacity", [(0, 0), (s["start"] - 0.3, 0)] + on, total)
            + "</rect>"
        )
        body.append(
            f'<g fill="{C["tab_text"]}" opacity="0.55">'
            + anim(
                "opacity",
                [(0, 0.55), (s["start"] - 0.3, 0.55), (s["start"], 1), (s["end"], 1), (s["end"] + 0.3, 0.55)],
                total,
            )
            + book.draw(MONO, label, tab_x + 14, 27.5, 14)
            + "</g>"
        )
        tab_x += w + 8

    cursor_h = 20
    for s in sessions:
        for r in s["rows"]:
            vis = [(0, 0), (r["start"], 0), (r["start"] + 0.01, 1), (s["end"], 1), (s["end"] + 0.35, 0)]
            if r["kind"] == "out":
                body.append(f'<g opacity="0">{anim("opacity", vis, total)}{r["svg"]}</g>')
                continue
            clip_id = f"c{len(body)}"
            widths = [(0, r["x0"] - LEFT), (r["start"], r["x0"] - LEFT)]
            widths += [(tm, round(x - LEFT + 1, 1)) for tm, x in zip(r["times"], r["stops"], strict=True)]
            body.append(
                f'<clipPath id="{clip_id}"><rect x="{LEFT}" y="{r["y"] - 22}" height="32" width="0">'
                + anim("width", widths, total, discrete=True)
                + "</rect></clipPath>"
            )
            body.append(f'<g opacity="0" clip-path="url(#{clip_id})">{anim("opacity", vis, total)}{r["svg"]}</g>')
            # Cursor follows the typing, then waits for the output.
            end_typing = r["times"][-1] + 0.25
            xs = [(0, r["x0"]), (r["start"], r["x0"])] + [
                (tm, round(x + 2, 1)) for tm, x in zip(r["times"], r["stops"], strict=True)
            ]
            body.append(
                f'<rect x="{r["x0"]}" y="{r["y"] - 15}" width="9" height="{cursor_h}" rx="1.5" '
                f'fill="{C["prompt"]}" opacity="0">'
                + anim("x", xs, total, discrete=True)
                + anim(
                    "opacity",
                    [(0, 0), (r["start"], 0), (r["start"] + 0.01, 0.9), (end_typing, 0.9), (end_typing + 0.01, 0)],
                    total,
                    discrete=True,
                )
                + "</rect>"
            )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
        f'aria-label="wasta in a Node and a Python REPL">'
        f"<defs>{book.svg_defs()}</defs>{''.join(body)}</svg>\n"
    )


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    (out / "demo.svg").write_text(build(), encoding="utf-8")
