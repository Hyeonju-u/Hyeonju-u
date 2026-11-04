"""
hours(24칸 리스트)를 받아서 SVG 문자열을 돌려주는 함수 모음.

    from draw import draw_clock, draw_sky
    svg = draw_clock(hours)   # 문자열이 돌아옴 → 파일로 저장은 직접!
"""
import math

FONT = "ui-sans-serif,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,Menlo,Consolas,monospace"

# (이모지, 이름, 시간 범위)
PERIODS = [
    ("🌅", "Morning", range(6, 12)),
    ("🏙️", "Daytime", range(12, 18)),
    ("🌆", "Evening", range(18, 24)),
    ("🌙", "Night", range(0, 6)),
]

# 가장 많이 커밋한 시간대에 따라 바뀌는 제목
TITLES = {
    "Morning": ("Morning Coder", "🌅", "Morning"),
    "Daytime": ("Day Coder", "☀️", "Day"),
    "Evening": ("Evening Coder", "🌆", "Evening"),
    "Night": ("Night Owl", "🦉", "Night"),
}


def summarize(hours):
    """hours를 받아서 그림에 필요한 숫자들을 계산한다."""
    total = sum(hours)
    counts = [(emoji, name, sum(hours[h] for h in r)) for emoji, name, r in PERIODS]
    top = max(counts, key=lambda x: x[2])[1]          # 커밋이 제일 많은 시간대 이름
    peak = hours.index(max(hours))                     # 커밋이 제일 많은 시각(0~23)
    title, emoji, short = TITLES[top]
    return total, counts, peak, title, emoji, short


def pct(n, total):
    return n / total * 100 if total else 0


# ---------------------------------------------------------------- A. 24시간 시계
def draw_clock(hours):
    total, counts, peak, title, emoji, short = summarize(hours)
    mx = max(hours) or 1
    W, H = 820, 380
    cx, cy, r0, r1 = 200, 190, 62, 150

    bars = []
    for h, v in enumerate(hours):
        a = h / 24 * 2 * math.pi - math.pi / 2        # 0시가 맨 위, 시계 방향
        da = 2 * math.pi / 24 * 0.36
        L = max(r0 + (r1 - r0) * v / mx, r0 + 4)
        pts = " ".join(
            f"{cx + rad * math.cos(ang):.1f},{cy + rad * math.sin(ang):.1f}"
            for rad, ang in [(r0, a - da), (L, a - da), (L, a + da), (r0, a + da)]
        )
        op = 0.25 + 0.75 * v / mx
        bars.append(
            f'<polygon points="{pts}" fill="url(#bar)" fill-opacity="{op:.2f}" '
            f'style="animation:grow .8s {h * 0.04:.2f}s both;transform-origin:{cx}px {cy}px"/>'
        )

    ticks = []
    for h in (0, 6, 12, 18):
        a = h / 24 * 2 * math.pi - math.pi / 2
        x, y = cx + (r1 + 18) * math.cos(a), cy + (r1 + 18) * math.sin(a) + 5
        ticks.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" class="tick">{h:02d}</text>')

    rows = []
    for i, (e, n, c) in enumerate(counts):
        y, p = 150 + i * 44, pct(c, total)
        rows.append(
            f'<text x="420" y="{y}" class="row">{e}  {n}</text>'
            f'<text x="770" y="{y}" class="pct" text-anchor="end">{p:.1f}%</text>'
            f'<rect x="420" y="{y + 10}" width="350" height="6" rx="3" fill="#10233d"/>'
            f'<rect x="420" y="{y + 10}" width="{350 * p / 100:.1f}" height="6" rx="3" fill="url(#bar)" '
            f'style="animation:wid 1s {0.3 + i * 0.15:.2f}s both"/>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#020b1f"/><stop offset="1" stop-color="#06204a"/></linearGradient>
<linearGradient id="bar" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7dd3fc"/><stop offset="1" stop-color="#2563eb"/></linearGradient>
<filter id="glow"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<style>
.tick{{font:12px {MONO};fill:#5b7ea6}} .row{{font:16px {FONT};fill:#cfe8ff}} .pct{{font:15px {MONO};fill:#7dd3fc}}
.title{{font:700 26px {FONT};fill:#e0f7ff}} .sub{{font:14px {MONO};fill:#5b9bd5}}
.ctr{{font:700 15px {FONT};fill:#e0f7ff}} .ctr2{{font:12px {MONO};fill:#7dd3fc}}
@keyframes grow{{from{{transform:scale(.4);opacity:0}}to{{transform:scale(1);opacity:1}}}}
@keyframes wid{{from{{width:0}}}}
</style>
</defs>
<rect width="{W}" height="{H}" rx="14" fill="url(#bg)"/>
<circle cx="{cx}" cy="{cy}" r="{r1}" fill="none" stroke="#1e3a5f" stroke-dasharray="2 6"/>
<circle cx="{cx}" cy="{cy}" r="{r0 - 6}" fill="#06111f" stroke="#1e3a5f"/>
{"".join(bars)}{"".join(ticks)}
<text x="{cx}" y="{cy - 2}" text-anchor="middle" class="ctr">{emoji} {short}</text>
<text x="{cx}" y="{cy + 16}" text-anchor="middle" class="ctr2">peak {peak:02d}:00</text>
<text x="420" y="70" class="title" filter="url(#glow)">I'm a {title} {emoji}</text>
<text x="420" y="98" class="sub">{total} commits · KST</text>
{"".join(rows)}
</svg>'''


# ---------------------------------------------------------------- B. 하늘 그라데이션
def draw_sky(hours):
    total, counts, peak, title, emoji, short = summarize(hours)
    mx = max(hours) or 1
    W, H = 820, 300
    x0, x1, base, top = 30, 790, 240, 90
    step = (x1 - x0) / 23
    pts = [(x0 + i * step, base - (base - top) * v / mx) for i, v in enumerate(hours)]

    # 점들을 부드러운 곡선으로 잇기 (Catmull-Rom → 베지어)
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    area = d + f" L{x1},{base} L{x0},{base} Z"

    count_of = {n: c for _, n, c in counts}
    segs = []
    for h, e, n in [(0, "🌙", "Night"), (6, "🌅", "Morning"), (12, "🏙️", "Daytime"), (18, "🌆", "Evening")]:
        xm = x0 + (h + 3) * step
        segs.append(
            f'<text x="{xm:.1f}" y="268" text-anchor="middle" class="seg">{e} {n}</text>'
            f'<text x="{xm:.1f}" y="287" text-anchor="middle" class="segp">{pct(count_of[n], total):.0f}%</text>'
        )
        if h:
            segs.append(
                f'<line x1="{x0 + h * step:.1f}" x2="{x0 + h * step:.1f}" y1="{top - 10}" y2="{base}" '
                f'stroke="#fff" stroke-opacity=".15" stroke-dasharray="3 5"/>'
            )

    px, py = pts[peak]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs>
<linearGradient id="sky" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="#0b1340"/><stop offset=".22" stop-color="#3b4a9a"/><stop offset=".33" stop-color="#f6a6b2"/>
<stop offset=".45" stop-color="#7cc8f8"/><stop offset=".62" stop-color="#4aa8f0"/><stop offset=".76" stop-color="#f59e6b"/>
<stop offset=".86" stop-color="#7b4fa0"/><stop offset="1" stop-color="#0b1340"/></linearGradient>
<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#020b1f" stop-opacity=".55"/></linearGradient>
<linearGradient id="hill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".85"/><stop offset="1" stop-color="#fff" stop-opacity=".15"/></linearGradient>
<clipPath id="rev"><rect x="0" y="0" width="0" height="{H}"><animate attributeName="width" from="0" to="{W}" dur="1.6s" fill="freeze"/></rect></clipPath>
<style>
.title{{font:700 24px {FONT};fill:#fff}} .sub{{font:13px {MONO};fill:#ffffffcc}}
.seg{{font:14px {FONT};fill:#fff}} .segp{{font:12px {MONO};fill:#ffffffbb}} .pk{{font:12px {MONO};fill:#0b1340}}
</style>
</defs>
<rect width="{W}" height="{H}" rx="14" fill="url(#sky)"/>
<rect width="{W}" height="{H}" rx="14" fill="url(#fade)"/>
<text x="30" y="44" class="title">I'm a {title} {emoji}</text>
<text x="30" y="66" class="sub">{total} commits · KST</text>
{"".join(segs)}
<g clip-path="url(#rev)">
<path d="{area}" fill="url(#hill)"/><path d="{d}" fill="none" stroke="#fff" stroke-width="2.5"/>
<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="#fff"/>
<rect x="{px - 38:.1f}" y="{py - 32:.1f}" width="76" height="20" rx="10" fill="#fff"/>
<text x="{px:.1f}" y="{py - 18:.1f}" text-anchor="middle" class="pk">peak {peak:02d}:00</text>
</g>
</svg>'''