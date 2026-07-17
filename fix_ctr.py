#!/usr/bin/env python3
"""CTR optimization for threadspec.org.
Rewrites titles, meta descriptions, adds FAQPage schema to all pages.
Goal: front-load the answer (tap drill / key spec) in title and description.
"""

import os
import re
import json

BASE = "/Users/juhaporraskorpi/clawd/threadspec"

# ============================================================
# HTML UTILITIES
# ============================================================

def hd(s):
    """Decode common HTML entities."""
    return (s
            .replace('&quot;', '"')
            .replace('&amp;', '&')
            .replace('&lt;', '<')
            .replace('&gt;', '>')
            .replace('&#x2212;', '−')
            .replace('&times;', '×')
            .replace('&#xd7;', '×'))

def he(s):
    """Encode string for HTML attribute value."""
    return (s
            .replace('&', '&amp;')
            .replace('"', '&quot;')
            .replace('<', '&lt;')
            .replace('>', '&gt;'))

def get_title(html):
    m = re.search(r'<title>([^<]*)</title>', html)
    return hd(m.group(1)) if m else ''

def extract_span(html, color):
    """Extract text from tap-drill highlight span of given Tailwind color name."""
    m = re.search(rf'class="text-2xl font-bold text-{color}-700">([^<]+)</span>', html)
    return hd(m.group(1).strip()) if m else None

def extract_td(html, label):
    """Exact label match in spec table."""
    pat = rf'{re.escape(label)}</td><td[^>]*>([^<]+)</td>'
    m = re.search(pat, html)
    return hd(m.group(1).strip()) if m else None

def extract_td_prefix(html, prefix):
    """Label starts-with match (handles variants like 'Major Diameter (d)')."""
    pat = rf'{re.escape(prefix)}[^<]*</td><td[^>]*>([^<]+)</td>'
    m = re.search(pat, html)
    return hd(m.group(1).strip()) if m else None

def first_val(text):
    """Return the portion of 'X" (Y mm)' or 'X mm (Y")' before the '('."""
    if not text:
        return ''
    m = re.match(r'^([^(]+)', text)
    return m.group(1).strip() if m else text

def drill_short(text):
    """'NAME (X.XXXX" / Y mm)' → 'NAME (X.XXXX")'. Strips metric portion."""
    if not text:
        return ''
    if ' / ' in text:
        return text[:text.rindex(' / ')] + ')'
    return text

def update_tags(html, title, desc):
    """Replace <title>, meta description, og:title, og:description."""
    t = he(title)
    d = he(desc)
    html = re.sub(r'<title>[^<]*</title>', f'<title>{t}</title>', html, count=1)
    html = re.sub(
        r'(<meta name="description" content=")[^"]*(")',
        rf'\g<1>{d}\g<2>', html, count=1)
    html = re.sub(
        r'(<meta property="og:title" content=")[^"]*(")',
        rf'\g<1>{t}\g<2>', html, count=1)
    html = re.sub(
        r'(<meta property="og:description" content=")[^"]*(")',
        rf'\g<1>{d}\g<2>', html, count=1)
    return html

def add_faq(html, qa_list):
    """Add or replace FAQPage JSON-LD schema block."""
    obj = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a}
            }
            for q, a in qa_list
        ]
    }
    script = (
        '<script type="application/ld+json">'
        + json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
        + '</script>'
    )

    if '"FAQPage"' in html:
        def rep(m):
            return script if '"FAQPage"' in m.group(0) else m.group(0)
        html = re.sub(
            r'<script type="application/ld\+json">.*?</script>',
            rep, html, flags=re.DOTALL)
    else:
        html = html.replace('</head>', script + '\n</head>', 1)
    return html

def save(path, html):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  {path.replace(BASE + "/", "")}')

def designation_from_h1(html):
    """
    Extract thread designation from the stable <h1> tag (not the title,
    which may have been modified by a previous script run).
    '<h1 ...>#12-24 UNC Thread Specifications</h1>'       → '#12-24 UNC'
    '<h1 ...>1/2&quot; NPT Thread Specifications</h1>'    → '1/2" NPT'
    '<h1 ...>M8×1.25 Thread Specifications</h1>'          → 'M8×1.25'
    """
    m = re.search(r'<h1[^>]*>([^<]+)Thread Specifications</h1>', html)
    if m:
        return hd(m.group(1).strip())
    # Fallback: extract from h1 and strip known suffixes
    m2 = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    if m2:
        t = hd(m2.group(1).strip())
        t = re.sub(r'\s+Thread\s+(?:Specifications|Chart)\s*$', '', t).strip()
        return t
    return ''


# ============================================================
# INCH DETAIL PAGES  (UNC / UNF / UNEF)
# ============================================================

def proc_inch_detail(path):
    html = open(path, encoding='utf-8').read()

    series = ('UNEF' if '/unef/' in path else 'UNF' if '/unf/' in path else 'UNC')
    std = 'ASME B1.1'

    desig = designation_from_h1(html)

    tap   = extract_span(html, 'blue')
    major = extract_td(html, 'Major Diameter')
    pitch = extract_td(html, 'Pitch Diameter')
    minor = extract_td(html, 'Minor Diameter (Internal)')
    stress = extract_td(html, 'Tensile Stress Area')

    if not tap or not desig:
        print(f'  SKIP (no data): {path}')
        return

    ds = drill_short(tap)

    # Title: front-load the tap drill answer  (target ≤ 62 chars displayed)
    new_title = f'{desig} Tap Drill: {ds} — {std}'

    # Description: answer immediately, then key dimensions
    parts = [f'Tap drill for {desig}: {tap}.']
    if major:
        parts.append(f'Major Ø {first_val(major)},')
    if pitch:
        parts.append(f'pitch Ø {first_val(pitch)},')
    if minor:
        parts.append(f'minor Ø {first_val(minor)}.')
    if stress:
        parts.append(f'Stress area {stress}.')
    parts.append(std + '.')
    new_desc = ' '.join(parts)

    # Trim if > 158 chars: drop stress area first, then minor
    if len(new_desc) > 158:
        parts2 = [f'Tap drill for {desig}: {tap}.']
        if major:
            parts2.append(f'Major Ø {first_val(major)},')
        if pitch:
            parts2.append(f'pitch Ø {first_val(pitch)},')
        if minor:
            parts2.append(f'minor Ø {first_val(minor)}.')
        parts2.append(std + '.')
        new_desc = ' '.join(parts2)
    if len(new_desc) > 158:
        # Drop minor too
        parts3 = [f'Tap drill for {desig}: {tap}.']
        if major:
            parts3.append(f'Major Ø {first_val(major)},')
        if pitch:
            parts3.append(f'pitch Ø {first_val(pitch)}.')
        parts3.append(std + '.')
        new_desc = ' '.join(parts3)

    # FAQ: 3 targeted questions
    qa = []
    if tap:
        qa.append((
            f'What is the tap drill size for {desig}?',
            f'The recommended tap drill for {desig} is {tap}. '
            f'This gives approximately 75% thread engagement per {std}.'
        ))
    if pitch:
        qa.append((
            f'What is the pitch diameter of {desig}?',
            f'The pitch diameter of {desig} is {pitch} per {std}.'
        ))
    if major:
        qa.append((
            f'What is the major diameter of {desig}?',
            f'The major diameter of {desig} is {major}.'
        ))

    html = update_tags(html, new_title, new_desc)
    html = add_faq(html, qa)
    save(path, html)


# ============================================================
# NPT DETAIL PAGES
# ============================================================

def proc_npt_detail(path):
    html = open(path, encoding='utf-8').read()

    desig = designation_from_h1(html)   # e.g. '1/2" NPT'

    tap      = extract_span(html, 'amber')
    od       = extract_td(html, 'Outside Diameter')
    tpi      = extract_td(html, 'TPI')
    pitch_e0 = extract_td(html, 'Pitch Diameter at E0 (hand-tight)')

    if not tap:
        print(f'  SKIP: {path}')
        return

    ds = drill_short(tap)

    new_title = f'{desig} Tap Drill: {ds} — ASME B1.20.1'

    parts = [f'{desig} (ASME B1.20.1): tap drill {tap}.']
    if od:
        parts.append(f'OD {first_val(od)},')
    if tpi:
        parts.append(f'TPI {tpi}.')
    if pitch_e0:
        parts.append(f'Pitch Ø at E0: {first_val(pitch_e0)}.')
    parts.append('Taper: 3/4″/ft (1:16 on diameter).')
    new_desc = ' '.join(parts)

    if len(new_desc) > 158:
        parts2 = [f'{desig} (ASME B1.20.1): tap drill {tap}.']
        if od:
            parts2.append(f'OD {first_val(od)},')
        if tpi:
            parts2.append(f'TPI {tpi}. Taper: 1:16.')
        new_desc = ' '.join(parts2)

    qa = [
        (
            f'What is the tap drill for {desig}?',
            f'The tap drill for {desig} is {tap} per ASME B1.20.1. '
            f'NPT uses a 1:16 taper — the tap itself cuts the tapered thread form.'
        )
    ]
    if od:
        qa.append((
            f'What is the outside diameter of {desig} pipe thread?',
            f'The outside diameter of {desig} pipe thread is {od} per ASME B1.20.1. '
            f'The nominal pipe size does not equal the actual OD.'
        ))
    if tpi:
        qa.append((
            f'How many threads per inch is {desig}?',
            f'{desig} has {tpi} threads per inch (TPI) with a 60° thread angle '
            f'and 1:16 taper per ASME B1.20.1.'
        ))

    html = update_tags(html, new_title, new_desc)
    html = add_faq(html, qa)
    save(path, html)


# ============================================================
# BSP DETAIL PAGES
# ============================================================

def proc_bsp_detail(path):
    html = open(path, encoding='utf-8').read()

    desig = designation_from_h1(html)   # e.g. 'G1/2" BSP'

    tap = extract_span(html, 'amber')
    od  = extract_td(html, 'Outside Diameter')
    tpi = extract_td(html, 'TPI')

    if not tap:
        print(f'  SKIP: {path}')
        return

    tpi_str = tpi or '?'
    new_title = f'{desig} Tap Drill: {tap}, TPI {tpi_str} — ISO 228'

    parts = [f'{desig} G-thread (ISO 228): tap drill {tap}.']
    if od:
        parts.append(f'OD {first_val(od)},')
    if tpi:
        parts.append(f'TPI {tpi}, 55° Whitworth profile.')
    parts.append('Parallel thread — standard in UK, Europe, Asia, Australia.')
    new_desc = ' '.join(parts)

    if len(new_desc) > 158:
        parts2 = [f'{desig} BSP (ISO 228): tap drill {tap}.']
        if od:
            parts2.append(f'OD {first_val(od)},')
        if tpi:
            parts2.append(f'TPI {tpi}. 55° Whitworth, parallel.')
        new_desc = ' '.join(parts2)

    qa = [
        (
            f'What is the tap drill for {desig}?',
            f'The tap drill for {desig} (G thread, ISO 228) is {tap}.'
        )
    ]
    if od:
        qa.append((
            f'What is the outside diameter of {desig}?',
            f'The outside diameter of {desig} G-thread is {od} per ISO 228. '
            f'BSP nominal sizes do not equal actual ODs.'
        ))
    qa.append((
        f'Are {desig} BSP and NPT threads interchangeable?',
        f'No. BSP uses a 55° Whitworth thread angle; NPT uses 60°. '
        f'Despite similar nominal sizes they are not interchangeable and will not seal correctly together.'
    ))

    html = update_tags(html, new_title, new_desc)
    html = add_faq(html, qa)
    save(path, html)


# ============================================================
# METRIC DETAIL PAGES  (coarse + fine)
# ============================================================

def proc_metric_detail(path, is_fine=False):
    html = open(path, encoding='utf-8').read()

    desig = designation_from_h1(html)   # e.g. 'M8×1.25' or 'M8×1.0'

    tap       = extract_span(html, 'emerald')
    pitch_dia = extract_td_prefix(html, 'Pitch Diameter')
    minor_int = extract_td_prefix(html, 'Minor Diameter — Internal')
    if not minor_int:
        minor_int = extract_td(html, 'Minor Diameter (D₁)')
    stress    = extract_td(html, 'Tensile Stress Area')

    # Extract pitch value from designation (M8×1.25 → '1.25')
    pitch_m = re.search(r'[\xd7xX]([\d.]+)\s*$', desig)
    pitch_str = pitch_m.group(1) if pitch_m else ''

    if not tap:
        print(f'  SKIP: {path}')
        return

    # Get pitch diameter in mm (metric pages show mm first)
    pitch_mm = first_val(pitch_dia) if pitch_dia else ''

    new_title = f'{desig} Tap Drill: {tap} — Pitch Ø {pitch_mm}, ISO 724'
    if len(new_title) > 63:
        new_title = f'{desig} Tap Drill: {tap} — ISO 724'

    thread_type = 'fine' if is_fine else 'coarse'
    parts = [f'{desig} {thread_type} thread (ISO 724): tap drill {tap}.']
    if pitch_dia:
        parts.append(f'Pitch Ø {pitch_dia},')
    if minor_int:
        parts.append(f'minor Ø {minor_int}.')
    if stress:
        parts.append(f'Stress area {stress}.')
    new_desc = ' '.join(parts)

    if len(new_desc) > 158:
        parts2 = [f'{desig} {thread_type} (ISO 724): tap drill {tap}.']
        if pitch_dia:
            parts2.append(f'Pitch Ø {pitch_dia}.')
        if stress:
            parts2.append(f'Stress area {stress}.')
        new_desc = ' '.join(parts2)

    # FAQ
    base_m = re.match(r'(M[\d.]+)', desig)
    base = base_m.group(1) if base_m else desig

    qa = [
        (
            f'What is the tap drill for {desig}?',
            f'The tap drill for {desig} is {tap}. This uses the d − P formula '
            f'(nominal diameter minus pitch) for approximately 75% thread engagement per ISO 724.'
        )
    ]
    if pitch_dia:
        qa.append((
            f'What is the pitch diameter of {desig}?',
            f'The pitch diameter of {desig} is {pitch_dia} per ISO 724.'
        ))
    if is_fine and pitch_str:
        qa.append((
            f'How does {desig} compare to {base} coarse thread?',
            f'{desig} is a fine thread with {pitch_str} mm pitch. The standard {base} coarse thread '
            f'has a larger pitch — coarse threads are easier to assemble while fine threads provide '
            f'higher tensile strength and vibration resistance.'
        ))
    elif not is_fine and pitch_str:
        qa.append((
            f'What is the standard pitch of {desig}?',
            f'The standard coarse pitch for {desig} is {pitch_str} mm per ISO 724. '
            f'The d − P tap drill formula gives {tap} for approximately 75% engagement. '
            f'For finer pitches, see the metric fine thread chart.'
        ))

    html = update_tags(html, new_title, new_desc)
    html = add_faq(html, qa)
    save(path, html)


# ============================================================
# CATEGORY / HUB PAGES
# ============================================================

def proc_unc_index(path):
    html = open(path, encoding='utf-8').read()
    t = 'UNC Thread Chart — 33 Sizes with Tap Drills & Pitch Diameters'
    d = ('Tap drill sizes and full dimensions for all 33 UNC thread sizes (#1-64 to 4-4). '
         '1/4-20: #7 drill; 1/2-13: 27/64″; 3/4-10: 21/32″. '
         'Major, pitch, minor diameters and stress areas per ASME B1.1.')
    if len(d) > 158:
        d = ('Tap drills for all 33 UNC sizes (#1-64 to 4-4). '
             '1/4-20: #7; 1/2-13: 27/64″; 3/4-10: 21/32″. '
             'Major, pitch, minor Ø per ASME B1.1.')
    qa = [
        (
            'What is the tap drill for 1/4-20 UNC?',
            'The tap drill for 1/4-20 UNC is #7 (0.2010″ / 5.11 mm), '
            'giving approximately 75% thread engagement per ASME B1.1.'
        ),
        (
            'What is the tap drill for 1/2-13 UNC?',
            'The tap drill for 1/2-13 UNC is 27/64″ (0.4219″ / 10.72 mm) per ASME B1.1.'
        ),
        (
            'What is the difference between UNC and UNF threads?',
            'UNC (Unified National Coarse) has fewer threads per inch and is the standard for '
            'general-purpose fastening. UNF (fine) has more TPI, higher tensile strength, and '
            'better vibration resistance, but is more susceptible to cross-threading.'
        ),
        (
            'How many standard UNC thread sizes are there?',
            'There are 33 standard UNC thread sizes, from #1-64 (0.073″ major diameter) '
            'to 4-4 (4.000″), per ASME B1.1.'
        ),
    ]
    html = update_tags(html, t, d)
    html = add_faq(html, qa)
    save(path, html)


def proc_unf_index(path):
    html = open(path, encoding='utf-8').read()
    t = 'UNF Thread Chart — 24 Sizes with Tap Drills & Pitch Diameters'
    d = ('Tap drill sizes and full dimensions for all 24 UNF thread sizes (#0-80 to 1-1/2-12). '
         '1/4-28: #3 drill; 1/2-20: 29/64″; 3/4-16: 11/16″. '
         'Major, pitch, minor diameters per ASME B1.1.')
    if len(d) > 158:
        d = ('Tap drills for all 24 UNF sizes (#0-80 to 1-1/2-12). '
             '1/4-28: #3; 1/2-20: 29/64″; 3/4-16: 11/16″. Per ASME B1.1.')
    qa = [
        (
            'What is the tap drill for 1/4-28 UNF?',
            'The tap drill for 1/4-28 UNF is #3 (0.2130″ / 5.41 mm) per ASME B1.1.'
        ),
        (
            'What is the tap drill for 1/2-20 UNF?',
            'The tap drill for 1/2-20 UNF is 29/64″ (0.4531″ / 11.51 mm) per ASME B1.1.'
        ),
        (
            'When should I use UNF instead of UNC?',
            'UNF threads are preferred when higher tensile strength or vibration resistance is needed, '
            'or in thin-walled parts. UNC is easier to start and more tolerant of contamination. '
            'UNF provides a finer pitch and deeper engagement in the same material thickness.'
        ),
        (
            'How many standard UNF thread sizes are there?',
            'There are 24 standard UNF thread sizes, from #0-80 (0.060″ major diameter) '
            'to 1-1/2-12, per ASME B1.1.'
        ),
    ]
    html = update_tags(html, t, d)
    html = add_faq(html, qa)
    save(path, html)


def proc_unef_index(path):
    html = open(path, encoding='utf-8').read()
    t = 'UNEF Thread Chart — Extra Fine Sizes with Tap Drills & TPI'
    d = ('Tap drill sizes and full dimensions for UNEF (Unified National Extra Fine) thread sizes. '
         '1/2-28 UNEF: 15/32″ drill; 7/8-20 UNEF: 53/64″; 1″-20 UNEF: 61/64″. '
         'Per ASME B1.1.')
    if len(d) > 158:
        d = ('Tap drills for UNEF extra fine thread sizes. '
             '1/2-28: 15/32″; 7/8-20: 53/64″; 1″-20: 61/64″. Per ASME B1.1.')
    qa = [
        (
            'What is UNEF thread used for?',
            'UNEF (Unified National Extra Fine) threads are used in aerospace, precision instruments, '
            'and thin-walled parts requiring maximum thread engagement in minimum material depth. '
            'They have more threads per inch than UNF for the same nominal diameter.'
        ),
        (
            'What is the tap drill for 1/2-28 UNEF?',
            'The tap drill for 1/2-28 UNEF is 15/32″ (0.4688″ / 11.91 mm) per ASME B1.1.'
        ),
        (
            'What is the difference between UNF and UNEF?',
            'UNEF (extra fine) has more threads per inch than UNF (fine) at the same nominal diameter. '
            'UNEF is used in thin-walled parts and precision applications; UNF is more common for '
            'general fine-thread fasteners.'
        ),
        (
            'What is the tap drill for 7/8-20 UNEF?',
            'The tap drill for 7/8-20 UNEF is 53/64″ (0.8281″ / 21.03 mm) per ASME B1.1.'
        ),
    ]
    html = update_tags(html, t, d)
    html = add_faq(html, qa)
    save(path, html)


def proc_metric_index(path):
    html = open(path, encoding='utf-8').read()
    t = 'ISO Metric Thread Chart — M1 to M68 Coarse: Tap Drills & Sizes'
    d = ('Tap drill sizes and full dimensions for all 36 ISO metric coarse thread sizes (M1 to M68). '
         'M6: 5.0 mm drill; M8: 6.8 mm; M10: 8.5 mm; M12: 10.2 mm. '
         'Pitch diameters and stress areas per ISO 724.')
    if len(d) > 158:
        d = ('Tap drills for all 36 ISO metric coarse sizes (M1–M68). '
             'M6: 5.0 mm; M8: 6.8 mm; M10: 8.5 mm; M12: 10.2 mm. '
             'Pitch Ø, minor Ø, stress area per ISO 724.')
    qa = [
        (
            'What is the tap drill size for M8?',
            'The tap drill for M8 (M8\xd71.25 coarse) is 6.8 mm, using the d − P formula '
            '(8 − 1.25 = 6.75, rounded up to standard 6.8 mm) for approximately 75% '
            'thread engagement per ISO 724.'
        ),
        (
            'What is the tap drill for M10?',
            'The tap drill for M10 (M10\xd71.5 coarse) is 8.5 mm using d − P (10 − 1.5 = 8.5 mm) per ISO 724.'
        ),
        (
            'What is the pitch of M6 coarse thread?',
            'The standard coarse pitch for M6 is 1.0 mm per ISO 724. The d − P tap drill is 5.0 mm.'
        ),
        (
            'What is the difference between metric coarse and metric fine threads?',
            'Metric coarse threads have a larger pitch (fewer turns per mm) and are the standard for '
            'general-purpose fastening. Metric fine threads have a smaller pitch, providing higher '
            'tensile strength and better vibration resistance, common in automotive and precision applications.'
        ),
    ]
    html = update_tags(html, t, d)
    html = add_faq(html, qa)
    save(path, html)


def proc_metric_fine_index(path):
    html = open(path, encoding='utf-8').read()
    t = 'ISO Metric Fine Thread Chart — M3 to M68: Tap Drills & Pitches'
    d = ('Tap drill sizes for 56+ ISO metric fine thread sizes (M3\xd70.35 to M68\xd73.0). '
         'M8\xd71.0: 7.0 mm drill; M10\xd71.25: 8.75 mm; M12\xd71.5: 10.5 mm. '
         'Pitch diameters and stress areas per ISO 724.')
    if len(d) > 158:
        d = ('Tap drills for ISO metric fine sizes (M3 to M68 fine pitches). '
             'M8\xd71.0: 7.0 mm; M10\xd71.25: 8.75 mm; M12\xd71.5: 10.5 mm. '
             'Per ISO 724.')
    qa = [
        (
            'What is the tap drill for M8\xd71.0 fine thread?',
            'The tap drill for M8\xd71.0 fine thread is 7.0 mm (d − P = 8 − 1.0 = 7.0 mm) '
            'per ISO 724. Compare to M8\xd71.25 coarse which requires 6.8 mm.'
        ),
        (
            'What is the tap drill for M10\xd71.25?',
            'The tap drill for M10\xd71.25 fine thread is 8.75 mm per ISO 724 (10 − 1.25 = 8.75 mm).'
        ),
        (
            'When should I use metric fine threads?',
            'Metric fine threads provide higher tensile strength and are preferred for vibration-prone '
            'applications (automotive, aircraft, precision instruments). They are harder to start and '
            'more susceptible to cross-threading than coarse threads of the same diameter.'
        ),
        (
            'What is the M12\xd71.5 tap drill?',
            'The tap drill for M12\xd71.5 fine thread is 10.5 mm (12 − 1.5 = 10.5 mm) per ISO 724.'
        ),
    ]
    html = update_tags(html, t, d)
    html = add_faq(html, qa)
    save(path, html)


def proc_npt_index(path):   # pipe-threads/index.html
    html = open(path, encoding='utf-8').read()
    t = 'NPT Thread Chart — 19 Pipe Sizes with Tap Drills & OD | ASME B1.20.1'
    if len(t) > 65:
        t = 'NPT Thread Chart — 19 Sizes: Tap Drills & OD | ASME B1.20.1'
    d = ('Tap drill sizes and full dimensions for all 19 NPT pipe thread sizes (1/16″ to 12″). '
         '1/4 NPT: 7/16″ drill; 1/2 NPT: 23/32″; 3/4 NPT: 59/64″. '
         'OD, TPI, and taper data per ASME B1.20.1.')
    if len(d) > 158:
        d = ('Tap drills for all 19 NPT pipe sizes (1/16″ to 12″). '
             '1/4 NPT: 7/16″; 1/2 NPT: 23/32″; 3/4 NPT: 59/64″. Per ASME B1.20.1.')
    qa = [
        (
            'What is the tap drill for 1/2 NPT?',
            'The tap drill for 1/2″ NPT is 23/32″ (0.7188″ / 18.26 mm) per ASME B1.20.1.'
        ),
        (
            'What is the outside diameter of 1/4 NPT pipe thread?',
            'The outside diameter of 1/4″ NPT pipe thread is 0.5400″ (13.72 mm) per ASME B1.20.1. '
            'The nominal pipe size (1/4″) does not match the actual OD.'
        ),
        (
            'How do NPT threads seal?',
            'NPT threads seal via metal-to-metal contact of tapered thread flanks. '
            'Teflon tape (PTFE) or pipe thread sealant is typically applied for a leak-free seal. '
            'NPT has a 1:16 taper (3/4″ per foot) per ASME B1.20.1.'
        ),
        (
            'Are NPT and BSP pipe threads compatible?',
            'No. NPT uses a 60° included thread angle; BSP uses 55° (Whitworth). '
            'They are not interchangeable even for the same nominal pipe size due to different '
            'thread angles, pitches, and ODs.'
        ),
    ]
    html = update_tags(html, t, d)
    html = add_faq(html, qa)
    save(path, html)


def proc_bsp_index(path):
    html = open(path, encoding='utf-8').read()
    t = 'BSP G-Thread Chart — 17 Sizes: Tap Drills & OD | ISO 228'
    d = ('Tap drill sizes and full dimensions for 17 BSP parallel G-thread sizes (G1/8″ to G4″). '
         'G1/4: 11.8 mm drill; G1/2: 19.0 mm; G3/4: 24.5 mm. '
         '55° Whitworth profile per ISO 228.')
    if len(d) > 158:
        d = ('Tap drills for 17 BSP parallel G-thread sizes (G1/8″ to G4″). '
             'G1/4: 11.8 mm; G1/2: 19.0 mm; G3/4: 24.5 mm. '
             '55° Whitworth, ISO 228.')
    qa = [
        (
            'What is the tap drill for G1/4 BSP?',
            'The tap drill for G1/4″ BSP (BSPP, parallel G thread) is 11.8 mm per ISO 228.'
        ),
        (
            'What is the difference between BSPP and BSPT?',
            'BSPP (G thread, ISO 228) is parallel — sealing requires a bonded seal or O-ring face. '
            'BSPT (R thread, ISO 7) is tapered — it seals on the thread taper like NPT. '
            'This chart covers G (parallel) threads.'
        ),
        (
            'What is the OD of G1/2 BSP thread?',
            'The outside diameter of G1/2″ BSP thread is 0.825″ (20.96 mm) per ISO 228. '
            'BSP nominal sizes do not equal actual ODs.'
        ),
        (
            'Are BSP and NPT threads interchangeable?',
            'No. BSP uses a 55° Whitworth thread profile; NPT uses 60°. '
            'They are not interchangeable despite similar nominal sizes — '
            'different thread angles, ODs, and pitches.'
        ),
    ]
    html = update_tags(html, t, d)
    html = add_faq(html, qa)
    save(path, html)


def proc_tap_drill_chart(path):
    html = open(path, encoding='utf-8').read()
    t = 'Tap Drill Chart — ISO Metric (M1–M68) & UNC Threads | d−P 75%'
    d = ('Standard tap drill sizes for ISO metric coarse (M1–M68) and UNC threads. '
         'M8: 6.8 mm; M10: 8.5 mm; 1/4-20 UNC: #7; 1/2-13 UNC: 27/64″. '
         'd − P formula for 75% thread engagement.')
    if len(d) > 158:
        d = ('Tap drill sizes for ISO metric coarse and UNC threads. '
             'M8: 6.8 mm; M10: 8.5 mm; 1/4-20: #7; 1/2-13: 27/64″. '
             'Uses d − P (75% engagement).')
    qa = [
        (
            'What is the M10 tap drill size?',
            'The M10 (M10\xd71.5 coarse) tap drill is 8.5 mm using d − P '
            '(10 − 1.5 = 8.5 mm) for approximately 75% thread engagement.'
        ),
        (
            'What is the 1/4-20 UNC tap drill?',
            'The 1/4-20 UNC tap drill is #7 (0.2010″ / 5.11 mm) per ASME B1.1.'
        ),
        (
            'What does the d − P tap drill formula mean?',
            'd − P means nominal diameter minus pitch. For M10\xd71.5: 10 − 1.5 = 8.5 mm. '
            'This gives approximately 75% thread engagement, balancing thread strength with ease of tapping. '
            'It is the industry standard recommendation.'
        ),
        (
            'What is the M6 tap drill size?',
            'The M6 (M6\xd71.0 coarse) tap drill is 5.0 mm using d − P (6 − 1.0 = 5.0 mm) per ISO 724.'
        ),
    ]
    html = update_tags(html, t, d)
    html = add_faq(html, qa)
    save(path, html)


def proc_calculator(path):
    html = open(path, encoding='utf-8').read()
    t = 'Thread Calculator — Pitch Ø, Minor Ø & Tap Drill for Any Thread'
    d = ('Calculate pitch diameter, minor diameter, tap drill size, and tensile stress area '
         'for any metric or inch thread. Supports ISO metric, UNC, UNF, and custom pitches. '
         'Instant results.')
    if len(d) > 158:
        d = ('Calculate pitch Ø, minor Ø, tap drill, and stress area for any metric or inch thread. '
             'ISO metric, UNC, UNF, and custom pitch supported. Instant results.')
    qa = [
        (
            'How do I calculate thread pitch diameter?',
            'For metric threads: d₂ = d − 0.6495 × P. '
            'For inch threads: d₂ = d − 0.6495 / n (where d = major diameter, '
            'P = pitch in mm, n = TPI). The pitch diameter is where thread width equals space width.'
        ),
        (
            'How do I calculate tap drill size?',
            'The standard tap drill is d − P (nominal diameter minus pitch) for approximately '
            '75% thread engagement. For M10\xd71.5: 10 − 1.5 = 8.5 mm. '
            'For 1/4-20 UNC: 0.250 − 1/20 = 0.200″, nearest standard is #7 (0.201″).'
        ),
        (
            'What is tensile stress area?',
            'Tensile stress area (Aₛ) = π/4 × ((d₂ + d₃)/2)² '
            'where d₂ is the pitch diameter and d₃ = D₁ − H/6. '
            'It represents the effective cross-sectional area under tension per ISO 898 and ASME B1.1.'
        ),
    ]
    html = update_tags(html, t, d)
    html = add_faq(html, qa)
    save(path, html)


def proc_npt_vs_bsp(path):
    html = open(path, encoding='utf-8').read()
    t = 'NPT vs BSP Pipe Threads — Thread Angle, Taper & Compatibility'
    d = ('Side-by-side comparison of NPT (60°, ASME B1.20.1) and BSP (55°, ISO 228/7) pipe threads: '
         'thread angle, taper, nominal vs actual OD, and global usage. '
         'Explains why they are not interchangeable.')
    if len(d) > 158:
        d = ('NPT vs BSP: 60° vs 55° thread angle, both 1:16 taper. '
             'Not interchangeable. NPT: North America (ASME B1.20.1). '
             'BSP: UK, Europe, Asia (ISO 228/7).')
    qa = [
        (
            'Can NPT and BSP fittings connect?',
            'No. NPT uses a 60° thread angle; BSP uses 55° Whitworth. '
            'Even though nominal sizes appear similar, the different angles mean they will not seal '
            'correctly together. Adapters exist but a direct thread-to-thread seal is unreliable.'
        ),
        (
            'What is the thread angle of NPT vs BSP?',
            'NPT (National Pipe Taper, ASME B1.20.1) uses a 60° included thread angle. '
            'BSP (British Standard Pipe, ISO 228/7) uses a 55° Whitworth thread angle. '
            'This difference makes them mechanically incompatible.'
        ),
        (
            'Which is more common — NPT or BSP?',
            'NPT is the standard in North America (USA, Canada, Mexico). '
            'BSP (both parallel G-thread and tapered R-thread) is standard in UK, Europe, Asia, '
            'and Australia. Both are widely encountered globally.'
        ),
        (
            'What does 1/2″ NPT mean?',
            '1/2″ NPT means the nominal pipe size is 1/2″, but the actual outside diameter '
            'is 0.840″ (21.34 mm). NPT nominal sizes refer to the original iron pipe bore, not '
            'the actual thread OD. NPT = National Pipe Taper per ASME B1.20.1.'
        ),
    ]
    html = update_tags(html, t, d)
    html = add_faq(html, qa)
    save(path, html)


def proc_home(path):
    html = open(path, encoding='utf-8').read()
    t = 'Thread Specs & Tap Drill Charts — UNC, UNF, NPT, BSP & Metric'
    d = ('Tap drill sizes, pitch diameters, and thread dimensions for UNC, UNF, UNEF, NPT, BSP, '
         'and ISO metric threads. M8: 6.8 mm; 1/4-20 UNC: #7; 1/2 NPT: 23/32″. '
         'Per ASME B1.1, ISO 724, ASME B1.20.1.')
    if len(d) > 158:
        d = ('Thread specs for UNC, UNF, NPT, BSP, and ISO metric threads. '
             'M8: 6.8 mm drill; 1/4-20 UNC: #7; 1/2 NPT: 23/32″. '
             'Per ASME B1.1, ISO 724, ASME B1.20.1.')
    qa = [
        (
            'What is the tap drill for 1/4-20 UNC?',
            'The tap drill for 1/4-20 UNC is #7 (0.2010″ / 5.11 mm) per ASME B1.1, '
            'giving approximately 75% thread engagement.'
        ),
        (
            'What is the M8 tap drill size?',
            'The M8 (M8\xd71.25 coarse) tap drill is 6.8 mm using the d − P formula '
            '(8 − 1.25 = 6.75, rounded up to standard 6.8 mm) per ISO 724.'
        ),
        (
            'What is the difference between UNC and UNF threads?',
            'UNC (Unified National Coarse) has fewer threads per inch and is the standard for '
            'general-purpose fastening. UNF (fine) has more TPI, higher tensile strength, and '
            'better vibration resistance, but is more susceptible to cross-threading.'
        ),
        (
            'What is the difference between NPT and BSP pipe threads?',
            'NPT (American standard, ASME B1.20.1) uses a 60° thread angle and is standard '
            'in North America. BSP (British/international, ISO 228) uses a 55° Whitworth angle '
            'and is standard in Europe, Asia, and Australia. They are not interchangeable.'
        ),
    ]
    html = update_tags(html, t, d)
    html = add_faq(html, qa)
    save(path, html)


# ============================================================
# MAIN
# ============================================================

def iter_subpages(base_dir):
    """Yield paths for sub-pages (skip the index.html of the dir itself)."""
    try:
        for slug_dir in sorted(os.listdir(base_dir)):
            p = os.path.join(base_dir, slug_dir, 'index.html')
            if os.path.isfile(p):
                yield p
    except FileNotFoundError:
        pass


def main():
    print('\n=== UNC detail pages ===')
    for p in iter_subpages(os.path.join(BASE, 'unc')):
        proc_inch_detail(p)

    print('\n=== UNF detail pages ===')
    for p in iter_subpages(os.path.join(BASE, 'unf')):
        proc_inch_detail(p)

    print('\n=== UNEF detail pages ===')
    for p in iter_subpages(os.path.join(BASE, 'unef')):
        proc_inch_detail(p)

    print('\n=== NPT detail pages ===')
    for p in iter_subpages(os.path.join(BASE, 'npt')):
        proc_npt_detail(p)

    print('\n=== BSP detail pages ===')
    for p in iter_subpages(os.path.join(BASE, 'bsp')):
        proc_bsp_detail(p)

    print('\n=== Metric coarse detail pages ===')
    for p in iter_subpages(os.path.join(BASE, 'metric')):
        proc_metric_detail(p, is_fine=False)

    print('\n=== Metric fine detail pages ===')
    for p in iter_subpages(os.path.join(BASE, 'metric-fine')):
        proc_metric_detail(p, is_fine=True)

    print('\n=== Category / hub pages ===')
    proc_unc_index(os.path.join(BASE, 'unc', 'index.html'))
    proc_unf_index(os.path.join(BASE, 'unf', 'index.html'))
    proc_unef_index(os.path.join(BASE, 'unef', 'index.html'))
    proc_metric_index(os.path.join(BASE, 'metric', 'index.html'))
    proc_metric_fine_index(os.path.join(BASE, 'metric-fine', 'index.html'))
    proc_npt_index(os.path.join(BASE, 'pipe-threads', 'index.html'))
    proc_bsp_index(os.path.join(BASE, 'bsp', 'index.html'))
    proc_tap_drill_chart(os.path.join(BASE, 'tap-drill-chart', 'index.html'))
    proc_calculator(os.path.join(BASE, 'calculator', 'index.html'))
    proc_npt_vs_bsp(os.path.join(BASE, 'npt-vs-bsp', 'index.html'))

    print('\n=== Homepage ===')
    proc_home(os.path.join(BASE, 'index.html'))

    print('\nDone.')


if __name__ == '__main__':
    main()
