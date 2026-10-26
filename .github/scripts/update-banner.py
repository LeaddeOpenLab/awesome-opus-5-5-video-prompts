"""Refresh the README banner after new content is published."""
import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
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

addition_date = str(update.get('date', ''))
# Count the actual library, and all additions on the latest publication day (UTC).
# Git history avoids the three-batch limit in latest-update.json and excludes edits.
headline = str(len(list((root / 'data/library').glob('*.json'))))
added = 0
addition_label = 'No additions yet'
if addition_date:
    day = datetime.fromisoformat(addition_date.replace('Z', '+00:00')).astimezone(timezone.utc)
    start = day.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    log = subprocess.check_output([
        'git', 'log', '--first-parent', '--format=%cI', '--name-only', '--diff-filter=A',
        f'--since={start.isoformat()}', f'--until={end.isoformat()}',
        '--', 'data/library/*.json',
    ], cwd=root, text=True)
    paths = set()
    in_day = False
    for line in log.splitlines():
        if not line:
            continue
        if line.startswith('data/library/'):
            if in_day:
                paths.add(line)
        else:
            committed = datetime.fromisoformat(line.replace('Z', '+00:00'))
            in_day = start <= committed < end
    added = len(paths)
    # An explicit date stays accurate when the static banner is viewed tomorrow.
    addition_label = f'+{added} added on {day.strftime("%d %b").upper()}'
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="200" viewBox="0 0 1440 200" role="img" aria-labelledby="title desc">
<title id="title">{headline} prompts · Actively updated · Leadde Open Lab</title>
<desc id="desc">Video prompts and creator previews. Daily additions: {added} prompts added on {escape(update_date(addition_date))}.</desc>
<rect x="1" y="1" width="1438" height="198" rx="18" fill="#FAF9FF" stroke="#E6E1F3"/>
<g font-family="Arial, Helvetica, sans-serif">
<text x="48" y="51" fill="#241C35" font-size="25" font-weight="700">Leadde <tspan font-weight="400" fill="#756C84">/ Open Lab</tspan></text>
<text x="48" y="111" fill="#6E4DFC" font-size="42" font-weight="700">{headline} video prompts</text>
<text x="48" y="157" fill="#655D72" font-size="23">Motion graphics · Explainers · 3D · Interactive</text>
<rect x="1116" y="26" width="276" height="40" rx="20" fill="#EEE8FF"/>
<circle cx="1140" cy="46" r="5" fill="#6E4DFC"/>
<text x="1158" y="53" fill="#6E4DFC" font-size="18" font-weight="700">ACTIVELY UPDATED</text>
<text x="1392" y="113" text-anchor="end" fill="#241C35" font-size="26" font-weight="700">{addition_label}</text>
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
versioned = root / f'data/banner-{stamp}-daily.svg'
versioned.write_text(svg)
readme = root / 'README.md'
readme.write_text(re.sub(r'\]\(data/banner[^)]*\)', f']({versioned.relative_to(root)})', re.sub(r'!\[[^\]]*(?=\]\(data/banner)', f'![{headline} prompts · Actively updated · Leadde Open Lab. Explore the web collection.', readme.read_text())))
