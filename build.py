import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
os.chdir(os.path.dirname(os.path.abspath(__file__)))

NAVY = "#1C4670"; GREEN = "#A8D08D"; ORANGE = "#E07B22"; MUTE = "#6B7690"; INK = "#10192A"
FONT = "font-family:'Prompt','Leelawadee UI',Tahoma,sans-serif"

def grouped(years, ours, comp=None, target=None, ymax=None, unit="", W=420, H=175, comp_label="คู่เทียบ", target_label=None, decimals=2):
    """Assessor-style chart: navy bars = ours, green bars = comparator, dotted orange target line, 'สูงดี' arrow."""
    comp = comp or {}
    vals = [v for v in ours if v is not None] + [v for v in comp.values() if v is not None] + ([target] if target else [])
    ymax = ymax or max(vals) * 1.25
    L, R, T, B = 34, 62, 28, 30
    pw, ph = W - L - R, H - T - B
    n = len(years); slot = pw / n
    def y(v): return T + ph - (v / ymax) * ph
    s = [f'<svg viewBox="0 0 {W} {H}" width="100%" style="display:block;{FONT}" aria-label="chart">']
    # axes
    s.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{T+ph}" stroke="{MUTE}" stroke-width="1"/>')
    s.append(f'<line x1="{L}" y1="{T+ph}" x2="{L+pw}" y2="{T+ph}" stroke="{MUTE}" stroke-width="1"/>')
    s.append(f'<text x="{L-4}" y="{T+4}" font-size="9" fill="{MUTE}" text-anchor="end">{unit}</text>')
    bw = min(34, slot * 0.32)
    for i, yr in enumerate(years):
        cx = L + slot * i + slot / 2
        has_c = comp.get(yr) is not None
        ox = cx - (bw + 3) / 2 if has_c else cx - bw / 2
        v = ours[i]
        if v is not None:
            s.append(f'<rect x="{ox-bw/2:.1f}" y="{y(v):.1f}" width="{bw}" height="{T+ph-y(v):.1f}" fill="{NAVY}" rx="2"/>')
            lab = f"{v:.{decimals}f}".rstrip("0").rstrip(".") if decimals else f"{v:.0f}"
            s.append(f'<text x="{ox:.1f}" y="{y(v)-4:.1f}" font-size="10.5" font-weight="600" fill="{INK}" text-anchor="middle">{lab}</text>')
        if has_c:
            c = comp[yr]; cxx = cx + (bw + 3) / 2
            s.append(f'<rect x="{cxx-bw/2:.1f}" y="{y(c):.1f}" width="{bw}" height="{T+ph-y(c):.1f}" fill="{GREEN}" rx="2"/>')
            lab = f"{c:.{decimals}f}".rstrip("0").rstrip(".") if decimals else f"{c:.0f}"
            s.append(f'<text x="{cxx+bw/2+1:.1f}" y="{y(c)-14:.1f}" font-size="10.5" fill="#3F6B2A" text-anchor="start">{lab}</text>')
        s.append(f'<text x="{cx:.1f}" y="{T+ph+14}" font-size="10.5" fill="{INK}" text-anchor="middle">{yr}</text>')
    if target is not None:
        ty = y(target)
        s.append(f'<line x1="{L}" y1="{ty:.1f}" x2="{L+pw}" y2="{ty:.1f}" stroke="{ORANGE}" stroke-width="2.2" stroke-dasharray="4 4"/>')
        s.append(f'<text x="{L+pw+3}" y="{ty+11 if comp else ty+3.5:.1f}" font-size="9.5" font-weight="600" fill="{ORANGE}">{target_label or ("เป้า " + (f"{target:g}"))}</text>')
    # good-direction arrow
    ax = L + pw - 40
    s.append(f'<path d="M{ax+8},{2} l-6,9 h4 v10 h4 v-10 h4 z" fill="{NAVY}"/>')
    s.append(f'<text x="{ax+22}" y="{16}" font-size="9.5" fill="{NAVY}">สูงดี</text>')
    if comp:
        s.append(f'<rect x="{L+pw+6}" y="{T+ph-12}" width="10" height="10" fill="{GREEN}"/><text x="{L+pw+19}" y="{T+ph-3}" font-size="9" fill="{MUTE}">{comp_label}</text>')
    s.append('</svg>')
    return "".join(s)

def hbar(items, highlight, W=440, H=190, unit="ชิ้น"):
    """Horizontal bars for institution comparison; highlight = label to colour navy."""
    items = sorted(items, key=lambda x: -x[1])
    L, R, T, B = 112, 44, 8, 22
    pw = W - L - R; rh = (H - T - B) / len(items); vmax = max(v for _, v in items) * 1.08
    s = [f'<svg viewBox="0 0 {W} {H}" width="100%" style="display:block;{FONT}" aria-label="chart">']
    for i, (lab, v) in enumerate(items):
        yy = T + rh * i + rh * 0.15; h = rh * 0.7
        col = NAVY if lab == highlight else GREEN
        w = pw * v / vmax
        s.append(f'<text x="{L-6}" y="{yy+h/2+4:.1f}" font-size="11" fill="{INK}" text-anchor="end" font-weight="{600 if lab==highlight else 400}">{lab}</text>')
        s.append(f'<rect x="{L}" y="{yy:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{col}" rx="2"/>')
        s.append(f'<text x="{L+w+5:.1f}" y="{yy+h/2+4:.1f}" font-size="11" font-weight="600" fill="{INK}">{v}</text>')
    s.append(f'<rect x="{L}" y="{H-14}" width="10" height="6" fill="{NAVY}"/><text x="{L+13}" y="{H-8}" font-size="8.5" fill="{MUTE}">ADT/มฟล.</text><rect x="{L+80}" y="{H-14}" width="10" height="6" fill="{GREEN}"/><text x="{L+93}" y="{H-8}" font-size="8.5" fill="{MUTE}">คู่เทียบ (สถาบันไทยขนาดใกล้เคียง)</text>')
    s.append('</svg>')
    return "".join(s)

charts = {
    "CHART_EMP": grouped(["2565", "2566", "2567", "2568"], [78.72, 71.36, 65.98, 64.48], comp={"2568": 72.6}, target=70, ymax=100, unit="%", comp_label="มฟล.", W=340, H=280),
    "CHART_GRAD": grouped(["2565", "2566", "2567", "2568"], [70.85, 86.26, 56.71, 43.97], target=70, ymax=100, unit="%", W=340, H=280),
    "CHART_PUB": grouped(["2565", "2566", "2567", "2568"], [36.36, 34.09, 51.02, 58.00], target=25, ymax=75, unit="%", W=340, H=280),
    "CHART_RANK": grouped(["2565", "2566", "2567", "2568"], [30.0, 37.5, 53.65, 57.89], target=35, ymax=75, unit="%", W=480, H=230),
    "CHART_OA": hbar([("มหาสารคาม", 265), ("ศิลปากร", 183), ("วลัยลักษณ์", 149), ("บูรพา", 137), ("มฟล. (ADT)", 132), ("นเรศวร", 122), ("อุบลราชธานี", 51)], "มฟล. (ADT)", W=440, H=380),
    "CHART_BUD": grouped(["ปีงบ 66", "ปีงบ 67", "ปีงบ 68", "ปีงบ 69"], [86.48, 86.94, 79.91, 87.80], target=85, ymax=100, unit="%", W=320, H=210),
    "CHART_SCO": grouped(["2565", "2566", "2567", "2568"], [0.25, 0.29, 1.50, 0.58], target=1.5, ymax=2.0, unit="ชิ้น/คน", W=320, H=210),
}

head = open("shell_head.html", encoding="utf-8").read()
foot = open("shell_foot.html", encoding="utf-8").read()
body = "".join(open(f, encoding="utf-8").read() for f in ["slides_a.html", "slides_b.html", "slides_c.html"])
for k, v in charts.items():
    assert "{{" + k + "}}" in body, k
    body = body.replace("{{" + k + "}}", v)
assert "{{" not in body
import re
def _scale(m):
    v = float(m.group(1)); f = 1.4 if v <= 16 else (1.25 if v <= 34 else 1.1)
    return f"font-size:{v*f:.1f}px".replace(".0px","px")
def _scale_svg(m):
    return f'font-size="{float(m.group(1))*1.35:.1f}"'
html = head + body
html = re.sub(r"font-size:\s*(\d+(?:\.\d+)?)px", _scale, html)
html = re.sub(r'font-size="(\d+(?:\.\d+)?)"', _scale_svg, html)
html = html + foot
open("index.html", "w", encoding="utf-8").write(html)
print("index.html", len(html), "bytes; sections:", body.count("<section"))
