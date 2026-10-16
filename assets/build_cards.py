#!/usr/bin/env python

"""
Purpose: Renders every SVG the profile README uses (hero, product cards,
         manifesto banner, writing cards) from one small dict, so adding a
         product is one entry and a rerun. No third-party image servers.
         Layout system: 830px full width, 408px cards (two + gutter = 830).
Author(s): John Reed
"""


# Imports
import logging
import os
import sys


# Logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
LOG = logging.getLogger("root.build_cards")
LOG.setLevel(logging.INFO)


# Constants
##################################################################
# One metal, never leave it. Catppuccin Macchiato base + peach,  #
# same palette as eventually-consistent.io.                      #
##################################################################
PEACH = "#f5a97f"
PEACH_SHADOW = "#b97a5c"
BASE = "#24273a"
MANTLE = "#1e2030"
SURFACE = "#363a4f"
TEXT = "#cad3f5"
SUBTEXT = "#a5adcb"
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

FULL_W = 830
CARD_W = 408
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

HERO = {
    "name": "John Reed",
    "line": "28 years of infrastructure. Now building with AI.",
    "sub": "Cloud / SRE / DevOps / ex-AWS TAM / Terraform / distributed DBs",
}

PRODUCTS = [
    {
        "slug": "cairn",
        "title": "cairn",
        "lines": [
            "Converged work management for AI CLIs.",
            "Tracker-truth planning, provenance-checked",
            "memory, one typed MCP server.",
        ],
        "repo": "eventually-consistent-code/cairn2",
    },
    {
        "slug": "okrdokey",
        "title": "OKRdokey",
        "lines": [
            "Self-hostable OKR tracker for small teams.",
            "Spreadsheet-simple, docker-compose-up,",
            "your data.",
        ],
        "repo": "eventually-consistent-code/okrdokey",
    },
    {
        "slug": "tagmanager",
        "title": "TagManager",
        "lines": [
            "Multi-cloud tag compliance. Scan AWS,",
            "Azure and GCP, catch missing or wrong tags,",
            "see it all in one dashboard.",
        ],
        "repo": "eventually-consistent-code/TagManager",
    },
    {
        "slug": "workspaces",
        "title": "AWS WorkSpaces, multi-region",
        "lines": [
            "Terragrunt/Terraform template for WorkSpaces",
            "across regions. Preflight validation,",
            "Well-Architected docs, sanitized.",
        ],
        "repo": "eventually-consistent-code/aws-workspaces-multi-region-deployment",
    },
]

MANIFESTO = "Tracker-truth. Provenance-checked. Eventually consistent."

POSTS = [
    {
        "slug": "post_harness_runs_itself",
        "date": "2026-09-10",
        "title": "The Harness Runs Itself",
        "line": "cairn runs whole phases unattended inside a token budget, and catches its own bugs in the act.",
    },
    {
        "slug": "post_work_harness",
        "date": "2026-08-14",
        "title": "The Work Harness",
        "line": "Six weeks turned cairn from a wrapper into a full work harness. Who is it actually competing with?",
    },
    {
        "slug": "post_four_tools",
        "date": "2026-08-04",
        "title": "Four Tools in Three Weeks",
        "line": "What building with AI actually looked like: four products, one coordinated launch, receipts included.",
    },
]


# Helpers
def esc(text):
    """
    Escapes the three characters that break SVG text nodes.
    :param text: raw string
    :returns escaped string
    """
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def frame(width, height, body, title):
    """
    Wraps body markup in the shared card chrome: rounded base panel,
    peach left rule, and an accessible title.
    :param width: svg width in px
    :param height: svg height in px
    :param body: inner svg markup
    :param title: accessible name for the image
    :returns full svg document as a string
    """
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">
  <title>{esc(title)}</title>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="{BASE}" stroke="{SURFACE}"/>
  <rect x="0" y="12" width="4" height="{height - 24}" rx="2" fill="{PEACH}"/>
{body}
</svg>
"""


def write(name, svg):
    """
    Writes one svg to the assets dir next to this script.
    :param name: file name without extension
    :param svg: svg markup
    """
    path = os.path.join(OUT_DIR, f"{name}.svg")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(svg)
    LOG.info("%s written...", os.path.basename(path))


# Renderers
def hero():
    """
    Full-width hero: name, the one line, a quiet subline.
    """
    body = f"""  <text x="32" y="64" font-family="{FONT}" font-size="34" font-weight="700" fill="{PEACH}">{esc(HERO["name"])}</text>
  <text x="32" y="104" font-family="{FONT}" font-size="20" fill="{TEXT}">{esc(HERO["line"])}</text>
  <text x="32" y="140" font-family="{FONT}" font-size="14" fill="{SUBTEXT}">{esc(HERO["sub"])}</text>
  <text x="{FULL_W - 32}" y="140" text-anchor="end" font-family="{FONT}" font-size="14" fill="{PEACH_SHADOW}">eventually-consistent.io</text>"""
    write("hero", frame(FULL_W, 172, body, f"{HERO['name']}: {HERO['line']}"))


def product_card(product):
    """
    408px product card: title, three-line pitch, repo path.
    :param product: dict with slug/title/lines/repo
    """
    rows = "".join(
        f'  <text x="28" y="{76 + i * 22}" font-family="{FONT}" font-size="14" fill="{TEXT}">{esc(line)}</text>\n'
        for i, line in enumerate(product["lines"])
    )
    body = f"""  <text x="28" y="44" font-family="{FONT}" font-size="22" font-weight="700" fill="{PEACH}">{esc(product["title"])}</text>
{rows}  <text x="28" y="164" font-family="{FONT}" font-size="12" fill="{PEACH_SHADOW}">github.com/{esc(product["repo"])}</text>"""
    write(f"card_{product['slug']}", frame(CARD_W, 184, body, f"{product['title']}: {' '.join(product['lines'])}"))


def manifesto():
    """
    One line, full width, the thing a visitor can repeat.
    """
    body = f"""  <text x="{FULL_W / 2}" y="58" text-anchor="middle" font-family="{FONT}" font-size="22" font-weight="700" fill="{PEACH}">{esc(MANIFESTO)}</text>"""
    write("manifesto", frame(FULL_W, 96, body, MANIFESTO))


def metrics_placeholder():
    """
    Stand-in for metrics.svg so the README never shows a broken image.
    The metrics workflow overwrites this file on its first successful run.
    """
    body = f"""  <text x="{FULL_W / 2}" y="52" text-anchor="middle" font-family="{FONT}" font-size="16" fill="{TEXT}">status renders here daily once the metrics workflow runs...</text>
  <text x="{FULL_W / 2}" y="78" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{SUBTEXT}">commits / streak / most-used languages, rendered into this repo, no third-party image server</text>"""
    write("metrics", frame(FULL_W, 108, body, "GitHub activity placeholder, replaced daily by the metrics workflow"))


def post_card(post):
    """
    Full-width writing card: date, title, one-line hook.
    :param post: dict with slug/date/title/line
    """
    body = f"""  <text x="28" y="40" font-family="{FONT}" font-size="12" fill="{PEACH_SHADOW}">{esc(post["date"])}</text>
  <text x="120" y="40" font-family="{FONT}" font-size="18" font-weight="700" fill="{PEACH}">{esc(post["title"])}</text>
  <text x="28" y="70" font-family="{FONT}" font-size="14" fill="{TEXT}">{esc(post["line"])}</text>"""
    write(post["slug"], frame(FULL_W, 96, body, f"{post['title']} ({post['date']}): {post['line']}"))


# Main
def main():
    """
    Renders every asset. Exit code is the count of failures, zero is good.
    """
    LOG.info("rendering profile assets...")
    errors = 0
    jobs = [hero, manifesto] + ([metrics_placeholder] if not os.path.exists(os.path.join(OUT_DIR, "metrics.svg")) else []) + [lambda p=p: product_card(p) for p in PRODUCTS] + [lambda p=p: post_card(p) for p in POSTS]
    for job in jobs:
        try:
            job()
        except (OSError, KeyError) as err:
            errors += 1
            LOG.error("render failed: %s", err)
    LOG.info("done. %d asset(s), %d error(s).", len(jobs), errors)
    sys.exit(errors)


if __name__ == "__main__":
    main()
