"""Build ADT_SAR2568_นำเสนอกรรมการ.pptx from shots/slide-NN.png with speaker notes
from SCRIPT.md (overview) + SCRIPT_รายละเอียด.md (detail) per slide.
"""
import io, sys, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from pptx import Presentation
from pptx.util import Inches, Pt

def parse_script(path):
    """Return {slide_no: text} from '## N · title' sections."""
    txt = open(path, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r"^## (\d+) · [^\n]*\n(.*?)(?=^## \d+ · |\Z)", txt, re.S | re.M):
        out[int(m.group(1))] = m.group(2).strip()
    return out

notes_src = parse_script("SCRIPT_NOTES.md")

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]

shots = sorted(f for f in os.listdir("shots_jpg") if f.startswith("slide-") and f.endswith(".jpg"))
for idx, fn in enumerate(shots, start=1):
    slide = prs.slides.add_slide(blank)
    slide.shapes.add_picture(os.path.join("shots_jpg", fn), 0, 0, width=prs.slide_width, height=prs.slide_height)
    notes = slide.notes_slide.notes_text_frame
    lines = [l.strip()[2:].strip() for l in notes_src.get(idx, "").splitlines() if l.strip().startswith("- ")]
    notes.text = ""
    first = True
    for line in lines:
        p = notes.paragraphs[0] if first else notes.add_paragraph()
        first = False
        p.text = "• " + line
        for r in p.runs:
            r.font.size = Pt(16)

out = "ADT_SAR2568_นำเสนอกรรมการ.pptx"
prs.save(out)
print("saved", out, len(shots), "slides")
