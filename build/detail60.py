"""Detail pages for 60 degree threads: ISO metric and Unified inch."""
import drills
import svg
import tables
from content import USES
from shell import (IN, bar, chips, e, facts, g, page, sig, spec_table, table, thousands, webpage_ld)
from threads import pct_thread

FAMILY_HUB = {
    'metric': ('/metric/', 'Metric Coarse'), 'metric-fine': ('/metric-fine/', 'Metric Fine'),
    'unc': ('/unc/', 'UNC'), 'unf': ('/unf/', 'UNF'), 'unef': ('/unef/', 'UNEF'),
}
ORD = {1: 'first', 2: 'second', 3: 'third'}


def is_m(t):
    return t['system'] == 'metric'


def nat(t, v, unit=True):
    """Value in the thread's own unit."""
    s = f"{v:.3f}" if is_m(t) else f"{v:.4f}"
    return s + ((' mm' if is_m(t) else ' in') if unit else '')


def alt(t, v, unit=True):
    """Value converted to the other unit."""
    if is_m(t):
        return f"{v / IN:.4f}" + (' in' if unit else '')
    return f"{v * IN:.3f}" + (' mm' if unit else '')


def area(t):
    """(mm2 text, in2 text) for the tensile stress area."""
    if is_m(t):
        if t['as_pub']:
            return f"{g(t['as_pub'], 2)}", f"{sig(t['as_pub'] / 645.16, 3)}"
        return sig(t['As'], 3), f"{sig(t['As'] / 645.16, 3)}"
    a = t['as_pub']
    return f"{sig(a * 645.16, 3)}", in2(a)


def in2(a):
    """Stress area in square inches with the precision ASME B1.1 prints."""
    if a < 0.01:
        return f"{a:.5f}"
    if a < 0.1:
        return f"{a:.4f}"
    s = f"{a:g}"
    if a < 1 and len(s.split('.')[1]) < 3:
        s = f"{a:.3f}"
    return s


def area_native(t):
    mm2, in2 = area(t)
    return (f"{mm2} mm²", f"{in2} in²") if is_m(t) else (f"{in2} in²", f"{mm2} mm²")


def drill_text(t):
    if is_m(t):
        return f"{t['drill_name']}"
    return f"{t['drill_name']} ({t['drill_in']:.4f} in)"


def minor_limits(t):
    """(min, max) internal minor diameter limits in native units, or None."""
    if is_m(t):
        if not t.get('tol'):
            return None
        return t['d1'], t['d1'] + t['tol']['TD1']
    L = t['limits']
    return float(L[5]), float(L[6])


def drill_options(t):
    rec = t['drill_mm'] if is_m(t) else t['drill_in']
    lim = minor_limits(t)
    if is_m(t):
        cands = [(f"{g(v, 2)} mm", v) for v in drills.METRIC]
        if rec not in drills.METRIC:
            cands.append((t['drill_name'], rec))
    else:
        cands = list(drills.INCH)
    out = []
    for name, dia in cands:
        pct = pct_thread(t['d'], dia, t['p'])
        if 50 <= pct <= 92 or abs(dia - rec) < 1e-9:
            out.append({'name': name, 'dia': dia, 'pct': pct, 'rec': abs(dia - rec) < 1e-9, 'x': False})
    out.sort(key=lambda o: abs(o['dia'] - rec))
    out = out[:7]
    # nearest drill from the other system
    if is_m(t):
        n, d_in = drills.nearest_inch(rec / IN)
        dia = d_in * IN
        name = n + f" ({d_in:.4f} in)"
    else:
        v = drills.nearest_metric(rec * IN)
        dia = v / IN
        name = f"{g(v, 2)} mm"
    pct = pct_thread(t['d'], dia, t['p'])
    if 45 <= pct <= 95:
        out.append({'name': name, 'dia': dia, 'pct': pct, 'rec': False, 'x': True})
    out.sort(key=lambda o: o['dia'])
    for o in out:
        o['within'] = None if lim is None else (lim[0] - 1e-9 <= o['dia'] <= lim[1] + 1e-9)
        o['mm'] = o['dia'] if is_m(t) else o['dia'] * IN
        o['in'] = o['dia'] / IN if is_m(t) else o['dia']
    return out


def siblings(t, fams):
    """Threads of the same nominal diameter across the 60 degree families of the same system."""
    keys = ('metric', 'metric-fine') if is_m(t) else ('unc', 'unf', 'unef')
    out = [x for k in keys for x in fams[k] if abs(x['d'] - t['d']) < 1e-9]
    return sorted(out, key=lambda x: -x['p'])


def nearest_other(t, fams):
    keys = ('unc', 'unf', 'unef') if is_m(t) else ('metric', 'metric-fine')
    dmm = t['d'] * (1 if is_m(t) else IN)
    pmm = t['p'] * (1 if is_m(t) else IN)
    best = []
    for k in keys:
        for x in fams[k]:
            xd = x['d'] * (1 if is_m(x) else IN)
            xp = x['p'] * (1 if is_m(x) else IN)
            if abs(xd - dmm) / dmm <= 0.06:
                best.append((abs(xd - dmm) / dmm + 0.25 * abs(xp - pmm) / pmm, x, xd, xp))
    best.sort(key=lambda b: b[0])
    return [(x, xd, xp) for _, x, xd, xp in best[:3]], dmm, pmm


def lead_text(t, fams):
    sib = siblings(t, fams)
    others = [x for x in sib if x is not t]
    d, p = t['d'], t['p']
    if t['family'] == 'metric':
        s = (f"{t['name']} is the ISO metric coarse thread for {g(d)} mm fasteners, which is why it is "
             f"usually written simply as M{g(d)}. It has a 60° profile with a pitch of {g(p)} mm "
             f"({t['tpi']:.1f} threads per inch).")
        if t['choice']:
            s += f" ISO 261 lists M{g(d)} as a {ORD[t['choice']]}-choice diameter."
        if others:
            s += (" Fine-pitch versions of the same diameter are "
                  + join_links(others) + ".")
        return s
    if t['family'] == 'metric-fine':
        c = next((x for x in fams['metric'] if abs(x['d'] - d) < 1e-9), None)
        s = (f"{t['name']} is an ISO metric fine-pitch thread: the {g(d)} mm diameter with a "
             f"{g(p)} mm pitch ({t['tpi']:.1f} threads per inch)")
        if c:
            gain = (t['As'] / c['As'] - 1) * 100
            s += (f" instead of the coarse {g(c['p'])} mm of <a href=\"{c['url']}\">{c['name']}</a>. "
                  f"The thread is {c['h_int'] - t['h_int']:.2f} mm shallower, so the tensile stress area "
                  f"rises from {area(c)[0]} to {area(t)[0]} mm² ({gain:.0f}% more) and the lead angle "
                  f"falls from {c['lead']:.2f}° to {t['lead']:.2f}°.")
        else:
            s += '.'
        return s
    fam = t['family']
    kind = {'unc': 'coarse', 'unf': 'fine', 'unef': 'extra fine'}[fam]
    lab = t['label']
    size = (f"number {lab[1:]} size (major diameter {d:.3f} in, {d * IN:.2f} mm)" if lab.startswith('#')
            else f"{lab} in ({d * IN:.2f} mm) diameter")
    s = (f"{t['name']} is the Unified {kind} thread for the {size}: {g(t['tpi'])} threads per inch, "
         f"a pitch of {p:.5f} in ({p * IN:.3f} mm), on a 60° profile. ASME B1.1 lists it in the "
         f"{fam.upper()} series{' as a secondary size' if t['secondary'] else ''}.")
    c = next((x for x in fams['unc'] if abs(x['d'] - d) < 1e-9), None)
    if fam != 'unc' and c:
        gain = (t['as_pub'] / c['as_pub'] - 1) * 100
        s += (f" Against the coarse <a href=\"{c['url']}\">{c['name']}</a> it has {g(t['tpi'])} threads "
              f"per inch instead of {g(c['tpi'])}, a stress area {gain:.0f}% larger and a lead angle of "
              f"{t['lead']:.2f}° instead of {c['lead']:.2f}°.")
    elif others:
        s += " Finer threads on the same diameter are " + join_links(others) + "."
    return s


def join_links(ts):
    parts = [f'<a href="{x["url"]}">{x["name"]}</a>' for x in ts]
    if len(parts) == 1:
        return parts[0]
    return ', '.join(parts[:-1]) + ' and ' + parts[-1]


def build(t, fams, prev, nxt):
    m = is_m(t)
    name = t['name']
    hub_url, hub_name = FAMILY_HUB[t['family']]
    u1, u2 = ('mm', 'in') if m else ('in', 'mm')
    lim = minor_limits(t)
    a_nat, a_alt = area_native(t)
    opts = drill_options(t)
    sib = siblings(t, fams)

    # ---- title and description
    if m:
        title = f"{name} Tap Drill: {t['drill_name']} — Pitch Ø {t['d2']:.3f} mm, ISO 724"
        desc = (f"{name} tap drill is {t['drill_name']} ({t['drill_pct']:.0f}% thread). Pitch Ø {t['d2']:.3f} mm, "
                f"minor Ø {t['d1']:.3f} mm, stress area {area(t)[0]} mm²")
        if t['clear']:
            desc += f", clearance hole {g(t['clear'][1])} mm"
        desc += '. ' + ('6g/6H limits per ISO 965-1.' if t.get('tol') else 'Dimensions per ISO 724.')
    else:
        title = f"{name} Tap Drill: {drill_text(t).replace(' in)', '\")')} — ASME B1.1"
        desc = (f"{name} tap drill is {t['drill_name']} ({t['drill_in']:.4f} in, {t['drill_mm']:.2f} mm). "
                f"Major Ø {t['d']:.4f} in, pitch Ø {t['d2']:.4f} in, minor Ø {t['d1']:.4f} in, "
                f"stress area {area(t)[1]} in². 2A/2B limits.")
    h1 = f"{name} Thread Dimensions and Tap Drill"

    b = [f'<h1>{e(h1)}</h1>', f'<p class="lead">{lead_text(t, fams)}</p>']
    if t.get('note'):
        b.append(f'<div class="note"><p>{e(t["note"])}</p></div>')
    use = USES.get(name) or USES.get(t.get('short', ''))
    if use:
        b.append(f'<p>{e(use)}</p>')

    # ---- facts
    fx = [('Tap drill', t['drill_name'], f"{t['drill_pct']:.0f}% thread"
           + ('' if m else f", {t['drill_mm']:.2f} mm"), True),
          ('Pitch', f"{g(t['p'])} mm" if m else f"{g(t['tpi'])} TPI",
           f"{t['tpi']:.1f} TPI" if m else f"{t['p'] * IN:.3f} mm", False),
          ('Major diameter', nat(t, t['d']), alt(t, t['d']), False),
          ('Pitch diameter', nat(t, t['d2']), alt(t, t['d2']), False),
          ('Minor diameter (nut)', nat(t, t['d1']), alt(t, t['d1']), False),
          ('Tensile stress area', a_nat, a_alt, False)]
    if t['clear']:
        if m:
            fx.append(('Clearance hole', f"{g(t['clear'][1])} mm", 'medium fit, ISO 273', False))
        else:
            c = t['clear'][1]
            fx.append(('Clearance hole', drills_label(c), 'normal fit, ASME B18.2.8', False))
    b.append(facts(fx))

    # ---- diagrams
    fmt_len = (lambda v: f"{g(v, 3)} mm") if m else (lambda v: f"{v:.3f} in")
    sv = svg.scale_view(name, t['d'], t['p'], t['h_ext'], u1, fmt_len, 'cp-scale')
    labels = {
        'p': f"P = {g(t['p'])} mm" if m else f"P = {t['p']:.4f} in",
        'maj': ('major Ø d', nat(t, t['d'])),
        'pit': ('pitch Ø d2', nat(t, t['d2'])),
        'min': ('minor Ø D1', nat(t, t['d1'])),
        'h': f"5H/8 = {nat(t, t['h_int'])}",
    }
    pv = svg.profile_view(name, labels,
                          f"Basic profile of {name}: 60 degree flanks, pitch {labels['p'][4:]}, major diameter "
                          f"{nat(t, t['d'])}, pitch diameter {nat(t, t['d2'])}, minor diameter {nat(t, t['d1'])}.")
    shown = (300 - 16) / (124 / t['d'])
    b.append('<section><h2>Thread profile</h2><div class="figs">'
             + svg.figure(sv, f"{name} drawn to scale: {shown / t['p']:.0f} threads in "
                              + (f"{shown:.1f} mm" if m else f"{shown:.2f} in") + " of length.")
             + svg.figure(pv, f"Basic profile with the {name} dimensions. The nut and bolt share the "
                              f"same pitch diameter.")
             + '</div></section>')

    # ---- dimensions
    ext_name = ('Minor diameter, external thread d<sub>3</sub>' if m
                else 'Minor diameter, external UNR thread d<sub>3</sub>')
    rows = [
        ('Major diameter d = D', nat(t, t['d'], 0), alt(t, t['d'], 0)),
        ('Pitch P', nat(t, t['p'], 0) if m else f"{t['p']:.5f}", alt(t, t['p'], 0)),
        ('Pitch diameter d<sub>2</sub> = D<sub>2</sub>', nat(t, t['d2'], 0), alt(t, t['d2'], 0)),
        ('Minor diameter, internal thread D<sub>1</sub>', nat(t, t['d1'], 0), alt(t, t['d1'], 0)),
        (ext_name, nat(t, t['d3'], 0), alt(t, t['d3'], 0)),
        ('Height of fundamental triangle H', nat(t, t['H'], 0), alt(t, t['H'], 0)),
        ('Thread height, internal (5H/8)', nat(t, t['h_int'], 0), alt(t, t['h_int'], 0)),
        (f"Thread height, external ({'17H/24' if m else '11H/16'})", nat(t, t['h_ext'], 0),
         alt(t, t['h_ext'], 0)),
        ('Crest flat of external thread (P/8)', nat(t, t['crest'], 0), alt(t, t['crest'], 0)),
        ('Crest flat of internal thread (P/4)', nat(t, t['root_flat'], 0), alt(t, t['root_flat'], 0)),
    ]
    rows2 = [
        ('Threads per inch', f"{t['tpi']:.2f}" if m else g(t['tpi'])),
        ('Flank angle', '60° (30° each side)'),
        ('Lead angle at the pitch diameter', f"{t['lead']:.2f}°"),
        ('Tensile stress area A<sub>s</sub>', f"{a_nat} ({a_alt})"),
    ]
    std = 'ISO 724' if m else 'ASME B1.1'
    b.append(f'<section><h2>{name} basic dimensions</h2>'
             + spec_table(rows, f"{name} basic dimensions", ('Dimension', u1, u2))
             + spec_table(rows2, f"{name} thread data", ('Property', 'Value'))
             + f'<p class="small muted">Basic (nominal) sizes per {std}, before tolerances. '
               f'{"d<sub>3</sub> is the root diameter of a bolt with the rounded root that ISO 898-1 uses for the stress area." if m else "A UN external thread with a flat root has the same basic minor diameter as the nut (D<sub>1</sub>); d<sub>3</sub> applies to the rounded UNR root."}'
               '</p></section>')

    # ---- tolerances
    b.append(limits_section(t))

    # ---- tap drill
    b.append(tap_section(t, opts, lim))

    # ---- clearance
    b.append(clearance_section(t))

    # ---- strength
    b.append(strength_section(t))

    # ---- same diameter
    if len(sib) > 1:
        rows_c = [(x['name'], x['p'], x['h_int'], x is t) for x in sib]
        fd = (lambda v: f"{v:.3f} mm") if m else (lambda v: f"{v:.4f} in")
        cmp_svg = svg.pitch_compare(rows_c, fd)
        head = ['Thread', 'Pitch (mm)' if m else 'TPI', f'Pitch Ø ({u1})', f'Minor Ø D1 ({u1})',
                'Stress area (' + ('mm²' if m else 'in²') + ')', 'Tap drill']
        trs, rc = [], []
        for x in sib:
            nm = f'<a href="{x["url"]}">{x["name"]}</a>' if x is not t else x['name']
            trs.append([nm, g(x['p']) if m else g(x['tpi']), nat(x, x['d2'], 0), nat(x, x['d1'], 0),
                        area(x)[0] if m else area(x)[1], x['drill_name']])
            rc.append('rec' if x is t else '')
        dia_lab = f"M{g(t['d'])}" if m else t['label'] + (' in' if not t['label'].startswith('#') else '')
        b.append(f'<section><h2>{dia_lab} pitches compared</h2>'
                 f'<p>All standard pitches on the {dia_lab} diameter. A finer pitch gives a shallower '
                 f'thread, a larger core and a smaller lead angle; a coarser pitch is faster to assemble '
                 f'and more tolerant of damage and plating.</p>'
                 + svg.figure(cmp_svg, f"{dia_lab} pitches at the same scale with crests aligned; "
                                       f"{name} is outlined.")
                 + table(head, trs, 'chart', label=f"{dia_lab} pitches compared", rowcls=rc)
                 + '<p class="small"><a href="/coarse-vs-fine/">When to choose a coarse or a fine thread</a></p>'
                 + '</section>')

    # ---- nearest in the other system
    near, dmm, pmm = nearest_other(t, fams)
    if near:
        x, xd, xp = near[0]
        diff = xd - dmm
        word = 'larger' if diff > 0 else 'smaller'
        other = 'inch' if m else 'metric'
        trs = [[name + ' (this thread)', f"{dmm:.3f}", f"{pmm:.3f}", f"{IN / pmm:.2f}", '—']]
        for x2, xd2, xp2 in near:
            trs.append([f'<a href="{x2["url"]}">{x2["name"]}</a>', f"{xd2:.3f}", f"{xp2:.3f}",
                        f"{IN / xp2:.2f}", f"{xd2 - dmm:+.3f}"])
        b.append(f'<section><h2>Closest {other} thread</h2>'
                 f'<p>No {other} thread is interchangeable with {name}. The nearest is '
                 f'<a href="{x["url"]}">{x["name"]}</a>, which is {abs(diff):.2f} mm {word} in diameter with a '
                 f'pitch of {xp:.3f} mm against {pmm:.3f} mm. A nut may start on the wrong thread and then '
                 f'bind or strip, so identify by both diameter and pitch.</p>'
                 + table(['Thread', 'Major Ø (mm)', 'Pitch (mm)', 'TPI', 'Ø difference (mm)'], trs, 'chart',
                         label=f"{name} against the closest {other} threads",
                         rowcls=['rec'] + [''] * len(near))
                 + '<p class="small"><a href="/thread-identifier/">Identify a thread from measurements</a></p>'
                 + '</section>')

    # ---- formulas
    b.append(formula_section(t))

    # ---- navigation
    links = []
    if prev:
        links.append((f"← {prev['name']}", prev['url']))
    if nxt:
        links.append((f"{nxt['name']} →", nxt['url']))
    links.append((f"All {hub_name} sizes", hub_url))
    links.append(('Tap drill chart', '/tap-drill-chart/'))
    links.append(('Thread calculator', '/calculator/'))
    b.append('<section><h2>Related sizes and tools</h2>' + chips(links) + '</section>')
    b.append(sources(t))

    schema = [webpage_ld(t['url'], title, desc,
                         {'@type': 'Thing', 'name': f"{name} screw thread"})]
    og = {'metric': '/metric/og-image.png', 'metric-fine': '/metric/og-image.png',
          'unc': '/unc/og-image.png', 'unf': '/unf/og-image.png', 'unef': '/unc/og-image.png'}[t['family']]
    return page(t['url'], title, desc, '\n'.join(b), trail=[(hub_name, hub_url), (name, None)],
                schema=schema, og_image=og)


def drills_label(n):
    return n if n[0] in '#ABCDEFGHIJKLMNOPQRSTUVWXYZ' else n + ' in'


def limits_section(t):
    m = is_m(t)
    name = t['name']
    if m:
        L = t.get('tol')
        if not L:
            return (f'<section><h2>{name} tolerance limits</h2><p>ISO 965-1 defines no grade 6 '
                    f'tolerances for a {g(t["p"])} mm pitch, so there are no 6g/6H limits for {name}. '
                    f'ISO 965-2 specifies tolerance classes 5H for the nut and 6h for the screw on '
                    f'M1, M1.2 and M1.4.</p></section>')
        d, d2, d1 = t['d'], t['d2'], t['d1']
        ext = [('Major diameter d', f"{d - L['es']:.3f}", f"{d - L['es'] - L['Td']:.3f}", f"{L['Td']:.3f}"),
               ('Pitch diameter d<sub>2</sub>', f"{d2 - L['es']:.3f}", f"{d2 - L['es'] - L['Td2']:.3f}",
                f"{L['Td2']:.3f}")]
        itn = [('Minor diameter D<sub>1</sub>', f"{d1 + L['TD1']:.3f}", f"{d1:.3f}", f"{L['TD1']:.3f}"),
               ('Pitch diameter D<sub>2</sub>', f"{d2 + L['TD2']:.3f}", f"{d2:.3f}", f"{L['TD2']:.3f}")]
        return (f'<section><h2>{name} tolerance limits (6g bolt, 6H nut)</h2>'
                f'<p>6g and 6H are the general-purpose tolerance classes for commercial screws and nuts. '
                f'The 6g screw has a fundamental deviation of {L["es"] * 1000:.0f} µm, so even at its '
                f'largest it sits {L["es"]:.3f} mm below the basic size and leaves room for a thin plating.</p>'
                + table(['External thread 6g', 'Max (mm)', 'Min (mm)', 'Tolerance (mm)'], ext, 'chart',
                        label=f"{name} 6g limits")
                + table(['Internal thread 6H', 'Max (mm)', 'Min (mm)', 'Tolerance (mm)'], itn, 'chart',
                        label=f"{name} 6H limits")
                + '<p class="small muted">Computed from the ISO 965-1 deviations and tolerances for normal '
                  'length of engagement; the results match the limits tabulated in ISO 965-2.</p></section>')
    L = t['limits']
    tol = lambda a, b: f"{float(a) - float(b):.4f}"
    ext = [('Major diameter', L[1], L[2], tol(L[1], L[2])),
           ('Pitch diameter', L[3], L[4], tol(L[3], L[4]))]
    itn = [('Minor diameter', L[6], L[5], tol(L[6], L[5])),
           ('Pitch diameter', L[8], L[7], tol(L[8], L[7]))]
    return (f'<section><h2>{name} limits of size (class 2A bolt, 2B nut)</h2>'
            f'<p>Classes 2A and 2B are the general-purpose fits for commercial bolts, screws and nuts. '
            f'The 2A external thread has an allowance of {L[0]} in, so its maximum size is that much '
            f'below basic; the 2B nut starts at the basic size.</p>'
            + table(['External thread 2A', 'Max (in)', 'Min (in)', 'Tolerance (in)'], ext, 'chart',
                    label=f"{name} class 2A limits")
            + table(['Internal thread 2B', 'Max (in)', 'Min (in)', 'Tolerance (in)'], itn, 'chart',
                    label=f"{name} class 2B limits")
            + '<p class="small muted">Limits of size from ASME B1.1 Table 2.</p></section>')


def tap_section(t, opts, lim):
    m = is_m(t)
    name = t['name']
    out = [f'<section id="tap-drill"><h2>{name} tap drill size</h2>']
    big = t['drill_name'] if m else f"{t['drill_name']} ({t['drill_in']:.4f} in, {t['drill_mm']:.2f} mm)"
    out.append(f'<div class="answer"><p>Tap drill for {name}: <span class="big">{big}</span></p>'
               f'<p>This leaves about {t["drill_pct"]:.0f}% thread in the tapped hole.</p></div>')
    if m:
        exact = t['drill_exact']
        if abs(exact - t['drill_mm']) > 1e-9:
            out.append(f'<p>The rule for metric tap drills is diameter minus pitch: {g(t["d"])} − {g(t["p"])} = '
                       f'{g(exact)} mm. Tap drill tables round this to {t["drill_name"]}, a stocked drill size.</p>')
        else:
            out.append(f'<p>The rule for metric tap drills is diameter minus pitch: {g(t["d"])} − {g(t["p"])} = '
                       f'{g(exact)} mm, which is a stocked drill size.</p>')
    else:
        basis = t['drill_basis']
        if basis == 'chart':
            out.append(f'<p>{t["drill_name"]} is the drill listed for {name} in standard tap drill charts. '
                       f'It is {t["d"] - t["drill_in"]:.4f} in under the {t["d"]:.4f} in major diameter.</p>')
        elif basis == 'single':
            out.append(f'<p>Few charts list a drill for a thread this large, and holes of this size are '
                       f'normally bored rather than drilled. {t["drill_name"]} follows the usual rule of major '
                       f'diameter minus one pitch.</p>')
        else:
            out.append(f'<p>Published charts rarely list this size. {t["drill_name"]} is the nominal diameter '
                       f'minus 3/64 in, the same convention charts use for 9/16-18 and 5/8-18.</p>')
    if lim:
        cls = '6H' if m else '2B'
        u = 'mm' if m else 'in'
        f3 = (lambda v: f"{v:.3f}") if m else (lambda v: f"{v:.3f}")
        rec_in = lim[0] - 1e-9 <= (t['drill_mm'] if m else t['drill_in']) <= lim[1] + 1e-9
        out.append(f'<p>The {cls} minor diameter of the finished nut thread must lie between {f3(lim[0])} and '
                   f'{f3(lim[1])} {u}. '
                   + (f'The recommended drill falls inside that band.' if rec_in else
                      f'The charted drill is slightly under that band: the tap trims the crests to size, at '
                      f'the cost of higher tapping torque. A drill inside the band is the safer choice in '
                      f'tough materials.') + '</p>')
    rows, rc = [], []
    for o in opts:
        tag = ''
        if o['rec']:
            tag = '<span class="tag">recommended</span>'
        within = '—' if o['within'] is None else ('yes' if o['within'] else 'no')
        rows.append([o['name'] + tag, f"{o['mm']:.2f}", f"{o['in']:.4f}", f"{o['pct']:.0f}%",
                     within, bar(o['pct'])])
        rc.append('rec' if o['rec'] else '')
    cls = '6H' if m else '2B'
    tb = table(['Drill', 'mm', 'in', '% thread', f'Within {cls} limits', 'Thread engagement'], rows,
               'chart', label=f"Tap drill options for {name}", rowcls=rc)
    tb = tb.replace('<td class="n"><span class="bar"', '<td class="barcell"><span class="bar"')
    out.append(f'<h3>Other drills that work for {name}</h3>'
               f'<p>A larger drill cuts less thread and taps more easily; a smaller one gives a fuller '
               f'thread but loads the tap harder.</p>' + tb)
    out.append('<p class="small muted">% thread = (major diameter − drill diameter) ÷ (1.299 × pitch). '
               'See the <a href="/tap-drill-chart/">tap drill chart</a> for how to choose a percentage.</p>')
    out.append('</section>')
    return ''.join(out)


def clearance_section(t):
    m = is_m(t)
    name = t['name']
    size = f"M{g(t['d'])}" if m else (t['label'] if t['label'].startswith('#') else t['label'] + ' in')
    if not t['clear']:
        if m:
            return (f'<section><h2>Clearance hole for {size}</h2><p>ISO 273 does not list a clearance '
                    f'hole for {size}; its table goes from M8 to M10. The neighbouring sizes leave '
                    f'0.4 to 0.5 mm of clearance in the fine series and about 1 mm in the medium series.</p></section>')
        if t['d'] > 1.5:
            why = 'ASME B18.2.8 covers sizes up to 1-1/2 in'
        else:
            why = f'ASME B18.2.8 does not list the {size} size'
        return (f'<section><h2>Clearance hole for {size}</h2><p>{why}, so there is no standard '
                f'clearance hole for the {size} size. Size the hole from the fit the joint needs.</p></section>')
    if m:
        c = t['clear']
        rows = [('Fine (H12)', g(c[0]), f"{c[0] / IN:.4f}", g(c[0] - t['d'])),
                ('Medium (H13)', g(c[1]), f"{c[1] / IN:.4f}", g(c[1] - t['d'])),
                ('Coarse (H14)', g(c[2]), f"{c[2] / IN:.4f}", g(c[2] - t['d']))]
        return (f'<section><h2>Clearance hole for {size}</h2>'
                f'<p>The clearance hole depends only on the {g(t["d"])} mm diameter, not on the pitch. '
                f'The medium series, {g(c[1])} mm, is the usual choice for general assembly.</p>'
                + table(['Series', 'Hole Ø (mm)', 'Hole Ø (in)', 'Clearance on Ø (mm)'], rows, 'chart',
                        label=f"Clearance holes for {size}")
                + '<p class="small muted">Hole diameters from ISO 273.</p></section>')
    c = t['clear']
    rows = []
    for fit, n in zip(('Close', 'Normal', 'Loose'), c):
        dia = drills.inch_drill(n)
        rows.append((fit, drills_label(n), f"{dia:.4f}", f"{dia * IN:.2f}", f"{dia - t['d']:.4f}"))
    return (f'<section><h2>Clearance hole for {size}</h2>'
            f'<p>The clearance hole depends only on the {t["d"]:.4f} in diameter, not on the thread series. '
            f'The normal fit, a {drills_label(c[1])} drill, is the usual choice for general assembly.</p>'
            + table(['Fit', 'Drill', 'Hole Ø (in)', 'Hole Ø (mm)', 'Clearance on Ø (in)'], rows, 'chart',
                    label=f"Clearance holes for {size}")
            + '<p class="small muted">Nominal drill sizes from ASME B18.2.8.</p></section>')


def strength_section(t):
    m = is_m(t)
    name = t['name']
    if m:
        if not t['in_898']:
            if t['family'] == 'metric':
                why = ('ISO 898-1 covers coarse threads from M1.6 to M39' if t['d'] < 1.6 or t['d'] > 39
                       else 'ISO 898-1 does not tabulate this size')
            else:
                why = 'ISO 898-1 tabulates fine-pitch loads only for a selected set of threads from M8×1 to M39×3'
            return (f'<section><h2>{name} strength</h2><p>{why}, so it gives no proof or breaking loads '
                    f'for {name}. For an estimate, multiply the tensile stress area of {area(t)[0]} mm² by '
                    f'the stress of the material: for example, 800 MPa gives '
                    f'{sig(float(area(t)[0]) * 0.8, 3)} kN.</p></section>')
        a = t['as_pub'] if t['as_pub'] else float(sig(t['As'], 3))
        rows = []
        for cls, lo, hi, rm, sp in tables.ISO898:
            if lo <= t['d'] <= hi:
                rows.append((cls, sp, rm, sig(a * sp / 1000, 3), sig(a * rm / 1000, 3)))
        note = ('Class 9.8 applies only up to 16 mm and is omitted. ' if t['d'] > 16 else '')
        src = ('A<sub>s</sub> from ISO 898-1' if t['as_pub']
               else 'A<sub>s</sub> computed from the ISO 898-1 formula; the standard tabulates it from M3')
        return (f'<section><h2>{name} proof and breaking loads</h2>'
                f'<p>Loads for steel bolts and screws by property class, from the tensile stress area of '
                f'{g(a, 2)} mm². The proof load is the highest load the fastener must carry without '
                f'permanent set.</p>'
                + table(['Property class', 'Proof stress (MPa)', 'Min tensile strength (MPa)',
                         'Proof load (kN)', 'Min breaking load (kN)'], rows, 'chart',
                        label=f"{name} loads by property class")
                + f'<p class="small muted">{note}Stresses from ISO 898-1:2013 Table 3; {src}. '
                  f'Loads rounded to three significant figures.</p></section>')
    d = t['d']
    if d < 0.25 or d > 1.5:
        why = ('SAE J429 starts at 1/4 in' if d < 0.25 else 'SAE J429 stops at 1-1/2 in')
        a = t['as_pub']
        extra = ''
        if d > 1.5:
            extra = (' Bolts this large are made to specifications such as ASTM A307, A449 or A354, '
                     'whose strengths depend on diameter.')
        return (f'<section><h2>{name} strength</h2><p>{why}, so the SAE grades give no proof load for '
                f'{name}.{extra} For an estimate, multiply the tensile stress area of {area(t)[1]} in² by the '
                f'strength of the material: for example, 60,000 psi gives {thousands(float(sig(a * 60000, 3)))} lbf.</p>'
                f'</section>')
    a = t['as_pub']
    rows = []
    for grade, lo, hi, proof, ten, _ in tables.J429:
        if lo <= d <= hi:
            rows.append((grade, thousands(proof), thousands(ten),
                         thousands(float(sig(a * proof, 3))), thousands(float(sig(a * ten, 3))),
                         sig(a * proof * 0.00444822, 3)))
    return (f'<section><h2>{name} proof and breaking loads</h2>'
            f'<p>Loads for steel bolts by SAE grade, from the tensile stress area of {area(t)[1]} in². '
            f'The proof load is the highest load the bolt must carry without permanent set.</p>'
            + table(['SAE grade', 'Proof stress (psi)', 'Min tensile strength (psi)', 'Proof load (lbf)',
                     'Min breaking load (lbf)', 'Proof load (kN)'], rows, 'chart',
                    label=f"{name} loads by SAE grade")
            + '<p class="small muted">Strengths from SAE J429 for this diameter; stress area from ASME B1.1. '
              'Loads rounded to three significant figures.</p></section>')


def formula_section(t):
    m = is_m(t)
    name = t['name']
    d, p = t['d'], t['p']
    u = 'mm' if m else 'in'
    f = (lambda v: f"{v:.3f}") if m else (lambda v: f"{v:.4f}")
    ds = g(d) if m else f"{d:.4f}"
    ps = g(p) if m else f"{p:.5f}"
    k3, h3 = ('1.226869', '17H/24') if m else ('1.190785', '11H/16')
    items = [
        f"P = {ps} {u}" + ('' if m else f" = 1 ÷ {g(t['tpi'])} threads per inch"),
        f"H = 0.866025 × P = {f(t['H'])} {u}",
        f"d<sub>2</sub> = d − 0.649519 × P = {ds} − {f(0.649519 * p)} = {f(t['d2'])} {u}",
        f"D<sub>1</sub> = d − 1.082532 × P = {ds} − {f(1.082532 * p)} = {f(t['d1'])} {u}",
        f"d<sub>3</sub> = d − {k3} × P = {ds} − {f(float(k3) * p)} = {f(t['d3'])} {u} (external root, {h3} deep)",
    ]
    if m:
        items.append(f"A<sub>s</sub> = π/4 × ((d<sub>2</sub> + d<sub>3</sub>) ÷ 2)² = π/4 × "
                     f"{(t['d2'] + t['d3']) / 2:.3f}² = {t['As']:.2f} mm²")
    else:
        items.append(f"A<sub>s</sub> = 0.7854 × (d − 0.9743 × P)² = 0.7854 × {d - 0.9743 * p:.4f}² = "
                     f"{t['As']:.5f} in²")
    items.append(f"Lead angle = arctan(P ÷ (π × d<sub>2</sub>)) = {t['lead']:.2f}°")
    return (f'<section><h2>How the {name} dimensions are calculated</h2><div class="panel">'
            f'<p>Every basic dimension follows from the major diameter and the pitch:</p><ul>'
            + ''.join(f'<li>{i}</li>' for i in items) + '</ul></div></section>')


def sources(t):
    if is_m(t):
        s = ('ISO 68-1 and ISO 724 (profile and basic dimensions), ISO 261 (diameter and pitch series), '
             'ISO 965-1 (tolerances), ISO 273 (clearance holes), ISO 898-1 (mechanical properties) and '
             'tap drill tables based on ISO 2306')
    else:
        s = ('ASME B1.1 (profile, series, limits of size and stress area), ASME B18.2.8 (clearance holes), '
             'SAE J429 (mechanical properties) and the tap drill tables of Machinery’s Handbook')
    return (f'<p class="small muted">Sources: {s}. <a href="/about/#sources">How this site checks its data</a>. '
            f'Last reviewed {__import__("shell").TODAY_TEXT}.</p>')
