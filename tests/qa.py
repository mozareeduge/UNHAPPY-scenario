from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable

from lxml import html as lxml_html
from playwright.sync_api import sync_playwright, Page, Browser, expect

ROOT = Path(__file__).resolve().parents[1]


def resolve_chromium_executable() -> str | None:
    """Locate a Chromium binary without pinning a path that only exists on one machine.

    Honors CHROMIUM_EXECUTABLE_PATH if set, then searches the Playwright
    browsers directory (PLAYWRIGHT_BROWSERS_PATH or the default cache), then
    falls back to a system-installed chromium. Returns None to let
    Playwright use its own managed browser when nothing else is found.
    """
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
HTML_PATH = ROOT / "index.html"
SCREEN_DIR = ROOT / "docs" / "screenshots"
SCREEN_DIR.mkdir(parents=True, exist_ok=True)
RAW_HTML = HTML_PATH.read_text(encoding="utf-8")
TEST_HTML = RAW_HTML.replace(
    "<head>",
    "<head><script>window.__UNHAPPY_TEST_MODE__=true;window.__UNHAPPY_TIME_SCALE__=0.02;</script>",
    1,
)

SYSTEM_LINES = [
    "Upload failed",
    "Sending the message failed",
    "Connection attempt failed",
    "Reconnecting…",
    "Failed",
    "Do you want to report the problem?",
    "Reporting the problem…",
    "Reporting failed",
]


@dataclass
class Result:
    family: str
    name: str
    passed: bool
    detail: str = ""


RESULTS: list[Result] = []


def record(family: str, name: str, fn: Callable[[], None]) -> None:
    try:
        fn()
        RESULTS.append(Result(family, name, True, "")); print(f"PASS [{family}] {name}", flush=True)
    except Exception as exc:  # noqa: BLE001
        RESULTS.append(Result(family, name, False, f"{type(exc).__name__}: {exc}")); print(f"FAIL [{family}] {name}: {type(exc).__name__}: {exc}", flush=True)


def new_page(browser: Browser, width: int = 1440, height: int = 900, reduced_motion: str | None = None) -> tuple[Page, list[str], list[str], list[str]]:
    context = browser.new_context(viewport={"width": width, "height": height}, device_scale_factor=1)
    page = context.new_page()
    console_errors: list[str] = []
    page_errors: list[str] = []
    requests: list[str] = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda exc: page_errors.append(str(exc)))
    page.on("request", lambda req: requests.append(req.url))
    if reduced_motion:
        page.emulate_media(reduced_motion=reduced_motion)
    page.set_content(TEST_HTML, wait_until="load")
    return page, console_errors, page_errors, requests


def state(page: Page) -> dict:
    return page.evaluate("window.__UNHAPPY_TEST__.getState()")


def render_state(page: Page, typ: str, actions: list[dict] | None = None) -> None:
    page.evaluate("([t,a]) => window.__UNHAPPY_TEST__.renderState(t, null, a)", [typ, actions or []])
    page.wait_for_timeout(100)


def assert_within(inner: dict, outer: dict, tolerance: float = 1.0) -> None:
    assert inner["x"] >= outer["x"] - tolerance, (inner, outer)
    assert inner["y"] >= outer["y"] - tolerance, (inner, outer)
    assert inner["x"] + inner["width"] <= outer["x"] + outer["width"] + tolerance, (inner, outer)
    assert inner["y"] + inner["height"] <= outer["y"] + outer["height"] + tolerance, (inner, outer)


def test_static_html() -> None:
    doc = lxml_html.fromstring(RAW_HTML)
    ids = doc.xpath("//*[@id]/@id")
    assert len(ids) == len(set(ids)), "duplicate ids"
    assert doc.xpath("string(//*[@id='threshold']//p[contains(@class,'author')])").strip() == "by mozare"
    assert doc.xpath("string(//*[@id='about-page']//*[contains(@class,'about-author')])").strip() == "by mozare"
    assert "Try again" not in "\n".join(SYSTEM_LINES)
    for line in SYSTEM_LINES:
        assert line in RAW_HTML
    assert "font-src 'none'" in RAW_HTML
    assert "connect-src 'none'" in RAW_HTML
    assert "localStorage" not in RAW_HTML and "sessionStorage" not in RAW_HTML
    assert "fetch(" not in RAW_HTML and "XMLHttpRequest" not in RAW_HTML
    assert "shell-mark error" not in RAW_HTML
    assert re.search(r"--state-font:\s*Bahnschrift", RAW_HTML)
    assert "by mozare" in RAW_HTML


def test_threshold_and_fonts(browser: Browser) -> None:
    page, _, errors, _ = new_page(browser)
    assert not errors
    assert page.locator("#threshold").is_visible()
    assert page.locator("#work").get_attribute("inert") is not None
    assert page.locator("#threshold-title").inner_text().replace("\n", " ") == "UNHAPPY Scenario"
    threshold_font = page.locator(".title-unhappy").evaluate("e=>getComputedStyle(e).fontFamily")
    scenario_font = page.locator(".title-scenario").evaluate("e=>getComputedStyle(e).fontFamily")
    page.evaluate("window.__UNHAPPY_TEST__.renderState('connection','Connection attempt failed',[{label:'Try again',value:'retry',primary:true}])")
    page.wait_for_timeout(100)
    state_font = page.locator(".system-shell.active .shell-title").evaluate("e=>getComputedStyle(e).fontFamily")
    assert threshold_font != scenario_font
    assert state_font != scenario_font
    assert "Roboto Condensed" in state_font or "Arial Narrow" in state_font or "Bahnschrift" in state_font
    page.context.close()


def test_enter_and_initial(browser: Browser) -> None:
    page, console_errors, page_errors, requests = new_page(browser)
    page.click("#enter-button")
    page.wait_for_timeout(120)
    assert page.locator("#work").is_visible()
    assert page.locator("#attachment").is_visible()
    assert page.locator(".upload-orbit").is_visible()
    assert page.locator(".message-spinner").is_visible()
    assert page.locator(".attachment-picture").is_visible()
    assert page.locator("#message-retry").is_hidden()
    assert not page_errors
    assert not console_errors
    # No external runtime request; set_content itself produces none.
    assert requests == []
    page.context.close()


def wait_phase(page: Page, phase: str, timeout: int = 4000) -> None:
    page.wait_for_function("p => document.body.dataset.phase === p", arg=phase, timeout=timeout)


def test_full_yes_and_loop(browser: Browser) -> None:
    page, console_errors, page_errors, _ = new_page(browser)
    page.click("#enter-button")
    wait_phase(page, "message-failed")
    expect(page.locator("#message-retry")).to_be_visible()
    page.locator("#message-retry").evaluate("e=>e.click()")
    wait_phase(page, "connection-failed")
    assert page.locator(".system-shell.active [data-action='retry']").is_enabled()
    # Action is live while poem inscription can still be underway.
    page.locator(".system-shell.active [data-action='retry']").evaluate("e=>e.click()")
    wait_phase(page, "report-question")
    no_btn = page.locator(".system-shell.active [data-action='no']")
    yes_btn = page.locator(".system-shell.active [data-action='yes']")
    assert no_btn.is_enabled() and yes_btn.is_enabled()
    assert page.evaluate("document.activeElement?.dataset?.action") == "no"
    page.click(".system-shell.active [data-action='yes']")
    wait_phase(page, "report-failed")
    wait_phase(page, "renewed-connection-failed")
    page.wait_for_function("() => window.__UNHAPPY_TEST__.getState().poem.filter(x => x.text === 'Connection attempt failed').length >= 2", timeout=4000)
    st = state(page)
    poem = [x["text"] for x in st["poem"]]
    assert "Try again" not in poem
    assert poem[:2] == SYSTEM_LINES[:2]
    assert poem.count("Connection attempt failed") >= 2
    assert poem.count("Reporting failed") >= 1
    assert st["activeShell"] == "renewed"
    assert not st["historicalReadableText"]
    assert st["shellCount"] <= 10
    assert not console_errors and not page_errors
    page.context.close()


def test_no_branch(browser: Browser) -> None:
    page, _, errors, _ = new_page(browser)
    page.click("#enter-button")
    wait_phase(page, "message-failed")
    page.locator("#message-retry").evaluate("e=>e.click()")
    wait_phase(page, "connection-failed")
    page.locator(".system-shell.active [data-action='retry']").evaluate("e=>e.click()")
    wait_phase(page, "report-question")
    page.click(".system-shell.active [data-action='no']")
    wait_phase(page, "renewed-connection-failed")
    page.wait_for_function("() => window.__UNHAPPY_TEST__.getState().poem.filter(x => x.text === 'Connection attempt failed').length >= 2", timeout=4000)
    poem = [x["text"] for x in state(page)["poem"]]
    assert "Reporting the problem…" not in poem
    assert "Reporting failed" not in poem
    assert poem.count("Connection attempt failed") >= 2
    assert not errors
    page.context.close()


def test_about_routes(browser: Browser) -> None:
    page, _, errors, _ = new_page(browser)
    page.evaluate("window.__UNHAPPY_TEST__.start()")
    page.wait_for_timeout(80)
    page.click("#about-trigger")
    assert page.locator("#about-page").evaluate("e=>e.open")
    assert page.locator("#about-return").is_visible()
    assert page.locator("#about-title").inner_text().replace("\n", " ") == "UNHAPPY Scenario"
    page.click("#about-return")
    assert not page.locator("#about-page").evaluate("e=>e.open")
    page.click("#about-trigger")
    page.click("#about-title-return")
    assert state(page)["phase"] == "threshold"
    assert page.locator("#threshold").is_visible()
    assert not errors
    page.context.close()


def test_shell_semantics_and_no_close(browser: Browser) -> None:
    page, _, errors, _ = new_page(browser)
    render_state(page, "question", [
        {"label": "No", "value": "no"},
        {"label": "Yes", "value": "yes", "primary": True},
    ])
    active = page.locator(".system-shell.active")
    assert active.get_attribute("role") == "dialog" or active.get_attribute("role") == "alertdialog"
    assert active.locator("button").count() == 2
    assert active.locator("button", has_text="Close").count() == 0
    assert active.locator("text=×").count() == 0
    assert active.locator(".shell-signal").count() == 1
    assert page.locator("#messenger-header").get_attribute("inert") is not None
    assert page.locator("#composer").get_attribute("inert") is not None
    assert not errors
    page.context.close()


def test_retry_animation(browser: Browser) -> None:
    page, _, _, _ = new_page(browser)
    render_state(page, "connection", [{"label": "Try again", "value": "retry", "primary": True}])
    button = page.locator(".system-shell.active .retry-call")
    assert button.count() == 1
    animation = button.evaluate("e=>getComputedStyle(e).animationName")
    duration = button.evaluate("e=>getComputedStyle(e).animationDuration")
    assert "retryCall" in animation
    assert duration not in ("0s", "0ms")
    page.context.close()


def test_poem_inscription(browser: Browser) -> None:
    page, _, errors, _ = new_page(browser)
    page.evaluate("window.__UNHAPPY_TEST__.appendLine('Upload failed')")
    page.wait_for_timeout(40)
    line = page.locator(".poem-line").last
    assert line.count() == 1
    # Smooth transition exists and is materially longer than a pop.
    duration = line.evaluate("e=>getComputedStyle(e).transitionDuration")
    values = [float(v.rstrip('s')) for v in duration.split(',')]
    assert max(values) >= 1.0
    page.wait_for_timeout(1250)
    assert float(line.evaluate("e=>getComputedStyle(e).opacity")) > .95
    assert page.locator(".blood-bloom").count() >= 1
    assert not errors
    page.context.close()


def test_historical_accumulation(browser: Browser) -> None:
    page, _, errors, _ = new_page(browser)
    types = ["connection", "reconnecting", "failed", "question", "reporting", "report-failed", "renewed"] * 16
    page.evaluate("types => window.__UNHAPPY_TEST__.renderSequence(types)", types)
    page.wait_for_timeout(500)
    st = state(page)
    assert st["shellCount"] <= 10
    assert st["historicalShells"] <= 9
    assert not st["historicalReadableText"]
    assert page.locator(".system-shell.historical").count() >= 5
    assert page.locator(".system-shell.active").count() == 1
    assert not errors
    page.context.close()


def test_long_poem_and_scroll(browser: Browser) -> None:
    page, _, errors, _ = new_page(browser)
    page.evaluate("window.__UNHAPPY_TEST__.stressLines(2000)")
    page.wait_for_timeout(250)
    assert page.locator(".poem-line").count() == 2000
    page.locator("#poem-scroll").evaluate("e=>e.scrollTop=0")
    page.wait_for_timeout(80)
    assert not page.locator("#return-latest").is_hidden()
    page.locator("#return-latest").evaluate("e=>e.click()")
    page.wait_for_timeout(80)
    assert state(page)["autoFollow"] is True
    page.locator("#poem-scroll").evaluate("e=>e.scrollTo({top:e.scrollHeight,behavior:'auto'})")
    page.wait_for_timeout(60)
    at_bottom = page.locator("#poem-scroll").evaluate("e=>e.scrollHeight-e.scrollTop-e.clientHeight<80")
    assert at_bottom
    assert not errors
    page.context.close()


def test_viewport_geometry(browser: Browser, width: int, height: int, typ: str, actions: list[dict] | None = None) -> None:
    page, _, errors, _ = new_page(browser, width, height)
    page.evaluate("window.__UNHAPPY_TEST__.appendLine('Upload failed')")
    page.evaluate("window.__UNHAPPY_TEST__.appendLine('Sending the message failed')")
    render_state(page, typ, actions)
    active_box = page.locator(".system-shell.active").bounding_box()
    conversation_box = page.locator("#conversation").bounding_box()
    assert active_box and conversation_box
    assert_within(active_box, conversation_box, 2)
    for i in range(page.locator(".system-shell.active button").count()):
        assert_within(page.locator(".system-shell.active button").nth(i).bounding_box(), active_box, 2)
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
    assert page.evaluate("document.documentElement.scrollHeight <= innerHeight + 1")
    if width <= 760:
        page.evaluate("window.__UNHAPPY_TEST__.setPoemSnap('reading', false)")
        page.wait_for_timeout(80)
        poem_box = page.locator("#poem-field").bounding_box()
        messenger_box = page.locator("#messenger").bounding_box()
        assert poem_box and messenger_box
        assert poem_box["y"] >= messenger_box["y"] + messenger_box["height"] - 2
        radius = page.locator("#poem-field").evaluate("e=>getComputedStyle(e).borderRadius")
        assert radius in ("0px", "")
    assert not errors
    page.context.close()


def test_mobile_snaps(browser: Browser) -> None:
    page, _, errors, _ = new_page(browser, 390, 844)
    page.evaluate("window.__UNHAPPY_TEST__.appendLine('Upload failed')")
    heights = []
    for snap in ["compact", "reading", "expanded"]:
        page.evaluate("s=>window.__UNHAPPY_TEST__.setPoemSnap(s,false)", snap)
        page.wait_for_timeout(40)
        heights.append(page.locator("#poem-field").bounding_box()["height"])
    assert heights[0] < heights[1] < heights[2]
    assert heights[0] >= 120
    assert heights[2] <= 844 * .86 + 2
    assert not errors
    page.context.close()


def test_reduced_motion(browser: Browser) -> None:
    page, _, errors, _ = new_page(browser, reduced_motion="reduce")
    render_state(page, "connection", [{"label": "Try again", "value": "retry", "primary": True}])
    duration = page.locator(".system-shell.active .retry-call").evaluate("e=>getComputedStyle(e).animationDuration")
    seconds = float(duration.rstrip("s"))
    assert seconds < .01
    assert not errors
    page.context.close()


def test_visual_fonts_and_scale(browser: Browser) -> None:
    page, _, errors, _ = new_page(browser)
    render_state(page, "connection", [{"label": "Try again", "value": "retry", "primary": True}])
    shell = page.locator(".system-shell.active")
    title = shell.locator(".shell-title")
    shell_box = shell.bounding_box()
    title_box = title.bounding_box()
    assert shell_box and title_box
    assert title_box["height"] < shell_box["height"] * .48
    assert title_box["width"] < shell_box["width"] * .84
    font_size = float(title.evaluate("e=>parseFloat(getComputedStyle(e).fontSize)"))
    assert 25 <= font_size <= 40
    assert not errors
    page.context.close()


def test_controls_targets(browser: Browser) -> None:
    page, _, errors, _ = new_page(browser)
    page.evaluate("window.__UNHAPPY_TEST__.renderState('question','Do you want to report the problem?',[{label:'No',value:'no'},{label:'Yes',value:'yes',primary:true}])")
    page.wait_for_timeout(100)
    for selector in [".system-shell.active button", "#about-trigger"]:
        loc = page.locator(selector)
        for i in range(loc.count()):
            box = loc.nth(i).bounding_box()
            assert box and box["height"] >= 42 and box["width"] >= 42
    assert not errors
    page.context.close()



def test_mobile_poem_affordance(browser: Browser) -> None:
    page, _, errors, _ = new_page(browser, 390, 844)
    render_state(page, 'connection', [{'label': 'Try again', 'value': 'retry', 'primary': True}])
    page.evaluate("window.__UNHAPPY_TEST__.appendLine('Upload failed')")
    page.wait_for_timeout(80)
    fault = page.locator('#poem-fault')
    assert fault.is_visible()
    box = fault.bounding_box()
    assert box and box['height'] >= 44 and box['width'] >= 44
    assert fault.get_attribute('aria-expanded') == 'false'
    up_opacity = float(page.locator('.fault-arrow-up').evaluate('e=>getComputedStyle(e).opacity'))
    down_opacity = float(page.locator('.fault-arrow-down').evaluate('e=>getComputedStyle(e).opacity'))
    assert up_opacity > down_opacity
    fault.click()
    page.wait_for_timeout(100)
    assert fault.get_attribute('aria-expanded') == 'true'
    assert state(page)['poemSnap'] == 'reading'
    fault.click()
    page.wait_for_timeout(100)
    assert fault.get_attribute('aria-expanded') == 'false'
    assert state(page)['poemSnap'] == 'compact'
    assert not errors
    page.context.close()


def test_short_desktop_question_layout(browser: Browser) -> None:
    page, _, errors, _ = new_page(browser, 1051, 566)
    page.evaluate("window.__UNHAPPY_TEST__.appendLine('Upload failed')")
    render_state(page, 'question', [
        {'label': 'No', 'value': 'no'},
        {'label': 'Yes', 'value': 'yes', 'primary': True},
    ])
    page.wait_for_timeout(700)
    shell = page.locator('.system-shell.active')
    shell_box = shell.bounding_box()
    conversation_box = page.locator('#conversation').bounding_box()
    composer_box = page.locator('#composer').bounding_box()
    assert shell_box and conversation_box and composer_box
    assert_within(shell_box, conversation_box, 2)
    assert shell_box['y'] + shell_box['height'] <= composer_box['y'] + 1
    for i in range(shell.locator('button').count()):
        assert_within(shell.locator('button').nth(i).bounding_box(), shell_box, 2)
    title = shell.locator('.shell-title').bounding_box()
    assert title and title['height'] < shell_box['height'] * .55
    assert not errors
    page.context.close()


def test_ordered_residue_geometry(browser: Browser) -> None:
    page, _, errors, _ = new_page(browser, 1280, 800)
    types = ['connection', 'reconnecting', 'failed', 'question', 'reporting', 'report-failed', 'renewed']
    page.evaluate('types => window.__UNHAPPY_TEST__.renderSequence(types)', types)
    page.wait_for_timeout(500)
    items = page.locator('.system-shell.historical')
    assert 4 <= items.count() <= 6
    points = []
    for i in range(items.count()):
        node = items.nth(i)
        age = int(node.get_attribute('data-age'))
        box = node.bounding_box()
        assert box
        points.append((age, box['x'] + box['width']/2, box['y'] + box['height']/2))
    points.sort()
    for earlier, later in zip(points, points[1:]):
        assert later[1] < earlier[1] + 1, points
        assert later[2] > earlier[2] - 1, points
    assert not errors
    page.context.close()

def run() -> int:
    record("Static integrity", "HTML, text and security invariants", test_static_html)
    with sync_playwright() as pw:
        launch_kwargs = {"headless": True, "args": ["--no-sandbox"]}
        if CHROMIUM_EXECUTABLE:
            launch_kwargs["executable_path"] = CHROMIUM_EXECUTABLE
        browser = pw.chromium.launch(**launch_kwargs)
        record("Typography and threshold", "Distinct threshold, editorial and state typography", lambda: test_threshold_and_fonts(browser))
        record("Initial encounter", "Threshold entry and zero-progress attachment state", lambda: test_enter_and_initial(browser))
        record("Procedure", "Complete Yes/reporting path returns to renewed connection failure", lambda: test_full_yes_and_loop(browser))
        record("Procedure", "No branch returns to renewed connection failure without reporting lines", lambda: test_no_branch(browser))
        record("Utility", "About return and return-to-title routes", lambda: test_about_routes(browser))
        record("Interaction ownership", "Active shell semantics, inert background and no close control", lambda: test_shell_semantics_and_no_close(browser))
        record("Affordance", "Try again has a reduced, rhythmic call animation", lambda: test_retry_animation(browser))
        record("Poem inscription", "Lines fade in smoothly and create blood-light residue", lambda: test_poem_inscription(browser))
        record("Layer archive", "Long shell histories remain bounded, textless and ordered", lambda: test_historical_accumulation(browser))
        record("Long duration", "2,000 poem lines preserve scroll and return-to-latest", lambda: test_long_poem_and_scroll(browser))
        record("Responsive", "Desktop 1440×900 question geometry", lambda: test_viewport_geometry(browser, 1440, 900, "question", [{"label":"No","value":"no"},{"label":"Yes","value":"yes","primary":True}]))
        record("Responsive", "Desktop 1280×800 reporting geometry", lambda: test_viewport_geometry(browser, 1280, 800, "reporting"))
        record("Responsive", "Tablet 1024×768 failed geometry", lambda: test_viewport_geometry(browser, 1024, 768, "failed"))
        record("Responsive", "Mobile 430×932 question and underfield geometry", lambda: test_viewport_geometry(browser, 430, 932, "question", [{"label":"No","value":"no"},{"label":"Yes","value":"yes","primary":True}]))
        record("Responsive", "Mobile 390×844 connection and underfield geometry", lambda: test_viewport_geometry(browser, 390, 844, "connection", [{"label":"Try again","value":"retry","primary":True}]))
        record("Responsive", "Mobile 320×568 report-failed geometry", lambda: test_viewport_geometry(browser, 320, 568, "report-failed"))
        record("Mobile poem", "Compact, reading and expanded underfield snaps", lambda: test_mobile_snaps(browser))
        record("Mobile poem", "Visible fault-latch affordance expands and collapses the underfield", lambda: test_mobile_poem_affordance(browser))
        record("Responsive", "Short desktop report question preserves shell, controls and composer clearance", lambda: test_short_desktop_question_layout(browser))
        record("Layer archive", "Historical frames accumulate in a bounded ordered direction", lambda: test_ordered_residue_geometry(browser))
        record("Accessibility", "Reduced-motion mode suppresses call animation", lambda: test_reduced_motion(browser))
        record("Visual proportion", "State type remains proportionate to its shell", lambda: test_visual_fonts_and_scale(browser))
        record("Accessibility", "Primary visible controls meet practical target sizes", lambda: test_controls_targets(browser))
        browser.close()

    output = ROOT / "tests" / "qa-results.json"
    output.write_text(json.dumps([asdict(r) for r in RESULTS], indent=2), encoding="utf-8")
    failed = [r for r in RESULTS if not r.passed]
    print(f"{len(RESULTS)-len(failed)}/{len(RESULTS)} checks passed")
    for r in failed:
        print(f"FAIL [{r.family}] {r.name}: {r.detail}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(run())
