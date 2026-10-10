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
def relative_time(value):
    if not value:
        return 'UPDATE PENDING'
    then = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if then.tzinfo is None:
        then = then.replace(tzinfo=timezone.utc)
    hours = max(0, int((datetime.now(timezone.utc) - then).total_seconds() // 3600))
    if hours == 0:
        return 'NOW'
    return f'{hours} HOUR{"S" if hours != 1 else ""} AGO'

added = int(update.get('added', 0))
addition_date = str(update.get('date', ''))
history = json.loads(os.environ.get('BANNER_UPDATES', '[]'))
if os.environ.get('GITHUB_TOKEN'):
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
timeline = ''
for i, item in enumerate(reversed(history)):
    x = 88 + i * 450
    timeline += f'<circle cx="{x}" cy="474" r="7" fill="#bef264"/><text x="{x}" y="511" fill="#aab5cb" font-size="18">{escape(relative_time(item["date"]))}</text><text x="{x}" y="548" fill="#fff" font-size="28" font-weight="700">+{int(item["added"])} updated</text>'
# Editorial headline requested by the maintainer; not an inventory calculation.
headline = '2000+'
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="640" viewBox="0 0 1440 640" role="img" aria-labelledby="title desc">
<title id="title">{headline} prompts · Opus 5.5 creative library</title>
<desc id="desc">Videos, animation, 3D and interactive demos. Latest batch update: +{added} · {escape(relative_time(addition_date))}. Refreshed with each content update.</desc>
<defs>
 <linearGradient id="bg" x2="1" y2="1"><stop stop-color="#101a32"/><stop offset="1" stop-color="#090b12"/></linearGradient>
 <linearGradient id="accent"><stop stop-color="#bef264"/><stop offset="1" stop-color="#5eead4"/></linearGradient>
 <pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse"><path d="M48 0H0V48" fill="none" stroke="#fff" stroke-opacity=".035"/></pattern>
</defs>
<rect width="1440" height="640" rx="24" fill="url(#bg)"/>
<rect width="1440" height="640" rx="24" fill="url(#grid)"/>
<g font-family="Arial, Helvetica, sans-serif">
 <text x="64" y="66" fill="#aab5cb" font-size="17" letter-spacing="4">LEADDE OPEN LAB / THE CREATIVE PROMPT COLLECTION</text>
 <rect x="1168" y="36" width="208" height="42" rx="21" fill="#bef264" fill-opacity=".1" stroke="#bef264" stroke-opacity=".3"/>
 <circle cx="1192" cy="57" r="5" fill="#bef264"/>
 <text x="1210" y="63" fill="#bef264" font-size="15" font-weight="700">ACTIVELY UPDATED</text>
 <text x="54" y="293" fill="url(#accent)" font-size="226" font-weight="800" letter-spacing="-12">{headline}</text>
 <text x="66" y="356" fill="#f5f7fc" font-size="38" font-weight="700" letter-spacing="10">PROMPTS</text>
 <path d="M835 130V372" stroke="#fff" stroke-opacity=".14"/>
 <text x="893" y="159" fill="#bef264" font-size="20" font-weight="700" letter-spacing="3">THE COLLECTION KEEPS GROWING</text>
 <text x="887" y="266" fill="#fff" font-size="104" font-weight="800">+{added}</text>
 <text x="893" y="309" fill="#fff" font-size="27" font-weight="700">PROMPTS IN THE LATEST BATCH</text>
 <text x="893" y="352" fill="#aab5cb" font-size="22">UPDATED {escape(relative_time(addition_date))}</text>
 <text x="64" y="412" fill="#aab5cb" font-size="19">OPUS 5.5 · VIDEO / ANIMATION / 3D / INTERACTIVE</text>
 <path d="M88 474H1298" stroke="#bef264" stroke-opacity=".4" stroke-width="2"/>
 {timeline}
 <text x="1376" y="607" text-anchor="end" fill="#aab5cb" font-size="15">UPDATED WITH EVERY NEW DROP · ORIGINAL CREATOR SOURCES</text>
</g>
</svg>
'''
target = root / 'data/banner.svg'
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(svg)
print(f'Updated {target.relative_to(root)}')
