# -*- coding: utf-8 -*-
"""VOL.15 构建脚本：index_template.html + _style_base.css → index.html（幂等）"""
import re

TPL = 'index_template.html'
CSS = '_style_base.css'
OUT = 'index.html'

base = open(CSS, encoding='utf-8').read()
# 换皮：谱系图主题（墨蓝主色 + 砖红辅色，延续 VOL.14 的砖红做系列连续性）
base = base.replace('--signal:#d96f1f', '--signal:#3e6e8e')
base = base.replace('rgba(217,111,31,.1)', 'rgba(62,110,142,.1)')
base = base.replace('--plum:#77588a', '--plum:#b5482a')
base = base.replace('rgba(119,88,138,.1)', 'rgba(181,72,42,.1)')
base = base.replace('#d96f1f', '#3e6e8e')

additions = '''
/* ---- VOL.15 小样专属 ---- */
.term{background:var(--code-bg);border-radius:8px;overflow:hidden;border:1px solid var(--line)}
.term-bar{display:flex;align-items:center;gap:6px;padding:7px 12px;background:rgba(255,255,255,.06);border-bottom:1px solid rgba(255,255,255,.08)}
.term-bar i{width:9px;height:9px;border-radius:50%;background:var(--line-strong);display:inline-block}
.term-bar i:first-child{background:#c75b5b}.term-bar i:nth-child(2){background:#c9a55b}.term-bar i:nth-child(3){background:#6fa876}
.term-bar span{margin-left:8px;font-family:var(--mono);font-size:11px;color:#9fb0a8;letter-spacing:.08em}
.term pre{margin:0;padding:12px 14px;font-family:var(--mono);font-size:12.5px;line-height:1.75;color:var(--code-ink);white-space:pre-wrap;min-height:96px}
.readout{display:flex;flex-wrap:wrap;gap:8px 18px;margin:12px 0;font-size:12.5px;color:var(--muted)}
.readout b{color:var(--ink);font-weight:600}
.readout b.bad{color:var(--signal)}
.g1-stop{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:14px 16px;margin-bottom:12px}
.g1-date{font-family:var(--mono);font-size:13px;color:var(--muted);letter-spacing:.06em}
.g1-name{font-size:22px;font-weight:700;color:var(--ink);margin:4px 0}
.g1-note{font-size:13px;color:var(--ink-soft);line-height:1.7}
.g2-cards{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}
.g2-card{border:1px solid var(--line-strong);border-radius:8px;background:var(--card);padding:8px 14px;font-family:var(--sans);font-size:13px;color:var(--ink);cursor:pointer;transition:.2s}
.g2-card:hover{border-color:var(--signal)}
.g2-card.hot{background:var(--signal-soft);border-color:var(--signal);color:var(--signal);font-weight:600}
.g2-q{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 14px}
.g2-qrow{display:flex;justify-content:space-between;gap:10px;padding:5px 0;font-size:12.5px;color:var(--muted);border-bottom:1px dashed var(--line-soft)}
.g2-qrow:last-child{border-bottom:0}
.g2-qrow b{color:var(--ink);text-align:right}
.g3-chips{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px}
.g3-chip{border:1px solid var(--line-strong);border-radius:999px;background:var(--card);padding:8px 16px;font-family:var(--sans);font-size:13px;color:var(--ink);cursor:pointer;transition:.2s}
.g3-chip:hover{border-color:var(--signal)}
.g3-chip.hot{background:var(--signal);border-color:var(--signal);color:#faf9f3;font-weight:600}
.g4-warn{font-size:12px;color:var(--muted);margin-top:8px}
.tbl-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
.tbl-wrap table{min-width:560px}
'''

html = open(TPL, encoding='utf-8').read()
# base 自带 <style>…</style> 外壳：剥壳，追加样式放回同一块内（VOL.14 教训）
assert base.startswith('<style>') and base.rstrip().endswith('</style>'), 'base 外壳异常'
base_inner = base[len('<style>'):base.rfind('</style>')]
html = html.replace('{{STYLE}}', '<style>' + base_inner + additions + '\n</style>')
assert html.split('</head>')[0].count('.g2-cards{') == 1, '追加样式必须位于 head 的 style 块内'

favicon = ('<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 '
           'viewBox=%220 0 24 24%22%3E%3Ccircle cx=%2212%22 cy=%2211%22 r=%223%22 fill=%22%233e6e8e%22/%3E%3Ccircle '
           'cx=%227%22 cy=%2218%22 r=%222.2%22 fill=%22%23b5482a%22/%3E%3Ccircle cx=%2217%22 cy=%2218%22 r=%222.2%22 '
           'fill=%22%233e6e8e%22/%3E%3Cpath d=%22M12 14l-4.4 5.2M12 14l4.4 5.2%22 stroke=%22%23333e48%22/%3E%3C/svg%3E"/>')
html = html.replace('<meta name="viewport"', favicon + '\n<meta name="viewport"', 1)

# 三张内容表包 tbl-wrap
html = re.sub(r'<table class="tbl">[\s\S]*?</table>',
              lambda m: '<div class="tbl-wrap">' + m.group(0) + '</div>', html)

open(OUT, 'w', encoding='utf-8', newline='\n').write(html)
checks = {
    'masthead': html.count('<header class="wrap masthead">'),
    'hero': html.count('<section class="wrap hero">'),
    'h1': html.count('<h1>'),
    'chapters': html.count('<section class="chapter"'),
    'demos': html.count('class="demo"'),
    'figs': html.count('class="fig"'),
    'tbl-wraps': html.count('tbl-wrap'),
    'stats': html.count('class="wrap stats"'),
}
print(checks)
assert checks['masthead'] == 1 and checks['hero'] == 1 and checks['h1'] == 1
assert checks['chapters'] == 5 and checks['demos'] == 4 and checks['figs'] == 4
assert checks['tbl-wraps'] == 4 + 2 and checks['stats'] == 1
print('build OK ->', OUT, len(html), 'chars')
