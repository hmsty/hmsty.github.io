"""Mirror a Substack publication into a static site.

Fetches every public post from Substack (cached in content/), then renders
HTML into site/. If Substack can't be reached, it builds from the cache.

Usage: python3 build.py [--offline]
"""
import html
import json
import re
import shutil
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

from reading import READING

# ---- settings ---------------------------------------------------------------
SUBSTACK = "https://willjensen.substack.com"
SITE_TITLE = "Will"
SITE_TAGLINE = "mostly markets"
LINKS = [
    ("x", "https://x.com/willjen45816414"),
    ("substack", SUBSTACK),
    ("linkedin", "https://www.linkedin.com/in/jensen-william/"),
]
SITE_URL = "https://hmsty.github.io"
PROJECT_GROUPS = [  # (group label, [(title, path under projects/, one-line description), ...]), newest first within a group
    ("blockchain", [
        ("A Web3 Dev Environment", "defi-agent", "a local environment for reading, analyzing, monitoring and transacting on blockchains from Claude Code"),
        ("The Lifecycle of a Tokenized Stock Trade", "two-ledgers", "order to finality on Wall Street and Ethereum, in 3D"),
        ("What a Blockchain Is", "what-a-blockchain-is", "an animated explainer, from first principles"),
    ]),
    ("ai", [
        ("Reading My AI History as Data", "reading-my-ai-history", "a year of my AI conversations, analyzed as a dataset"),
    ]),
    ("games", [
        ("GTO Practice Tool", "gto-practice-tool", "a free poker trainer that grades every decision against a solver"),
        ("Chess Wrapped", "chess-wrapped", "a data report on 4,400 of my chess games"),
    ]),
]
PROJECTS = [p for _, group in PROJECT_GROUPS for p in group]  # flat list, used for the sitemap
CONTACT_EMAIL = ""  # optional: a forwarding alias, never a real inbox
GOATCOUNTER = "hmsty"  # e.g. "hmsty" for hmsty.goatcounter.com; empty = no analytics
# -----------------------------------------------------------------------------

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
OUT = ROOT / "site"
UA = {"User-Agent": "Mozilla/5.0 (site mirror)"}


def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch():
    CONTENT.mkdir(exist_ok=True)
    offset = 0
    while True:
        batch = get_json(f"{SUBSTACK}/api/v1/archive?sort=new&offset={offset}&limit=50")
        if not batch:
            break
        for p in batch:
            if p.get("audience") != "everyone":
                continue  # skip paid-only posts
            path = CONTENT / f"{p['slug']}.json"
            post = get_json(f"{SUBSTACK}/api/v1/posts/{p['slug']}")
            keep = {k: post.get(k) for k in (
                "slug", "title", "subtitle", "post_date", "body_html",
                "cover_image", "canonical_url", "wordcount")}
            path.write_text(json.dumps(keep, indent=1), encoding="utf-8")
        offset += len(batch)


def fetch_rss():
    """Fallback when the API blocks us: the RSS feed has the newest ~20 posts."""
    import xml.etree.ElementTree as ET
    from email.utils import parsedate_to_datetime
    req = urllib.request.Request(f"{SUBSTACK}/feed", headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        root = ET.fromstring(r.read())
    ns = {"content": "http://purl.org/rss/1.0/modules/content/"}
    CONTENT.mkdir(exist_ok=True)
    for item in root.iter("item"):
        link = item.findtext("link")
        slug = link.rstrip("/").rsplit("/", 1)[-1]
        body = item.findtext("content:encoded", namespaces=ns) or ""
        enc = item.find("enclosure")
        words = len(re.sub(r"<[^>]+>", " ", body).split())
        date = parsedate_to_datetime(item.findtext("pubDate")).isoformat()
        (CONTENT / f"{slug}.json").write_text(json.dumps({
            "slug": slug, "title": item.findtext("title"),
            "subtitle": item.findtext("description"), "post_date": date,
            "body_html": body, "cover_image": enc.get("url") if enc is not None else None,
            "canonical_url": link, "wordcount": words}, indent=1), encoding="utf-8")


def clean_body(body):
    # Drop Substack's image toolbar buttons and icons.
    body = re.sub(r"<button\b.*?</button>", "", body, flags=re.S)
    body = re.sub(r"<svg\b.*?</svg>", "", body, flags=re.S)
    body = re.sub(r'\sdata-attrs="[^"]*"', "", body)
    # Subscribe widgets and share buttons belong to Substack.
    body = re.sub(r'<p class="button-wrapper".*?</p>', "", body, flags=re.S)
    body = re.sub(r'<div class="subscription-widget-wrap.*?</form></div></div>', "", body, flags=re.S)
    # A short paragraph that's entirely bold is a section heading.
    body = re.sub(r"<p><strong>([^<]{1,80})</strong></p>", r"<h2>\1</h2>", body)
    # The post title is the page's h1; make each post's top heading level h2
    # so sections look the same no matter which level was used on Substack.
    levels = [int(n) for n in re.findall(r"<h([1-6])\b", body)]
    if levels:
        shift = 2 - min(levels)
        body = re.sub(r"<(/?)h([1-6])\b",
                      lambda m: f"<{m.group(1)}h{min(6, int(m.group(2)) + shift)}", body)
    # Make bare URLs in footnotes clickable.
    def linkify(m):
        url = m.group(1)
        return f'<p><a href="{url}">{url}</a></p>'
    body = re.sub(r"<p>(https?://[^\s<]+)</p>", linkify, body)
    return body


def fmt_date(iso):
    d = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return f"{d:%B} {d.day}, {d:%Y}"  # %-d is Unix-only; this works on Windows too


FONTS = ("https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700"
         "&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap")

# Palette: background #262422 (warm graphite), ink #2B241C, paper #EDE6D6, moss #5C6B47, moss-ink #3A4530,
# rust #9C4A2E, brass #96721F. Moss/rust/brass are too dark for text on ink,
# so they're only used for rules, underlines and highlights.
CSS = """
:root{--ink:#262422;--ink-2:#312e2b;--paper:#EDE6D6;--body:#e2dacb;--muted:#a9a295;
--moss:#5C6B47;--rust:#9C4A2E;--brass:#96721F;--brass-lt:#b9a068;
--mono:"JetBrains Mono",ui-monospace,Menlo,monospace;--serif:"Source Serif 4",Georgia,serif}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;color-scheme:dark}
body{margin:0;background:var(--ink);color:var(--paper);font:14px/1.75 var(--mono);-webkit-font-smoothing:antialiased}
.w{max-width:660px;margin:0 auto;padding:56px 20px 40px}
a{color:var(--paper);text-decoration:none;border-bottom:1px solid var(--moss);transition:color .15s,border-color .15s}
a:hover{color:var(--brass-lt);border-color:var(--brass)}
a:focus-visible{outline:2px solid var(--brass-lt);outline-offset:3px;border-radius:2px}
html{scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important}}
::selection{background:var(--rust);color:var(--paper)}
.hd{display:flex;align-items:center;gap:14px;margin:0 0 44px}
.hd img{width:44px;height:44px;border-radius:50%;object-fit:cover;flex:none}
.hd a{border:0}
.hd h1,.hd .name{font-size:14px;font-weight:700;margin:0}
.t{color:var(--muted);margin:0}
h2.s{font-size:14px;font-weight:400;color:var(--muted);margin:0 0 8px}
h2.s::before{content:"// ";color:var(--brass)}
ul.posts{list-style:none;padding:0;margin:0 0 40px}
ul.posts li{display:flex;gap:20px;margin:0 0 6px}
ul.posts span{color:var(--muted);flex:none}
ul.posts a{align-self:flex-start;border:0;text-decoration:underline;text-decoration-color:var(--moss);text-decoration-thickness:1px;text-underline-offset:6px}
ul.posts a:hover{text-decoration-color:var(--brass)}
ul.proj li{display:block;margin:0 0 14px}
ul.proj span{display:block;font-size:13px;line-height:1.6}
h3.g{font:400 12px/1.4 var(--mono);color:var(--muted);margin:0 0 10px}
ul.proj{margin-bottom:26px}ul.proj.last{margin-bottom:40px}
.shelves{margin:0 0 40px}
h2.s .n{color:var(--muted);opacity:.7;margin-left:8px}
.jump{margin:0 0 8px;line-height:2.2}
.jump a{margin-right:16px;white-space:nowrap}
.shelves section{scroll-margin-top:24px}
h3.sec{font-size:14px;font-weight:700;color:var(--paper);margin:40px 0 6px}
h4.k{font-size:12px;font-weight:400;color:var(--muted);margin:16px 0 4px;letter-spacing:.04em}
ul.books{list-style:none;padding:0;margin:0}
ul.books li{margin:0 0 6px}
ul.books span{color:var(--muted)}
.l a{display:inline-block;margin-right:14px;padding:6px 2px;border:0;text-decoration:underline;text-decoration-color:var(--moss);text-underline-offset:5px;text-decoration-thickness:1px}
.l a:hover{text-decoration-color:var(--brass)}
.l{margin:-6px 0 0 -2px}
.gap{height:28px}
footer{margin-top:72px;color:var(--muted);font-size:12px}
/* essays */
article{margin-top:8px}
article h1.title{font:600 34px/1.2 var(--serif);margin:0 0 12px;color:var(--paper)}
article .sub{font:italic 20px/1.5 var(--serif);color:var(--muted);margin:0 0 14px}
article .meta{color:var(--muted);font-size:13px;margin:0 0 40px}
article .meta::before{content:"// ";color:var(--brass)}
.body{font:19px/1.75 var(--serif);color:var(--body)}
.body p{margin:0 0 1.25em}
.body h2,.body h3,.body h4{font-family:var(--serif);color:var(--paper);line-height:1.25;margin:1.9em 0 .6em}
.body h2{font-size:25px}.body h3{font-size:21px}.body h4{font-size:19px}
.body a{color:var(--paper);border-bottom:1px solid var(--brass)}
.body a:hover{color:var(--brass-lt)}
.body strong{color:var(--paper)}
.body img{max-width:100%;height:auto;display:block;margin:0 auto;border-radius:3px;filter:brightness(.92)}
.body figure{margin:32px 0}
.body figcaption{font:13px/1.5 var(--mono);color:var(--muted);text-align:center;margin-top:10px}
.body blockquote{margin:28px 0;padding-left:20px;border-left:2px solid var(--brass);color:var(--muted)}
.body hr{border:0;border-top:1px solid var(--ink-2);margin:40px 0}
.body pre,.body code{font-family:var(--mono);font-size:14px}
.body pre{overflow-x:auto;background:var(--ink-2);padding:16px;border-radius:4px}
.body table{display:block;overflow-x:auto}
.body ul,.body ol{padding-left:1.3em}
.body li{margin:.3em 0}
a.footnote-anchor{font:12px var(--mono);vertical-align:super;line-height:0;border:0;color:var(--brass-lt);padding:10px 4px;margin:-10px -2px}
.footnote{display:flex;gap:12px;font:13px/1.6 var(--mono);color:var(--muted);margin:6px 0;overflow-wrap:anywhere}
:not(.footnote)+.footnote{border-top:1px solid var(--ink-2);padding-top:28px;margin-top:48px}
.footnote p{margin:0}
.footnote a{color:var(--muted)}
a.footnote-number{border:0;color:var(--brass-lt);min-width:2em;padding:0 4px;margin:0 -4px}
.footnote,a.footnote-anchor{scroll-margin-top:30vh}
.footnote:target{background:var(--ink-2);border-radius:4px;outline:6px solid var(--ink-2)}
a.footnote-anchor:target{background:var(--rust);color:var(--paper);border-radius:3px}
.end{margin-top:48px;padding-top:20px;border-top:1px solid var(--ink-2);color:var(--muted);font-size:13px}
.back{margin:0 0 18px;font-size:13px}.back a{color:var(--muted);text-decoration:none;border-bottom:1px solid var(--moss)}
.contact{margin-top:14px}.contact summary{cursor:pointer;color:var(--muted);list-style:none;width:max-content;border-bottom:1px solid var(--moss)}
.contact summary::-webkit-details-marker{display:none}.contact[open] summary{color:var(--paper)}
.card{margin-top:10px;width:200px;height:200px;box-sizing:border-box;padding:18px;background:var(--ink-2);border:1px solid var(--moss);border-radius:4px;display:flex;flex-direction:column;gap:8px}
.card p{margin:0 0 6px;color:var(--muted)}.card a{color:var(--paper);text-decoration:none;border-bottom:1px solid var(--brass);width:max-content}
@media (max-width:520px){ul.posts li{flex-direction:column;gap:0;margin-bottom:12px}
article h1.title{font-size:28px}.body{font-size:18px}}
"""


def page(title, body, desc="", image="", path="", index=True):
    t = html.escape(title)
    d = html.escape(desc or SITE_TAGLINE)
    og_img = html.escape(image) if image else f"{SITE_URL}/og.png"
    stats = (f'<script data-goatcounter="https://{GOATCOUNTER}.goatcounter.com/count" '
             f'async src="https://gc.zgo.at/count.js"></script>' if GOATCOUNTER else "")
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
{f'<link rel="canonical" href="{SITE_URL}/{path}">' if index else '<meta name="robots" content="noindex">'}
<meta property="og:title" content="{t}"><meta property="og:description" content="{d}">
<meta property="og:url" content="{SITE_URL}/{path}"><meta property="og:image" content="{og_img}">
<meta property="og:site_name" content="{html.escape(SITE_TITLE)}"><meta property="og:type" content="{'article' if image else 'website'}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#262422">
<link rel="icon" href="/pfp.jpg">
<link rel="alternate" type="application/rss+xml" title="{html.escape(SITE_TITLE)}" href="{SUBSTACK}/feed">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="/style.css">
</head><body><div class="w">
{body}
</div>{stats}</body></html>
"""


def header(home):
    tag = "h1" if home else "div"
    back = '' if home else '<p class="back"><a href="/">← home</a></p>'
    return (back + f'<header class="hd"><a href="/"><img src="/pfp.jpg" alt="" width="44" height="44"></a>'
            f'<div><{tag} class="name"><a href="/">{SITE_TITLE.lower()}</a></{tag}>'
            f'<p class="t">{html.escape(SITE_TAGLINE)}</p></div></header>')


def build():
    posts = [json.loads(p.read_text(encoding="utf-8")) for p in CONTENT.glob("*.json")]
    posts.sort(key=lambda p: p["post_date"], reverse=True)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT / "style.css").write_text(CSS, encoding="utf-8")
    (OUT / ".nojekyll").write_text("")
    shutil.copy(ROOT / "pfp.jpg", OUT / "pfp.jpg")
    shutil.copy(ROOT / "og.png", OUT / "og.png")
    for f in ROOT.glob("google*.html"):  # Google Search Console verification
        shutil.copy(f, OUT / f.name)
    shutil.copytree(ROOT / "projects", OUT / "projects")

    items = []
    for p in posts:
        title, sub = html.escape(p["title"]), html.escape(p.get("subtitle") or "")
        month = p["post_date"][:7]
        mins = max(1, round((p.get("wordcount") or 0) / 230))
        items.append(f'<li><span>{month}</span><a href="/p/{p["slug"]}/">{title}</a></li>')
        body = (
            header(False)
            + f'<article><h1 class="title">{title}</h1>'
            + (f'<p class="sub">{sub}</p>' if sub else "")
            + f'<div class="meta">{fmt_date(p["post_date"]).lower()} · {mins} min read</div>'
            + f'<div class="body">{clean_body(p["body_html"] or "")}</div>'
            + f'<div class="end">also on <a href="{p["canonical_url"]}">substack</a>, '
            f'where you can <a href="{SUBSTACK}/subscribe">subscribe</a> by email. '
            f'<a href="/">← home</a></div></article>')
        d = OUT / "p" / p["slug"]
        d.mkdir(parents=True)
        (d / "index.html").write_text(page(f'{p["title"]} · {SITE_TITLE}', body, p.get("subtitle") or "",
                                           p.get("cover_image") or "", f"p/{p['slug']}/"), encoding="utf-8")

    def slug(name):
        return re.sub(r"[^a-z0-9]+", "-", name).strip("-")

    def shelf(items):
        return '<ul class="books">' + "".join(
            f'<li>{html.escape(t)}' + (f' <span>· {html.escape(a)}</span>' if a else "") + "</li>"
            for t, a in items) + "</ul>"

    jump = " ".join(f'<a href="#{slug(sec)}">{sec}</a>' for sec in READING)
    books = f'<nav class="jump">{jump}</nav>' + "".join(
        f'<section id="{slug(sec)}"><h3 class="sec">{sec}</h3>'
        + shelf(items) + "</section>"
        for sec, items in READING.items())
    projects = "".join(
        f'<h3 class="g">{html.escape(g)}</h3><ul class="posts proj{" last" if k == len(PROJECT_GROUPS) - 1 else ""}">'
        + "".join(f'<li><a href="/projects/{p}/">{html.escape(t)}</a><span>{html.escape(d)}</span></li>' for t, p, d in group)
        + "</ul>"
        for k, (g, group) in enumerate(PROJECT_GROUPS))
    links = "".join(f'<a href="{u}" rel="me noopener" target="_blank">{n}</a>' for n, u in LINKS)
    mail = f'<a href="mailto:{CONTACT_EMAIL}">email</a>' if CONTACT_EMAIL else ""
    contact = ('<details class="contact"><summary>contact</summary><div class="card"><p>say hi</p>'
               + "".join(f'<a href="{u}" rel="me noopener" target="_blank">{n}</a>'
                         for n, u in LINKS if n in ("x", "linkedin")) + mail + '</div></details>')
    home = (header(True)
            + f'<h2 class="s">writing</h2><ul class="posts">{"".join(items)}</ul>'
            + f'<h2 class="s">projects</h2>{projects}'
            + '<h2 class="s">reading</h2><p class="l"><a href="/reading/">suggested reading</a></p><div class="gap"></div>'
            + f'<h2 class="s">elsewhere</h2><p class="l">{links}</p>{contact}')
    (OUT / "index.html").write_text(page(SITE_TITLE, home), encoding="utf-8")

    (OUT / "reading").mkdir()
    (OUT / "reading" / "index.html").write_text(page(f"Suggested reading · {SITE_TITLE}",
        header(False) + f'<h2 class="s">suggested reading</h2><div class="shelves">{books}</div>'
        + '<p class="t"><a href="/">← home</a></p>', "Books I'd suggest.", path="reading/"), encoding="utf-8")

    (OUT / "404.html").write_text(page("Not found", header(False)
        + '<p class="t">nothing here. <a href="/">go home</a>.</p>', index=False), encoding="utf-8")

    # Sitemap and robots.txt so search engines find every page.
    urls = [("", None), ("reading/", None)]
    urls += [(f"p/{p['slug']}/", p["post_date"][:10]) for p in posts]
    urls += [(f"projects/{p}/", None) for _, p, _ in PROJECTS]
    entries = "".join(
        f"<url><loc>{SITE_URL}/{u}</loc>" + (f"<lastmod>{d}</lastmod>" if d else "") + "</url>"
        for u, d in urls)
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{entries}</urlset>\n',
        encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n",
                                    encoding="utf-8")
    print(f"Built {len(posts)} posts into {OUT}")


if __name__ == "__main__":
    if "--offline" not in sys.argv:
        try:
            fetch()
        except Exception as e:
            print(f"API fetch failed ({e}); trying RSS.")
            try:
                fetch_rss()
            except Exception as e:  # Substack down or blocking: use the cache
                print(f"RSS fetch failed ({e}); building from cache.")
    build()
