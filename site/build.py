#!/usr/bin/env python3
"""build.py - generate the Faleni website from lexicon.csv + the markdown docs.

Output goes to site/dist/. Uses the `markdown` package if installed (nicer), and
falls back to a built-in converter otherwise, so it always builds.

    python3 site/build.py        # then open site/dist/index.html
"""
import csv
import hashlib
import html
import json
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIST = os.path.join(HERE, "dist")
ASSETS = os.path.join(HERE, "assets")
TEMPLATES = os.path.join(HERE, "templates")

# Set this to your GitHub repo to wire up the "propose a word" button + CI links.
# Override without editing the file via:  FALENI_REPO_URL=https://github.com/me/repo
REPO_URL = os.environ.get("FALENI_REPO_URL", "https://github.com/jfoval/faleni")
REPO_SET = "your-username" not in REPO_URL          # False while it's the placeholder

# Onset -> readable family label + an accent color for the home grid.
FAMILY_INFO = [
    ("p", "people", "People & body", "#c2410c", "pa person, pama mother"),
    ("m", "mind", "Mind & feeling", "#7c3aed", "me want, masu happy"),
    ("s", "nature", "Nature", "#0e7c66", "sa water, sena moon"),
    ("t", "thing", "Things & places", "#b45309", "tu house, tuna city"),
    ("k", "action", "Actions", "#2563eb", "ka go, kema eat"),
    ("l", "quality", "Qualities & color", "#be123c", "la good, lasa red"),
    ("f", "speech", "Speech & info", "#0891b2", "fa speak, fila book"),
    ("n", "time", "Number, time & space", "#4d7c0f", "no time, niwi in"),
    ("V", "logic", "Logic & connectives", "#6b7280", "a all, isa if"),
]
DOMAIN_LABEL = {
    "people": "people & body", "mind": "mind", "nature": "nature",
    "thing": "things & places", "action": "actions", "quality": "qualities",
    "color": "color", "speech": "speech & info", "time": "number/time/space",
    "logic": "logic", "grammar": "grammar", "pronoun": "pronoun",
    "number": "numeral", "proper": "name",
}
DOMAIN_ORDER = ["people", "mind", "nature", "thing", "action", "quality", "color",
                "speech", "time", "logic", "grammar", "pronoun", "number", "proper"]

NAV = [("Home", "index.html", "home"), ("Learn", "learn.html", "learn"),
       ("Sounds", "pronounce.html", "sounds"),
       ("Dictionary", "dictionary.html", "dict"), ("Grammar", "spec.html", "grammar"),
       ("Contribute", "contribute.html", "contribute")]

# rewrite in-repo doc links to their generated pages
LINK_MAP = {
    "spec.md": "spec.html", "grammar-extras.md": "extras.html", "coinage.md": "coinage.html",
    "compounds.md": "compounds.html", "readme.md": "index.html", "lexicon.csv": "dictionary.html",
    "lesson-1.md": "lesson-1.html", "lesson-2.md": "lesson-2.html", "lesson-3.md": "lesson-3.html",
    "faleni.py": "contribute.html", "contributing.md": "contribute.html",
}


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------- markdown ---
# Lines that are passed through as raw HTML (allowlist of real block tags, so a
# paragraph that merely starts with "<" is escaped instead of injected).
_RAW_HTML = re.compile(
    r"^</?(details|summary|div|section|aside|table|thead|tbody|tr|td|th|"
    r"ul|ol|li|pre|blockquote|p|h[1-6]|hr|br|img|figure|figcaption)\b", re.I)
_SAFE_SCHEMES = ("http:", "https:", "mailto:")
# Friendly labels for in-doc links whose visible text is a raw source filename.
_FRIENDLY = {
    "SPEC.md": "the grammar", "GRAMMAR-EXTRAS.md": "Numbers &amp; extras",
    "COINAGE.md": "Coining words", "compounds.md": "the compounds page",
    "lexicon.csv": "the dictionary", "README.md": "the overview",
    "CONTRIBUTING.md": "Contributing", "lesson-1.md": "Lesson 1",
    "lesson-2.md": "Lesson 2", "lesson-3.md": "Lesson 3",
}


def _safe_href(url):
    u = (url or "").strip()
    low = u.lower()
    if low.startswith(_SAFE_SCHEMES) or u.startswith(("#", "/")) or ":" not in u.split("/")[0]:
        return u
    return "#"                                     # drop javascript:/data:/etc.


def _emph(t):
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    return re.sub(r"(?<!\*)\*(?!\s)([^*]+?)\*(?!\*)", r"<em>\1</em>", t)


def _inline(s):
    codes, links = [], []

    def code_sub(m):
        codes.append("<code>" + html.escape(m.group(1)) + "</code>")
        return "\x00C%d\x00" % (len(codes) - 1)

    def link_sub(m):
        links.append((m.group(1), m.group(2)))
        return "\x00L%d\x00" % (len(links) - 1)

    s = re.sub(r"`([^`]+)`", code_sub, s)
    s = re.sub(r"\[([^\]]+)\]\(((?:[^()]|\([^()]*\))+)\)", link_sub, s)   # allow one balanced ()
    s = html.escape(s)
    s = _emph(s)

    def restore_link(m):
        text, url = links[int(m.group(1))]
        return '<a href="%s">%s</a>' % (html.escape(_safe_href(url)), _emph(html.escape(text)))

    s = re.sub(r"\x00L(\d+)\x00", restore_link, s)
    s = re.sub(r"\x00C(\d+)\x00", lambda m: codes[int(m.group(1))], s)
    return s


def _is_table_sep(l):
    return bool(re.match(r"^\s*\|?[\s:\-\|]+\|?\s*$", l)) and "-" in l


def _starts_block(l):
    s = l.lstrip()
    return bool(s.startswith("#") or s.startswith(">") or s.startswith("```")
                or _RAW_HTML.match(s) or re.match(r"^\s*(?:[-*]|\d+\.)\s+", l)
                or re.match(r"^\s*---+\s*$", l) or ("|" in l))


def _is_real_block(lines, i):
    """Context-aware block check for list continuation: a line with a literal '|'
    is only a table when the NEXT line is a separator, so prose containing pipes
    is absorbed as a continuation rather than fragmenting the list item."""
    l = lines[i]
    s = l.lstrip()
    if (s.startswith("#") or s.startswith(">") or s.startswith("```")
            or _RAW_HTML.match(s) or re.match(r"^\s*---+\s*$", l)):
        return True
    return "|" in l and i + 1 < len(lines) and _is_table_sep(lines[i + 1])


def _cells(l):
    l = l.strip()
    if l.startswith("|"):
        l = l[1:]
    if l.endswith("|"):
        l = l[:-1]
    return [c.strip() for c in l.split("|")]


def _parse_list(lines, i, base_indent):
    """Parse one list starting at line i, absorbing continuation lines and
    nesting deeper-indented sub-lists. Returns (html, next_index)."""
    n = len(lines)
    ordered = bool(re.match(r"^\s*\d+\.\s+", lines[i]))
    items = []
    while i < n:
        m = re.match(r"^(\s*)(?:[-*]|\d+\.)\s+(.*)$", lines[i])
        if not m or len(m.group(1)) != base_indent:
            break
        parts, child = [m.group(2)], ""
        i += 1
        while i < n:
            l = lines[i]
            if not l.strip():                       # blank: stay in the list only if a sibling/child follows
                j = i
                while j < n and not lines[j].strip():
                    j += 1
                nxt = re.match(r"^(\s*)(?:[-*]|\d+\.)\s+", lines[j]) if j < n else None
                if nxt and len(nxt.group(1)) >= base_indent:
                    i = j
                break
            nxt = re.match(r"^(\s*)(?:[-*]|\d+\.)\s+", l)
            if nxt:
                ci = len(nxt.group(1))
                if ci > base_indent:                # deeper -> nested list
                    sub, i = _parse_list(lines, i, ci)
                    child += sub
                    continue
                break                               # sibling or shallower -> outer loop
            if _is_real_block(lines, i):
                break
            parts.append(l.strip())                 # lazy continuation line
            i += 1
        items.append((" ".join(parts), child))
    tag = "ol" if ordered else "ul"
    body = "".join("<li>%s%s</li>" % (_inline(t), c) for t, c in items)
    return "<%s>%s</%s>" % (tag, body, tag), i


def _basic_md(text):
    lines = text.split("\n")
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if _RAW_HTML.match(line.lstrip()):
            out.append(line)
            i += 1
            continue
        if re.match(r"^```", line.strip()):
            i += 1
            buf = []
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            out.append("<pre><code>" + html.escape("\n".join(buf)) + "</code></pre>")
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            lv, txt = len(m.group(1)), m.group(2).strip()
            slug = re.sub(r"[^a-z0-9]+", "-", txt.lower()).strip("-")
            out.append('<h%d id="%s">%s</h%d>' % (lv, slug, _inline(txt), lv))
            i += 1
            continue
        if re.match(r"^\s*---+\s*$", line):
            out.append("<hr>")
            i += 1
            continue
        if "|" in line and i + 1 < n and _is_table_sep(lines[i + 1]):
            header = line
            i += 2
            body = []
            while i < n and "|" in lines[i] and lines[i].strip():
                body.append(lines[i])
                i += 1
            th = "".join("<th>%s</th>" % _inline(c) for c in _cells(header))
            trs = "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % _inline(c) for c in _cells(r)) for r in body)
            out.append("<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (th, trs))
            continue
        if line.lstrip().startswith(">"):
            buf = []
            while i < n and lines[i].lstrip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append("<blockquote>%s</blockquote>" % "<br>".join(_inline(b) for b in buf))
            continue
        if re.match(r"^\s*(?:[-*]|\d+\.)\s+", line):
            indent = len(re.match(r"^(\s*)", line).group(1))
            block, i = _parse_list(lines, i, indent)
            out.append(block)
            continue
        buf = []
        while i < n and lines[i].strip() and not _starts_block(lines[i]):
            buf.append(lines[i])
            i += 1
        if not buf:                       # safety: never loop forever
            buf.append(lines[i])
            i += 1
        out.append("<p>%s</p>" % _inline(" ".join(buf)))
    return "\n".join(out)


def _rewrite_links(s):
    def sub(m):
        url = m.group(1)
        if url.startswith(("http", "#", "mailto")):
            return 'href="%s"' % url
        path = url.split("#")[0]
        anchor = ("#" + url.split("#")[1]) if "#" in url else ""
        base = os.path.basename(path).lower()
        if base in LINK_MAP:
            return 'href="%s%s"' % (LINK_MAP[base], anchor)
        return 'href="%s"' % _safe_href(url)
    return re.sub(r'href="([^"]+)"', sub, s)


def _friendly_link_text(s):
    names = "|".join(re.escape(k) for k in _FRIENDLY)
    return re.sub(r">(?:[^<>]*/)?(" + names + r")</a>",
                  lambda m: ">" + _FRIENDLY[m.group(1)] + "</a>", s)


def md_to_html(text):
    try:
        import markdown
        body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
    except Exception:
        body = _basic_md(text)
    return _friendly_link_text(_rewrite_links(body))


# ------------------------------------------------------------------ pages ---
def nav_html(active, current_href):
    out = []
    for label, href, key in NAV:
        # is-active highlights the section; aria-current only when this IS the page
        cls = "nav-link is-active" if key == active else "nav-link"
        cur = ' aria-current="page"' if href == current_href else ""
        out.append('<a class="%s"%s href="%s">%s</a>' % (cls, cur, href, label))
    return "".join(out)


_VER = {}


def asset_version():
    """Short content hash of the CSS+JS, used to cache-bust asset URLs."""
    if "v" not in _VER:
        h = hashlib.sha1()
        for fn in ("style.css", "app.js"):
            with open(os.path.join(ASSETS, fn), "rb") as f:
                h.update(f.read())
        _VER["v"] = h.hexdigest()[:8]
    return _VER["v"]


def page(title, desc, content, active, count, current_href):
    base = read(os.path.join(TEMPLATES, "base.html"))
    return (base.replace("{{TITLE}}", html.escape(title))
                .replace("{{DESC}}", html.escape(desc))
                .replace("{{NAV}}", nav_html(active, current_href))
                .replace("{{CONTENT}}", content)
                .replace("{{COUNT}}", str(count))
                .replace("{{VER}}", asset_version()))


def doc_page(md_filename):
    return '<article class="prose">%s</article>' % md_to_html(read(os.path.join(ROOT, md_filename)))


def write(name, contents):
    with open(os.path.join(DIST, name), "w", encoding="utf-8") as f:
        f.write(contents)


def load_lexicon():
    with open(os.path.join(ROOT, "lexicon.csv"), newline="", encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if (r.get("word") or "").strip()]


def build_index(rows, count):
    fam_cards = "".join(
        '<div class="fam-card" style="--fam:%s"><div class="onset">%s</div>'
        '<div class="dom">%s</div><div class="ex">%s</div></div>'
        % (color, "V" if onset == "V" else onset + "-", label, html.escape(ex))
        for onset, _key, label, color, ex in FAMILY_INFO)
    samples = [
        ("wa ha mu we", "I love you."),
        ("we ha me kema jeta?", "What do you want to eat?"),
        ("tu wa ha le nelo ame tu we", "My house is bigger than yours."),
        ("neka, wa jo ha ka nosa ti famu", "Tomorrow, we go to school."),
    ]
    sample_html = "".join(
        '<div class="sample"><span class="fa">%s</span><span class="en">%s</span></div>'
        % (html.escape(fa), html.escape(en)) for fa, en in samples)
    return """
<section class="hero">
  <h1>Faleni</h1>
  <p class="tagline">A language built to be the easiest to learn and the clearest
  to speak &mdash; with one rule for inventing a word for anything.</p>
  <div class="cta">
    <a class="btn btn-primary" href="learn.html">Start Lesson 1</a>
    <a class="btn btn-ghost" href="dictionary.html">Browse %d words</a>
  </div>
</section>

<section class="section">
  <h2>Say something now</h2>
  <div class="samples">%s</div>
</section>

<section class="section">
  <h2>The whole idea: the first sound tells the meaning</h2>
  <p class="lead">Every content word's onset marks its domain. You never think about
  it while speaking &mdash; but it makes the vocabulary coherent and tells you how to
  coin new words.</p>
  <div class="family-grid">%s</div>
</section>

<section class="section">
  <h2>Why it's different</h2>
  <ul>
    <li><strong>~10 rules, zero exceptions.</strong> No irregular verbs, no genders,
      no cases. Words never change shape.</li>
    <li><strong>Fully original.</strong> Every root is invented &mdash; nothing borrowed
      from any language.</li>
    <li><strong>It composes.</strong> %d roots + compounds express thousands of ideas:
      <span class="fa">teku fa</span> (tool-speak) = phone.</li>
    <li><strong>One source of truth.</strong> This whole site is generated from
      <a href="dictionary.html"><code>lexicon.csv</code></a>; it can never drift.</li>
  </ul>
  <div class="cta"><a class="btn btn-ghost" href="spec.html">Read the grammar</a>
  <a class="btn btn-ghost" href="contribute.html">Add a word</a></div>
</section>
""" % (count, sample_html, fam_cards, count)


def build_learn():
    lessons = [
        ("lesson-1.html", "Lesson 1 — Your first words",
         "Sounds, &ldquo;I am&hellip;&rdquo;, saying no, yes/no questions, greetings, your name."),
        ("lesson-2.html", "Lesson 2 — Doing things",
         "Verbs, objects, open questions, plurals, possession, counting."),
        ("lesson-3.html", "Lesson 3 — Describing your world",
         "Adjectives, adverbs, time, space, comparison, and building new words."),
    ]
    cards = "".join(
        '<div class="card"><h2><a href="%s">%s</a></h2><p class="muted">%s</p></div>'
        % (href, title, desc) for href, title, desc in lessons)
    return """
<section class="hero" style="padding-bottom:8px">
  <h1>Learn Faleni</h1>
  <p class="tagline">Three short lessons. By the end you can hold a simple
  conversation. Each has practice with answers.</p>
  <p><a class="btn btn-ghost" href="pronounce.html">&#128266; First, hear the sounds</a></p>
</section>
<section class="section">%s
  <p>After the lessons: keep a <a href="compounds.html">compound cheat-sheet</a> handy,
  browse the <a href="dictionary.html">dictionary</a>, and read the full
  <a href="spec.html">grammar</a> when you want the details.</p>
</section>
""" % cards


def build_dictionary(rows, count):
    present = [d for d in DOMAIN_ORDER if any(r.get("domain") == d for r in rows)]
    chips = ['<button class="family-chip is-active" data-family="all">All</button>']
    for d in present:
        c = sum(1 for r in rows if r.get("domain") == d)
        chips.append('<button class="family-chip" data-family="%s">%s <span class="muted">%d</span></button>'
                     % (d, html.escape(DOMAIN_LABEL.get(d, d)), c))
    body = []
    for r in rows:
        word = r.get("word", "")
        gloss = r.get("gloss", "")
        dom = r.get("domain", "")
        decomp = r.get("decomp", "")
        search = html.escape((word + " " + gloss).lower(), quote=True)
        wesc = html.escape(word)
        body.append(
            '<tr class="dict-row" data-family="%s" data-search="%s">'
            '<td class="fa">%s <button class="say-btn" data-say="%s" '
            'aria-label="Hear %s" title="Hear it">&#128266;</button></td><td>%s</td>'
            '<td><span class="badge">%s</span></td><td class="decomp">%s</td></tr>'
            % (html.escape(dom, quote=True), search, wesc,
               html.escape(word, quote=True), wesc,
               html.escape(gloss), html.escape(DOMAIN_LABEL.get(dom, dom)),
               html.escape(decomp)))
    return """
<div class="dict-tools">
  <h1 style="font-family:var(--serif);margin:.2em 0">Dictionary</h1>
  <input id="dict-search" class="dict-search" type="search" placeholder="Search a word or meaning&hellip;" autocomplete="off" aria-label="Search the dictionary">
  <div class="chips">%s</div>
  <div class="dict-count" id="dict-count">%d entries</div>
</div>
<table class="dict">
  <thead><tr><th>Word</th><th>Meaning</th><th>Family</th><th>Built from</th></tr></thead>
  <tbody>%s</tbody>
</table>
<div class="dict-empty" id="dict-empty">No words match. Try fewer letters, or
<a href="contribute.html">propose it</a>.</div>
""" % ("".join(chips), count, "".join(body))


def build_contribute():
    legend = "".join(
        '<tr><td class="fa">%s</td><td>%s</td><td class="muted">%s</td></tr>'
        % ("V-" if o == "V" else o + "-", label, html.escape(ex))
        for o, _k, label, _c, ex in FAMILY_INFO)
    fam_options = "".join('<option value="%s">%s</option>' % (key, label)
                          for _o, key, label, _c, _e in FAMILY_INFO)
    repo_attr = REPO_URL if REPO_SET else ""
    if REPO_SET:
        btn = ('<a id="propose-link" class="btn btn-primary" href="%s/issues/new" '
               'target="_blank" rel="noopener">Open a proposal issue</a>' % REPO_URL)
        note = ""
    else:
        btn = ('<a id="propose-link" class="btn btn-primary is-disabled" aria-disabled="true" '
               'title="Maintainer: set the repo to enable this">Open a proposal issue</a>')
        note = ('<p class="muted" style="margin-top:8px">Maintainer: set <code>REPO_URL</code> in '
                '<code>site/build.py</code> (or the <code>FALENI_REPO_URL</code> env var) and rebuild '
                'to enable this button.</p>')
    return """
<section class="hero" style="padding-bottom:8px">
  <h1>Add a word</h1>
  <p class="tagline">Faleni grows by proposal, not free edit &mdash; that's what keeps
  it regular and original.</p>
</section>

<section class="section">
  <h2>How it works</h2>
  <ol class="steps">
    <li><strong>Build before you invent.</strong> Most things are a compound of
      existing words &mdash; check <a href="compounds.html">compounds</a> and the
      <a href="dictionary.html">dictionary</a> first.</li>
    <li><strong>Coin into the right family.</strong> A new word's first sound marks its
      domain (table below).</li>
    <li><strong>Validate.</strong> Run <code>python3 tools/faleni.py check &lt;word&gt;</code>
      &mdash; it confirms the word is legal, unclaimed, and not a near-homophone.</li>
    <li><strong>Propose.</strong> Open a pre-filled <strong>issue</strong> from the form
      below (quickest), or open a <strong>pull request</strong> adding the line to
      <code>lexicon.csv</code> &mdash; PRs run the validator in CI automatically, and a
      maintainer reviews and merges.</li>
  </ol>
</section>

<section class="section">
  <h2>Draft a proposal</h2>
  <div class="card">
    <form id="propose-form" data-repo="%s">
      <div class="field"><label for="p-word">Word (e.g. <code>siso</code>)</label>
        <input id="p-word" type="text" placeholder="lowercase, (C)V syllables"></div>
      <div class="field"><label for="p-gloss">Meaning</label>
        <input id="p-gloss" type="text" placeholder="snow"></div>
      <div class="field"><label for="p-family">Family (sets the onset)</label>
        <select id="p-family">%s</select></div>
      <p class="muted">Your <code>lexicon.csv</code> line:</p>
      <div class="out" id="propose-out"></div>
      <p style="margin-top:14px">%s</p>%s
    </form>
  </div>
</section>

<section class="section">
  <h2>Onset &rarr; family</h2>
  <table class="dict"><thead><tr><th>Starts with</th><th>Domain</th><th>Examples</th></tr></thead>
  <tbody>%s</tbody></table>
  <p>Full rules in <a href="coinage.html">Coining words</a>.</p>
</section>
""" % (repo_attr, fam_options, btn, note, legend)


def build_pronounce():
    vowels = [
        ("a", "/a/", "father", "wa", "I / me"),
        ("e", "/e/", "bet (a bit tenser)", "we", "you"),
        ("i", "/i/", "machine", "wi", "he / she / they"),
        ("o", "/o/", "go", "wo", "this / here"),
        ("u", "/u/", "flute", "wu", "that / there"),
    ]
    cons = [
        ("p", "/p/", "spin", "pa", "person"), ("t", "/t/", "stop", "te", "thing"),
        ("k", "/k/", "skip", "ka", "go"), ("f", "/f/", "fun", "fa", "speak"),
        ("s", "/s/", "sun", "sa", "water"), ("h", "/h/", "hat", "ha", "is / does"),
        ("m", "/m/", "man", "ma", "know"), ("n", "/n/", "no", "no", "time"),
        ("l", "/l/", "love", "la", "good"), ("w", "/w/", "water", "wa", "I"),
        ("j", "/j/", "yes  (the y-sound!)", "ju", "you"),
    ]

    def rows(data):
        return "".join(
            '<tr><td class="fa">%s</td><td class="ipa">%s</td><td>as in <em>%s</em></td>'
            '<td><span class="fa">%s</span> &middot; %s '
            '<button class="say-btn" data-say="%s" aria-label="Hear %s" title="Hear it">&#128266;</button></td></tr>'
            % (letter, html.escape(ipa), html.escape(kw), ex, html.escape(gloss),
               html.escape(ex, quote=True), html.escape(ex))
            for letter, ipa, kw, ex, gloss in data)

    samples = [
        ("faleni", "the name: FA-le-ni"),
        ("wa ha mu we", "I love you"),
        ("la nami", "good morning"),
        ("we ha me kema jeta", "what do you want to eat?"),
    ]
    sample_rows = "".join(
        '<li><span class="fa">%s</span> <button class="say-btn" data-say="%s" '
        'aria-label="Hear it" title="Hear it">&#128266;</button> &mdash; %s</li>'
        % (html.escape(fa), html.escape(fa, quote=True), html.escape(en))
        for fa, en in samples)

    return """
<section class="hero" style="padding-bottom:8px">
  <h1>How Faleni sounds</h1>
  <p class="tagline">16 sounds, each said exactly one way. Learn them once and you
  can pronounce every word.</p>
</section>

<section class="section">
  <p class="lead">Three rules cover all of pronunciation:</p>
  <ul>
    <li><strong>One letter, one sound</strong> &mdash; always. No silent letters, no exceptions.</li>
    <li><strong>Stress the first syllable</strong> of every word (<span class="fa">FA</span>-le-ni).</li>
    <li><strong><span class="fa">j</span> = English &ldquo;y&rdquo;</strong> &mdash; the one thing to remember
      (<span class="fa">ju</span> = &ldquo;you&rdquo;).</li>
  </ul>
  <p class="speech-note muted">&#128266; buttons read the word with your browser's speech
  engine &mdash; a close approximation. The IPA and English keyword are the exact target.</p>
</section>

<section class="section">
  <h2>The 5 vowels</h2>
  <p>Pure vowels, like Spanish or Japanese &mdash; never gliding. (The examples are the
  pronouns, which differ only by their vowel.)</p>
  <table class="dict sound-table"><thead><tr><th>Letter</th><th>Sound</th><th>Like</th><th>Example</th></tr></thead>
  <tbody>%s</tbody></table>
</section>

<section class="section">
  <h2>The 11 consonants</h2>
  <table class="dict sound-table"><thead><tr><th>Letter</th><th>Sound</th><th>Like</th><th>Example</th></tr></thead>
  <tbody>%s</tbody></table>
  <p class="muted">Voicing doesn't change meaning, so a softer <em>b / d / g / v / z</em> for
  <span class="fa">p / t / k / f / s</span> is still understood &mdash; say what's comfortable.</p>
</section>

<section class="section">
  <h2>Hear whole phrases</h2>
  <ul>%s</ul>
  <p>Every word in the <a href="dictionary.html">dictionary</a> has a &#128266; button too.</p>
</section>
""" % (rows(vowels), rows(cons), sample_rows)


def main():
    rows = load_lexicon()
    count = len(rows)

    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(os.path.join(DIST, "assets"))
    os.makedirs(os.path.join(DIST, "data"))
    for fn in os.listdir(ASSETS):
        shutil.copy(os.path.join(ASSETS, fn), os.path.join(DIST, "assets", fn))

    with open(os.path.join(DIST, "data", "lexicon.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=0)

    pages = [
        ("index.html", "Faleni — the easy tongue",
         "An efficient, fully original constructed language with a systematic word engine.",
         build_index(rows, count), "home"),
        ("learn.html", "Learn Faleni", "Three lessons to start speaking Faleni.",
         build_learn(), "learn"),
        ("pronounce.html", "Faleni pronunciation",
         "Hear how Faleni sounds — the 16 sounds, each with audio and an English keyword.",
         build_pronounce(), "sounds"),
        ("dictionary.html", "Faleni dictionary",
         "Search every Faleni word, filterable by meaning-family.",
         build_dictionary(rows, count), "dict"),
        ("spec.html", "Faleni grammar", "The full Faleni specification.",
         doc_page("SPEC.md"), "grammar"),
        ("extras.html", "Faleni numbers & extras",
         "Decimals, dates, clock, comparison and more.", doc_page("GRAMMAR-EXTRAS.md"), "grammar"),
        ("coinage.html", "Coining Faleni words", "How to add new words to Faleni.",
         doc_page("COINAGE.md"), "contribute"),
        ("compounds.html", "Faleni compounds", "~100 ready-made compounds and the pattern.",
         doc_page("compounds.md"), "learn"),
        ("lesson-1.html", "Faleni Lesson 1", "Your first Faleni words.",
         doc_page(os.path.join("lessons", "lesson-1.md")), "learn"),
        ("lesson-2.html", "Faleni Lesson 2", "Verbs, objects and questions.",
         doc_page(os.path.join("lessons", "lesson-2.md")), "learn"),
        ("lesson-3.html", "Faleni Lesson 3", "Describing your world.",
         doc_page(os.path.join("lessons", "lesson-3.md")), "learn"),
        ("contribute.html", "Contribute to Faleni",
         "Propose a new word; the validator and a maintainer keep it clean.",
         build_contribute(), "contribute"),
    ]
    for name, title, desc, content, active in pages:
        write(name, page(title, desc, content, active, count, name))

    print("Built %d pages + lexicon.json (%d entries) -> %s"
          % (len(pages), count, DIST))
    if not REPO_SET:
        print("WARNING: REPO_URL is still the 'your-username' placeholder; the "
              "Contribute CTA is disabled. Set FALENI_REPO_URL or edit build.py.")


if __name__ == "__main__":
    main()
