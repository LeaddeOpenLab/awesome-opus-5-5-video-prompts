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
    (r'imageSmoothingEnabled\s*=\s*false', '关闭画布插值，配合整数倍缩放保留像素硬边，避免缩放造成模糊。'),
    (r'One shape, never cut', '用同一个形状的连续变形连接状态，避免转场退化成互不相关的幻灯片。'),
    (r'(?:last frame is the first frame|first and last frames? (?:must )?match|seamless(?:ly)? loop(?:ing)?|perfect(?:ly)? loop(?:ing)?)', '把首尾衔接设为动画约束；复用时同时检查位置、速度和光照是否能连续循环。'),
    (r'(?:fixed|locked|static|stationary) camera|camera (?:is |must (?:stay|remain) )?(?:fixed|locked|static)', '明确固定镜头，减少构图漂移，让主体运动更容易观察和对比。'),
    (r'One idea per shot', '限制每个镜头的信息量，让文字、画面和动作围绕同一信息点展开。'),
    (r'No external assets, libraries, or network requests|no external (?:assets|dependencies|libraries)', '把外部依赖排除出实现范围，减少缺失素材、未安装库或网络请求导致的运行问题。'),
    (r'(?:single|one)[ -](?:self-contained )?HTML file|single-file HTML|self-contained HTML', '明确交付一个 HTML 文件，便于保存和在浏览器打开；仍需检查实际是否引入了外部依赖。'),
    (r'(?:no|without) (?:text|subtitles|watermarks|UI|interactivity)\b', '用明确的排除项限定输出范围，减少模型自行增加不需要的文字、界面或交互。'),
    (r'(?:actual|real) product (?:screenshot[s]?[/a-z]*|assets)|real footage only', '要求使用真实产品素材，减少占位卡片和凭空设计的界面；开始前要提供可用素材。'),
    (r'(?:motion must match the music|sync(?:ed|hronized)? (?:to|with) (?:the )?(?:beat|music)|on the beats|beat-driven|\d+ BPM)', '把动效节奏与音频拍点联系起来；复用时先确定音轨和时间轴，再安排关键动作。'),
    (r'(?:fixed|stable) \d+\s*(?:hz|fps)|fixed timestep|zero object allocation|allocation-free', '将更新节奏或内存分配写进实现要求，减少动画中的抖动风险；性能仍需实际运行检查。'),
    (r'\b(?:XPBD|PBD|Navier.Stokes|spring.mass|soft.body physics|rigid.body physics)\b', '点名物理模型或仿真类型，要求运动有计算依据；复用时检查参数、稳定性和交互响应。'),
    (r'(?:state machine|IDLE[^\n]{0,70}CHARGE)', '将动作组织为状态和转换，便于逐段检查，而不是只要求角色持续“动起来”。'),
    (r'(?:source for each fact|confidence level|dimension markings|to scale from the plan)', '把来源、可信度或尺寸作为约束，让结果能与参考资料逐项对照。'),
    (r'(?:before animating|before modeling|build, render, inspect, and refine|render and inspect|compare[^\n.]{0,65}screenshot)', '给制作过程设置先后顺序或检查环节，减少跳过研究、验证就直接交付的情况。'),
    (r'(?:ask me for|ask the user for|before starting, ask)', '先索取必要输入，再开始制作，减少模型擅自猜测品牌、素材和内容的情况。'),
    (r'(?:one|single) (?:accent color|continuous take|unbroken shot)|continuous single shot', '限制视觉变量或剪辑方式，为各段内容提供统一规则，减少风格与镜头的随机变化。'),
    (r'(?:use|with) edge-tts|\bedge-tts\b', '指定语音合成工具，让配音成为交付的一部分；复用时核对语速与动画时长。'),
    (r'(?:scroll.scrubbed|scroll.progress|video\.currentTime|scroll.driven)', '将视觉状态与滚动位置关联；复用时检查正向、反向滚动时画面是否一致。'),
    (r'(?:undo/redo|undo and redo|save locally|localStorage)', '把状态恢复或本地保存纳入功能要求，让交互结果可以继续编辑，而不是一次性演示。'),
    (r'(?:mouse/touch|mouse and touch|touch and mouse|arrow keys|WASD|one-thumb touch controls)', '明确输入方式，让可交互效果有具体操作入口；复用时检查对应设备上的响应。'),
    (r'(?:9:16|16:9|540x960|1920[×x]1080|1080[×x]1920)', '先规定画幅或分辨率，帮助构图适配目标发布场景，减少导出后再裁切。'),
    (r'(?:\d+(?:[–-]\d+)?[ -]second|\d+[ -]minute|\d+s)\s+(?:animated |motion.graphics |explainer |3D |2D )?(?:video|animation|ad|film|trailer)', '给成片设定时间边界，让内容和动作有明确预算；复用时按时长分配镜头和节奏。'),
    (r'(?:readable|legible) (?:text|typography|labels)|large (?:text|labels)', '把可读性明确列为约束；复用时在实际播放尺寸下检查字号、对比度和停留时长。'),
    (r'(?:limited|fixed) (?:color )?palette|\d+[ -]color palette', '限制调色板，减少不同元素各自使用颜色导致的风格混乱。'),
    (r'(?:squash and stretch|anticipation|overshoot|spring animation|spring physics)', '用具体运动原则描述质感，比笼统要求“更生动”更可执行；复用时控制幅度与节奏。'),
    (r'(?:infinite zoom|camera orbit|orbiting camera|fly.through|first.person walkthrough)', '明确镜头或浏览方式，使场景围绕实际观看路径组织；复用时检查转向和移动速度。'),
    (r'(?:empty glass to completed cocktail|step.by.step|from start to finish)', '要求完整的过程顺序，给内容建立起点、步骤和终点，便于检查遗漏。'),
    (r'\b(?:Manim|Remotion|Blender(?: Python)?|Three\.?js|WebGPU|WGSL|Canvas 2D|WebGL|FFmpeg|HyperFrames|Raylib-cs)\b', '点名实现或渲染工具，减少技术路线漂移；复用时准备相应环境，不能把工具名当作完整制作步骤。'),
    (r'(?:pixel.art|pixel art|16.bit|8.bit)', '用明确的像素风格限定视觉方向；复用时补充逻辑分辨率、调色板和缩放方式。'),
    (r'(?:paper.cutout|stop.motion|hand.drawn|watercolor|vaporwave|Grand Budapest Hotel)', '给出可辨认的视觉参考；复用时再明确配色、材质和运动方式，避免只停留在风格标签。'),
    (r'(?:multiplayer|1-on-1|turn.based|card game|platformer|racing game)', '先限定玩法类型或参与方式；复用时补齐操作、规则和胜负条件，才能从场景变成可玩的系统。'),
    (r'(?:educational|explaining|explainer|visualization|visualisation)', '明确讲解或可视化用途；复用时补充受众、关键结论和例子，并核对知识与数据。'),
    (r'(?:product|launch|promo|commercial|advertisement|ad video)', '明确商业展示用途；复用时提供产品素材、一个核心卖点和结束行动，减少空泛宣传镜头。'),
    (r'(?:simulation|simulate|physics|fluid|gravity|particle)', '把任务限定为可观察的模拟现象；复用时补充运动规则、参数和交互，避免只有相似外观。'),
    (r'(?:interactive|playable|drag|click|shake)', '把用户操作纳入目标；复用时明确操作触发什么状态变化，避免只得到可观看的静态场景。'),
    (r'(?:history|documentary|news|explain|explanatory|theorem|data cent(?:er|re))', '给出讲解或研究对象；公开片段未展开事实与脚本，复用时先补充来源、受众和关键结论。'),
    (r'(?:music video|song|sound track|soundtrack|lyrics|beat|chords)', '以歌曲或音乐作为创作依据；复用时提供可用音轨，并明确节拍、歌词与画面的对应关系。'),
    (r'(?:reference|image|photo|mock.?ups?|this design|this floor plan)', '将输入参考作为设计起点；复用时提供原图或文件，并说明哪些比例、颜色和结构必须保留。'),
    (r'(?:voice over|narrat(?:e|or)|spoken word)', '明确口播或旁白需求；复用时补充文稿、语速和音画对齐方式。'),
    (r'(?:3[Dd]|CAD|modeling|modelling|isometric)', '限定空间建模或三维展示方向；复用时补充尺寸、视角和材质，减少模型对空间细节的猜测。'),
    (r'(?:game|simulator|Minecraft|Zelda|Tetris|Tron|shooter|Hades|Mario)', '给出玩法或游戏参考；复用时明确核心操作、目标和失败条件，避免只复刻外观。'),
    (r'(?:running|runs|walking|danc(?:e|es|ing)|landing|chasing|shaking|hatching|moving)', '把主体动作写进要求；复用时拆分关键姿态、接触点和速度，检查运动是否连贯。'),
    (r'(?:rain|pond|swamp|river|sea|water|lava|volcano|fireworks)', '给出环境或自然现象作为视觉主题；复用时补充运动方向、密度和光照，形成可执行的场景要求。'),
    (r'(?:UI|menu|dashboard|screen|web app|website)', '明确界面展示的对象；复用时补充内容层级、状态变化和真实数据，避免只有静态装饰。'),
    (r'(?:video|film|movie|trailer|showreel|edit|presentation|PV)', '给出成片用途或形式；公开片段未展开制作约束，复用时补充时长、画幅、素材和交付格式。'),
    (r'(?:looping|loop|animated|animation|motion)', '明确需要时间变化；复用时补充动作阶段、速度和结束状态，避免只得到一张场景图。'),
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
        return {'quote': '', 'insight': '当前没有可引用的公开提示词；先查看原作者来源，不从成片倒推未公开的指令。', 'kind': 'missing'}
    if re.match(r'^/[\w-]+(?:\s|$)', source):
        return {'quote': source.split()[0], 'insight': '这是工作流命令，具体行为取决于配套技能与项目上下文；复用时先取得对应工作流定义。', 'kind': 'command'}
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
    return {'quote': excerpt, 'insight': '公开片段只给出创作方向；复用时补充主体动作、画面约束和交付格式，不能据此推断完整制作过程。', 'kind': 'fragment'}


def detail_tip(tip):
    quote = '<code>' + escape(tip['quote']) + '</code>：' if tip['quote'] else ''
    return f'{START}\n> [!TIP]\n> **💡 Pro Tip / 核心咒语** — {quote}{escape(tip["insight"])}\n{END}\n\n'


def card_tip(tip):
    quote = '<code>' + escape(tip['quote']) + '</code>：' if tip['quote'] else ''
    return f'{START}\n<blockquote><strong>💡 Pro Tip / 核心咒语</strong><br>{quote}{escape(tip["insight"])}</blockquote>\n{END}\n'


def strip_tips(content):
    return re.sub(re.escape(START) + r'.*?' + re.escape(END) + r'\n(?:\n)?', '', content, flags=re.S)


def render_detail(content, tip):
    original = strip_tips(content)
    return re.sub(r'(?m)^## Prompt ', lambda m: detail_tip(tip) + m.group(0), original, count=1)


def render_gallery(content, tips):
    original = strip_tips(content)
    def add(match):
        card = match.group(0)
        ids = re.findall(r'(?:prompts/|gifs/|covers/)(\d+)', card)
        tip = next((tips[id] for id in ids if id in tips), None)
        return card.replace('</td>', card_tip(tip) + '</td>') if tip else card
    return re.sub(r'<td\b[^>]*>.*?</td>', add, original, flags=re.S)


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
