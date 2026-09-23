"""Build an EDITABLE PowerPoint from the HTML deck.
Walks the rendered DOM of each slide (Playwright, 1280x720 = 13.333in x 7.5in, 1px = 0.75pt),
and emits native shapes: rectangles/cards, text boxes (runs keep size/weight/colour),
pictures (with object-fit cover cropping), native charts (with dashed target line), and notes.
Usage: py make_pptx_native.py   (needs http://127.0.0.1:8765/ serving this folder)
"""
import io, sys, os, re, json, time, copy
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.oxml.ns import qn
from lxml import etree

PX = 914400 / 96.0          # EMU per CSS px (13.333in = 1280px)
def E(px): return Emu(int(round(px * PX)))

FONT_MAP = {"Prompt": "Prompt", "IBM Plex Mono": "Consolas"}

# ---------- chart specs (same data as build.py) ----------
CHARTS = {
    "CHART_EMP":  dict(kind="col", cats=["2565","2566","2567","2568"], ours=[78.72,71.36,65.98,64.48], target=70, ymax=100, unit="%"),
    "CHART_GRAD": dict(kind="col", cats=["2565","2566","2567","2568"], ours=[70.85,86.26,56.71,43.97], target=70, ymax=100, unit="%"),
    "CHART_PUB":  dict(kind="col", cats=["2565","2566","2567","2568"], ours=[36.36,34.09,51.02,58.00], target=25, ymax=75, unit="%"),
    "CHART_RANK": dict(kind="col", cats=["2565","2566","2567","2568"], ours=[30.0,37.5,53.65,57.89], target=35, ymax=75, unit="%"),
    "CHART_BUD":  dict(kind="col", cats=["ปีงบ 66","ปีงบ 67","ปีงบ 68","ปีงบ 69"], ours=[86.48,86.94,79.91,87.80], target=85, ymax=100, unit="%"),
    "CHART_SCO":  dict(kind="col", cats=["2565","2566","2567","2568"], ours=[0.25,0.29,1.50,0.58], target=1.5, ymax=2.0, unit="ชิ้น/คน"),
    "CHART_ENROL": dict(kind="col", cats=["2564","2565","2566","2567","2568"], ours=[499,780,559,502,537], comp={"2564":280,"2565":400,"2566":410,"2567":330,"2568":360}, comp_label="แผนรับ", ymax=900, unit="คน"),
    "CHART_EMPLOYER": dict(kind="col", cats=["2565","2566","2567","2568"], ours=[4.34,4.18,4.05,None], target=4, ymax=5, unit="คะแนน"),
    "CHART_RET": dict(kind="col", cats=["2565","2566","2567","2568"], ours=[86.79,89.34,89.84,85.28], target=75, ymax=100, unit="%"),
    "CHART_GRANT": dict(kind="col", cats=["ปีงบ 66","ปีงบ 67","ปีงบ 68"], ours=[14.15,16.98,15.73], target=6.5, ymax=20, unit="ลบ."),
    "CHART_OA":   dict(kind="bar", items=[("มหาสารคาม",265),("ศิลปากร",183),("วลัยลักษณ์",149),("บูรพา",137),("มฟล.",132),("นเรศวร",122),("อุบลราชธานี",51)], highlight="มฟล."),
}
NAVY, GREEN, ORANGE, MUTE, INK = "1C4670", "A8D08D", "E07B22", "6B7690", "10192A"

JS_EXTRACT = r"""
() => {
  const stage = document.getElementById('stage'); const sr = stage.getBoundingClientRect();
  const s = document.querySelector('#stage .s.on');
  const out = [];
  const INLINE = new Set(['B','I','SPAN','SMALL','A','U','STRONG','EM','BR']);
  const parseColor = c => { const m = (c||'').match(/rgba?\(([^)]+)\)/); if(!m) return null; const p = m[1].split(',').map(Number); const a = p.length>3 ? p[3] : 1; if (a === 0) return null; const h = p.slice(0,3).map(v=>('0'+Math.round(v).toString(16)).slice(-2)).join('').toUpperCase(); return {hex:h, a}; };
  const rect = el => { const r = el.getBoundingClientRect(); return {x:r.left-sr.left, y:r.top-sr.top, w:r.width, h:r.height}; };
  const runStyle = (el) => { const cs = getComputedStyle(el); return {size: parseFloat(cs.fontSize), bold: parseInt(cs.fontWeight)>=600, italic: cs.fontStyle==='italic', color: (parseColor(cs.color)||{hex:'10192A'}).hex, font: cs.fontFamily.split(',')[0].replace(/["']/g,'').trim(), upper: cs.textTransform==='uppercase'}; };
  const collectRuns = (el, runs) => {
    el.childNodes.forEach(n => {
      if (n.nodeType === 3) { const t = n.textContent.replace(/\s+/g,' '); if (t.trim()) runs.push(Object.assign({text:t}, runStyle(el))); }
      else if (n.nodeType === 1) {
        if (n.tagName === 'BR') runs.push({br:true});
        else if (INLINE.has(n.tagName) && getComputedStyle(n).display.startsWith('inline')) collectRuns(n, runs);
      }
    });
  };
  const hasDirectText = el => [...el.childNodes].some(n => n.nodeType===3 && n.textContent.trim());
  const walk = (el) => {
    if (el.id === 'bar') return;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return;
    const r = rect(el);
    if (r.w <= 0 || r.h <= 0) return;
    const tag = el.tagName;
    if (tag === 'IMG') { out.push({t:'img', src: el.getAttribute('src'), x:r.x, y:r.y, w:r.w, h:r.h, fit: cs.objectFit, pos: cs.objectPosition, nw: el.naturalWidth, nh: el.naturalHeight, radius: parseFloat(cs.borderTopLeftRadius)||0, bg: (parseColor(cs.backgroundColor)||{}).hex||null}); return; }
    if (tag === 'svg' || tag === 'SVG') { out.push({t:'chart', key: el.dataset.chart || null, x:r.x, y:r.y, w:r.w, h:r.h}); return; }
    if (el === s) { out.push({t:'bg', color:(parseColor(cs.backgroundColor)||{hex:'FFFFFF'}).hex}); }
    else {
      const bg = parseColor(cs.backgroundColor);
      let grad = null;
      if (cs.backgroundImage && cs.backgroundImage.includes('linear-gradient') && cs.backgroundImage.includes('0deg')) grad = {hex:'081A2E', a:0.72};
      const bw = ['Top','Right','Bottom','Left'].map(side => ({w: parseFloat(cs['border'+side+'Width'])||0, c: (parseColor(cs['border'+side+'Color'])||{}).hex||null, st: cs['border'+side+'Style']}));
      const anyBorder = bw.some(b => b.w>0 && b.st!=='none' && b.c);
      if (bg || grad || anyBorder) out.push({t:'rect', x:r.x, y:r.y, w:r.w, h:r.h, fill: grad ? grad.hex : (bg?bg.hex:null), alpha: grad ? grad.a : (bg?bg.a:1), border: bw, radius: parseFloat(cs.borderTopLeftRadius)||0});
    }
    if (hasDirectText(el)) {
      const runs = []; collectRuns(el, runs);
      if (tag === 'LI') { runs.unshift(Object.assign({text:'•  '}, runStyle(el))); }
      const fs = parseFloat(cs.fontSize); let lh = parseFloat(cs.lineHeight); if (isNaN(lh)) lh = fs*1.3;
      const pad = ['Top','Right','Bottom','Left'].map(k => parseFloat(cs['padding'+k])||0);
      let x = r.x, w = r.w; if (tag === 'LI') { x -= 18; w += 18; }
      let valign = 'top'; if (tag==='TD'||tag==='TH') valign = 'top';
      out.push({t:'text', x, y:r.y, w, h:r.h, pad, runs, align: cs.textAlign, lh: lh/fs, valign});
      [...el.children].forEach(c => { if (!(INLINE.has(c.tagName) && getComputedStyle(c).display.startsWith('inline'))) walk(c); });
    } else {
      [...el.children].forEach(walk);
    }
  };
  walk(s);
  return out;
}
"""

def set_alpha(fill, alpha):
    if alpha >= 0.999: return
    solid = fill._xPr.find(qn('a:solidFill'))
    if solid is None: return
    clr = solid[0]
    a = etree.SubElement(clr, qn('a:alpha')); a.set('val', str(int(alpha*100000)))

def add_rect(slide, it):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if it['radius'] > 0.5 else MSO_SHAPE.RECTANGLE
    borders = it['border']  # top,right,bottom,left
    full = all(b['w']>0 and b['st']!='none' and b['c'] for b in borders)
    minw = min(b['w'] for b in borders) if full else 0
    only_bottom = (not full) and borders[2]['w']>0 and borders[2]['st']!='none' and borders[2]['c'] and not any(b['w']>0 and b['c'] for b in borders[:2]+borders[3:])
    only_top = (not full) and borders[0]['w']>0 and borders[0]['c'] and not any(b['w']>0 and b['c'] for b in borders[1:])
    if it['fill'] or full:
        sh = slide.shapes.add_shape(shape_type, E(it['x']), E(it['y']), E(it['w']), E(it['h']))
        if it['radius'] > 0.5:
            sh.adjustments[0] = min(0.5, it['radius'] / max(1, min(it['w'], it['h'])))
        if it['fill']:
            sh.fill.solid(); sh.fill.fore_color.rgb = RGBColor.from_string(it['fill']); set_alpha(sh.fill, it['alpha'])
        else:
            sh.fill.background()
        if full:
            base = min(borders, key=lambda b: b['w'])
            sh.line.color.rgb = RGBColor.from_string(base['c']); sh.line.width = Pt(max(0.5, minw*0.75))
        else:
            sh.line.fill.background()
        sh.shadow.inherit = False
        sh.text_frame.text = ""
    for side, b in (("bottom", borders[2]), ("top", borders[0]), ("left", borders[3]), ("right", borders[1])):
        if not (b['w']>0 and b['st']!='none' and b['c']): continue
        if full and b['w'] <= minw + 0.5: continue
        if side == "bottom": x1,y1,x2,y2 = it['x'], it['y']+it['h'], it['x']+it['w'], it['y']+it['h']
        elif side == "top": x1,y1,x2,y2 = it['x'], it['y'], it['x']+it['w'], it['y']
        elif side == "left": x1,y1,x2,y2 = it['x'], it['y'], it['x'], it['y']+it['h']
        else: x1,y1,x2,y2 = it['x']+it['w'], it['y'], it['x']+it['w'], it['y']+it['h']
        ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, E(x1), E(y1), E(x2), E(y2))
        ln.line.color.rgb = RGBColor.from_string(b['c']); ln.line.width = Pt(max(0.5, b['w']*0.75))

def add_text(slide, it):
    tb = slide.shapes.add_textbox(E(it['x']), E(it['y']), E(it['w']), E(it['h']))
    tf = tb.text_frame; tf.word_wrap = True
    pt, pr, pb, pl = it['pad']
    tf.margin_top, tf.margin_right, tf.margin_bottom, tf.margin_left = E(pt), E(pr), E(pb), E(pl)
    tf.vertical_anchor = MSO_ANCHOR.TOP
    p = tf.paragraphs[0]
    align = {"right": PP_ALIGN.RIGHT, "center": PP_ALIGN.CENTER, "end": PP_ALIGN.RIGHT}.get(it['align'], PP_ALIGN.LEFT)
    p.alignment = align; p.line_spacing = max(0.9, min(1.6, it['lh']))
    first = True
    for r in it['runs']:
        if r.get('br'):
            p = tf.add_paragraph(); p.alignment = align; p.line_spacing = max(0.9, min(1.6, it['lh'])); continue
        run = p.add_run()
        t = r['text']
        if r.get('upper'): t = t.upper()
        run.text = t
        f = run.font; f.size = Pt(max(6, r['size']*0.75*0.94)); f.bold = r['bold']; f.italic = r['italic']
        fname = FONT_MAP.get(r['font'], "Prompt")
        f.name = fname; f.color.rgb = RGBColor.from_string(r['color'])
        rPr = run._r.get_or_add_rPr()
        for tagn in ('a:cs', 'a:ea'):
            el = rPr.find(qn(tagn))
            if el is None:
                el = etree.SubElement(rPr, qn(tagn))
            el.set('typeface', fname)
    tb.shadow.inherit = False

def add_img(slide, it):
    src = it['src']
    if not os.path.exists(src): return
    x, y, w, h = it['x'], it['y'], it['w'], it['h']
    nw, nh = it['nw'] or 1, it['nh'] or 1
    if it['fit'] == 'contain':
        if it.get('bg'):
            bgr = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, E(x), E(y), E(w), E(h)); bgr.fill.solid(); bgr.fill.fore_color.rgb = RGBColor.from_string(it['bg']); bgr.line.fill.background()
        s = min(w/nw, h/nh); cw, ch = nw*s, nh*s
        slide.shapes.add_picture(src, E(x+(w-cw)/2), E(y+(h-ch)/2), E(cw), E(ch)); return
    pic = slide.shapes.add_picture(src, E(x), E(y), E(w), E(h))
    box_ar, img_ar = w/h, nw/nh
    if img_ar > box_ar:      # image wider: crop left/right
        keep = box_ar/img_ar; c = (1-keep)
        pic.crop_left = c/2; pic.crop_right = c/2
    else:                     # image taller: crop top/bottom
        keep = img_ar/box_ar; c = (1-keep)
        if 'top' in (it.get('pos') or '') and not it['pos'].startswith('50%'):
            pic.crop_top = 0; pic.crop_bottom = c
        else:
            pic.crop_top = c/2; pic.crop_bottom = c/2

def add_target_line(chart, cats, target, label):
    plotArea = chart._chartSpace.find(qn('c:chart')).find(qn('c:plotArea'))
    bar = plotArea.find(qn('c:barChart'))
    axIds = [a.get('val') for a in bar.findall(qn('c:axId'))]
    n = len(bar.findall(qn('c:ser')))
    C = 'http://schemas.openxmlformats.org/drawingml/2006/chart'; A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
    pts_c = "".join(f'<c:pt idx="{i}"><c:v>{c}</c:v></c:pt>' for i, c in enumerate(cats))
    pts_v = "".join(f'<c:pt idx="{i}"><c:v>{target}</c:v></c:pt>' for i in range(len(cats)))
    xml = f'''<c:lineChart xmlns:c="{C}" xmlns:a="{A}"><c:grouping val="standard"/><c:varyColors val="0"/>
<c:ser><c:idx val="{n}"/><c:order val="{n}"/><c:tx><c:v>{label}</c:v></c:tx>
<c:spPr><a:ln w="22225" cap="rnd"><a:solidFill><a:srgbClr val="{ORANGE}"/></a:solidFill><a:prstDash val="dash"/><a:round/></a:ln></c:spPr>
<c:marker><c:symbol val="none"/></c:marker>
<c:cat><c:strLit><c:ptCount val="{len(cats)}"/>{pts_c}</c:strLit></c:cat>
<c:val><c:numLit><c:formatCode>General</c:formatCode><c:ptCount val="{len(cats)}"/>{pts_v}</c:numLit></c:val>
<c:smooth val="0"/></c:ser><c:marker val="1"/><c:axId val="{axIds[0]}"/><c:axId val="{axIds[1]}"/></c:lineChart>'''
    el = etree.fromstring(xml)
    bar.addnext(el)

def style_axis_text(chart, size=9):
    chart.font.size = Pt(size); chart.font.name = "Prompt"; chart.font.color.rgb = RGBColor.from_string(INK)

def add_chart(slide, it):
    spec = CHARTS.get(it['key'])
    if not spec: return
    x, y, w, h = E(it['x']), E(it['y']), E(it['w']), E(it['h'])
    if spec['kind'] == 'col':
        cd = CategoryChartData(); cd.categories = spec['cats']
        cd.add_series('สำนักวิชา', spec['ours'])
        comp = spec.get('comp')
        if comp: cd.add_series(spec.get('comp_label','คู่เทียบ'), [comp.get(c) for c in spec['cats']])
        gf = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, w, h, cd); chart = gf.chart
        style_axis_text(chart); chart.has_title = False
        chart.has_legend = True
        chart.legend.position = XL_LEGEND_POSITION.BOTTOM; chart.legend.include_in_layout = False; chart.legend.font.size = Pt(8)
        va = chart.value_axis; va.maximum_scale = spec['ymax']; va.minimum_scale = 0; va.has_major_gridlines = False
        va.tick_labels.font.size = Pt(8); va.format.line.color.rgb = RGBColor.from_string(MUTE)
        ca = chart.category_axis; ca.tick_labels.font.size = Pt(9); ca.format.line.color.rgb = RGBColor.from_string(MUTE)
        plot = chart.plots[0]; plot.gap_width = 120; plot.overlap = -10
        plot.has_data_labels = True; dl = plot.data_labels; dl.font.size = Pt(8); dl.font.bold = True; dl.number_format = ('#,##0' if spec.get('decimals')==0 else 'General'); dl.number_format_is_linked = False; dl.position = XL_LABEL_POSITION.OUTSIDE_END
        plot.series[0].format.fill.solid(); plot.series[0].format.fill.fore_color.rgb = RGBColor.from_string(NAVY)
        if comp:
            plot.series[1].format.fill.solid(); plot.series[1].format.fill.fore_color.rgb = RGBColor.from_string(GREEN)
        if spec.get('target') is not None:
            add_target_line(chart, spec['cats'], spec['target'], f"เป้าหมาย {spec['target']:g}")
    else:
        items = list(reversed(spec['items']))  # bar chart draws first category at bottom
        cd = CategoryChartData(); cd.categories = [i[0] for i in items]; cd.add_series('ผลงาน 5 ปี', [i[1] for i in items])
        gf = slide.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, x, y, w, h, cd); chart = gf.chart
        style_axis_text(chart); chart.has_legend = False; chart.has_title = False
        va = chart.value_axis; va.has_major_gridlines = False; va.visible = False
        ca = chart.category_axis; ca.tick_labels.font.size = Pt(9); ca.format.line.color.rgb = RGBColor.from_string(MUTE)
        plot = chart.plots[0]; plot.gap_width = 60
        plot.has_data_labels = True; dl = plot.data_labels; dl.font.size = Pt(9); dl.font.bold = True; dl.position = XL_LABEL_POSITION.OUTSIDE_END
        ser = plot.series[0]; ser.format.fill.solid(); ser.format.fill.fore_color.rgb = RGBColor.from_string(GREEN)
        for i, (lab, v) in enumerate(items):
            if lab == spec['highlight']:
                pt = ser.points[i]; pt.format.fill.solid(); pt.format.fill.fore_color.rgb = RGBColor.from_string(NAVY)

def parse_notes(path):
    txt = open(path, encoding="utf-8").read(); out = {}
    for m in re.finditer(r"^## (\d+) · [^\n]*\n(.*?)(?=^## \d+ · |\Z)", txt, re.S | re.M):
        out[int(m.group(1))] = [l.strip()[2:].strip() for l in m.group(2).splitlines() if l.strip().startswith("- ")]
    return out

def main():
    notes = parse_notes("SCRIPT_NOTES.md")
    with sync_playwright() as p:
        try: browser = p.chromium.launch()
        except Exception: browser = p.chromium.launch(channel="chrome")
        page = browser.new_context(viewport={"width": 1280, "height": 720}).new_page()
        page.goto("http://127.0.0.1:8765/index.html?n=" + str(int(time.time())), wait_until="networkidle")
        page.wait_for_timeout(1200)
        page.evaluate("""() => { document.getElementById('bar').style.display='none'; const st=document.getElementById('stage'); st.style.transform='none'; st.style.transformOrigin='top left'; const vp=document.getElementById('viewport'); vp.style.display='block'; vp.style.height='720px'; vp.style.width='1280px'; window.addEventListener('resize', e=>e.stopImmediatePropagation(), true); }""")
        n = page.evaluate("document.querySelectorAll('#stage .s').length")
        print("slides in DOM:", n, "url:", page.url)
        slides_data = []
        for i in range(n):
            page.evaluate("(i) => { const s=[...document.querySelectorAll('#stage .s')]; s.forEach((x,k)=>x.classList.toggle('on', k===i)); }", i)
            page.wait_for_timeout(120)
            slides_data.append(page.evaluate(JS_EXTRACT))
        browser.close()
    json.dump(slides_data, open("shots/dom.json", "w", encoding="utf-8"), ensure_ascii=False)

    prs = Presentation(); prs.slide_width = E(1280); prs.slide_height = E(720)
    blank = prs.slide_layouts[6]
    for idx, items in enumerate(slides_data, start=1):
        slide = prs.slides.add_slide(blank)
        for it in items:
            t = it['t']
            if t == 'bg':
                slide.background.fill.solid(); slide.background.fill.fore_color.rgb = RGBColor.from_string(it['color'])
            elif t == 'rect': add_rect(slide, it)
            elif t == 'text': add_text(slide, it)
            elif t == 'img': add_img(slide, it)
            elif t == 'chart': add_chart(slide, it)
        # bottom stripe (CSS ::after)
        for x0, w0, col in ((0, 1280*0.66, "0F2A44"), (1280*0.66, 1280*0.34, "C8952B")):
            r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, E(x0), E(714), E(w0), E(6)); r.fill.solid(); r.fill.fore_color.rgb = RGBColor.from_string(col); r.line.fill.background(); r.shadow.inherit = False
        tf = slide.notes_slide.notes_text_frame; tf.text = ""
        for k, line in enumerate(notes.get(idx, [])):
            para = tf.paragraphs[0] if k == 0 else tf.add_paragraph(); para.text = "• " + line
            for r in para.runs: r.font.size = Pt(16)
        print("slide", idx, "shapes", len(slide.shapes))
    out = "ADT_SAR2568_นำเสนอกรรมการ.pptx"
    prs.save(out); print("saved", out)
    import shutil
    try:
        shutil.copy(out, os.path.join(r"G:\My Drive\School\SAR", "ADT_SAR2568_นำเสนอกรรมการ_v4.pptx")); print("copied to SAR root as _editable")
    except PermissionError:
        print("WARNING: target file is open in PowerPoint; copy skipped")

if __name__ == "__main__":
    main()
