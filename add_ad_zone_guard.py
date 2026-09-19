#!/usr/bin/env python3
"""Stop Google Auto Ads from injecting ad slots inside data tables.

Two changes per HTML page that contains a <table>:

1. Tag every table wrapper (the existing <div class="overflow-x-auto">
   that directly precedes a <table>) with the marker class
   `data-table-zone`.
2. Inject a <style id="ad-zone-guard"> block into <head> that hides any
   auto-placed ad rendered inside a tagged zone.

A class is used rather than an id because most pages carry two tables,
and a repeated id would be invalid HTML. The stylesheet still honours
`#data-table-zone` so an id may be added by hand anywhere without a
second CSS edit.

Idempotent: re-running makes no further changes. Use --dry-run to preview.
"""

import argparse
import pathlib
import re
import sys

ZONE_CLASS = "data-table-zone"
STYLE_ID = "ad-zone-guard"

STYLE_BLOCK = (
    f'<style id="{STYLE_ID}">'
    "#data-table-zone .google-auto-placed,"
    "#data-table-zone ins.adsbygoogle,"
    f".{ZONE_CLASS} .google-auto-placed,"
    f".{ZONE_CLASS} ins.adsbygoogle{{display:none !important}}"
    "</style>"
)

# A <div> opening tag carrying a class attribute, immediately followed by
# a <table>. Captures the quoted class list so it can be extended.
WRAPPER_RE = re.compile(
    r'<div\b([^>]*?)\bclass="([^"]*)"([^>]*)>(\s*)(?=<table\b)',
    re.IGNORECASE,
)

# An already-injected style block, so the rule can be refreshed in place.
EXISTING_STYLE_RE = re.compile(
    rf'\s*<style id="{STYLE_ID}">.*?</style>', re.IGNORECASE | re.DOTALL
)

HEAD_CLOSE_RE = re.compile(r"</head>", re.IGNORECASE)


def tag_wrappers(html):
    """Add the marker class to each table wrapper. Returns (html, n_added)."""
    added = 0

    def repl(m):
        nonlocal added
        pre, classes, post, gap = m.groups()
        if ZONE_CLASS in classes.split():
            return m.group(0)
        added += 1
        return f'<div{pre}class="{classes} {ZONE_CLASS}"{post}>{gap}'

    return WRAPPER_RE.sub(repl, html), added


def inject_style(html):
    """Ensure the guard stylesheet is present and current. Returns (html, changed)."""
    existing = EXISTING_STYLE_RE.search(html)
    if existing:
        if existing.group(0).strip() == STYLE_BLOCK:
            return html, False
        # Stale version from an earlier run - replace it.
        html = EXISTING_STYLE_RE.sub("", html, count=1)

    if not HEAD_CLOSE_RE.search(html):
        return html, False
    return HEAD_CLOSE_RE.sub("\n" + STYLE_BLOCK + "\n</head>", html, count=1), True


def process(path, dry_run):
    html = path.read_text(encoding="utf-8")
    if "<table" not in html:
        return None

    out, n_wrapped = tag_wrappers(html)
    out, styled = inject_style(out)

    if out == html:
        return (path, 0, False)
    if not dry_run:
        path.write_text(out, encoding="utf-8")
    return (path, n_wrapped, styled)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".", help="repository root (default: .)")
    ap.add_argument("--dry-run", action="store_true", help="report without writing")
    args = ap.parse_args()

    root = pathlib.Path(args.root)
    pages = sorted(p for p in root.rglob("*.html") if ".git" not in p.parts)

    scanned = changed = wrappers = styles = 0
    for page in pages:
        result = process(page, args.dry_run)
        if result is None:
            continue
        scanned += 1
        _, n_wrapped, styled = result
        wrappers += n_wrapped
        styles += 1 if styled else 0
        if n_wrapped or styled:
            changed += 1

    verb = "would update" if args.dry_run else "updated"
    print(f"pages with tables : {scanned}")
    print(f"pages {verb:<13}: {changed}")
    print(f"wrappers tagged   : {wrappers}")
    print(f"style blocks added: {styles}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
