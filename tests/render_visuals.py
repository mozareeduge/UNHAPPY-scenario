import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[1]


def resolve_chromium_executable() -> str | None:
    env_path = os.environ.get("CHROMIUM_EXECUTABLE_PATH")
    if env_path and Path(env_path).is_file():
        return env_path
    browsers_root = os.environ.get("PLAYWRIGHT_BROWSERS_PATH") or str(Path.home() / ".cache" / "ms-playwright")
    for candidate in sorted(Path(browsers_root).glob("chromium-*/chrome-linux/chrome"), reverse=True):
        if candidate.is_file():
            return str(candidate)
    for candidate in ("/usr/bin/chromium", "/usr/bin/chromium-browser"):
        if Path(candidate).is_file():
            return candidate
    return None


CHROMIUM_EXECUTABLE = resolve_chromium_executable()
OUT = ROOT / 'docs' / 'screenshots'
OUT.mkdir(parents=True, exist_ok=True)
RAW = (ROOT / 'index.html').read_text(encoding='utf-8')
HTML = RAW.replace('<head>', '<head><script>window.__UNHAPPY_TEST_MODE__=true;window.__UNHAPPY_TIME_SCALE__=0.18;</script>', 1)


def wait_phase(page, phase, timeout=10000):
    page.wait_for_function('p=>document.body.dataset.phase===p', arg=phase, timeout=timeout)


FINGERPRINT = os.environ.get('UNHAPPY_CANDIDATE_FINGERPRINT', 'uncomputed')
WATERMARK = f'REVIEW_ARTIFACT — NOT AUTOMATIC ARTISTIC PASS · candidate {FINGERPRINT[:12]}'


def shot(page, name, mobile=False):
    page.screenshot(path=str(OUT / name), animations='allow')


def label(im):
    d = ImageDraw.Draw(im)
    d.rectangle([0, im.height - 22, im.width, im.height], fill=(0, 0, 0))
    d.text((6, im.height - 18), WATERMARK, fill=(179, 75, 80))
    return im


def run_route(page, prefix):
    shot(page, f'{prefix}-00-threshold.png')
    page.click('#enter-button')
    page.wait_for_timeout(450)
    shot(page, f'{prefix}-01-sending.png')
    wait_phase(page, 'upload-failed')
    page.wait_for_timeout(160)
    shot(page, f'{prefix}-02-upload-failed.png')
    wait_phase(page, 'message-failed')
    page.wait_for_timeout(250)
    shot(page, f'{prefix}-03-message-failed.png')
    page.locator('#message-retry').evaluate('e=>e.click()')
    wait_phase(page, 'connection-failed')
    page.wait_for_timeout(350)
    shot(page, f'{prefix}-04-connection.png')
    page.locator(".system-shell.active [data-action='retry']").evaluate('e=>e.click()')
    wait_phase(page, 'reconnecting')
    page.wait_for_timeout(500)
    shot(page, f'{prefix}-05-reconnecting.png')
    wait_phase(page, 'failed')
    page.wait_for_timeout(250)
    shot(page, f'{prefix}-06-failed.png')
    wait_phase(page, 'report-question')
    page.wait_for_timeout(350)
    shot(page, f'{prefix}-07-question.png')
    page.locator(".system-shell.active [data-action='yes']").evaluate('e=>e.click()')
    wait_phase(page, 'reporting')
    page.wait_for_timeout(420)
    shot(page, f'{prefix}-08-reporting.png')
    wait_phase(page, 'report-failed')
    page.wait_for_timeout(260)
    shot(page, f'{prefix}-09-report-failed.png')
    wait_phase(page, 'renewed-connection-failed')
    page.wait_for_timeout(420)
    shot(page, f'{prefix}-10-renewed.png')
    page.click('#about-trigger')
    page.wait_for_timeout(250)
    shot(page, f'{prefix}-11-about.png')


def extra_states(page, prefix):
    """Named renders for C01-C09: retry erosion, process exhaustion, decision/closure,
    dense historical pressure, desktop annexation, and a bloom anchor close-up."""
    if page.evaluate("document.getElementById('about-page').open"):
        page.click('#about-return')
    page.evaluate("window.__UNHAPPY_TEST__.reset()")
    page.evaluate("window.__UNHAPPY_TEST__.start()")
    wait_phase(page, 'message-failed')
    page.wait_for_selector('#message-retry:not([hidden])', timeout=8000)
    page.locator('#message-retry').evaluate('e=>e.click()')
    wait_phase(page, 'connection-failed')
    page.wait_for_timeout(300)
    shot(page, f'{prefix}-12-retry-first.png')
    for _ in range(2):
        page.locator(".system-shell.active [data-action='retry']").evaluate('e=>e.click()')
        wait_phase(page, 'report-question')
        page.click(".system-shell.active [data-action='no']")
        wait_phase(page, 'renewed-connection-failed')
    page.wait_for_timeout(300)
    shot(page, f'{prefix}-13-retry-third.png')

    page.evaluate("window.__UNHAPPY_TEST__.reset()")
    page.evaluate("window.__UNHAPPY_TEST__.start()")
    wait_phase(page, 'message-failed')
    page.wait_for_selector('#message-retry:not([hidden])', timeout=8000)
    page.locator('#message-retry').evaluate('e=>e.click()')
    wait_phase(page, 'connection-failed')
    page.locator(".system-shell.active [data-action='retry']").evaluate('e=>e.click()')
    wait_phase(page, 'reconnecting')
    page.wait_for_timeout(300)
    shot(page, f'{prefix}-14-reconnecting-first.png')
    wait_phase(page, 'report-question')
    for _ in range(2):
        page.click(".system-shell.active [data-action='no']")
        wait_phase(page, 'renewed-connection-failed')
        page.locator(".system-shell.active [data-action='retry']").evaluate('e=>e.click()')
        wait_phase(page, 'reconnecting')
    page.wait_for_timeout(300)
    shot(page, f'{prefix}-15-reconnecting-third.png')
    wait_phase(page, 'report-question')
    page.wait_for_timeout(200)
    shot(page, f'{prefix}-16-decision.png')
    page.click(".system-shell.active [data-action='no']")
    page.wait_for_timeout(80)
    shot(page, f'{prefix}-17-no-closure.png')
    wait_phase(page, 'renewed-connection-failed')

    page.evaluate(
        "types => window.__UNHAPPY_TEST__.renderSequence(types)",
        ['connection', 'reconnecting', 'failed', 'question', 'reporting', 'report-failed', 'renewed'] * 3,
    )
    page.wait_for_timeout(400)
    shot(page, f'{prefix}-18-historical-pressure.png')

    if prefix == 'desktop':
        page.evaluate("window.__UNHAPPY_TEST__.reset()")
        for _ in range(10):
            page.evaluate("window.__UNHAPPY_TEST__.appendLine('Connection attempt failed')")
        page.wait_for_timeout(200)
        shot(page, f'{prefix}-19-annexation.png')

    page.evaluate("window.__UNHAPPY_TEST__.reset()")
    page.evaluate("window.__UNHAPPY_TEST__.appendLine('Connection attempt failed')")
    page.wait_for_timeout(200)
    shot(page, f'{prefix}-20-bloom-anchor.png')

    if prefix == 'mobile':
        for i, snap in enumerate(('compact', 'reading', 'expanded')):
            page.evaluate("s=>window.__UNHAPPY_TEST__.setPoemSnap(s,false)", snap)
            page.wait_for_timeout(120)
            shot(page, f'{prefix}-2{i+1}-seam-{snap}.png')


def contact_sheet(prefix, cols, thumb_width, pad=18):
    files = sorted(OUT.glob(f'{prefix}-*.png'))
    thumbs=[]
    for f in files:
        im=Image.open(f).convert('RGB')
        ratio=thumb_width/im.width
        th=im.resize((thumb_width, int(im.height*ratio)), Image.Resampling.LANCZOS)
        canvas=Image.new('RGB',(thumb_width, th.height+34),'black')
        canvas.paste(th,(0,0))
        d=ImageDraw.Draw(canvas)
        d.text((8, th.height+8), f.stem.split('-',2)[-1].replace('-',' '), fill=(220,216,208))
        thumbs.append(canvas)
    rows=(len(thumbs)+cols-1)//cols
    cell_h=max(i.height for i in thumbs)
    sheet=Image.new('RGB',(cols*thumb_width+(cols+1)*pad, rows*cell_h+(rows+1)*pad+22),(8,8,8))
    for idx,im in enumerate(thumbs):
        x=pad+(idx%cols)*(thumb_width+pad)
        y=pad+(idx//cols)*(cell_h+pad)
        sheet.paste(im,(x,y))
    label(sheet)
    sheet.save(ROOT/'docs'/f'{prefix}_state_contact_sheet.png',quality=95)


with sync_playwright() as pw:
    launch_kwargs = {'headless': True, 'args': ['--no-sandbox']}
    if CHROMIUM_EXECUTABLE:
        launch_kwargs['executable_path'] = CHROMIUM_EXECUTABLE
    browser = pw.chromium.launch(**launch_kwargs)
    page = browser.new_page(viewport={'width':1440,'height':900}, device_scale_factor=1)
    page.set_content(HTML, wait_until='load')
    run_route(page, 'desktop')
    extra_states(page, 'desktop')
    page.context.close()

    page = browser.new_page(viewport={'width':390,'height':844}, device_scale_factor=1)
    page.set_content(HTML, wait_until='load')
    run_route(page, 'mobile')
    extra_states(page, 'mobile')
    page.context.close()
    browser.close()

contact_sheet('desktop', cols=3, thumb_width=420)
contact_sheet('mobile', cols=4, thumb_width=210)
