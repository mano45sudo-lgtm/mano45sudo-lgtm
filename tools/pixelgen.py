"""1-bit pixel banner for the GitHub profile README.

    python tools/pixelgen.py

Black, white, greys, one red accent. Gradients are Bayer-dithered.
"""
import math
import os
import random

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
        self.under = []

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
                f'{"".join(self.under)}{runs(self.px, self.s)}{"".join(self.extra)}</svg>')


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


# ── banner: moon rising behind dithered mountains (no text) ───────
def banner():
    W, H, s = 300, 72, 4
    c = Canvas(W, H, s)
    rnd = random.Random(4)

    def range_(n, ylo, yhi, slope_lo, slope_hi):
        step = (W + 40) / (n - 1)
        peaks = [(-20 + i * step + rnd.uniform(-step / 4, step / 4), rnd.uniform(ylo, yhi),
                  rnd.uniform(slope_lo, slope_hi)) for i in range(n)]
        return [min(py + sl * abs(x - px) for px, py, sl in peaks) + 0.8 * math.sin(x * 0.7) * math.sin(x * 0.13)
                for x in range(W)]

    far = range_(7, 30, 42, 0.35, 0.6)
    mid = range_(8, 46, 54, 0.3, 0.55)
    near = range_(6, 61, 66, 0.12, 0.25)

    # moon: cell size == banner pixel size, drawn underneath the mountains
    R, F, dur = 17, 16, 12
    mcx, mcy = 214, 27
    frames = moon_frames(R, F)
    c.under.append("".join(
        f'<g class="f" style="animation-delay:{-dur + i*dur/F:.3f}s">{runs(px, s, (mcx-R)*s, (mcy-R)*s)}</g>'
        for i, px in enumerate(frames)))

    for i in range(46):
        x, y = rnd.randrange(W), rnd.randrange(3, 34)
        if y >= far[x] - 3 or (x - mcx) ** 2 + (y - mcy) ** 2 < (R + 4) ** 2:
            continue
        if i % 9 == 0:
            c.extra.append(f'<rect class="tw" style="animation-delay:{i*0.31:.2f}s" x="{x*s}" y="{y*s}" width="{s}" height="{s}" fill="{INK}"/>')
        else:
            c.set(x, y, "#3a3a3a" if rnd.random() < 0.7 else "#7a7a7a")

    for x in range(W):
        for y in range(int(far[x]), H):
            if y >= near[x]:
                col, v = None, 0
            elif y >= mid[x]:
                col, v = "#7a7a7a", 0.10 + 0.12 * min(1, (y - mid[x]) / 14)
            else:
                col, v = INK, 0.55 * max(0, 1 - (y - far[x]) / 18) + 0.06
            c.set(x, y, col if col and dither(v, x, y) else BG)   # opaque: hides the moon
        c.set(x, int(far[x]), INK)
        c.set(x, int(mid[x]), "#bdbdbd")
        c.set(x, int(near[x]), "#2e2e2e")

    lx = 214
    c.extra.append(f'<rect class="lt" x="{lx*s}" y="{(int(near[lx])-1)*s}" width="{s}" height="{s}" fill="{RED}"/>')
    pct = 100 / F
    css = (f".f{{visibility:hidden;animation:f {dur}s linear infinite}}"
           f"@keyframes f{{0%,{pct:.3f}%{{visibility:visible}}{pct+0.001:.3f}%,100%{{visibility:hidden}}}}"
           ".tw{animation:tw 5s steps(1) infinite}@keyframes tw{0%,80%{opacity:.25}81%,100%{opacity:1}}"
           ".lt{animation:lt 3s ease-in-out infinite}@keyframes lt{0%,100%{opacity:1}50%{opacity:.3}}")
    return c.svg(css, radius=10)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith(".svg"):
            os.remove(os.path.join(OUT, f))
    svg = banner()
    with open(os.path.join(OUT, "banner.svg"), "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"banner.svg {len(svg)/1024:.1f} KB")
