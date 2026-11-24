#!/usr/bin/env python3
"""
Baut portfolio.girnstein.studio aus den Dateien in content/.

    python3 build.py            -> erzeugt die fertige Website in _site/
    python3 build.py --serve    -> baut und startet eine Vorschau auf http://localhost:8000

Keine Abhängigkeiten, nur Python 3.9+.

Inhalte:
    content/site.md            globale Einstellungen (Name, Domain, Links ...)
    content/pages/*.md         Seiten (Startseite, About, Volunteering, Kontakt, Impressum, Work-Übersicht)
    content/work/<slug>.md     ein Projekt pro Datei
    content/blog/<slug>.md     ein Blogpost pro Datei
Bilder liegen in assets/ (Projekte: assets/work/<slug>/).
"""
import html
import json
import os
import re
import shutil
import struct
import subprocess
import sys
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, 'content')
OUT = os.path.join(ROOT, '_site')

CATEGORY_LABELS = {'tech': 'Tech', 'creative': 'Kreativ'}


# --------------------------------------------------------------------------
# Frontmatter
# --------------------------------------------------------------------------

def parse_value(v):
    v = v.strip()
    if v == '':
        return ''
    if v.startswith('[') and v.endswith(']'):
        inner = v[1:-1].strip()
        if not inner:
            return []
        return [parse_value(x) for x in re.findall(r'"(?:[^"\\]|\\.)*"|[^,]+', inner)]
    if len(v) >= 2 and v[0] == v[-1] == '"':
        return v[1:-1].replace('\\"', '"')
    if v in ('true', 'ja', 'yes'):
        return True
    if v in ('false', 'nein', 'no'):
        return False
    if re.fullmatch(r'-?\d+', v):
        return int(v)
    return v


def read_doc(path):
    text = open(path, encoding='utf-8').read()
    meta, body = {}, text
    if text.startswith('---'):
        _, fm, body = text.split('---', 2)
        for line in fm.strip().splitlines():
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            key, _, val = line.partition(':')
            meta[key.strip()] = parse_value(val)
    meta['_body'] = body.strip('\n')
    meta['_file'] = os.path.relpath(path, ROOT)
    meta.setdefault('slug', os.path.splitext(os.path.basename(path))[0])
    return meta


def as_list(v):
    if v in (None, ''):
        return []
    return v if isinstance(v, list) else [x.strip() for x in str(v).split(',') if x.strip()]


# --------------------------------------------------------------------------
# Bildgrößen (für width/height gegen Layout-Springen)
# --------------------------------------------------------------------------

def image_size(path):
    try:
        with open(path, 'rb') as f:
            head = f.read(26)
            if head[:8] == b'\x89PNG\r\n\x1a\n':
                return struct.unpack('>II', head[16:24])
            if head[:2] == b'\xff\xd8':
                f.seek(2)
                while True:
                    marker = f.read(2)
                    if len(marker) < 2 or marker[0] != 0xFF:
                        return None
                    if marker[1] in (0xC0, 0xC1, 0xC2):
                        f.read(3)
                        h, w = struct.unpack('>HH', f.read(4))
                        return w, h
                    seg = struct.unpack('>H', f.read(2))[0]
                    f.seek(seg - 2, 1)
    except OSError:
        pass
    return None


def img_tag(src, alt='', cls='', eager=False, sizes=None):
    attrs = [f'src="{esc(src)}"', f'alt="{esc(alt)}"']
    if src.startswith('/'):
        dim = image_size(os.path.join(ROOT, src.lstrip('/')))
        if dim:
            attrs.append(f'width="{dim[0]}" height="{dim[1]}"')
    if cls:
        attrs.append(f'class="{cls}"')
    attrs.append('loading="eager" fetchpriority="high"' if eager else 'loading="lazy"')
    attrs.append('decoding="async"')
    return '<img ' + ' '.join(attrs) + '>'


# --------------------------------------------------------------------------
# Markdown (kleiner Dialekt, siehe README)
# --------------------------------------------------------------------------

def esc(s):
    return html.escape(str(s), quote=True)


def resolve(url, base):
    if re.match(r'^(https?:|mailto:|tel:|/|#)', url):
        return url
    return base.rstrip('/') + '/' + url


def inline(text, base=''):
    links = []

    def keep_link(m):
        label, url = m.group(1), m.group(2)
        url = resolve(url, base)
        ext = url.startswith('http')
        attrs = ' target="_blank" rel="noopener"' if ext else ''
        links.append(f'<a href="{esc(url)}"{attrs}>{inline_fmt(esc(label))}</a>')
        return f'\x00{len(links) - 1}\x00'

    text = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', keep_link, text)
    text = inline_fmt(esc(text))
    text = text.replace('  \n', '<br>\n')
    return re.sub(r'\x00(\d+)\x00', lambda m: links[int(m.group(1))], text)


def inline_fmt(t):
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t, flags=re.S)
    t = re.sub(r'(?<![\w/])_(.+?)_(?![\w])', r'<em>\1</em>', t)
    return t


IMG_RE = re.compile(r'^!\[([^\]]*)\]\(([^)\s]+)\)$')


class Ctx:
    """was Direktiven wie ::projects brauchen"""
    def __init__(self, base='', projects=None, site=None):
        self.base = base
        self.projects = projects or []
        self.site = site or {}


def md(text, ctx):
    return render_blocks(text.split('\n'), ctx)


def render_blocks(lines, ctx):
    out, para = [], []

    def flush():
        if not para:
            return
        imgs = [IMG_RE.match(l.strip()) for l in para]
        if all(imgs):
            figs = ''.join(img_tag(resolve(m.group(2), ctx.base), m.group(1)) for m in imgs)
            out.append(f'<div class="gallery reveal n{len(imgs)}">{figs}</div>')
        else:
            out.append('<p>' + inline('\n'.join(para), ctx.base) + '</p>')
        para.clear()

    i = 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        # ::: container
        if s.startswith(':::') and len(s) > 3:
            flush()
            names = s[3:].strip().split()
            depth, j, inner = 1, i + 1, []
            while j < len(lines):
                t = lines[j].strip()
                if t.startswith(':::') and len(t) > 3:
                    depth += 1
                elif t == ':::':
                    depth -= 1
                    if depth == 0:
                        break
                inner.append(lines[j])
                j += 1
            out.append(f'<div class="{" ".join(esc(n) for n in names)}">' + render_blocks(inner, ctx) + '</div>')
            i = j + 1
            continue
        if not s:
            flush()
        elif s.startswith('#'):
            flush()
            m = re.match(r'^(#{1,6})\s+(.*)$', s)
            lvl = min(len(m.group(1)) + 0, 6)
            out.append(f'<h{lvl} class="reveal">{inline(m.group(2), ctx.base)}</h{lvl}>')
        elif s.startswith('::'):
            flush()
            out.append(directive(s[2:].strip(), ctx))
        elif s.startswith('>'):
            flush()
            buf = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                buf.append(lines[i].strip()[1:].strip())
                i += 1
            parts = [p for p in '\n'.join(buf).split('\n\n') if p.strip()]
            out.append(''.join(f'<p class="lead reveal">{inline(p, ctx.base)}</p>' for p in parts))
            continue
        elif s in ('---', '***'):
            flush()
            out.append('<hr>')
        elif re.match(r'^[-*] ', s):
            flush()
            items = []
            while i < len(lines) and re.match(r'^[-*] ', lines[i].strip()):
                items.append(lines[i].strip()[2:])
                i += 1
            out.append('<ul>' + ''.join(f'<li>{inline(x, ctx.base)}</li>' for x in items) + '</ul>')
            continue
        else:
            para.append(line.rstrip(' ') + ('  ' if line.endswith('  ') else ''))
        i += 1
    flush()
    return '\n'.join(out)


def directive(s, ctx):
    name, _, arg = s.partition(' ')
    arg = arg.strip()
    if name == 'label':
        return f'<p class="label reveal"><span class="dot"></span>{inline(arg, ctx.base)}</p>'
    if name == 'button':
        m = re.match(r'\[([^\]]+)\]\(([^)\s]+)\)', arg)
        if not m:
            return ''
        return button(m.group(1), resolve(m.group(2), ctx.base))
    if name == 'youtube':
        vid = esc(arg.split()[0])
        return (f'<div class="video reveal" data-yt="{vid}">'
                f'<button type="button" class="video__play" aria-label="Video abspielen (lädt YouTube)">'
                + img_tag(f'/assets/video/{vid}.jpg', '') +
                f'<span class="video__icon" aria-hidden="true"></span>'
                f'<span class="video__note">Mit Klick wird das Video von YouTube geladen.</span></button></div>')
    if name == 'section':
        title, _, num = arg.partition('|')
        return (f'<div class="sectionhead reveal"><h2 class="sectionhead__title">{inline(title.strip())}</h2>'
                f'<span class="sectionhead__num">{esc(num.strip())}</span></div>')
    if name == 'projects':
        args = arg.split()
        mode = args[0] if args else 'all'
        items = ctx.projects
        if mode == 'featured':
            items = [p for p in items if p.get('featured')]
        elif mode == 'highlight':
            items = [p for p in items if p.get('highlight')]
        elif mode in CATEGORY_LABELS:
            items = [p for p in items if p.get('category') == mode]
        if len(args) > 1 and args[1].isdigit():
            items = items[:int(args[1])]
        return project_grid(items)
    if name == 'contact':
        return contact_block(ctx.site)
    if name == 'stat':
        num, _, label = arg.partition('|')
        return f'<div class="stat reveal"><span class="stat__num">{esc(num.strip())}</span><span class="stat__label">{inline(label.strip())}</span></div>'
    return f'<!-- unbekannte Direktive: {esc(name)} -->'


# --------------------------------------------------------------------------
# Bausteine
# --------------------------------------------------------------------------

ARROW = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def button(label, url, cls=''):
    ext = url.startswith('http')
    attrs = ' target="_blank" rel="noopener"' if ext else ''
    return (f'<a class="btn {cls}" href="{esc(url)}"{attrs}><span class="btn__icon">{ARROW}</span>'
            f'<span class="btn__label">{esc(label)}</span></a>')


def project_url(p):
    return f'/work/{p["slug"]}/'


def project_card(p):
    cover = f'/assets/work/{p["slug"]}/{p["cover"]}'
    tags = ''.join(f'<span class="pill">{esc(t)}</span>' for t in as_list(p.get('tags')))
    badge = ''
    if p.get('highlight'):
        badge = f'<span class="card__badge">Highlight · {esc(p.get("focus", ""))}</span>'
    return (f'<a class="card reveal" href="{project_url(p)}" data-cat="{esc(p.get("category", ""))}" '
            f'data-focus="{esc(p.get("focus", ""))}" data-cursor="Ansehen">'
            f'<span class="card__bar"><span class="card__title">{esc(p["title"])}</span>'
            f'<span class="card__year">{esc(p.get("year", ""))}</span></span>'
            f'<span class="card__img">{img_tag(cover, p.get("cover_alt", p["title"]))}{badge}</span>'
            f'<span class="card__tags"><span class="pill pill--cat">{esc(CATEGORY_LABELS.get(p.get("category"), ""))}</span>{tags}</span>'
            f'</a>')


def project_grid(items):
    return '<div class="grid">' + ''.join(project_card(p) for p in items) + '</div>'


def contact_block(site):
    mail = site['email']
    return f'''<section class="connect reveal">
  <p class="label"><span class="dot"></span>Connect</p>
  <h2 class="connect__title">Let’s do something incredible together</h2>
  <p class="connect__text">Lass uns gemeinsam etwas Starkes bauen. Schreib mir, ich freue mich auf dein Projekt und deine Ideen.</p>
  <div class="connect__actions">
    {button(mail, 'mailto:' + mail, 'btn--lime')}
    {button('LinkedIn', site['linkedin'])}
    {button('Instagram', site['instagram'])}
  </div>
</section>'''


# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------

def gs_network():
    return open(os.path.join(ROOT, 'templates', 'gs-network.html'), encoding='utf-8').read()


def nav_links(site, current):
    items = [('/', 'Home'), ('/about/', 'About'), ('/work/', 'Work'), ('/volunteer/', 'Volunteering')]
    out = []
    for n, (url, label) in enumerate(items, 1):
        cur = ' aria-current="page"' if current == url else ''
        out.append(f'<li><a href="{url}"{cur}><span class="nav__num">0{n}</span>{label}</a></li>')
    return ''.join(out)


def layout(site, page):
    """page: dict mit title, description, url, image, body, jsonld, noindex, nav, og_type"""
    url = site['url'].rstrip('/') + page['url']
    image = page.get('image') or site['og_image']
    image_abs = image if image.startswith('http') else site['url'].rstrip('/') + image
    title = page['title']
    desc = page.get('description') or site['description']
    robots = 'noindex, follow' if page.get('noindex') else 'index, follow, max-image-preview:large'
    jsonld = json.dumps(page['jsonld'], ensure_ascii=False, indent=1) if page.get('jsonld') else ''
    year = date.today().year
    nav_cur = page.get('nav', '')
    return f'''<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{esc(url)}">
<meta name="author" content="{esc(site['name'])}">
<meta property="og:type" content="{page.get('og_type', 'website')}">
<meta property="og:site_name" content="{esc(site['site_name'])}">
<meta property="og:locale" content="de_DE">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(url)}">
<meta property="og:image" content="{esc(image_abs)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{esc(image_abs)}">
<meta name="theme-color" content="#090909">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/pages/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/clash-display-600.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css?v={site['_version']}">
{('<script type="application/ld+json">' + jsonld + '</script>') if jsonld else ''}
<script>document.documentElement.classList.add('js')</script>
</head>
<body class="{page.get('body_class', '')}">
<a class="skip" href="#main">Zum Inhalt springen</a>
<header class="header">
  <a class="header__logo" href="/" aria-label="David Girnstein, Startseite">{img_tag('/assets/pages/logo.png', '#DAVID', eager=True)}</a>
  <nav class="nav" aria-label="Hauptnavigation">
    <ul class="nav__list">{nav_links(site, nav_cur)}</ul>
    <a class="nav__cta" href="/contact/">Get in touch</a>
  </nav>
  <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="menu" aria-label="Menü öffnen"><span></span><span></span></button>
</header>
<div class="menu" id="menu" hidden>
  <ul>{nav_links(site, nav_cur)}<li><a href="/contact/"><span class="nav__num">05</span>Get in touch</a></li></ul>
</div>
<main id="main">
{page['body']}
</main>
<footer class="footer">
  <div class="footer__top">
    <p class="footer__kicker">Interested in working with me?</p>
    <a class="footer__mail" href="mailto:{esc(site['email'])}">{esc(site['email'])}</a>
  </div>
  <div class="footer__cols">
    <div><p class="footer__h">Social:</p><a href="{esc(site['instagram'])}" target="_blank" rel="noopener">Instagram</a><a href="{esc(site['linkedin'])}" target="_blank" rel="noopener">LinkedIn</a></div>
    <div><p class="footer__h">Information:</p><a href="/impressum/">Impressum &amp; Datenschutz</a><a href="/contact/">Kontakt</a></div>
    <div><p class="footer__h">Available:</p><p>{esc(site['available'])}</p></div>
    <div><p class="footer__h">Expertise:</p><p>{'<br>'.join(esc(x) for x in as_list(site['expertise']))}</p></div>
  </div>
{gs_network()}
  <p class="footer__copy">© {year} {esc(site['name'])}</p>
</footer>
<a class="badge" href="/contact/" aria-label="Kontakt aufnehmen" data-cursor="Hallo!">
  <svg class="badge__ring" viewBox="0 0 100 100" aria-hidden="true"><defs><path id="badge-circle" d="M50,50 m-37,0 a37,37 0 1,1 74,0 a37,37 0 1,1 -74,0"/></defs><text><textPath href="#badge-circle" textLength="230">CONTACT ME • CONTACT ME • </textPath></text></svg>
  <svg class="badge__star" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 0c.6 6.2 5.8 11.4 12 12-6.2.6-11.4 5.8-12 12-.6-6.2-5.8-11.4-12-12C6.2 11.4 11.4 6.2 12 0z"/></svg>
</a>
<div class="cursor" aria-hidden="true"><span class="cursor__label"></span></div>
<script src="/assets/site.js?v={site['_version']}" defer></script>
</body>
</html>
'''


def hero(title, image, alt='', kicker='', sub='', extra='', cls=''):
    img = img_tag(image, alt, cls='hero__img', eager=True) if image else ''
    return f'''<section class="hero {cls}">
  {img}
  <div class="hero__shade"></div>
  <div class="hero__inner">
    {f'<div class="hero__kicker">{kicker}</div>' if kicker else ''}
    <h1 class="hero__title" data-split>{title}</h1>
    {f'<p class="hero__sub">{sub}</p>' if sub else ''}
    {extra}
  </div>
</section>'''


# --------------------------------------------------------------------------
# JSON-LD
# --------------------------------------------------------------------------

def person_node(site):
    return {
        '@type': 'Person', '@id': site['person_id'], 'name': site['name'],
        'url': site['cv_url'], 'sameAs': [site['linkedin'], site['instagram'], site['url']],
    }


def website_node(site):
    return {
        '@type': 'WebSite', '@id': site['url'] + '/#website', 'url': site['url'] + '/',
        'name': site['site_name'], 'inLanguage': 'de-DE', 'publisher': {'@id': site['person_id']},
    }


def breadcrumbs(site, trail):
    return {
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': n, 'name': name, 'item': site['url'] + url}
            for n, (name, url) in enumerate(trail, 1)
        ],
    }


def graph(*nodes):
    return {'@context': 'https://schema.org', '@graph': [n for n in nodes if n]}


# --------------------------------------------------------------------------
# Seiten bauen
# --------------------------------------------------------------------------

def write(rel_url, content):
    path = os.path.join(OUT, rel_url.strip('/'), 'index.html') if rel_url.endswith('/') else os.path.join(OUT, rel_url.lstrip('/'))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(content)


def load_collection(name, site):
    folder = os.path.join(CONTENT, name)
    items = []
    if not os.path.isdir(folder):
        return items
    for fn in sorted(os.listdir(folder)):
        if not fn.endswith('.md') or fn.startswith('_'):
            continue
        d = read_doc(os.path.join(folder, fn))
        if d.get('visible') is False:
            continue
        portfolios = as_list(d.get('portfolio')) or ['main']
        if site['portfolio'] not in portfolios:
            continue
        items.append(d)
    items.sort(key=lambda d: (d.get('order', 999), -int(d.get('year') or 0), d['title']))
    return items


def git_date(path):
    try:
        r = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', path], cwd=ROOT, capture_output=True, text=True, timeout=10)
        return r.stdout.strip() or None
    except Exception:
        return None


def build():
    site = read_doc(os.path.join(CONTENT, 'site.md'))
    site['url'] = site['url'].rstrip('/')
    site['_version'] = date.today().strftime('%Y%m%d')
    projects = load_collection('work', site)
    posts = load_collection('blog', site)
    pages = {os.path.splitext(f)[0]: read_doc(os.path.join(CONTENT, 'pages', f))
             for f in os.listdir(os.path.join(CONTENT, 'pages')) if f.endswith('.md')}

    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(os.path.join(ROOT, 'assets'), os.path.join(OUT, 'assets'))
    for f in ('CNAME',):
        if os.path.exists(os.path.join(ROOT, f)):
            shutil.copy(os.path.join(ROOT, f), OUT)
    open(os.path.join(OUT, '.nojekyll'), 'w').close()

    sitemap = []  # (url, source file)
    ctx_pages = Ctx(base='/assets/pages', projects=projects, site=site)
    person, website = person_node(site), website_node(site)

    # ---- Seiten aus content/pages --------------------------------------
    for key, p in pages.items():
        if p.get('visible') is False:
            continue
        url = p.get('url', f'/{key}/')
        body_html = md(p['_body'], ctx_pages)
        template = p.get('template', 'page')
        if template == 'home':
            body = home_hero(site, p) + f'<div class="home">{body_html}</div>'
        elif template == 'work':
            body = hero(esc(p.get('hero_title', p['title'])), p.get('hero_image'), p.get('hero_alt', '')) + work_index(projects, body_html)
        else:
            body = hero(p.get('hero_title_html') or esc(p.get('hero_title', p['title'])), p.get('hero_image'), p.get('hero_alt', '')) + \
                f'<div class="page prose">{body_html}</div>'
        trail = [('Home', '/')] + ([] if url == '/' else [(p.get('nav_title', p['title']), url)])
        node = {'@type': p.get('schema', 'WebPage'), '@id': site['url'] + url + '#webpage', 'url': site['url'] + url,
                'name': p.get('seo_title', p['title']), 'description': p.get('description', ''),
                'isPartOf': {'@id': website['@id']}, 'inLanguage': 'de-DE'}
        if template == 'home':
            node['about'] = {'@id': site['person_id']}
        if template == 'work':
            node['mainEntity'] = {'@type': 'ItemList', 'itemListElement': [
                {'@type': 'ListItem', 'position': n, 'url': site['url'] + project_url(x), 'name': x['title']}
                for n, x in enumerate(projects, 1)]}
        write(url, layout(site, {
            'title': p.get('seo_title', p['title']), 'description': p.get('description'), 'url': url,
            'image': p.get('og_image') or p.get('hero_image'), 'body': body, 'noindex': p.get('noindex'),
            'nav': url, 'body_class': f'tpl-{template}',
            'jsonld': graph(website, person, node, breadcrumbs(site, trail) if url != '/' else None),
        }))
        if not p.get('noindex'):
            sitemap.append((url, p['_file']))

    # ---- Projekte -------------------------------------------------------
    for n, p in enumerate(projects):
        url = project_url(p)
        base = f'/assets/work/{p["slug"]}'
        cover = f'{base}/{p["cover"]}'
        ctx = Ctx(base=base, projects=projects, site=site)
        actions = ''
        if p.get('link'):
            label, _, href = str(p['link']).partition('|')
            actions += button(label.strip(), href.strip(), 'btn--light')
        actions += ''.join(f'<span class="pill pill--dark">{esc(t)}</span>' for t in as_list(p.get('tags')))
        kicker = ''
        if p.get('year'):
            kicker += f'<span class="chip"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M3 10h18M8 3v4M16 3v4" stroke="currentColor" stroke-width="2"/></svg>{esc(p["year"])}</span>'
        kicker += f'<span class="chip chip--cat">{esc(CATEGORY_LABELS.get(p.get("category"), ""))} · {esc(p.get("focus", ""))}</span>'
        others = [x for x in projects if x is not p]
        more = (others[n:] + others[:n])[:2]
        body = hero(esc(p['title']), cover, p.get('cover_alt', ''), kicker=kicker, sub=esc(p.get('summary', '')),
                    extra=f'<div class="hero__actions">{actions}</div>', cls='hero--project') + \
            f'<article class="page prose">{md(p["_body"], ctx)}</article>' + \
            f'<section class="more"><div class="sectionhead"><h2 class="sectionhead__title">Wanna see more?</h2><a class="sectionhead__num" href="/work/">Alle Projekte →</a></div>{project_grid(more)}</section>'
        desc = p.get('description') or p.get('summary') or f'{p["title"]}: Projekt von {site["name"]}.'
        work = {
            '@type': 'CreativeWork', '@id': site['url'] + url + '#work', 'url': site['url'] + url,
            'name': p['title'], 'headline': p['title'], 'description': desc,
            'image': site['url'] + cover, 'inLanguage': 'de-DE',
            'genre': CATEGORY_LABELS.get(p.get('category'), ''),
            'keywords': ', '.join(as_list(p.get('tags')) + [p.get('focus', '')]),
            'creator': {'@id': site['person_id']}, 'author': {'@id': site['person_id']},
            'isPartOf': {'@id': website['@id']},
        }
        if p.get('year'):
            work['dateCreated'] = str(p['year'])
        vids = re.findall(r'^::youtube\s+([\w-]+)', p['_body'], re.M)
        if vids:
            work['video'] = [{'@type': 'VideoObject', 'name': p['title'], 'embedUrl': f'https://www.youtube-nocookie.com/embed/{v}',
                              'thumbnailUrl': f'{site["url"]}/assets/video/{v}.jpg', 'description': desc} for v in vids]
        write(url, layout(site, {
            'title': p.get('seo_title') or f'{p["title"]} | {site["name"]}', 'description': desc, 'url': url,
            'image': cover, 'body': body, 'nav': '/work/', 'og_type': 'article', 'body_class': 'tpl-project',
            'jsonld': graph(website, person, work, breadcrumbs(site, [('Home', '/'), ('Work', '/work/'), (p['title'], url)])),
        }))
        sitemap.append((url, p['_file']))

    # ---- Blog -----------------------------------------------------------
    for p in posts:
        url = f'/blog/{p["slug"]}/'
        base = f'/assets/blog/{p["slug"]}'
        cover = resolve(p.get('cover', ''), base) if p.get('cover') else None
        ctx = Ctx(base=base, projects=projects, site=site)
        body = hero(esc(p['title']), cover, p.get('cover_alt', ''), kicker=f'<span class="chip">{esc(p.get("date", ""))}</span>',
                    sub=esc(p.get('summary', '')), cls='hero--project') + f'<article class="page prose">{md(p["_body"], ctx)}</article>'
        post = {'@type': 'BlogPosting', '@id': site['url'] + url + '#post', 'url': site['url'] + url,
                'headline': p['title'], 'description': p.get('summary', ''), 'inLanguage': 'de-DE',
                'author': {'@id': site['person_id']}, 'publisher': {'@id': site['person_id']},
                'isPartOf': {'@id': website['@id']}}
        if cover:
            post['image'] = cover if cover.startswith('http') else site['url'] + cover
        if p.get('date_iso'):
            post['datePublished'] = p['date_iso']
        write(url, layout(site, {
            'title': f'{p["title"]} | {site["name"]}', 'description': p.get('summary'), 'url': url, 'image': cover,
            'body': body, 'og_type': 'article', 'body_class': 'tpl-project',
            'jsonld': graph(website, person, post, breadcrumbs(site, [('Home', '/'), (p['title'], url)])),
        }))
        sitemap.append((url, p['_file']))

    # ---- 404, robots, sitemap ------------------------------------------
    write('/404.html', layout(site, {
        'title': f'Seite nicht gefunden | {site["name"]}', 'url': '/404.html', 'noindex': True,
        'body': hero('404*', '/assets/pages/contact-hero.jpg', '') +
        '<div class="page prose"><p class="lead">Diese Seite gibt es (nicht mehr).</p>' + button('Zur Startseite', '/') + ' ' + button('Alle Projekte', '/work/') + '</div>',
    }))
    open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\n\nSitemap: {site["url"]}/sitemap.xml\n')
    entries = []
    for url, src in sorted(sitemap, key=lambda x: (x[0] != '/', x[0])):
        lm = git_date(src)
        entries.append(f'  <url><loc>{esc(site["url"] + url)}</loc>' + (f'<lastmod>{lm}</lastmod>' if lm else '') + '</url>')
    open(os.path.join(OUT, 'sitemap.xml'), 'w').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(entries) + '\n</urlset>\n')
    print(f'Fertig: {len(projects)} Projekte, {len(posts)} Blogposts, {len(sitemap)} URLs in der Sitemap -> {os.path.relpath(OUT)}/')


def home_hero(site, p):
    socials = (f'<a href="{esc(site["instagram"])}" target="_blank" rel="noopener">Instagram</a>'
               f'<a href="{esc(site["linkedin"])}" target="_blank" rel="noopener">LinkedIn</a>')
    return f'''<section class="hero hero--home">
  {img_tag(p['hero_image'], p.get('hero_alt', ''), cls='hero__img', eager=True)}
  <div class="hero__shade"></div>
  <div class="hero__inner">
    <div class="hero__kicker">©{date.today().year}</div>
    <h1 class="hero__title hero__title--xl" data-split>{esc(p.get('hero_title', 'David'))}<span class="accent">*</span></h1>
    <span class="visually-hidden">{esc(site['name'])}: {esc(p.get('tagline', ''))}</span>
    <dl class="hero__facts">
      <div><dt>Social:</dt><dd>{socials}</dd></div>
      <div><dt>Location:</dt><dd>{esc(site['location'])}<br><time class="clock" data-tz="Europe/Berlin"></time></dd></div>
      <div><dt>Available:</dt><dd>{esc(site['available'])}</dd></div>
      <div><dt>Expertise:</dt><dd>{'<br>'.join(esc(x) for x in as_list(site['expertise']))}</dd></div>
    </dl>
  </div>
</section>'''


def work_index(projects, intro_html):
    counts = {k: sum(1 for p in projects if p.get('category') == k) for k in CATEGORY_LABELS}
    filters = [('all', 'Alle', len(projects))] + [(k, CATEGORY_LABELS[k], counts[k]) for k in ('tech', 'creative')]
    btns = ''.join(f'<button type="button" class="filter__btn" data-filter="{k}" aria-pressed="{"true" if k == "all" else "false"}">'
                   f'{label}<span class="filter__count">{n}</span></button>' for k, label, n in filters)
    return f'''<div class="page page--wide">
  {intro_html}
  <div class="sectionhead reveal"><h2 class="sectionhead__title">All Works</h2><span class="sectionhead__num">{len(projects):02d}</span></div>
  <div class="filter" role="group" aria-label="Projekte filtern">{btns}</div>
  {project_grid(projects)}
</div>'''


def serve():
    import http.server
    import functools
    port = int(os.environ.get('PORT', 8000))
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=OUT)
    print(f'Vorschau: http://localhost:{port}/  (Strg+C beendet)')
    http.server.ThreadingHTTPServer(('127.0.0.1', port), handler).serve_forever()


if __name__ == '__main__':
    build()
    if '--serve' in sys.argv:
        serve()
