#!/usr/bin/env python3
"""Build the curated public site from repository records. Python standard library only."""
import html
from catalog import build_catalog, template_section
from orbit import build_orbit
import json
import os
from pathlib import Path
import shutil
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
OUT = ROOT / '_site'
CONFIG = json.loads((SITE / 'site.json').read_text())
BASE = os.environ.get('SITE_URL', CONFIG['url']).rstrip('/') + '/'
REPO = CONFIG['repository']
GA_ID = os.environ.get('GA_MEASUREMENT_ID') or CONFIG.get('ga_measurement_id', '')
VERIFY = os.environ.get('GOOGLE_SITE_VERIFICATION') or CONFIG['google_site_verification']
SELECTION = json.loads((SITE / 'selection.json').read_text())
E = lambda value: html.escape(str(value), quote=True)
CATEGORIES = {
    'motion-graphics': {'name': 'Motion graphics', 'title': 'Claude motion graphics prompts', 'intro': 'Kinetic typography, interface motion and small animated details. Explore the shared prompts behind these creator-made examples.', 'when': 'Choose this collection when timing, typography or a repeatable loop is central to the result. A short showreel can help you explore a visual direction; a UI sequence is useful for demonstrating product behavior.', 'before': 'Decide on the aspect ratio, palette and delivery format first. A browser animation and an exported video are different deliverables. Some prompts need a renderer, audio files or a prepared coding workspace.', 'short': 'Kinetic type, interface loops and animation with a sense of rhythm.'},
    'explainers': {'name': 'Explainers', 'title': 'Claude explainer video prompts', 'intro': 'Turn a business idea or a difficult concept into a visual sequence. These examples include HTML explainers, Manim lessons and code-rendered science stories.', 'when': 'Choose this collection when the viewer needs to understand an idea, a process or a change over time. Start with one clear learning outcome and an audience you can describe in a sentence.', 'before': 'Review the script before the animation. Check factual claims, define the language and audience, and decide whether you need narration. The case pages distinguish the shared prompt from our suggested setup steps.', 'short': 'Business stories and educational ideas, explained one scene at a time.'},
    '3d-worlds': {'name': '3D worlds', 'title': 'Claude 3D world and Blender prompts', 'intro': 'Explore browser-based worlds and a historical Blender reconstruction. Read the original creative brief alongside the tools and context needed to try it.', 'when': 'Choose this collection for spatial exploration, environmental storytelling or a moving camera through a scene. Browser-based work suits interaction; Blender offers a separate modeling and rendering workflow.', 'before': 'Choose the runtime and set a manageable scene scope. Test camera controls and performance early. Historical reconstructions also need source research; visual plausibility is not a substitute for evidence.', 'short': 'Places to explore, from painted towns to historical streets.'},
}
for item in SELECTION:
    record = json.loads((ROOT / 'data/library' / (item['id'] + '.json')).read_text())
    evidence = record.get('analysis', {}).get('caseEvidence', {})
    item['author'] = record['post']['author']['username']
    item['source'] = record['post']['canonicalUrl']
    prompt_info = evidence.get('prompt', {})
    item['prompt'] = (prompt_info.get('englishText') or record.get('promptTranslations', {}).get('en') or record['prompt']).strip()
    item['status'] = 'Full shared prompt' if prompt_info.get('status') == 'full_original' else 'Shared prompt fragment'
    item['model'] = 'Claude Opus ' + str(evidence.get('model', {}).get('version') or '(version not confirmed)')
    item['published'] = record['post']['publishedAt'][:10]
    item['modified'] = record.get('storedAt', record['post']['publishedAt'])[:10]
BY_ID = {item['id']: item for item in SELECTION}
PLAY = '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5 3l12 7-12 7z" fill="currentColor"/></svg>'
SEARCH = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg>'

def case_url(item):
    return 'prompts/' + item['slug'] + '/'

def link(prefix, path=''):
    return prefix + path or './'

def preview(item, prefix):
    return f'<button class="play" data-prompt-id="{item["id"]}" aria-label="Preview {E(item["title"])}" data-preview="{prefix}assets/previews/{item["id"]}.mp4" data-poster="{prefix}assets/posters/{item["id"]}.jpg" data-title="{E(item["title"])}" data-link="{prefix}{case_url(item)}" data-repo-link="{REPO}/blob/main/prompts/{item["id"]}.md">{PLAY}<span>Play preview</span></button>'

def card(item, prefix, filterable=False):
    cat = CATEGORIES[item['category']]['name']
    search = ' '.join([item['title'], item['description'], item['tool'], cat, item['author']]).lower()
    filter_category = "3d-scenes" if item["category"] == "3d-worlds" else item["category"]
    data = f' data-card data-mode="selected" data-category="{filter_category}" data-search="{E(search)}"' if filterable else ''
    feature = item.get('showcase', '') if filterable else ''
    style = ' card-' + feature if feature else ''
    motion = 'spotlight' if feature == 'spotlight' else 'hover'
    pause = '<button class="hero-pause" data-card-toggle hidden>Pause preview</button>' if feature == 'spotlight' else ''
    badge = '<div class="editor-pick">Editor’s pick</div>' if feature else ''
    return f'''<article class="card{style}" data-prompt-id="{item['id']}"{data}>
<div class="card-media"><a href="{prefix}{case_url(item)}" tabindex="-1" aria-hidden="true"><img src="{prefix}assets/posters/{item['id']}.jpg" alt="" width="800" height="500" loading="lazy"></a><video class="card-video" data-card-video="{motion}" data-prompt-id="{item['id']}" data-src="{prefix}assets/previews/{item['id']}.mp4" muted playsinline loop preload="none" aria-hidden="true"></video>{pause}{preview(item,prefix)}</div>
<div class="card-info">{badge}<div class="card-top"><span>{E(cat)}</span><span class="tool">{E(item['tool'])}</span></div>
<h3><a href="{prefix}{case_url(item)}">{E(item['title'])}</a></h3><p>{E(item['description'])}</p>
<div class="card-bottom"><a href="{E(item['source'])}">@{E(item['author'])} ↗</a><a href="{REPO}/blob/main/prompts/{item['id']}.md" data-placement="selected-card">View prompt on GitHub ↗</a></div></div></article>'''

def star_hint(target):
    return f'<div class="star-hint" data-star-hint="{target}" role="status" hidden><span>Found this useful?</span> <a href="{REPO}" data-placement="copy-success" data-link-type="star">☆ Star this repo for your next project ↗</a></div>'

def prompt_example(ident, title, setup):
    item = BY_ID[ident]
    target = 'home-prompt-' + ident
    return f'''<article class="card prompt-example" data-prompt-id="{ident}" data-placement="home-example">
<div class="card-media"><a href="./{case_url(item)}"><img src="./assets/posters/{ident}.jpg" alt="{E(item['title'])}" width="800" height="500" loading="lazy"></a>{preview(item, './')}</div>
<div class="card-info"><div class="card-top"><span>{E(item['tool'])}</span></div><h3>{E(title)}</h3><p>{E(setup)}</p>
<div class="prompt-block"><div class="prompt-header"><span>Creator’s shared prompt</span><button class="copy" data-copy="{target}" data-prompt-id="{ident}" aria-live="polite">Copy prompt</button></div><pre id="{target}" tabindex="0">{E(item['prompt'])}</pre></div>
<p class="prompt-credit"><a href="{E(item['source'])}">Original post by @{E(item['author'])} ↗</a></p>
<div class="dialog-actions"><a class="text-link" href="{REPO}/blob/main/prompts/{ident}.md">View prompt on GitHub ↗</a><a class="text-link" href="./{case_url(item)}">Setup &amp; details →</a></div></div></article>'''

def document(title, description, body, path='', image_id=None, noindex=False, image_path=None):
    prefix = '../' * len([p for p in path.split('/') if p])
    prefix = prefix or './'
    canonical = BASE + path
    image_url = BASE + (image_path or ('assets/posters/' + (image_id or '2110107260751884639') + '.jpg'))
    schema = {'@context':'https://schema.org','@type':'WebPage' if path.startswith(('prompts/', 'tutorials/')) else 'CollectionPage','name':title,'description':description,'url':canonical,'publisher':{'@type':'Organization','name':'Leadde Open Lab','url':'https://github.com/LeaddeOpenLab'}}
    verification = f'<meta name="google-site-verification" content="{E(VERIFY)}">' if VERIFY else ''
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="ga-measurement-id" content="{E(GA_ID)}"><meta name="repository-url" content="{E(REPO)}">
<title>{E(title)} | Leadde Open Lab</title><meta name="description" content="{E(description)}">
<link rel="canonical" href="{E(canonical)}">{verification}{'<meta name="robots" content="noindex">' if noindex else ''}
<meta property="og:type" content="website"><meta property="og:site_name" content="Leadde Open Lab"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(description)}"><meta property="og:url" content="{E(canonical)}"><meta property="og:image" content="{E(image_url)}"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/svg+xml" href="{prefix}assets/favicon.svg"><link rel="stylesheet" href="{prefix}assets/site.css"><script src="{prefix}assets/translations.js" defer></script><script src="{prefix}assets/i18n.js" defer></script><script src="{prefix}assets/prompts.js" defer></script><script src="{prefix}assets/site.js" defer></script>
<script type="application/ld+json">{json.dumps(schema).replace('<', chr(92)+'u003c')}</script></head><body>
<a class="skip" href="#main">Skip to content</a><header class="header"><div class="wrap"><a class="brand" href="{prefix}" aria-label="Leadde Open Lab home"><img src="{prefix}assets/leadde-logo.png" width="106" height="27" alt="Leadde"><span>Open Lab</span></a><nav class="nav" aria-label="Main navigation"><a class="nav-secondary" href="{prefix}#collection">Collection</a><a class="nav-secondary" href="{prefix}#how-to-use">How to use</a><a class="github" href="{REPO}">GitHub ↗</a><select class="language-select" data-language aria-label="Language"><option value="en">English</option><option value="zh-CN">简中</option></select></nav></div></header>
<main id="main">{body}</main>
<footer class="footer"><div class="wrap"><div class="footer-top"><span>An open collection by <a href="https://leadde.ai">Leadde</a>.</span><div class="footer-links"><a href="{REPO}">GitHub ↗</a><a href="{REPO}/issues/new">Suggest a correction</a><a href="https://leadde.ai">Leadde.ai ↗</a></div></div><p class="footer-note">Prompts and previews are credited to their original creators. These examples have not been independently reproduced by this collection. Our editable templates are original code; community materials remain their creators’ property. <a href="{REPO}/blob/main/data/docs/RIGHTS.md">Attribution &amp; use →</a></p></div></footer>
<dialog class="dialog" data-preview-dialog aria-labelledby="preview-title"><div class="dialog-bar"><h2 id="preview-title">Creator preview</h2><button class="dialog-close" data-close aria-label="Close preview">×</button></div><video controls muted playsinline loop preload="none" aria-label="Short visual preview of the creator’s work"></video><div class="dialog-foot"><span>Short creator preview · no audio</span><div class="dialog-actions"><a class="text-link" data-preview-repo-link data-placement="preview-prompt" href="{REPO}">View prompt on GitHub ↗</a><button class="copy" data-copy="preview-prompt" aria-live="polite">Copy prompt</button><a class="text-link" data-preview-link href="{prefix}">Setup &amp; details →</a></div></div>{star_hint('preview-prompt')}<pre id="preview-prompt" class="preview-prompt" hidden></pre></dialog>
</body></html>'''

def write(path, content):
    dest = OUT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding='utf-8')

OUT.mkdir(exist_ok=True)
# Only replace build-owned directories; source records are never modified.
for folder in ['assets', 'prompts', 'collections']:
    if (OUT / folder).exists(): shutil.rmtree(OUT / folder)
shutil.copytree(SITE / 'assets', OUT / 'assets')
shutil.copytree(SITE / 'public', OUT, dirs_exist_ok=True)

catalog_cards, catalog_filters, catalog_count, catalog_updated = build_catalog(ROOT, OUT, REPO, BY_ID)
templates_html = template_section(ROOT, OUT, REPO)

locale = json.loads((SITE / 'zh-CN.json').read_text())
translations = dict(locale['ui'])
for key, translated in locale['categories'].items():
    for field, value in translated.items():
        translations[CATEGORIES[key][field]] = value
for item in SELECTION:
    translated = locale['cases'][item['id']]
    for field in ['title', 'description', 'inputs', 'note'] + (['seo_title'] if 'seo_title' in item else []):
        translations[item[field]] = translated[field]
    for original, value in zip(item['steps'], translated['steps']):
        translations[original] = value
for count in range(catalog_count + 1):
    translations[f'{count} {"example" if count == 1 else "examples"}'] = f'{count} 个案例'
write('assets/translations.js', 'window.siteTranslations = ' + json.dumps(translations, ensure_ascii=False).replace('<', '\\u003c') + ';\n')

write('assets/prompts.js', 'window.sitePrompts = ' + json.dumps({x['id']: x['prompt'] for x in SELECTION}, ensure_ascii=False).replace('<', chr(92)+'u003c') + ';\n')

hero = BY_ID['2110107260751884639']
ordered = [BY_ID[i] for i in ['2110107260751884639','2110476412213686723','2102476258948927543','2109782159250608604','2103629247751618782','2103802923465768972','2103499977632997524','2103273003555402193','2103128559174971663']]
ordered[0]['showcase'] = 'spotlight'
for item in ordered[1:3]: item['showcase'] = 'featured'
filters = '<button class="filter" data-filter="all" aria-pressed="true">All work</button>' + ''.join(f'<button class="filter" data-filter="{key}" aria-pressed="false">{value["name"]}</button>' for key,value in CATEGORIES.items())
topics = ''.join(f'<article class="topic"><div class="topic-number">0{i+1} / COLLECTION</div><h3>{v["name"]}</h3><p>{v["short"]}</p><a class="text-link" href="./collections/{key}/">Explore collection <span>↗</span></a></article>' for i,(key,v) in enumerate(CATEGORIES.items()))
examples = [
    ('2110476412213686723', 'Motion graphics showreel', 'Start with a 15-second reel. Choose an animation tool in your coding workspace; the author did not name a renderer.'),
    ('2104896325255037196', 'Product introduction video', 'Replace the website URL in the prompt with your product URL. Provide your logo, brand colors and UI assets, then choose a renderer.'),
    ('2103499977632997524', 'Business explainer animation', 'Replace the bracketed business description with your offer, audience and colors. Ask for one HTML file and preview it in a browser.'),
]
examples_html = '<section class="collection prompt-examples" id="prompt-examples" aria-labelledby="examples-title"><div class="section-heading"><div><div class="kicker">Copy a prompt</div><h2 id="examples-title">Three video prompts to try with Claude Opus.</h2><p>Choose a use case, watch the preview and copy the creator’s prompt. Replace the inputs before you run it.</p></div></div><div class="grid">' + ''.join(prompt_example(*item) for item in examples) + '</div><p class="examples-note">Creator previews are references, not guaranteed outputs. These examples have not been independently reproduced by this collection.</p><a class="text-link" href="#how-to-use">How to use these prompts ↓</a></section>'
body = f'''<div class="wrap"><section class="hero"><div class="hero-copy"><div class="eyebrow">Opus 5.5, in motion</div><h1>Claude Opus <span>Video Prompts</span> &amp; Animation Examples</h1><p>Copy creator-shared prompts for motion graphics, product videos and explainers. Watch the results, check the tools and make your own with Claude Opus.</p><div class="actions"><a class="button" href="#prompt-examples">Try a prompt <span>↓</span></a><a class="text-link" data-placement="hero-star" data-link-type="star" href="{REPO}">☆ Star on GitHub <span>↗</span></a></div><p class="hero-note">Motion graphics, explainers &amp; 3D worlds.<br>Selected by Leadde Open Lab.</p></div><div class="hero-art"><div class="hero-picture"><a href="./{case_url(hero)}"><img src="./assets/posters/{hero['id']}.jpg" alt="A rainy Tokyo vending-machine diorama, shown in the creator’s model comparison" width="800" height="500" fetchpriority="high"></a><video class="hero-video" data-hero-video data-prompt-id="{hero['id']}" data-src="./assets/previews/{hero['id']}.mp4" muted playsinline loop preload="none" aria-hidden="true"></video><button class="hero-pause" data-hero-toggle hidden>Pause preview</button><span class="corner-label">FEATURED WORLD</span>{preview(hero,'./')}</div><div class="hero-caption"><div><strong>{E(hero['title'])}</strong><p>By @{hero['author']} · Three.js</p></div><a href="{REPO}/blob/main/prompts/{hero['id']}.md" class="text-link" data-placement="hero-prompt" data-prompt-id="{hero['id']}">View prompt on GitHub ↗</a></div></div></section>
<div class="index-strip"><span>Opus 5.5 video &amp; animation prompts</span><span>{catalog_count} library examples · 3 editable templates</span><span>Original creators, always credited</span></div>
<section class="collection" id="collection"><nav class="collection-nav" aria-label="Browse prompts"><button class="filter" data-browse="selected" aria-pressed="true">Selected examples</button><button class="filter" data-browse="latest" aria-pressed="false">Latest additions</button><button class="filter" data-browse="all" aria-pressed="false">All examples</button><a href="#templates">Editable templates ↓</a></nav><div class="section-heading"><div><div class="kicker">Selected work</div><h2>Standout work. A prompt behind every frame.</h2><p>Start with our editor’s picks, then explore the full library.</p><p class="catalog-meta"><span>Library updated</span> <time>{catalog_updated}</time></p></div><label class="search">{SEARCH}<span class="sr-only">Search the full library</span><input data-search type="search" placeholder="Search prompts, tools, creators…"></label></div><div class="filters"><div class="filter-options" role="group" aria-label="Filter by collection">{catalog_filters}</div><span class="result-count" data-count aria-live="polite">9 examples</span></div><div class="grid showcase-grid">{''.join(card(x,'./',True) for x in ordered)}{catalog_cards}</div><button class="button load-more" data-more hidden>Show more examples</button><p class="no-results" data-empty hidden>No matching examples. Try a different search or choose All work.</p><div class="collection-bottom"><p>Selected previews here; every library entry links to its prompt and original creator.</p><a class="text-link" href="{REPO}#browse-the-full-library" data-placement="collection-library">Browse the full library on GitHub ↗</a></div></section>{examples_html}{templates_html}</div>
<section class="topics"><div class="wrap"><div class="kicker">A closer look</div><h2>Three ways to get started.</h2><div class="topic-grid">{topics}</div></div></section>
<div class="wrap"><section class="how" id="how-to-use"><div class="how-intro"><div class="kicker">From prompt to project</div><h2>How to use Claude Opus video prompts.</h2><p>These prompts ask a coding agent to build animations. You will need a workspace that can run the generated code and its animation tools.</p></div><div class="steps"><div><div class="step-number">01</div><h3>Paste into your coding workspace</h3><p>Open Claude Code or a coding workspace with Claude Opus. Check the example’s tools, then paste the prompt and ask for the required project files.</p></div><div><div class="step-number">02</div><h3>Replace the inputs</h3><p>Swap the website URL or bracketed text for your own product, audience and colors. Supply any requested assets and specify the duration and aspect ratio.</p></div><div><div class="step-number">03</div><h3>Preview, then export</h3><p>Open HTML animations in a browser; follow the project setup for other tools. Review the result, then use your renderer or a screen recording to export a video. An HTML file is not an MP4.</p></div></div></section><section class="closing"><div><h2>Keep a few good ideas close.</h2><p>Star the GitHub collection to find it again when your next project comes along.</p></div><a class="button light" data-placement="closing-star" data-link-type="star" href="{REPO}">☆ Star on GitHub <span>↗</span></a></section></div>'''
write('index.html', document('Claude Opus Video Prompts & Animation Examples', 'Copy Claude Opus video prompts for motion graphics, product videos and explainers. Explore creator previews, tool requirements and a short getting-started guide.', body))
pages = [('', None)]
for key, cat in CATEGORIES.items():
    path = 'collections/' + key + '/'
    items = [x for x in SELECTION if x['category'] == key]
    repo_category = '3d-scenes' if key == '3d-worlds' else key
    body = f'''<div class="wrap"><div class="page-head"><nav class="breadcrumb" aria-label="Breadcrumb"><a href="../../">Collection</a><span>/</span><span>{cat['name']}</span></nav><div class="eyebrow">{len(items)} selected examples</div><h1>{cat['title']}</h1><p>{cat['intro']}</p><a class="text-link" href="{REPO}/blob/main/data/categories/{repo_category}.md" data-placement="category-library">Browse this category on GitHub ↗</a></div><div class="category-intro"><div><h2>When to use these prompts</h2><p>{cat['when']}</p></div><div><h2>Before you begin</h2><p>{cat['before']}</p></div></div><section class="collection"><div class="grid">{''.join(card(x,'../../') for x in items)}</div></section><div class="closing"><p>Looking for another direction?</p><a class="text-link" href="../../#collection">See all selected work →</a></div></div>'''
    write(path+'index.html',document(cat['title'],cat['intro'],body,path))
    pages.append((path,max(x['modified'] for x in items)))
for item in SELECTION:
    path=case_url(item); cat=CATEGORIES[item['category']]
    related=[x for x in SELECTION if x['category']==item['category'] and x['id']!=item['id']]
    body=f'''<div class="wrap"><div class="page-head"><nav class="breadcrumb" aria-label="Breadcrumb"><a href="../../">Collection</a><span>/</span><a href="../../collections/{item['category']}/">{cat['name']}</a><span>/</span><span>Prompt</span></nav><div class="eyebrow">{E(item['tool'])}</div><h1>{E(item['title'])}</h1><p>{E(item['description'])}</p></div>
<div class="detail" data-prompt-id="{item['id']}"><div class="detail-main"><video class="detail-video" data-prompt-id="{item['id']}" controls muted playsinline loop preload="none" poster="../../assets/posters/{item['id']}.jpg" src="../../assets/previews/{item['id']}.mp4" aria-label="Short creator preview of {E(item['title'])}"></video><div class="media-caption"><span>Short creator preview · no audio</span><a href="{E(item['source'])}">Original post by @{E(item['author'])} ↗</a></div><section class="prompt-block" id="prompt"><div class="prompt-header"><h2>The shared prompt</h2><div class="dialog-actions"><a class="text-link" href="{REPO}/blob/main/prompts/{item['id']}.md" data-placement="detail-prompt">View prompt on GitHub ↗</a><button class="copy" data-copy="prompt-text" data-prompt-id="{item['id']}" aria-live="polite">Copy prompt</button></div></div>{star_hint('prompt-text')}<pre id="prompt-text">{E(item['prompt'])}</pre><div class="prompt-foot">{item['status']} · English · <a href="{REPO}/blob/main/prompts/{item['id']}.md" data-placement="detail-source">View prompt on GitHub ↗</a></div></section><section class="customize"><h2>Make this prompt yours</h2><p>Suggestions from Leadde Open Lab; the creator’s prompt above is unchanged.</p><ul><li><strong>Subject:</strong> Replace the subject with your product, story or lesson.</li><li><strong>Palette:</strong> Specify your brand colors and visual style.</li><li><strong>Timing:</strong> Set a duration for video, or a loop length for interactive work.</li><li><strong>Frame:</strong> Choose landscape 16:9, portrait 9:16 or square 1:1.</li></ul></section></div>
<aside class="detail-sidebar" aria-label="Setup and source notes"><section class="side-section"><h2>What you’ll need</h2><p>{E(item['inputs'])}</p></section><section class="side-section"><h2>How to try it</h2><p style="font-size:11px;margin-bottom:15px">Suggested workflow from Leadde Open Lab.</p><ol>{''.join('<li>'+E(s)+'</li>' for s in item['steps'])}</ol></section><section class="side-section"><h2>About this example</h2><div class="meta-row"><span>Creator</span><span>@{E(item['author'])}</span></div><div class="meta-row"><span>Source model</span><span>{E(item['model'])}</span></div><div class="meta-row"><span>Published</span><span>{item['published']}</span></div><div class="meta-row"><span>Our reproduction</span><span>Not tested</span></div><div class="note"><strong>A note before you start</strong><p>{E(item['note'])}</p></div></section></aside></div><section class="related"><div class="kicker">Keep exploring</div><h2>More {cat['name'].lower()}.</h2><div class="grid">{''.join(card(x,'../../') for x in related)}</div></section></div>'''
    write(path+'index.html',document(item.get('seo_title', item['title']+' — Claude prompt'),item['description']+' Copy the shared prompt and read setup notes.',body,path,item['id']))
    pages.append((path,item['modified']))
pages.append((build_orbit(ROOT, OUT, BASE, document), None))
# The build date is not a content-modification date. Omit lastmod rather than invent one.
write('sitemap.xml','<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{E(BASE+p)}</loc></url>\n' for p,_ in pages)+'</urlset>\n')
# Supported alternative for one-off Search Console submission troubleshooting.
# Keep both formats on the same page list; neither format guarantees crawling.
write('sitemap.txt', ''.join(BASE + path + '\n' for path, _ in pages))
write('.nojekyll','')
not_found='<div class="wrap"><section class="page-head"><div class="eyebrow">404</div><h1>This page has moved<br>out of frame.</h1><p>Return to the collection to find a prompt for your next project.</p><div class="actions"><a class="button" href="'+E(BASE)+'">Back to the collection →</a></div></section></div>'
# Absolute asset URLs let GitHub Pages render the 404 at any missing path depth.
error=document('Page not found','Return to the Leadde Open Lab prompt collection.',not_found,noindex=True)
write('404.html',error.replace('href="./','href="'+E(BASE)).replace('src="./','src="'+E(BASE)))
print(f'Built {len(pages)} indexable pages in {OUT}')
print(f'Site URL: {BASE}')
print('Google verification: '+('HTML tag configured' if VERIFY else 'HTML verification file included' if list((SITE / 'public').glob('google*.html')) else 'not configured'))
