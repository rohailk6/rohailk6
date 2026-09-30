"""Generate standalone animated SVGs. Daily graph updates use only Python stdlib."""
import argparse
from datetime import date, timedelta
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PROFILE = json.loads((ROOT / 'profile.json').read_text())
BG, FG, MUTED, GREEN = '#0d1117', '#e6edf3', '#8b949e', '#56d364'


def text(x, y, value, color=FG, size=14):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}">{escape(str(value))}</text>'


def panel(width, height, title, content):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">
<title>{escape(title)}</title>
<style>text{{font-family:ui-monospace,Menlo,Consolas,monospace}} .reveal{{animation:reveal .65s both}} @keyframes reveal{{from{{opacity:0;transform:translateY(5px)}}to{{opacity:1;transform:translateY(0)}}}} @media(prefers-reduced-motion:reduce){{.reveal{{animation:none}}}}</style>
<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="12" fill="{BG}" stroke="#30363d"/>
<path d="M1 40H{width-1}" stroke="#30363d"/>
<circle cx="19" cy="20" r="4" fill="#ff5f57"/><circle cx="34" cy="20" r="4" fill="#febc2e"/><circle cx="49" cy="20" r="4" fill="#28c840"/>
{text(68,24,title,MUTED,11)}{content}</svg>'''


class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells, self.tips = {}, {}
        self.tip = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('data-date') and 'data-level' in a:
            self.cells[a['id']] = {'date': a['data-date'], 'level': int(a['data-level'])}
        if tag == 'tool-tip':
            self.tip = a.get('for')
            if self.tip:
                self.tips[self.tip] = ''

    def handle_data(self, value):
        if self.tip:
            self.tips[self.tip] += value

    def handle_endtag(self, tag):
        if tag == 'tool-tip':
            self.tip = None

    def days(self):
        days = []
        for key, cell in self.cells.items():
            label = self.tips.get(key, '').strip()
            match = re.match(r'(No|[\d,]+) contributions? on ', label)
            if not match or not 0 <= cell['level'] <= 4:
                raise ValueError(f'Unrecognized contribution cell: {cell["date"]}')
            count = 0 if match[1] == 'No' else int(match[1].replace(',', ''))
            days.append({**cell, 'count': count})
        days.sort(key=lambda d: d['date'])
        if not 350 <= len(days) <= 371:
            raise ValueError(f'Unexpected calendar length: {len(days)}; retaining old files')
        dates = [date.fromisoformat(d['date']) for d in days]
        if any(b - a != timedelta(days=1) for a, b in zip(dates, dates[1:])):
            raise ValueError('Calendar has duplicate or missing days')
        return days


def heatmap(html_path=None):
    if html_path:
        source = Path(html_path).read_text()
    else:
        req = Request(f'https://github.com/users/{PROFILE["username"]}/contributions', headers={'User-Agent': 'profile-art-generator', 'Accept-Language': 'en-US'})
        with urlopen(req, timeout=45) as response:
            source = response.read().decode()
    parser = Calendar()
    parser.feed(source)
    days = parser.days()
    first = date.fromisoformat(days[0]['date'])
    start = first - timedelta(days=(first.weekday() + 1) % 7)
    palette = ['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353']
    content = text(28, 73, 'A year of building', FG, 18)
    content += text(28, 95, f'{days[0]["date"]} — {days[-1]["date"]}', MUTED, 11)
    last_month = None
    for day in days:
        d = date.fromisoformat(day['date'])
        column, row = (d - start).days // 7, (d.weekday() + 1) % 7
        x, y = 45 + column * 14.5, 131 + row * 16
        if d.month != last_month and (d.day <= 7 or last_month is None):
            content += text(x, 120, d.strftime('%b'), MUTED, 10)
            last_month = d.month
        label = escape(f'{day["date"]}: {day["count"]} contributions')
        content += f'<rect class="reveal" style="animation-delay:{(column+row)*.018:.3f}s" x="{x}" y="{y}" width="11" height="12" rx="2" fill="{palette[day["level"]]}"><title>{label}</title></rect>'
    for row, label in [(1, 'M'), (3, 'W'), (5, 'F')]:
        content += text(25, 141 + row * 16, label, MUTED, 10)
    total = sum(d['count'] for d in days)
    active = sum(d['count'] > 0 for d in days)
    content += text(28, 274, f'{total:,} contributions / {active} active days', GREEN, 13)
    content += text(654, 273, 'Less', MUTED, 10)
    for i, color in enumerate(palette):
        content += f'<rect x="{686+i*16}" y="263" width="12" height="12" rx="2" fill="{color}"/>'
    content += text(770, 273, 'More', MUTED, 10)
    svg = panel(860, 298, './contributions.sh', content)
    (ROOT / 'data/contributions.json').write_text(json.dumps({'username': PROFILE['username'], 'days': days}, indent=2) + '\n')
    (ROOT / 'contrib-heatmap.svg').write_text(svg)
    print(f'Contribution graph: {len(days)} days, {total} contributions')


def card():
    content = text(25, 83, PROFILE['name'], GREEN, 25)
    content += text(25, 110, '@' + PROFILE['username'], MUTED, 13)
    rows = [('Role', 'role'), ('Based', 'location'), ('Stack', 'stack'), ('Build', 'building'), ('Repo', 'project'), ('Explore', 'interests')]
    for i, (label, key) in enumerate(rows):
        y = 153 + i * 33
        content += f'<g class="reveal" style="animation-delay:{i*.13:.2f}s">{text(25,y,label,GREEN,12)}{text(105,y,PROFILE[key],FG,12)}</g>'
    content += text(25, 362, '$ ship · learn · repeat', MUTED, 12)
    (ROOT / 'info-card.svg').write_text(panel(490, 390, 'rohail@github: ~ / whoami', content))


def portrait():
    from PIL import Image, ImageOps, ImageFilter
    original = ImageOps.exif_transpose(Image.open(ROOT / 'assets/portrait-source.png')).convert('RGBA')
    alpha = original.getchannel('A')
    source = ImageOps.autocontrast(original.convert('L')).filter(ImageFilter.UnsharpMask(radius=2, percent=140))
    # Transparent pixels map to spaces; retain the entire supplied cutout.
    background = Image.new('L', source.size, 0)
    background.paste(source, mask=alpha)
    # Match the rendered text area's aspect before sampling the character grid.
    source = ImageOps.pad(background, (660, 602), color=0).resize((66, 43), Image.Resampling.LANCZOS)
    ramp = ' .,:;irsXA253hMHGS#9B&@'
    content = ''
    for row in range(43):
        line = ''.join(ramp[round(source.getpixel((col,row))/255*(len(ramp)-1))] for col in range(66))
        content += f'<text class="reveal" style="animation-delay:{row*.025:.3f}s" x="20" y="{65+row*7}" xml:space="preserve" fill="{FG}" font-size="8" textLength="330" lengthAdjust="spacingAndGlyphs">{escape(line)}</text>'
    content += text(20, 377, './portrait --ascii', MUTED, 10)
    (ROOT / 'portrait.svg').write_text(panel(370, 390, 'rohail / portrait', content))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--heatmap-only', action='store_true')
    ap.add_argument('--html', help='Use a downloaded GitHub calendar for offline builds')
    args = ap.parse_args()
    heatmap(args.html)
    if not args.heatmap_only:
        card()
        portrait()
