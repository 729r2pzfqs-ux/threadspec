"""Guides, tools and site pages."""
import json

import svg
from detail60 import area
from hubs import faq, family_links, src_line
from shell import (IN, ORG, SITE, TODAY_TEXT, chips, e, g, page, table, webpage_ld)


# ---------------------------------------------------------------- NPT vs BSP

def npt_vs_bsp(fams):
    rows = []
    for n in fams['npt']:
        b = next((x for x in fams['bsp'] if x['label'] == n['label']), None)
        if not b:
            continue
        same = abs(b['tpi'] - n['tpi']) < 1e-9
        rows.append([n['label'], f'<a href="{n["url"]}">{g(n["tpi"])}</a>', f"{n['D'] * IN:.2f}",
                     f"{n['p'] * IN:.3f}", f'<a href="{b["url"]}">{b["tpi"]}</a>', f"{b['d']:.2f}",
                     f"{b['p']:.3f}", f"{b['d'] - n['D'] * IN:+.2f}", 'same' if same else 'different'])
    rc = ['rec' if r[-1] == 'same' else '' for r in rows]
    title = 'NPT vs BSP Pipe Threads: Angle, Taper & Compatibility'
    desc = ('NPT vs BSP: 60° flanks and a 1 in 16 taper against 55° Whitworth, parallel (G) or taper (R). '
            'Only 1/2 and 3/4 share 14 TPI, and even those do not seal together.')
    b = ['<h1>NPT vs BSP Pipe Threads</h1>',
         '<p class="lead">NPT and BSP are the two pipe thread systems in general use. They differ in flank '
         'angle, crest shape, pitch and diameter, so an NPT fitting does not seal in a BSP port even when the '
         'two appear to screw together. NPT is the standard in the United States and Canada; BSP is used almost '
         'everywhere else.</p>',
         table(['', 'NPT', 'BSP parallel (G, BSPP)', 'BSP taper (R, BSPT)'],
               [['Standard', 'ASME B1.20.1', 'ISO 228-1', 'ISO 7-1, EN 10226'],
                ['Flank angle', '60°', '55°', '55°'],
                ['Crests and roots', 'flat', 'rounded', 'rounded'],
                ['Thread height', '0.8 × pitch', '0.640 × pitch', '0.640 × pitch'],
                ['Taper', '1 in 16 on diameter', 'none', '1 in 16 on diameter'],
                ['Seals on', 'the thread, with sealant', 'a washer or O-ring at the face',
                 'the thread, with sealant'],
                ['Designation', '1/2-14 NPT', 'G1/2', 'R1/2 (male), Rc1/2, Rp1/2 (female)']],
               'chart', label='NPT and BSP compared', num_from=9),
         '<section><h2>Thread form</h2>'
         + svg.figure(svg.form_compare(), 'The two forms at the same pitch. NPT is deeper and sharper; BSP is '
                                          'shallower with rounded crests and roots.', 'wide')
         + '<p>The 5° difference in flank angle is the reason the two cannot share a gauge or a tap. An NPT '
           'male in a BSP female touches only at the crests, leaving the flanks apart, and a thread that does '
           'not bear on its flanks neither seals nor carries load properly.</p></section>',
         '<section><h2>How each one seals</h2>'
         + svg.figure(svg.seal_compare(), 'Taper threads seal along the thread itself. Parallel threads seal '
                                          'on a separate element outside the thread.', 'wide')
         + '<p><strong>Taper threads</strong> (NPT, and BSP taper R into Rc or Rp) wedge together as they are '
           'tightened. The wedging gives a mechanical lock, but the crests and roots still leave a spiral '
           'passage, so PTFE tape or pipe compound is needed to make the joint tight.</p>'
           '<p><strong>Parallel threads</strong> (BSP G) never wedge. ISO 228-1 defines them for joints where '
           'the seal is made outside the thread: a bonded washer, an O-ring in a groove or a flat gasket is '
           'clamped between the fitting and the face of the port.</p></section>',
         '<section><h2>Size by size</h2>'
         '<p>The nominal sizes look the same but the threads behind them differ. Only the 1/2 and 3/4 sizes have '
         'the same pitch in both systems.</p>'
         + table(['Size', 'NPT TPI', 'NPT OD (mm)', 'NPT pitch (mm)', 'BSP TPI', 'BSP major Ø (mm)',
                  'BSP pitch (mm)', 'BSP − NPT Ø (mm)', 'Pitch'], rows, 'chart',
                 label='NPT and BSP dimensions by size', rowcls=rc)
         + '<p>Where the pitch is the same, the male will enter the female for a couple of turns and feel as if '
           'it fits. This is the dangerous case: the joint can be tightened, but it holds on a few crests and '
           'leaks or blows out under pressure. Where the pitch differs by one thread per inch, the parts bind '
           'within two or three turns.</p></section>',
         '<section><h2>Telling them apart</h2><ol>'
         '<li>Count the threads per inch with a thread gauge. 27, 18, 11.5 or 8 means NPT. 28, 19 or 11 means '
         'BSP. 14 can be either.</li>'
         '<li>Look at the crests. Flat crests with sharp corners are NPT; smoothly rounded crests are BSP.</li>'
         '<li>Check for taper by measuring the diameter at the first and last full thread. NPT and BSP taper (R) '
         'narrow toward the end; BSP parallel (G) does not.</li>'
         '<li>Look for a sealing face. A machined flat or a groove for a washer or O-ring beside the thread means '
         'a parallel thread.</li>'
         '<li>Measure the outside diameter and compare it with the table above.</li></ol>'
         '<p class="small"><a href="/thread-identifier/">Identify a thread from measurements</a></p></section>',
         '<section><h2>Connecting NPT to BSP</h2>'
         '<p>Use an adapter with one thread of each kind. Adapters are stocked for every common size. Do not rely '
         'on extra tape to make mismatched threads hold pressure.</p></section>',
         faq([('Can I screw an NPT fitting into a BSP port?',
               'Not for a pressure-tight joint. In the 1/2 and 3/4 sizes the parts will engage because both have '
               '14 threads per inch, but the flank angles differ and the joint leaks. Use an adapter.'),
              ('Is BSP tapered or parallel?',
               'Both exist. G (BSPP) is parallel and seals on a washer. R, Rc and Rp (BSPT) are the taper system '
               'that seals on the thread.'),
              ('Which countries use NPT?',
               'The United States and Canada, and equipment built to American standards anywhere, particularly '
               'in oil and gas. Most other countries use BSP.')]),
         family_links('/npt-vs-bsp/'),
         src_line('ASME B1.20.1, ISO 228-1 and ISO 7-1')]
    return page('/npt-vs-bsp/', title, desc, '\n'.join(b), trail=[('NPT vs BSP', None)],
                schema=[webpage_ld('/npt-vs-bsp/', title, desc)], og_image='/pipe-threads/og-image.png')


# ---------------------------------------------------------------- coarse vs fine

def coarse_vs_fine(fams):
    def pair(c, f):
        gain = (f['As'] / c['As'] - 1) * 100
        m = c['system'] == 'metric'
        a = (lambda t: area(t)[0]) if m else (lambda t: area(t)[1])
        h = (lambda t: f"{t['h_int']:.3f}") if m else (lambda t: f"{t['h_int']:.4f}")
        return [f'<a href="{c["url"]}">{c["name"]}</a>', f'<a href="{f["url"]}">{f["name"]}</a>',
                f"{h(c)} / {h(f)}", f"{a(c)} / {a(f)}", f"+{gain:.0f}%", f"{c['lead']:.2f}° / {f['lead']:.2f}°"]
    mrows = []
    for d, p in ((8, 1), (10, 1.25), (12, 1.25), (12, 1.5), (16, 1.5), (20, 1.5), (24, 2)):
        c = next(t for t in fams['metric'] if t['d'] == d)
        f = next(t for t in fams['metric-fine'] if t['d'] == d and t['p'] == p)
        mrows.append(pair(c, f))
    urows = []
    for lab in ('#10', '1/4', '5/16', '3/8', '1/2', '5/8', '3/4', '1'):
        c = next(t for t in fams['unc'] if t['label'] == lab)
        f = next(t for t in fams['unf'] if t['label'] == lab)
        urows.append(pair(c, f))
    m10 = [t for k in ('metric', 'metric-fine') for t in fams[k] if t['d'] == 10]
    m10.sort(key=lambda t: -t['p'])
    fig = svg.pitch_compare([(t['name'], t['p'], t['h_int'], False) for t in m10], lambda v: f"{v:.3f} mm")
    title = 'Coarse vs Fine Threads: Strength, Pitch & When to Use Each'
    desc = ('Coarse vs fine threads compared with numbers: M10×1.25 has 6% more stress area than M10×1.5, '
            '1/2-20 UNF 13% more than 1/2-13 UNC. When each is the right choice.')
    b = ['<h1>Coarse vs Fine Threads</h1>',
         '<p class="lead">Every common bolt diameter comes in a coarse pitch and at least one fine pitch. The '
         'fine thread is shallower, so the bolt keeps a larger core and is stronger in tension; the coarse '
         'thread is deeper, faster to assemble and harder to damage. Coarse is the default, and fine is chosen '
         'for a reason.</p>',
         '<section><h2>The same diameter at four pitches</h2>'
         + svg.figure(fig, 'The four standard pitches of M10, drawn to the same scale with the crests aligned. '
                           'The finer the pitch, the shallower the groove and the more metal left in the core.',
                      'wide')
         + '</section>',
         '<section><h2>Metric: coarse against fine</h2>'
         + table(['Coarse', 'Fine', 'Thread height (mm)', 'Stress area (mm²)', 'Gain', 'Lead angle'], mrows,
                 'chart', label='Metric coarse and fine threads compared')
         + '</section>',
         '<section><h2>Inch: UNC against UNF</h2>'
         + table(['UNC', 'UNF', 'Thread height (in)', 'Stress area (in²)', 'Gain', 'Lead angle'], urows,
                 'chart', label='UNC and UNF threads compared')
         + '<p class="small muted">Each cell gives coarse / fine. Gain is the increase in tensile stress area '
           'from coarse to fine.</p></section>',
         '<section><h2>What the fine thread gains</h2><ul>'
         '<li><strong>Tensile strength of the bolt.</strong> The stress area is 4 to 15% larger, and the bolt '
         'carries that much more load at the same material strength.</li>'
         '<li><strong>Resistance to loosening.</strong> The lead angle is smaller, so less of the clamp load '
         'acts to turn the nut back.</li>'
         '<li><strong>Finer adjustment.</strong> One turn moves the nut a shorter distance, which suits '
         'adjusters and bearing preload.</li>'
         '<li><strong>Thin walls.</strong> A shallow thread can be cut in a tube or a thin section that a coarse '
         'thread would weaken or break through.</li></ul></section>',
         '<section><h2>What the coarse thread gains</h2><ul>'
         '<li><strong>Stripping strength in soft material.</strong> The thicker thread ridge carries more shear, '
         'so coarse threads are preferred for tapped holes in aluminium, cast iron, brass and plastics.</li>'
         '<li><strong>Tolerance of damage.</strong> A nick, a burr, dirt or a thick coating such as hot-dip '
         'galvanizing is a smaller fraction of a deep thread.</li>'
         '<li><strong>Speed.</strong> Fewer turns to run a nut down, and less risk of cross-threading when '
         'starting it.</li>'
         '<li><strong>Less galling.</strong> Stainless steel and titanium fasteners seize less readily on a '
         'coarse pitch.</li>'
         '<li><strong>Availability.</strong> Coarse is what is stocked everywhere, in every strength class.</li>'
         '</ul></section>',
         '<section><h2>Choosing</h2>'
         '<p>Use the coarse thread unless one of the advantages of the fine thread is needed. Typical reasons '
         'to go fine are a highly loaded bolt in a steel or hardened nut thread, a joint exposed to vibration, a '
         'thin-walled part, or an adjustment. Whatever the pitch, both parts must match: a fine nut does not '
         'go on a coarse bolt.</p></section>',
         faq([('Are fine threads stronger than coarse threads?',
               'The bolt is, by about 4 to 15% in tension, because its core is larger. The thread in the nut or '
               'tapped hole is weaker in shear per unit length, which matters in soft materials.'),
              ('Do fine threads hold better under vibration?',
               'Yes, somewhat. The smaller lead angle reduces the tendency of the clamp load to unscrew the '
               'nut. A locking feature is still needed where vibration is severe.'),
              ('Does the tap drill change with the pitch?',
               'Yes. A finer pitch needs a larger tap drill: M10×1.5 uses 8.5 mm, M10×1.25 uses 8.8 mm and '
               'M10×1 uses 9 mm.')]),
         family_links('/coarse-vs-fine/'),
         src_line('ISO 724, ISO 898-1 and ASME B1.1 (dimensions and stress areas)')]
    return page('/coarse-vs-fine/', title, desc, '\n'.join(b), trail=[('Coarse vs Fine', None)],
                schema=[webpage_ld('/coarse-vs-fine/', title, desc)])


# ---------------------------------------------------------------- terminology

TERMS = [
    ('Major diameter', 'The largest diameter of the thread: over the crests of a bolt, or across the roots of '
                       'a nut. It is the nominal size, so an M8 bolt has a basic major diameter of 8 mm. '
                       'Symbols d (external) and D (internal).'),
    ('Minor diameter', 'The smallest diameter: at the roots of a bolt, or across the crests of a nut. For a '
                       'nut it is the bore left by the tap drill. Symbols D<sub>1</sub> for the internal thread '
                       'and d<sub>3</sub> for the rounded root of an external thread.'),
    ('Pitch diameter', 'The diameter of an imaginary cylinder that cuts the thread where the ridge and the '
                       'groove are equally wide. It controls the fit between nut and bolt and is what thread '
                       'gauges check. Symbols d<sub>2</sub> and D<sub>2</sub>; also called effective diameter.'),
    ('Pitch', 'The distance from a point on one thread to the same point on the next, measured along the '
              'axis. Metric threads state it in millimetres (M8×1.25).'),
    ('Threads per inch (TPI)', 'The number of threads in one inch of length, used for inch threads. It is '
                               'the reciprocal of the pitch: 20 threads per inch is a pitch of 0.050 in, or '
                               '1.27 mm.'),
    ('Lead', 'The distance a nut advances in one turn. For a single-start thread it equals the pitch; for a '
             'two-start thread it is twice the pitch.'),
    ('Lead angle', 'The angle of the thread helix at the pitch diameter, arctan(lead ÷ (π × pitch diameter)). '
                   'Fine threads have a smaller lead angle.'),
    ('Crest', 'The top surface of the thread ridge, furthest from the body the thread is cut on.'),
    ('Root', 'The bottom of the groove between two ridges.'),
    ('Flank', 'The sloping surface joining crest and root. The flanks are the surfaces that carry the load.'),
    ('Flank angle and thread angle', 'The thread angle is the angle between the two flanks: 60° for metric, '
                                     'Unified and NPT threads, 55° for Whitworth and BSP. The flank angle is '
                                     'half of it.'),
    ('Fundamental triangle height (H)', 'The height of the sharp V that the flanks would form if they met at '
                                        'a point. For a 60° thread H = 0.866 × pitch. Real threads are '
                                        'truncated to a fraction of H.'),
    ('Thread height', 'The radial distance from crest to root. In the basic 60° profile it is 5H/8, or '
                      '0.541 × pitch.'),
    ('Percentage of thread', 'How much of the thread height is left in a tapped hole, set by the tap drill. '
                             'Standard tap drills give about 75%.'),
    ('Length of engagement', 'The axial length over which nut and bolt threads are in contact. Tolerances are '
                             'given for a normal length of engagement.'),
    ('Tolerance class', 'A code for how far a thread may deviate from its basic size. Metric classes pair a '
                        'grade number with a position letter, capital for nuts: 6H for a nut, 6g for a bolt. '
                        'Unified classes are 1A, 2A, 3A for bolts and 1B, 2B, 3B for nuts, with 3 the tightest.'),
    ('Allowance', 'An intentional gap between the largest bolt and the smallest nut. A 6g or 2A bolt has an '
                  'allowance; a 6h or 3A bolt has none. It leaves room for plating and eases assembly.'),
    ('Tensile stress area', 'The cross-section used to calculate the strength of a bolt in tension. It is '
                            'based on a diameter between the pitch and minor diameters and is larger than '
                            'the area at the root.'),
    ('Proof load', 'The highest tensile load a bolt must withstand without permanent stretch. It is roughly '
                   '90% of the load at yield.'),
    ('Taper', 'The change of diameter along a taper thread. Pipe threads use 1 in 16: the diameter grows by '
              'one unit for every sixteen along the axis.'),
    ('Hand-tight engagement', 'How far a taper pipe thread screws in by hand before the flanks meet, written '
                              'L<sub>1</sub> in ASME B1.20.1.'),
    ('Right-hand and left-hand', 'A right-hand thread tightens clockwise and is the default. Left-hand threads '
                                 'are marked LH in the designation.'),
]


def terminology(fams):
    labels = {'p': 'pitch P', 'maj': ('major', 'diameter'), 'pit': ('pitch', 'diameter'),
              'min': ('minor', 'diameter'), 'h': 'thread height', 'angle': '60°'}
    fig = svg.profile_view('thread', labels, 'Cross-section of a nut on a bolt with the pitch, the major, '
                                             'pitch and minor diameters and the thread height marked.')
    dl = ''.join(f'<h3 id="{t.lower().split(" (")[0].replace(" ", "-")}">{t}</h3><p>{d}</p>' for t, d in TERMS)
    title = 'Thread Terminology: Major, Minor & Pitch Diameter Explained'
    desc = ('Screw thread terms explained with a diagram: major, minor and pitch diameter, pitch, TPI, lead, '
            'flank angle, tolerance class, allowance and stress area.')
    b = ['<h1>Thread Terminology</h1>',
         '<p class="lead">The terms used in thread tables and standards, with the symbols ISO and ASME use '
         'for them. The drawing shows a section through a nut screwed onto a bolt.</p>',
         svg.figure(fig, 'A nut (blue) on a bolt (grey) in section. All three diameters are measured across '
                         'the full thread, not from the axis.'),
         f'<section class="faq"><h2>Terms</h2>{dl}</section>',
         '<section><h2>Reading a thread designation</h2>'
         + table(['Designation', 'Meaning'],
                 [['M8', 'ISO metric, 8 mm major diameter, coarse pitch (1.25 mm)'],
                  ['M8×1', 'ISO metric, 8 mm major diameter, 1 mm fine pitch'],
                  ['M8×1.25 – 6g', 'as above, external thread of tolerance class 6g'],
                  ['M10×1 – 6H – LH', 'internal thread, class 6H, left-hand'],
                  ['1/4-20 UNC – 2A', '1/4 in diameter, 20 threads per inch, Unified coarse, external class 2A'],
                  ['#10-32 UNF – 2B', 'number 10 size (0.190 in), 32 threads per inch, internal class 2B'],
                  ['1/2-14 NPT', 'taper pipe thread for nominal 1/2 in pipe, 14 threads per inch'],
                  ['G1/2 A', 'BSP parallel thread, size 1/2, external, tolerance class A'],
                  ['R1/2, Rc1/2', 'BSP taper thread, size 1/2: male and female']],
                 'chart', label='Thread designations', num_from=9)
         + '</section>',
         family_links('/thread-terminology/'),
         src_line('ISO 5408 (vocabulary), ISO 68-1, ISO 965-1, ASME B1.1 and ASME B1.20.1')]
    return page('/thread-terminology/', title, desc, '\n'.join(b), trail=[('Thread Terminology', None)],
                schema=[webpage_ld('/thread-terminology/', title, desc)])


# ---------------------------------------------------------------- calculator

CALC_JS = r"""
(function(){
var $=function(i){return document.getElementById(i)};
function row(k,a,b){return '<tr><th scope="row">'+k+'</th><td class="n">'+a+'</td><td class="n">'+b+'</td></tr>'}
function units(){
  var m=$('system').value==='metric';
  $('diam-label').textContent=m?'Major diameter (mm)':'Major diameter (in)';
  $('pitch-label').textContent=m?'Pitch (mm)':'Threads per inch';
  $('diameter').value=m?'10':'0.5';$('pitch').value=m?'1.5':'13';
  $('diameter').step=m?'0.1':'0.0001';
  calc();
}
function calc(){
  var m=$('system').value==='metric',d=parseFloat($('diameter').value),q=parseFloat($('pitch').value);
  var out=$('results'),msg=$('msg');
  if(!(d>0)||!(q>0)){msg.textContent='Enter a diameter and a pitch greater than zero.';out.innerHTML='';$('drills').innerHTML='';return}
  var f=m?1:25.4,D=d*f,P=m?q:25.4/q;
  if(D-1.226869*P<=0){msg.textContent='That pitch is too coarse for the diameter: the thread would have no core.';out.innerHTML='';$('drills').innerHTML='';return}
  msg.textContent='';
  var H=0.866025*P,d2=D-0.649519*P,D1=D-1.082532*P,k=m?1.226869:1.190785,d3=D-k*P;
  var As=m?Math.PI/4*Math.pow((d2+d3)/2,2):0.7854*Math.pow(D-0.9743*P,2);
  var lead=Math.atan(P/(Math.PI*d2))*180/Math.PI;
  function b(v){return row.apply(null,arguments)}
  function mm(v){return v.toFixed(3)} function inch(v){return (v/25.4).toFixed(4)}
  out.innerHTML=
   row('Major diameter d',mm(D),inch(D))+row('Pitch P',mm(P),(P/25.4).toFixed(5))+
   row('Threads per inch',(25.4/P).toFixed(2),'')+
   row('Pitch diameter d<sub>2</sub>',mm(d2),inch(d2))+
   row('Minor diameter, internal D<sub>1</sub>',mm(D1),inch(D1))+
   row('Minor diameter, external d<sub>3</sub>',mm(d3),inch(d3))+
   row('Fundamental triangle height H',mm(H),inch(H))+
   row('Thread height 5H/8',mm(0.541266*P),inch(0.541266*P))+
   row('Lead angle',lead.toFixed(2)+'°','')+
   row('Tensile stress area',As.toFixed(2)+' mm²',(As/645.16).toFixed(5)+' in²');
  var h='';[83,77,70,65,60].forEach(function(p){var dr=D-p/100*1.299038*P;
   h+='<tr'+(p===77?' class="rec"':'')+'><th scope="row">'+p+'%'+(p===77?' <span class="tag">standard</span>':'')+'</th><td class="n">'+dr.toFixed(2)+'</td><td class="n">'+(dr/25.4).toFixed(4)+'</td></tr>'});
  $('drills').innerHTML=h;
}
$('system').addEventListener('change',units);
$('diameter').addEventListener('input',calc);$('pitch').addEventListener('input',calc);
calc();
})();
"""


def calculator(fams):
    title = 'Thread Calculator: Pitch Ø, Minor Ø & Tap Drill, Any Size'
    desc = ('Enter a diameter and pitch or TPI to get pitch Ø, minor Ø, tap drill, lead angle and tensile '
            'stress area for any 60° metric or inch thread. Instant results.')
    b = ['<h1>Thread Calculator</h1>',
         '<p class="lead">Calculates the basic dimensions of any 60° thread from its major diameter and pitch: '
         'ISO metric, Unified inch, or a special size that is in no chart. Results appear as you type.</p>',
         '<div class="panel" style="margin-bottom:1.5rem"><div class="calc">'
         '<div><label for="system">Thread system</label><select id="system">'
         '<option value="metric">Metric (mm)</option><option value="inch">Inch (TPI)</option></select></div>'
         '<div><label for="diameter" id="diam-label">Major diameter (mm)</label>'
         '<input type="number" id="diameter" value="10" step="0.1" min="0" inputmode="decimal"></div>'
         '<div><label for="pitch" id="pitch-label">Pitch (mm)</label>'
         '<input type="number" id="pitch" value="1.5" step="0.01" min="0" inputmode="decimal"></div>'
         '</div><p id="msg" class="err" role="alert" style="margin:.75rem 0 0"></p></div>',
         '<section><h2>Basic dimensions</h2>'
         '<div class="tw data-table-zone" tabindex="0" role="region" aria-label="Calculated dimensions">'
         '<table class="spec" aria-live="polite"><thead><tr><th scope="col">Dimension</th><th scope="col" class="n">mm</th>'
         '<th scope="col" class="n">in</th></tr></thead><tbody id="results"></tbody></table></div>'
         '<noscript><p class="note">The calculator needs JavaScript. The thread charts list the same values '
         'for every standard size.</p></noscript></section>',
         '<section><h2>Tap drill by percentage of thread</h2>'
         '<div class="tw data-table-zone" tabindex="0" role="region" aria-label="Tap drill diameters">'
         '<table class="chart"><thead><tr><th scope="col">% thread</th><th scope="col" class="n">Drill Ø (mm)</th>'
         '<th scope="col" class="n">Drill Ø (in)</th></tr></thead><tbody id="drills"></tbody></table></div>'
         '<p class="small muted">These are exact diameters. Pick the nearest drill you have that is not '
         'below the 83% size, which is the basic minor diameter.</p></section>',
         '<section><h2>Formulas</h2><div class="panel"><ul>'
         '<li>H = 0.866025 × P, the height of the fundamental triangle</li>'
         '<li>Pitch diameter d<sub>2</sub> = d − 0.649519 × P</li>'
         '<li>Minor diameter of the internal thread D<sub>1</sub> = d − 1.082532 × P</li>'
         '<li>Minor diameter of the external thread d<sub>3</sub> = d − 1.226869 × P (ISO metric, rounded '
         'root) or d − 1.190785 × P (Unified UNR)</li>'
         '<li>Tensile stress area, metric: A<sub>s</sub> = π/4 × ((d<sub>2</sub> + d<sub>3</sub>) ÷ 2)² '
         '(ISO 898-1)</li>'
         '<li>Tensile stress area, inch: A<sub>s</sub> = 0.7854 × (d − 0.9743 ÷ n)², n = threads per inch '
         '(ASME B1.1)</li>'
         '<li>Tap drill = d − (% thread ÷ 100) × 1.299038 × P</li>'
         '<li>Lead angle = arctan(P ÷ (π × d<sub>2</sub>))</li></ul></div>'
         '<p>The calculator gives basic sizes, before tolerances. For a standard thread, the thread page '
         'also lists the tolerance limits and the drill sizes that are actually stocked.</p></section>',
         faq([('Does the calculator work for pipe threads?',
               'No. NPT and BSP threads have different proportions and, for NPT, a taper. Use the '
               '<a href="/pipe-threads/">NPT</a> and <a href="/bsp/">BSP</a> charts.'),
              ('Why is the tap drill larger than the minor diameter?',
               'The basic minor diameter is the smallest the hole may be. Drilling to it means cutting an 83% '
               'thread, which loads the tap heavily. The standard drill leaves about 77%.'),
              ('Can I use it for Whitworth or Acme threads?',
               'No. The formulas are for the 60° profile shared by ISO metric and Unified threads.')]),
         family_links('/calculator/'),
         src_line('ISO 724, ISO 898-1 and ASME B1.1 (formulas)')]
    schema = [webpage_ld('/calculator/', title, desc),
              {'@context': 'https://schema.org', '@type': 'WebApplication', 'name': 'Thread Calculator',
               'url': SITE + '/calculator/', 'applicationCategory': 'UtilitiesApplication',
               'operatingSystem': 'Any', 'isAccessibleForFree': True,
               'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'}, 'publisher': ORG}]
    return page('/calculator/', title, desc, '\n'.join(b), trail=[('Calculator', None)], schema=schema,
                scripts=f'<script>{CALC_JS}</script>\n')


# ---------------------------------------------------------------- identifier

ID_JS = r"""
(function(){
var T=JSON.parse(document.getElementById('thread-data').textContent);
var $=function(i){return document.getElementById(i)};
var FAM={m:'ISO metric coarse',f:'ISO metric fine',c:'UNC',u:'UNF',e:'UNEF',n:'NPT',b:'BSP'};
function labels(){
  $('dia-label').textContent=($('part').value==='ext'?'Outside diameter of the thread':'Bore of the threaded hole')+' ('+$('dunit').value+')';
  $('pitch-label').textContent=$('punit').value==='mm'?'Pitch (mm), optional':'Threads per inch, optional';
}
function run(){
  labels();
  var d=parseFloat($('dia').value),q=parseFloat($('pitchv').value),out=$('matches'),msg=$('idmsg');
  if(!(d>0)){msg.textContent='Enter the measured diameter.';out.innerHTML='';return}
  msg.textContent='';
  if($('dunit').value==='in')d*=25.4;
  var p=null;if(q>0)p=$('punit').value==='mm'?q:25.4/q;
  var ext=$('part').value==='ext',res=[];
  T.forEach(function(t){
    var ref=ext?t[3]:t[5],dd=(d-ref)/ref;
    // an external thread measures a little under nominal, a tapped bore a little over basic
    var s=Math.abs(dd+(ext?0.012:-0.02));
    if(p!==null){var dp=Math.abs(p-t[4])/t[4];s=s+dp*1.5}
    if(Math.abs(dd)<0.12&&(p===null||Math.abs(p-t[4])/t[4]<0.12))res.push([s,t,d-ref,p===null?null:p-t[4]]);
  });
  res.sort(function(a,b){return a[0]-b[0]});res=res.slice(0,8);
  if(!res.length){out.innerHTML='<tr><td colspan="6">No standard thread within 12% of that size. Check the measurement and the units.</td></tr>';return}
  var h='';res.forEach(function(r,i){var t=r[1];
    h+='<tr'+(i===0?' class="rec"':'')+'><th scope="row"><a href="'+t[1]+'">'+t[0]+'</a></th><td>'+FAM[t[2]]+'</td><td class="n">'+t[3].toFixed(3)+'</td><td class="n">'+t[5].toFixed(3)+'</td><td class="n">'+t[4].toFixed(3)+' ('+(25.4/t[4]).toFixed(1)+')</td><td class="n">'+(r[2]>=0?'+':'')+r[2].toFixed(2)+'</td></tr>'});
  out.innerHTML=h;
}
['part','dia','dunit','pitchv','punit'].forEach(function(i){$(i).addEventListener('input',run)});
run();
})();
"""


def confused(fams):
    pairs = [('M5×0.8', '#10-32 UNF'), ('M6×1', '1/4-28 UNF'), ('M8×1.25', '5/16-18 UNC'),
             ('M10×1.5', '3/8-16 UNC'), ('M12×1.75', '1/2-13 UNC'), ('M16×2', '5/8-11 UNC'),
             ('M20×2.5', '3/4-10 UNC'), ('M24×3', '1-8 UNC')]
    allm = {t['name']: t for k in ('metric', 'metric-fine') for t in fams[k]}
    allu = {t['name']: t for k in ('unc', 'unf', 'unef') for t in fams[k]}
    rows = []
    for a, b in pairs:
        m, u = allm[a], allu[b]
        ud, up = u['d'] * IN, u['p'] * IN
        rows.append([f'<a href="{m["url"]}">{a}</a>', f'<a href="{u["url"]}">{b}</a>',
                     f"{m['d']:.3f} / {ud:.3f}", f"{ud - m['d']:+.3f}", f"{m['p']:.3f} / {up:.3f}",
                     f"{(up / m['p'] - 1) * 100:+.0f}%"])
    return ('<section><h2>Pairs that are easily confused</h2>'
            '<p>These metric and inch threads are close enough in size for a nut of one to start on a bolt of '
            'the other. None of the pairs is interchangeable: the joint either binds after a few turns or '
            'goes together loosely and strips under load.</p>'
            + table(['Metric', 'Inch', 'Major Ø (mm)', 'Inch − metric Ø (mm)', 'Pitch (mm)',
                     'Pitch difference'], rows, 'chart', label='Metric and inch threads that are easily confused')
            + '<p>M5 and #10-32 are the closest pair: the pitches differ by less than 1% and the diameters by '
              '0.17 mm. A thread that goes together by hand and then tightens unexpectedly, or that feels '
              'loose all the way, is the usual sign of a mismatch.</p></section>')


def identifier(fams):
    code = {'metric': 'm', 'metric-fine': 'f', 'unc': 'c', 'unf': 'u', 'unef': 'e', 'npt': 'n', 'bsp': 'b'}
    data = []
    for k, ts in fams.items():
        for t in ts:
            if t['system'] == 'metric':
                row = [t['name'], t['url'], code[k], t['d'], t['p'], round(t['d1'], 3)]
            elif t['system'] == 'inch':
                row = [t['name'], t['url'], code[k], round(t['d'] * IN, 3), round(t['p'] * IN, 4),
                       round(t['d1'] * IN, 3)]
            elif t['system'] == 'npt':
                row = [t['plain'], t['url'], code[k], round(t['D'] * IN, 3), round(t['p'] * IN, 4),
                       round(t['K0'] * IN, 3)]
            else:
                row = [t['name'], t['url'], code[k], t['d'], round(t['p'], 4), round(t['d1'], 3)]
            data.append(row)
    blob = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    title = 'Thread Identifier: Find a Thread from Diameter & Pitch'
    desc = ('Measure the diameter and pitch of an unknown bolt, nut or pipe fitting and find the matching '
            'thread among 214 metric, UNC, UNF, UNEF, NPT and BSP sizes.')
    b = ['<h1>Thread Identifier</h1>',
         '<p class="lead">Enter what you measured on an unknown thread and get the standard threads closest to '
         'it, across metric, inch and pipe threads. The diameter alone narrows it down; adding the pitch usually '
         'settles it.</p>',
         '<div class="panel" style="margin-bottom:1.5rem"><div class="calc">'
         '<div><label for="part">What did you measure?</label><select id="part">'
         '<option value="ext">A bolt, screw or male fitting</option>'
         '<option value="int">A nut or threaded hole</option></select></div>'
         '<div><label for="dia" id="dia-label">Outside diameter of the thread (mm)</label>'
         '<input type="number" id="dia" value="7.9" step="0.01" min="0" inputmode="decimal"></div>'
         '<div><label for="dunit">Diameter unit</label><select id="dunit"><option value="mm">mm</option>'
         '<option value="in">in</option></select></div>'
         '<div><label for="pitchv" id="pitch-label">Pitch (mm), optional</label>'
         '<input type="number" id="pitchv" value="1.25" step="0.01" min="0" inputmode="decimal"></div>'
         '<div><label for="punit">Pitch unit</label><select id="punit"><option value="mm">mm</option>'
         '<option value="tpi">threads per inch</option></select></div>'
         '</div><p id="idmsg" class="err" role="alert" style="margin:.75rem 0 0"></p></div>',
         '<section><h2>Closest standard threads</h2>'
         '<div class="tw data-table-zone" tabindex="0" role="region" aria-label="Closest threads">'
         '<table class="chart" aria-live="polite"><thead><tr><th scope="col">Thread</th><th scope="col">Series</th>'
         '<th scope="col" class="n">Major Ø (mm)</th><th scope="col" class="n">Minor Ø (mm)</th>'
         '<th scope="col" class="n">Pitch mm (TPI)</th><th scope="col" class="n">Your Ø − standard (mm)</th>'
         '</tr></thead><tbody id="matches"></tbody></table></div>'
         '<noscript><p class="note">The identifier needs JavaScript. Without it, compare your measurements '
         'with the thread charts linked below.</p></noscript>'
         '<p class="small muted">The best match is highlighted. A bolt normally measures 0.05 to 0.3 mm under '
         'its nominal diameter, and a tapped hole slightly over the basic minor diameter; the ranking allows '
         'for that.</p></section>',
         '<section><h2>How to measure a thread</h2><ol>'
         '<li><strong>Diameter.</strong> Measure across the crests of a bolt with a caliper. For a nut or a '
         'threaded hole, measure the bore across the crests of the internal thread. On a taper pipe thread, '
         'measure at the largest full thread.</li>'
         '<li><strong>Pitch.</strong> Use a thread pitch gauge and try leaves until one sits in the thread with '
         'no light showing. Without a gauge, measure the length of ten threads and divide by ten, or count the '
         'threads in one inch.</li>'
         '<li><strong>Metric or inch.</strong> A pitch that comes out at a round metric value such as 1.0, '
         '1.25 or 1.5 mm is metric. A whole number of threads per inch such as 13, 16, 20 or 24 is an inch '
         'thread.</li>'
         '<li><strong>Parallel or taper.</strong> Compare the diameter at the start and at the end of the '
         'thread. If it changes, it is a taper pipe thread (NPT or BSP taper).</li>'
         '<li><strong>Flank angle.</strong> If a 14 threads per inch pipe thread could be either NPT or BSP, '
         'look at the crests: flat for NPT, rounded for BSP.</li></ol></section>',
         confused(fams),
         family_links('/thread-identifier/'),
         src_line('ISO 724, ASME B1.1, ASME B1.20.1 and ISO 228-1 (basic dimensions)'),
         f'<script type="application/json" id="thread-data">{blob}</script>']
    schema = [webpage_ld('/thread-identifier/', title, desc),
              {'@context': 'https://schema.org', '@type': 'WebApplication', 'name': 'Thread Identifier',
               'url': SITE + '/thread-identifier/', 'applicationCategory': 'UtilitiesApplication',
               'operatingSystem': 'Any', 'isAccessibleForFree': True,
               'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'}, 'publisher': ORG}]
    return page('/thread-identifier/', title, desc, '\n'.join(b), trail=[('Thread Identifier', None)],
                schema=schema, scripts=f'<script>{ID_JS}</script>\n')


# ---------------------------------------------------------------- about, privacy, 404

def about(fams):
    n = {k: len(v) for k, v in fams.items()}
    total = sum(n.values())
    mail = ('<!--email_off--><a href="mailto:info&#64;threadspec&#46;org">info&#64;threadspec&#46;org</a>'
            '<!--/email_off-->')
    title = 'About ThreadSpec.org: Sources and How the Data Is Checked'
    desc = ('ThreadSpec.org is an independent thread reference. How dimensions are computed and checked '
            'against ISO 724, ISO 965-1, ASME B1.1, ASME B1.20.1 and ISO 228-1.')
    b = ['<h1>About ThreadSpec.org</h1>',
         f'<p class="lead">ThreadSpec.org is an independent reference for screw thread dimensions and tap '
         f'drills, covering {total} threads in seven series. It is free to use and is funded by advertising.</p>',
         '<section><h2>What the site covers</h2>'
         + table(['Series', 'Sizes', 'Range', 'Standard'],
                 [['<a href="/metric/">ISO metric coarse</a>', n['metric'], 'M1 to M68', 'ISO 261, ISO 724'],
                  ['<a href="/metric-fine/">ISO metric fine</a>', n['metric-fine'], 'M3×0.35 to M48×3',
                   'ISO 261, ISO 724'],
                  ['<a href="/unc/">Unified coarse (UNC)</a>', n['unc'], '#1-64 to 4-4', 'ASME B1.1'],
                  ['<a href="/unf/">Unified fine (UNF)</a>', n['unf'], '#0-80 to 1-1/2-12', 'ASME B1.1'],
                  ['<a href="/unef/">Unified extra fine (UNEF)</a>', n['unef'], '#12-32 to 1-11/16-18',
                   'ASME B1.1'],
                  ['<a href="/pipe-threads/">NPT</a>', n['npt'], '1/16 to 12', 'ASME B1.20.1'],
                  ['<a href="/bsp/">BSP parallel (G)</a>', n['bsp'], 'G1/16 to G4', 'ISO 228-1']],
                 'chart', label='Thread series covered', num_from=9)
         + '</section>',
         '<section id="sources"><h2>How the data is produced and checked</h2>'
         '<p>All pages are generated from one data set, so a chart and the page for a single thread cannot '
         'disagree. Three kinds of value are handled differently.</p>'
         '<h3>Computed from the standard formulas</h3>'
         '<p>The pitch, minor and root diameters, thread heights, lead angles and stress areas of metric and '
         'Unified threads are calculated from the major diameter and pitch with the formulas of ISO 724 and '
         'ASME B1.1. The results are then compared automatically with values printed in the standards: the '
         'stress areas of ISO 898-1 and ASME B1.1, the basic diameters in ASME B1.1 Table 2, and the 6g and 6H '
         'limits of ISO 965-2. A page is not published if a computed value disagrees with the printed one.</p>'
         '<h3>Taken from tables in the standards</h3>'
         '<p>NPT dimensions are those of ASME B1.20.1 Table 2 and BSP dimensions those of ISO 228-1 Table 1. '
         'Class 2A and 2B limits are from ASME B1.1 Table 2, clearance holes from ISO 273 and ASME B18.2.8, and '
         'strength values from ISO 898-1 and SAE J429, each shown only for the sizes the standard covers.</p>'
         '<h3>Conventions</h3>'
         '<p>A tap drill is a recommendation, not a dimension of the thread, and published charts do not always '
         'agree. Metric drills follow the diameter-minus-pitch rule of ISO 2306 as rounded in standard tables. '
         'Inch drills are those of Machinery’s Handbook and the usual shop charts. NPT drills are the sizes '
         'printed on standard shop charts, with the drill suggested in the appendix of ASME B1.20.1 shown '
         'beside them where it differs. BSP drills are from tap manufacturers’ charts. Where a size appears in no chart, the '
         'page says how the drill was chosen.</p>'
         '<h3>Standards referred to</h3><ul>'
         '<li>ISO 68-1, ISO 261, ISO 724: metric thread profile, series and basic dimensions</li>'
         '<li>ISO 965-1 and ISO 965-2: metric thread tolerances and limits of size</li>'
         '<li>ISO 273: clearance holes for bolts and screws</li>'
         '<li>ISO 898-1: mechanical properties of steel fasteners</li>'
         '<li>ISO 2306: drills for tapping</li>'
         '<li>ISO 228-1 and ISO 7-1: pipe threads, parallel and taper</li>'
         '<li>ASME B1.1: Unified inch screw threads</li>'
         '<li>ASME B1.20.1: pipe threads, general purpose (inch)</li>'
         '<li>ASME B18.2.8: clearance holes for inch fasteners</li>'
         '<li>SAE J429: mechanical requirements for inch bolts</li></ul></section>',
         '<section><h2>Limits of this reference</h2>'
         '<p>The pages give basic sizes and the general-purpose tolerance classes. They are a working reference '
         'and do not replace the standards themselves, which contain further classes, gauging rules and '
         'conditions. For safety-critical or contractual work, confirm the values against the current edition '
         'of the governing standard.</p></section>',
         '<section><h2>Corrections</h2>'
         f'<p>If you find a value that disagrees with a standard, please write to {mail} with the thread, the '
         f'value and the source. Confirmed errors are corrected and the page date is updated.</p></section>',
         '<section><h2>Contact</h2>'
         f'<p>Email: {mail}</p></section>',
         f'<p class="small muted">Last reviewed {TODAY_TEXT}.</p>']
    schema = [{'@context': 'https://schema.org', '@type': 'AboutPage', 'url': SITE + '/about/', 'name': title,
               'description': desc, 'inLanguage': 'en', 'dateModified': '2026-09-29', 'mainEntity': ORG}]
    return page('/about/', title, desc, '\n'.join(b), trail=[('About', None)], schema=schema)


def privacy():
    mail = ('<!--email_off--><a href="mailto:info&#64;threadspec&#46;org">info&#64;threadspec&#46;org</a>'
            '<!--/email_off-->')
    title = 'Privacy Policy — ThreadSpec.org'
    desc = ('Privacy policy for ThreadSpec.org: what data is collected, how Google Analytics and Google AdSense '
            'cookies are used, and how to contact us.')
    b = ['<h1>Privacy Policy</h1>',
         f'<p class="muted">Last updated: {TODAY_TEXT}</p>',
         '<p class="lead">ThreadSpec.org is a free reference website. We keep data collection to a minimum; '
         'this page explains what is collected and why.</p>',
         '<section><h2>What we collect</h2><p>The site has no accounts and never asks for a name, an email '
         'address or other personal details. The thread calculator and the thread identifier run entirely in '
         'your browser: the values you enter are not sent anywhere.</p></section>',
         '<section><h2>Analytics</h2><p>We use Google Analytics 4 and Ahrefs Web Analytics to see which pages '
         'are useful and how visitors find the site. Google Analytics records pages visited, approximate '
         'location (city level), browser and device type and the referring website, using cookies and similar '
         'identifiers set by Google. Ahrefs Web Analytics counts page views without cookies.</p>'
         '<p>The data we see is aggregated and does not identify you. Google explains how it processes this data '
         'at <a href="https://policies.google.com/privacy" rel="noopener">policies.google.com/privacy</a>, and '
         'you can opt out on all websites with the '
         '<a href="https://tools.google.com/dlpage/gaoptout" rel="noopener">Google Analytics opt-out browser '
         'add-on</a>.</p></section>',
         '<section><h2>Advertising</h2><p>We use Google AdSense to show ads, which is what keeps this reference '
         'free. Google and its partners use cookies and similar technologies to serve and measure those ads, '
         'including ads based on your earlier visits to this and other websites.</p>'
         '<p>You can turn off personalised advertising in '
         '<a href="https://myadcenter.google.com/" rel="noopener">Google My Ad Center</a>, opt out of some '
         'third-party vendors’ use of cookies at '
         '<a href="https://www.aboutads.info/choices/" rel="noopener">aboutads.info/choices</a>, and read '
         '<a href="https://policies.google.com/technologies/partner-sites" rel="noopener">how Google uses '
         'information from sites that use its services</a>.</p></section>',
         '<section><h2>Consent in Europe</h2><p>For visitors in the European Economic Area, the United Kingdom '
         'and Switzerland, analytics and advertising storage is switched off by default. It is enabled only '
         'after you give consent in the message shown on your first visit. You can change your choice at any '
         'time through the privacy link that message leaves on the page.</p></section>',
         '<section><h2>Cookies</h2><p>The cookies on this site are set by Google Analytics (names beginning with '
         '_ga) and by Google AdSense and its advertising partners. We set no cookies of our own. Blocking or '
         'deleting these cookies does not affect how the site works.</p></section>',
         '<section><h2>Hosting and server logs</h2><p>The site is served as static pages. Our hosting and '
         'content delivery providers may keep standard server logs (IP address, requested URL, time and user '
         'agent) for security and operation. We do not combine these logs with any other data.</p></section>',
         '<section><h2>Third-party content</h2><p>Pages load scripts from Google (googletagmanager.com and '
         'googlesyndication.com) and from Ahrefs (analytics.ahrefs.com). The stylesheet and all diagrams are '
         'served from this site. When your browser requests a third-party script, the operator of that service '
         'receives your IP address as part of the request.</p></section>',
         '<section><h2>Your rights</h2><p>Depending on where you live, for example under the GDPR or the CCPA, '
         'you may have the right to access, correct or delete personal data. We hold no personal data about '
         'visitors, so such requests are usually best sent to Google. For anything else, contact us and we '
         'will help.</p></section>',
         '<section><h2>Changes</h2><p>If the way the site handles data changes, this page and its date are '
         'updated.</p></section>',
         f'<section><h2>Contact</h2><p>Questions about privacy: {mail}</p></section>']
    return page('/privacy/', title, desc, '\n'.join(b), trail=[('Privacy Policy', None)],
                schema=[webpage_ld('/privacy/', title, desc)])


def not_found():
    b = ['<h1>Page not found</h1>',
         '<p class="lead">There is no page at this address. The thread you are looking for is probably in one '
         'of the charts below.</p>',
         chips([('Metric coarse chart', '/metric/'), ('Metric fine chart', '/metric-fine/'),
                ('UNC chart', '/unc/'), ('UNF chart', '/unf/'), ('UNEF chart', '/unef/'),
                ('NPT chart', '/pipe-threads/'), ('BSP chart', '/bsp/'),
                ('Tap drill chart', '/tap-drill-chart/'), ('Thread identifier', '/thread-identifier/'),
                ('Home', '/')])]
    html = page('/404.html', 'Page Not Found — ThreadSpec.org',
                'Page not found on ThreadSpec.org. Browse the thread charts for metric, UNC, UNF, NPT and BSP '
                'threads.', '\n'.join(b), noindex=True)
    return html.replace('<link rel="canonical" href="https://threadspec.org/404.html">\n', '')


def npt_redirect():
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="0;url=/pipe-threads/">
<link rel="canonical" href="https://threadspec.org/pipe-threads/">
<title>NPT Thread Chart</title>
<meta name="robots" content="noindex,follow">
</head>
<body>
<p>The NPT thread chart is at <a href="/pipe-threads/">threadspec.org/pipe-threads/</a>.</p>
</body>
</html>
"""
