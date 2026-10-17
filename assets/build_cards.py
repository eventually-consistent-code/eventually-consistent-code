#!/usr/bin/env python

"""
Purpose: Renders every SVG the profile README uses (hero, product cards,
         manifesto banner, writing cards) from one small dict, so adding a
         product is one entry and a rerun. No third-party image servers.
         Look: the Mac-OS-X Aqua theme of eventually-consistent.io, white
         windows with a gradient title bar and traffic lights, one blue.
         Layout system: 830px full width, 408px cards (two + gutter = 830).
Author(s): John Reed
"""


# Imports
import base64
import logging
import os
import struct
import sys


# Logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
LOG = logging.getLogger("root.build_cards")
LOG.setLevel(logging.INFO)


# Constants
##################################################################
# One metal, never leave it. Measured off the live site's CSS:   #
# navy text, Aqua blue accent, white windows on a pale page.     #
##################################################################
WINDOW = "#ffffff"
BORDER = "#9db3c7"
BORDER_SOFT = "#c3d3e2"
BAR_LINE = "#9fb6cc"
TEXT = "#1f2d3a"
HEADING = "#14304b"
MUTED = "#5f7389"
BLUE = "#2f7fd6"
BLUE_DEEP = "#1a5fb4"
CODE_BG = "#1c1d21"
CODE_TEXT = "#e6edf3"
CODE_PROMPT = "#8ab4f8"
LIGHT_RED, LIGHT_YELLOW, LIGHT_GREEN = "#ff5f57", "#febc2e", "#28c840"
FONT = "'Lucida Grande', 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

FULL_W = 830
CARD_W = 408
BAR_H = 26
INSET = 4
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_DIR = os.path.join(OUT_DIR, "logos")

HERO = {
    "name": "John Reed",
    "line": "28 years of infrastructure. Now building with AI.",
    "sub": "Cloud / SRE / DevOps / ex-AWS TAM / Terraform / distributed DBs",
    "logo": "sphere",
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
        "repo": "eventually-consistent-code-org/cairn2",
        "button": "INSTALL CAIRN",
        "cmd": ["/plugin marketplace add \\", "  eventually-consistent-code-org/cairn2", "/plugin install cairn@cairn-dev"],
        "logo": "cairn",
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
        "button": "RUN OKRDOKEY",
        "cmd": ["gh repo clone eventually-consistent-code/okrdokey", "cd okrdokey && docker compose up"],
        "logo": "okrdokey",
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
        "button": "RUN TAGMANAGER",
        "cmd": ["gh repo clone eventually-consistent-code/TagManager", "cd TagManager && docker compose up"],
        "logo": "tagmanager",
    },
    {
        "slug": "workspaces",
        "title": "AWS WorkSpaces",
        "lines": [
            "Terragrunt/Terraform template for WorkSpaces",
            "across regions. Preflight validation,",
            "Well-Architected docs, sanitized.",
        ],
        "repo": "eventually-consistent-code/aws-workspaces-multi-region-deployment",
        "button": "CLONE TEMPLATE",
        "cmd": ["gh repo clone eventually-consistent-code/ \\", "  aws-workspaces-multi-region-deployment"],
        "logo": None,
    },
]

MANIFESTO = "Tracker-truth. Provenance-checked. Eventually consistent."

POSTS = [
    {
        "slug": "post_harness_runs_itself",
        "date": "2026-09-10",
        "title": "The Harness Runs Itself",
        "line": "cairn runs whole phases unattended inside a token budget, and catches its own bugs.",
    },
    {
        "slug": "post_work_harness",
        "date": "2026-08-14",
        "title": "The Work Harness",
        "line": "Six weeks turned cairn from a wrapper into a work harness. Who is it competing with?",
    },
    {
        "slug": "post_four_tools",
        "date": "2026-08-04",
        "title": "Four Tools in Three Weeks",
        "line": "What building with AI actually looked like: four products, one launch, receipts included.",
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


def logo(name, x, y, height):
    """
    Embeds one PNG from assets/logos as a data URI so the card stays a single
    self-contained file. Width follows the PNG's own aspect ratio.
    :param name: file stem in assets/logos
    :param x: left edge
    :param y: top edge
    :param height: rendered height in px
    :returns (svg image element, rendered width)
    """
    path = os.path.join(LOGO_DIR, f"{name}.png")
    with open(path, "rb") as handle:
        raw = handle.read()
    # PNG keeps its size in the IHDR chunk, bytes 16-24, no library needed
    px_w, px_h = struct.unpack(">II", raw[16:24])
    width = round(height * px_w / px_h)
    data = base64.b64encode(raw).decode("ascii")
    return (
        f'  <image x="{x}" y="{y}" width="{width}" height="{height}" href="data:image/png;base64,{data}"/>\n',
        width,
    )


def mark(x, y, size, letters):
    """
    Fallback app-icon for a product with no logo: a blue Aqua tile with two
    letters, so the card row stays level with its neighbours.
    :param x: left edge
    :param y: top edge
    :param size: tile size in px
    :param letters: short text drawn on the tile
    :returns svg markup
    """
    return (
        f'  <rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{size * 0.22}" fill="url(#aqua-blue)" stroke="{BLUE_DEEP}"/>\n'
        f'  <rect x="{x + 2}" y="{y + 2}" width="{size - 4}" height="{size / 2 - 2}" rx="{size * 0.18}" fill="#ffffff" fill-opacity="0.22"/>\n'
        f'  <text x="{x + size / 2}" y="{y + size * 0.66}" text-anchor="middle" font-family="{FONT}" font-size="{size * 0.4}" font-weight="700" fill="#ffffff">{esc(letters)}</text>\n'
    )


def defs():
    """
    Shared gradients and the window shadow. Same ids in every file, each
    svg is its own document so they never collide.
    :returns svg defs block
    """
    return f"""  <defs>
    <linearGradient id="aqua-bar" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fdfeff"/>
      <stop offset="0.5" stop-color="#eaf1f8"/>
      <stop offset="0.51" stop-color="#d4e2f0"/>
      <stop offset="1" stop-color="#e3eef8"/>
    </linearGradient>
    <linearGradient id="aqua-blue" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#5ea0e6"/>
      <stop offset="0.5" stop-color="{BLUE}"/>
      <stop offset="0.51" stop-color="#2a73c7"/>
      <stop offset="1" stop-color="{BLUE_DEEP}"/>
    </linearGradient>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="115%">
      <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#28466e" flood-opacity="0.22"/>
    </filter>
  </defs>
"""


def frame(width, height, body, title, bar=None):
    """
    Wraps body markup in the shared window chrome: white panel with a soft
    shadow, an Aqua title bar with traffic lights when a bar title is given,
    and an accessible title.
    :param width: svg width in px
    :param height: svg height in px
    :param body: inner svg markup
    :param title: accessible name for the image
    :param bar: text for the title bar, None for a bare panel
    :returns full svg document as a string
    """
    win_w, win_h = width - 2 * INSET, height - 2 * INSET
    chrome = ""
    if bar is not None:
        # Clip the gradient bar to the window's rounded top
        lights = "".join(
            f'  <circle cx="{INSET + 18 + i * 18}" cy="{INSET + BAR_H / 2}" r="5.5" fill="{color}" stroke="#000" stroke-opacity="0.18"/>\n'
            for i, color in enumerate((LIGHT_RED, LIGHT_YELLOW, LIGHT_GREEN))
        )
        chrome = f"""  <clipPath id="win"><rect x="{INSET}" y="{INSET}" width="{win_w}" height="{win_h}" rx="10"/></clipPath>
  <rect x="{INSET}" y="{INSET}" width="{win_w}" height="{BAR_H}" fill="url(#aqua-bar)" clip-path="url(#win)"/>
  <line x1="{INSET}" y1="{INSET + BAR_H + 0.5}" x2="{INSET + win_w}" y2="{INSET + BAR_H + 0.5}" stroke="{BAR_LINE}"/>
{lights}  <text x="{(INSET + 72 + width - INSET - 12) / 2}" y="{INSET + BAR_H / 2 + 4.5}" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{HEADING}">{esc(bar)}</text>
"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">
  <title>{esc(title)}</title>
{defs()}  <rect x="{INSET}" y="{INSET}" width="{win_w}" height="{win_h}" rx="10" fill="{WINDOW}" stroke="{BORDER}" filter="url(#shadow)"/>
{chrome}{body}
</svg>
"""


def button(cx, top, width, label):
    """
    Aqua pill: blue gradient, gloss highlight, white label. Drawn into the
    card so the whole image is one link.
    :param cx: horizontal centre
    :param top: top edge
    :param width: pill width
    :param label: button text
    :returns svg markup
    """
    left = cx - width / 2
    return f"""  <rect x="{left}" y="{top}" width="{width}" height="34" rx="17" fill="url(#aqua-blue)" stroke="{BLUE_DEEP}"/>
  <rect x="{left + 3}" y="{top + 2}" width="{width - 6}" height="15" rx="8" fill="#ffffff" fill-opacity="0.28"/>
  <text x="{cx}" y="{top + 22}" text-anchor="middle" font-family="{FONT}" font-size="12" font-weight="700" letter-spacing="1" fill="#ffffff">&#9654;  {esc(label)}</text>
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
    Full-width hero window: the sphere, name, the one line, a quiet subline.
    """
    height = 176
    sphere, sphere_w = logo(HERO["logo"], 30, BAR_H + 22, 104)
    left = 30 + sphere_w + 26
    body = f"""{sphere}  <text x="{left}" y="{BAR_H + 56}" font-family="{FONT}" font-size="34" font-weight="700" fill="{HEADING}">{esc(HERO["name"])}</text>
  <text x="{left}" y="{BAR_H + 92}" font-family="{FONT}" font-size="19" fill="{TEXT}">{esc(HERO["line"])}</text>
  <text x="{left}" y="{BAR_H + 122}" font-family="{FONT}" font-size="13" fill="{MUTED}">{esc(HERO["sub"])}</text>
  <text x="{FULL_W - INSET - 24}" y="{BAR_H + 122}" text-anchor="end" font-family="{FONT}" font-size="13" fill="{BLUE}">eventually-consistent.io</text>"""
    write("hero", frame(FULL_W, height, body, f"{HERO['name']}: {HERO['line']}", bar="eventually-consistent.io"))


def product_card(product):
    """
    Product window: repo path in the title bar, icon and name, three-line
    pitch, a dark terminal strip with the install command, and the Aqua
    button drawn into the card so the whole image is one link.
    :param product: dict with slug/title/lines/repo/cmd/button/logo
    """
    icon_top, icon_h = BAR_H + 20, 56
    if product["logo"]:
        icon, icon_w = logo(product["logo"], 28, icon_top, icon_h)
    else:
        icon, icon_w = mark(28, icon_top, icon_h, "WS"), icon_h
    rows = "".join(
        f'  <text x="28" y="{BAR_H + 108 + i * 22}" font-family="{FONT}" font-size="14" fill="{TEXT}">{esc(line)}</text>\n'
        for i, line in enumerate(product["lines"])
    )
    # Every card shares the tallest strip so paired cards sit level
    strip_top = BAR_H + 108 + 3 * 22 - 6
    strip_h = 16 + 17 * max(len(x["cmd"]) for x in PRODUCTS)
    cmds = "".join(
        f'  <text x="28" y="{strip_top + 19 + i * 17}" font-family="{MONO}" font-size="10" fill="{CODE_PROMPT}">$ <tspan fill="{CODE_TEXT}">{esc(line)}</tspan></text>\n'
        for i, line in enumerate(product["cmd"])
    )
    # Long repo paths overrun a 408px title bar, so fall back to the bare repo name
    bar = f"github.com/{product['repo']}" if len(product["repo"]) <= 40 else f".../{product['repo'].split('/')[1]}"
    btn_top = strip_top + strip_h + 14
    body = f"""{icon}  <text x="{28 + icon_w + 16}" y="{icon_top + 36}" font-family="{FONT}" font-size="22" font-weight="700" fill="{HEADING}">{esc(product["title"])}</text>
{rows}  <rect x="{INSET + 12}" y="{strip_top}" width="{CARD_W - 2 * INSET - 24}" height="{strip_h}" rx="6" fill="{CODE_BG}"/>
{cmds}{button(CARD_W / 2, btn_top, 220, product["button"])}"""
    height = btn_top + 34 + 18 + INSET
    write(f"card_{product['slug']}", frame(CARD_W, height, body, f"{product['title']}: {' '.join(product['lines'])} {product['button']}: {' '.join(product['cmd'])}", bar=bar))


def manifesto():
    """
    One line, full width, the thing a visitor can repeat. An Aqua gradient
    strip, no window chrome.
    """
    height = 72
    body = f"""  <rect x="{INSET}" y="{INSET}" width="{FULL_W - 2 * INSET}" height="{height - 2 * INSET}" rx="10" fill="url(#aqua-bar)" stroke="{BAR_LINE}"/>
  <text x="{FULL_W / 2}" y="{height / 2 + 8}" text-anchor="middle" font-family="{FONT}" font-size="22" font-weight="700" fill="{HEADING}">{esc(MANIFESTO)}</text>"""
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{FULL_W}" height="{height}" viewBox="0 0 {FULL_W} {height}" role="img" aria-label="{esc(MANIFESTO)}">
  <title>{esc(MANIFESTO)}</title>
{defs()}{body}
</svg>
"""
    write("manifesto", svg)


def metrics_placeholder():
    """
    Stand-in for metrics.svg so the README never shows a broken image.
    The metrics workflow overwrites this file on its first successful run.
    """
    body = f"""  <text x="{FULL_W / 2}" y="52" text-anchor="middle" font-family="{FONT}" font-size="16" fill="{TEXT}">status renders here daily once the metrics workflow runs...</text>
  <text x="{FULL_W / 2}" y="78" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{MUTED}">commits / streak / most-used languages, rendered into this repo, no third-party image server</text>"""
    write("metrics", frame(FULL_W, 108, body, "GitHub activity placeholder, replaced daily by the metrics workflow"))


def post_card(post):
    """
    Full-width writing entry, like the post list on the site: date, title,
    one-line hook, a blue read cue at the right.
    :param post: dict with slug/date/title/line
    """
    body = f"""  <text x="28" y="40" font-family="{FONT}" font-size="12" fill="{MUTED}">{esc(post["date"])}</text>
  <text x="118" y="40" font-family="{FONT}" font-size="18" font-weight="700" fill="{HEADING}">{esc(post["title"])}</text>
  <text x="28" y="68" font-family="{FONT}" font-size="14" fill="{TEXT}">{esc(post["line"])}</text>
  <text x="{FULL_W - INSET - 24}" y="40" text-anchor="end" font-family="{FONT}" font-size="12" font-weight="700" fill="{BLUE}">READ &#9654;</text>"""
    write(post["slug"], frame(FULL_W, 92, body, f"{post['title']} ({post['date']}): {post['line']}"))


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
        except (OSError, KeyError, struct.error) as err:
            errors += 1
            LOG.error("render failed: %s", err)
    LOG.info("done. %d asset(s), %d error(s).", len(jobs), errors)
    sys.exit(errors)


if __name__ == "__main__":
    main()
