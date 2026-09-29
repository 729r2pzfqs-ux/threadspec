#!/usr/bin/env python3
"""Generate ThreadSpec.org. Run from anywhere: python3 build/build.py"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import shell  # noqa: E402

with open(os.path.join(ROOT, 'assets', 'site.css'), 'rb') as fh:
    shell.CSS_VER = hashlib.sha1(fh.read()).hexdigest()[:8]

import detail60  # noqa: E402
import detailpipe  # noqa: E402
import guides  # noqa: E402
import hubs  # noqa: E402
import threads  # noqa: E402


def write(url, html):
    path = os.path.join(ROOT, url.strip('/'), 'index.html') if url.endswith('/') else os.path.join(ROOT, url.strip('/'))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(html)


def main():
    fams = threads.build()
    urls = []

    def out(url, html, prio):
        write(url, html)
        urls.append((url, prio))

    out('/', hubs.home(fams), '1.0')
    out('/metric/', hubs.metric_hub(fams), '0.9')
    out('/metric-fine/', hubs.metric_fine_hub(fams), '0.9')
    for fam in ('unc', 'unf', 'unef'):
        out(f'/{fam}/', hubs.un_hub(fam, fams), '0.9')
    out('/pipe-threads/', hubs.npt_hub(fams), '0.9')
    out('/bsp/', hubs.bsp_hub(fams), '0.9')
    out('/tap-drill-chart/', hubs.tap_chart(fams), '0.9')
    out('/calculator/', guides.calculator(fams), '0.8')
    out('/thread-identifier/', guides.identifier(fams), '0.8')
    out('/npt-vs-bsp/', guides.npt_vs_bsp(fams), '0.8')
    out('/coarse-vs-fine/', guides.coarse_vs_fine(fams), '0.8')
    out('/thread-terminology/', guides.terminology(fams), '0.7')
    for fam in ('metric', 'metric-fine', 'unc', 'unf', 'unef'):
        ts = fams[fam]
        for i, t in enumerate(ts):
            out(t['url'], detail60.build(t, fams, ts[i - 1] if i else None,
                                         ts[i + 1] if i + 1 < len(ts) else None), '0.7')
    for fam, fn in (('npt', detailpipe.build_npt), ('bsp', detailpipe.build_bsp)):
        ts = fams[fam]
        for i, t in enumerate(ts):
            out(t['url'], fn(t, fams, ts[i - 1] if i else None, ts[i + 1] if i + 1 < len(ts) else None), '0.7')
    out('/about/', guides.about(fams), '0.4')
    out('/privacy/', guides.privacy(), '0.2')
    write('/404.html', guides.not_found())
    write('/npt/', guides.npt_redirect())

    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, _ in urls:
        sm.append(f'<url><loc>{shell.SITE}{u}</loc><lastmod>{shell.TODAY}</lastmod></url>')
    sm.append('</urlset>')
    with open(os.path.join(ROOT, 'sitemap.xml'), 'w') as fh:
        fh.write('\n'.join(sm) + '\n')

    n = {k: len(v) for k, v in fams.items()}
    llms = f"""# ThreadSpec.org

> Reference for screw thread dimensions, tolerance limits and tap drills: {sum(n.values())} threads across ISO metric, Unified inch (UNC, UNF, UNEF), NPT and BSP. Diameters are computed from the ISO 724 and ASME B1.1 formulas and checked against the tables in the standards.

## Thread charts

- [ISO metric coarse]({shell.SITE}/metric/): {n['metric']} sizes, M1 to M68
- [ISO metric fine]({shell.SITE}/metric-fine/): {n['metric-fine']} sizes, M3x0.35 to M48x3
- [UNC]({shell.SITE}/unc/): {n['unc']} Unified coarse sizes, #1-64 to 4-4
- [UNF]({shell.SITE}/unf/): {n['unf']} Unified fine sizes, #0-80 to 1-1/2-12
- [UNEF]({shell.SITE}/unef/): {n['unef']} Unified extra fine sizes, #12-32 to 1-11/16-18
- [NPT]({shell.SITE}/pipe-threads/): {n['npt']} taper pipe thread sizes, 1/16 to 12, per ASME B1.20.1
- [BSP]({shell.SITE}/bsp/): {n['bsp']} parallel pipe thread sizes, G1/16 to G4, per ISO 228-1

## Tools and guides

- [Tap drill chart]({shell.SITE}/tap-drill-chart/): tap drills for every thread with percentage of thread
- [Thread calculator]({shell.SITE}/calculator/): basic dimensions for any diameter and pitch
- [Thread identifier]({shell.SITE}/thread-identifier/): find a thread from a measured diameter and pitch
- [NPT vs BSP]({shell.SITE}/npt-vs-bsp/): differences and compatibility
- [Coarse vs fine threads]({shell.SITE}/coarse-vs-fine/): what changes with the pitch
- [Thread terminology]({shell.SITE}/thread-terminology/): definitions and designations
- [About and sources]({shell.SITE}/about/): how the data is produced and checked

## On each thread page

Basic dimensions in mm and inches (major, pitch and minor diameter, thread height, lead angle, tensile stress area), tolerance limits (6g/6H or 2A/2B), the recommended tap drill with alternative drills and their percentage of thread, clearance holes, and proof loads by property class or SAE grade where the standard covers the size.

## Formulas (60 degree threads)

- H = 0.866025 x P
- Pitch diameter d2 = d - 0.649519 x P
- Internal minor diameter D1 = d - 1.082532 x P
- External root diameter d3 = d - 1.226869 x P (ISO metric), d - 1.190785 x P (Unified UNR)
- Stress area, metric: As = pi/4 x ((d2 + d3)/2)^2; inch: As = 0.7854 x (d - 0.9743/n)^2
- Percentage of thread = (d - drill) / (1.299038 x P) x 100

Contact: info@threadspec.org
"""
    with open(os.path.join(ROOT, 'llms.txt'), 'w') as fh:
        fh.write(llms)
    print(f"wrote {len(urls)} pages, css {shell.CSS_VER}")


if __name__ == '__main__':
    main()
