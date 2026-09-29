#!/usr/bin/env python3
"""Quality gate for ThreadSpec.org. Exits non-zero on any failure.

1. Data: computed values against tables printed in the standards.
2. Pages: titles, descriptions, headings, structured data, links, sitemap.
"""
import glob
import html
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import tables  # noqa: E402
import threads  # noqa: E402

errors = []
warnings = []


def err(msg):
    errors.append(msg)


def check_data():
    F = threads.build()
    for t in F['metric'] + F['metric-fine']:
        if t['drill_mm'] < t['d1']:
            err(f"{t['name']}: tap drill {t['drill_mm']} below minor diameter {t['d1']:.3f}")
        if not 60 <= t['drill_pct'] <= 85:
            err(f"{t['name']}: tap drill gives {t['drill_pct']:.0f}% thread")
        if t['as_pub'] and abs(t['As'] - t['as_pub']) / t['as_pub'] > 0.004:
            err(f"{t['name']}: stress area {t['As']:.2f} vs ISO 898-1 {t['as_pub']}")
        c = tables.ISO965_CHECK.get((t['d'], t['p']))
        if c:
            L = t['tol']
            got = [t['d'] - L['es'], t['d'] - L['es'] - L['Td'], t['d2'] - L['es'],
                   t['d2'] - L['es'] - L['Td2'], t['d1'], t['d1'] + L['TD1'], t['d2'], t['d2'] + L['TD2']]
            for a, b in zip(got, c):
                if abs(a - b) > 0.0011:
                    err(f"{t['name']}: limit {a:.4f} vs ISO 965-2 {b}")
        if t['d'] > 1.4 and t['tol'] is None:
            err(f"{t['name']}: no ISO 965-1 tolerance found")
    for fam in ('unc', 'unf', 'unef'):
        for t in F[fam]:
            L = [float(x) for x in t['limits']]
            if abs(t['As'] - t['as_pub']) / t['as_pub'] > 0.006:
                err(f"{t['name']}: stress area {t['As']:.5f} vs B1.1 {t['as_pub']}")
            if abs(L[7] - t['d2']) > 0.00011:
                err(f"{t['name']}: pitch diameter {t['d2']:.4f} vs B1.1 {L[7]}")
            if abs(L[5] - t['d1']) > 0.0006:
                err(f"{t['name']}: minor diameter {t['d1']:.4f} vs B1.1 {L[5]}")
            if t['drill_in'] < L[5] - 0.002:
                err(f"{t['name']}: tap drill {t['drill_in']} below 2B minor minimum {L[5]}")
            if not 55 <= t['drill_pct'] <= 90:
                err(f"{t['name']}: tap drill gives {t['drill_pct']:.0f}% thread")
    for t in F['bsp']:
        c = tables.BSP_CHECK.get(t['label'])
        if c and (abs(t['d2'] - c[0]) > 0.0011 or abs(t['d1'] - c[1]) > 0.0011):
            err(f"{t['name']}: d2/d1 {t['d2']:.3f}/{t['d1']:.3f} vs ISO 228-1 {c}")
        if t['drill_mm'] <= t['d1']:
            err(f"{t['name']}: tap drill not above minor diameter")
    for t in F['npt']:
        p = t['p']
        if abs(t['E0'] + t['L1'] / 16 - t['E1']) > 2e-5:
            err(f"{t['name']}: E1 inconsistent with E0 and L1")
        if abs(t['E0'] + t['L2'] / 16 - t['E2']) > 6e-5:
            err(f"{t['name']}: E2 inconsistent with E0 and L2")
        if abs(t['E0'] - 0.8 * p - t['K0']) > 6e-5:
            err(f"{t['name']}: K0 inconsistent with E0")
        if abs(t['D'] - (0.05 * t['D'] + 1.1) * p - t['E0']) > 2e-5:
            err(f"{t['name']}: E0 inconsistent with D")
        for k in ('std', 'ream', 'common'):
            if t[k] and not (t['K0'] - 0.05 <= t[k]['in'] <= t['K0'] + 0.05):
                err(f"{t['name']}: {k} drill {t[k]['in']} far from K0 {t['K0']}")
    return sum(len(v) for v in F.values())


def check_pages():
    files = sorted(glob.glob(os.path.join(ROOT, '**', 'index.html'), recursive=True))
    files = [f for f in files if '/build/' not in f]
    titles, descs = Counter(), Counter()
    urls = set()
    for f in files:
        rel = '/' + os.path.relpath(os.path.dirname(f), ROOT).replace('\\', '/') + '/'
        if rel == '/./':
            rel = '/'
        urls.add(rel)
    sm = re.findall(r'<loc>https://threadspec\.org(/[^<]*)</loc>', open(os.path.join(ROOT, 'sitemap.xml')).read())
    words = []
    for f in files + [os.path.join(ROOT, '404.html')]:
        s = open(f, encoding='utf-8').read()
        rel = '/' + os.path.relpath(f, ROOT)
        url = rel[:-len('index.html')] if rel.endswith('index.html') else rel
        noindex = 'name="robots" content="noindex' in s
        for bad in ('/Users/', 'gmail.com', 'tailwind', 'hreflang'):
            if bad in s:
                err(f"{rel}: contains '{bad}'")
        m = re.search(r'<title>(.*?)</title>', s)
        title = html.unescape(m.group(1)) if m else ''
        if noindex:
            if 'adsbygoogle' in s:
                err(f"{rel}: ad script on a noindex page")
            if url in sm:
                err(f"{rel}: noindex page in sitemap")
            continue
        if url not in sm:
            err(f"{rel}: missing from sitemap")
        d = re.search(r'<meta name="description" content="(.*?)">', s)
        desc = html.unescape(d.group(1)) if d else ''
        if not title or len(title) > 60:
            err(f"{rel}: title length {len(title)}: {title}")
        if not 100 <= len(desc) <= 160:
            err(f"{rel}: description length {len(desc)}: {desc}")
        titles[title] += 1
        descs[desc] += 1
        if len(re.findall(r'<h1[ >]', s)) != 1:
            err(f"{rel}: expected one h1")
        c = re.search(r'<link rel="canonical" href="https://threadspec\.org(.*?)">', s)
        if not c or c.group(1) != url:
            err(f"{rel}: canonical {c.group(1) if c else None}")
        for blob in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            try:
                j = json.loads(blob)
            except ValueError as ex:
                err(f"{rel}: invalid JSON-LD ({ex})")
                continue
            if j.get('@type') == 'FAQPage':
                err(f"{rel}: FAQPage markup present")
        if url != '/' and '"BreadcrumbList"' not in s:
            err(f"{rel}: no BreadcrumbList")
        ids = re.findall(r'\sid="([^"]+)"', s)
        for k, v in Counter(ids).items():
            if v > 1:
                err(f"{rel}: duplicate id {k}")
        for a, b in re.findall(r'url\(#([^)]+)\)', s) and [(x, x) for x in re.findall(r'url\(#([^)]+)\)', s)]:
            if a not in ids:
                err(f"{rel}: clip-path target #{a} missing")
        for href in re.findall(r'href="(/[^"#?]*)(?:#[^"]*)?"', s):
            if href.startswith('//'):
                continue
            target = os.path.join(ROOT, href.strip('/'))
            if href.endswith('/') or href == '/':
                ok = os.path.isfile(os.path.join(target, 'index.html'))
            else:
                ok = os.path.isfile(target)
            if not ok:
                err(f"{rel}: broken link {href}")
        for frag in re.findall(r'href="#([^"]+)"', s):
            if frag not in ids:
                err(f"{rel}: broken fragment #{frag}")
        for sv in re.findall(r'<svg class="dg"[^>]*>', s):
            if 'aria-label="' not in sv or 'role="img"' not in sv:
                err(f"{rel}: diagram without text alternative")
        main = s[s.index('<main'):s.index('</main>')]
        main = re.sub(r'<script.*?</script>', ' ', main, flags=re.S)
        main = re.sub(r'<svg.*?</svg>', ' ', main, flags=re.S)
        n = len(re.sub(r'<[^>]+>', ' ', main).split())
        words.append((n, rel))
        if n < 300 and url not in ('/privacy/',):
            err(f"{rel}: only {n} words")
    for t, n in titles.items():
        if n > 1:
            err(f"duplicate title x{n}: {t}")
    for t, n in descs.items():
        if n > 1:
            err(f"duplicate description x{n}: {t}")
    for u in sm:
        if u not in urls:
            err(f"sitemap lists missing page {u}")
    if len(sm) != len(set(sm)):
        err('sitemap has duplicates')
    words.sort()
    return len(files), words


def main():
    n = check_data()
    pages, words = check_pages()
    for e_ in errors[:60]:
        print('FAIL', e_)
    if len(errors) > 60:
        print(f'... and {len(errors) - 60} more')
    med = words[len(words) // 2][0]
    print(f"{n} threads, {pages} pages, words min {words[0][0]} ({words[0][1]}) median {med}")
    print(f"home page {os.path.getsize(os.path.join(ROOT, 'index.html')) / 1024:.0f} KB")
    if errors:
        print(f"{len(errors)} failures")
        sys.exit(1)
    print('all checks passed')


if __name__ == '__main__':
    main()
