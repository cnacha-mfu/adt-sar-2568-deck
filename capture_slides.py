"""Render every slide of index.html to PNG (2560x1440) with Playwright.
Usage: py capture_slides.py  (needs the deck served at http://127.0.0.1:8765/)
Output: shots/slide-01.png ... slide-24.png
"""
import io, sys, os, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/index.html?cap=" + str(int(time.time()))
os.makedirs("shots", exist_ok=True)

with sync_playwright() as p:
    try:
        browser = p.chromium.launch()
    except Exception:
        browser = p.chromium.launch(channel="chrome")
    ctx = browser.new_context(viewport={"width": 1280, "height": 720}, device_scale_factor=2)
    page = ctx.new_page()
    page.goto(URL, wait_until="networkidle")
    page.wait_for_timeout(1500)  # web fonts
    page.evaluate("""() => {
        document.getElementById('bar').style.display = 'none';
        const st = document.getElementById('stage');
        st.style.transform = 'none';
        st.style.transformOrigin = 'top left';
        const vp = document.getElementById('viewport');
        vp.style.display = 'block'; vp.style.height = '720px'; vp.style.width = '1280px'; vp.style.overflow = 'hidden';
        document.body.style.background = '#fff';
        window.addEventListener('resize', e => e.stopImmediatePropagation(), true);
    }""")
    n = page.evaluate("document.querySelectorAll('#stage .s').length")
    for i in range(n):
        page.evaluate("""(i) => { const s=[...document.querySelectorAll('#stage .s')]; s.forEach((x,k)=>x.classList.toggle('on', k===i)); }""", i)
        page.wait_for_timeout(250)
        page.locator("#stage").screenshot(path=f"shots/slide-{i+1:02d}.png")
        print("captured", i + 1)
    browser.close()
print("done", n)
