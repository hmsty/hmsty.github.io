# hmsty.github.io

Will's personal site, live at https://hmsty.github.io. Minimal and dark:
writing, projects, a suggested-reading page, and links elsewhere.

## Before every change

Run `git pull` first. The site is edited from more than one computer.

Commit as `hmsty <277348908+hmsty@users.noreply.github.com>`. Set it for this repo with
`git config user.name hmsty` and `git config user.email 277348908+hmsty@users.noreply.github.com`.
The history is public, so a real email or computer name in a commit is published.
The history was rewritten on 2026-10-03 to remove personal info. If a pull reports
diverged histories, don't merge or rebase: run `git fetch` and `git reset --hard origin/main`
so the old commits don't come back.

## How it works

- `build.py` generates everything into `site/`, which is not committed.
  - The settings block at the top holds the title, tagline, links, projects and analytics.
  - The CSS and HTML templates live in the same file.
- `content/*.json` stores posts mirrored from Substack (willjensen.substack.com).
- `reading.py` holds the suggested-reading list.
- `projects/<name>/index.html` holds standalone project pages, copied into the site as-is.
- `pfp.jpg` is the avatar. `og.png` is the link-preview card.
- `.github/workflows/build.yml` rebuilds and deploys on every push to `main`, and once a day.

Commands:

```bash
python3 build.py              # fetch new Substack posts, then build
python3 build.py --offline    # build from what's already in content/
python3 -m http.server 8765 --directory site   # preview at localhost:8765
```

To publish, commit and push to `main`. The site is live a minute or two after the
Action finishes. Check the live page after deploying.

## Substack sync

Substack blocks GitHub's servers and probably other cloud servers too, so the
daily Action can't fetch new posts. Running `python3 build.py` locally can. After
syncing, commit `content/` and push.

## Rules

- **Privacy comes first.** Never publish PII or sensitive details about Will or
  anyone else. That includes location and moves, schedules and routines, other
  people's usernames or names, and links that expose other people's accounts.
  Check projects and any other added HTML before publishing, including hidden
  text, aria labels, script data and outbound links. Flag any risk before
  publishing; don't fix it silently.
- **Reading list (`reading.py`):**
  - List only books Will has actually read. Ask him if you're unsure.
  - Sections are by subject, never by author. Every line is "Title · Author".
  - Don't show a book count. The page is titled "suggested reading".
  - The home page links to it under its own "reading" heading, not under "elsewhere".
- **Elsewhere** is for other places to find Will. The links run x, substack,
  linkedin, in that order, and open in a new tab.
- **Projects:** on the home page, use a descriptive link name with a one-line
  description underneath. Leave the content of a project page as Will made it;
  only add the small "← will jensen" back link.
- **Design:** keep it minimal and use the existing palette. Don't add sections or
  ornament without asking.
  - Background: warm graphite `#262422`.
  - Text: paper `#EDE6D6`. Muted text: `#a9a295`.
  - Accents: moss `#5C6B47`, brass `#96721F`, rust `#9C4A2E`.
  - Moss, brass and rust are too dark to use as text on the background; keep
    them for underlines, rules and highlights.
  - Monospace (JetBrains Mono) for the site, serif (Source Serif 4) for essay text.
- **Tagline** is "mostly markets stuff", lowercase, with no period.
