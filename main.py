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
NAVY = (14, 30, 60)       # night blue
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
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '*': ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
}

# ---------------------------------------------------------------- canvas
# A flat RGB bytearray, row-major. All drawing goes through these helpers.
pix = bytearray(W * H * 3)


def _set(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        pix[i] = color[0]
        pix[i + 1] = color[1]
        pix[i + 2] = color[2]


def fill(color):
    for i in range(0, W * H * 3, 3):
        pix[i] = color[0]
        pix[i + 1] = color[1]
        pix[i + 2] = color[2]


def fill_rect(x, y, w, h, color):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            pix[i] = color[0]
            pix[i + 1] = color[1]
            pix[i + 2] = color[2]


def hline(x, y, w, color, thick=1):
    fill_rect(x, y, w, thick, color)


def vline(x, y, h, color, thick=1):
    fill_rect(x, y, thick, h, color)


def rect(x, y, w, h, color, thick=1):
    hline(x, y, w, color, thick)
    hline(x, y + h - thick, w, color, thick)
    vline(x, y, h, color, thick)
    vline(x + w - thick, y, h, color, thick)


def line(x0, y0, x1, y1, color):
    # Bresenham's line algorithm.
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        _set(x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def disc(cx, cy, r, color):
    # Filled circle by horizontal spans.
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)


def ring(cx, cy, r, color, thick=2):
    # Circle outline: draw concentric discs and erase the middle.
    disc(cx, cy, r, color)
    disc(cx, cy, r - thick, PAPER)


def polyline(points, color):
    for (ax, ay), (bx, by) in zip(points, points[1:]):
        line(ax, ay, bx, by, color)


# ---------------------------------------------------------------- text
def text_w(s, scale=1):
    return len(s) * 6 * scale


def text(x, y, s, scale=1, color=INK):
    s = s.upper()
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[' '])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '1':
                    fill_rect(cx + col * scale, y + row * scale,
                              scale, scale, color)
        cx += 6 * scale


def wrap(s, max_w, scale=1):
    # Break text into lines that fit max_w pixels at the given scale.
    words = s.upper().split(' ')
    lines = []
    cur = ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if text_w(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(x, y, s, max_w, scale=1, color=INK, gap=11):
    lines = wrap(s, max_w, scale)
    for i, ln in enumerate(lines):
        text(x, y + i * gap, ln, scale, color)
    return y + len(lines) * gap


# ---------------------------------------------------------------- PNG encoder
def _chunk(kind, data):
    out = struct.pack('>I', len(data))
    out += kind
    out += data
    out += struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png():
    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += pix[yy * W * 3:(yy + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)
    return (b'\x89PNG\r\n\x1a\n'
            + _chunk(b'IHDR', ihdr)
            + _chunk(b'IDAT', comp)
            + _chunk(b'IEND', b''))


# ---------------------------------------------------------------- layout
def masthead():
    title = "THE WORLD IN ONE PAGE"
    text((W - text_w(title, 4)) // 2, 26, title, 4, INK)
    hline(24, 62, W - 48, INK, 2)
    text(24, 72, "NO. 327", 1, GREY)
    date = "MONDAY, 23 NOVEMBER 2026"
    text((W - text_w(date, 2)) // 2, 70, date, 2, INK)
    price = "PRICE: ONE DAY"
    text(W - 24 - text_w(price, 1), 72, price, 1, GREY)
    hline(24, 96, W - 48, INK, 2)


def lead():
    text(32, 112, "CLIMATE", 2, RED)
    text(32, 132, "COP31 COLLAPSES", 5, INK)
    text(32, 176, "NO DEAL IN ANTALYA", 3, DARKRED)
    y = para(32, 212,
             "AFTER TWO WEEKS OF TALKS AND 48 HOURS OF OVERTIME, "
             "NEARLY 200 NATIONS LEFT ANTALYA WITH NO DEAL. THE EU "
             "REFUSED ANY TEXT WITHOUT FOSSIL FUEL LANGUAGE.",
             560, 1, INK, 11)
    y = para(32, y + 8,
             "SAUDI ARABIA AND OTHER OIL STATES BLOCKED ANY MENTION "
             "OF OIL, GAS AND COAL. MORE THAN 130 COUNTRIES DEMANDED "
             "A PHASE-OUT. PRESIDENT MURAT KURUM: NO CONSENSUS.",
             560, 1, INK, 11)
    y = para(32, y + 8,
             "THE LONGEST COP IN HISTORY ENDS IN FAILURE, THE FIRST "
             "SINCE COPENHAGEN IN 2009.",
             560, 1, DARKRED, 11)
    # By the numbers: three stat boxes filling the lower lead column.
    stats = [("258", "DEM HOUSE SEATS"),
             ("7", "SEA DRONES"),
             ("175,187", "LEAN FILES")]
    for i, (num, label) in enumerate(stats):
        bx = 32 + i * 190
        rect(bx, 310, 176, 64, INK, 1)
        text(bx + 12, 322, num, 3, BLUE)
        text(bx + 12, 352, label, 1, GREY)
    # Cracked globe on the right: ring first, then blue disc, green land
    # blobs, red crack. (The ring erases its own middle, so it must come
    # before the fill.)
    cx, cy, r = 810, 280, 105
    ring(cx, cy, r, NAVY, 3)
    disc(cx, cy, r - 3, SKY)
    disc(cx - 38, cy - 30, 26, GREEN)
    disc(cx + 30, cy - 48, 18, GREEN)
    disc(cx + 42, cy + 34, 22, GREEN)
    disc(cx - 30, cy + 48, 15, GREEN)
    polyline([(cx - 88, cy - 62), (cx - 40, cy - 18), (cx - 70, cy + 8),
              (cx - 12, cy + 40), (cx + 30, cy + 12), (cx + 62, cy + 52),
              (cx + 88, cy + 20)], RED)
    polyline([(cx - 40, cy - 18), (cx - 6, cy - 44), (cx + 26, cy - 30)],
             DARKRED)
    tag = "48H OVERTIME"
    text(cx - text_w(tag, 1) // 2, cy + r + 12, tag, 1, DARKRED)
    hline(24, 436, W - 48, INK, 2)


def panel(x, y, kicker, headline):
    rect(x, y, 480, 156, INK, 2)
    text(x + 12, y + 10, kicker, 1, RED)
    text(x + 12, y + 26, headline, 2, INK)


def panel_democrats(x, y):
    panel(x, y, "WASHINGTON", "DEMOCRATS TAKE 258")
    para(x + 12, y + 50,
         "LARGEST HOUSE MAJORITY SINCE 1992. HUBBARD BEATS FOXX IN N.C.",
         456, 1, INK, 11)
    text(x + 12, y + 92, "DEM 258", 1, BLUE)
    text(x + 12 + 270, y + 92, "GOP 177", 1, RED)
    fill_rect(x + 12, y + 106, 270, 16, BLUE)
    fill_rect(x + 12 + 270, y + 106, 186, 16, RED)
    text(x + 12, y + 130, "44 SEATS GAINED. 4 RACES UNCALLED.", 1, GREY)


def panel_merkury(x, y):
    panel(x, y, "LIBYA", "UKRAINE SINKS WARSHIP")
    para(x + 12, y + 50,
         "7 SEA DRONES SINK THE CORVETTE MERKURY IN BENGHAZI, 2,400 KM "
         "FROM THE FRONT. A KA-27 HELICOPTER IS DESTROYED AND THE MV "
         "ANGARA IS HIT.",
         456, 1, INK, 11)
    # Ship: hull, mast and flag, with seven drone dots above it.
    hx, hy = x + 150, y + 132
    fill_rect(hx, hy, 180, 10, NAVY)
    line(hx, hy, hx + 22, hy - 14, NAVY)
    line(hx + 180, hy, hx + 158, hy - 14, NAVY)
    vline(hx + 90, hy - 34, 34, NAVY, 3)
    fill_rect(hx + 93, hy - 34, 22, 10, RED)
    for i, dx in enumerate((-120, -80, -40, 0, 40, 80, 120)):
        disc(hx + 90 + dx, hy - 52 - (abs(i - 3) * -4), 3, RED)


def panel_dymer(x, y):
    panel(x, y, "UKRAINE", "BOY, 7, ALIVE IN RUBBLE")
    para(x + 12, y + 50,
         "A RUSSIAN DRONE FLATTENS A FIVE-STOREY BLOCK IN DYMER. 11 "
         "KILLED. RESCUERS PULL DAVYD OUT AFTER 14 HOURS. KYIV REGION "
         "MOURNS.",
         456, 1, INK, 11)
    # Rescue starburst: eight spokes from one centre.
    cx, cy = x + 240, y + 118
    for ang in range(8):
        dx = int(26 * [1, 0.7, 0, -0.7, -1, -0.7, 0, 0.7][ang])
        dy = int(26 * [0, 0.7, 1, 0.7, 0, -0.7, -1, -0.7][ang])
        line(cx, cy, cx + dx, cy + dy, GOLD)
    disc(cx, cy, 8, GOLD)
    text(cx - 3, cy - 3, "7", 1, NAVY)


def panel_riemann(x, y):
    panel(x, y, "MATHEMATICS", "A MACHINE PROVES RIEMANN?")
    para(x + 12, y + 50,
         "ALPOGE AND CLAUDE CLAIM A PROOF IN 175,187 LEAN FILES. THE "
         "LEAN COMMUNITY CERTIFIES IT. DEBATE GOES ON.",
         456, 1, INK, 11)
    # Prime staircase: ascending bars, one per prime under 30.
    bx, by = x + 60, y + 138
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    for i, p in enumerate(primes):
        h = 6 + p
        fill_rect(bx + i * 34, by - h, 22, h, TEAL)
    text(bx + 340, by - 18, "?", 3, RED)


def footer_item(x, y, kicker, body):
    text(x, y, kicker, 1, RED)
    para(x, y + 12, body, 320, 1, INK, 11)


def footer():
    hline(24, 788, W - 48, INK, 2)
    footer_item(24, 800, "THE HAGUE",
                "ICJ: MYANMAR COMMITTED GENOCIDE, 9-6. FIRST SUCH "
                "RULING IN 80 YEARS.")
    footer_item(352, 800, "BANTEN",
                "FACTORY FIRE KILLS 24, DOZENS MISSING IN SERANG.")
    footer_item(680, 800, "SPORT",
                "LIVERPOOL 4-0 MAN UTD. POCHETTINO DEBUT ENDS IN ROUT.")
    footer_item(24, 880, "TRAVEL",
                "DELTA SYSTEM FAILURE DELAYS 1,000+ FLIGHTS IN ATLANTA.")
    footer_item(352, 880, "WASHINGTON",
                "TRUMP INCLINED TO RESUME IRAN STRIKES AFTER NEW YEAR.")
    footer_item(680, 880, "TRADE",
                "S. KOREA EXPORTS TOP $1 TRILLION, A FIRST. CHIPS LEAD.")
    hline(24, 968, W - 48, INK, 2)
    foot = "SOURCES: CNN, REUTERS, AP, BBC - THE WORLD IN ONE PAGE"
    text((W - text_w(foot, 1)) // 2, 980, foot, 1, GREY)


def main():
    fill(PAPER)
    rect(8, 8, W - 16, H - 16, INK, 2)
    masthead()
    lead()
    panel_democrats(24, 448)
    panel_merkury(520, 448)
    panel_dymer(24, 620)
    panel_riemann(520, 620)
    footer()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(encode_png())
    print("wrote", path)


if __name__ == "__main__":
    main()
