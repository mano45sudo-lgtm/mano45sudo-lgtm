"""1-bit pixel assets for the GitHub profile README.

    python tools/pixelgen.py

Black, white, greys, one red accent. Gradients are Bayer-dithered.
Edit the CONTENT block and re-run.
"""
import math
import os
import random

# ── CONTENT ───────────────────────────────────────────────────────
NAME = "MANOKARTHIK"
ROLE = "DESIGN ENGINEER"
NOW = "NOW: BUILDING MINIMI"
HANDLE = "GITHUB.COM/MANO45SUDO-LGTM"
SECTIONS = ["ABOUT", "WORK", "TOOLS", "ACTIVITY", "CONTACT"]
TOOLS = ["FIGMA", "REACT", "NEXT.JS", "TYPESCRIPT", "TAILWIND", "NODE.JS", "PYTHON", "REACT NATIVE"]
PROJECTS = [  # file id, title, two description lines, tag
    ("minimi", "MINIMI", "WEB SEARCH CHAT AGENT", "WITH DATED MEMORY", "TYPESCRIPT / NODE"),
    ("buildtogether", "BUILDTOGETHER", "TEAM WORKSPACE WHERE", "CHAT BECOMES TASKS", "TYPESCRIPT"),
    ("faceauth", "DATALAKE FACEAUTH", "OFFLINE FACE AUTH AND", "ATTENDANCE ON DEVICE", "REACT NATIVE"),
    ("talentiq", "TALENTIQ", "RESUME PARSING AND", "CANDIDATE SCORING", "NEXT.JS"),
]

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

BG = "#000000"
INK = "#f2f2f2"
GREY = "#8c8c8c"
DIM = "#4a4a4a"
LINE = "#1f1f1f"
RED = "#e5372b"

# ── 5x7 font ──────────────────────────────────────────────────────
_F = """
A .###. #...# #...# ##### #...# #...# #...#
B ####. #...# #...# ####. #...# #...# ####.
C .###. #...# #.... #.... #.... #...# .###.
D ####. #...# #...# #...# #...# #...# ####.
E ##### #.... #.... ####. #.... #.... #####
F ##### #.... #.... ####. #.... #.... #....
G .###. #...# #.... #.### #...# #...# .####
H #...# #...# #...# ##### #...# #...# #...#
I ##### ..#.. ..#.. ..#.. ..#.. ..#.. #####
J ..### ...#. ...#. ...#. #..#. #..#. .##..
K #...# #..#. #.#.. ##... #.#.. #..#. #...#
L #.... #.... #.... #.... #.... #.... #####
M #...# ##.## #.#.# #.#.# #...# #...# #...#
N #...# #...# ##..# #.#.# #..## #...# #...#
O .###. #...# #...# #...# #...# #...# .###.
P ####. #...# #...# ####. #.... #.... #....
Q .###. #...# #...# #...# #.#.# #..#. .##.#
R ####. #...# #...# ####. #.#.. #..#. #...#
S .#### #.... #.... .###. ....# ....# ####.
T ##### ..#.. ..#.. ..#.. ..#.. ..#.. ..#..
U #...# #...# #...# #...# #...# #...# .###.
V #...# #...# #...# #...# #...# .#.#. ..#..
W #...# #...# #...# #.#.# #.#.# ##.## #...#
X #...# #...# .#.#. ..#.. .#.#. #...# #...#
Y #...# #...# .#.#. ..#.. ..#.. ..#.. ..#..
Z ##### ....# ...#. ..#.. .#... #.... #####
0 .###. #...# #..## #.#.# ##..# #...# .###.
1 ..#.. .##.. ..#.. ..#.. ..#.. ..#.. .###.
2 .###. #...# ....# ...#. ..#.. .#... #####
3 ####. ....# ....# .###. ....# ....# ####.
4 ...#. ..##. .#.#. #..#. ##### ...#. ...#.
5 ##### #.... ####. ....# ....# #...# .###.
6 .###. #.... #.... ####. #...# #...# .###.
7 ##### ....# ...#. ..#.. .#... .#... .#...
8 .###. #...# #...# .###. #...# #...# .###.
9 .###. #...# #...# .#### ....# ....# .###.
- ..... ..... ..... .###. ..... ..... .....
. ..... ..... ..... ..... ..... ..... ..#..
, ..... ..... ..... ..... ..... ..#.. .#...
: ..... ..#.. ..... ..... ..... ..#.. .....
/ ....# ...#. ...#. ..#.. .#... .#... #....
^ .#### ...## ..#.# .#..# #.... ..... .....
"""
FONT = {" ": ["....."] * 7}
for _line in _F.strip().splitlines():
    _ch, *_rows = _line.split()
    FONT[_ch] = _rows


def tw(txt, scale=1):
    return len(txt) * 6 * scale - scale


BAYER = [
    [0, 32, 8, 40, 2, 34, 10, 42], [48, 16, 56, 24, 50, 18, 58, 26],
    [12, 44, 4, 36, 14, 46, 6, 38], [60, 28, 52, 20, 62, 30, 54, 22],
    [3, 35, 11, 43, 1, 33, 9, 41], [51, 19, 59, 27, 49, 17, 57, 25],
    [15, 47, 7, 39, 13, 45, 5, 37], [63, 31, 55, 23, 61, 29, 53, 21],
]


def dither(v, x, y):
    return v > (BAYER[y % 8][x % 8] + 0.5) / 64


# ── canvas: logical grid, rendered as stroked runs ────────────────
class Canvas:
    def __init__(self, w, h, s):
        self.w, self.h, self.s = w, h, s
        self.px = {}
        self.extra = []

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[(x, y)] = c

    def get(self, x, y):
        return self.px.get((x, y))

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def text(self, txt, x, y, scale, c, dot=0):
        """dot>0: draw each font pixel as a (scale-dot) square -> dot-matrix look."""
        for ch in txt:
            for ry, row in enumerate(FONT[ch]):
                for rx, b in enumerate(row):
                    if b == "#":
                        self.rect(x + rx * scale, y + ry * scale, scale - dot, scale - dot, c)
            x += 6 * scale

    def outline(self, c, inset=0):
        x0, y0, x1, y1 = inset, inset, self.w - 1 - inset, self.h - 1 - inset
        for x in range(x0 + 1, x1):
            self.set(x, y0, c)
            self.set(x, y1, c)
        for y in range(y0 + 1, y1):
            self.set(x0, y, c)
            self.set(x1, y, c)

    def svg(self, css="", bg=BG, radius=0):
        W, H = self.w * self.s, self.h * self.s
        bg_el = f'<rect width="{W}" height="{H}" rx="{radius}" fill="{bg}"/>' if bg else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
                f'shape-rendering="crispEdges"><style>{css}</style>{bg_el}'
                f'{runs(self.px, self.s)}{"".join(self.extra)}</svg>')


def runs(px, s, ox=0, oy=0, cls=""):
    """Turn {(x,y): colour} into one stroked path per colour (compact)."""
    by = {}
    for (x, y), c in px.items():
        by.setdefault(c, {}).setdefault(y, []).append(x)
    out = []
    for c, rows in by.items():
        d = []
        for y in sorted(rows):
            xs = sorted(rows[y])
            i = 0
            while i < len(xs):
                j = i
                while j + 1 < len(xs) and xs[j + 1] == xs[j] + 1:
                    j += 1
                d.append(f"M{ox + xs[i]*s} {oy + y*s + s/2:g}h{(j-i+1)*s}")
                i = j + 1
        attr = f' class="{cls}"' if cls else ""
        out.append(f'<path{attr} stroke="{c}" stroke-width="{s}" d="{"".join(d)}"/>')
    return "".join(out)


# ── the moon: lit sphere, cratered, rotating, 1-bit ───────────────
def moon_frames(r, frames, seed=3):
    rnd = random.Random(seed)
    craters = [(rnd.uniform(0, 2 * math.pi), rnd.uniform(-1.2, 1.2), rnd.uniform(0.07, 0.28)) for _ in range(34)]
    maria = [(rnd.uniform(0, 2 * math.pi), rnd.uniform(-0.6, 0.7), rnd.uniform(0.35, 0.6)) for _ in range(5)]
    L = (-0.55, -0.45, 0.7)
    n = math.sqrt(sum(v * v for v in L))
    L = tuple(v / n for v in L)

    def angdist(lon1, lat1, lon2, lat2):
        c = math.sin(lat1) * math.sin(lat2) + math.cos(lat1) * math.cos(lat2) * math.cos(lon1 - lon2)
        return math.acos(max(-1, min(1, c)))

    out = []
    for f in range(frames):
        rot = 2 * math.pi * f / frames
        px = {}
        for y in range(-r, r + 1):
            for x in range(-r, r + 1):
                nx, ny = (x + 0.5) / r, (y + 0.5) / r
                d2 = nx * nx + ny * ny
                if d2 > 1:
                    continue
                nz = math.sqrt(1 - d2)
                lon = math.atan2(nx, nz) + rot
                lat = math.asin(-ny)
                alb = 1.0
                for mlon, mlat, mr in maria:
                    d = angdist(lon, lat, mlon, mlat)
                    if d < mr:
                        alb *= 0.72 + 0.28 * (d / mr) ** 2
                for clon, clat, cr in craters:
                    d = angdist(lon, lat, clon, clat)
                    if d < cr:
                        alb *= 0.55 + 0.45 * (d / cr) ** 3
                    elif d < cr * 1.25:
                        alb *= 1.18
                alb *= 0.92 + 0.08 * math.sin(lon * 9 + math.sin(lat * 7) * 2)
                lam = max(0.0, nx * L[0] + ny * L[1] + nz * L[2])
                v = min(1.0, (lam ** 0.9) * alb * 1.08 + 0.015)
                gx, gy = x + r, y + r
                if dither(v, gx, gy):
                    px[(gx, gy)] = INK
                elif d2 > 0.93 and v < 0.05 and (gx + gy) % 3 == 0:
                    px[(gx, gy)] = "#262626"  # faint earthshine rim on the dark side
        out.append(px)
    return out


# ── header ────────────────────────────────────────────────────────
def header():
    W, H, s = 600, 210, 2
    c = Canvas(W, H, s)
    rnd = random.Random(9)
    m = 28

    c.text(ROLE, m, 24, 2, GREY)
    lbl = "GITHUB / README"
    c.text(lbl, W - m - tw(lbl, 2), 24, 2, DIM)

    c.text(NAME, m, 82, 5, INK, dot=1)

    c.rect(m, 140, 4, 4, RED)
    c.text(NOW, m + 10, 138, 2, GREY)

    for x in range(m, W - m, 4):
        c.rect(x, 176, 2, 1, LINE)
    c.text(HANDLE, m, 186, 2, DIM)
    c.text("2026", W - m - tw("2026", 2), 186, 2, DIM)

    # moon (rendered on a 4px grid, separately, as animated frames)
    R, F, CELL = 41, 16, 3
    cx, cy = 482, 100          # logical centre
    ox, oy = cx * s - R * CELL, cy * s - R * CELL
    frames = moon_frames(R, F)
    dur = 12
    groups = []
    for i, px in enumerate(frames):
        groups.append(f'<g class="f" style="animation-delay:{-dur + i*dur/F:.3f}s">{runs(px, CELL, ox, oy)}</g>')
    c.extra.append("".join(groups))

    # sparse stars, away from text and moon
    stars = []
    while len(stars) < 34:
        x, y = rnd.randrange(m, W - m), rnd.randrange(8, 170)
        if (x - cx) ** 2 + (y - cy) ** 2 < (R * CELL // 2 + 16) ** 2:
            continue
        if 16 < y < 44 or (70 < y < 152 and x < 400):
            continue
        stars.append((x, y))
    for i, (x, y) in enumerate(stars):
        if i % 6 == 0:
            c.extra.append(f'<rect class="tw" style="animation-delay:{i*0.37:.2f}s" x="{x*s}" y="{y*s}" width="{s*2}" height="{s*2}" fill="{INK}"/>')
        else:
            c.rect(x, y, 1, 1, "#5a5a5a" if i % 3 else "#3a3a3a")

    pct = 100 / F
    css = (f".f{{visibility:hidden;animation:f {dur}s linear infinite}}"
           f"@keyframes f{{0%,{pct:.3f}%{{visibility:visible}}{pct+0.001:.3f}%,100%{{visibility:hidden}}}}"
           ".tw{animation:tw 5s steps(1) infinite}@keyframes tw{0%,80%{opacity:.25}81%,100%{opacity:1}}")
    return c.svg(css, radius=12)


# ── footer: dithered ridgelines at night ──────────────────────────
def footer():
    W, H, s = 300, 72, 4
    c = Canvas(W, H, s)
    rnd = random.Random(4)

    def range_(n, ylo, yhi, slope_lo, slope_hi):
        step = (W + 40) / (n - 1)
        peaks = [(-20 + i * step + rnd.uniform(-step / 4, step / 4), rnd.uniform(ylo, yhi), rnd.uniform(slope_lo, slope_hi)) for i in range(n)]
        ys = []
        for x in range(W):
            y = min(py + sl * abs(x - px) for px, py, sl in peaks)
            ys.append(y + 0.8 * math.sin(x * 0.7) * math.sin(x * 0.13))
        return ys

    far = range_(7, 16, 30, 0.35, 0.6)
    mid = range_(8, 34, 44, 0.3, 0.55)
    near = range_(6, 52, 58, 0.12, 0.25)

    # stars
    for _ in range(40):
        x, y = rnd.randrange(W), rnd.randrange(4, 30)
        if y < far[x] - 3:
            c.set(x, y, "#3a3a3a" if rnd.random() < 0.7 else "#7a7a7a")

    for x in range(W):
        for y in range(H):
            if y >= near[x]:
                continue
            if y >= mid[x]:
                t = (y - mid[x]) / 14
                v = 0.10 + 0.12 * min(1, t)          # mist pooling in the valley
                col = "#7a7a7a"
            elif y >= far[x]:
                t = (y - far[x]) / 18
                v = 0.55 * max(0, 1 - t) + 0.06       # bright ridge, fading down
                col = INK
            else:
                continue
            if dither(v, x, y):
                c.set(x, y, col)
        c.set(x, int(far[x]), INK)
        c.set(x, int(mid[x]), "#bdbdbd")
        c.set(x, int(near[x]), "#2e2e2e")

    lx = 214
    ly = int(near[lx]) - 1
    c.extra.append(f'<rect class="lt" x="{lx*s}" y="{ly*s}" width="{s}" height="{s}" fill="{RED}"/>')
    msg = "THANKS FOR READING"
    c.text(msg, W - 12 - tw(msg), 8, 1, DIM)
    c.text("MK", 12, 8, 1, DIM)
    css = ".lt{animation:lt 3s ease-in-out infinite}@keyframes lt{0%,100%{opacity:1}50%{opacity:.3}}"
    return c.svg(css, radius=12)


# ── section rule: "01  ABOUT ··········" ─────────────────────────
def section(i, name):
    W, H, s = 600, 20, 2
    c = Canvas(W, H, s)
    num = f"{i:02d}"
    c.text(num, 0, 3, 2, DIM)
    x = tw(num, 2) + 12
    c.text(name, x, 3, 2, INK)
    for xx in range(x + tw(name, 2) + 12, W, 4):
        c.rect(xx, 10, 2, 1, LINE)
    return c.svg(bg=None)


# ── tools grid ────────────────────────────────────────────────────
def tools():
    cols, cw, rh = 3, 196, 30
    rows = math.ceil(len(TOOLS) / cols)
    W, H, s = 600, rows * rh + 14, 2
    c = Canvas(W, H, s)
    for i, t in enumerate(TOOLS):
        x, y = (i % cols) * cw + 16, (i // cols) * rh + 18
        c.rect(x, y + 4, 4, 4, DIM)
        c.text(t, x + 12, y + 1, 2, "#d0d0d0")
    c.outline(LINE)
    return c.svg(radius=10)


# ── project card ──────────────────────────────────────────────────
def card(idx, title, d1, d2, tag):
    W, H, s = 296, 128, 2
    c = Canvas(W, H, s)
    c.outline(LINE)
    p = 16
    c.text(f"{idx:02d}", p, p, 2, DIM)
    c.text("^", W - p - tw("^", 2), p, 2, GREY)
    c.text(title, p, 40, 2, INK)
    c.text(d1, p, 64, 2, "#636363")
    c.text(d2, p, 82, 2, "#636363")
    c.rect(p, 109, 4, 1, DIM)
    c.text(tag, p + 10, 106, 1, DIM)
    return c.svg(radius=10)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".svg"):
            os.remove(os.path.join(OUT, f))
    files = {"header.svg": header(), "footer.svg": footer(), "tools.svg": tools()}
    for i, name in enumerate(SECTIONS, 1):
        files[f"s-{name.lower()}.svg"] = section(i, name)
    for i, (fid, *rest) in enumerate(PROJECTS, 1):
        files[f"work-{fid}.svg"] = card(i, *rest)
    for name, svg in files.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
            fh.write(svg)
        print(f"{name:24s} {len(svg)/1024:6.1f} KB")
