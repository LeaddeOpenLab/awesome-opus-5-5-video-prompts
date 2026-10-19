"""Refresh the README banner after new content is published."""
import json
import os
import re
import urllib.request
from datetime import datetime, timezone
from html import escape
from pathlib import Path

root = Path(__file__).resolve().parents[2]
update_file = root / 'data/latest-update.json'
update = json.loads(update_file.read_text()) if update_file.exists() else {}
def update_date(value):
    if not value:
        return 'DATE PENDING'
    then = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if then.tzinfo is None:
        then = then.replace(tzinfo=timezone.utc)
    return then.astimezone(timezone.utc).strftime('%d %b %Y · %H:%M UTC').upper()

added = int(update.get('added', 0))
addition_date = str(update.get('date', ''))
# Published batch metadata is authoritative, including editorial withdrawals.
history = [{'date': item['date'], 'added': item['published']}
           for item in update.get('history', [])]
if not history:
    history = json.loads(os.environ.get('BANNER_UPDATES', '[]'))
if not history and os.environ.get('GITHUB_TOKEN'):
    repo = os.environ['GITHUB_REPOSITORY']
    req = urllib.request.Request(
        f'https://api.github.com/repos/{repo}/commits?path=data%2Flibrary&per_page=30',
        headers={'Authorization': 'Bearer ' + os.environ['GITHUB_TOKEN'],
                 'Accept': 'application/vnd.github+json', 'User-Agent': 'readme-banner'})
    with urllib.request.urlopen(req) as response:
        commits = json.load(response)
    history = []
    for commit in commits:
        match = re.match(r'^Add ([1-9]\d*) prompts?(?: ·|$)', commit['commit']['message'].splitlines()[0])
        if match:
            batch_count = 0
            page = 1
            while True:
                detail_req = urllib.request.Request(
                    f'https://api.github.com/repos/{repo}/commits/{commit["sha"]}?per_page=100&page={page}',
                    headers=req.headers)
                with urllib.request.urlopen(detail_req) as response:
                    files = json.load(response).get('files', [])
                batch_count += sum(1 for file in files
                    if re.fullmatch(r'data/library/[^/]+\.json', file['filename'])
                    and file['status'] in ('added', 'modified'))
                if len(files) < 100:
                    break
                page += 1
            history.append({'date': commit['commit']['committer']['date'], 'added': batch_count})
        if len(history) == 3:
            break
if history:
    added, addition_date = history[0]['added'], history[0]['date']
else:
    history = [{'date': addition_date, 'added': added}]
# Keep the collection headline while leaving room for featured work above the fold.
headline = '2000+'
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="200" viewBox="0 0 1440 200" role="img" aria-labelledby="title desc">
<title id="title">{headline} prompts · Actively updated · Leadde Open Lab</title>
<desc id="desc">Video prompts and creator previews. Latest batch: {added} prompts updated on {escape(update_date(addition_date))}.</desc>
<rect x="1" y="1" width="1438" height="198" rx="18" fill="#FAF9FF" stroke="#E6E1F3"/>
<g font-family="Arial, Helvetica, sans-serif">
<text x="48" y="51" fill="#241C35" font-size="25" font-weight="700">Leadde <tspan font-weight="400" fill="#756C84">/ Open Lab</tspan></text>
<text x="48" y="111" fill="#6E4DFC" font-size="42" font-weight="700">{headline} video prompts</text>
<text x="48" y="157" fill="#655D72" font-size="23">Motion graphics · Explainers · 3D · Interactive</text>
<rect x="1116" y="26" width="276" height="40" rx="20" fill="#EEE8FF"/>
<circle cx="1140" cy="46" r="5" fill="#6E4DFC"/>
<text x="1158" y="53" fill="#6E4DFC" font-size="18" font-weight="700">ACTIVELY UPDATED</text>
<text x="1392" y="113" text-anchor="end" fill="#241C35" font-size="26" font-weight="700">+{added} prompts updated</text>
<text x="1392" y="157" text-anchor="end" fill="#655D72" font-size="20">{escape(update_date(addition_date))}</text>
</g>
</svg>
'''
target = root / 'data/banner.svg'
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(svg)
print(f'Updated {target.relative_to(root)}')

# Each content batch gets a new image URL, avoiding stale raw-image caches.
stamp = datetime.fromisoformat(addition_date.replace('Z', '+00:00')).strftime('%Y%m%d-%H%M%S') if addition_date else 'pending'
versioned = root / f'data/banner-{stamp}-compact.svg'
versioned.write_text(svg)
readme = root / 'README.md'
readme.write_text(re.sub(r'\]\(data/banner[^)]*\)', f']({versioned.relative_to(root)})', readme.read_text()))
