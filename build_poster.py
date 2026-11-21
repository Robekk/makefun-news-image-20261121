#!/usr/bin/env python3
"""Build the news-image poster for Saturday 21 November 2026.

Renders a broadsheet-style front page at 2048x2048 with PIL, then
downscales to 1024x1024 and saves entry.png next to this file.
Deterministic: no randomness, no timestamps in the image.
Build-time tool only -- main.py does not import this or PIL.
"""

import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

PAPER = (246, 239, 219)   # #f6efdb
INK = (25, 25, 25)        # #191919
RED = (179, 53, 44)       # #b3352c
FAINT = (216, 205, 178)   # map land dots / pale panels
PALE = (238, 229, 203)    # illustration sky
WHITE = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def wrap(draw, text, font, maxw):
    """Greedy word wrap using real font metrics."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, x, y, lines, font, lh, fill=INK):
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


def tracked_width(draw, text, font, tracking):
    return sum(draw.textlength(ch, font=font) for ch in text) + tracking * (len(text) - 1)


def draw_tracked(draw, x, y, text, font, fill, tracking):
    cx = x
    for ch in text:
        draw.text((cx, y), ch, font=font, fill=fill)
        cx += draw.textlength(ch, font=font) + tracking
    return cx


def draw_tracked_right(draw, right, y, text, font, fill, tracking):
    w = tracked_width(draw, text, font, tracking)
    draw_tracked(draw, right - w, y, text, font, fill, tracking)


# ---------------------------------------------------------------- content

STATS = [
    ("$1.91bn", "liquidated in 24 hours as Bitcoin fell below $59,000"),
    ("92,000", "people at COP31 in Antalya, the largest summit ever"),
    ("~900,000", "AI chips cleared for China in six months, says a US House panel"),
    ("3", "Houthi missiles downed over Riyadh"),
    ("42", "people hurt in the Kryvyi Rih strike; 2 killed"),
    ("8 yrs", "BepiColombo's voyage to Mercury ends tonight"),
]

TIMELINE = [
    ("Overnight", "Russia strikes three Kyiv bridges; a missile lands in Poland"),
    ("~02:00 UTC", "Riyadh downs Houthi missiles, the second attack in days"),
    ("Morning", "COP31's third draft due in Antalya; talks in overtime"),
    ("Midday", "Spain's general strike halts the country"),
    ("18:24 UTC", "BepiColombo fires its thrusters at Mercury"),
]

HEROES = [
    ("1", "KYIV · UKRAINE WAR · TODAY",
     "Russia strikes Kyiv's bridges as a missile lands in Poland",
     "Moscow's strike hit three Kyiv bridges and killed 12 across Ukraine, "
     "officials say; a Russian missile came down in Polish territory, Warsaw "
     "sought NATO support, Danish jets scrambled. In Kryvyi Rih, 2 died and "
     "42 were hurt."),
    ("2", "ANTALYA · CLIMATE · TODAY",
     "COP31 runs into overtime with no deal",
     "A third draft is due Saturday morning after talks passed their Friday "
     "deadline. The fossil-fuel words are out, the $120bn adaptation figure "
     "is gone, and delegates unfurled a 'failure' banner; Kurum: 'close to "
     "the finish line'."),
    ("3", "MARKETS · CRYPTO · TODAY",
     "Bitcoin falls below $59,000 in a $1.91bn washout",
     "More than 292,000 traders were liquidated in 24 hours as crypto "
     "followed Friday's stock rout down. Bitcoin trades near $58,400, "
     "Ether fell 7.6% to $1,622, and the fear gauge sits at 12: extreme fear."),
]

CARDS = [
    ("4", "RIYADH · CONFLICT", True,
     "Riyadh downs three Houthi missiles",
     "Air defences destroyed three ballistic missiles fired at the capital "
     "early Saturday, the second attack in days; debris caused damage."),
    ("5", "MERCURY · SPACE · ESA", False,
     "BepiColombo reaches Mercury after eight years",
     "The ESA-JAXA craft fires its thrusters at 19:24 CET tonight to be "
     "caught by Mercury's gravity: two orbiters there at once, a first."),
    ("6", "BEIJING · TECH", False,
     "US cleared ~900,000 AI chips for China",
     "Washington approved nearly 900,000 AI chip sales to Chinese firms in "
     "six months, a House panel reports; California subpoenas Nvidia."),
    ("7", "WELLINGTON · ELECTION", False,
     "New Zealand's election is too close to call",
     "Preliminary results give PM Luxon's right coalition a razor-thin "
     "lead; special votes, counted by 27 November, will decide it."),
    ("8", "DANDONG · DIPLOMACY", True,
     "Kim Jong-un crosses into China by the new bridge",
     "North Korea's leader arrived in Dandong Saturday over the new Yalu "
     "River Bridge, a Korean source says; Trump was too busy to meet him."),
    ("9", "BRUSSELS · EUROPE · EU", False,
     "EU pays out nearly €8bn to Ukraine",
     "The bloc's largest-ever one-off payment to Kyiv, €7.9bn, plus €1bn in "
     "military aid; Britain will supply 1,000 long-range drones for £260m."),
    ("10", "COPENHAGEN · SECURITY", False,
     "Denmark charges two over a Russian murder plot",
     "Two Danes are accused of being recruited by Russia to kill a Ukrainian "
     "rapper; Denmark expelled Russia's defence attaché."),
    ("11", "MADRID · STRIKE", False,
     "General strike brings Spain to a halt",
     "Workers and students walked out over living costs; in Rome the same "
     "day they marched against Meloni's budget."),
    ("12", "HODEIDAH · YEMEN · WAR", False,
     "UN warns port strikes threaten a lifeline",
     "Civilians were told to leave the port area as the coalition hit Houthi "
     "targets, including six missile and drone workshops in Sana'a."),
    ("13", "NEW YORK · CYBER", True,
     "Banks hit in attack on outside vendors",
     "JPMorgan, Visa and Mastercard report cyber incidents at third-party "
     "providers; payment networks unaffected."),
]

BRIEFS = [
    (14, "EU and Canada deepen ties on minerals and defence"),
    (15, "Ukraine says it struck three Russian missile launchers"),
    (16, "Pentagon: US engagement against Iran cost $48.3bn"),
    (17, "Switzerland calls ICJ Myanmar ruling an important step"),
    (18, "Hyundai unveils the 2027 Elantra at the LA Auto Show"),
    (19, "UN yearbook: only 44 of 96 climate indicators improving"),
    (20, "Pill hailed as a breakthrough for pancreatic cancer"),
    (21, "LA jury convicts a man over the Palisades Fire"),
    (22, "Turkey flies its jet-propelled Kizilelma drone fighter"),
    (23, "El Salvador's Bukele seeks third term"),
    (24, "Venezuela rejects ICJ on Essequibo; wants Guyana talks"),
    (25, "Sudan's army dismantles RSF strongholds in West Kordofan"),
    (26, "Iraq enters Jurf al-Sakhar after 12 years of Kataib Hezbollah"),
    (27, "Indian man gets 19 years in US over Sikh murder plot"),
    (28, "Russia jails a former deputy defence minister for 10 years"),
    (29, "Germany's minister regrets 'foolish' US Ukraine comment"),
    (30, "Syria arrests ex-officer suspected in 2014 bloodshed"),
    (31, "600 women killed in South Africa in three months"),
    (32, "Caravan of some 300 migrants crosses into Mexico"),
    (33, "Japan passes 100,000 centenarians"),
    (34, "Hello Kitty firm cuts ties with spy show after China row"),
    (35, "Xi: US must do 'right' on Taiwan; AI needs human oversight"),
    (36, "Middle powers chart own course as Trump courts Xi, Putin"),
    (37, "Macron asks to resume Ukraine's EU application"),
    (38, "Montenegro rejects land concessions to Croatia"),
    (39, "Kerch Bridge may need 24 months to reopen"),
    (40, "Gold -4% to $3,539; silver -7.4% to $41.08"),
    (41, "Oil +1.4% to $83.62 as Red Sea attacks widen"),
    (42, "Ether -7.6% to $1,622; Solana to $68.88 in rout"),
    (43, "India resume on 159/1, day three of Wellington Test"),
    (44, "Medvedev meets Zverev in tonight's ATP semi"),
    (45, "Las Vegas GP qualifying today; the race is Sunday"),
    (46, "Australia host England in first T20, Melbourne"),
    (47, "Grand Slam of Darts quarter-finals today, Wolverhampton"),
    (48, "EU and UK sign farm and youth-mobility deals"),
    (49, "EU-UK summit: Burnham seeks to mend Brexit effects"),
    (50, "Ukraine to send food aid to nine countries"),
]

PINS = [  # (number, lon, lat)
    ("1", 30.5, 50.4), ("2", 30.7, 36.9), ("4", 46.7, 24.7),
    ("6", 116.4, 39.9), ("7", 174.8, -41.3), ("8", 124.4, 40.1),
    ("9", 4.35, 50.85), ("10", 12.6, 55.7), ("11", -3.7, 40.4),
    ("12", 43.0, 14.8), ("13", -74.0, 40.7),
]

DATE_CHECK = (
    "DATE CHECK — First reported before Saturday, so they are NOT on this "
    "page as Saturday's news: the Shenzhen trilateral summit and its peace "
    "declaration · Trump's White House presser (Miller, Putin, the "
    "data-centre tax) · Wall Street's Friday rout (S&P 500 -3.7%) · Cyclone "
    "Akvan's landfall in Odisha · the ICJ's genocide ruling on Myanmar · "
    "Indonesia's vice-president resigning (Thu) · the India-Japan "
    "firing-range deal (Thu) · GTA VI's release. Their Saturday fallout is "
    "covered above."
)

FOOTER = (
    "Every story here happened, or was first reported, on Saturday 21 "
    "November 2026, in some time zone. CLAIM = one side's account, not "
    "independently confirmed. Sources: Reuters, AP, AFP, BBC, Al Jazeera, "
    "UN News, Yonhap, ESA. Original drawings."
)


# Coarse world land map as (row -> [(col_start, col_end), ...]) spans on a
# 36 row x 72 col grid; each cell is 5deg x 5deg. Row 0 is 90N..85N,
# col 0 is 180W..175W. Used to draw a dotted landmass map.
LAND_SPANS = {
    1: [(19, 22), (25, 30), (38, 40), (45, 48), (54, 57)],
    2: [(17, 24), (26, 29), (44, 70)],
    3: [(2, 8), (12, 24), (26, 28), (40, 42), (44, 71)],
    4: [(1, 10), (13, 27), (32, 33), (39, 43), (44, 71)],
    5: [(2, 11), (14, 29), (32, 33), (35, 35), (38, 43), (44, 71)],
    6: [(4, 9), (14, 30), (35, 36), (38, 40), (42, 71)],
    7: [(13, 29), (35, 70)],
    8: [(8, 26), (36, 64), (65, 66)],
    9: [(7, 26), (34, 36), (38, 64), (65, 66)],
    10: [(7, 25), (33, 41), (42, 66)],
    11: [(8, 22), (32, 52), (53, 57), (59, 63)],
    12: [(11, 17), (21, 21), (31, 48), (53, 57), (58, 62), (64, 64)],
    13: [(12, 17), (31, 48), (54, 57), (58, 61), (64, 65)],
    14: [(14, 17), (31, 48), (55, 56), (59, 61), (64, 65)],
    15: [(20, 24), (32, 37), (46, 49), (56, 56), (58, 62), (65, 65)],
    16: [(20, 26), (35, 41), (46, 49), (57, 59), (60, 63), (64, 64)],
    17: [(20, 28), (37, 47), (60, 65), (66, 68)],
    18: [(21, 29), (38, 47), (59, 62), (66, 69)],
    19: [(21, 29), (38, 45), (48, 49), (61, 65), (66, 69)],
    20: [(22, 29), (38, 46), (48, 49), (59, 66)],
    21: [(22, 28), (38, 46), (48, 49), (59, 66)],
    22: [(23, 28), (39, 44), (59, 66)],
    23: [(23, 27), (39, 43), (60, 65)],
    24: [(23, 26), (61, 65), (70, 71)],
    25: [(23, 26), (70, 71)],
    26: [(23, 25), (69, 70)],
    27: [(23, 25), (69, 69)],
    28: [(23, 24)],
}


def land_cells():
    cells = set()
    for r, spans in LAND_SPANS.items():
        for c0, c1 in spans:
            for c in range(c0, c1 + 1):
                cells.add((r, c))
    return cells


# ------------------------------------------------------------- illustrations

def ill_bridge(d, x, y, w, h):
    """Hero 1: river, one bridge deck, skyline, red strike streaks."""
    d.rectangle([x, y, x + w, y + h], fill=PALE)
    # skyline blocks
    for bx, bh in [(0.04, 0.42), (0.13, 0.58), (0.22, 0.36), (0.70, 0.5),
                   (0.80, 0.64), (0.90, 0.4)]:
        d.rectangle([x + w * bx, y + h * (0.66 - bh * 0.55),
                     x + w * (bx + 0.07), y + h * 0.66], fill=INK)
    # red streaks coming down
    for sx in (0.34, 0.50, 0.62):
        d.line([x + w * (sx + 0.08), y + h * 0.05, x + w * sx, y + h * 0.36],
               fill=RED, width=7)
        d.ellipse([x + w * sx - 9, y + h * 0.36 - 9, x + w * sx + 9,
                   y + h * 0.36 + 9], fill=RED)
    # river
    d.rectangle([x, y + h * 0.82, x + w, y + h], fill=(198, 186, 152))
    # one bridge deck with towers and cables
    yy = y + h * 0.72
    d.line([x, yy, x + w, yy], fill=INK, width=7)
    for tx in (0.28, 0.68):
        d.line([x + w * tx, yy - h * 0.22, x + w * tx, yy], fill=INK, width=6)
        d.line([x + w * tx, yy - h * 0.22, x + w * (tx - 0.22), yy], fill=INK, width=3)
        d.line([x + w * tx, yy - h * 0.22, x + w * (tx + 0.22), yy], fill=INK, width=3)


def ill_globe(d, x, y, w, h):
    """Hero 2: globe with meridians, a red FAILURE banner, a table line."""
    d.rectangle([x, y, x + w, y + h], fill=PALE)
    # banner across the top
    bw, bh = w * 0.34, 30
    bx0 = x + (w - bw) / 2
    d.rectangle([bx0, y + 6, bx0 + bw, y + 6 + bh], fill=RED)
    f = F(SANS_B, 22)
    tw = d.textlength("FAILURE", font=f)
    d.text((x + w / 2 - tw / 2, y + 9), "FAILURE", font=f, fill=WHITE)
    # globe
    cx, cy, r = x + w * 0.5, y + h * 0.66, h * 0.26
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=5)
    for fx in (0.45, 0.75):
        d.ellipse([cx - r * fx, cy - r, cx + r * fx, cy + r], outline=INK, width=3)
    d.line([cx - r, cy, cx + r, cy], fill=INK, width=3)
    d.line([cx, cy - r, cx, cy + r], fill=INK, width=3)
    # conference table line
    d.line([x + w * 0.08, y + h * 0.95, x + w * 0.92, y + h * 0.95], fill=INK, width=5)


def ill_chart(d, x, y, w, h):
    """Hero 3: falling market chart with a $59k break line."""
    d.rectangle([x, y, x + w, y + h], fill=PALE)
    gx0, gy0, gx1, gy1 = x + w * 0.08, y + h * 0.10, x + w * 0.94, y + h * 0.86
    for i in range(1, 4):
        yy = gy0 + (gy1 - gy0) * i / 4
        d.line([gx0, yy, gx1, yy], fill=(205, 194, 163), width=2)
    d.line([gx0, gy0, gx0, gy1], fill=INK, width=4)
    d.line([gx0, gy1, gx1, gy1], fill=INK, width=4)
    pts = [(0.0, 0.12), (0.14, 0.20), (0.26, 0.16), (0.38, 0.30), (0.50, 0.27),
           (0.60, 0.44), (0.72, 0.40), (0.82, 0.62), (0.90, 0.58), (1.0, 0.80)]
    xy = [(gx0 + (gx1 - gx0) * px, gy0 + (gy1 - gy0) * py) for px, py in pts]
    d.line(xy, fill=RED, width=8)
    for px, py in xy[::3]:
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED)
    # dashed threshold line at the break
    yy = gy0 + (gy1 - gy0) * 0.52
    for xx in range(int(gx0), int(gx1), 26):
        d.line([xx, yy, xx + 14, yy], fill=INK, width=3)
    f = F(SANS_B, 23)
    d.text((gx0 + 8, gy1 - 32), "$60,000", font=f, fill=INK)


ILLUSTRATIONS = [ill_bridge, ill_globe, ill_chart]


# ------------------------------------------------------------------- layout

S = 2048
M = 52
W = S - 2 * M

BRIEF_SIZE = 20          # fixed brief font size (render px) -- never auto-fit
BRIEF_LH = 20


def section_rule(d, y, thick=3):
    d.line([M, y, M + W, y], fill=INK, width=thick)
    return y + thick


def draw_kicker(d, y):
    f = F(SANS_B, 25)
    draw_tracked(d, M, y, "ONE DAY OF WORLD NEWS, ONE PICTURE", f, INK, 3)
    draw_tracked_right(d, M + W, y, "50 STORIES · 7 REGIONS · EVERY ONE FROM THIS SATURDAY",
                        f, RED, 3)
    return y + 32


def draw_title(d, y):
    f = F(SERIF_B, 96)
    t = "Saturday 21 November 2026"
    tw = d.textlength(t, font=f)
    d.text((M + (W - tw) / 2, y), t, font=f, fill=INK)
    return y + 106


def draw_stats(d, y):
    colw = W / 6
    fnum = F(SERIF_B, 46)
    fcap = F(SANS, 20)
    heights = []
    for i, (num, cap) in enumerate(STATS):
        lines = wrap(d, cap, fcap, colw - 18)
        heights.append(len(lines))
    body = max(heights) * 23
    for i, (num, cap) in enumerate(STATS):
        x = M + i * colw
        if i:
            d.line([x, y + 4, x, y + 52 + body], fill=INK, width=2)
        d.text((x + 9, y), num, font=fnum, fill=INK)
        lines = wrap(d, cap, fcap, colw - 18)
        draw_lines(d, x + 9, y + 50, lines, fcap, 23)
    return y + 50 + body + 6


def draw_timeline(d, y):
    fh = F(SANS_B, 24)
    d.text((M, y), "THE DAY IN UTC", font=fh, fill=RED)
    y += 30
    colw = W / 5
    doty = y + 8
    d.line([M + colw / 2, doty, M + W - colw / 2, doty], fill=INK, width=3)
    for i in range(5):
        cx = M + colw * i + colw / 2
        d.ellipse([cx - 9, doty - 9, cx + 9, doty + 9], fill=RED)
    y += 22
    ft = F(SANS_B, 25)
    fx = F(SANS, 20)
    maxlines = 0
    cols = []
    for when, what in TIMELINE:
        lines = wrap(d, what, fx, colw - 20)
        cols.append(lines)
        maxlines = max(maxlines, len(lines))
    for i, ((when, what), lines) in enumerate(zip(TIMELINE, cols)):
        x = M + i * colw + 10
        d.text((x, y), when, font=ft, fill=INK)
        draw_lines(d, x, y + 30, lines, fx, 23)
    return y + 30 + maxlines * 23 + 2


def hero_height(d, cardw):
    inner = cardw - 36
    fh = F(SERIF_B, 32)
    fd = F(SANS, 21)
    worst = 0
    for _n, _k, head, dek in HEROES:
        hl = len(wrap(d, head, fh, inner))
        dl = len(wrap(d, dek, fd, inner))
        worst = max(worst, 98 + 38 + hl * 35 + dl * 22 + 12)
    return worst


def draw_heroes(d, y):
    gap = 20
    cardw = (W - 2 * gap) // 3
    h = hero_height(d, cardw)
    fh = F(SERIF_B, 32)
    fd = F(SANS, 21)
    fk = F(SANS_B, 20)
    fn = F(SANS_B, 24)
    for i, (num, kick, head, dek) in enumerate(HEROES):
        x = M + i * (cardw + gap)
        d.rectangle([x, y, x + cardw, y + h], outline=INK, width=3)
        ILLUSTRATIONS[i](d, x + 3, y + 3, cardw - 6, 92)
        cy = y + 98
        d.ellipse([x + 18, cy, x + 58, cy + 40], fill=RED)
        nw = d.textlength(num, font=fn)
        d.text((x + 38 - nw / 2, cy + 6), num, font=fn, fill=WHITE)
        d.text((x + 70, cy + 8), kick, font=fk, fill=RED)
        cy += 38
        cy = draw_lines(d, x + 18, cy, wrap(d, head, fh, cardw - 36), fh, 35)
        draw_lines(d, x + 18, cy + 2, wrap(d, dek, fd, cardw - 36), fd, 22)
    return y + h


def card_height(d, cards, cardw):
    inner = cardw - 28
    fh = F(SERIF_B, 25)
    fd = F(SANS, 20)
    worst = 0
    for _n, _k, _t, head, dek in cards:
        hl = len(wrap(d, head, fh, inner))
        dl = len(wrap(d, dek, fd, inner))
        worst = max(worst, 44 + hl * 28 + dl * 21)
    return worst


def draw_card_row(d, y, cards):
    gap = 14
    cardw = (W - 4 * gap) // 5
    h = card_height(d, cards, cardw)
    fh = F(SERIF_B, 25)
    fd = F(SANS, 20)
    fk = F(SANS_B, 16)
    fn = F(SANS_B, 25)
    ft = F(SANS_B, 14)
    for i, (num, kick, tagged, head, dek) in enumerate(cards):
        x = M + i * (cardw + gap)
        d.rectangle([x, y, x + cardw, y + h], outline=INK, width=2)
        d.text((x + 14, y + 10), num, font=fn, fill=RED)
        kw = cardw - 28 - d.textlength(num, font=fn) - 12
        if tagged:
            tw = d.textlength("REPORTED", font=ft) + 12
            d.rectangle([x + cardw - tw - 10, y + 10, x + cardw - 10, y + 31], fill=RED)
            d.text((x + cardw - tw - 4, y + 13), "REPORTED", font=ft, fill=WHITE)
            kw -= tw + 6
        kx = x + 14 + d.textlength(num, font=fn) + 8
        kline = kick
        while d.textlength(kline, font=fk) > kw and len(kline) > 4:
            kline = kline[:-2]
        d.text((kx, y + 15), kline, font=fk, fill=RED)
        cy = draw_lines(d, x + 14, y + 32, wrap(d, head, fh, cardw - 28), fh, 28)
        draw_lines(d, x + 14, cy + 1, wrap(d, dek, fd, cardw - 28), fd, 21)
    return y + h


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=INK, width=2)
    cw, ch = w / 72, h / 36
    land = (186, 173, 138)
    for (r, c) in land_cells():
        cx, cy = x + (c + 0.5) * cw, y + (r + 0.5) * ch
        d.ellipse([cx - 3.4, cy - 3.4, cx + 3.4, cy + 3.4], fill=land)
    fn = F(SANS_B, 17)
    # Every pin gets a small dot at its EXACT lon/lat position. Badges sit
    # on their dot unless they would collide or clip the panel; those are
    # offset and tied to their dot with a thin leader line:
    #   6 Beijing / 8 Dandong share one spot in NE China -- split apart.
    #   9 Brussels hides behind 10 Copenhagen -- 9 down-left, 10 above.
    #   7 Wellington's dot is at the panel's right edge -- badge pulled in.
    OFFSETS = {
        "6": (-26, -24),
        "8": (28, 26),
        "9": (-40, 30),
        "10": (6, -30),
        "7": (-30, 0),
    }
    pts = {}
    for num, lon, lat in PINS:
        px = x + (lon + 180) / 360 * w
        py = y + (90 - lat) / 180 * h
        pts[num] = (px, py)
    for num, (dx, dy) in OFFSETS.items():
        px, py = pts[num]
        d.line([px, py, px + dx, py + dy], fill=RED, width=2)
    for num, (px, py) in pts.items():
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=RED)
    for num, (px, py) in pts.items():
        dx, dy = OFFSETS.get(num, (0, 0))
        bx, by = px + dx, py + dy
        r = 15 if len(num) == 1 else 17
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=RED, outline=WHITE, width=2)
        tw = d.textlength(num, font=fn)
        d.text((bx - tw / 2, by - 11), num, font=fn, fill=WHITE)


def draw_bottom(d, y):
    fh = F(SANS_B, 24)
    d.text((M, y), "WHERE IT HAPPENED", font=fh, fill=RED)
    bx = M + 520 + 24
    d.text((bx, y), "ALSO ON SATURDAY", font=fh, fill=RED)
    y += 30
    mapw, maph = 520, 260
    draw_map(d, M, y, mapw, maph)
    fcap = F(SANS, 20)
    cap = ("Pins 1-13 mark the drawn stories. No. 3 is in the markets; "
           "No. 5 is in space: Mercury.")
    cy = draw_lines(d, M, y + maph + 10, wrap(d, cap, fcap, mapw), fcap, 25)
    # briefs in 3 sequential columns, split points chosen to balance height
    fb = F(SANS, BRIEF_SIZE)
    fn = F(SANS_B, BRIEF_SIZE)
    bw = W - 520 - 24
    colw = (bw - 2 * 18) // 3
    items = []
    for num, text in BRIEFS:
        lines = wrap(d, text, fb, colw - fn.getlength(f"{num} "))
        items.append((num, lines, len(lines) * BRIEF_LH + 2))
    best = None
    for i in range(1, len(items) - 1):
        for j in range(i + 1, len(items)):
            hs = [sum(it[2] for it in items[:i]),
                  sum(it[2] for it in items[i:j]),
                  sum(it[2] for it in items[j:])]
            if best is None or max(hs) < best[0]:
                best = (max(hs), i, j)
    _, si, sj = best
    cols = [items[:si], items[si:sj], items[sj:]]
    heights = [sum(it[2] for it in col) for col in cols]
    top = y
    for j, col in enumerate(cols):
        cx = bx + j * (colw + 18)
        cy2 = top
        for num, lines, _h in col:
            label = f"{num} "
            d.text((cx, cy2), label, font=fn, fill=RED)
            off = fn.getlength(label)
            for k, ln in enumerate(lines):
                d.text((cx + (off if k == 0 else 0), cy2), ln, font=fb, fill=INK)
                cy2 += BRIEF_LH
            cy2 += 2
    return max(cy, top + max(heights))


def draw_date_check(d, y):
    f = F(SANS, 21)
    lines = wrap(d, DATE_CHECK, f, W - 36)
    h = len(lines) * 24 + 14
    d.rectangle([M, y, M + W, y + h], outline=RED, width=3)
    draw_lines(d, M + 18, y + 8, lines, f, 24)
    return y + h


def draw_footer(d, y):
    fr = F(SANS_B, 22)
    t = "SATURDAY 21 NOVEMBER 2026 · ONE DAY, ONE PICTURE"
    tw = d.textlength(t, font=fr)
    f = F(SANS, 20)
    lines = wrap(d, FOOTER, f, W - tw - 40)
    draw_lines(d, M, y, lines, f, 25)
    d.text((M + W - tw, y + 2), t, font=fr, fill=RED)
    return y + len(lines) * 25


def build():
    img = Image.new("RGB", (S, S), PAPER)
    d = ImageDraw.Draw(img)
    y = 30
    y = draw_kicker(d, y) + 4
    y = section_rule(d, y, 6) + 3
    y = section_rule(d, y, 2) + 10
    y = draw_title(d, y) + 2
    y = section_rule(d, y, 3) + 12
    y = draw_stats(d, y) + 6
    y = section_rule(d, y, 2) + 10
    y = draw_timeline(d, y) + 6
    y = section_rule(d, y, 3) + 12
    y = draw_heroes(d, y) + 8
    y = draw_card_row(d, y, CARDS[:5]) + 8
    y = draw_card_row(d, y, CARDS[5:]) + 8
    y = draw_bottom(d, y) + 6
    y = draw_date_check(d, y) + 8
    y = draw_footer(d, y)
    print("final y:", y, "of", S)
    img = img.resize((1024, 1024), Image.LANCZOS)
    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    build()
