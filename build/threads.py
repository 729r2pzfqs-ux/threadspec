"""Thread data for ThreadSpec.org: the single source of truth.

Diameters of 60 degree threads (ISO metric, Unified) are computed from the
profile formulas. Everything that is a convention or a tabulated value (tap
drills, pipe thread tables, strength classes, clearance holes) is stored
explicitly with the source it was checked against. See BUILD.md.
"""
import math
from fractions import Fraction

import drills
import tables

IN = 25.4
K_D2 = 0.649519      # 2 * 3H/8
K_D1 = 1.082532      # 2 * 5H/8
K_D3 = 1.226869      # 2 * 17H/24, ISO metric external root
K_D3_UNR = 1.190785  # 2 * 11H/16, ASME B1.1 UNR external root
K_H = 0.866025
PCT = 1.299038       # 2 * 0.75 H: the "100 % thread" double depth used for tap drills


def pct_thread(d, drill, p):
    """Percentage of thread for a tap drill, conventional definition."""
    return (d - drill) / (PCT * p) * 100


# ---------------------------------------------------------------- ISO metric

# ISO 261 coarse pitches with choice (1st / 2nd / 3rd preference).
COARSE = [
    (1, .25, 1), (1.2, .25, 1), (1.4, .3, 2), (1.6, .35, 1), (1.8, .35, 2), (2, .4, 1),
    (2.5, .45, 1), (3, .5, 1), (3.5, .6, 2), (4, .7, 1), (5, .8, 1), (6, 1, 1), (7, 1, 2),
    (8, 1.25, 1), (9, 1.25, 3), (10, 1.5, 1), (12, 1.75, 1), (14, 2, 2), (16, 2, 1),
    (18, 2.5, 2), (20, 2.5, 1), (22, 2.5, 2), (24, 3, 1), (27, 3, 2), (30, 3.5, 1),
    (33, 3.5, 2), (36, 4, 1), (39, 4, 2), (42, 4.5, 1), (45, 4.5, 2), (48, 5, 1),
    (52, 5, 2), (56, 5.5, 1), (60, 5.5, 2), (64, 6, 1), (68, 6, 2),
]
CHOICE = {d: c for d, _, c in COARSE}

FINE = [
    (3, .35), (4, .5), (5, .5), (6, .75), (7, .75), (8, .75), (8, 1), (9, 1),
    (10, .75), (10, 1), (10, 1.25), (12, 1), (12, 1.25), (12, 1.5),
    (14, 1), (14, 1.25), (14, 1.5), (16, 1), (16, 1.25), (16, 1.5),
    (18, 1), (18, 1.5), (18, 2), (20, 1), (20, 1.5), (20, 2), (22, 1), (22, 1.5), (22, 2),
    (24, 1), (24, 1.5), (24, 2), (27, 1), (27, 1.5), (27, 2), (30, 1), (30, 1.5), (30, 2),
    (33, 1.5), (33, 2), (33, 3), (36, 1.5), (36, 2), (36, 3), (39, 1.5), (39, 2), (39, 3),
    (42, 1.5), (42, 2), (42, 3), (45, 1.5), (45, 2), (45, 3), (48, 1.5), (48, 2), (48, 3),
]
# Status notes from ISO 261 Table 2.
FINE_NOTE = {
    (14, 1.25): 'ISO 261 lists M14×1.25 for spark plugs only.',
    (33, 3): 'ISO 261 lists M33×3 in parentheses: a pitch to be avoided where possible.',
    (16, 1.25): 'M16×1.25 is not listed in ISO 261. The dimensions below follow from the '
                'ISO 68-1 profile, but taps, dies and fasteners in this pitch are special order. '
                'The standard fine pitches for M16 are 1.5 and 1 mm.',
}

# Tap drills (mm). Coarse: values printed in tap drill tables based on ISO 2306 / DIN 336.
DRILL_COARSE = {
    1: .75, 1.2: .95, 1.4: 1.1, 1.6: 1.25, 1.8: 1.45, 2: 1.6, 2.5: 2.05, 3: 2.5, 3.5: 2.9,
    4: 3.3, 5: 4.2, 6: 5, 7: 6, 8: 6.8, 9: 7.8, 10: 8.5, 12: 10.2, 14: 12, 16: 14, 18: 15.5,
    20: 17.5, 22: 19.5, 24: 21, 27: 24, 30: 26.5, 33: 29.5, 36: 32, 39: 35, 42: 37.5,
    45: 40.5, 48: 43, 52: 47, 56: 50.5, 60: 54.5, 64: 58, 68: 62,
}
# Fine: d - P. For 0.75 and 1.25 mm pitches published tables round to 0.1 mm.
DRILL_FINE_ROUNDED = {
    (6, .75): 5.2, (7, .75): 6.2, (8, .75): 7.2, (10, .75): 9.2,
    (10, 1.25): 8.8, (12, 1.25): 10.8, (14, 1.25): 12.8, (16, 1.25): 14.8,
}


def fmt_pitch(p):
    s = f"{p:g}"
    return s


def metric_name(d, p):
    return f"M{d:g}×{p:g}"


def metric_slug(d, p, fine):
    if not fine:
        return f"m{d:g}"
    ps = f"{p:.2f}".rstrip('0')
    if ps.endswith('.'):
        ps += '0'
    return f"m{d:g}x{ps.replace('.', '-')}"


def make_metric(d, p, fine):
    t = {
        'system': 'metric', 'family': 'metric-fine' if fine else 'metric',
        'unit': 'mm', 'd': float(d), 'p': float(p), 'tpi': IN / p,
        'name': metric_name(d, p), 'short': f"M{d:g}" if not fine else metric_name(d, p),
        'slug': metric_slug(d, p, fine), 'size_key': float(d),
        'series': 'ISO metric fine pitch' if fine else 'ISO metric coarse pitch',
        'standard': 'ISO 724', 'choice': CHOICE.get(d),
        'note': FINE_NOTE.get((d, p)) if fine else None,
    }
    t['url'] = f"/{t['family']}/{t['slug']}/"
    geom(t)
    if fine:
        exact = round(d - p, 3)
        drill = DRILL_FINE_ROUNDED.get((d, p), exact)
        t['drill_exact'] = exact
    else:
        drill = DRILL_COARSE[d]
        t['drill_exact'] = round(d - p, 3)
    t['drill_mm'] = drill
    t['drill_in'] = drill / IN
    t['drill_name'] = f"{fmt_mm(drill)} mm"
    t['drill_pct'] = pct_thread(d, drill, p)
    t['as_pub'] = tables.AS_ISO898.get((d, p))
    t['tol'] = tables.iso965(d, p)
    t['in_898'] = (1.6 <= d <= 39) if not fine else ((d, p) in tables.AS_ISO898)
    t['clear'] = tables.ISO273.get(d)
    return t


def geom(t):
    d, p = t['d'], t['p']
    t['H'] = K_H * p
    t['d2'] = d - K_D2 * p
    t['d1'] = d - K_D1 * p          # D1, internal minor diameter
    t['h_int'] = 0.541266 * p       # 5H/8
    if t['system'] == 'metric':
        t['d3'] = d - K_D3 * p      # ISO 724:2023 d3, rounded root, h3 = 17H/24
        t['h_ext'] = 0.613435 * p
    else:
        t['d3'] = d - K_D3_UNR * p  # ASME B1.1 UNR root, hs = 11H/16
        t['h_ext'] = 0.595392 * p
    t['crest'] = p / 8
    t['root_flat'] = p / 4
    t['lead'] = math.degrees(math.atan(p / (math.pi * t['d2'])))
    if t['system'] == 'metric':
        t['As'] = math.pi / 4 * ((t['d2'] + t['d3']) / 2) ** 2
    else:
        t['As'] = 0.7854 * (d - 0.9743 * p) ** 2
    t['A_minor'] = math.pi / 4 * t['d3'] ** 2


def fmt_mm(v, nd=None):
    """Drill style mm formatting: 6.8, 5, 10.25, 0.75."""
    if nd is not None:
        return f"{v:.{nd}f}"
    s = f"{v:.2f}".rstrip('0').rstrip('.')
    return s


# ---------------------------------------------------------------- Unified inch

NUM_DIA = {0: .060, 1: .073, 2: .086, 3: .099, 4: .112, 5: .125, 6: .138, 8: .164, 10: .190, 12: .216}


def un_size(label):
    """'#10' -> 0.190, '1-1/4' -> 1.25."""
    if label.startswith('#'):
        return NUM_DIA[int(label[1:])]
    return float(drills.parse_frac(label))


def un_slug(label, fam):
    s = label.replace('#', 'num-').replace('/', '-')
    return f"{s}-{fam}"


def make_un(label, tpi, fam):
    d = un_size(label)
    p = 1 / tpi
    t = {
        'system': 'inch', 'family': fam, 'unit': 'in', 'd': d, 'p': p, 'tpi': tpi,
        'label': label, 'name': f"{label}-{tpi:g} {fam.upper()}", 'short': f"{label}-{tpi:g}",
        'slug': un_slug(label, fam), 'size_key': d * IN,
        'series': {'unc': 'Unified coarse (UNC)', 'unf': 'Unified fine (UNF)',
                   'unef': 'Unified extra fine (UNEF)'}[fam],
        'standard': 'ASME B1.1', 'note': None,
    }
    t['url'] = f"/{fam}/{t['slug']}/"
    geom(t)
    name = tables.UN_DRILL[(label, tpi)]
    t['drill_name'] = drill_label(name)
    t['drill_basis'] = tables.UN_DRILL_BASIS.get((label, tpi), 'chart')
    t['as_pub'] = tables.AS_B11.get((label, tpi))
    t['secondary'] = label in tables.UN_SECONDARY
    t['drill_in'] = drills.inch_drill(name)
    t['drill_mm'] = t['drill_in'] * IN
    t['drill_pct'] = pct_thread(d, t['drill_in'], p)
    t['limits'] = tables.UN_LIMITS.get((label, tpi))
    t['clear'] = tables.B18_2_8.get(label)
    return t


# ---------------------------------------------------------------- build lists

def build():
    fams = {
        'metric': [make_metric(d, p, False) for d, p, _ in COARSE],
        'metric-fine': [make_metric(d, p, True) for d, p in FINE],
        'unc': [make_un(l, n, 'unc') for l, n in tables.UNC],
        'unf': [make_un(l, n, 'unf') for l, n in tables.UNF],
        'unef': [make_un(l, n, 'unef') for l, n in tables.UNEF],
        'npt': [make_npt(r) for r in tables.NPT],
        'bsp': [make_bsp(r) for r in tables.BSP],
    }
    return fams


# ---------------------------------------------------------------- pipe threads

def pipe_slug(label):
    return label.replace('/', '-')


def drill_label(name):
    return name if name[0] in '#ABCDEFGHIJKLMNOPQRSTUVWXYZ' else name + '"'


def make_npt(r):
    label, tpi = r['label'], r['tpi']
    p = 1 / tpi
    t = dict(r)
    t.update({
        'system': 'npt', 'family': 'npt', 'unit': 'in', 'p': p,
        'name': f'{label}" NPT', 'short': f'{label} NPT', 'plain': f'{label}-{tpi:g} NPT',
        'slug': pipe_slug(label) + '-npt', 'size_key': r['D'],
        'h': 0.8 * p, 'H': K_H * p, 'turns': r['L1'] / p, 'threads_eff': r['L2'] / p,
        'standard': 'ASME B1.20.1',
    })
    t['url'] = f"/npt/{t['slug']}/"
    for k in ('std', 'ream', 'common'):
        n = r['drill_' + k]
        t[k] = None if n is None else {'name': drill_label(n), 'in': drills.inch_drill(n),
                                       'mm': drills.inch_drill(n) * IN}
    t['main'] = t['std'] or t['common']
    return t


def make_bsp(r):
    label, tpi, d, drill = r
    p = IN / tpi
    in_iso = label not in tables.BSP_NOT_IN_ISO228
    h = 0.640327 * p
    t = {
        'system': 'bsp', 'family': 'bsp', 'unit': 'mm', 'label': label, 'tpi': tpi, 'p': p,
        'name': f'G{label}', 'short': f'G{label}', 'slug': 'g' + pipe_slug(label) + '-bsp',
        'size_key': d, 'd': d, 'h': h, 'd2': d - h, 'd1': d - 2 * h,
        'r': 0.137329 * p, 'H': 0.960491 * p,
        'drill_mm': drill, 'drill_in': drill / IN, 'drill_name': f"{fmt_mm(drill)} mm",
        'standard': 'ISO 228-1', 'in_iso': in_iso,
    }
    t['url'] = f"/bsp/{t['slug']}/"
    return t
