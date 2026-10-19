"""Build the ORBIT tutorial, homepage entry and downloadable source."""
import html
import json
import shutil
import zipfile

PATH = 'tutorials/codex-product-launch-video/'


def add_assets(page, prefix, tutorial=False):
    marker = f'<script src="{prefix}assets/i18n.js"'
    page = page.replace(marker,
        f'<script src="{prefix}assets/orbit-translations.js" defer></script>'
        f'<link rel="stylesheet" href="{prefix}assets/orbit.css">' + marker, 1)
    if tutorial:
        page = page.replace('</body>', f'<script src="{prefix}assets/orbit.js" defer></script></body>')
    return page


def build_orbit(root, out, base, document):
    content = root / 'site/tutorials'
    meta = json.loads((content / 'orbit.json').read_text())
    source = root / 'templates/orbit-launch-15s'
    assets = out / 'assets/orbit'
    editor = assets / 'editor'
    # Copy only the files intended for distribution, never node_modules or QA output.
    filenames = ['index.html', 'config.js', 'motion.js', 'render.mjs', 'check.mjs',
                 'package.json', 'LICENSE', 'README.md', 'prompt.en.txt', 'prompt.zh-CN.txt']
    editor.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(assets / 'orbit-source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in filenames:
            shutil.copy2(source / name, editor / name)
            archive.write(source / name, 'orbit/' + name)
    editor_html = (editor / 'index.html').read_text()
    editor_html = editor_html.replace('</head>',
        '<meta name="robots" content="noindex">'
        '<meta name="description" content="Edit the ORBIT product launch animation and save your configuration.">'
        f'<link rel="canonical" href="{html.escape(base)}assets/orbit/editor/">'
        '</head>')
    (editor / 'index.html').write_text(editor_html)

    home = (out / 'index.html').read_text()
    marker = '<section class="collection" id="collection"'
    assert marker in home
    home = home.replace(marker, (content / 'orbit-entry.html').read_text() + marker, 1)
    hero_marker = '</div><p class="hero-note">'
    assert hero_marker in home
    home = home.replace(hero_marker,
        f'<a class="text-link orbit-hero-link" href="./{PATH}">Make a 15-second video with Codex →</a>' + hero_marker, 1)
    home = home.replace('<a href="#templates">Editable templates ↓</a>',
        '<a href="#templates">Editable templates ↓</a><a href="#hands-on">Hands-on tutorial ↓</a>', 1)
    (out / 'index.html').write_text(add_assets(home, './'))

    canonical = base + PATH
    page = document(meta['title'], meta['description'],
        (content / 'orbit.html').read_text(), PATH, image_path='assets/orbit/poster.jpg')
    page = page.replace('These examples have not been independently reproduced by this collection.',
        'Community examples have not been independently reproduced unless explicitly stated. '
        'This Codex tutorial was rendered and checked locally.')
    schema = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Collection', 'item': base},
            {'@type': 'ListItem', 'position': 2, 'name': meta['title'], 'item': canonical}]},
        {'@type': 'VideoObject', '@id': canonical + '#video',
         'name': 'ORBIT — 15-second product launch animation made with Codex',
         'description': 'A silent product launch animation for the fictional ORBIT note-taking app, featuring kinetic typography, orbital graphics and three feature cards.',
         'thumbnailUrl': [base + 'assets/orbit/poster.jpg'],
         'uploadDate': meta['published'], 'duration': 'PT15S',
         'contentUrl': base + 'assets/orbit/after.mp4',
         'mainEntityOfPage': canonical,
         'creator': {'@type': 'Organization', 'name': 'Leadde Open Lab',
                     'url': 'https://github.com/LeaddeOpenLab'}}]}
    schema_json = json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c')
    page = page.replace('</head>',
        '<meta name="robots" content="index,follow,max-image-preview:large">'
        '<meta property="og:image:width" content="1920">'
        '<meta property="og:image:height" content="1080">'
        '<meta property="og:image:alt" content="ORBIT product launch animation: Make room for the spark.">'
        f'<script type="application/ld+json">{schema_json}</script></head>')
    destination = out / PATH
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'index.html').write_text(add_assets(page, '../../', tutorial=True))
    return PATH
