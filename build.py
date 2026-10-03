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

# ---- settings ---------------------------------------------------------------
SUBSTACK = "https://willjensen.substack.com"
SITE_TITLE = "Will Jensen"
SITE_TAGLINE = "Writing on crypto, finance, and money as technology."
SITE_URL = "https://hmsty.github.io"
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
            path.write_text(json.dumps(keep, indent=1))
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
            "canonical_url": link, "wordcount": words}, indent=1))


def clean_body(body):
    # Drop Substack's image toolbar buttons and icons.
    body = re.sub(r"<button\b.*?</button>", "", body, flags=re.S)
    body = re.sub(r"<svg\b.*?</svg>", "", body, flags=re.S)
    body = re.sub(r'\sdata-attrs="[^"]*"', "", body)
    # Subscribe widgets and share buttons belong to Substack.
    body = re.sub(r'<p class="button-wrapper".*?</p>', "", body, flags=re.S)
    body = re.sub(r'<div class="subscription-widget-wrap.*?</form></div></div>', "", body, flags=re.S)
    # Make bare URLs in footnotes clickable.
    def linkify(m):
        url = m.group(1)
        return f'<p><a href="{url}">{url}</a></p>'
    body = re.sub(r"<p>(https?://[^\s<]+)</p>", linkify, body)
    return body


def fmt_date(iso):
    d = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return d.strftime("%B %-d, %Y")


CSS = """
:root{--bg:#fbfaf7;--fg:#1d1c1a;--muted:#6b675f;--rule:#e4e0d8;--accent:#9a3b1b}
@media (prefers-color-scheme:dark){:root{--bg:#161513;--fg:#e9e6df;--muted:#9a958b;--rule:#2d2b27;--accent:#e08a5f}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:19px/1.65 "Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif}
.wrap{max-width:680px;margin:0 auto;padding:0 20px}
header.top{padding:40px 0 12px;display:flex;justify-content:space-between;align-items:baseline;gap:16px;flex-wrap:wrap}
header.top a.name{font-weight:700;font-size:21px;color:var(--fg);text-decoration:none}
nav a{font:15px/1 -apple-system,system-ui,sans-serif;color:var(--muted);text-decoration:none;margin-left:18px}
nav a:hover{color:var(--fg)}
a{color:var(--accent)}
.intro{color:var(--muted);margin:24px 0 40px;font-style:italic}
ul.posts{list-style:none;padding:0;margin:0}
ul.posts li{padding:22px 0;border-top:1px solid var(--rule)}
ul.posts a{color:var(--fg);text-decoration:none;font-size:23px;font-weight:600;line-height:1.3}
ul.posts a:hover{color:var(--accent)}
.meta{font:14px/1.4 -apple-system,system-ui,sans-serif;color:var(--muted);margin-top:6px}
.sub{color:var(--muted);margin:6px 0 0;font-size:17px;line-height:1.5}
article h1.title{font-size:38px;line-height:1.15;margin:40px 0 12px}
article .sub{font-size:20px}
article .meta{margin:16px 0 36px}
article h1,article h2,article h3{line-height:1.25;margin:1.8em 0 .5em}
article h1{font-size:28px}article h2{font-size:25px}article h3{font-size:21px}
article img{max-width:100%;height:auto;display:block;margin:0 auto}
article figure{margin:28px 0}
article figcaption{font-size:15px;color:var(--muted);text-align:center;margin-top:8px}
article blockquote{margin:24px 0;padding-left:20px;border-left:3px solid var(--rule);color:var(--muted)}
article pre,article code{font-size:15px}
article pre{overflow-x:auto}
article table{display:block;overflow-x:auto}
a.footnote-anchor{font-size:13px;vertical-align:super;line-height:0;text-decoration:none;padding:0 2px}
.footnote{display:flex;gap:10px;font-size:15px;line-height:1.5;color:var(--muted);margin:6px 0;overflow-wrap:anywhere}
.footnote:first-of-type{border-top:1px solid var(--rule);padding-top:24px;margin-top:40px}
.footnote p{margin:0}
.footnote-number{text-decoration:none;min-width:1.4em}
.substack{margin:48px 0 0;padding:20px;border:1px solid var(--rule);border-radius:8px;font:15px/1.5 -apple-system,system-ui,sans-serif;color:var(--muted)}
footer{margin:64px 0 40px;padding-top:20px;border-top:1px solid var(--rule);font:14px/1.5 -apple-system,system-ui,sans-serif;color:var(--muted)}
footer a{color:var(--muted)}
@media (max-width:520px){body{font-size:18px}article h1.title{font-size:30px}nav a{margin:0 18px 0 0}}
"""


def page(title, body, desc="", image="", path=""):
    t = html.escape(title)
    d = html.escape(desc or SITE_TAGLINE)
    og_img = f'<meta property="og:image" content="{html.escape(image)}">' if image else ""
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
<meta property="og:title" content="{t}"><meta property="og:description" content="{d}">
<meta property="og:url" content="{SITE_URL}/{path}">{og_img}
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="{html.escape(SITE_TITLE)}" href="{SUBSTACK}/feed">
<link rel="stylesheet" href="/style.css">
</head><body><div class="wrap">
<header class="top"><a class="name" href="/">{html.escape(SITE_TITLE)}</a>
<nav><a href="/">Writing</a><a href="/about/">About</a><a href="{SUBSTACK}/subscribe">Subscribe</a></nav></header>
{body}
<footer>© {datetime.now().year} {html.escape(SITE_TITLE)} · Get new posts by email on <a href="{SUBSTACK}">Substack</a></footer>
</div></body></html>
"""


def build():
    posts = [json.loads(p.read_text()) for p in CONTENT.glob("*.json")]
    posts.sort(key=lambda p: p["post_date"], reverse=True)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT / "style.css").write_text(CSS)
    (OUT / ".nojekyll").write_text("")

    items = []
    for p in posts:
        title, sub = html.escape(p["title"]), html.escape(p.get("subtitle") or "")
        date = fmt_date(p["post_date"])
        mins = max(1, round((p.get("wordcount") or 0) / 230))
        items.append(
            f'<li><a href="/p/{p["slug"]}/">{title}</a>'
            f'<div class="meta">{date} · {mins} min read</div>'
            + (f'<p class="sub">{sub}</p>' if sub else "") + "</li>")
        body = (
            f'<article><h1 class="title">{title}</h1>'
            + (f'<p class="sub">{sub}</p>' if sub else "")
            + f'<div class="meta">{date} · {mins} min read</div>'
            + clean_body(p["body_html"] or "")
            + f'<div class="substack">Originally published on <a href="{p["canonical_url"]}">Substack</a>. '
            f'<a href="{SUBSTACK}/subscribe">Subscribe</a> to get new posts by email.</div></article>')
        d = OUT / "p" / p["slug"]
        d.mkdir(parents=True)
        (d / "index.html").write_text(page(p["title"], body, p.get("subtitle") or "",
                                           p.get("cover_image") or "", f"p/{p['slug']}/"))

    home = f'<p class="intro">{html.escape(SITE_TAGLINE)}</p><ul class="posts">{"".join(items)}</ul>'
    (OUT / "index.html").write_text(page(SITE_TITLE, home))

    about_src = ROOT / "about.html"
    about = about_src.read_text() if about_src.exists() else "<p>About me.</p>"
    (OUT / "about").mkdir()
    (OUT / "about" / "index.html").write_text(
        page(f"About · {SITE_TITLE}", f'<article><h1 class="title">About</h1>{about}</article>', path="about/"))

    (OUT / "404.html").write_text(page("Not found", '<p class="intro">That page doesn\'t exist. <a href="/">Go home</a>.</p>'))
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
