"""Chart (hub) pages, the combined tap drill chart and the home page."""
import svg
from detail60 import area
from shell import (IN, ORG, SITE, TODAY_TEXT, cards, chips, dataset_ld, e, g, page, table, webpage_ld)

XT_MM = [1, 2, 3, 5, 8, 12, 20, 36, 68]
XT_IN = [0.06, 0.125, 0.25, 0.5, 1, 2, 4]


def frac_in(v):
    return {0.06: '#0', 0.125: '1/8', 0.25: '1/4', 0.5: '1/2', 1: '1', 2: '2', 4: '4'}[v]


def faq(items):
    out = ['<section class="faq"><h2>Common questions</h2>']
    for q, a in items:
        out.append(f'<h3>{q}</h3><p>{a}</p>')
    out.append('</section>')
    return ''.join(out)


def src_line(text):
    return (f'<p class="small muted">Sources: {text}. <a href="/about/#sources">How this site checks its '
            f'data</a>. Last reviewed {TODAY_TEXT}.</p>')


def family_links(skip):
    allf = [('Metric coarse chart', '/metric/'), ('Metric fine chart', '/metric-fine/'),
            ('UNC chart', '/unc/'), ('UNF chart', '/unf/'), ('UNEF chart', '/unef/'),
            ('NPT chart', '/pipe-threads/'), ('BSP chart', '/bsp/'),
            ('Tap drill chart', '/tap-drill-chart/'), ('Thread calculator', '/calculator/'),
            ('Thread identifier', '/thread-identifier/')]
    return '<section><h2>Other charts and tools</h2>' + chips([l for l in allf if l[1] != skip]) + '</section>'


# ---------------------------------------------------------------- metric

def metric_plot(fams):
    coarse = [(t['d'], t['p'], f"{t['name']}: pitch {g(t['p'])} mm") for t in fams['metric']]
    fine = [(t['d'], t['p'], f"{t['name']}: pitch {g(t['p'])} mm") for t in fams['metric-fine']]
    return svg.series_plot(
        [('Coarse pitch', 's1', coarse, True), ('Fine pitches', 's2', fine, False)],
        'Nominal diameter (mm, log scale)', 'Pitch (mm)',
        'Pitch against nominal diameter for ISO metric threads. The coarse pitch rises in steps from '
        '0.25 mm at M1 to 6 mm at M64; fine pitches stay between 0.35 and 3 mm.',
        xfmt=lambda v: f"M{g(v)}", yfmt=lambda v: g(v), xticks=XT_MM, yticks=[1, 2, 3, 4, 5, 6])


def metric_hub(fams):
    ts = fams['metric']
    rows = []
    for t in ts:
        rows.append([f'<a href="{t["url"]}">{t["name"]}</a>', g(t['p']), f"{t['d2']:.3f}", f"{t['d1']:.3f}",
                     f"{t['d3']:.3f}", g(t['drill_mm'], 2), g(t['clear'][1]) if t['clear'] else '—',
                     area(t)[0], {1: '1st', 2: '2nd', 3: '3rd'}[t['choice']]])
    title = 'ISO Metric Thread Chart: M1 to M68 Coarse, Tap Drills'
    desc = ('Tap drills for all 36 ISO metric coarse threads, M1 to M68. M6: 5 mm; M8: 6.8 mm; M10: 8.5 mm; '
            'M12: 10.2 mm. Pitch Ø, minor Ø, clearance hole and stress area.')
    b = ['<h1>ISO Metric Coarse Thread Chart</h1>',
         '<p class="lead">All 36 coarse-pitch ISO metric threads from M1 to M68, with pitch, basic diameters, '
         'tap drill, clearance hole and tensile stress area. A metric thread written without a pitch, such as '
         'M10, means the coarse pitch in this chart.</p>',
         table(['Thread', 'Pitch (mm)', 'Pitch Ø d2', 'Minor Ø D1', 'Root Ø d3', 'Tap drill (mm)',
                'Clearance hole', 'Stress area (mm²)', 'ISO 261 choice'], rows, 'chart',
               label='ISO metric coarse thread chart',
               caption='Diameters in mm. Clearance hole is the ISO 273 medium series.'),
         '<p class="small">Finer pitches on the same diameters are in the '
         '<a href="/metric-fine/">metric fine thread chart</a>.</p>',
         '<section><h2>How pitch grows with diameter</h2>'
         + svg.figure(metric_plot(fams), 'Each diameter has one coarse pitch (green, joined) and up to three '
                                         'fine pitches (orange). Hover or tap a point for the thread.', 'wide')
         + '<p>The coarse pitch is not a fixed fraction of the diameter. It is about a quarter of the '
           'diameter at M1, a seventh at M10 and less than a tenth at M64, so small coarse threads are '
           'proportionally much deeper than large ones.</p></section>',
         '<section><h2>Reading the chart</h2>'
         '<p><strong>Pitch diameter d<sub>2</sub></strong> is where the thread ridge and the groove are equally '
         'wide; it is the diameter that decides whether a nut and bolt fit. '
         '<strong>Minor diameter D<sub>1</sub></strong> is the basic bore of the nut thread and the lower limit '
         'for a tapped hole. <strong>Root diameter d<sub>3</sub></strong> is the bottom of the bolt thread with '
         'its rounded root, used for strength calculations.</p>'
         '<p><strong>ISO 261 choice</strong> ranks the diameters. First-choice sizes are the ones to design '
         'with; second and third choice sizes (M7, M9, M14, M18, M22 and so on) are standard but stocked less '
         'widely.</p>'
         '<p>All values are basic sizes, before tolerances. Each thread page gives the 6g and 6H limits, a '
         'range of usable tap drills and proof loads by property class.</p></section>',
         faq([('What is the tap drill for M8?',
               'The tap drill for M8×1.25 is 6.8 mm. The rule is diameter minus pitch, 8 − 1.25 = 6.75 mm, '
               'rounded to the stocked 6.8 mm drill. It leaves about 74% thread.'),
              ('Is M10 the same as M10×1.5?',
               'Yes. When no pitch is given the coarse pitch is meant, and the coarse pitch of M10 is 1.5 mm. '
               'M10×1.25 and M10×1 are fine-pitch threads and need different taps and nuts.'),
              ('Why is there no clearance hole for M9?',
               'ISO 273 does not list the 9 mm size. M9 is a third-choice diameter that new designs avoid.')]),
         family_links('/metric/'),
         src_line('ISO 261 (pitches and choice), ISO 724 (basic dimensions), ISO 273 (clearance holes), '
                  'ISO 898-1 (stress areas) and tap drill tables based on ISO 2306')]
    schema = [dataset_ld('/metric/', 'ISO metric coarse thread dimensions, M1 to M68', desc,
                         ['pitch', 'pitch diameter', 'minor diameter', 'tap drill diameter',
                          'clearance hole diameter', 'tensile stress area'],
                         'ISO 261, ISO 724, ISO 273, ISO 898-1')]
    return page('/metric/', title, desc, '\n'.join(b), trail=[('Metric Coarse', None)], schema=schema,
                og_image='/metric/og-image.png', wide=True)


def metric_fine_hub(fams):
    ts = fams['metric-fine']
    rows = []
    for t in ts:
        flag = ' *' if t['note'] else ''
        rows.append([f'<a href="{t["url"]}">{t["name"]}</a>{flag}', g(t['p']), f"{t['d2']:.3f}",
                     f"{t['d1']:.3f}", f"{t['d3']:.3f}", g(t['drill_mm'], 2),
                     g(t['clear'][1]) if t['clear'] else '—', area(t)[0]])
    title = 'ISO Metric Fine Thread Chart: M3 to M48, Tap Drills'
    desc = ('Tap drills for 56 ISO metric fine threads, M3×0.35 to M48×3. M8×1: 7 mm; M10×1.25: 8.8 mm; '
            'M12×1.5: 10.5 mm; M14×1.5: 12.5 mm. Pitch Ø, minor Ø and stress area.')
    b = ['<h1>ISO Metric Fine Thread Chart</h1>',
         '<p class="lead">Fine-pitch ISO metric threads from M3×0.35 to M48×3, with basic diameters, tap drill, '
         'clearance hole and tensile stress area. A fine thread is always written with its pitch, because a '
         'diameter can have up to three of them.</p>',
         table(['Thread', 'Pitch (mm)', 'Pitch Ø d2', 'Minor Ø D1', 'Root Ø d3', 'Tap drill (mm)',
                'Clearance hole', 'Stress area (mm²)'], rows, 'chart', label='ISO metric fine thread chart',
               caption='Diameters in mm. * see the note on the thread page: restricted or non-standard pitch.'),
         '<p class="small">The default pitch for each diameter is in the '
         '<a href="/metric/">metric coarse thread chart</a>.</p>',
         '<section><h2>Which fine pitches exist</h2>'
         '<p>ISO 261 assigns each diameter a short list of fine pitches rather than one. Up to M7 there is a '
         'single fine pitch; from M8 there are two or three. The same few pitches repeat across diameters: '
         '1 mm, 1.5 mm, 2 mm and 3 mm cover almost everything from M8 to M48, which keeps the number of taps '
         'and gauges down.</p>'
         '<p>Three entries in this chart carry a warning. M14×1.25 is listed by ISO 261 for spark plugs only, '
         'M33×3 is a pitch the standard asks designers to avoid, and M16×1.25 is not in ISO 261 at all.</p></section>',
         '<section><h2>What a fine pitch changes</h2>'
         '<p>At the same diameter a finer pitch makes the thread shallower. The core of the bolt is larger, so '
         'the tensile stress area goes up: M12×1.25 has 92.1 mm² against 84.3 mm² for coarse M12, about 9% more. '
         'The lead angle is smaller, so the thread resists loosening better and gives finer adjustment per turn. '
         'The cost is slower assembly, more sensitivity to damaged or plated threads, and a weaker nut thread in '
         'soft materials.</p>'
         '<p class="small"><a href="/coarse-vs-fine/">Coarse vs fine threads compared in detail</a></p></section>',
         faq([('What is the tap drill for M10×1.25?',
               'Diameter minus pitch gives 10 − 1.25 = 8.75 mm. Most tap drill tables round this to 8.8 mm, '
               'and either drill leaves about 75% thread.'),
              ('What is the tap drill for M12×1.5?',
               'The tap drill for M12×1.5 is 10.5 mm, which is 12 − 1.5 exactly.'),
              ('Do fine threads use the same clearance hole?',
               'Yes. The clearance hole depends only on the diameter, so M10×1 and M10×1.5 both use 11 mm in '
               'the ISO 273 medium series.')]),
         family_links('/metric-fine/'),
         src_line('ISO 261 (pitches), ISO 724 (basic dimensions), ISO 273 (clearance holes), ISO 898-1 '
                  '(stress areas) and tap drill tables based on ISO 2306')]
    schema = [dataset_ld('/metric-fine/', 'ISO metric fine thread dimensions, M3 to M48', desc,
                         ['pitch', 'pitch diameter', 'minor diameter', 'tap drill diameter',
                          'tensile stress area'], 'ISO 261, ISO 724, ISO 273, ISO 898-1')]
    return page('/metric-fine/', title, desc, '\n'.join(b), trail=[('Metric Fine', None)], schema=schema,
                og_image='/metric/og-image.png', wide=True)


# ---------------------------------------------------------------- unified

def un_plot(fams):
    ser = []
    for fam, cls, nm in (('unc', 's1', 'UNC'), ('unf', 's2', 'UNF'), ('unef', 's3', 'UNEF')):
        ser.append((nm, cls, [(t['d'], t['tpi'], f"{t['name']}: {g(t['tpi'])} threads per inch")
                              for t in fams[fam]], False))
    return svg.series_plot(
        ser, 'Major diameter (in, log scale)', 'Threads per inch (log scale)',
        'Threads per inch against diameter for the UNC, UNF and UNEF series. At every diameter UNC has '
        'the fewest threads per inch and UNEF the most.',
        ylog=True, xfmt=frac_in, yfmt=lambda v: g(v), xticks=XT_IN, yticks=[4, 8, 16, 32, 64])


UN_TEXT = {
    'unc': {
        'title': 'UNC Thread Chart: 33 Sizes, Tap Drills & Pitch Diameters',
        'desc': ('Tap drills for all 33 UNC threads, #1-64 to 4-4. 1/4-20: #7; 3/8-16: 5/16; 1/2-13: 27/64; '
                 '3/4-10: 21/32. Major, pitch and minor Ø, stress area per ASME B1.1.'),
        'h1': 'UNC Thread Chart (Unified Coarse)',
        'lead': ('All 33 Unified coarse threads from #1-64 to 4-4, with diameters, tap drill and tensile stress '
                 'area. UNC is the default inch thread: a bolt described only by its diameter, such as a 1/2 inch '
                 'bolt, is normally 1/2-13 UNC.'),
        'about': ('<p>The coarse series has the fewest threads per inch that ASME B1.1 assigns to each '
                  'diameter. The threads are deep relative to the diameter, which makes them quick to assemble, '
                  'tolerant of dirt, burrs and plating, and strong in soft materials such as cast iron and '
                  'aluminium, where the nut thread is the weak part of the joint.</p>'
                  '<p>The series starts at #1. There is no #0 coarse thread: #0-80 belongs to the fine '
                  'series. Above 1 inch, the 8-thread series (8 UN) is often used in place of UNC for high-'
                  'pressure bolting, because its pitch stays constant as the diameter grows.</p>'),
        'faq': [('What is the tap drill for 1/4-20?',
                 'The tap drill for 1/4-20 UNC is a #7 drill, 0.2010 in (5.11 mm). It leaves about 75% thread.'),
                ('What is the tap drill for 3/8-16?',
                 'The tap drill for 3/8-16 UNC is 5/16 in, 0.3125 in (7.94 mm), for about 77% thread.'),
                ('What does 1/4-20 mean?',
                 'The first number is the major diameter in inches and the second is the number of threads '
                 'per inch. 1/4-20 is a 0.250 in thread with 20 threads per inch, a pitch of 0.050 in.')],
    },
    'unf': {
        'title': 'UNF Thread Chart: 24 Sizes, Tap Drills & Pitch Diameters',
        'desc': ('Tap drills for all 24 UNF threads, #0-80 to 1-1/2-12. #10-32: #21; 1/4-28: #3; 3/8-24: Q; '
                 '1/2-20: 29/64. Major, pitch and minor Ø, stress area per ASME B1.1.'),
        'h1': 'UNF Thread Chart (Unified Fine)',
        'lead': ('All 24 Unified fine threads from #0-80 to 1-1/2-12, with diameters, tap drill and tensile '
                 'stress area. UNF is the fine-pitch alternative to UNC and the usual choice in automotive and '
                 'aerospace fasteners.'),
        'about': ('<p>A fine thread is shallower than the coarse thread of the same diameter, so the bolt has '
                  'a larger core. 1/2-20 UNF has a stress area of 0.1599 in² against 0.1419 in² for 1/2-13 UNC, '
                  'about 13% more. The smaller lead angle also resists loosening under vibration and gives finer '
                  'adjustment.</p>'
                  '<p>The fine series ends at 1-1/2 in. Above that, ASME B1.1 continues it with the '
                  '12-thread series (12 UN). The thread sold as “1-14 UNF” is a common misnomer: the standard '
                  'fine thread for 1 inch is 1-12, and 1-14 is a special (UNS) thread.</p>'),
        'faq': [('What is the tap drill for 1/4-28?',
                 'The tap drill for 1/4-28 UNF is a #3 drill, 0.2130 in (5.41 mm), for about 80% thread.'),
                ('What is the tap drill for 10-32?',
                 'The tap drill for #10-32 UNF is a #21 drill, 0.1590 in (4.04 mm), for about 76% thread.'),
                ('Is UNF stronger than UNC?',
                 'The bolt is stronger in tension, by roughly 10 to 15%, because its core is larger. The nut '
                 'thread is more easily stripped in soft material, so coarse threads are preferred in aluminium '
                 'and cast iron.')],
    },
    'unef': {
        'title': 'UNEF Thread Chart: 25 Extra Fine Sizes, Tap Drills & TPI',
        'desc': ('Tap drills for all 25 UNEF extra fine threads, #12-32 to 1-11/16-18. 1/4-32: 7/32; '
                 '1/2-28: 15/32; 3/4-20: 45/64; 1-20: 61/64. Diameters per ASME B1.1.'),
        'h1': 'UNEF Thread Chart (Unified Extra Fine)',
        'lead': ('All 25 Unified extra fine threads from #12-32 to 1-11/16-18, with diameters, tap drill and '
                 'tensile stress area. UNEF is used where the thread must be shallow: thin-walled tubes, '
                 'adjusting screws, bearing retaining nuts and instrument fittings.'),
        'about': ('<p>The extra fine series has the most threads per inch of the three standard series. '
                  'At 1 inch it has 20 threads per inch against 12 for UNF and 8 for UNC, so the thread is less '
                  'than half as deep as the coarse one and can be cut in a wall that a coarse thread would '
                  'break through.</p>'
                  '<p>Half of the UNEF sizes are secondary sizes in ASME B1.1 (the odd sixteenths such as '
                  '11/16, 13/16 and 1-1/16). Above 1-11/16 in the standard continues the series with the '
                  '16-thread series (16 UN).</p>'),
        'faq': [('What is the tap drill for 1/2-28?',
                 'The tap drill for 1/2-28 UNEF is 15/32 in, 0.4688 in (11.91 mm), for about 67% thread.'),
                ('What is the tap drill for 1/4-32?',
                 'The tap drill for 1/4-32 UNEF is 7/32 in, 0.2188 in (5.56 mm), for about 77% thread.'),
                ('Where are UNEF threads used?',
                 'On thin-walled parts and for fine adjustment: instrument and optical mounts, bearing '
                 'lock nuts, hydraulic tube fittings and electrical connectors.')],
    },
}


def un_hub(fam, fams):
    ts = fams[fam]
    x = UN_TEXT[fam]
    rows = []
    for t in ts:
        rows.append([f'<a href="{t["url"]}">{t["name"]}</a>', g(t['tpi']), f"{t['d']:.4f}",
                     f"{t['d2']:.4f}", f"{t['d1']:.4f}", t['drill_name'], f"{t['drill_in']:.4f}",
                     f"{t['drill_mm']:.2f}", f"{t['drill_pct']:.0f}%", area(t)[1]])
    b = [f'<h1>{x["h1"]}</h1>', f'<p class="lead">{x["lead"]}</p>',
         table(['Thread', 'TPI', 'Major Ø (in)', 'Pitch Ø (in)', 'Minor Ø D1 (in)', 'Tap drill',
                'Drill (in)', 'Drill (mm)', '% thread', 'Stress area (in²)'], rows, 'chart',
               label=f'{fam.upper()} thread chart',
               caption='Basic sizes per ASME B1.1. Minor Ø is the basic minor diameter of the internal thread.'),
         f'<section><h2>About the {fam.upper()} series</h2>{x["about"]}</section>',
         '<section><h2>Threads per inch by series</h2>'
         + svg.figure(un_plot(fams), 'UNC (green), UNF (orange) and UNEF (blue) on the same axes. Hover or tap '
                                     'a point for the thread.', 'wide')
         + '</section>',
         faq(x['faq']),
         family_links(f'/{fam}/'),
         src_line('ASME B1.1 (series, basic dimensions and stress areas) and the tap drill tables of '
                  'Machinery’s Handbook')]
    schema = [dataset_ld(f'/{fam}/', f'{fam.upper()} thread dimensions and tap drills', x['desc'],
                         ['threads per inch', 'major diameter', 'pitch diameter', 'minor diameter',
                          'tap drill diameter', 'tensile stress area'], 'ASME B1.1')]
    og = '/unf/og-image.png' if fam == 'unf' else '/unc/og-image.png'
    return page(f'/{fam}/', x['title'], x['desc'], '\n'.join(b), trail=[(fam.upper(), None)], schema=schema,
                og_image=og, wide=True)


# ---------------------------------------------------------------- pipe

def npt_hub(fams):
    ts = fams['npt']
    rows = []
    for t in ts:
        m = t['main']
        rows.append([f'<a href="{t["url"]}">{t["plain"]}</a>', g(t['tpi']), f"{t['D']:.3f}",
                     f"{t['D'] * IN:.2f}", m['name'] if m else '—',
                     t['std']['name'] if t['std'] else '—', f"{t['E0']:.5f}", f"{t['E1']:.5f}",
                     f"{t['L1']:.3f}", f"{t['L2']:.4f}", f"{t['K0']:.4f}"])
    title = 'NPT Thread Chart: 19 Sizes, Tap Drills & OD, ASME B1.20.1'
    desc = ('NPT pipe thread chart, 1/16 to 12 in: TPI, pipe OD, pitch diameters and tap drills. 1/4 NPT: 7/16; '
            '1/2 NPT: 23/32; 3/4 NPT: 59/64; 1 NPT: 1-5/32. ASME B1.20.1.')
    ex = next(t for t in ts if t['label'] == '1/2')
    b = ['<h1>NPT Thread Chart (National Pipe Taper)</h1>',
         '<p class="lead">All 19 NPT sizes from 1/16 to 12 inch, with threads per inch, pipe outside diameter, '
         'pitch diameters, engagement lengths and tap drills from ASME B1.20.1. NPT is the taper pipe thread '
         'used in the United States and Canada.</p>',
         table(['Thread', 'TPI', 'Pipe OD (in)', 'Pipe OD (mm)', 'Tap drill', 'ASME B1.20.1 drill', 'E0 (in)',
                'E1 (in)', 'L1 (in)', 'L2 (in)', 'K0 (in)'], rows, 'chart', label='NPT thread chart',
               caption='Tap drill: the size on standard charts. ASME B1.20.1 drill: the size the standard '
                       'suggests for tapping without reaming. E0, E1: pitch diameter at the pipe end and at the hand-tight plane. L1: hand-tight '
                       'engagement. L2: effective thread length. K0: minor diameter at the pipe end.'),
         '<section><h2>Where the diameters are measured</h2>'
         + svg.figure(svg.npt_view(ex, lambda v, nd=5: f"{v:.{nd}f}"),
                      '1/2-14 NPT as an example. The pitch diameter grows by 1/16 in for every inch along '
                      'the axis; the taper is exaggerated in the drawing.', 'wide')
         + '<p>Because the thread is tapered it has no single pitch diameter. E<sub>0</sub> is the pitch '
           'diameter at the end of the pipe, E<sub>1</sub> at the plane where a fitting stops when screwed '
           'on by hand, and E<sub>2</sub> at the end of the effective thread. The three are tied together by '
           'the taper: E<sub>1</sub> = E<sub>0</sub> + L<sub>1</sub> ÷ 16.</p></section>',
         '<section><h2>Two tap drill columns</h2>'
         '<p>The chart gives two drills because published sources differ. The first column is the size '
         'printed on standard tap drill charts and in Machinery’s Handbook, and is the one most shops '
         'use. The second is the drill ASME B1.20.1 suggests in its appendix for tapping without reaming, '
         'which the standard lists up to the 2-1/2 size.</p>'
         '<p>Where the two differ, the chart size is the larger by 1/64 in. It taps more easily but leaves '
         'shallower threads at the bottom of the hole, so the smaller drill is the better choice for high '
         'pressure or soft material.</p>'
         '<p>No drill is published for 8, 10 and 12 inch NPT. Threads of that size are bored or milled to the '
         'minor diameter K<sub>0</sub>.</p></section>',
         '<section><h2>Nominal size is not a dimension</h2>'
         '<p>NPT sizes name the pipe, following the nominal pipe size (NPS) system. A 1/2 NPT thread is cut '
         'on pipe with an outside diameter of 0.840 in (21.34 mm), and nothing on it measures half an inch. '
         'To identify a pipe thread, measure the outside diameter and count the threads per inch, then match '
         'them to the chart.</p>'
         '<p class="small"><a href="/thread-identifier/">Identify a thread from measurements</a> · '
         '<a href="/npt-vs-bsp/">NPT vs BSP</a></p></section>',
         faq([('What is the tap drill for 1/4 NPT?',
               'The tap drill for 1/4-18 NPT is 7/16 in (0.4375 in, 11.11 mm). The standard and the usual '
               'shop charts agree on this size.'),
              ('What is the tap drill for 1/2 NPT?',
               'The tap drill for 1/2-14 NPT is 23/32 in (0.7188 in, 18.26 mm). ASME B1.20.1 suggests the '
               'slightly smaller 45/64 in (0.7031 in), which is harder to tap but leaves a fuller thread.'),
              ('Do NPT threads need sealant?',
               'Yes. NPT threads wedge together but leave a spiral leak path at the crests and roots, so '
               'ASME B1.20.1 calls for a sealant such as PTFE tape or pipe compound for a pressure-tight '
               'joint. NPTF (Dryseal) threads are made to seal without it.')]),
         family_links('/pipe-threads/'),
         src_line('ASME B1.20.1 Table 2 (dimensions) and Appendix (suggested drills), Machinery’s Handbook '
                  '(shop tap drill chart)')]
    schema = [dataset_ld('/pipe-threads/', 'NPT pipe thread dimensions and tap drills', desc,
                         ['threads per inch', 'pipe outside diameter', 'pitch diameter', 'engagement length',
                          'tap drill diameter'], 'ASME B1.20.1')]
    return page('/pipe-threads/', title, desc, '\n'.join(b), trail=[('NPT Pipe Threads', None)], schema=schema,
                og_image='/pipe-threads/og-image.png', wide=True)


def bsp_hub(fams):
    ts = fams['bsp']
    rows = []
    for t in ts:
        flag = '' if t['in_iso'] else ' *'
        rows.append([f'<a href="{t["url"]}">{t["name"]}</a>{flag}', str(t['tpi']), f"{t['p']:.3f}",
                     f"{t['d']:.3f}", f"{t['d2']:.3f}", f"{t['d1']:.3f}", f"{t['d'] / IN:.4f}",
                     g(t['drill_mm'], 2)])
    ex = next(t for t in ts if t['label'] == '1/2')
    labels = {'p': f"P = {ex['p']:.3f} mm", 'maj': ('major Ø d', f"{ex['d']:.3f} mm"),
              'pit': ('pitch Ø d2', f"{ex['d2']:.3f} mm"), 'min': ('minor Ø d1', f"{ex['d1']:.3f} mm"),
              'h': f"h = {ex['h']:.3f} mm", 'r': f"r = {ex['r']:.3f}"}
    title = 'BSP G Thread Chart: 21 Sizes, Tap Drills & OD, ISO 228-1'
    desc = ('BSP parallel (G) thread chart, G1/16 to G4: TPI, diameters and tap drills. G1/4: 11.8 mm; '
            'G1/2: 19 mm; G3/4: 24.5 mm; G1: 30.75 mm. 55° Whitworth, ISO 228-1.')
    b = ['<h1>BSP Thread Chart (British Standard Pipe, G)</h1>',
         '<p class="lead">Parallel BSP threads from G1/16 to G4, with threads per inch, basic diameters and tap '
         'drills from ISO 228-1. BSP is the pipe thread of Europe, Asia, Australia and most of the world outside '
         'North America.</p>',
         table(['Thread', 'TPI', 'Pitch (mm)', 'Major Ø (mm)', 'Pitch Ø (mm)', 'Minor Ø (mm)',
                'Major Ø (in)', 'Tap drill (mm)'], rows, 'chart', label='BSP thread chart',
               caption='Basic sizes per ISO 228-1. * G1-3/8 is not in ISO 228-1; values from manufacturers’ tables.'),
         '<section><h2>The Whitworth form</h2>'
         + svg.figure(svg.bsp_view(labels, 'Whitworth profile of G1/2: 55 degree flanks with rounded crests and '
                                           'roots, pitch 1.814 mm, major diameter 20.955 mm.'),
                      'G1/2 as an example. Every BSP thread has the same proportions: height 0.640 × pitch, '
                      'radius 0.137 × pitch.')
         + '<p>BSP threads use the Whitworth profile: flanks at 55° with the crests and roots rounded to a '
           'radius. Only four pitches cover the whole range: 28 threads per inch for G1/16 and G1/8, 19 for G1/4 '
           'and G3/8, 14 from G1/2 to G7/8, and 11 from G1 upward.</p></section>',
         '<section><h2>G, R, Rc and Rp</h2>'
         '<p><strong>G</strong> is the parallel thread of ISO 228-1, also called BSPP. It does not seal on '
         'the thread; the joint is made with a washer or O-ring against a face.</p>'
         '<p><strong>R</strong> (male taper), <strong>Rc</strong> (female taper) and <strong>Rp</strong> '
         '(female parallel) are the threads of ISO 7-1 and EN 10226, also called BSPT. They have the same '
         'pitch and form as G and the same diameters at the gauge plane, but they seal on the thread and '
         'need a sealant.</p>'
         '<p>A letter after the size of an external G thread gives its tolerance class: G1/2 A is the '
         'tighter class, G1/2 B the looser one. Internal G threads have one class and carry no letter.</p>'
         '<p class="small"><a href="/npt-vs-bsp/">NPT vs BSP</a> · '
         '<a href="/thread-identifier/">Identify a thread from measurements</a></p></section>',
         faq([('What is the tap drill for G1/4?',
               'The tap drill for G1/4 (1/4 BSP parallel) is 11.8 mm. The basic minor diameter is 11.445 mm, '
               'and the tolerance on it lies entirely above that size.'),
              ('What is the tap drill for G1/2?',
               'The tap drill for G1/2 is 19 mm, against a basic minor diameter of 18.631 mm.'),
              ('Is BSP the same as NPT?',
               'No. BSP has 55° flanks with rounded crests, NPT has 60° flanks with flat crests, and only the '
               '1/2 and 3/4 sizes share the same 14 threads per inch. They do not seal together.')]),
         family_links('/bsp/'),
         src_line('ISO 228-1 Table 1 (dimensions), ISO 7-1 (taper threads) and tap manufacturers’ drill '
                  'charts')]
    schema = [dataset_ld('/bsp/', 'BSP parallel (G) pipe thread dimensions and tap drills', desc,
                         ['threads per inch', 'pitch', 'major diameter', 'pitch diameter', 'minor diameter',
                          'tap drill diameter'], 'ISO 228-1')]
    return page('/bsp/', title, desc, '\n'.join(b), trail=[('BSP Threads', None)], schema=schema,
                og_image='/pipe-threads/og-image.png', wide=True)


# ---------------------------------------------------------------- tap drill chart

def tap_chart(fams):
    secs = ['<h1>Tap Drill Size Chart</h1>',
            '<p class="lead">Tap drill sizes for 214 threads: ISO metric coarse and fine, UNC, UNF, UNEF, NPT '
            'and BSP. Each drill is given in millimetres and inches with the percentage of thread it leaves.</p>',
            chips([('Metric coarse', '#metric'), ('Metric fine', '#metric-fine'), ('UNC', '#unc'),
                   ('UNF', '#unf'), ('UNEF', '#unef'), ('NPT', '#npt'), ('BSP', '#bsp'),
                   ('Choosing a percentage', '#percent')])]

    def m_rows(ts):
        return [[f'<a href="{t["url"]}">{t["name"]}</a>', g(t['drill_mm'], 2), f"{t['drill_in']:.4f}",
                 f"{t['drill_pct']:.0f}%", f"{t['d1']:.3f}"] for t in ts]

    def u_rows(ts):
        return [[f'<a href="{t["url"]}">{t["name"]}</a>', t['drill_name'], f"{t['drill_in']:.4f}",
                 f"{t['drill_mm']:.2f}", f"{t['drill_pct']:.0f}%", f"{t['d1']:.4f}"] for t in ts]

    mh = ['Thread', 'Tap drill (mm)', 'Drill (in)', '% thread', 'Minor Ø D1 (mm)']
    uh = ['Thread', 'Tap drill', 'Drill (in)', 'Drill (mm)', '% thread', 'Minor Ø D1 (in)']
    secs.append('<section id="metric"><h2>ISO metric coarse tap drills</h2>'
                + table(mh, m_rows(fams['metric']), 'chart', label='Metric coarse tap drills')
                + '<p class="small"><a href="/metric/">Full metric coarse chart</a></p></section>')
    secs.append('<section id="metric-fine"><h2>ISO metric fine tap drills</h2>'
                + table(mh, m_rows(fams['metric-fine']), 'chart', label='Metric fine tap drills')
                + '<p class="small">For 0.75 mm and 1.25 mm pitches, tables round diameter minus pitch to a '
                  '0.1 mm drill (8.75 becomes 8.8); either size works. '
                  '<a href="/metric-fine/">Full metric fine chart</a></p></section>')
    for fam in ('unc', 'unf', 'unef'):
        secs.append(f'<section id="{fam}"><h2>{fam.upper()} tap drills</h2>'
                    + table(uh, u_rows(fams[fam]), 'chart', label=f'{fam.upper()} tap drills')
                    + f'<p class="small"><a href="/{fam}/">Full {fam.upper()} chart</a></p></section>')
    rows = []
    for t in fams['npt']:
        s, r, c = t['std'], t['ream'], t['common']
        rows.append([f'<a href="{t["url"]}">{t["plain"]}</a>',
                     c['name'] if c else '—', f"{c['in']:.4f}" if c else '—', f"{c['mm']:.2f}" if c else '—',
                     s['name'] if s else '—', r['name'] if r else '—', f"{t['K0']:.4f}"])
    secs.append('<section id="npt"><h2>NPT tap drills</h2>'
                + table(['Thread', 'Tap drill', 'Drill (in)', 'Drill (mm)', 'ASME B1.20.1, no reaming',
                         'ASME B1.20.1, before reaming', 'Minor Ø K0 (in)'], rows, 'chart',
                        label='NPT tap drills',
                        caption='Tap drill: standard shop charts and Machinery’s Handbook. The two ASME '
                                'columns are the drills suggested in the appendix of ASME B1.20.1.')
                + '<p class="small"><a href="/pipe-threads/">Full NPT chart and why the columns differ</a></p></section>')
    rows = [[f'<a href="{t["url"]}">{t["name"]}</a>', g(t['drill_mm'], 2), f"{t['drill_in']:.4f}",
             f"{(t['d'] - t['drill_mm']) / (2 * t['h']) * 100:.0f}%", f"{t['d1']:.3f}"] for t in fams['bsp']]
    secs.append('<section id="bsp"><h2>BSP (G) tap drills</h2>'
                + table(mh[:4] + ['Minor Ø (mm)'], rows, 'chart', label='BSP tap drills')
                + '<p class="small"><a href="/bsp/">Full BSP chart</a></p></section>')

    m8 = next(t for t in fams['metric'] if t['name'] == 'M8×1.25')
    prow = []
    for pct in (100, 90, 83, 77, 70, 65, 60, 50):
        dr = m8['d'] - pct / 100 * 1.299038 * m8['p']
        prow.append([f"{pct}%", f"{dr:.2f}", f"{pct / 100 * 0.649519 * m8['p']:.3f}",
                     'hole below the minimum minor Ø: not usable' if pct >= 90 else
                     'basic minor Ø, the smallest allowed hole' if pct == 83 else
                     'standard tap drill (diameter minus pitch)' if pct == 77 else
                     'easier tapping, general work' if pct == 70 else
                     'stainless, tough alloys, deep holes' if pct in (65, 60) else
                     'thin sheet only'])
    secs.append('<section id="percent"><h2>What percentage of thread to use</h2>'
                '<p>The percentage of thread says how much of the full thread height is left in the hole. '
                'It is set only by the drill: a larger drill leaves less. The convention measures it against '
                'a height of 0.6495 × pitch, so</p>'
                '<div class="panel"><p><strong>% thread = (major diameter − drill diameter) ÷ (1.299 × pitch) '
                '× 100</strong></p><p>and, turned around, drill = major diameter − % × 1.299 × pitch.</p></div>'
                '<p>Standard tap drills sit at 70 to 80%. The metric rule of diameter minus pitch gives exactly '
                '77%, or a little less once it is rounded up to a stocked drill. Going above 80% raises the tapping torque sharply and gains very little strength, because '
                'in a nut of normal height the bolt usually breaks before a 60% thread strips. Going below 60% starts '
                'to cost strength.</p>'
                + table(['% thread', 'Drill for M8×1.25 (mm)', 'Thread height left (mm)', 'Typical use'], prow,
                        'chart', label='Drill diameter against percentage of thread for M8×1.25',
                        rowcls=['', '', '', 'rec', '', '', '', ''])
                + '<p>Three practical rules: use the charted drill in mild steel, brass and aluminium; go one '
                  'drill size larger in stainless steel, titanium and hardened material; and check that the '
                  'hole stays inside the minor diameter limits of the thread class, which each thread page '
                  'lists.</p>'
                  '<p>Thread-forming (roll) taps displace metal instead of cutting it and need a larger hole, '
                  'close to the pitch diameter. The drills in this chart are for cutting taps only.</p></section>')
    secs.append(faq([
        ('What size drill for an M6 tap?', 'A 5 mm drill. M6×1 coarse: 6 − 1 = 5 mm, which leaves 77% thread.'),
        ('What size drill for a 1/4-20 tap?', 'A #7 drill, 0.2010 in (5.11 mm). A 13/64 in drill (0.2031 in) '
                                              'is the nearest fractional size and leaves about 72% thread.'),
        ('Can I use a slightly larger drill than the chart says?',
         'Yes, within limits. One drill size larger typically drops the thread from about 77% to 65 to 70%, '
         'which costs little strength and makes tapping much easier. Stay inside the minor diameter limits '
         'given on the thread page.')]))
    secs.append(family_links('/tap-drill-chart/'))
    secs.append(src_line('tap drill tables based on ISO 2306, Machinery’s Handbook, ASME B1.20.1 Appendix '
                         'and tap manufacturers’ charts'))
    title = 'Tap Drill Chart: Metric, UNC, UNF, NPT & BSP Drill Sizes'
    desc = ('Tap drill sizes for 214 threads in mm and inches with % thread. M6: 5 mm; M8: 6.8 mm; M10: 8.5 mm; '
            '1/4-20: #7; 3/8-16: 5/16; 1/2-13: 27/64; 1/4 NPT: 7/16.')
    schema = [dataset_ld('/tap-drill-chart/', 'Tap drill sizes for metric, unified and pipe threads', desc,
                         ['tap drill diameter', 'percentage of thread', 'minor diameter'],
                         'ISO 2306, ASME B1.1, ASME B1.20.1, ISO 228-1')]
    return page('/tap-drill-chart/', title, desc, '\n'.join(secs), trail=[('Tap Drill Chart', None)],
                schema=schema, og_image='/tap-drill-chart/og-image.png', wide=True)


# ---------------------------------------------------------------- home

def home(fams):
    n = {k: len(v) for k, v in fams.items()}
    total = sum(n.values())
    pm = [t for t in fams['metric'] if t['d'] in (3, 4, 5, 6, 8, 10, 12, 16, 20, 24)]
    pu = [t for t in fams['unc'] if t['label'] in ('#6', '#8', '#10', '1/4', '5/16', '3/8', '1/2', '5/8',
                                                   '3/4', '1')]
    mrows = [[f'<a href="{t["url"]}">{t["name"]}</a>', g(t['p']), f"{t['d2']:.3f}", g(t['drill_mm'], 2),
              g(t['clear'][1]), area(t)[0]] for t in pm]
    urows = [[f'<a href="{t["url"]}">{t["name"]}</a>', g(t['tpi']), f"{t['d']:.4f}", f"{t['d2']:.4f}",
              t['drill_name'], f"{t['drill_mm']:.2f}"] for t in pu]
    labels = {'p': 'pitch P', 'maj': ('major', 'diameter'), 'pit': ('pitch', 'diameter'),
              'min': ('minor', 'diameter'), 'h': 'thread height', 'angle': '60°'}
    anat = svg.profile_view('thread', labels,
                            'Cross-section of a 60 degree screw thread showing the pitch between crests, the '
                            'major, pitch and minor diameters and the thread height.')
    b = ['<h1>Thread Dimensions and Tap Drill Reference</h1>',
         f'<p class="lead">Dimensions, tolerance limits and tap drills for {total} screw and pipe threads: ISO '
         f'metric, Unified inch (UNC, UNF, UNEF), NPT and BSP. Every value is checked against the governing '
         f'standard and shown in both millimetres and inches.</p>',
         cards([('ISO metric coarse', f"{n['metric']} sizes, M1 to M68. The default metric thread.", '/metric/'),
                ('ISO metric fine', f"{n['metric-fine']} sizes, M3×0.35 to M48×3.", '/metric-fine/'),
                ('UNC, Unified coarse', f"{n['unc']} sizes, #1-64 to 4-4.", '/unc/'),
                ('UNF, Unified fine', f"{n['unf']} sizes, #0-80 to 1-1/2-12.", '/unf/'),
                ('UNEF, Unified extra fine', f"{n['unef']} sizes, #12-32 to 1-11/16-18.", '/unef/'),
                ('NPT pipe threads', f"{n['npt']} sizes, 1/16 to 12 inch, taper.", '/pipe-threads/'),
                ('BSP pipe threads', f"{n['bsp']} sizes, G1/16 to G4, parallel.", '/bsp/'),
                ('Tap drill chart', 'Every tap drill on one page, with % thread.', '/tap-drill-chart/'),
                ('Thread identifier', 'Enter a diameter and pitch to find the thread.', '/thread-identifier/')]),
         '<section><h2>The parts of a thread</h2>'
         + svg.figure(anat, 'A nut (blue) on a bolt (grey). The pitch diameter is the one that decides '
                            'whether the two fit.')
         + '<p>Three diameters describe a thread. The <strong>major diameter</strong> is measured over the '
           'crests of the bolt and gives the thread its name. The <strong>minor diameter</strong> is the bore '
           'of the nut, and sets the tap drill. The <strong>pitch diameter</strong> lies between them, where '
           'ridge and groove are equally wide. The <strong>pitch</strong> is the distance from one crest to '
           'the next; inch threads state it as threads per inch.</p>'
           '<p class="small"><a href="/thread-terminology/">All thread terms explained</a></p></section>',
         '<section><h2>Common metric threads</h2>'
         + table(['Thread', 'Pitch (mm)', 'Pitch Ø (mm)', 'Tap drill (mm)', 'Clearance hole (mm)',
                  'Stress area (mm²)'], mrows, 'chart', label='Common metric threads')
         + '<p class="small"><a href="/metric/">All 36 metric coarse threads</a> · '
           '<a href="/metric-fine/">Metric fine threads</a></p></section>',
         '<section><h2>Common inch threads</h2>'
         + table(['Thread', 'TPI', 'Major Ø (in)', 'Pitch Ø (in)', 'Tap drill', 'Drill (mm)'], urows, 'chart',
                 label='Common UNC threads')
         + '<p class="small"><a href="/unc/">All 33 UNC threads</a> · <a href="/unf/">UNF threads</a> · '
           '<a href="/unef/">UNEF threads</a></p></section>',
         '<section><h2>Guides</h2>'
         + cards([('Coarse vs fine threads', 'What changes with the pitch, and when each is the better choice.',
                   '/coarse-vs-fine/'),
                  ('NPT vs BSP', 'Why the two pipe thread systems do not seal together.', '/npt-vs-bsp/'),
                  ('Thread calculator', 'Diameters, tap drill and stress area for any diameter and pitch.',
                   '/calculator/')])
         + '</section>',
         '<section><h2>Where the numbers come from</h2>'
         '<p>The diameters of metric and Unified threads are computed from the profile formulas of ISO 724 and '
         'ASME B1.1 and then compared with the tables printed in those standards. Tolerance limits follow '
         'ISO 965-1 and ASME B1.1. Pipe thread dimensions are taken from ASME B1.20.1 and ISO 228-1. Tap drills '
         'are conventions, not calculations, so they are taken from published drill tables and the source is '
         'named where tables disagree.</p>'
         '<p class="small"><a href="/about/">About this site and its sources</a></p></section>']
    title = 'Thread Specs & Tap Drill Charts: Metric, UNC, UNF, NPT, BSP'
    desc = (f'Dimensions and tap drills for {total} threads. M6: 5 mm drill; M8: 6.8 mm; M10: 8.5 mm; '
            f'1/4-20 UNC: #7; 1/2-13: 27/64. ISO metric, UNC, UNF, UNEF, NPT and BSP.')
    schema = [{'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'ThreadSpec.org',
               'url': SITE + '/', 'description': desc, 'inLanguage': 'en', 'publisher': ORG},
              dict({'@context': 'https://schema.org'}, **ORG)]
    return page('/', title, desc, '\n'.join(b), schema=schema, wide=True)
