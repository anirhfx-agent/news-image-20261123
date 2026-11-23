#!/usr/bin/env python3
"""The World in One Page -- make.fun bounty news-image-20261123.

Sums up world news of Monday 23 November 2026 in a single 1024x1024
PNG, drawn as a newspaper front page. Pure Python 3 standard library:
the page rasterizer, the 5x7 bitmap font and the PNG encoder are all
written in this one file, so the program needs no network, no system
fonts and no third-party packages at run time.

Deterministic: fixed layout, fixed palette, fixed zlib level, no clock,
no randomness, no hash-order dependence. Two runs write identical bytes.

Usage: python3 main.py
Writes: $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png)
"""
import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 228)   # newsprint cream
INK = (22, 22, 22)        # near-black ink
RED = (176, 30, 30)       # headline red
DARKRED = (138, 18, 18)
BLUE = (28, 74, 138)      # deep blue
NAVY = (14, 30, 60)       # night panel
SKY = (186, 216, 238)     # pale sky
GOLD = (198, 158, 40)     # gold accent
GREEN = (42, 122, 52)     # green accent
WHITE = (255, 255, 255)
GREY = (96, 94, 86)       # muted grey
LIGHT = (233, 228, 214)   # light panel
ORANGE = (230, 118, 28)
TEAL = (18, 110, 110)

# ---------------------------------------------------------------- 5x7 font
# Glyphs are 7 rows of 5 bits; '#' is ink. Uppercase, digits, punctuation.
# Text is set in capitals throughout; text() uppercases its input.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "01100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
}


# ---------------------------------------------------------------- canvas
class Canvas:
    """A plain RGB framebuffer with small drawing primitives."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bytes(bg) * (w * h))

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(c)

    def fill(self, x, y, w, h, c):
        x0 = max(x, 0)
        y0 = max(y, 0)
        x1 = min(x + w, self.w)
        y1 = min(y + h, self.h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def outline(self, x, y, w, h, c, t=1):
        self.fill(x, y, w, t, c)
        self.fill(x, y + h - t, w, t, c)
        self.fill(x, y, t, h, c)
        self.fill(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.fill(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        """Bresenham line, t pixels thick (square brush)."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill(x0 - t // 2, y0 - t // 2, t, t, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5)
            self.fill(cx - dx, yy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c, t=2):
        for yy in range(cy - r - t, cy + r + t + 1):
            for xx in range(cx - r - t, cx + r + t + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if r - t / 2 <= d <= r + t / 2:
                    self.put(xx, yy, c)

    def star(self, cx, cy, r, c, spikes=8):
        """Explosion starburst: straight spokes from the centre."""
        for k in range(spikes):
            a = math.pi * 2 * k / spikes
            self.line(cx, cy, int(cx + r * math.cos(a)),
                      int(cy + r * math.sin(a)), c, 3)
        self.disc(cx, cy, max(3, r // 4), c)

    # -- text -------------------------------------------------------------
    def twidth(self, s, scale):
        return len(s) * 6 * scale - scale

    def text(self, x, y, s, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.fill(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_c(self, y, s, scale, c):
        """Centred text on the full page width."""
        self.text((self.w - self.twidth(s, scale)) // 2, y, s, scale, c)

    def wrap(self, s, width, scale):
        """Greedy word wrap; returns a list of lines fitting width px."""
        limit = max(1, width // (6 * scale))
        lines = []
        for chunk in s.split('\n'):
            words = chunk.split(' ')
            cur = ''
            for word in words:
                trial = word if not cur else cur + ' ' + word
                if len(trial) <= limit:
                    cur = trial
                else:
                    if cur:
                        lines.append(cur)
                    while len(word) > limit:
                        lines.append(word[:limit])
                        word = word[limit:]
                    cur = word
            if cur or not lines:
                lines.append(cur)
        return lines

    def para(self, x, y, s, width, scale, c, leading=None):
        """Draw a wrapped paragraph; returns the y just below it."""
        lh = leading if leading is not None else 7 * scale + 4
        for line in self.wrap(s, width, scale):
            self.text(x, y, line, scale, c)
            y += lh
        return y


# ---------------------------------------------------------------- PNG encoder
def _chunk(kind, data):
    out = struct.pack('>I', len(data)) + kind + data
    out += struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    """Encode the canvas as a deterministic RGB PNG (filter 0 rows)."""
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.buf[y * stride:(y + 1) * stride]
    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b'\x89PNG\r\n\x1a\n'
    png += _chunk(b'IHDR', ihdr)
    png += _chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += _chunk(b'IEND', b'')
    return png


# ---------------------------------------------------------------- illustrations
def draw_flag_us(cv, x, y, w, h):
    """Stars and stripes, simplified: 7 stripes, blue canton, dot stars."""
    stripe = max(1, h // 7)
    for i in range(7):
        cv.fill(x, y + i * stripe, w, stripe, RED if i % 2 == 0 else WHITE)
    cw, ch = w * 2 // 5, stripe * 4
    cv.fill(x, y, cw, ch, BLUE)
    for r in range(3):
        for c in range(4):
            cv.disc(x + 6 + c * 9, y + 5 + r * 8, 1, WHITE)


def draw_clock(cv, cx, cy, r, hour, minute):
    """A clock face with hands at hour:minute."""
    cv.disc(cx, cy, r, WHITE)
    cv.ring(cx, cy, r, INK, 3)
    cv.ring(cx, cy, r - 6, RED, 1)
    for k in range(12):
        a = math.pi * 2 * k / 12
        x1 = int(cx + (r - 8) * math.sin(a))
        y1 = int(cy - (r - 8) * math.cos(a))
        cv.disc(x1, y1, 2, INK)
    ha = math.pi * 2 * (hour % 12 + minute / 60.0) / 12
    ma = math.pi * 2 * minute / 60.0
    cv.line(cx, cy, int(cx + (r * 0.5) * math.sin(ha)),
            int(cy - (r * 0.5) * math.cos(ha)), INK, 4)
    cv.line(cx, cy, int(cx + (r * 0.75) * math.sin(ma)),
            int(cy - (r * 0.75) * math.cos(ma)), INK, 3)
    cv.disc(cx, cy, 4, RED)


def draw_globe_crack(cv, cx, cy, r):
    """A cracked globe: teal disc, pale latitude lines, a white crack."""
    cv.disc(cx, cy, r, TEAL)
    cv.ring(cx, cy, r, WHITE, 2)
    for dy in (-r // 2, 0, r // 2):
        w = int((r * r - dy * dy) ** 0.5)
        cv.hline(cx - w, cy + dy, 2 * w, SKY, 2)
    # land blobs
    cv.disc(cx - r // 3, cy - r // 4, r // 4, GREEN)
    cv.disc(cx + r // 3, cy + r // 3, r // 5, GREEN)
    # jagged crack, top to bottom
    pts = [(cx - 10, cy - r + 4), (cx + 8, cy - r // 2), (cx - 14, cy),
           (cx + 10, cy + r // 2), (cx - 6, cy + r - 4)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        cv.line(x0, y0, x1, y1, WHITE, 4)
        cv.line(x0, y0, x1, y1, RED, 2)


def draw_seat_bar(cv, x, y, w, h, dem, rep):
    """House seat bar: blue Democrats, red Republicans, 435 seats total."""
    total = dem + rep
    cv.outline(x, y, w, h, INK, 2)
    bw = w - 4
    dw = bw * dem // total
    cv.fill(x + 2, y + 2, dw, h - 4, BLUE)
    cv.fill(x + 2 + dw, y + 2, bw - dw, h - 4, RED)


def draw_warship(cv, x, y, w, h):
    """A warship listing to starboard, on fire, on dark water."""
    # hull, tilted: bow up-left, stern down-right
    cv.line(x + 6, y + h // 2, x + w - 6, y + h // 2 + 14, WHITE, 3)
    cv.fill(x + 10, y + h // 2, w - 26, 12, WHITE)
    cv.fill(x + w // 3, y + h // 2 - 16, w // 5, 16, WHITE)
    cv.fill(x + w * 2 // 3, y + h // 2 - 26, 6, 26, WHITE)
    cv.line(x + w * 2 // 3 + 3, y + h // 2 - 26, x + w * 2 // 3 + 3,
            y + h // 2 - 40, WHITE, 2)
    # flames above the deck
    cv.star(x + w // 2, y + h // 2 - 34, 18, ORANGE, 9)
    cv.star(x + w // 2, y + h // 2 - 34, 10, GOLD, 7)
    # waves
    for k in range(3):
        wy = y + h - 12 + k * 6
        cv.hline(x + 4 + k * 8, wy, w - 16 - k * 8, SKY, 2)


def draw_drone(cv, x, y, s=1):
    """A small sea drone with a wake line behind it."""
    cv.disc(x, y, 4, WHITE)
    cv.fill(x - 8, y - 2, 6, 4, WHITE)
    cv.line(x - 8, y, x - 26, y, SKY, 2)
    cv.line(x - 8, y - 3, x - 22, y - 3, SKY, 1)


def draw_rubble(cv, x, y, w, h):
    """A collapsed five-storey block: broken slabs and a hopeful star."""
    # leaning slabs
    cv.line(x + 8, y + h - 8, x + w // 2 - 6, y + 20, GREY, 8)
    cv.line(x + w // 2 + 6, y + 12, x + w - 10, y + h - 8, GREY, 8)
    cv.fill(x + w // 2 - 14, y + h - 26, 28, 18, WHITE)
    cv.fill(x + 16, y + h - 16, 30, 8, WHITE)
    cv.fill(x + w - 52, y + h - 14, 34, 6, WHITE)
    # the light that found the boy
    cv.star(x + w // 2, y + 34, 30, GOLD, 8)
    cv.star(x + w // 2, y + 34, 16, WHITE, 6)


def draw_prime_steps(cv, x, y, w, h):
    """A rising prime staircase with a big question mark over it."""
    steps = (6, 14, 22, 34, 46, 58, 74, 92)
    n = len(steps)
    sw = w // n
    for i, s in enumerate(steps):
        cv.fill(x + i * sw, y + h - s, sw - 4, s, BLUE)
    cv.text(x + w - 44, y + 2, "?", 5, GOLD)
    cv.text(x + 2, y + h - 8, "2 3 5 7 11 13", 1, GREY)


# ---------------------------------------------------------------- page furniture
def kicker(cv, x, y, label, accent=RED):
    cv.fill(x, y - 2, 26, 4, accent)
    cv.text(x + 34, y - 4, label, 2, accent)


def rule(cv, y, x0=24, x1=1000, c=INK, t=2):
    cv.hline(x0, y, x1 - x0, c, t)


def masthead(cv):
    cv.text_c(24, "THE WORLD IN ONE PAGE", 5, INK)
    cv.text_c(72, "MONDAY 23 NOVEMBER 2026", 3, RED)
    cv.text(24, 100, "ONE DAY IN ONE PICTURE", 1, GREY)
    right = "VOL. 1 - NO. 327"
    cv.text(1000 - cv.twidth(right, 1), 100, right, 1, GREY)
    rule(cv, 116, 24, 1000, INK, 3)
    rule(cv, 122, 24, 1000, INK, 1)


def lead_story(cv):
    """Top story: COP31 collapses in Antalya with no deal."""
    y = 140
    kicker(cv, 24, y + 4, "CLIMATE - ANTALYA")
    cv.para(24, y + 26, "COP31 COLLAPSES:", 540, 4, INK, 34)
    cv.para(24, y + 60, "NO DEAL IN ANTALYA", 540, 4, RED, 34)
    cv.para(24, y + 108,
            "Nearly 200 countries leave Antalya with no overarching "
            "climate deal after almost 48 hours of overtime talks. "
            "The EU refused any text without language on phasing "
            "out fossil fuels.",
            536, 2, INK, 19)
    cv.para(24, y + 208,
            "Draft texts had dropped the fossil-fuel wording and a "
            "$120bn finance target. Talks end with no agreement.",
            536, 2, GREY, 19)
    # illustration: cracked globe, 48 hours over
    px, py, pw, ph = 584, 132, 416, 268
    cv.fill(px, py, pw, ph, NAVY)
    cv.outline(px, py, pw, ph, INK, 2)
    cv.text(px + 16, py + 12, "ANTALYA, TURKIYE", 1, WHITE)
    draw_globe_crack(cv, px + 110, py + 145, 78)
    cv.text(px + 240, py + 96, "48H", 5, GOLD)
    cv.text(px + 240, py + 140, "OVERTIME", 2, WHITE)
    cv.text(px + 240, py + 164, "NO DEAL", 2, RED)
    cv.text(px + 16, py + 240, "NEARLY 200 COUNTRIES, NO AGREEMENT",
            1, GREY)
    rule(cv, 416, 24, 1000, INK, 2)


def house_panel(cv):
    """Democrats clinch 258 House seats, the largest since 1992."""
    x, y, w, h = 24, 432, 476, 224
    cv.fill(x, y, w, h, LIGHT)
    cv.outline(x, y, w, h, INK, 2)
    kicker(cv, x + 16, y + 20, "WASHINGTON", RED)
    draw_flag_us(cv, x + 380, y + 14, 80, 40)
    cv.para(x + 16, y + 44, "DEMOCRATS CLINCH 258", 444, 3, INK, 26)
    cv.para(x + 16, y + 70, "LARGEST SINCE 1992", 444, 3, RED, 26)
    cv.para(x + 16, y + 106,
            "AP calls at least 258 seats for the Democrats in the "
            "midterms - the largest House majority for either "
            "party since 1992.",
            444, 2, INK, 19)
    draw_seat_bar(cv, x + 16, y + 184, 444, 22, 258, 177)
    cv.text(x + 16, y + 210, "DEM 258 - REP 177 - 435 SEATS", 1, INK)


def libya_panel(cv):
    """Ukraine sinks the Russian corvette Merkury off Benghazi."""
    x, y, w, h = 524, 432, 476, 224
    cv.fill(x, y, w, h, NAVY)
    cv.outline(x, y, w, h, INK, 2)
    kicker(cv, x + 16, y + 20, "LIBYA - BENGHAZI", ORANGE)
    cv.para(x + 16, y + 44, "UKRAINE SINKS RUSSIAN", 444, 3, WHITE, 26)
    cv.para(x + 16, y + 70, "WARSHIP IN LIBYA", 444, 3, WHITE, 26)
    cv.para(x + 16, y + 106,
            "Seven sea drones sink the corvette Merkury in "
            "Benghazi port. A Ka-27 helicopter is destroyed; "
            "the MV Angara is hit too.",
            290, 2, WHITE, 19)
    cv.text(x + 316, y + 98, "2,400 KM FROM THE FRONT", 1, SKY)
    draw_warship(cv, x + 316, y + 132, 144, 66)
    draw_drone(cv, x + 336, y + 204)


def dymer_panel(cv):
    """Russian strike on Dymer kills 11; a boy survives 14 hours."""
    x, y, w, h = 24, 672, 476, 212
    cv.fill(x, y, w, h, NAVY)
    cv.outline(x, y, w, h, INK, 2)
    kicker(cv, x + 16, y + 20, "UKRAINE - DYMER", ORANGE)
    cv.para(x + 16, y + 44, "11 KILLED IN KYIV", 444, 3, WHITE, 26)
    cv.para(x + 16, y + 70, "REGION STRIKE", 444, 3, WHITE, 26)
    cv.para(x + 16, y + 106,
            "A strike flattens a five-storey block in Dymer. "
            "Rescuers pull seven-year-old Davyd alive after "
            "14 hours under the rubble.",
            290, 2, WHITE, 19)
    draw_rubble(cv, x + 316, y + 104, 144, 92)
    cv.text(x + 316, y + 200, "BOY, 7, ALIVE", 1, GOLD)


def riemann_panel(cv):
    """Anthropic's Alpoge and Claude claim a Riemann proof."""
    x, y, w, h = 524, 672, 476, 212
    cv.fill(x, y, w, h, WHITE)
    cv.outline(x, y, w, h, INK, 2)
    kicker(cv, x + 16, y + 20, "MATH - AI", BLUE)
    cv.para(x + 16, y + 44, "CLAUDE 'PROVES' RIEMANN?", 444, 3, RED, 26)
    cv.para(x + 16, y + 74,
            "Anthropic's Alpoge says he and Claude proved the "
            "1859 Riemann Hypothesis in 175,187 Lean files. "
            "Unverified; a rival proof lands the same day.",
            290, 2, INK, 19)
    draw_prime_steps(cv, x + 316, y + 80, 144, 96)
    cv.text(x + 316, y + 182, "175,187 FILES", 1, GREY)


def footer(cv):
    """Also today: six more stories from Monday 23 November."""
    y = 900
    rule(cv, y, 24, 1000, INK, 2)
    cv.text(24, y + 12, "ALSO TODAY", 2, RED)
    items = [
        ("JUSTICE", "World Court: Myanmar committed genocide, 9-6 - "
         "first in 80 years. Myanmar calls it 'not fair'."),
        ("INDONESIA", "Factory fire in Banten kills 24; about 30 "
         "still unaccounted for."),
        ("SPORT", "Liverpool thrash 10-man Man Utd 4-0 in "
         "Pochettino's first match."),
        ("USA", "Delta delays top 1,000 flights at Atlanta after "
         "a system failure."),
        ("IRAN", "Trump 'inclined' to resume conflict if no deal "
         "by New Year."),
        ("ECONOMY", "South Korea's exports top $1 trillion for "
         "the first time."),
    ]
    col_w = 488
    for i, (tag, body) in enumerate(items):
        cx = 24 + (i % 2) * (col_w + 24)
        cy = y + 36 + (i // 2) * 26
        cv.text(cx, cy, tag + ":", 1, RED)
        cv.para(cx + cv.twidth(tag + ": ", 1), cy, body, 400, 1, INK, 10)
    rule(cv, 1014, 24, 1000, INK, 1)


# ---------------------------------------------------------------- main
def main():
    cv = Canvas(W, H, PAPER)
    masthead(cv)
    lead_story(cv)
    house_panel(cv)
    libya_panel(cv)
    dymer_panel(cv)
    riemann_panel(cv)
    footer(cv)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(encode_png(cv))
    print("wrote", path)


if __name__ == "__main__":
    main()
