"""Restore the approved template section after the collector rebuilds README."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
START = '<!-- runnable-templates:start -->'
END = '<!-- runnable-templates:end -->'


def with_template_cards(content, cards):
    section = cards.strip() + '\n\n'
    pattern = re.escape(START) + r'.*?' + re.escape(END) + r'\n*'
    content = re.sub(pattern, '', content, count=1, flags=re.S)
    return content.replace('## Start here\n', section + '## Start here\n', 1)


if __name__ == '__main__':
    path = ROOT / 'README.md'
    current = path.read_text()
    updated = with_template_cards(current, (ROOT / '.github/readme-template-cards.md').read_text())
    if updated != current:
        path.write_text(updated)
        print('Restored runnable template cards; existing content preserved.')
