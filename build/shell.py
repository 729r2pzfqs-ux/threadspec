"""Page shell, formatting helpers and structured data for ThreadSpec.org."""
import json
from html import escape

SITE = 'https://threadspec.org'
TODAY = '2026-09-29'
TODAY_TEXT = '29 September 2026'
IN = 25.4

HEAD_SCRIPTS = """<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('consent','default',{'analytics_storage':'denied','ad_storage':'denied','ad_user_data':'denied','ad_personalization':'denied','wait_for_update':500,'region':['BE','BG','CZ','DK','DE','EE','IE','GR','ES','FR','HR','IT','CY','LV','LT','LU','HU','MT','NL','AT','PL','PT','RO','SI','SK','FI','SE','GB','CH','IS','LI','NO']});gtag('consent','default',{'analytics_storage':'granted','ad_storage':'granted','ad_user_data':'granted','ad_personalization':'granted'});</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5861928596436289" crossorigin="anonymous"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-EPVR72CBWM"></script>
<script>gtag('js',new Date());gtag('config','G-EPVR72CBWM');</script>
<script src="https://analytics.ahrefs.com/analytics.js" data-key="Mltx4IlGmyyajJD6d+8LLg" async></script>"""

NAV = [('/metric/', 'Metric'), ('/unc/', 'UNC'), ('/unf/', 'UNF'), ('/pipe-threads/', 'NPT'),
       ('/bsp/', 'BSP'), ('/tap-drill-chart/', 'Tap Drills'), ('/calculator/', 'Calculator'),
       ('/thread-identifier/', 'Identify')]

GEAR = ('<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" '
        'stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 '
        '002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 '
        '1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 '
        '1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 '
        '00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 '
        '2.37-2.37.996.608 2.296.07 2.572-1.065z"/><circle cx="12" cy="12" r="3"/></svg>')

FOOT = """<footer class="site-foot">
<div class="foot-in">
<div class="foot-grid">
<div><h2>Metric threads</h2><ul>
<li><a href="/metric/">ISO metric coarse chart</a></li>
<li><a href="/metric-fine/">ISO metric fine chart</a></li>
<li><a href="/metric/m6/">M6 thread</a></li>
<li><a href="/metric/m8/">M8 thread</a></li>
<li><a href="/metric/m10/">M10 thread</a></li>
<li><a href="/metric/m12/">M12 thread</a></li>
</ul></div>
<div><h2>Inch threads</h2><ul>
<li><a href="/unc/">UNC thread chart</a></li>
<li><a href="/unf/">UNF thread chart</a></li>
<li><a href="/unef/">UNEF thread chart</a></li>
<li><a href="/unc/1-4-unc/">1/4-20 UNC</a></li>
<li><a href="/unc/3-8-unc/">3/8-16 UNC</a></li>
<li><a href="/unc/1-2-unc/">1/2-13 UNC</a></li>
</ul></div>
<div><h2>Pipe threads</h2><ul>
<li><a href="/pipe-threads/">NPT thread chart</a></li>
<li><a href="/bsp/">BSP thread chart</a></li>
<li><a href="/npt-vs-bsp/">NPT vs BSP</a></li>
<li><a href="/npt/1-4-npt/">1/4 NPT</a></li>
<li><a href="/npt/1-2-npt/">1/2 NPT</a></li>
<li><a href="/bsp/g1-2-bsp/">G1/2 BSP</a></li>
</ul></div>
<div><h2>Tools and guides</h2><ul>
<li><a href="/tap-drill-chart/">Tap drill chart</a></li>
<li><a href="/calculator/">Thread calculator</a></li>
<li><a href="/thread-identifier/">Thread identifier</a></li>
<li><a href="/thread-terminology/">Thread terminology</a></li>
<li><a href="/coarse-vs-fine/">Coarse vs fine threads</a></li>
<li><a href="/about/">About and sources</a></li>
</ul></div>
</div>
<div class="foot-base">
<p>&copy; 2026 ThreadSpec.org. Thread dimensions and tap drill reference.</p>
<p>Contact: <!--email_off--><a href="mailto:info&#64;threadspec&#46;org">info&#64;threadspec&#46;org</a><!--/email_off--></p>
<p><a href="/about/">About</a> · <a href="/privacy/">Privacy</a> · <a href="/sitemap.xml">Sitemap</a></p>
</div>
</div>
</footer>"""

NAV_JS = ("var m=document.getElementById('nav-links');var o=m.classList.toggle('open');"
          "this.setAttribute('aria-expanded',o?'true':'false')")


def e(s):
    return escape(str(s), quote=True)


def ld(obj):
    return ('<script type="application/ld+json">'
            + json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
            + '</script>')


def breadcrumbs(trail):
    """trail: [(name, url or None), ...] starting after Home."""
    items = [('Home', '/')] + trail
    html = ['<nav class="crumbs" aria-label="Breadcrumb"><ol>']
    data = []
    for i, (name, url) in enumerate(items):
        last = i == len(items) - 1
        if last:
            html.append(f'<li aria-current="page">{e(name)}</li>')
        else:
            html.append(f'<li><a href="{url}">{e(name)}</a></li>')
        data.append({'@type': 'ListItem', 'position': i + 1, 'name': name,
                     'item': SITE + (url if url else '')})
    html.append('</ol></nav>')
    return ''.join(html), {'@context': 'https://schema.org', '@type': 'BreadcrumbList',
                           'itemListElement': data}


ORG = {'@type': 'Organization', 'name': 'ThreadSpec.org', 'url': SITE + '/',
       'logo': SITE + '/logos/logo-icon-512x512.png', 'email': 'info@threadspec.org'}


def webpage_ld(url, title, desc, about=None):
    d = {'@context': 'https://schema.org', '@type': 'WebPage', 'url': SITE + url, 'name': title,
         'description': desc, 'inLanguage': 'en', 'dateModified': TODAY,
         'isPartOf': {'@type': 'WebSite', 'name': 'ThreadSpec.org', 'url': SITE + '/'},
         'publisher': ORG}
    if about:
        d['about'] = about
    return d


def dataset_ld(url, name, desc, variables, based_on):
    return {'@context': 'https://schema.org', '@type': 'Dataset', 'name': name, 'description': desc,
            'url': SITE + url, 'inLanguage': 'en', 'dateModified': TODAY,
            'isAccessibleForFree': True, 'creator': ORG, 'publisher': ORG,
            'license': 'https://creativecommons.org/licenses/by/4.0/',
            'variableMeasured': variables, 'isBasedOn': based_on,
            'keywords': ['screw thread', 'tap drill', 'thread dimensions']}


def page(url, title, desc, body, trail=None, schema=None, og_image='/og-image.png', wide=False,
         noindex=False, extra_head='', scripts=''):
    crumbs_html, crumbs_ld = ('', None)
    if trail is not None:
        t = [(n, u) for n, u in trail]
        t[-1] = (t[-1][0], url)
        crumbs_html, crumbs_ld = breadcrumbs(t)
    lds = []
    if crumbs_ld:
        lds.append(ld(crumbs_ld))
    for s in (schema or []):
        lds.append(ld(s))
    nav = ''.join(f'<a href="{u}"{" aria-current=\"page\"" if url == u else ""}>{n}</a>' for u, n in NAV)
    robots = '<meta name="robots" content="noindex,follow">\n' if noindex else ''
    ads = '' if noindex else HEAD_SCRIPTS
    if noindex:
        # analytics only; no ads on pages kept out of the index
        ads = '\n'.join(l for l in HEAD_SCRIPTS.split('\n') if 'adsbygoogle' not in l)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{robots}<link rel="canonical" href="{SITE}{url}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{SITE}{url}">
<meta property="og:image" content="{SITE}{og_image}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="ThreadSpec.org">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#047857">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="stylesheet" href="/assets/site.css?v={CSS_VER}">
{ads}
{''.join(lds)}
{extra_head}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-nav">
<div class="nav-in">
<a href="/" class="brand">{GEAR}ThreadSpec.org</a>
<button class="nav-toggle" aria-label="Menu" aria-expanded="false" aria-controls="nav-links" onclick="{NAV_JS}"><svg fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg></button>
<nav class="nav-links" id="nav-links" aria-label="Main">{nav}</nav>
</div>
</header>
<main id="main"{' class="wide"' if wide else ''}>
{crumbs_html}
{body}
</main>
{FOOT}
{scripts}</body>
</html>
"""


CSS_VER = '1'


# ---------------------------------------------------------------- number formatting

def strip0(s):
    return s.rstrip('0').rstrip('.') if '.' in s else s


def mm(v, nd=3):
    return f"{v:.{nd}f}"


def inch(v, nd=4):
    return f"{v:.{nd}f}"


def mm_u(v, nd=3):
    return f"{v:.{nd}f} mm"


def in_u(v, nd=4):
    return f"{v:.{nd}f} in"


def g(v, nd=3):
    """Short form without trailing zeros: 8, 1.25, 0.75."""
    return strip0(f"{v:.{nd}f}")


def sig(v, n=3):
    """n significant figures, plain notation."""
    if v == 0:
        return '0'
    from math import floor, log10
    d = n - 1 - floor(log10(abs(v)))
    s = f"{round(v, d):.{max(d, 0)}f}"
    return s


def thousands(v):
    return f"{v:,.0f}"


# ---------------------------------------------------------------- html helpers

def table(head, rows, cls='', caption=None, label=None, rowcls=None, first_th=True, num_from=1):
    """head: list of header cells; rows: list of cell lists. Columns >= num_from are numeric."""
    h = ''.join(f'<th scope="col"{" class=\"n\"" if i >= num_from else ""}>{c}</th>'
                for i, c in enumerate(head))
    body = []
    for ri, r in enumerate(rows):
        rc = f' class="{rowcls[ri]}"' if rowcls and rowcls[ri] else ''
        cells = []
        for i, c in enumerate(r):
            n = ' class="n"' if i >= num_from else ''
            if i == 0 and first_th:
                cells.append(f'<th scope="row">{c}</th>')
            else:
                cells.append(f'<td{n}>{c}</td>')
        body.append(f'<tr{rc}>{"".join(cells)}</tr>')
    cap = f'<caption>{caption}</caption>' if caption else ''
    lab = f' aria-label="{e(label)}"' if label else ''
    c = f' class="{cls}"' if cls else ''
    return (f'<div class="tw data-table-zone" tabindex="0" role="region"{lab}>'
            f'<table{c}>{cap}<thead><tr>{h}</tr></thead><tbody>{"".join(body)}</tbody></table></div>')


def spec_table(rows, label, head=('Dimension', 'Value')):
    """Two or three column property table. rows: [(name, value[, value2])]."""
    n = max(len(r) for r in rows)
    hd = list(head)[:n]
    out = []
    for r in rows:
        tds = ''.join(f'<td class="n">{c}</td>' for c in r[1:])
        out.append(f'<tr><th scope="row">{r[0]}</th>{tds}</tr>')
    h = ''.join(f'<th scope="col"{" class=\"n\"" if i else ""}>{c}</th>' for i, c in enumerate(hd))
    return (f'<div class="tw data-table-zone" tabindex="0" role="region" aria-label="{e(label)}">'
            f'<table class="spec"><thead><tr>{h}</tr></thead><tbody>{"".join(out)}</tbody></table></div>')


def facts(items):
    """items: [(label, value, sub, highlight)]"""
    out = ['<ul class="facts">']
    for k, v, s, hl in items:
        sub = f'<span class="s">{s}</span>' if s else ''
        out.append(f'<li{" class=\"hl\"" if hl else ""}><span class="k">{k}</span>'
                   f'<span class="v">{v}</span>{sub}</li>')
    out.append('</ul>')
    return ''.join(out)


def chips(links):
    return '<ul class="chips">' + ''.join(f'<li><a href="{u}">{e(n)}</a></li>' for n, u in links) + '</ul>'


def cards(items):
    return ('<ul class="cards">' + ''.join(
        f'<li><a href="{u}"><span class="t">{e(t)}</span><span class="d">{e(d)}</span></a></li>'
        for t, d, u in items) + '</ul>')


def bar(pct, maxv=100.0):
    w = max(0.0, min(100.0, pct / maxv * 100))
    return f'<span class="bar" style="width:{w:.0f}%"></span>'
