"""Generate terminal panels using established public profile details."""
from build_profile import ROOT, panel, text, GREEN, MUTED, FG


def save(name, width, height, title, content):
    (ROOT / 'assets' / name).write_text(panel(width, height, title, content))


def build():
    content = text(30, 83, 'HELLO, WORLD. I’M ROHAIL.', GREEN, 13)
    content += text(30, 128, 'From interface to API.', FG, 34)
    content += text(30, 160, 'Full-stack developer · Islamabad, Pakistan', MUTED, 15)
    content += text(30, 194, 'Web applications / RAG / algorithms', GREEN, 13)
    content += '<g class="reveal" style="animation-delay:.4s"><path d="M742 85l-22 24 22 24m45-48 22 24-22 24m-17-51-14 56" fill="none" stroke="#56d364" stroke-width="3" stroke-linecap="round"/></g>'
    save('header.svg', 860, 220, 'rohail.dev / welcome', content)
    content = ''
    groups = [
        ('01 / LANGUAGES', 'Python · TypeScript · JavaScript', 'C++ · HTML · CSS'),
        ('02 / BACKEND & DATA', 'FastAPI · PostgreSQL · Qdrant', 'Retrieval-augmented generation'),
        ('03 / TOOLS & FOUNDATIONS', 'Git · Cisco Packet Tracer', 'Algorithms · Networking'),
    ]
    for i, (label, first, second) in enumerate(groups):
        y = 76 + i * 86
        content += f'<g class="reveal" style="animation-delay:{i*.15}s">'
        content += text(28, y, label, GREEN, 11)
        content += text(28, y+26, first, FG, 17)
        content += text(28, y+48, second, MUTED, 13) + '</g>'
    save('stack.svg', 860, 316, './stack --list', content)
    projects = [
        ('project-rag.svg', '01 / AI & BACKEND', 'podcast-rag-api', ['A retrieval-augmented API', 'for podcast transcripts.'], 'Python / FastAPI / Qdrant'),
        ('project-events.svg', '02 / WEB DEVELOPMENT', 'dev-events', ['A hub for discovering', 'developer events.'], 'TypeScript / Web'),
        ('project-algorithms.svg', '03 / PROBLEM SOLVING', 'Leetcode-solutions', ['Algorithm practice with a focus', 'on efficiency and clarity.'], 'C++ / Data structures'),
        ('project-creative.svg', '04 / CREATIVE WORK', 'VideoEditing-Portfolio', ['A portfolio showcasing', 'video editing samples.'], 'HTML / Video editing'),
    ]
    for filename, category, title, lines, tags in projects:
        content = text(22, 72, category, GREEN, 10) + text(22, 103, title, FG, 19)
        content += text(22, 137, lines[0], MUTED, 13) + text(22, 158, lines[1], MUTED, 13)
        content += text(22, 198, tags, GREEN, 11) + text(22, 227, 'Explore repository →', MUTED, 11)
        save(filename, 424, 246, '~/projects', content)
    content = text(28, 83, 'Let’s talk code, projects, and ideas.', FG, 23)
    content += text(28, 115, 'Find me on GitHub or LinkedIn, or send an email below.', MUTED, 13)
    content += text(28, 149, 'rohail@github ~ $ _', GREEN, 13)
    save('connect.svg', 860, 176, './connect', content)


if __name__ == '__main__':
    build()
