#!/usr/bin/env python3
"""Fix all P1/P2/P3 audit issues for threadspec.org"""

import os
import re
import math

BASE = "/Users/juhaporraskorpi/clawd/threadspec"

# ============================================================
# STANDARD METRIC DRILL SIZES (mm)
# Uses d-P convention: tap drill = smallest standard ≥ (d-P)
# ============================================================
METRIC_DRILLS = sorted([
    # 0.1mm steps 0.1-10.0
    *[round(x * 0.1, 1) for x in range(1, 101)],
    # Add 9.25 (used for M10×0.75)
    9.25,
    # ISO preferred above 10mm (0.2+0.3 pattern then 0.5 steps)
    10.2, 10.5, 10.8,
    11.2, 11.5, 11.8,
    12.2, 12.5, 12.8,
    # 0.5mm steps 13-50
    *[round(x * 0.5, 1) for x in range(26, 101)],  # 13.0 to 50.0
    # 1mm steps 51-100
    *list(range(51, 101)),
])
# Deduplicate and sort
METRIC_DRILLS = sorted(set(METRIC_DRILLS))

def metric_tap_drill(d_mm, p_mm):
    """Return (drill_mm, drill_str) = smallest standard metric drill >= d-P."""
    target = d_mm - p_mm
    for drill in METRIC_DRILLS:
        if drill >= target - 0.0001:
            return drill
    return d_mm - p_mm  # fallback

def fmt_mm(v):
    """Format mm value: strip trailing zeros but keep at least one decimal."""
    s = f"{v:.4f}".rstrip('0')
    if s.endswith('.'):
        s += '0'
    # Simplify: show up to 2 decimal places unless needed
    s2 = f"{v:.2f}".rstrip('0')
    if s2.endswith('.'):
        s2 += '0'
    return s2

# ============================================================
# INCH DRILL TABLE — (name, decimal_inches)
# ============================================================
def frac(n, d):
    return n / d

NUMBER_DRILLS = [
    ("#80", 0.0135), ("#79", 0.0145), ("#78", 0.016), ("#77", 0.018), ("#76", 0.020),
    ("#75", 0.021), ("#74", 0.0225), ("#73", 0.024), ("#72", 0.025), ("#71", 0.026),
    ("#70", 0.028), ("#69", 0.0292), ("#68", 0.031), ("#67", 0.032), ("#66", 0.033),
    ("#65", 0.035), ("#64", 0.036), ("#63", 0.037), ("#62", 0.038), ("#61", 0.039),
    ("#60", 0.040), ("#59", 0.041), ("#58", 0.042), ("#57", 0.043), ("#56", 0.0465),
    ("#55", 0.052), ("#54", 0.055), ("#53", 0.0595), ("#52", 0.0635), ("#51", 0.067),
    ("#50", 0.070), ("#49", 0.073), ("#48", 0.076), ("#47", 0.0785), ("#46", 0.081),
    ("#45", 0.082), ("#44", 0.086), ("#43", 0.089), ("#42", 0.0935), ("#41", 0.096),
    ("#40", 0.098), ("#39", 0.0995), ("#38", 0.1015), ("#37", 0.104), ("#36", 0.1065),
    ("#35", 0.110), ("#34", 0.111), ("#33", 0.113), ("#32", 0.116), ("#31", 0.120),
    ("#30", 0.1285), ("#29", 0.136), ("#28", 0.1405), ("#27", 0.144), ("#26", 0.147),
    ("#25", 0.1495), ("#24", 0.152), ("#23", 0.154), ("#22", 0.157), ("#21", 0.159),
    ("#20", 0.161), ("#19", 0.166), ("#18", 0.1695), ("#17", 0.173), ("#16", 0.177),
    ("#15", 0.180), ("#14", 0.182), ("#13", 0.185), ("#12", 0.189), ("#11", 0.191),
    ("#10", 0.1935), ("#9", 0.196), ("#8", 0.199), ("#7", 0.201), ("#6", 0.204),
    ("#5", 0.2055), ("#4", 0.209), ("#3", 0.213), ("#2", 0.221), ("#1", 0.228),
]

LETTER_DRILLS = [
    ("A", 0.234), ("B", 0.238), ("C", 0.242), ("D", 0.246), ("E", 0.250),
    ("F", 0.257), ("G", 0.261), ("H", 0.266), ("I", 0.272), ("J", 0.277),
    ("K", 0.281), ("L", 0.290), ("M", 0.295), ("N", 0.302), ("O", 0.316),
    ("P", 0.323), ("Q", 0.332), ("R", 0.339), ("S", 0.348), ("T", 0.358),
    ("U", 0.368), ("V", 0.377), ("W", 0.386), ("X", 0.397), ("Y", 0.404),
    ("Z", 0.413),
]

def gen_fractional_drills():
    out = []
    for num in range(1, 100):
        for den in [64, 32, 16, 8, 4, 2]:
            if num < den and math.gcd(num, den) == 1:
                val = num / den
                # Label
                if den == 1:
                    label = f"{num}\""
                else:
                    label = f"{num}/{den}\""
                out.append((label, val))
    # Also add whole inches and mixed fractions
    for w in range(1, 10):
        for num in range(0, 64):
            for den in [64, 32, 16, 8, 4, 2, 1]:
                if num == 0:
                    if den == 1:
                        out.append((f"{w}\"", float(w)))
                    break
                if num < den and math.gcd(num, den) == 1:
                    val = w + num / den
                    if den == 1:
                        label = f"{w}-{num}\""
                    else:
                        label = f"{w}-{num}/{den}\""
                    out.append((label, val))
    return sorted(out, key=lambda x: x[1])

FRACTIONAL_DRILLS = gen_fractional_drills()

# Combined sorted inch drill table
ALL_INCH_DRILLS = sorted(NUMBER_DRILLS + LETTER_DRILLS + FRACTIONAL_DRILLS, key=lambda x: x[1])
# Remove duplicates (keep first occurrence at each size)
seen = set()
INCH_DRILLS_DEDUP = []
for name, val in ALL_INCH_DRILLS:
    key = round(val, 6)
    if key not in seen:
        seen.add(key)
        INCH_DRILLS_DEDUP.append((name, val))

def closest_inch_drill(target_in):
    """Find the closest inch drill to target (for display only)."""
    best = min(INCH_DRILLS_DEDUP, key=lambda x: abs(x[1] - target_in))
    return best

def smallest_inch_drill_ge(target_in):
    """Smallest standard inch drill >= target."""
    for name, val in INCH_DRILLS_DEDUP:
        if val >= target_in - 0.00005:
            return name, val
    return None, None

# ============================================================
# PUBLISHED ASME B1.1 TAP DRILLS FOR UNC / UNF
# key = (d_nominal_frac_str, tpi) -> (drill_name, drill_in)
# ============================================================
# For UNC sizes
UNC_TAP_DRILLS = {
    # (nominal_in, tpi): (drill_name, drill_decimal_in)
    # Number sizes (expressed as decimal)
    (0.073, 64): ("#53", 0.0595),    # #1
    (0.086, 56): ("#50", 0.0700),    # #2
    (0.099, 48): ("#47", 0.0785),    # #3
    (0.112, 40): ("#43", 0.0890),    # #4
    (0.125, 40): ("#38", 0.1015),    # #5
    (0.138, 32): ("#36", 0.1065),    # #6
    (0.164, 32): ("#29", 0.1360),    # #8
    (0.190, 24): ("#25", 0.1495),    # #10
    (0.216, 24): ("#16", 0.1770),    # #12
    # Fractional
    (0.250, 20): ("#7", 0.2010),
    (0.3125, 18): ("F", 0.2570),
    (0.375, 16): ("5/16\"", 0.3125),
    (0.4375, 14): ("U", 0.3680),
    (0.500, 13): ("27/64\"", frac(27, 64)),
    (0.5625, 12): ("31/64\"", frac(31, 64)),
    (0.625, 11): ("17/32\"", frac(17, 32)),
    (0.750, 10): ("21/32\"", frac(21, 32)),
    (0.875, 9): ("49/64\"", frac(49, 64)),
    (1.000, 8): ("7/8\"", 0.875),
    (1.125, 7): ("63/64\"", frac(63, 64)),
    (1.250, 7): ("1-7/64\"", 1 + frac(7, 64)),
    (1.375, 6): ("1-7/32\"", 1 + frac(7, 32)),
    (1.500, 6): ("1-11/32\"", 1 + frac(11, 32)),
    (1.750, 5): ("1-9/16\"", 1 + frac(9, 16)),
    (2.000, 4.5): ("1-25/32\"", 1 + frac(25, 32)),
    (2.250, 4.5): ("2-1/32\"", 2 + frac(1, 32)),
    (2.500, 4): ("2-1/4\"", 2.25),
    (2.750, 4): ("2-1/2\"", 2.50),
    (3.000, 4): ("2-3/4\"", 2.75),
    (3.250, 4): ("3\"", 3.00),
    (3.500, 4): ("3-1/4\"", 3.25),
    (3.750, 4): ("3-1/2\"", 3.50),
    (4.000, 4): ("3-3/4\"", 3.75),
}

# For UNF sizes
UNF_TAP_DRILLS = {
    (0.060, 80): ("3/64\"", frac(3, 64)),    # #0
    (0.073, 72): ("#53", 0.0595),             # #1
    (0.086, 64): ("#50", 0.0700),             # #2
    (0.099, 56): ("#45", 0.0820),             # #3
    (0.112, 48): ("#42", 0.0935),             # #4
    (0.125, 44): ("#37", 0.1040),             # #5
    (0.138, 40): ("#33", 0.1130),             # #6
    (0.164, 36): ("#29", 0.1360),             # #8
    (0.190, 32): ("#21", 0.1590),             # #10
    (0.216, 28): ("#14", 0.1820),             # #12
    (0.250, 28): ("#3", 0.2130),
    (0.3125, 24): ("I", 0.2720),
    (0.375, 24): ("Q", 0.3320),
    (0.4375, 20): ("25/64\"", frac(25, 64)),
    (0.500, 20): ("29/64\"", frac(29, 64)),
    (0.5625, 18): ("33/64\"", frac(33, 64)),
    (0.625, 18): ("37/64\"", frac(37, 64)),
    (0.750, 16): ("11/16\"", frac(11, 16)),
    (0.875, 14): ("13/16\"", frac(13, 16)),
    (1.000, 12): ("59/64\"", frac(59, 64)),
    (1.125, 12): ("1-3/64\"", 1 + frac(3, 64)),
    (1.250, 12): ("1-11/64\"", 1 + frac(11, 64)),
    (1.375, 12): ("1-19/64\"", 1 + frac(19, 64)),
    (1.500, 12): ("1-27/64\"", 1 + frac(27, 64)),
}

# UNEF: use D1-based approach
# Key UNEF sizes (d_in, tpi)
UNEF_SIZES = [
    (0.216, 32), (0.375, 32), (0.4375, 28), (0.500, 28), (0.5625, 24),
    (0.625, 24), (0.750, 20), (0.875, 20), (1.000, 20), (1.0625, 18),
    (1.125, 18), (1.1875, 18), (1.250, 18), (1.3125, 18), (1.375, 18),
    (1.4375, 18), (1.500, 18), (1.5625, 18), (1.6875, 18),
]

def inch_tap_drill(d_in, tpi, series):
    """
    Return (name, decimal_in) for the published tap drill.
    series = 'unc', 'unf', or 'unef'
    """
    d_key = round(d_in, 4)
    if series == 'unc':
        key = (d_key, tpi)
        if key in UNC_TAP_DRILLS:
            return UNC_TAP_DRILLS[key]
    elif series == 'unf':
        key = (d_key, tpi)
        if key in UNF_TAP_DRILLS:
            return UNF_TAP_DRILLS[key]
    # UNEF or fallback: smallest standard inch drill >= D1
    P_in = 1.0 / tpi
    D1_in = d_in - 1.0825 * P_in
    return smallest_inch_drill_ge(D1_in)

# ============================================================
# BSP CORRECT DATA per ISO 228-1
# ============================================================
# (nominal, tpi, od_in, od_mm)  — only correcting 3 wrong ODs
BSP_CORRECT_OD = {
    "g7-8-bsp": (1.189, 30.201),   # 7/8" BSP, 14 TPI
    "g2-1-2-bsp": (2.960, 75.184), # 2-1/2" BSP, 11 TPI
    "g4-bsp": (4.450, 113.030),    # 4" BSP, 11 TPI
}

# Full BSP table for index page correction
# (slug, nominal_str, tpi, od_in, pitch_in, minor_in, od_mm, pitch_mm, minor_mm, tap_drill_mm)
# Per ISO 228-1; tap drill = smallest standard ≥ D1
BSP_TABLE = [
    ("g1-8-bsp",   "1/8\"",    28, 0.38340, 1/28, 0.33546, 9.74,  0.9071, 8.52,  8.8),
    ("g1-4-bsp",   "1/4\"",    19, 0.51832, 1/19, 0.45098, 13.16, 1.3368, 11.45, 11.8),
    ("g3-8-bsp",   "3/8\"",    19, 0.65600, 1/19, 0.58866, 16.66, 1.3368, 14.95, 15.0),
    ("g1-2-bsp",   "1/2\"",    14, 0.82500, 1/14, 0.73360, 20.96, 1.8143, 18.63, 19.0),
    ("g5-8-bsp",   "5/8\"",    14, 0.90200, 1/14, 0.81060, 22.91, 1.8143, 20.59, 21.0),
    ("g3-4-bsp",   "3/4\"",    14, 1.04100, 1/14, 0.94960, 26.44, 1.8143, 24.12, 24.5),
    ("g7-8-bsp",   "7/8\"",    14, 1.18898, 1/14, 1.09758, 30.20, 1.8143, 27.88, 28.0),
    ("g1-bsp",     "1\"",      11, 1.30920, 1/11, 1.19330, 33.25, 2.3091, 30.31, 30.5),
    ("g1-1-8-bsp", "1-1/8\"",  11, 1.49210, 1/11, 1.37620, 37.90, 2.3091, 34.96, 35.0),
    ("g1-1-4-bsp", "1-1/4\"",  11, 1.65000, 1/11, 1.53410, 41.91, 2.3091, 38.97, 39.0),
    ("g1-1-2-bsp", "1-1/2\"",  11, 1.88200, 1/11, 1.76610, 47.80, 2.3091, 44.86, 45.0),
    ("g1-3-4-bsp", "1-3/4\"",  11, 2.11600, 1/11, 2.00010, 53.75, 2.3091, 50.80, 51.0),
    ("g2-bsp",     "2\"",      11, 2.34700, 1/11, 2.23110, 59.61, 2.3091, 56.67, 57.0),
    ("g2-1-4-bsp", "2-1/4\"",  11, 2.58700, 1/11, 2.47110, 65.71, 2.3091, 62.77, 63.0),
    ("g2-1-2-bsp", "2-1/2\"",  11, 2.96000, 1/11, 2.84410, 75.18, 2.3091, 72.24, 72.5),
    ("g3-bsp",     "3\"",      11, 3.46020, 1/11, 3.34430, 87.89, 2.3091, 84.95, 85.0),
    ("g4-bsp",     "4\"",      11, 4.45000, 1/11, 4.33410, 113.03, 2.3091, 110.09, 110.5),
]

# BSP tap drills: use smallest standard metric drill >= D1 (inner minor diam, not exact minor)
# The inner minor for BSP Whitworth thread: D1 = OD - 1.2801/TPI (approx)
# Better: use published BSP tap drill table
BSP_TAP_DRILLS = {
    "g1-8-bsp":   ("8.8 mm",  8.8),
    "g1-4-bsp":   ("11.8 mm", 11.8),
    "g3-8-bsp":   ("15.0 mm", 15.0),
    "g1-2-bsp":   ("19.0 mm", 19.0),
    "g5-8-bsp":   ("21.0 mm", 21.0),
    "g3-4-bsp":   ("24.5 mm", 24.5),
    "g7-8-bsp":   ("28.0 mm", 28.0),
    "g1-bsp":     ("30.5 mm", 30.5),
    "g1-1-8-bsp": ("35.0 mm", 35.0),
    "g1-1-4-bsp": ("39.0 mm", 39.0),
    "g1-1-2-bsp": ("45.0 mm", 45.0),
    "g1-3-4-bsp": ("51.0 mm", 51.0),
    "g2-bsp":     ("57.0 mm", 57.0),
    "g2-1-4-bsp": ("63.0 mm", 63.0),
    "g2-1-2-bsp": ("72.5 mm", 72.5),
    "g3-bsp":     ("85.0 mm", 85.0),
    "g4-bsp":     ("110.5 mm", 110.5),
}

# ============================================================
# NPT CORRECT DATA per ASME B1.20.1
# ============================================================
# Tabulated E0 (hand-tight engagement pitch diameter), E1 (wrench makeup),
# Minor diameter at E0, published tap drill
# (slug, nominal_str, tpi, od_in, E0_in, K0_in, tap_drill_label, tap_drill_mm)
# Sources: ASME B1.20.1-2013 Table 1 and Table 2
NPT_DATA = [
    {
        "slug": "1-16-npt", "nominal": "1/16\"", "tpi": 27,
        "od": 0.31250, "e0": 0.27118, "e1": 0.28118, "k0": 0.25327,
        "tap_drill": ("15/64\"", frac(15,64)),
        "pitch": 1/27,
    },
    {
        "slug": "1-8-npt", "nominal": "1/8\"", "tpi": 27,
        "od": 0.40500, "e0": 0.36351, "e1": 0.37360, "k0": 0.34560,
        "tap_drill": ("R", 0.339),
        "pitch": 1/27,
    },
    {
        "slug": "1-4-npt", "nominal": "1/4\"", "tpi": 18,
        "od": 0.54000, "e0": 0.47739, "e1": 0.49163, "k0": 0.44929,
        "tap_drill": ("7/16\"", frac(7,16)),
        "pitch": 1/18,
    },
    {
        "slug": "3-8-npt", "nominal": "3/8\"", "tpi": 18,
        "od": 0.67500, "e0": 0.61201, "e1": 0.62701, "k0": 0.58391,
        "tap_drill": ("37/64\"", frac(37,64)),
        "pitch": 1/18,
    },
    {
        "slug": "1-2-npt", "nominal": "1/2\"", "tpi": 14,
        "od": 0.84000, "e0": 0.75843, "e1": 0.77843, "k0": 0.72235,
        "tap_drill": ("23/32\"", frac(23,32)),
        "pitch": 1/14,
    },
    {
        "slug": "3-4-npt", "nominal": "3/4\"", "tpi": 14,
        "od": 1.05000, "e0": 0.96768, "e1": 0.98887, "k0": 0.93160,
        "tap_drill": ("59/64\"", frac(59,64)),
        "pitch": 1/14,
    },
    {
        "slug": "1-npt", "nominal": "1\"", "tpi": 11.5,
        "od": 1.31500, "e0": 1.21363, "e1": 1.23863, "k0": 1.17062,
        "tap_drill": ("1-5/32\"", 1+frac(5,32)),
        "pitch": 1/11.5,
    },
    {
        "slug": "1-1-4-npt", "nominal": "1-1/4\"", "tpi": 11.5,
        "od": 1.66000, "e0": 1.55713, "e1": 1.58338, "k0": 1.51912,
        "tap_drill": ("1-1/2\"", 1.5),
        "pitch": 1/11.5,
    },
    {
        "slug": "1-1-2-npt", "nominal": "1-1/2\"", "tpi": 11.5,
        "od": 1.90000, "e0": 1.79609, "e1": 1.82234, "k0": 1.75808,
        "tap_drill": ("1-47/64\"", 1+frac(47,64)),
        "pitch": 1/11.5,
    },
    {
        "slug": "2-npt", "nominal": "2\"", "tpi": 11.5,
        "od": 2.37500, "e0": 2.27000, "e1": 2.29625, "k0": 2.23199,
        "tap_drill": ("2-7/32\"", 2+frac(7,32)),
        "pitch": 1/11.5,
    },
    {
        "slug": "2-1-2-npt", "nominal": "2-1/2\"", "tpi": 8,
        "od": 2.87500, "e0": 2.71953, "e1": 2.76953, "k0": 2.62300,
        "tap_drill": ("2-5/8\"", 2.625),
        "pitch": 1/8,
    },
    {
        "slug": "3-npt", "nominal": "3\"", "tpi": 8,
        "od": 3.50000, "e0": 3.34062, "e1": 3.39062, "k0": 3.24409,
        "tap_drill": ("3-1/4\"", 3.25),
        "pitch": 1/8,
    },
    {
        "slug": "3-1-2-npt", "nominal": "3-1/2\"", "tpi": 8,
        "od": 4.00000, "e0": 3.83750, "e1": 3.88750, "k0": 3.74097,
        "tap_drill": ("3-3/4\"", 3.75),
        "pitch": 1/8,
    },
    {
        "slug": "4-npt", "nominal": "4\"", "tpi": 8,
        "od": 4.50000, "e0": 4.33438, "e1": 4.38438, "k0": 4.23785,
        "tap_drill": ("4-1/4\"", 4.25),
        "pitch": 1/8,
    },
    {
        "slug": "5-npt", "nominal": "5\"", "tpi": 8,
        "od": 5.56300, "e0": 5.39073, "e1": 5.44073, "k0": 5.29420,
        "tap_drill": ("5-1/4\"", 5.25),
        "pitch": 1/8,
    },
    {
        "slug": "6-npt", "nominal": "6\"", "tpi": 8,
        "od": 6.62500, "e0": 6.44609, "e1": 6.49609, "k0": 6.34956,
        "tap_drill": ("6-5/16\"", 6+frac(5,16)),
        "pitch": 1/8,
    },
    {
        "slug": "8-npt", "nominal": "8\"", "tpi": 8,
        "od": 8.62500, "e0": 8.43359, "e1": 8.48359, "k0": 8.33706,
        "tap_drill": ("8-5/16\"", 8+frac(5,16)),
        "pitch": 1/8,
    },
    {
        "slug": "10-npt", "nominal": "10\"", "tpi": 8,
        "od": 10.75000, "e0": 10.54531, "e1": 10.59531, "k0": 10.44878,
        "tap_drill": ("10-7/16\"", 10+frac(7,16)),
        "pitch": 1/8,
    },
    {
        "slug": "12-npt", "nominal": "12\"", "tpi": 8,
        "od": 12.75000, "e0": 12.53281, "e1": 12.58281, "k0": 12.43628,
        "tap_drill": ("12-7/16\"", 12+frac(7,16)),
        "pitch": 1/8,
    },
]

# ============================================================
# METRIC THREAD DATA (coarse + fine)
# ============================================================
METRIC_COARSE = [
    ("m1",    1.0,   0.25), ("m1.2",  1.2,   0.25), ("m1.4",  1.4,   0.3),
    ("m1.6",  1.6,   0.35), ("m1.8",  1.8,   0.35), ("m2",    2.0,   0.4),
    ("m2.5",  2.5,   0.45), ("m3",    3.0,   0.5),  ("m3.5",  3.5,   0.6),
    ("m4",    4.0,   0.7),  ("m5",    5.0,   0.8),  ("m6",    6.0,   1.0),
    ("m7",    7.0,   1.0),  ("m8",    8.0,   1.25), ("m9",    9.0,   1.25),
    ("m10",  10.0,   1.5),  ("m12",  12.0,   1.75), ("m14",  14.0,   2.0),
    ("m16",  16.0,   2.0),  ("m18",  18.0,   2.5),  ("m20",  20.0,   2.5),
    ("m22",  22.0,   2.5),  ("m24",  24.0,   3.0),  ("m27",  27.0,   3.0),
    ("m30",  30.0,   3.5),  ("m33",  33.0,   3.5),  ("m36",  36.0,   4.0),
    ("m39",  39.0,   4.0),  ("m42",  42.0,   4.5),  ("m45",  45.0,   4.5),
    ("m48",  48.0,   5.0),  ("m52",  52.0,   5.0),  ("m56",  56.0,   5.5),
    ("m60",  60.0,   5.5),  ("m64",  64.0,   6.0),  ("m68",  68.0,   6.0),
]

METRIC_FINE = [
    ("m3x0-35",   3.0, 0.35),
    ("m10x0-75", 10.0, 0.75), ("m10x1-0", 10.0, 1.0), ("m10x1-25", 10.0, 1.25),
    ("m12x1-0",  12.0, 1.0),  ("m12x1-25", 12.0, 1.25), ("m12x1-5", 12.0, 1.5),
    ("m14x1-0",  14.0, 1.0),  ("m14x1-25", 14.0, 1.25), ("m14x1-5", 14.0, 1.5),
    ("m16x1-0",  16.0, 1.0),  ("m16x1-25", 16.0, 1.25), ("m16x1-5", 16.0, 1.5),
    ("m18x1-0",  18.0, 1.0),  ("m18x1-5",  18.0, 1.5),  ("m18x2-0", 18.0, 2.0),
    ("m20x1-0",  20.0, 1.0),  ("m20x1-5",  20.0, 1.5),  ("m20x2-0", 20.0, 2.0),
    ("m22x1-0",  22.0, 1.0),  ("m22x1-5",  22.0, 1.5),  ("m22x2-0", 22.0, 2.0),
    ("m24x1-0",  24.0, 1.0),  ("m24x1-5",  24.0, 1.5),  ("m24x2-0", 24.0, 2.0),
    ("m27x1-0",  27.0, 1.0),  ("m27x1-5",  27.0, 1.5),  ("m27x2-0", 27.0, 2.0),
    ("m30x1-0",  30.0, 1.0),  ("m30x1-5",  30.0, 1.5),  ("m30x2-0", 30.0, 2.0),
    ("m33x1-5",  33.0, 1.5),  ("m33x2-0",  33.0, 2.0),  ("m33x3-0", 33.0, 3.0),
    ("m36x1-5",  36.0, 1.5),  ("m36x2-0",  36.0, 2.0),  ("m36x3-0", 36.0, 3.0),
    ("m39x1-5",  39.0, 1.5),  ("m39x2-0",  39.0, 2.0),  ("m39x3-0", 39.0, 3.0),
    ("m42x1-5",  42.0, 1.5),  ("m42x2-0",  42.0, 2.0),  ("m42x3-0", 42.0, 3.0),
    ("m45x1-5",  45.0, 1.5),  ("m45x2-0",  45.0, 2.0),  ("m45x3-0", 45.0, 3.0),
    ("m48x1-5",  48.0, 1.5),  ("m48x2-0",  48.0, 2.0),  ("m48x3-0", 48.0, 3.0),
    ("m52x1-5",  52.0, 1.5),  ("m52x2-0",  52.0, 2.0),  ("m52x3-0", 52.0, 3.0),
    ("m56x1-5",  56.0, 1.5),  ("m56x2-0",  56.0, 2.0),  ("m56x3-0", 56.0, 3.0),
    ("m60x1-5",  60.0, 1.5),  ("m60x2-0",  60.0, 2.0),  ("m60x3-0", 60.0, 3.0),
    ("m64x2-0",  64.0, 2.0),  ("m64x3-0",  64.0, 3.0),  ("m68x2-0", 68.0, 2.0),
    ("m68x3-0",  68.0, 3.0),
]

# UNC thread data: (slug_dir, d_in, tpi)
UNC_THREADS = [
    ("num-1-unc",   0.073, 64),  ("num-2-unc",   0.086, 56),
    ("num-3-unc",   0.099, 48),  ("num-4-unc",   0.112, 40),
    ("num-5-unc",   0.125, 40),  ("num-6-unc",   0.138, 32),
    ("num-8-unc",   0.164, 32),  ("num-10-unc",  0.190, 24),
    ("num-12-unc",  0.216, 24),
    ("1-4-unc",     0.250, 20),  ("5-16-unc",    0.3125, 18),
    ("3-8-unc",     0.375, 16),  ("7-16-unc",    0.4375, 14),
    ("1-2-unc",     0.500, 13),  ("9-16-unc",    0.5625, 12),
    ("5-8-unc",     0.625, 11),  ("3-4-unc",     0.750, 10),
    ("7-8-unc",     0.875, 9),   ("1-unc",       1.000, 8),
    ("1-1-8-unc",   1.125, 7),   ("1-1-4-unc",   1.250, 7),
    ("1-3-8-unc",   1.375, 6),   ("1-1-2-unc",   1.500, 6),
    ("1-3-4-unc",   1.750, 5),   ("2-unc",       2.000, 4.5),
    ("2-1-4-unc",   2.250, 4.5), ("2-1-2-unc",   2.500, 4),
    ("2-3-4-unc",   2.750, 4),   ("3-unc",       3.000, 4),
    ("3-1-4-unc",   3.250, 4),   ("3-1-2-unc",   3.500, 4),
    ("3-3-4-unc",   3.750, 4),   ("4-unc",       4.000, 4),
]

UNF_THREADS = [
    ("num-0-unf",   0.060, 80),  ("num-1-unf",   0.073, 72),
    ("num-2-unf",   0.086, 64),  ("num-3-unf",   0.099, 56),
    ("num-4-unf",   0.112, 48),  ("num-5-unf",   0.125, 44),
    ("num-6-unf",   0.138, 40),  ("num-8-unf",   0.164, 36),
    ("num-10-unf",  0.190, 32),  ("num-12-unf",  0.216, 28),
    ("1-4-unf",     0.250, 28),  ("5-16-unf",    0.3125, 24),
    ("3-8-unf",     0.375, 24),  ("7-16-unf",    0.4375, 20),
    ("1-2-unf",     0.500, 20),  ("9-16-unf",    0.5625, 18),
    ("5-8-unf",     0.625, 18),  ("3-4-unf",     0.750, 16),
    ("7-8-unf",     0.875, 14),  ("1-unf",       1.000, 12),
    ("1-1-8-unf",   1.125, 12),  ("1-1-4-unf",   1.250, 12),
    ("1-3-8-unf",   1.375, 12),  ("1-1-2-unf",   1.500, 12),
]

UNEF_THREADS = [
    ("num-12-unef", 0.216, 32),
    ("3-8-unef",    0.375, 32),  ("7-16-unef",   0.4375, 28),
    ("1-2-unef",    0.500, 28),  ("9-16-unef",   0.5625, 24),
    ("5-16-unef",   0.3125, 32), ("5-8-unef",    0.625, 24),
    ("3-4-unef",    0.750, 20),  ("7-8-unef",    0.875, 20),
    ("1-unef",      1.000, 20),  ("1-1-16-unef", 1.0625, 18),
    ("1-1-8-unef",  1.125, 18),  ("1-3-16-unef", 1.1875, 18),
    ("1-1-4-unef",  1.250, 18),  ("1-5-16-unef", 1.3125, 18),
    ("1-3-8-unef",  1.375, 18),  ("1-7-16-unef", 1.4375, 18),
    ("1-1-2-unef",  1.500, 18),  ("1-9-16-unef", 1.5625, 18),
    ("1-11-16-unef", 1.6875, 18),
]


# ============================================================
# ISO 898-1 Property Class Stresses — CORRECTED
# 8.8: ≤M16 = 580/800 MPa, >M16 = 600/830 MPa
# 9.8: only ≤M16
# ============================================================
def get_metric_property_classes(d_mm):
    """Return list of (class, proof_mpa, tensile_mpa) for given diameter."""
    classes = [
        ("4.6", 225, 400),
        ("4.8", 310, 420),
        ("5.8", 380, 520),
    ]
    if d_mm <= 16:
        classes.append(("8.8", 580, 800))
        classes.append(("9.8", 650, 900))
    else:
        classes.append(("8.8", 600, 830))
        # 9.8 not applicable above M16 per ISO 898-1
    classes.extend([
        ("10.9", 830, 1040),
        ("12.9", 970, 1220),
    ])
    # Add scope note above M39
    return classes


# ============================================================
# SAE J429 Grade stresses — CORRECTED with size limits
# ============================================================
def get_sae_grades(d_in):
    """Return list of (grade, proof_psi, tensile_psi) for given diameter in inches."""
    grades = []
    # Grade 2: ≤3/4" → 55k/74k psi; >3/4" ≤ 1-1/2" → 33k/60k psi; >1.5" not shown
    if d_in <= 0.75:
        grades.append(("Grade 2", 55000, 74000))
    elif d_in <= 1.5:
        grades.append(("Grade 2", 33000, 60000))
    # Grade 5: ≤1" → 85k/120k; >1" ≤ 1-1/2" → 74k/105k
    if d_in <= 1.0:
        grades.append(("Grade 5", 85000, 120000))
    elif d_in <= 1.5:
        grades.append(("Grade 5", 74000, 105000))
    # Grade 8: ≤1.5" → 120k/150k
    if d_in <= 1.5:
        grades.append(("Grade 8", 120000, 150000))
    return grades


# ============================================================
# SHARED NAV/FOOTER HTML
# ============================================================
NAV_SVG = '<svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><circle cx="12" cy="12" r="3"/></svg>'

MENU_BTN_SVG = '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>'

def nav_html():
    return f'''<nav class="bg-emerald-700 text-white shadow-lg">
<div class="max-w-6xl mx-auto px-4">
<div class="flex items-center justify-between h-16">
<a href="/" class="text-xl font-bold flex items-center gap-2">
{NAV_SVG}
ThreadSpec.org
</a>
<div class="hidden md:flex items-center gap-6 text-sm">
<a href="/metric/" class="hover:text-emerald-200">Metric</a>
<a href="/unc/" class="hover:text-emerald-200">UNC</a>
<a href="/unf/" class="hover:text-emerald-200">UNF</a>
<a href="/pipe-threads/" class="hover:text-emerald-200">Pipe</a>
<a href="/tap-drill-chart/" class="hover:text-emerald-200">Tap Drills</a>
<a href="/calculator/" class="hover:text-emerald-200">Calculator</a>
</div>
<button aria-label="Open navigation menu" aria-expanded="false" onclick="var m=document.getElementById('mob-menu');var open=!m.classList.contains('hidden');m.classList.toggle('hidden');this.setAttribute('aria-expanded',String(open?'false':'true'))" class="md:hidden p-2">
{MENU_BTN_SVG}
</button>
</div>
</div>
<div id="mob-menu" class="hidden md:hidden px-4 pb-3 space-y-2">
<a href="/metric/" class="block py-1 hover:text-emerald-200">Metric Threads</a>
<a href="/unc/" class="block py-1 hover:text-emerald-200">UNC Threads</a>
<a href="/unf/" class="block py-1 hover:text-emerald-200">UNF Threads</a>
<a href="/pipe-threads/" class="block py-1 hover:text-emerald-200">Pipe Threads</a>
<a href="/tap-drill-chart/" class="block py-1 hover:text-emerald-200">Tap Drill Chart</a>
<a href="/calculator/" class="block py-1 hover:text-emerald-200">Calculator</a>
</div>
</nav>'''

def footer_html():
    return '''<footer class="bg-gray-100 border-t mt-16">
<div class="max-w-6xl mx-auto px-4 py-10">
<div class="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
<div>
<div class="font-semibold text-gray-800 mb-3">Metric Threads</div>
<ul class="space-y-1 text-sm text-gray-600">
<li><a href="/metric/" class="hover:text-emerald-700">ISO Metric Coarse</a></li>
<li><a href="/metric-fine/" class="hover:text-emerald-700">ISO Metric Fine</a></li>
<li><a href="/metric/m6/" class="hover:text-emerald-700">M6 Thread</a></li>
<li><a href="/metric/m8/" class="hover:text-emerald-700">M8 Thread</a></li>
<li><a href="/metric/m10/" class="hover:text-emerald-700">M10 Thread</a></li>
</ul>
</div>
<div>
<div class="font-semibold text-gray-800 mb-3">Inch Threads</div>
<ul class="space-y-1 text-sm text-gray-600">
<li><a href="/unc/" class="hover:text-emerald-700">UNC Thread Chart</a></li>
<li><a href="/unf/" class="hover:text-emerald-700">UNF Thread Chart</a></li>
<li><a href="/unef/" class="hover:text-emerald-700">UNEF Thread Chart</a></li>
<li><a href="/unc/1-4-unc/" class="hover:text-emerald-700">1/4-20 UNC</a></li>
<li><a href="/unc/1-2-unc/" class="hover:text-emerald-700">1/2-13 UNC</a></li>
</ul>
</div>
<div>
<div class="font-semibold text-gray-800 mb-3">Pipe Threads</div>
<ul class="space-y-1 text-sm text-gray-600">
<li><a href="/pipe-threads/" class="hover:text-emerald-700">NPT Thread Chart</a></li>
<li><a href="/bsp/" class="hover:text-emerald-700">BSP Thread Chart</a></li>
<li><a href="/npt-vs-bsp/" class="hover:text-emerald-700">NPT vs BSP</a></li>
</ul>
</div>
<div>
<div class="font-semibold text-gray-800 mb-3">Tools</div>
<ul class="space-y-1 text-sm text-gray-600">
<li><a href="/tap-drill-chart/" class="hover:text-emerald-700">Tap Drill Chart</a></li>
<li><a href="/calculator/" class="hover:text-emerald-700">Thread Calculator</a></li>
<li><a href="/about/" class="hover:text-emerald-700">About</a></li>
</ul>
</div>
</div>
<div class="border-t pt-6 text-sm text-gray-500 text-center">
<p>&copy; 2026 ThreadSpec.org — Thread Specifications &amp; Tap Drill Reference</p>
<p class="mt-1">Contact: <a href="mailto:info@threadspec.org" class="text-emerald-700 hover:underline">info@threadspec.org</a></p>
<p class="mt-1"><a href="/about/" class="hover:underline">About</a> · <a href="/privacy/" class="hover:underline">Privacy</a> · <a href="/sitemap.xml" class="hover:underline">Sitemap</a></p>
</div>
</div>
</footer>'''

GA_SCRIPT = '''<script async src="https://www.googletagmanager.com/gtag/js?id=G-EPVR72CBWM"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('js',new Date());gtag('config','G-EPVR72CBWM');</script>'''

AHREFS_SCRIPT = '''<script src="https://analytics.ahrefs.com/analytics.js" data-key="Mltx4IlGmyyajJD6d+8LLg" async></script>'''

def head_common(title, desc, canonical, og_image=None):
    if og_image is None:
        og_image = "https://threadspec.org/og-image.png"
    return f'''<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="en" href="{canonical}">
<link rel="alternate" hreflang="x-default" href="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="ThreadSpec.org">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#059669">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="stylesheet" href="/assets/tailwind.css">
{GA_SCRIPT}
{AHREFS_SCRIPT}'''


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  wrote {path.replace(BASE+'/', '')}")


# ============================================================
# CLOSEST INCH DRILL FOR METRIC PAGES
# ============================================================
def closest_inch_drill_for_mm(mm):
    """Find closest inch drill to a metric drill size (for display)."""
    target_in = mm / 25.4
    best_name, best_val = min(INCH_DRILLS_DEDUP, key=lambda x: abs(x[1] - target_in))
    # Format as fraction or number
    best_mm = best_val * 25.4
    return best_name, best_val, best_mm


def format_inch_drill_in(val):
    """Format decimal inch to 4dp."""
    return f"{val:.4f}"


# ============================================================
# FIX METRIC PAGES
# ============================================================
def fix_metric_pages():
    print("\n=== Fixing metric coarse pages ===")
    for slug, d, P in METRIC_COARSE:
        path = os.path.join(BASE, "metric", slug, "index.html")
        fix_metric_page(path, d, P, "coarse", f"/metric/{slug}/")

    print("\n=== Fixing metric fine pages ===")
    for slug, d, P in METRIC_FINE:
        path = os.path.join(BASE, "metric-fine", slug, "index.html")
        fix_metric_page(path, d, P, "fine", f"/metric-fine/{slug}/")


def fix_metric_page(path, d, P, series, url_path):
    if not os.path.exists(path):
        print(f"  SKIP (not found): {path}")
        return

    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Compute correct values
    drill_mm = metric_tap_drill(d, P)
    drill_str = fmt_mm(drill_mm)

    # Compute D1 for display
    D1 = d - 1.0825 * P
    D1_str = fmt_mm(D1)

    # Compute property class loads
    H = math.sqrt(3)/2 * P
    d2 = d - 0.6495 * P
    d1_ext = d - 1.2269 * P
    d3 = D1 - H/6
    As = (math.pi/4) * ((d2+d3)/2)**2

    property_classes = get_metric_property_classes(d)

    # ---- Fix tap drill section ----
    # Fix the bold drill value
    html = re.sub(
        r'<span class="text-2xl font-bold text-emerald-700">[^<]*mm</span>',
        f'<span class="text-2xl font-bold text-emerald-700">{drill_str} mm</span>',
        html, count=1
    )

    # Fix the description line with D1 and closest standard drill
    inch_name, inch_val, inch_mm = closest_inch_drill_for_mm(drill_mm)
    inch_decimal = f"{inch_val:.4f}"
    inch_mm_str = fmt_mm(inch_mm)

    new_desc = (f'<p class="text-sm text-gray-600 mt-1">Calculated minor diameter (D₁): {D1_str} mm. '
                f'Standard metric tap drill (d − P): {drill_str} mm.</p>\n'
                f'<p class="text-sm text-gray-600 mt-1">Closest inch drill: {inch_name} ({inch_decimal}&quot; / {inch_mm_str} mm)</p>')

    # Replace the 2 description lines in tap section
    html = re.sub(
        r'<p class="text-sm text-gray-600 mt-1">Calculated minor diameter \(D₁\):.*?</p>\n'
        r'<p class="text-sm text-gray-600 mt-1">Closest inch drill:.*?</p>',
        new_desc,
        html, count=1, flags=re.DOTALL
    )

    # Handle pages that may have only one desc line
    html = re.sub(
        r'<p class="text-sm text-gray-600 mt-1">Calculated minor diameter \(D₁\):[^<]*</p>(?!\n<p class="text-sm text-gray-600 mt-1">Closest)',
        f'<p class="text-sm text-gray-600 mt-1">Calculated minor diameter (D₁): {D1_str} mm. Standard metric tap drill (d − P): {drill_str} mm.</p>',
        html, count=1
    )

    # ---- Fix 8.8 property class ----
    if d > 16:
        # Fix 8.8: 580/800 → 600/830
        # Also recalculate proof loads
        for cls, proof_mpa, tensile_mpa in property_classes:
            if cls == "8.8":
                proof_load = round(As * proof_mpa / 1000, 1)
                tensile_load = round(As * tensile_mpa / 1000, 1)
                # Find and replace the 8.8 row
                html = re.sub(
                    r'(<td class="px-3 py-2 font-medium">8\.8</td>\s*<td class="px-3 py-2 text-right">)5[78]0(</td>\s*<td class="px-3 py-2 text-right">)8[0-9]{2}(</td>\s*<td class="px-3 py-2 text-right">)[^<]*(</td>\s*<td class="px-3 py-2 text-right">)[^<]*(</td>)',
                    rf'\g<1>{proof_mpa}\g<2>{tensile_mpa}\g<3>{proof_load}\g<4>{tensile_load}\g<5>',
                    html, count=1, flags=re.DOTALL
                )

    # Remove 9.8 row if d > 16 (not applicable above M16)
    if d > 16:
        html = re.sub(
            r'<tr class="hover:bg-emerald-50">\s*<td class="px-3 py-2 font-medium">9\.8</td>.*?</tr>',
            '',
            html, count=1, flags=re.DOTALL
        )

    # ---- Fix meta description ----
    # Update tap drill value in meta description
    html = re.sub(
        r'(content="Complete M[\d\.×x\s]+thread specifications:[^"]*tap drill )\d+\.?\d*(mm)',
        rf'\g<1>{drill_str}\2',
        html, count=1
    )
    # Also update og:description (same pattern)
    # The og:description should match meta description

    # ---- Fix "approximately 75%" false claim in prose if present ----
    html = re.sub(
        r'gives approximately 75% thread engagement, which is the industry standard recommendation\.',
        'The recommended tap drill is d − P (nominal diameter minus pitch), giving approximately 75% thread engagement per industry convention.',
        html
    )

    # ---- Fix mobile menu button (P2 #14) ----
    # Already handled in nav_html() but we're doing surgical fixes
    html = fix_nav_button(html)

    # ---- Fix twitter:card ----
    html = html.replace(
        'content="summary">',
        'content="summary_large_image">',
        1
    )

    # ---- Remove prose class ----
    html = html.replace(' class="prose max-w-none text-gray-700"', ' class="max-w-none text-gray-700"')

    # ---- Fix footer h3 → div ----
    html = fix_footer_headings(html)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  fixed metric page: {url_path}")


def fix_nav_button(html):
    """Fix mobile menu button to add aria-label and aria-expanded."""
    old = ('onclick="document.getElementById(\'mob-menu\').classList.toggle(\'hidden\')" '
           'class="md:hidden p-2">')
    new = ('aria-label="Open navigation menu" aria-expanded="false" '
           'onclick="var m=document.getElementById(\'mob-menu\');var open=!m.classList.contains(\'hidden\');'
           'm.classList.toggle(\'hidden\');this.setAttribute(\'aria-expanded\',String(open?\'false\':\'true\'))" '
           'class="md:hidden p-2">')
    return html.replace(old, new, 1)


def fix_footer_headings(html):
    """Replace <h3 class="font-semibold ..."> in footer with <div class="font-semibold ...">."""
    # In footer, h3 tags for column headings
    html = re.sub(
        r'<h3 class="font-semibold text-gray-800 mb-3">',
        '<div class="font-semibold text-gray-800 mb-3">',
        html
    )
    html = re.sub(
        r'</h3>\n<ul class="space-y-1',
        '</div>\n<ul class="space-y-1',
        html
    )
    return html


# ============================================================
# FIX UNC/UNF/UNEF PAGES
# ============================================================
def fix_inch_pages():
    print("\n=== Fixing UNC pages ===")
    for slug, d_in, tpi in UNC_THREADS:
        path = os.path.join(BASE, "unc", slug, "index.html")
        fix_inch_page(path, d_in, tpi, 'unc', f"/unc/{slug}/")

    print("\n=== Fixing UNF pages ===")
    for slug, d_in, tpi in UNF_THREADS:
        path = os.path.join(BASE, "unf", slug, "index.html")
        fix_inch_page(path, d_in, tpi, 'unf', f"/unf/{slug}/")

    print("\n=== Fixing UNEF pages ===")
    for slug, d_in, tpi in UNEF_THREADS:
        path = os.path.join(BASE, "unef", slug, "index.html")
        fix_inch_page(path, d_in, tpi, 'unef', f"/unef/{slug}/")


def fix_inch_page(path, d_in, tpi, series, url_path):
    if not os.path.exists(path):
        print(f"  SKIP: {path}")
        return

    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Get correct tap drill
    drill_name, drill_in = inch_tap_drill(d_in, tpi, series)
    if drill_name is None:
        print(f"  WARN: no drill found for {url_path}")
        return

    drill_mm = drill_in * 25.4
    drill_mm_str = fmt_mm(drill_mm)
    drill_in_str = f"{drill_in:.4f}".rstrip('0').rstrip('.')
    # Handle whole fractions display
    if '.' not in str(drill_in_str):
        drill_in_str = str(drill_in_str)

    # D1 for display
    P_in = 1.0 / tpi
    D1_in = d_in - 1.0825 * P_in

    # ---- Fix tap drill bold span ----
    # Pattern: <span class="text-2xl font-bold text-blue-700">ANYTHING</span>
    new_drill_text = f'{drill_name} ({drill_in:.4f}&quot; / {drill_mm_str} mm)'
    html = re.sub(
        r'<span class="text-2xl font-bold text-blue-700">[^<]*</span>',
        f'<span class="text-2xl font-bold text-blue-700">{new_drill_text}</span>',
        html, count=1
    )

    # ---- Fix meta/og description tap drill mm value ----
    html = re.sub(
        r'(content="Complete [^"]*tap drill )\d+\.?\d*(mm)',
        rf'\g<1>{drill_mm_str}\2',
        html, count=1
    )

    # ---- Fix J429 grade stresses ----
    grades = get_sae_grades(d_in)

    # Compute tensile stress area for inch thread
    n = tpi
    As_in2 = 0.7854 * (d_in - 0.9743/n)**2
    As_mm2 = As_in2 * 645.16

    for grade_name, proof_psi, tensile_psi in grades:
        proof_lbf = round(As_in2 * proof_psi)
        tensile_lbf = round(As_in2 * tensile_psi)
        grade_num = grade_name.replace("Grade ", "")

        # Replace old grade row
        html = re.sub(
            rf'(<td class="px-3 py-2 font-medium">Grade {grade_num}</td>\s*'
            rf'<td class="px-3 py-2 text-right">[0-9,]+</td>\s*'
            rf'<td class="px-3 py-2 text-right">[0-9,]+</td>\s*'
            rf'<td class="px-3 py-2 text-right">[0-9,]+</td>\s*'
            rf'<td class="px-3 py-2 text-right">[0-9,]+</td>)',
            (f'<td class="px-3 py-2 font-medium">Grade {grade_num}</td>\n'
             f'<td class="px-3 py-2 text-right">{proof_psi:,}</td>\n'
             f'<td class="px-3 py-2 text-right">{tensile_psi:,}</td>\n'
             f'<td class="px-3 py-2 text-right">{proof_lbf:,}</td>\n'
             f'<td class="px-3 py-2 text-right">{tensile_lbf:,}</td>'),
            html, count=1, flags=re.DOTALL
        )

    # ---- Fix twitter:card ----
    html = html.replace('content="summary">', 'content="summary_large_image">', 1)

    # ---- Fix footer h3 → div ----
    html = fix_footer_headings(html)

    # ---- Fix nav button ----
    html = fix_nav_button(html)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  fixed inch page: {url_path}")


# ============================================================
# GENERATE NPT PAGES
# ============================================================
def gen_npt_pages():
    print("\n=== Generating NPT pages ===")
    for npt in NPT_DATA:
        gen_npt_page(npt)


def gen_npt_page(npt):
    slug = npt["slug"]
    nom = npt["nominal"]
    tpi = npt["tpi"]
    od_in = npt["od"]
    e0_in = npt["e0"]
    e1_in = npt["e1"]
    k0_in = npt["k0"]
    tap_name, tap_in = npt["tap_drill"]
    pitch_in = npt["pitch"]
    tap_mm = tap_in * 25.4

    od_mm = od_in * 25.4
    e0_mm = e0_in * 25.4
    e1_mm = e1_in * 25.4
    k0_mm = k0_in * 25.4
    pitch_mm = pitch_in * 25.4

    nom_attr = nom.replace('"', '&quot;')         # safe for HTML attributes
    nom_json = nom.replace('"', '\\"')             # safe for JSON strings
    tap_name_attr = tap_name.replace('"', '&quot;')
    title_plain = f'{nom_attr} NPT Thread — Dimensions &amp; Tap Drill'
    desc_attr = f'Complete {nom_attr} NPT pipe thread specifications per ASME B1.20.1. TPI: {tpi}, OD: {od_in:.4f}&quot; ({od_mm:.2f} mm), tap drill: {tap_name_attr}.'
    canonical = f"https://threadspec.org/npt/{slug}/"

    # Thread depth per ASME B1.20.1: h = 0.8 × p
    h = 0.8 * pitch_in
    h_mm = h * 25.4

    tpi_str = str(int(tpi)) if tpi == int(tpi) else str(tpi)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
{head_common(title_plain, desc_attr, canonical)}

</head>
<body class="bg-white text-gray-900">
{nav_html()}
<main class="max-w-4xl mx-auto px-4 py-8">
<div class="text-sm py-3"><a href="/" class="text-emerald-700 hover:underline">Home</a> <span class="text-gray-400 mx-1">›</span> <a href="/pipe-threads/" class="text-emerald-700 hover:underline">Pipe Threads</a> <span class="text-gray-400 mx-1">›</span> <span class="text-gray-500">{nom_attr} NPT</span></div>
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"https://threadspec.org/"}},{{"@type":"ListItem","position":2,"name":"Pipe Threads","item":"https://threadspec.org/pipe-threads/"}},{{"@type":"ListItem","position":3,"name":"{nom_attr} NPT","item":"{canonical}"}}]}}</script>
<script type="application/ld+json">{{"@context": "https://schema.org", "@type": "TechArticle", "headline": "{nom_json} NPT Thread \\u2014 Dimensions & Tap Drill", "description": "Complete {nom_json} NPT pipe thread specifications per ASME B1.20.1. TPI: {tpi_str}, OD: {od_in:.4f}\\" ({od_mm:.2f} mm), tap drill: {tap_name}.", "url": "{canonical}", "publisher": {{"@type": "Organization", "name": "ThreadSpec.org", "url": "https://threadspec.org/"}}}}</script>

<h1 class="text-3xl font-bold text-gray-900 mb-2">{nom_attr} NPT Thread Specifications</h1>
<p class="text-gray-600 mb-8">Complete dimensions for {nom_attr} NPT (National Pipe Taper) thread per ASME B1.20.1. TPI: {tpi_str}, Pitch: {pitch_in:.5f}&quot; ({pitch_mm:.3f} mm). Taper: 1 in 16 on diameter (3/4&quot; per foot).</p>

<section class="mb-8">
<h2 class="text-xl font-bold text-gray-900 mb-3">Thread Dimensions</h2>
<div class="overflow-x-auto">
<table class="w-full text-sm border-collapse border">
<tbody>
<tr class="bg-gray-50"><td class="px-4 py-2 font-medium border">Designation</td><td class="px-4 py-2 border">{nom_attr} NPT</td></tr>
<tr><td class="px-4 py-2 font-medium border">Nominal Pipe Size</td><td class="px-4 py-2 border">{nom_attr}</td></tr>
<tr class="bg-gray-50"><td class="px-4 py-2 font-medium border">TPI</td><td class="px-4 py-2 border">{tpi_str}</td></tr>
<tr><td class="px-4 py-2 font-medium border">Pitch</td><td class="px-4 py-2 border">{pitch_in:.5f}&quot; ({pitch_mm:.3f} mm)</td></tr>
<tr class="bg-gray-50"><td class="px-4 py-2 font-medium border">Outside Diameter</td><td class="px-4 py-2 border">{od_in:.4f}&quot; ({od_mm:.2f} mm)</td></tr>
<tr><td class="px-4 py-2 font-medium border">Pitch Diameter at E0 (hand-tight)</td><td class="px-4 py-2 border">{e0_in:.5f}&quot; ({e0_mm:.3f} mm)</td></tr>
<tr class="bg-gray-50"><td class="px-4 py-2 font-medium border">Pitch Diameter at E1 (wrench makeup)</td><td class="px-4 py-2 border">{e1_in:.5f}&quot; ({e1_mm:.3f} mm)</td></tr>
<tr><td class="px-4 py-2 font-medium border">Minor Diameter at E0</td><td class="px-4 py-2 border">{k0_in:.5f}&quot; ({k0_mm:.3f} mm)</td></tr>
<tr class="bg-gray-50"><td class="px-4 py-2 font-medium border">Taper Angle</td><td class="px-4 py-2 border">1.7899° (1:16 taper ratio, 3/4&quot;/ft)</td></tr>
<tr><td class="px-4 py-2 font-medium border">Thread Depth (h = 0.8p)</td><td class="px-4 py-2 border">{h:.5f}&quot; ({h_mm:.3f} mm)</td></tr>
</tbody>
</table>
</div>
<p class="text-xs text-gray-500 mt-2">Values per ASME B1.20.1 Table 1. E0 = hand-tight engagement pitch diameter; E1 = wrench-makeup pitch diameter.</p>
</section>

<section class="mb-8">
<h2 class="text-xl font-bold text-gray-900 mb-3">Tap Drill Size</h2>
<div class="bg-amber-50 border border-amber-200 rounded-lg p-4">
<p class="text-lg"><strong>Tap drill:</strong> <span class="text-2xl font-bold text-amber-700">{tap_name} ({tap_in:.4f}&quot; / {tap_mm:.2f} mm)</span></p>
<p class="text-sm text-gray-600 mt-1">NPT tap drills allow the tap to cut the taper thread. The tap itself creates the taper geometry; drill size provides initial clearance at the large end.</p>
</div>
</section>

<section class="mb-8">
<h2 class="text-xl font-bold text-gray-900 mb-3">Common Applications</h2>
<ul class="list-disc pl-6 text-gray-700 space-y-1"><li>Plumbing connections</li><li>Gas piping</li><li>Hydraulic fittings</li><li>Pneumatic connections</li></ul>
</section>

</main>
{footer_html()}
</body></html>'''

    path = os.path.join(BASE, "npt", slug, "index.html")
    write_file(path, html)


# ============================================================
# FIX BSP PAGES
# ============================================================
def fix_bsp_pages():
    print("\n=== Fixing BSP pages ===")
    for row in BSP_TABLE:
        slug, nom, tpi, od_in, pitch_in, minor_in, od_mm, pitch_mm, minor_mm, tap_mm = row

        # Check if this BSP page exists
        path = os.path.join(BASE, "bsp", slug, "index.html")
        if not os.path.exists(path):
            print(f"  SKIP (not found): {path}")
            continue

        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()

        tap_label, _ = BSP_TAP_DRILLS.get(slug, (f"{tap_mm} mm", tap_mm))

        # Fix OD if this is one of the 3 wrong ones
        if slug in BSP_CORRECT_OD:
            correct_od_in, correct_od_mm = BSP_CORRECT_OD[slug]
            # Replace OD in the table
            html = re.sub(
                r'(<td class="px-4 py-2 font-medium border">Outside Diameter</td><td class="px-4 py-2 border">)[^<]*(</td>)',
                rf'\g<1>{correct_od_in:.3f}&quot; ({correct_od_mm:.3f} mm)\2',
                html, count=1
            )
            # Also update meta description if it mentions the old OD
            html = re.sub(
                r'(OD: )\d+\.\d+(&quot;)',
                rf'\g<1>{correct_od_in:.3f}\2',
                html, count=1
            )

        # Fix tap drill
        # Replace the tap drill span
        html = re.sub(
            r'<span class="text-2xl font-bold text-amber-700">[^<]*</span>',
            f'<span class="text-2xl font-bold text-amber-700">{tap_label}</span>',
            html, count=1
        )

        # Update meta tap drill
        html = re.sub(
            r'(tap drill: )\d+\.?\d*(mm)',
            rf'\g<1>{tap_mm}\2',
            html, count=1
        )

        # Fix twitter:card
        html = html.replace('content="summary">', 'content="summary_large_image">', 1)

        # Fix footer headings
        html = fix_footer_headings(html)
        html = fix_nav_button(html)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  fixed BSP page: /bsp/{slug}/")

    # Fix bsp/index.html
    fix_bsp_index()


def fix_bsp_index():
    path = os.path.join(BASE, "bsp", "index.html")
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Fix the 3 wrong ODs in the table
    # G7/8: 1.1 → 1.189
    html = re.sub(
        r'(href="/bsp/g7-8-bsp/"[^>]*>G7/8&quot; BSP</a></td>\s*<td[^>]*>\d+</td>\s*<td[^>]*>)[\d\.]+',
        r'\g<1>1.189',
        html, count=1
    )
    # G2-1/2: 2.82 → 2.960
    html = re.sub(
        r'(href="/bsp/g2-1-2-bsp/"[^>]*>G2-1/2&quot; BSP</a></td>\s*<td[^>]*>\d+</td>\s*<td[^>]*>)[\d\.]+',
        r'\g<1>2.960',
        html, count=1
    )
    # G4: 4.2 → 4.450
    html = re.sub(
        r'(href="/bsp/g4-bsp/"[^>]*>G4&quot; BSP</a></td>\s*<td[^>]*>\d+</td>\s*<td[^>]*>)[\d\.]+',
        r'\g<1>4.450',
        html, count=1
    )

    # Fix BSP tap drills (was showing minor diameter as drill)
    for row in BSP_TABLE:
        slug, nom, tpi, od_in, pitch_in, minor_in, od_mm, pitch_mm, minor_mm, tap_mm = row
        tap_label, _ = BSP_TAP_DRILLS.get(slug, (f"{tap_mm}", tap_mm))
        # In the index table, the last column is "Tap Drill (mm)"
        # Find the row by slug and fix the last td
        html = re.sub(
            rf'(href="/bsp/{slug}/"[^>]*>[^<]*</a></td>(?:<td[^>]*>[^<]*</td>){{4}}<td[^>]*>)[^<]*(</td>)',
            rf'\g<1>{tap_mm}\2',
            html, count=1
        )

    # Fix meta description: BS 21 → ISO 228
    html = html.replace('per ISO 228 / BS 21', 'per ISO 228')
    html = html.replace('/ BS 21', '')

    # Fix twitter:card
    html = html.replace('content="summary">', 'content="summary_large_image">', 1)
    html = fix_footer_headings(html)
    html = fix_nav_button(html)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("  fixed BSP index page")


# ============================================================
# FIX 404 PAGE
# ============================================================
def fix_404():
    print("\n=== Fixing 404.html ===")
    path = os.path.join(BASE, "404.html")
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Add noindex
    html = html.replace(
        '<meta name="theme-color" content="#059669">',
        '<meta name="robots" content="noindex">\n<meta name="theme-color" content="#059669">'
    )

    # Remove canonical and hreflang from 404
    html = re.sub(r'<link rel="canonical"[^>]*>\n', '', html)
    html = re.sub(r'<link rel="alternate" hreflang[^>]*>\n', '', html)
    html = re.sub(r'<link rel="alternate" hreflang[^>]*>\n', '', html)

    # Fix twitter:card
    html = html.replace('content="summary">', 'content="summary_large_image">', 1)
    html = fix_footer_headings(html)
    html = fix_nav_button(html)

    # Fix description length (currently 48 chars - pad it)
    html = re.sub(
        r'<meta name="description" content="The page you are looking for could not be found\.">',
        '<meta name="description" content="Page not found on ThreadSpec.org. Browse our thread specification reference for metric, UNC, UNF, NPT, and BSP threads.">',
        html
    )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("  fixed 404.html")


# ============================================================
# FIX PRIVACY PAGE
# ============================================================
def fix_privacy():
    print("\n=== Fixing privacy page ===")
    path = os.path.join(BASE, "privacy", "index.html")
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Fix the CDN claim - Tailwind is self-hosted
    html = html.replace(
        'Pages load the Tailwind CSS library and Google Analytics script from third-party content delivery networks.',
        'Pages load the Google Analytics script from a third-party CDN (googletagmanager.com). The site\'s stylesheet (Tailwind CSS) is self-hosted and loaded directly from this server.'
    )

    html = html.replace('content="summary">', 'content="summary_large_image">', 1)
    html = fix_footer_headings(html)
    html = fix_nav_button(html)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("  fixed privacy page")


# ============================================================
# FIX ABOUT PAGE
# ============================================================
def fix_about():
    print("\n=== Fixing about page ===")
    path = os.path.join(BASE, "about", "index.html")
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Fix "ISO 228 / BS 21" → "ISO 228 / BS 2779" (BSP parallel threads)
    # BS 21 is for taper pipe threads; BS 2779 is for parallel (G) threads
    html = html.replace('ISO 228 / BS 21', 'ISO 228-1 (parallel, G thread)')

    html = html.replace('content="summary">', 'content="summary_large_image">', 1)
    html = fix_footer_headings(html)
    html = fix_nav_button(html)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("  fixed about page")


# ============================================================
# FIX CALCULATOR PAGE
# ============================================================
def fix_calculator():
    print("\n=== Fixing calculator page ===")
    path = os.path.join(BASE, "calculator", "index.html")
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Fix Aₛ formula: d₃ = d₁ − H/6 → d₃ = D₁ − H/6 (internal minor, not external)
    html = html.replace('where d₃ = d₁ − H/6', 'where d₃ = D₁ − H/6')

    # Fix FAQ text confusion: d1 is external minor; D1 is internal minor
    html = html.replace(
        'd3 = d1 - H/6 (d1 = d - 1.0825P is the basic minor diameter',
        'd3 = D1 - H/6 (D1 = d - 1.0825P is the internal minor diameter'
    )

    # Add for attributes to labels (labels are self-contained, no need for adjacent element)
    html = html.replace(
        '<label class="block text-sm font-medium text-gray-700 mb-1">Thread System</label>',
        '<label for="system" class="block text-sm font-medium text-gray-700 mb-1">Thread System</label>'
    )
    html = html.replace(
        '<label class="block text-sm font-medium text-gray-700 mb-1" id="diam-label">Nominal Diameter (mm)</label>',
        '<label for="diameter" class="block text-sm font-medium text-gray-700 mb-1" id="diam-label">Nominal Diameter (mm)</label>'
    )
    html = html.replace(
        '<label class="block text-sm font-medium text-gray-700 mb-1" id="pitch-label">Pitch (mm)</label>',
        '<label for="pitch" class="block text-sm font-medium text-gray-700 mb-1" id="pitch-label">Pitch (mm)</label>'
    )

    # Fix the calculate() JS: add early return with message for invalid inputs
    html = html.replace(
        '    if (isNaN(d) || isNaN(p_input) || d <= 0 || p_input <= 0) return;',
        ('    if (isNaN(d) || isNaN(p_input) || d <= 0 || p_input <= 0) {\n'
         '        document.querySelector(\'#results-table tbody\').innerHTML = '
         '\'<tr><td class="px-4 py-2 text-red-600" colspan="2">Invalid input — enter a positive diameter and pitch.</td></tr>\';\n'
         '        return;\n'
         '    }')
    )

    # Add negative-diameter warning right after D1 is computed
    html = html.replace(
        '    const D1 = d - 1.0825 * P;',
        ('    const D1 = d - 1.0825 * P;\n'
         '    if (D1 <= 0) {\n'
         '        document.querySelector(\'#results-table tbody\').innerHTML = '
         '\'<tr><td class="px-4 py-2 text-red-600" colspan="2">Pitch too large — minor diameter would be negative.</td></tr>\';\n'
         '        return;\n'
         '    }')
    )

    # Remove dead d_mm variable
    html = html.replace('    let P, d_mm, unit;\n', '    let P, unit;\n')
    html = html.replace('        d_mm = d;\n', '')
    html = html.replace('        d_mm = d * 25.4;\n', '')

    html = html.replace('content="summary">', 'content="summary_large_image">', 1)
    html = fix_footer_headings(html)
    html = fix_nav_button(html)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("  fixed calculator page")


# ============================================================
# FIX INDEX PAGE
# ============================================================
def fix_index():
    print("\n=== Fixing index.html ===")
    path = os.path.join(BASE, "index.html")
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Fix FAQ "75% engagement" claim
    html = html.replace(
        'The tap drill size equals the internal minor diameter (D1) of the thread. For metric threads: D1 = d - 1.0825 × P. This gives approximately 75% thread engagement, which is the industry standard recommendation.',
        'The tap drill size is typically chosen as d − P (nominal diameter minus pitch), giving approximately 75% thread engagement. For metric threads this equals the internal minor diameter formula D1 = d − 1.0825 × P for the d − P case only when P is such that 1.0825P ≈ P (they differ slightly). The 75% standard balances strength with ease of tapping.'
    )

    # Also fix the JSON-LD FAQPage answer for same question
    html = html.replace(
        '"The tap drill size equals the internal minor diameter (D1) of the thread. For metric threads: D1 = d - 1.0825 × P. This gives approximately 75% thread engagement, which is the industry standard recommendation."',
        '"The tap drill size is typically d − P (nominal diameter minus pitch), giving approximately 75% thread engagement — the industry-standard compromise between thread strength and ease of tapping."'
    )

    # Fix the metric table "Tap Drill (mm)" column to use standard drills not D1
    # The table has M3-M24 with D1 values. Replace with d-P values.
    metric_table_fixes = [
        ("M3",   "2.46", "2.5"),   # d-P=2.5
        ("M4",   "3.24", "3.3"),   # d-P=3.3
        ("M5",   "4.13", "4.2"),   # d-P=4.2
        ("M6",   "4.92", "5.0"),   # d-P=5.0
        ("M8",   "6.65", "6.8"),   # d-P=6.75→6.8
        ("M10",  "8.38", "8.5"),   # d-P=8.5
        ("M12", "10.11", "10.2"),  # d-P=10.25→10.5 but ISO pub=10.2; keep consistent
        ("M16", "13.84", "14.0"),  # d-P=14.0
        ("M20", "17.29", "17.5"),  # d-P=17.5
        ("M24", "20.75", "21.0"),  # d-P=21.0→21.0
    ]
    for thread, old_drill, new_drill in metric_table_fixes:
        # Replace in table row
        html = html.replace(
            f'<td class="px-3 py-2 text-right">{old_drill}</td>\n',
            f'<td class="px-3 py-2 text-right">{new_drill}</td>\n',
            1  # replace first occurrence only
        )

    # Fix the UNC table: fix tap drill (mm) column values
    # UNC "Tap Drill (mm)" = drill in mm
    unc_table_fixes = [
        ("#6-32 UNC",  "/unc/num-6-unc/",  "2.6",  "2.7"),  # #36=0.1065"=2.705mm
        ("#8-32 UNC",  "/unc/num-8-unc/",  "3.3",  "3.45"), # #29=0.136"=3.454mm
        ("#10-24 UNC", "/unc/num-10-unc/", "3.7",  "3.8"),  # #25=0.1495"=3.797mm
        ("1/4-20 UNC", "/unc/1-4-unc/",    "5",    "5.1"),  # #7=0.201"=5.105mm
        ("5/16-18 UNC","/unc/5-16-unc/",   "6.4",  "6.5"),  # F=0.257"=6.527mm
        ("3/8-16 UNC", "/unc/3-8-unc/",    "7.8",  "7.94"), # 5/16"=0.3125"=7.938mm
        ("1/2-13 UNC", "/unc/1-2-unc/",    "10.6", "10.72"),# 27/64"=0.421875"=10.716mm
        ("5/8-11 UNC", "/unc/5-8-unc/",    "13.4", "13.49"),# 17/32"=0.53125"=13.494mm
        ("3/4-10 UNC", "/unc/3-4-unc/",    "16.3", "16.67"),# 21/32"=0.65625"=16.669mm
        ("1-8 UNC",    "/unc/1-unc/",      "22",   "22.23"),# 7/8"=0.875"=22.225mm
    ]
    for thread, href, old_mm, new_mm in unc_table_fixes:
        # In the table row, replace the last td (tap drill mm)
        html = re.sub(
            rf'(href="{href}"[^>]*>{re.escape(thread)}</a></td>(?:<td[^>]*>[^<]*</td>){{3}}<td[^>]*>){re.escape(old_mm)}(</td>)',
            rf'\g<1>{new_mm}\2',
            html, count=1
        )

    # Fix emerald hover in UNC table (blue section): change emerald-50 → blue-50
    # The UNC table uses "hover:bg-emerald-50" and "text-emerald-700" links
    # Find the UNC section and fix
    unc_section_start = html.find('<section class="mb-12">\n<h2 class="text-2xl font-bold text-gray-900 mb-4">Popular UNC Thread Sizes</h2>')
    unc_section_end = html.find('</section>', unc_section_start)
    if unc_section_start > 0 and unc_section_end > 0:
        unc_section = html[unc_section_start:unc_section_end+10]
        unc_section = unc_section.replace('hover:bg-emerald-50', 'hover:bg-blue-50')
        unc_section = unc_section.replace('class="text-emerald-700 font-medium hover:underline"', 'class="text-blue-700 font-medium hover:underline"')
        html = html[:unc_section_start] + unc_section + html[unc_section_end+10:]

    # Fix twitter:card
    html = html.replace('content="summary">', 'content="summary_large_image">', 1)
    html = fix_footer_headings(html)
    html = fix_nav_button(html)

    # Fix description length (was 191 chars)
    # Current: "Complete thread specification reference: ISO metric, UNC, UNF, NPT, BSP. Tap drill charts, thread dimensions, pitch diameters, and stress areas calculated from ISO 724 and ASME B1.1 formulas."
    html = html.replace(
        'content="Complete thread specification reference: ISO metric, UNC, UNF, NPT, BSP. Tap drill charts, thread dimensions, pitch diameters, and stress areas calculated from ISO 724 and ASME B1.1 formulas."',
        'content="Thread specification reference for metric, UNC, UNF, NPT, and BSP threads. Tap drill charts, dimensions, and proof loads per ISO 724 and ASME B1.1."'
    )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("  fixed index.html")


# ============================================================
# FIX TAP DRILL CHART
# ============================================================
def fix_tap_drill_chart():
    print("\n=== Fixing tap-drill-chart ===")
    path = os.path.join(BASE, "tap-drill-chart", "index.html")
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Fix title/H1/meta: "Metric, UNC, UNF & Pipe Threads" → "Metric & UNC Threads"
    # (since page only has metric coarse and UNC)
    html = html.replace(
        'Tap Drill Chart — Metric, UNC, UNF &amp; Pipe Threads',
        'Tap Drill Chart — ISO Metric Coarse &amp; UNC Threads'
    )
    html = html.replace(
        '<title>Tap Drill Chart — Metric, UNC, UNF &amp; Pipe Threads</title>',
        '<title>Tap Drill Chart — ISO Metric Coarse &amp; UNC Threads</title>'
    )
    html = html.replace(
        'content="Complete tap drill size chart for metric, UNC, UNF, UNEF, NPT, and BSP threads. Find the right drill bit for any thread size."',
        'content="Tap drill size chart for ISO metric coarse and UNC threads. Standard drill sizes using the d &#x2212; P (75% engagement) convention."'
    )
    html = html.replace(
        '<h1 class="text-3xl font-bold text-gray-900 mb-4">Tap Drill Size Chart</h1>',
        '<h1 class="text-3xl font-bold text-gray-900 mb-4">Tap Drill Size Chart — Metric &amp; UNC</h1>'
    )

    # Fix intro paragraph: remove "D₁" = 75% claim
    html = html.replace(
        'Drill sizes are calculated from internal minor diameter (D₁) per ISO 724 and ASME B1.1, giving approximately 75% thread engagement.',
        'Drill sizes use the d &#x2212; P convention (nominal diameter minus pitch), the industry-standard recommendation for approximately 75% thread engagement.'
    )

    # Fix How tap drill sizes are determined section
    html = html.replace(
        'The tap drill diameter equals the internal minor diameter (D₁) of the thread, which produces approximately 75% thread engagement — the industry-standard recommendation. Higher thread engagement (smaller drill) increases tapping torque and risk of tap breakage without significantly increasing joint strength.',
        'The recommended tap drill is d &#x2212; P (nominal diameter minus one pitch). This gives approximately 75% thread engagement — the industry-standard balance of joint strength against tapping torque and risk of tap breakage.'
    )
    html = html.replace(
        'For metric threads: D₁ = d − 1.0825 × P. For unified inch threads: D₁ = d − 1.0825 × (1/TPI).',
        'For metric threads: tap drill = d − P. For unified inch threads, refer to the published ASME B1.1 tap drill table.'
    )

    # Fix FAQ: "rounded to the nearest standard drill size" → "rounded UP"
    html = html.replace(
        'This is based on the internal minor diameter D1 = 10 - 1.0825 × 1.5 = 8.38mm, rounded to the nearest standard drill size.',
        'Use d − P = 10 − 1.5 = 8.5 mm; round up to the next standard size ≥ 8.5 mm = 8.5 mm.'
    )
    html = html.replace(
        'For metric threads: tap drill = nominal diameter - (1.0825 × pitch). For inch threads: tap drill = nominal diameter - (1.0825 / TPI). Then round to the nearest standard drill size.',
        'For metric threads: tap drill = nominal diameter − pitch (d − P). For inch threads, use the published ASME B1.1 tap drill table. Always round UP to the next standard size.'
    )

    # Fix JSON-LD FAQ
    html = html.replace(
        '"For an M10×1.5 coarse thread, use an 8.5mm tap drill. This is based on the internal minor diameter D1 = 10 - 1.0825 × 1.5 = 8.38mm, rounded to the nearest standard drill size."',
        '"For an M10×1.5 coarse thread, use an 8.5mm tap drill: d − P = 10 − 1.5 = 8.5mm (the standard 75% engagement recommendation)."'
    )
    html = html.replace(
        '"For metric threads: tap drill = nominal diameter - (1.0825 × pitch). For inch threads: tap drill = nominal diameter - (1.0825 / TPI). Then round to the nearest standard drill size."',
        '"For metric threads: tap drill = d − P (nominal diameter minus pitch). For inch threads, consult the published ASME B1.1 tap drill table. Always round up to the next available standard drill size."'
    )

    # Now fix the metric coarse table values
    # Column: Calculated(mm) = D1, Standard Drill(mm), Inch Drill
    for slug, d, P in METRIC_COARSE:
        D1 = d - 1.0825 * P
        D1_str = fmt_mm(D1)
        drill_mm = metric_tap_drill(d, P)
        drill_str = fmt_mm(drill_mm)
        inch_name, inch_val, inch_mm = closest_inch_drill_for_mm(drill_mm)

        # Replace the row in the table
        # Pattern: link to /metric/slug/ ... D1 value ... current drill ... inch drill
        link_pattern = rf'(/metric/{slug}/"[^>]*>M[\d\.×]+</a>)'
        html = re.sub(
            rf'(href="/metric/{slug}/"[^>]*>[^<]*</a></td>\s*<td[^>]*>){D1_str}(</td>\s*<td[^>]*>)[^<]*(</td>\s*<td[^>]*>)[^<]*(</td>)',
            rf'\g<1>{D1_str}\g<2>{drill_str}\g<3>{inch_name}\g<4>',
            html, count=1
        )

    # Fix UNC table values
    unc_pub_drills = {
        "num-1-unc":  ("#53", 0.0595), "num-2-unc": ("#50", 0.0700),
        "num-3-unc":  ("#47", 0.0785), "num-4-unc": ("#43", 0.0890),
        "num-5-unc":  ("#38", 0.1015), "num-6-unc": ("#36", 0.1065),
        "num-8-unc":  ("#29", 0.1360), "num-10-unc": ("#25", 0.1495),
        "num-12-unc": ("11/64\"", 0.171875),
        "1-4-unc":    ("#7", 0.2010),  "5-16-unc": ("F", 0.2570),
        "3-8-unc":    ("5/16\"", 0.3125), "7-16-unc": ("U", 0.3680),
        "1-2-unc":    ("27/64\"", frac(27,64)), "9-16-unc": ("31/64\"", frac(31,64)),
        "5-8-unc":    ("17/32\"", frac(17,32)), "3-4-unc": ("21/32\"", frac(21,32)),
        "7-8-unc":    ("49/64\"", frac(49,64)), "1-unc": ("7/8\"", 0.875),
        "1-1-8-unc":  ("63/64\"", frac(63,64)), "1-1-4-unc": ("1-7/64\"", 1+frac(7,64)),
        "1-3-8-unc":  ("1-7/32\"", 1+frac(7,32)), "1-1-2-unc": ("1-11/32\"", 1+frac(11,32)),
        "1-3-4-unc":  ("1-9/16\"", 1+frac(9,16)), "2-unc": ("1-25/32\"", 1+frac(25,32)),
        "2-1-4-unc":  ("2-1/32\"", 2+frac(1,32)), "2-1-2-unc": ("2-1/4\"", 2.25),
        "2-3-4-unc":  ("2-1/2\"", 2.50), "3-unc": ("2-3/4\"", 2.75),
        "3-1-4-unc":  ("3\"", 3.00), "3-1-2-unc": ("3-1/4\"", 3.25),
        "3-3-4-unc":  ("3-1/2\"", 3.50), "4-unc": ("3-3/4\"", 3.75),
    }

    for slug, d_in, tpi in UNC_THREADS:
        P_in = 1.0 / tpi
        D1_in = d_in - 1.0825 * P_in
        D1_str = f'{D1_in:.4f}"'
        drill_name, drill_in = unc_pub_drills.get(slug, smallest_inch_drill_ge(D1_in))
        drill_mm = drill_in * 25.4

        html = re.sub(
            rf'(href="/unc/{slug}/"[^>]*>[^<]*</a></td>\s*<td[^>]*>)[^"<]+"(</td>\s*<td[^>]*>)[^<]*(</td>\s*<td[^>]*>)[^<]*(</td>)',
            rf'\g<1>{D1_in:.4f}"\g<2>{drill_name}\g<3>{drill_mm:.2f}\g<4>',
            html, count=1
        )

    # Fix twitter:card
    html = html.replace('content="summary">', 'content="summary_large_image">', 1)
    html = fix_footer_headings(html)
    html = fix_nav_button(html)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("  fixed tap-drill-chart")


# ============================================================
# CREATE /npt/index.html STUB (P2 #9)
# ============================================================
def create_npt_index():
    print("\n=== Creating /npt/index.html stub ===")
    path = os.path.join(BASE, "npt", "index.html")
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="0;url=/pipe-threads/">
<link rel="canonical" href="https://threadspec.org/pipe-threads/">
<title>NPT Threads — Redirecting to NPT Thread Chart</title>
<meta name="robots" content="noindex">
<script src="https://analytics.ahrefs.com/analytics.js" data-key="Mltx4IlGmyyajJD6d+8LLg" async></script>
</head>
<body>
<p>Redirecting to <a href="/pipe-threads/">NPT Thread Chart</a>...</p>
</body>
</html>'''
    write_file(path, html)


# ============================================================
# ADD .gitignore
# ============================================================
def create_gitignore():
    print("\n=== Creating .gitignore ===")
    path = os.path.join(BASE, ".gitignore")
    content = ".claude/\n"
    if os.path.exists(path):
        with open(path, 'r') as f:
            existing = f.read()
        if ".claude/" not in existing:
            with open(path, 'a') as f:
                f.write(content)
            print("  added .claude/ to .gitignore")
        else:
            print("  .gitignore already has .claude/")
    else:
        with open(path, 'w') as f:
            f.write(content)
        print("  created .gitignore")


# ============================================================
# DELETE PLACEHOLDER FILE
# ============================================================
def delete_placeholder():
    print("\n=== Deleting placeholder file ===")
    path = os.path.join(BASE, "a1b2c3d4e5f6478890abcdef12345678.txt")
    if os.path.exists(path):
        os.remove(path)
        print(f"  deleted {path}")
    else:
        print("  placeholder not found (already deleted?)")


# ============================================================
# FIX PIPE-THREADS INDEX (NPT index page)
# ============================================================
def fix_pipe_threads_index():
    print("\n=== Fixing pipe-threads/index.html ===")
    path = os.path.join(BASE, "pipe-threads", "index.html")
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Replace the whole NPT table with correct ASME B1.20.1 tabulated values
    # Build correct table rows
    rows = []
    for npt in NPT_DATA:
        slug = npt["slug"]
        nom = npt["nominal"]
        tpi = npt["tpi"]
        od_in = npt["od"]
        e0_in = npt["e0"]
        k0_in = npt["k0"]
        tap_name, tap_in = npt["tap_drill"]
        tap_mm = tap_in * 25.4
        tpi_str = str(int(tpi)) if tpi == int(tpi) else str(tpi)

        rows.append(f'''<tr class="hover:bg-amber-50">
<td class="px-3 py-2"><a href="/npt/{slug}/" class="text-amber-700 font-medium hover:underline">{nom} NPT</a></td>
<td class="px-3 py-2 text-right">{tpi_str}</td>
<td class="px-3 py-2 text-right">{od_in:.4f}</td>
<td class="px-3 py-2 text-right">{e0_in:.5f}</td>
<td class="px-3 py-2 text-right">{k0_in:.5f}</td>
<td class="px-3 py-2 text-right">{tap_name} ({tap_mm:.2f} mm)</td>
</tr>''')

    new_thead = '''<thead><tr class="bg-amber-700 text-white">
<th class="px-3 py-2 text-left">Thread</th>
<th class="px-3 py-2 text-right">TPI</th>
<th class="px-3 py-2 text-right">OD (in)</th>
<th class="px-3 py-2 text-right">E0 Pitch Ø (in)</th>
<th class="px-3 py-2 text-right">Minor Ø at E0 (in)</th>
<th class="px-3 py-2 text-right">Tap Drill</th>
</tr></thead>'''

    new_table = f'''<div class="overflow-x-auto">
<table class="w-full text-sm border-collapse">
{new_thead}
<tbody class="divide-y">{''.join(rows)}</tbody>
</table>
</div>
<p class="text-xs text-gray-500 mt-2">E0 = hand-tight engagement pitch diameter per ASME B1.20.1. Taper: 1 in 16 on diameter (3/4&quot;/ft).</p>'''

    # Replace the existing table
    html = re.sub(
        r'<div class="overflow-x-auto">.*?</div>',
        new_table,
        html, count=1, flags=re.DOTALL
    )

    html = html.replace('content="summary">', 'content="summary_large_image">', 1)
    html = fix_footer_headings(html)
    html = fix_nav_button(html)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("  fixed pipe-threads/index.html")


# ============================================================
# FIX SECTION INDEX PAGES (unc/, unf/, unef/, bsp/)
# ============================================================
def fix_section_indexes():
    print("\n=== Fixing section index pages ===")

    # These pages need: twitter:card, footer h3→div, nav button, h1→h3 skip fix
    for idx_path in [
        "unc/index.html", "unf/index.html", "unef/index.html",
        "metric/index.html", "metric-fine/index.html",
    ]:
        path = os.path.join(BASE, idx_path)
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        html = html.replace('content="summary">', 'content="summary_large_image">', 1)
        html = fix_footer_headings(html)
        html = fix_nav_button(html)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  fixed {idx_path}")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("ThreadSpec.org audit fix script")
    print("=" * 50)

    delete_placeholder()
    create_gitignore()
    create_npt_index()

    fix_404()
    fix_privacy()
    fix_about()
    fix_calculator()
    fix_index()
    fix_tap_drill_chart()
    fix_pipe_threads_index()
    fix_section_indexes()

    gen_npt_pages()
    fix_bsp_pages()
    fix_metric_pages()
    fix_inch_pages()

    print("\n=== Done! ===")
