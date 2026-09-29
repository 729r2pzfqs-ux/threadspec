"""Inline SVG diagrams, drawn from the thread data. Styling lives in assets/site.css (.dg)."""
import math
from html import escape

T30 = math.tan(math.radians(30))


def f(v):
    """Compact coordinate formatting."""
    s = f"{v:.1f}"
    return s[:-2] if s.endswith('.0') else s


def pts(points):
    return ' '.join(f"{f(x)},{f(y)}" for x, y in points)


def text(x, y, s, cls='', anchor='start', rot=None):
    a = f' text-anchor="{anchor}"' if anchor != 'start' else ''
    c = f' class="{cls}"' if cls else ''
    r = f' transform="rotate({rot} {f(x)} {f(y)})"' if rot is not None else ''
    return f'<text x="{f(x)}" y="{f(y)}"{a}{c}{r}>{escape(s)}</text>'


def line(x1, y1, x2, y2, cls):
    return f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" class="{cls}"/>'


def arrow(x, y, direction):
    """Small solid arrowhead with its tip at (x, y)."""
    a, b = 7, 2.6
    p = {'l': [(x, y), (x + a, y - b), (x + a, y + b)],
         'r': [(x, y), (x - a, y - b), (x - a, y + b)],
         'u': [(x, y), (x - b, y + a), (x + b, y + a)],
         'd': [(x, y), (x - b, y - a), (x + b, y - a)]}[direction]
    return f'<polygon points="{pts(p)}" class="fill-ink"/>'


def dim_h(x1, x2, y, label, ty=None, cls=''):
    """Horizontal dimension with arrows; arrows flip outside when the span is short."""
    out = []
    if x2 - x1 >= 22:
        out += [line(x1, y, x2, y, 'dim'), arrow(x1, y, 'l'), arrow(x2, y, 'r')]
    else:
        out += [line(x1 - 14, y, x2 + 14, y, 'dim'), arrow(x1, y, 'r'), arrow(x2, y, 'l')]
    out.append(text((x1 + x2) / 2, y - 5 if ty is None else ty, label, cls, 'middle'))
    return ''.join(out)


def dim_v(x, y1, y2, label=None, tx=None, anchor='start', cls=''):
    out = []
    if y2 - y1 >= 22:
        out += [line(x, y1, x, y2, 'dim'), arrow(x, y1, 'u'), arrow(x, y2, 'd')]
    else:
        out += [line(x, y1 - 14, x, y2 + 14, 'dim'), arrow(x, y1, 'd'), arrow(x, y2, 'u')]
    if label:
        out.append(text(x + 6 if tx is None else tx, (y1 + y2) / 2 + 4, label, cls, anchor))
    return ''.join(out)


def svg(w, h, label, body):
    return (f'<svg class="dg" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label, quote=True)}" '
            f'xmlns="http://www.w3.org/2000/svg">{body}</svg>')


def figure(svg_code, caption, cls=''):
    c = f' class="{cls}"' if cls else ''
    return f'<figure{c}>{svg_code}<figcaption>{caption}</figcaption></figure>'


# ------------------------------------------------------------------ 60 degree outline

def v_outline(x0, x1, y_crest, p, depth, crest, phase=0.0, down=True):
    """Truncated 60 degree thread outline from x0 to x1.

    Crests sit on y_crest, roots `depth` away (below when down=True). `phase`
    shifts the pattern along x as a fraction of the pitch. Returns points that
    may run slightly past x0/x1; callers clip.
    """
    run = depth * T30
    root = p - crest - 2 * run
    sgn = 1 if down else -1
    start = x0 - p + (phase % 1.0) * p - crest / 2
    out = []
    x = start
    while x < x1 + p:
        out += [(x, y_crest), (x + crest, y_crest),
                (x + crest + run, y_crest + sgn * depth),
                (x + crest + run + root, y_crest + sgn * depth)]
        x += p
    return out


# ------------------------------------------------------------------ 1. to-scale side view

def scale_view(name, d, p, h_ext, unit, fmt, uid):
    """External thread drawn to scale: diameter against pitch."""
    W, Hh = 380, 214
    x0, x1, yc, dia_px = 16, 300, 96, 124
    s = dia_px / d
    pp = p * s
    depth = h_ext * s
    crest = pp / 8
    top_y = yc - dia_px / 2
    bot_y = yc + dia_px / 2
    top = v_outline(x0, x1, top_y, pp, depth, crest, phase=0.0, down=True)
    bot = v_outline(x0, x1, bot_y, pp, depth, crest, phase=0.5, down=False)
    body = [f'<clipPath id="{uid}"><rect x="{x0}" y="0" width="{x1 - x0}" height="{Hh}"/></clipPath>',
            f'<g clip-path="url(#{uid})">',
            f'<polygon points="{pts(top + bot[::-1])}" class="metal"/>']
    # crest and root lines across the body: a half-pitch advance over half a turn
    run = depth * T30
    n = 0
    x = x0 - 2 * pp
    while x < x1 + pp:
        a = x - crest / 2
        if pp >= 12:
            body.append(line(a, top_y, a + pp / 2, bot_y, 'edge'))
            body.append(line(a + crest, top_y, a + crest + pp / 2, bot_y, 'edge'))
        else:
            body.append(line(x, top_y, x + pp / 2, bot_y, 'edge-l' if pp < 6 else 'edge'))
        if pp >= 7:
            rx = x + pp / 2
            body.append(line(rx, top_y + depth, rx + pp / 2, bot_y - depth, 'edge-l'))
        x += pp
        n += 1
    body.append('</g>')
    body.append(line(x0, top_y, x0, bot_y, 'edge'))
    body.append(line(x1, top_y, x1, bot_y, 'edge'))
    body.append(line(4, yc, x1 + 8, yc, 'cl'))
    # major diameter
    body.append(line(x1 + 2, top_y, 322, top_y, 'ext'))
    body.append(line(x1 + 2, bot_y, 322, bot_y, 'ext'))
    body.append(dim_v(314, top_y, bot_y))
    body.append(text(322, yc - 6, 'major Ø', 't-s t-m'))
    body.append(text(322, yc + 9, fmt(d), 't-b'))
    # pitch count
    npit = 10 if 10 * pp <= 250 else (5 if 5 * pp <= 250 else 1)
    a = x0 + pp            # first full crest centre inside the view
    b = a + npit * pp
    yd = bot_y + 22
    body.append(line(a, bot_y + 3, a, yd + 5, 'ext'))
    body.append(line(b, bot_y + 3, b, yd + 5, 'ext'))
    lbl = (f"{npit} threads = {fmt(npit * p)}" if npit > 1 else f"1 thread = {fmt(p)}")
    body.append(dim_h(a, b, yd, lbl, ty=yd + 16))
    shown = (x1 - x0) / s
    label = (f"{name} external thread drawn to scale: major diameter {fmt(d)}, "
             f"{shown / p:.0f} threads in the length shown.")
    return svg(W, Hh, label, ''.join(body))


# ------------------------------------------------------------------ 2. basic profile with values

def profile_view(name, labels, aria):
    """ISO 68-1 / ASME B1.1 basic profile, nut above bolt, with caller-supplied labels.

    labels: dict with keys p, maj, pit, min (each a (line1, line2) pair or str), h, angle.
    """
    W, Hh = 390, 232
    P = 116.0
    H = P * 0.866025
    xa, xb = 34, 284
    y_maj = 72.0
    y_min = y_maj + 0.625 * H
    y_pit = y_maj + 0.375 * H
    out = v_outline(xa, xb, y_maj, P, 0.625 * H, P / 8, phase=0.42, down=True)
    uid = 'cp-prof'
    body = [f'<clipPath id="{uid}"><rect x="{xa}" y="0" width="{xb - xa}" height="{Hh}"/></clipPath>',
            f'<g clip-path="url(#{uid})">',
            f'<polygon points="{pts([(xa - P, 34)] + out + [(xb + P, 34)])}" class="nut"/>',
            f'<polygon points="{pts([(xa - P, 196)] + out + [(xb + P, 196)])}" class="metal"/>',
            '</g>']
    # crest centres of the bolt inside the window
    start = xa - P + 0.42 * P
    crests = [start + k * P for k in range(4) if xa + 8 < start + k * P < xb - 8]
    c1 = crests[0]
    c2 = c1 + P
    # sharp V apex above first full groove for the angle
    gx = c1 + P / 2
    body.append(text(gx, y_maj + 27, labels.get('angle', '60°'), 't-b', 'middle'))
    body.append(text(xa + 8, 50, labels.get('nut', 'Nut (internal thread)'), 't-s'))
    body.append(text(xa + 8, 186, labels.get('bolt', 'Bolt (external thread)'), 't-s'))
    # pitch
    body.append(line(c1, y_maj - 3, c1, 14, 'ext'))
    body.append(line(c2, y_maj - 3, c2, 14, 'ext'))
    body.append(dim_h(c1, c2, 22, labels['p'], ty=17))
    # diameters to the right
    for y, key, cls in ((y_maj, 'maj', 'ext'), (y_pit, 'pit', 'ref'), (y_min, 'min', 'ext')):
        body.append(line(xa if key == 'pit' else xb, y, xb + 12, y, cls))
        l1, l2 = labels[key]
        off = {'maj': -9, 'pit': 0, 'min': 9}[key]
        body.append(text(xb + 16, y - 2 + off, l1, 't-s t-m'))
        body.append(text(xb + 16, y + 11 + off, l2, 't-b'))
    # thread height on the left
    body.append(line(xa - 2, y_maj, 12, y_maj, 'ext'))
    body.append(line(xa - 2, y_min, 12, y_min, 'ext'))
    body.append(dim_v(20, y_maj, y_min))
    body.append(text(14, (y_maj + y_min) / 2, labels['h'], 't-s', 'middle', rot=-90))
    # axis hint
    body.append(line(xa - 10, 214, xb + 10, 214, 'cl'))
    body.append(text(xb + 16, 218, labels.get('axis', 'thread axis'), 't-s t-m'))
    return svg(W, Hh, aria, ''.join(body))


# ------------------------------------------------------------------ 3. pitch comparison

def pitch_compare(rows, fmt_depth):
    """rows: list of (name, p, depth, current). Same diameter, same scale."""
    pmax = max(r[1] for r in rows)
    s = 64.0 / pmax
    xa, xb = 118, 370
    row_h = max(44, 0.62 * pmax * s + 20)
    Hh = int(14 + row_h * len(rows))
    body = [f'<clipPath id="cp-cmp"><rect x="{xa}" y="0" width="{xb - xa}" height="{Hh}"/></clipPath>']
    y = 14.0
    for name, p, depth, cur in rows:
        pp = p * s
        out = v_outline(xa, xb, y, pp, depth * s, pp / 8, phase=0.5, down=True)
        base = y + row_h - 12
        poly = [(xa - pp * 2, base)] + out + [(xb + pp * 2, base)]
        body.append(f'<g clip-path="url(#cp-cmp)"><polygon points="{pts(poly)}" class="metal"/>')
        if cur:
            body.append(f'<polyline points="{pts(out)}" class="hl"/>')
        body.append('</g>')
        body.append(text(4, y + 13, name, 't-br' if cur else 't-b'))
        body.append(text(4, y + 28, f"depth {fmt_depth(depth)}", 't-s t-m'))
        y += row_h
    names = ', '.join(r[0] for r in rows)
    return svg(380, Hh, f"Thread profiles of {names} drawn to the same scale, crests aligned.", ''.join(body))


# ------------------------------------------------------------------ 4. NPT taper

def npt_view(t, fmt):
    W, Hh = 400, 256
    x0, L2px = 46, 236
    n = t['L2'] / t['p']
    pp = L2px / n
    hp = 0.8 * pp
    rise = 34.0                       # exaggerated taper across L2
    slope = rise / L2px
    yE0 = 150.0

    def ypl(x):
        return yE0 - (x - x0) * slope

    xE1 = x0 + L2px * t['L1'] / t['L2']
    xE2 = x0 + L2px
    xend = 372
    # thread outline on the taper, fading into the pipe OD after E2
    top = []
    x = x0
    k = 0
    run = hp * T30
    crest = (pp - 2 * run) / 2
    while x < xE2 + 2.2 * pp:
        fade = 1.0 if x < xE2 else max(0.0, 1 - (x - xE2) / (2.2 * pp))
        yc = ypl(x + crest / 2) - hp / 2
        if x >= xE2:
            yc = ypl(xE2) - hp / 2   # crests run out onto the pipe OD
        yr = yc + hp * fade
        top += [(x, yc), (x + crest, yc), (x + crest + run, yr), (x + crest + run + crest, yr)]
        x += pp
        k += 1
    y_od = ypl(xE2) - hp / 2
    bore = 184.0
    poly = [(x0, bore)] + top + [(xend, y_od), (xend, bore)]
    body = [f'<polygon points="{pts(poly)}" class="metal"/>',
            line(30, 232, xend + 8, 232, 'cl'),
            text(xend + 8, 248, 'pipe axis', 't-s t-m', 'end'),
            line(x0, ypl(x0), xE2 + 14, ypl(xE2 + 14), 'ref')]
    for xx, lab, val in ((x0, 'E0', t['E0']), (xE1, 'E1', t['E1']), (xE2, 'E2', t['E2'])):
        body.append(line(xx, 40, xx, 222, 'ext'))
        body.append(f'<circle cx="{f(xx)}" cy="{f(ypl(xx))}" r="3.5" class="fill-br"/>')
        body.append(text(xx + 4, 202, lab, 't-br'))
        body.append(text(xx + 4, 216, fmt(val), 't-s'))
    body.append(dim_h(x0, xE1, 66, f"L1 = {fmt(t['L1'], 4)}", ty=61))
    body.append(dim_h(x0, xE2, 40, f"L2 = {fmt(t['L2'], 4)}", ty=35))
    body.append(text(xE1 + 5, 84, 'hand-tight', 't-s t-m'))
    body.append(text(xE1 + 5, 96, 'plane', 't-s t-m'))
    body.append(text(xend, y_od - 20, f"OD {fmt(t['D'], 3)}", 't-b', 'end'))
    body.append(line(xend - 20, y_od - 16, xend - 20, y_od, 'ext'))
    body.append(text(x0, 20, 'Taper 1 in 16 on diameter (1°47′ per side), exaggerated here', 't-s t-m'))
    aria = (f"{t['name']} external taper thread: pitch diameter {fmt(t['E0'])} at the pipe end (E0), "
            f"{fmt(t['E1'])} at the hand-tight plane (E1) and {fmt(t['E2'])} at the end of the "
            f"effective thread (E2).")
    return svg(W, Hh, aria, ''.join(body))


# ------------------------------------------------------------------ 5. Whitworth profile

def whitworth_path(xa, xb, y_crest, P, phase):
    """55 degree Whitworth outline with rounded crests and roots as an SVG path."""
    h = 0.640327 * P
    r = 0.137329 * P
    tv = 0.073917 * P          # vertical distance from crest (or root) to the tangent point
    th = 0.121819 * P          # horizontal half width at the tangent point
    y_root = y_crest + h
    x = xa - 2 * P + phase * P
    d = [f"M{f(x - th)},{f(y_crest + tv)}"]
    while x < xb + P:
        d.append(f"A{f(r)},{f(r)} 0 0 1 {f(x + th)},{f(y_crest + tv)}")
        d.append(f"L{f(x + P / 2 - th)},{f(y_root - tv)}")
        d.append(f"A{f(r)},{f(r)} 0 0 0 {f(x + P / 2 + th)},{f(y_root - tv)}")
        d.append(f"L{f(x + P - th)},{f(y_crest + tv)}")
        x += P
    return ' '.join(d), x


def bsp_view(labels, aria):
    W, Hh = 390, 232
    P = 116.0
    h = 0.640327 * P
    xa, xb = 34, 284
    y_maj = 70.0
    y_min = y_maj + h
    y_pit = y_maj + h / 2
    d, xe = whitworth_path(xa, xb, y_maj, P, 0.42)
    start = xa - 2 * P + 0.42 * P
    nut = f'M{f(start - 0.121819 * P)},34 L' + d[1:] + f' L{f(xe)},34 Z'
    bolt = f'M{f(start - 0.121819 * P)},196 L' + d[1:] + f' L{f(xe)},196 Z'
    body = [f'<clipPath id="cp-w"><rect x="{xa}" y="0" width="{xb - xa}" height="{Hh}"/></clipPath>',
            '<g clip-path="url(#cp-w)">',
            f'<path d="{nut}" class="nut"/>', f'<path d="{bolt}" class="metal"/>', '</g>']
    crests = [start + k * P for k in range(5) if xa + 8 < start + k * P < xb - 8]
    c1 = crests[0]
    c2 = c1 + P
    body.append(text(c1 + P / 2, y_maj + 30, '55°', 't-b', 'middle'))
    body.append(text(xa + 8, 50, labels.get('nut', 'Internal thread (port)'), 't-s'))
    body.append(text(xa + 8, 186, labels.get('bolt', 'External thread (fitting)'), 't-s'))
    body.append(line(c1, y_maj - 3, c1, 14, 'ext'))
    body.append(line(c2, y_maj - 3, c2, 14, 'ext'))
    body.append(dim_h(c1, c2, 22, labels['p'], ty=17))
    for y, key, cls in ((y_maj, 'maj', 'ext'), (y_pit, 'pit', 'ref'), (y_min, 'min', 'ext')):
        body.append(line(xa if key == 'pit' else xb, y, xb + 12, y, cls))
        l1, l2 = labels[key]
        off = {'maj': -9, 'pit': 0, 'min': 9}[key]
        body.append(text(xb + 16, y - 2 + off, l1, 't-s t-m'))
        body.append(text(xb + 16, y + 11 + off, l2, 't-b'))
    body.append(line(xa - 2, y_maj, 12, y_maj, 'ext'))
    body.append(line(xa - 2, y_min, 12, y_min, 'ext'))
    body.append(dim_v(20, y_maj, y_min))
    body.append(text(14, (y_maj + y_min) / 2, labels['h'], 't-s', 'middle', rot=-90))
    if labels.get('r'):
        body.append(text(c2 + P / 2, y_maj - 6, labels['r'], 't-s', 'middle'))
    body.append(line(xa - 10, 214, xb + 10, 214, 'cl'))
    body.append(text(xb + 16, 218, 'thread axis', 't-s t-m'))
    return svg(W, Hh, aria, ''.join(body))


# ------------------------------------------------------------------ 6. NPT vs BSP

def form_compare():
    """60 degree flat-truncated NPT form next to the 55 degree rounded Whitworth form."""
    W, Hh = 400, 190
    P = 84.0
    body = ['<clipPath id="cp-f1"><rect x="14" y="0" width="176" height="190"/></clipPath>',
            '<clipPath id="cp-f2"><rect x="210" y="0" width="176" height="190"/></clipPath>']
    # NPT: h = 0.8P, flats 0.038P
    h = 0.8 * P
    run = h * T30
    crest = (P - 2 * run) / 2
    out = []
    x = 14 - P + 8
    while x < 190 + P:
        out += [(x, 60), (x + crest, 60), (x + crest + run, 60 + h), (x + crest + run + crest, 60 + h)]
        x += P
    body.append(f'<g clip-path="url(#cp-f1)"><polygon points="{pts([(0, 150)] + out + [(260, 150)])}" class="metal"/></g>')
    body.append(text(102, 22, 'NPT', 't-b', 'middle'))
    body.append(text(102, 38, '60° flanks, flat crests and roots', 't-s t-m', 'middle'))
    body.append(text(102, 168, 'thread height 0.8 × pitch', 't-s', 'middle'))
    body.append(text(102, 183, 'cut on a 1 in 16 taper', 't-s', 'middle'))
    d, xe = whitworth_path(210, 386, 60 + (h - 0.640327 * P) / 2, P, 0.3)
    body.append(f'<g clip-path="url(#cp-f2)"><path d="M120,150 L{d[1:]} L{f(xe)},150 Z" class="metal"/></g>')
    body.append(text(298, 22, 'BSP (G, R, Rc, Rp)', 't-b', 'middle'))
    body.append(text(298, 38, '55° flanks, rounded crests and roots', 't-s t-m', 'middle'))
    body.append(text(298, 168, 'thread height 0.64 × pitch', 't-s', 'middle'))
    body.append(text(298, 183, 'G is parallel, R is tapered', 't-s', 'middle'))
    body.append(line(200, 10, 200, 186, 'ext'))
    return svg(W, Hh, 'NPT thread form with 60 degree flanks and flat crests beside the BSP Whitworth form '
                      'with 55 degree flanks and rounded crests, at the same pitch.', ''.join(body))


def seal_compare():
    """Where each joint seals: on the threads (NPT, R) or on a face seal (G)."""
    W, Hh = 400, 214
    b = ['<clipPath id="cp-s1"><rect x="0" y="0" width="196" height="214"/></clipPath>']
    # left: taper joint, upper half section
    b.append(text(100, 18, 'NPT: seals on the thread', 't-b', 'middle'))
    b.append(f'<polygon points="{pts([(20, 60), (180, 60), (180, 118), (150, 124), (60, 140), (20, 140)])}" class="nut"/>')
    b.append(f'<polygon points="{pts([(60, 140), (150, 124), (190, 124), (190, 176), (60, 176)])}" class="metal"/>')
    b.append(f'<polyline points="{pts([(62, 139.6), (148, 124.4)])}" class="hl2"/>')
    b.append(line(14, 190, 194, 190, 'cl'))
    b.append(text(26, 78, 'female port', 't-s'))
    b.append(text(120, 166, 'male pipe', 't-s'))
    b.append(text(100, 206, 'sealant fills the thread gap', 't-s t-m', 'middle'))
    # right: parallel joint with bonded washer
    b.append(text(302, 18, 'BSP G: seals on a washer', 't-b', 'middle'))
    b.append(f'<polygon points="{pts([(250, 60), (386, 60), (386, 132), (250, 132)])}" class="nut"/>')
    b.append(f'<polygon points="{pts([(214, 96), (240, 96), (240, 132), (380, 132), (380, 176), (214, 176)])}" class="metal"/>')
    b.append('<rect x="241" y="100" width="8" height="32" rx="2" class="seal"/>')
    b.append(line(210, 190, 390, 190, 'cl'))
    b.append(text(262, 78, 'female port', 't-s'))
    b.append(text(300, 166, 'male fitting', 't-s'))
    b.append(text(302, 206, 'washer or O-ring seals', 't-s t-m', 'middle'))
    b.append(line(200, 28, 200, 196, 'ext'))
    return svg(W, Hh, 'A tapered NPT joint seals along the wedged thread flanks with sealant, while a parallel '
                      'BSPP joint seals on a bonded washer or O-ring against the port face.', ''.join(b))


# ------------------------------------------------------------------ 7. series plot

def series_plot(series, xlabel, ylabel, aria, ylog=False, xfmt=None, yfmt=None, xticks=None, yticks=None):
    """Scatter of thread series on a log diameter axis.

    series: list of (name, css_class, [(x, y, title), ...], connect)
    """
    W, Hh = 420, 300
    L, R, T, B = 46, 12, 34, 44
    xs = [p[0] for s in series for p in s[2]]
    ys = [p[1] for s in series for p in s[2]]
    x0, x1 = min(xs) * 0.88, max(xs) * 1.12
    y0, y1 = (min(ys) * 0.85, max(ys) * 1.15) if ylog else (0, max(ys) * 1.08)

    def X(v):
        return L + (math.log(v) - math.log(x0)) / (math.log(x1) - math.log(x0)) * (W - L - R)

    def Y(v):
        if ylog:
            return Hh - B - (math.log(v) - math.log(y0)) / (math.log(y1) - math.log(y0)) * (Hh - T - B)
        return Hh - B - (v - y0) / (y1 - y0) * (Hh - T - B)

    b = [f'<rect x="0" y="0" width="{W}" height="{Hh}" class="bg"/>']
    for v in yticks:
        if y0 <= v <= y1:
            b.append(line(L, Y(v), W - R, Y(v), 'grid'))
            b.append(text(L - 6, Y(v) + 4, yfmt(v), 't-s t-m', 'end'))
    for v in xticks:
        if x0 <= v <= x1:
            b.append(line(X(v), Hh - B, X(v), Hh - B + 4, 'axis'))
            b.append(text(X(v), Hh - B + 17, xfmt(v), 't-s t-m', 'middle'))
    b.append(line(L, Hh - B, W - R, Hh - B, 'axis'))
    b.append(text((L + W - R) / 2, Hh - 8, xlabel, 't-s', 'middle'))
    b.append(text(L - 40, T - 14, ylabel, 't-s'))
    lx = L + 120
    for name, cls, pts_, connect in series:
        if connect:
            b.append(f'<polyline points="{pts([(X(x), Y(y)) for x, y, _ in pts_])}" class="l1"/>')
    for i, (name, cls, pts_, connect) in enumerate(series):
        for x, y, title in pts_:
            b.append(f'<circle cx="{f(X(x))}" cy="{f(Y(y))}" r="4" class="{cls}"><title>{escape(title)}</title></circle>')
    if len(series) > 1:
        lx = L + 8
        for name, cls, _, _ in series:
            b.append(f'<circle cx="{lx}" cy="{T - 4}" r="4" class="{cls}"/>')
            b.append(text(lx + 8, T, name, 't-s'))
            lx += 16 + len(name) * 6.4 + 10
    return svg(W, Hh, aria, ''.join(b))
