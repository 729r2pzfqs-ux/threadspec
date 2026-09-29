"""Standard twist drill sizes: number, letter, fractional inch and metric."""
from fractions import Fraction

NUMBER = {
    80: .0135, 79: .0145, 78: .0160, 77: .0180, 76: .0200, 75: .0210, 74: .0225, 73: .0240,
    72: .0250, 71: .0260, 70: .0280, 69: .0292, 68: .0310, 67: .0320, 66: .0330, 65: .0350,
    64: .0360, 63: .0370, 62: .0380, 61: .0390, 60: .0400, 59: .0410, 58: .0420, 57: .0430,
    56: .0465, 55: .0520, 54: .0550, 53: .0595, 52: .0635, 51: .0670, 50: .0700, 49: .0730,
    48: .0760, 47: .0785, 46: .0810, 45: .0820, 44: .0860, 43: .0890, 42: .0935, 41: .0960,
    40: .0980, 39: .0995, 38: .1015, 37: .1040, 36: .1065, 35: .1100, 34: .1110, 33: .1130,
    32: .1160, 31: .1200, 30: .1285, 29: .1360, 28: .1405, 27: .1440, 26: .1470, 25: .1495,
    24: .1520, 23: .1540, 22: .1570, 21: .1590, 20: .1610, 19: .1660, 18: .1695, 17: .1730,
    16: .1770, 15: .1800, 14: .1820, 13: .1850, 12: .1890, 11: .1910, 10: .1935, 9: .1960,
    8: .1990, 7: .2010, 6: .2040, 5: .2055, 4: .2090, 3: .2130, 2: .2210, 1: .2280,
}
LETTER = {
    'A': .234, 'B': .238, 'C': .242, 'D': .246, 'E': .250, 'F': .257, 'G': .261, 'H': .266,
    'I': .272, 'J': .277, 'K': .281, 'L': .290, 'M': .295, 'N': .302, 'O': .316, 'P': .323,
    'Q': .332, 'R': .339, 'S': .348, 'T': .358, 'U': .368, 'V': .377, 'W': .386, 'X': .397,
    'Y': .404, 'Z': .413,
}


def frac_name(fr):
    """Fraction(59, 64) -> '59/64'; Fraction(37, 32) -> '1-5/32'; Fraction(2) -> '2'."""
    whole, rem = divmod(fr.numerator, fr.denominator)
    if rem == 0:
        return str(whole)
    part = f"{rem}/{fr.denominator}"
    return f"{whole}-{part}" if whole else part


def parse_frac(s):
    """'1-5/32' -> Fraction(37, 32)."""
    s = s.strip().rstrip('"')
    if '-' in s:
        w, f = s.split('-')
        return int(w) + Fraction(f)
    return Fraction(s)


def inch_drills():
    """All inch drills as (name, diameter_in), sorted by diameter."""
    out = [(f"#{n}", d) for n, d in NUMBER.items()]
    out += [(k, d) for k, d in LETTER.items()]
    for i in range(1, 64 * 4 + 1):          # 1/64 steps to 4 in
        fr = Fraction(i, 64)
        if fr <= Fraction(7, 4) or fr.denominator <= 32 and fr <= 2 or fr.denominator <= 16:
            out.append((frac_name(fr) + '"', float(fr)))
    return sorted(out, key=lambda x: (x[1], x[0]))


def metric_drills():
    """Commonly stocked metric drills in mm (ISO 235 style steps)."""
    s = set()
    for i in range(30, 301):                # 0.30 .. 3.00 in 0.05 steps below 3
        if i % 5 == 0:
            s.add(round(i / 100, 2))
    for i in range(30, 141):                # 3.0 .. 14.0 in 0.1
        s.add(round(i / 10, 1))
    for v in (3.25, 3.75, 4.25, 4.75, 5.25, 5.75, 6.25, 6.75, 7.25, 7.75, 8.25, 8.75,
              9.25, 9.75, 10.25, 10.75, 11.25, 11.75, 12.25, 12.75, 13.25, 13.75):
        s.add(v)
    for i in range(56, 129):                # 14.0 .. 32.0 in 0.25
        s.add(i / 4)
    for i in range(64, 201):                # 32.0 .. 100.0 in 0.5
        s.add(i / 2)
    return sorted(s)


INCH = inch_drills()
METRIC = metric_drills()


def inch_drill(name):
    """Look up an inch drill by name ('#7', 'F', '27/64', '1-5/32')."""
    n = name.strip().rstrip('"')
    if n.startswith('#'):
        return NUMBER[int(n[1:])]
    if n in LETTER:
        return LETTER[n]
    return float(parse_frac(n))


def nearest_inch(d_in):
    return min(INCH, key=lambda x: abs(x[1] - d_in))


def nearest_metric(d_mm):
    return min(METRIC, key=lambda x: abs(x - d_mm))
