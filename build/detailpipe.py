"""Detail pages for pipe threads: NPT (ASME B1.20.1) and BSP parallel G (ISO 228-1)."""
import drills
import svg
import tables
from content import USES
from shell import IN, TODAY_TEXT, bar, chips, e, facts, g, page, spec_table, table, webpage_ld

# ISO 7-1 taper sizes (R, Rc, Rp) that share gauge diameters with the G thread of the same size.
ISO7_SIZES = {'1/16', '1/8', '1/4', '3/8', '1/2', '3/4', '1', '1-1/4', '1-1/2', '2', '2-1/2', '3', '4'}
# Tap drill for the taper internal thread Rc without reaming, mm (Emuge chart).
RC_DRILL = {'1/16': 6.15, '1/8': 8.15, '1/4': 10.85, '3/8': 14.3, '1/2': 17.8, '3/4': 23.2, '1': 29.2}
# Tap drill for the parallel internal thread Rp, mm (Emuge chart).
RP_DRILL = {'1/16': 6.55, '1/8': 8.6, '1/4': 11.5, '3/8': 15, '1/2': 18.5, '3/4': 24, '1': 30.25}


def i5(v):
    return f"{v:.5f}"


def i4(v):
    return f"{v:.4f}"


def m3(v):
    return f"{v * IN:.3f}"


def npt_title_drill(t):
    return t['main']['name'] if t['main'] else None


def build_npt(t, fams, prev, nxt):
    lab = t['label']
    name = t['name']
    plain = t['plain']
    tpi = t['tpi']
    main = t['main']
    if main:
        title = f'{lab}" NPT Tap Drill: {main["name"]} — {g(tpi)} TPI, ASME B1.20.1'
        dtxt = f'tap drill {main["name"]} ({main["in"]:.4f} in)'
        if t['std'] and t['common'] and t['common']['name'] != t['std']['name']:
            dtxt += f', {t["common"]["name"]} on many charts'
    else:
        title = f'{lab}" NPT Thread Dimensions — {g(tpi)} TPI, ASME B1.20.1'
        dtxt = f'bore before tapping {t["K0"]:.4f} in'
    desc = (f'{lab}" NPT: {g(tpi)} TPI, pipe OD {t["D"]:.3f} in ({t["D"] * IN:.2f} mm), {dtxt}. '
            f'Pitch Ø {t["E0"]:.5f} in at the pipe end, 1 in 16 taper.')
    b = [f'<h1>{plain} Thread Dimensions and Tap Drill</h1>']
    lead = (f'{lab} NPT, written in full as {plain}, is the American taper pipe thread for nominal '
            f'{lab} inch pipe: {g(tpi)} threads per inch cut on a 1 in 16 taper, on pipe with an outside '
            f'diameter of {t["D"]:.3f} in ({t["D"] * IN:.2f} mm). The nominal size names the pipe and is not a '
            f'dimension you can measure on the thread.')
    b.append(f'<p class="lead">{lead}</p>')
    use = USES.get(f'{lab} NPT')
    if use:
        b.append(f'<p>{e(use)}</p>')
    fx = []
    if main:
        fx.append(('Tap drill', main['name'], f"{main['in']:.4f} in, {main['mm']:.2f} mm", True))
    else:
        fx.append(('Bore before tapping', f"{t['K0']:.4f} in", f"{t['K0'] * IN:.2f} mm", True))
    fx += [('Threads per inch', g(tpi), f"pitch {t['p'] * IN:.3f} mm", False),
           ('Pipe outside diameter', f"{t['D']:.3f} in", f"{t['D'] * IN:.2f} mm", False),
           ('Pitch Ø at hand-tight plane', f"{t['E1']:.5f} in", f"{t['E1'] * IN:.3f} mm", False),
           ('Hand-tight engagement', f"{t['L1']:.3f} in", f"{t['turns']:.2f} threads", False),
           ('Effective thread length', f"{t['L2']:.4f} in", f"{t['threads_eff']:.2f} threads", False)]
    b.append(facts(fx))

    fmt = lambda v, nd=5: f"{v:.{nd}f}"
    dg = svg.npt_view(t, fmt)
    b.append('<section><h2>Where the diameters are measured</h2>'
             + svg.figure(dg, f'{plain} external thread. E0, E1 and E2 are pitch diameters (inches) at three '
                              f'planes along the taper; the taper is exaggerated to make it visible.', 'wide')
             + f'<p>A taper thread has no single pitch diameter. ASME B1.20.1 defines it at the end of the pipe '
               f'(E<sub>0</sub>), at the plane where a fitting stops when screwed on by hand (E<sub>1</sub>), and '
               f'at the end of the effective thread (E<sub>2</sub>). Each step of 1 in along the axis adds '
               f'1/16 in to the diameter.</p></section>')

    wrench = 3 if t['D'] <= 2.375 else 2
    rows = [
        ('Pipe outside diameter D', f"{t['D']:.4f}", m3(t['D'])),
        ('Pitch P', i5(t['p']), m3(t['p'])),
        ('Pitch diameter at pipe end E<sub>0</sub>', i5(t['E0']), m3(t['E0'])),
        ('Pitch diameter at hand-tight plane E<sub>1</sub>', i5(t['E1']), m3(t['E1'])),
        ('Pitch diameter at end of effective thread E<sub>2</sub>', i5(t['E2']), m3(t['E2'])),
        ('Hand-tight engagement L<sub>1</sub>', i4(t['L1']), m3(t['L1'])),
        ('Effective thread length L<sub>2</sub>', i4(t['L2']), m3(t['L2'])),
        ('Minor diameter at pipe end K<sub>0</sub>', i4(t['K0']), m3(t['K0'])),
        ('Thread height h (0.8 × P)', i5(t['h']), m3(t['h'])),
    ]
    rows2 = [
        ('Threads per inch', g(tpi)),
        ('Flank angle', '60° (30° each side)'),
        ('Taper', '1 in 16 on diameter (3/4 in per foot)'),
        ('Taper angle to the axis', '1° 47′ (1.7899°)'),
        ('Threads engaged by hand', f"{t['turns']:.2f}"),
        ('Wrench make-up', f"{wrench} threads"),
    ]
    b.append(f'<section><h2>{plain} dimensions</h2>'
             + spec_table(rows, f"{plain} dimensions", ('Dimension', 'in', 'mm'))
             + spec_table(rows2, f"{plain} thread data", ('Property', 'Value'))
             + '<p class="small muted">Basic dimensions from ASME B1.20.1 Table 2. Millimetre values are '
               'conversions.</p></section>')

    # tap drill
    b.append(npt_tap(t))

    # make-up
    total = t['L1'] + wrench * t['p']
    b.append(f'<section><h2>How far {lab} NPT screws in</h2>'
             f'<p>A {lab} NPT fitting turns in by hand for {t["L1"]:.3f} in ({t["L1"] * IN:.1f} mm), about '
             f'{t["turns"]:.1f} threads, before the flanks meet. The standard then allows {wrench} more threads of '
             f'wrench make-up, for a total engagement of about {total:.3f} in ({total * IN:.1f} mm). '
             f'Tolerance on the hand-tight position is one thread either way, so a joint that stops a turn early '
             f'or late is still within the standard.</p>'
             f'<p>NPT threads do not seal by themselves. The crests and roots leave a spiral gap, so '
             f'ASME B1.20.1 calls for a sealant (PTFE tape or pipe compound) where the joint must be '
             f'pressure-tight. Dryseal NPTF threads to ASME B1.20.3 have the same pitch and taper but '
             f'controlled crests and roots that seal without it.</p></section>')

    # BSP counterpart
    gt = next((x for x in fams['bsp'] if x['label'] == lab), None)
    if gt:
        same = 'the same pitch' if abs(gt['tpi'] - tpi) < 1e-9 else 'a different pitch'
        rows = [(f'{plain} (this thread)', g(tpi), f"{t['D'] * IN:.3f}", f"{t['D']:.4f}", '60°', '1 in 16'),
                (f'<a href="{gt["url"]}">{gt["name"]} (BSPP)</a>', g(gt['tpi']), f"{gt['d']:.3f}",
                 f"{gt['d'] / IN:.4f}", '55°', 'parallel')]
        b.append(f'<section><h2>{lab} NPT against {gt["name"]} BSP</h2>'
                 f'<p>The British Standard Pipe thread of the same nominal size has {same} '
                 f'({g(gt["tpi"])} against {g(tpi)} threads per inch), a 55° flank angle instead of 60° and a '
                 f'major diameter of {gt["d"]:.3f} mm against {t["D"] * IN:.3f} mm. '
                 + ('Because the pitch matches, the two will screw together for a turn or two, but the flanks '
                    'do not mate and the joint will leak. ' if same == 'the same pitch' else
                    'The two do not screw together properly. ')
                 + 'Use an adapter.</p>'
                 + table(['Thread', 'TPI', 'Major Ø (mm)', 'Major Ø (in)', 'Flank angle', 'Taper'], rows,
                         'chart', label=f"{lab} NPT compared with {gt['name']}", rowcls=['rec', ''])
                 + '<p class="small"><a href="/npt-vs-bsp/">NPT vs BSP in detail</a></p></section>')

    links = []
    if prev:
        links.append((f"← {prev['plain']}", prev['url']))
    if nxt:
        links.append((f"{nxt['plain']} →", nxt['url']))
    links += [('All NPT sizes', '/pipe-threads/'), ('BSP thread chart', '/bsp/'),
              ('Tap drill chart', '/tap-drill-chart/'), ('Thread identifier', '/thread-identifier/')]
    b.append('<section><h2>Related sizes and tools</h2>' + chips(links) + '</section>')
    b.append(f'<p class="small muted">Sources: ASME B1.20.1 (dimensions, Table 2; suggested drills, Appendix), '
             f'Machinery’s Handbook (shop tap drill chart). <a href="/about/#sources">How this site checks '
             f'its data</a>. Last reviewed {TODAY_TEXT}.</p>')
    schema = [webpage_ld(t['url'], title, desc, {'@type': 'Thing', 'name': f"{plain} pipe thread"})]
    return page(t['url'], title, desc, '\n'.join(b), trail=[('NPT Pipe Threads', '/pipe-threads/'),
                                                             (f'{lab} NPT', None)],
                schema=schema, og_image='/pipe-threads/og-image.png')


def npt_tap(t):
    lab = t['label']
    out = [f'<section id="tap-drill"><h2>{lab} NPT tap drill size</h2>']
    if not t['main']:
        out.append(f'<div class="answer"><p>Bore before tapping {lab} NPT: <span class="big">{t["K0"]:.4f} in '
                   f'({t["K0"] * IN:.2f} mm)</span></p><p>This is K<sub>0</sub>, the basic minor diameter at the '
                   f'small end of the thread.</p></div>'
                   f'<p>No tap drill is published for {lab} NPT. Threads this large are bored or milled, and '
                   f'ASME B1.20.1 gives the minor diameter K<sub>0</sub> as the basis for the hole size. Taper the '
                   f'bore at 1 in 16 where full threads are needed over the whole engagement.</p></section>')
        return ''.join(out)
    m = t['main']
    out.append(f'<div class="answer"><p>Tap drill for {lab} NPT: <span class="big">{m["name"]} '
               f'({m["in"]:.4f} in, {m["mm"]:.2f} mm)</span></p>')
    if t['std']:
        out.append('<p>Suggested by ASME B1.20.1 for tapping a drilled hole without reaming.</p></div>')
    else:
        out.append('<p>From the pipe tap drill table in Machinery’s Handbook. ASME B1.20.1 suggests drills '
                   'only up to the 2-1/2 size.</p></div>')
    rows, rc = [], []
    k0 = t['K0']
    if t['std']:
        rows.append(['Drill only, no reaming (ASME B1.20.1)<span class="tag">recommended</span>',
                     t['std']['name'], f"{t['std']['in']:.4f}", f"{t['std']['mm']:.2f}",
                     f"{t['std']['in'] - k0:+.4f}"])
        rc.append('rec')
    if t['ream']:
        rows.append(['Drill, then taper ream (ASME B1.20.1)', t['ream']['name'], f"{t['ream']['in']:.4f}",
                     f"{t['ream']['mm']:.2f}", f"{t['ream']['in'] - k0:+.4f}"])
        rc.append('')
    if t['common']:
        tag = '' if t['std'] else '<span class="tag">recommended</span>'
        rows.append([f'Common shop chart{tag}', t['common']['name'], f"{t['common']['in']:.4f}",
                     f"{t['common']['mm']:.2f}", f"{t['common']['in'] - k0:+.4f}"])
        rc.append('' if t['std'] else 'rec')
    out.append(table(['Method', 'Drill', 'in', 'mm', 'Against K0 (in)'], rows, 'chart',
                     label=f"Tap drills for {lab} NPT", rowcls=rc))
    txt = (f'<p>The hole for a taper tap is a compromise, because a straight drilled hole meets a tapered '
           f'thread. The minor diameter of the thread is {k0:.4f} in at the small end (K<sub>0</sub>) and grows '
           f'by 1/16 in per inch of depth.')
    if t['std'] and t['common'] and t['common']['name'] != t['std']['name']:
        txt += (f' Many printed charts give {t["common"]["name"]} for {lab} NPT. That is '
                f'{t["common"]["in"] - t["std"]["in"]:.4f} in larger than the drill the standard suggests: it taps '
                f'more easily but leaves shallower threads at the bottom of the hole.')
    txt += (' For the fullest thread, drill with the smaller size and follow with a 1 in 16 taper pipe reamer.'
            if t['ream'] else '') + '</p>'
    out.append(txt)
    out.append('<p class="small muted">ASME B1.20.1 notes that its suggested drills do not guarantee fully '
               'formed threads over the whole hand-tight length.</p></section>')
    return ''.join(out)


def bsp_pct(t, drill):
    return (t['d'] - drill) / (2 * t['h']) * 100


def build_bsp(t, fams, prev, nxt):
    lab = t['label']
    name = t['name']
    tpi = t['tpi']
    title = f"{name} BSP Tap Drill: {t['drill_name']}, {tpi} TPI — ISO 228-1"
    desc = (f"{name} (BSPP {lab} in): tap drill {t['drill_name']}, {tpi} TPI, pitch {t['p']:.3f} mm. "
            f"Major Ø {t['d']:.3f} mm ({t['d'] / IN:.4f} in), pitch Ø {t['d2']:.3f} mm, minor Ø {t['d1']:.3f} mm. "
            f"55° parallel thread.")
    b = [f'<h1>{name} BSP Thread Dimensions and Tap Drill</h1>']
    lead = (f'{name} is the parallel British Standard Pipe thread (BSPP) of nominal size {lab}: {tpi} threads '
            f'per inch on a 55° Whitworth form with rounded crests and roots, and a major diameter of '
            f'{t["d"]:.3f} mm ({t["d"] / IN:.4f} in). The size names the bore of the pipe it was once cut on, '
            f'so nothing on the thread measures {lab} inch.')
    b.append(f'<p class="lead">{lead}</p>')
    if not t['in_iso']:
        b.append(f'<div class="note"><p>{name} is not one of the sizes in ISO 228-1. It appears in '
                 f'manufacturers’ thread tables with the dimensions below, which follow the same Whitworth '
                 f'proportions, but fittings in this size are uncommon.</p></div>')
    use = USES.get(name)
    if use:
        b.append(f'<p>{e(use)}</p>')
    b.append(facts([
        ('Tap drill', t['drill_name'], f"{t['drill_in']:.4f} in, {bsp_pct(t, t['drill_mm']):.0f}% thread", True),
        ('Threads per inch', str(tpi), f"pitch {t['p']:.3f} mm", False),
        ('Major diameter', f"{t['d']:.3f} mm", f"{t['d'] / IN:.4f} in", False),
        ('Pitch diameter', f"{t['d2']:.3f} mm", f"{t['d2'] / IN:.4f} in", False),
        ('Minor diameter', f"{t['d1']:.3f} mm", f"{t['d1'] / IN:.4f} in", False),
        ('Thread height', f"{t['h']:.3f} mm", f"{t['h'] / IN:.4f} in", False),
    ]))
    labels = {'p': f"P = {t['p']:.3f} mm", 'maj': ('major Ø d', f"{t['d']:.3f} mm"),
              'pit': ('pitch Ø d2', f"{t['d2']:.3f} mm"), 'min': ('minor Ø d1', f"{t['d1']:.3f} mm"),
              'h': f"h = {t['h']:.3f} mm", 'r': f"r = {t['r']:.3f}"}
    dg = svg.bsp_view(labels, f"Whitworth profile of {name}: 55 degree flanks with rounded crests and roots, "
                              f"pitch {t['p']:.3f} mm, major diameter {t['d']:.3f} mm, pitch diameter "
                              f"{t['d2']:.3f} mm, minor diameter {t['d1']:.3f} mm.")
    b.append('<section><h2>Thread profile</h2>'
             + svg.figure(dg, f"Whitworth profile with the {name} dimensions. Crests and roots are rounded to a "
                              f"radius of {t['r']:.3f} mm.")
             + '</section>')
    rows = [
        ('Major diameter d = D', f"{t['d']:.3f}", f"{t['d'] / IN:.4f}"),
        ('Pitch diameter d<sub>2</sub> = D<sub>2</sub>', f"{t['d2']:.3f}", f"{t['d2'] / IN:.4f}"),
        ('Minor diameter d<sub>1</sub> = D<sub>1</sub>', f"{t['d1']:.3f}", f"{t['d1'] / IN:.4f}"),
        ('Pitch P', f"{t['p']:.3f}", f"{t['p'] / IN:.5f}"),
        ('Thread height h (0.640327 × P)', f"{t['h']:.3f}", f"{t['h'] / IN:.4f}"),
        ('Crest and root radius r (0.137329 × P)', f"{t['r']:.3f}", f"{t['r'] / IN:.4f}"),
        ('Height of fundamental triangle H', f"{t['H']:.3f}", f"{t['H'] / IN:.4f}"),
    ]
    rows2 = [('Threads per inch', str(tpi)), ('Flank angle', '55° (27.5° each side)'),
             ('Taper', 'none (parallel thread)')]
    src = 'ISO 228-1 Table 1' if t['in_iso'] else 'manufacturers’ tables (size not in ISO 228-1)'
    b.append(f'<section><h2>{name} dimensions</h2>'
             + spec_table(rows, f"{name} dimensions", ('Dimension', 'mm', 'in'))
             + spec_table(rows2, f"{name} thread data", ('Property', 'Value'))
             + f'<p class="small muted">Basic dimensions from {src}. Inch values are conversions.</p></section>')

    # tap drill options
    rec = t['drill_mm']
    cands = [v for v in drills.METRIC if 50 <= bsp_pct(t, v) <= 95]
    if rec not in cands:
        cands.append(rec)
    cands = sorted(sorted(cands, key=lambda v: abs(v - rec))[:6])
    rows, rc = [], []
    for v in cands:
        isr = abs(v - rec) < 1e-9
        rows.append([f"{g(v, 2)} mm" + ('<span class="tag">recommended</span>' if isr else ''), f"{v:.2f}",
                     f"{v / IN:.4f}", f"{bsp_pct(t, v):.0f}%", bar(bsp_pct(t, v))])
        rc.append('rec' if isr else '')
    tb = table(['Drill', 'mm', 'in', '% thread', 'Thread engagement'], rows, 'chart',
               label=f"Tap drill options for {name}", rowcls=rc)
    tb = tb.replace('<td class="n"><span class="bar"', '<td class="barcell"><span class="bar"')
    b.append(f'<section id="tap-drill"><h2>{name} tap drill size</h2>'
             f'<div class="answer"><p>Tap drill for {name}: <span class="big">{t["drill_name"]} '
             f'({t["drill_in"]:.4f} in)</span></p><p>This is {rec - t["d1"]:.2f} mm over the basic minor '
             f'diameter of {t["d1"]:.3f} mm and leaves about {bsp_pct(t, rec):.0f}% thread.</p></div>'
             f'<p>ISO 228-1 puts the whole tolerance on the minor diameter of the internal thread above the '
             f'basic size, so the hole is always drilled larger than {t["d1"]:.3f} mm. Drilling to the '
             f'basic minor diameter itself leaves the tap cutting on its full profile and risks breaking it.</p>'
             + tb
             + '<p class="small muted">% thread = (major diameter − drill diameter) ÷ (2 × thread height).</p>'
             + '</section>')

    # taper version
    if lab in ISO7_SIZES:
        extra = ''
        if lab in RC_DRILL:
            extra = (f' The tap drill for the taper internal thread Rc{lab} is {g(RC_DRILL[lab], 2)} mm, and for '
                     f'the parallel internal thread Rp{lab} it is {g(RP_DRILL[lab], 2)} mm; both are smaller '
                     f'than the {t["drill_name"]} used for {name}.')
        b.append(f'<section><h2>{name} and the tapered R{lab} (BSPT)</h2>'
                 f'<p>The taper thread of ISO 7-1 (EN 10226), written R{lab} for the male and Rc{lab} or Rp{lab} '
                 f'for the female, has the same {tpi} threads per inch and the same 55° form as {name}, and '
                 f'at its gauge plane it has the same diameters. It differs in being cut on a 1 in 16 taper and '
                 f'in sealing on the thread with a sealant. The male R{lab} mates with a taper Rc{lab} or a '
                 f'parallel Rp{lab} female thread. Rp is not the same thing as G: the basic sizes agree but '
                 f'the tolerances do not, so a {name} port is not a specified mate for a taper male.{extra}</p></section>')
    else:
        b.append(f'<section><h2>Is there a tapered {lab} BSP?</h2><p>ISO 7-1, the standard for taper BSP '
                 f'threads (R, Rc and Rp), does not include the {lab} size. {name} exists only as a parallel '
                 f'thread.</p></section>')

    b.append(f'<section><h2>How {name} seals</h2><p>A {name} joint does not seal on its threads. ISO 228-1 is '
             f'the standard for pipe threads where the pressure-tight joint is made outside the thread: the '
             f'male fitting clamps a bonded washer, an O-ring or a flat gasket against the face of the port. '
             f'The thread only supplies the clamping force, so thread sealant is not what makes the joint '
             f'tight.</p></section>')

    nt = next((x for x in fams['npt'] if x['label'] == lab), None)
    if nt:
        same = abs(nt['tpi'] - tpi) < 1e-9
        rows = [(f'{name} (this thread)', str(tpi), f"{t['d']:.3f}", f"{t['d'] / IN:.4f}", '55°', 'parallel'),
                (f'<a href="{nt["url"]}">{nt["plain"]}</a>', g(nt['tpi']), f"{nt['D'] * IN:.3f}",
                 f"{nt['D']:.4f}", '60°', '1 in 16')]
        b.append(f'<section><h2>{name} against {lab} NPT</h2>'
                 f'<p>The American NPT thread of the same nominal size has {g(nt["tpi"])} threads per inch '
                 f'against {tpi}, a 60° flank angle and an outside diameter of {nt["D"] * IN:.3f} mm against '
                 f'{t["d"]:.3f} mm. '
                 + ('The pitch is the same, so the parts start to screw together, but the flank angles differ '
                    'and the joint will not hold pressure. ' if same else 'The parts do not fit each other. ')
                 + 'Use an adapter.</p>'
                 + table(['Thread', 'TPI', 'Major Ø (mm)', 'Major Ø (in)', 'Flank angle', 'Taper'], rows,
                         'chart', label=f"{name} compared with {lab} NPT", rowcls=['rec', ''])
                 + '<p class="small"><a href="/npt-vs-bsp/">NPT vs BSP in detail</a></p></section>')

    links = []
    if prev:
        links.append((f"← {prev['name']}", prev['url']))
    if nxt:
        links.append((f"{nxt['name']} →", nxt['url']))
    links += [('All BSP sizes', '/bsp/'), ('NPT thread chart', '/pipe-threads/'),
              ('Tap drill chart', '/tap-drill-chart/'), ('Thread identifier', '/thread-identifier/')]
    b.append('<section><h2>Related sizes and tools</h2>' + chips(links) + '</section>')
    b.append(f'<p class="small muted">Sources: ISO 228-1 (dimensions and sealing principle), ISO 7-1 (taper '
             f'threads), tap manufacturers’ drill charts. <a href="/about/#sources">How this site checks its '
             f'data</a>. Last reviewed {TODAY_TEXT}.</p>')
    schema = [webpage_ld(t['url'], title, desc, {'@type': 'Thing', 'name': f"{name} pipe thread"})]
    return page(t['url'], title, desc, '\n'.join(b), trail=[('BSP Threads', '/bsp/'), (name, None)],
                schema=schema, og_image='/pipe-threads/og-image.png')
