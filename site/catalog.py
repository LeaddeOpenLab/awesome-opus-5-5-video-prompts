"""Small catalog view built from the same published records as the repository."""
import html
import json
import re
import shutil

E = lambda value: html.escape(str(value), quote=True)
GROUPS = {'product-brand': 'Product & brand', 'motion-graphics': 'Motion graphics', 'ui-web': 'UI & web', 'explainers': 'Explainers', 'music-storytelling': 'Music & storytelling', '3d-scenes': '3D worlds', 'games-interactive': 'Games & interactive'}

def build_catalog(root, out, repo, selected):
    membership = {}
    for key in GROUPS:
        for ident in re.findall(r'../../prompts/(\d+)\.md', (root / f'data/categories/{key}.md').read_text()):
            membership.setdefault(ident, []).append(key)
    update = json.loads((root / 'data/latest-update.json').read_text())
    records = []
    for path in (root / 'data/library').glob('*.json'):
        if not (root / 'prompts' / (path.stem + '.md')).is_file():
            continue
        record = json.loads(path.read_text())
        records.append((path.stem, record))
    records.sort(key=lambda row: (row[1].get('storedAt', ''), row[0]), reverse=True)
    cards = []
    counts = {key: 0 for key in GROUPS}
    for ident, record in records:
        ev = record.get('analysis', {}).get('caseEvidence', {})
        groups = list(dict.fromkeys(membership.get(ident, [])))
        for key in groups: counts[key] += 1
        title = ev.get('title') or record.get('summaryEn') or record.get('summary') or ident
        purpose = ev.get('purpose', {}).get('label') or ''
        author = record['post']['author']['username']
        tools = ev.get('tools') or []
        tool = ' · '.join(dict.fromkeys(x.get('name', '') for x in tools if isinstance(x, dict) and x.get('name'))) or 'Tools not specified'
        status = 'Full shared prompt' if ev.get('prompt', {}).get('status') == 'full_original' else 'Shared prompt fragment'
        date = record.get('storedAt', '')[:10]
        new = date == update['date'][:10]
        target = './prompts/' + selected[ident]['slug'] + '/' if ident in selected else repo + '/blob/main/prompts/' + ident + '.md'
        cover = record.get('coverPath', '')
        media = '<div class="catalog-placeholder">Code &amp; motion</div>'
        if cover and (root / cover).is_file():
            dest = out / 'assets/catalog' / (ident + '.jpg')
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / cover, dest)
            media = f'<img src="./assets/catalog/{ident}.jpg" alt="" width="800" height="450" loading="lazy">'
        label = ' · '.join(GROUPS[g] for g in groups) or 'Creative coding'
        search = ' '.join([title, purpose, author, tool, label]).lower()
        cards.append(f'''<article class="card catalog-card" data-prompt-id="{ident}" data-placement="catalog-prompt" data-card data-category="{E(' '.join(groups))}" data-mode="catalog" data-new="{str(new).lower()}" data-search="{E(search)}" hidden>
<div class="card-media"><a href="{E(target)}" tabindex="-1" aria-hidden="true">{media}</a></div>
<div class="card-info"><div class="card-top"><span>{E(label)}</span>{'<span class="new-badge">New</span>' if new else ''}</div>
<h3><a href="{E(target)}">{E(title)}</a></h3><p>{E(purpose)}</p><p class="catalog-meta">{E(tool)}</p><p class="catalog-meta"><span>{status}</span> · <span>Added</span> <time>{E(date)}</time></p>
<div class="card-bottom"><a href="{E(record['post']['canonicalUrl'])}">@{E(author)} ↗</a><a href="{E(target)}" data-placement="catalog-prompt">View prompt →</a></div></div></article>''')
    filters = '<button class="filter" data-filter="all" aria-pressed="true">All categories</button>' + ''.join(f'<button class="filter" data-filter="{key}" aria-pressed="false"><span>{name}</span> <small>{counts[key]}</small></button>' for key,name in GROUPS.items())
    return ''.join(cards), filters, len(records), update['date'][:10]


def template_section(root, out, repo):
    cards = []
    for slug, name, description in [('product-ui-15s', 'Product UI', 'Replace your product screenshot, copy and brand color.'), ('feature-demo-15s', 'Feature Demo', 'Show a problem, the workflow and a clear result.'), ('product-launch-15s', 'Product Launch', 'Introduce your product and three key benefits.')]:
        dest = out / 'assets/templates' / slug
        dest.mkdir(parents=True, exist_ok=True)
        for file in ['poster.jpg', 'example.mp4']:
            shutil.copyfile(root / 'templates' / slug / file, dest / file)
        url = repo + '/tree/main/templates/' + slug
        cards.append(f'''<article class="card" data-prompt-id="{slug}" data-placement="template-get"><video class="template-video" controls playsinline preload="none" poster="./assets/templates/{slug}/poster.jpg" src="./assets/templates/{slug}/example.mp4" data-prompt-id="{slug}" aria-label="{name} template preview"></video><div class="card-info"><div class="kicker">Editable template</div><h3>{name}</h3><p>{description}</p><div class="card-bottom"><a href="{url}" data-placement="template-get">Get template →</a><a href="{repo}/blob/main/templates/{slug}/README.zh-CN.md">中文说明 ↗</a></div></div></article>''')
    return '<section class="collection templates" id="templates"><div class="section-heading"><div><div class="kicker">Make it yours</div><h2>Start with a 15-second template.</h2><p>Original templates by Leadde Open Lab. Edit the config, preview, then export your MP4.</p><p class="catalog-meta">15 seconds · 1080p · MIT · Export: Node.js + Playwright + FFmpeg</p></div></div><div class="grid">' + ''.join(cards) + '</div></section>'
