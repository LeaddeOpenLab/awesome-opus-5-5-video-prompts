"""Add source-grounded prompt tips without rebuilding existing Markdown layouts."""
import json
import re
from collections import Counter
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
START = '<!-- pro-tip:start -->'
END = '<!-- pro-tip:end -->'
# Each match quotes an actual instruction; explanations describe intent, not proven results.
RULES = [
    (r'imageSmoothingEnabled\s*=\s*false', 'Disable canvas interpolation and use integer scaling to preserve crisp pixel edges.'),
    (r'One shape, never cut', 'Connect states by continuously transforming one shape, rather than cutting between unrelated slides.'),
    (r'(?:last frame is the first frame|first and last frames? (?:must )?match|seamless(?:ly)? loop(?:ing)?|perfect(?:ly)? loop(?:ing)?)', 'Make the loop boundary explicit; check position, velocity and lighting at both ends.'),
    (r'(?:fixed|locked|static|stationary) camera|camera (?:is |must (?:stay|remain) )?(?:fixed|locked|static)', 'Lock the camera to reduce framing drift and make subject motion easier to inspect.'),
    (r'One idea per shot', 'Give each shot one idea so text, visuals and motion reinforce the same message.'),
    (r'No external assets, libraries, or network requests|no external (?:assets|dependencies|libraries)', 'Exclude external dependencies to reduce failures caused by missing assets, libraries or network requests.'),
    (r'(?:single|one)[ -](?:self-contained )?HTML file|single-file HTML|self-contained HTML', 'Specify one HTML deliverable for easy browser playback; still check whether the implementation loads external dependencies.'),
    (r'(?:no|without) (?:text|subtitles|watermarks|UI|interactivity)\b', 'Use explicit exclusions to prevent unwanted text, UI or interactions.'),
    (r'(?:actual|real) product (?:screenshot[s]?[/a-z]*|assets)|real footage only', 'Require real product assets instead of placeholder cards or invented interfaces; provide the assets before starting.'),
    (r'(?:motion must match the music|sync(?:ed|hronized)? (?:to|with) (?:the )?(?:beat|music)|on the beats|beat-driven|\d+ BPM)', 'Connect motion to musical beats; establish the soundtrack and timeline before placing key actions.'),
    (r'(?:fixed|stable) \d+\s*(?:hz|fps)|fixed timestep|zero object allocation|allocation-free', 'Specify update timing or allocation constraints to reduce stutter; verify performance by running the result.'),
    (r'\b(?:XPBD|PBD|Navier.Stokes|spring.mass|soft.body physics|rigid.body physics)\b', 'Name the physics model or simulation type, then check parameters, stability and interaction response.'),
    (r'(?:state machine|IDLE[^\n]{0,70}CHARGE)', 'Organize motion into states and transitions so each phase can be checked independently.'),
    (r'(?:source for each fact|confidence level|dimension markings|to scale from the plan)', 'Make sources, confidence or dimensions explicit so the result can be compared with references.'),
    (r'(?:before animating|before modeling|build, render, inspect, and refine|render and inspect|compare[^\n.]{0,65}screenshot)', 'Specify production order and inspection checkpoints instead of jumping straight to delivery.'),
    (r'(?:ask me for|ask the user for|before starting, ask)', 'Request essential inputs first rather than guessing the brand, assets or content.'),
    (r'(?:one|single) (?:accent color|continuous take|unbroken shot)|continuous single shot', 'Limit visual variables or editing choices to keep style and shot transitions consistent.'),
    (r'(?:use|with) edge-tts|\bedge-tts\b', 'Specify the speech tool as part of delivery, then check narration speed against animation duration.'),
    (r'(?:scroll.scrubbed|scroll.progress|video\.currentTime|scroll.driven)', 'Map visual state to scroll position and check consistency when scrolling in either direction.'),
    (r'(?:undo/redo|undo and redo|save locally|localStorage)', 'Include state restoration or local saving so the result remains editable after the initial demo.'),
    (r'(?:mouse/touch|mouse and touch|touch and mouse|arrow keys|WASD|one-thumb touch controls)', 'Specify input methods and verify their response on the intended devices.'),
    (r'(?:9:16|16:9|540x960|1920[×x]1080|1080[×x]1920)', 'Set aspect ratio or resolution before composing the scene to avoid cropping after export.'),
    (r'(?:\d+(?:[–-]\d+)?[ -]second|\d+[ -]minute|\d+s)\s+(?:animated |motion.graphics |explainer |3D |2D )?(?:video|animation|ad|film|trailer)', 'Set a duration budget, then allocate shots and motion to fit it.'),
    (r'(?:readable|legible) (?:text|typography|labels)|large (?:text|labels)', 'Make readability explicit; check type size, contrast and hold time at the actual playback size.'),
    (r'(?:limited|fixed) (?:color )?palette|\d+[ -]color palette', 'Limit the palette to keep visual elements consistent.'),
    (r'(?:squash and stretch|anticipation|overshoot|spring animation|spring physics)', 'Describe concrete animation principles, then control their amplitude and timing.'),
    (r'(?:infinite zoom|camera orbit|orbiting camera|fly.through|first.person walkthrough)', 'Specify the camera or navigation path and check turning and movement speed.'),
    (r'(?:empty glass to completed cocktail|step.by.step|from start to finish)', 'Define a complete sequence with a beginning, intermediate steps and an ending.'),
    (r'\b(?:Manim|Remotion|Blender(?: Python)?|Three\.?js|WebGPU|WGSL|Canvas 2D|WebGL|FFmpeg|HyperFrames|Raylib-cs)\b', 'Name the implementation or rendering tool and prepare its environment; a tool name alone is not a complete workflow.'),
    (r'(?:pixel.art|pixel art|16.bit|8.bit)', 'Specify the pixel-art style, then add logical resolution, palette and scaling requirements.'),
    (r'(?:paper.cutout|stop.motion|hand.drawn|watercolor|vaporwave|Grand Budapest Hotel)', 'Use a recognizable visual reference, then specify palette, materials and motion beyond the style label.'),
    (r'(?:multiplayer|1-on-1|turn.based|card game|platformer|racing game)', 'Define the game type or participation model, then add controls, rules and win/loss conditions.'),
    (r'(?:educational|explaining|explainer|visualization|visualisation)', 'State the teaching or visualization purpose, then add audience, key conclusions and examples; verify facts and data.'),
    (r'(?:product|launch|promo|commercial|advertisement|ad video)', 'Provide product assets, one key selling point and a closing action for a focused commercial presentation.'),
    (r'(?:simulation|simulate|physics|fluid|gravity|particle)', 'Define the simulated phenomenon, then add motion rules, parameters and interaction beyond its appearance.'),
    (r'(?:interactive|playable|drag|click|shake)', 'Specify how user input changes state so the result is interactive rather than merely viewable.'),
    (r'(?:history|documentary|news|explain|explanatory|theorem|data cent(?:er|re))', 'Identify the teaching or research subject, then supply sources, audience and key conclusions before scripting.'),
    (r'(?:music video|song|sound track|soundtrack|lyrics|beat|chords)', 'Provide the soundtrack and specify how beats or lyrics map to visual events.'),
    (r'(?:reference|image|photo|mock.?ups?|this design|this floor plan)', 'Supply the reference image or file and state which proportions, colors and structures must stay intact.'),
    (r'(?:voice over|narrat(?:e|or)|spoken word)', 'Specify the script, speaking rate and synchronization method for narration or dialogue.'),
    (r'(?:3[Dd]|CAD|modeling|modelling|isometric)', 'Add dimensions, camera views and materials to the spatial brief to reduce guesswork.'),
    (r'(?:game|simulator|Minecraft|Zelda|Tetris|Tron|shooter|Hades|Mario)', 'Define core controls, objectives and failure conditions beyond the visual game reference.'),
    (r'(?:running|runs|walking|danc(?:e|es|ing)|landing|chasing|shaking|hatching|moving)', 'Break the requested action into key poses, contact points and speeds; check continuity.'),
    (r'(?:rain|pond|swamp|river|sea|water|lava|volcano|fireworks)', 'Turn the environment into an actionable scene brief with movement direction, density and lighting.'),
    (r'(?:UI|menu|dashboard|screen|web app|website)', 'Specify content hierarchy, state changes and real data for the interface rather than static decoration.'),
    (r'(?:video|film|movie|trailer|showreel|edit|presentation|PV)', 'Add duration, aspect ratio, assets and delivery format to the short production brief.'),
    (r'(?:looping|loop|animated|animation|motion)', 'Define motion phases, speed and the end state so the output changes over time rather than remaining a still scene.'),
]
RULES = [(re.compile(r'(?<!\w)(?:' + pattern + r')(?!\w)', re.I), insight) for pattern, insight in RULES]


def clean(value):
    return ' '.join(value.split())


def prompt_for(record):
    evidence = record.get('analysis', {}).get('caseEvidence', {})
    return (record.get('promptTranslations', {}).get('en')
            or evidence.get('prompt', {}).get('englishText') or record.get('prompt', ''))


def make_tip(prompt, override=None):
    source = clean(prompt)
    if override and clean(override['quote']) in source:
        return {**override, 'kind': 'editorial'}
    if not source:
        return {'quote': '', 'insight': 'No public prompt is available to quote. Check the original creator source rather than reconstructing unpublished instructions from the result.', 'kind': 'missing'}
    if re.match(r'^/[\w-]+(?:\s|$)', source):
        return {'quote': source.split()[0], 'insight': 'This is a workflow command whose behavior depends on its supporting skill and project context; obtain that workflow definition before reuse.', 'kind': 'command'}
    for index, (pattern, insight) in enumerate(RULES):
        match = pattern.search(source)
        if match:
            quote = source if index >= 28 and len(source) <= 150 else match.group(0)
            return {'quote': quote, 'insight': insight, 'kind': 'constraint'}
    # A short public fragment cannot support an invented explanation of success.
    words = source.split()
    excerpt = ' '.join(words[:16])
    if len(excerpt) > 110:
        excerpt = excerpt[:110].rsplit(' ', 1)[0] or excerpt[:110]
    return {'quote': excerpt, 'insight': 'The public fragment gives a creative direction only; add subject motion, visual constraints and delivery format without assuming the full production process.', 'kind': 'fragment'}


def detail_tip(tip):
    quote = '<code>' + escape(tip['quote']) + '</code>: ' if tip['quote'] and not re.search(r'[\u4e00-\u9fff]', tip['quote']) else ''
    return f'{START}\n> [!TIP]\n> **💡 Pro Tip** — {quote}{escape(tip["insight"])}\n{END}\n\n'


def card_tip(tip):
    quote = '<code>' + escape(tip['quote']) + '</code>: ' if tip['quote'] and not re.search(r'[\u4e00-\u9fff]', tip['quote']) else ''
    return f'{START}\n<blockquote><strong>💡 Pro Tip</strong><br>{quote}{escape(tip["insight"])}</blockquote>\n{END}\n'


def strip_tips(content):
    return re.sub(re.escape(START) + r'.*?' + re.escape(END) + r'\n(?:\n)?', '', content, flags=re.S)


def render_detail(content, tip):
    original = strip_tips(content)
    return re.sub(r'(?m)^## Prompt ', lambda m: detail_tip(tip) + m.group(0), original, count=1)


def render_gallery(content, tips):
    original = strip_tips(content)
    def add(match):
        card = match.group(0)
        if card.startswith('## Featured creations'):
            return card
        ids = re.findall(r'(?:prompts/|gifs/|covers/)(\d+)', card)
        tip = next((tips[id] for id in ids if id in tips), None)
        return card.replace('</td>', card_tip(tip) + '</td>') if tip else card
    return re.sub(r'^## Featured creations\n.*?(?=^## |\Z)|<td\b[^>]*>.*?</td>', add, original, flags=re.S | re.M)


def main():
    overrides = json.loads((ROOT / 'data/pro-tip-overrides.json').read_text())
    tips = {}
    for path in sorted((ROOT / 'data/library').glob('*.json')):
        record = json.loads(path.read_text())
        tips[path.stem] = make_tip(prompt_for(record), overrides.get(path.stem))
    changed = 0
    for path in sorted((ROOT / 'prompts').glob('*.md')):
        if path.stem not in tips:
            continue
        original = path.read_text()
        updated = render_detail(original, tips[path.stem])
        if updated != original:
            path.write_text(updated)
            changed += 1
    for path in [ROOT / 'README.md', *sorted((ROOT / 'data/categories').glob('*.md'))]:
        original = path.read_text()
        updated = render_gallery(original, tips)
        if updated != original:
            path.write_text(updated)
            changed += 1
    print(f'Pro Tips: {len(tips)} cases; {changed} Markdown files updated; {dict(Counter(t["kind"] for t in tips.values()))}')


if __name__ == '__main__':
    main()
