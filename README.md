# UNHAPPY Scenario

**by Mohammad Zare (Mozare) · version 2.6.0 · [Experience the work](https://unhappy.theblackbirdfield.com/)**

*UNHAPPY Scenario* is an internet blackout poem, an English-language browser work.

**The work's statement**

> Software calls the route away from success an unhappy scenario. The phrase makes interruption sound manageable: a branch to be anticipated, named, and recovered from.
>
> UNHAPPY Scenario stays with that calm language after recovery has ceased to be credible. Drawn from the small notices through which systems explain failure and promise return, the poem carries their familiar English into the memory of repeated internet blackouts in Iran. What begins as technical inconvenience becomes a vocabulary for isolation, deferred contact, and an accountability that cannot be reached.

**Status:** published work, English edition, version 2.6.0; this repository is its public source.

**How to cite:** Zare, M. (2026). *UNHAPPY Scenario: An Internet Blackout Poem* (Version 2.6.0) [Electronic literature]. https://unhappy.theblackbirdfield.com/

**Rights:** Copyright 2026 Mohammad Zare. Quotation, scholarly discussion, review and archival description are permitted with attribution; reproduction, adaptation, exhibition or republication of the complete work requires permission. See [RIGHTS.md](RIGHTS.md).

---

## Engineering notes

`index.html` is the complete standalone artwork. It contains no external runtime dependency and performs no upload, message transmission, connectivity test, report, analytics request, cookie write, or persistent-storage operation.

## Encounter

Open `index.html` in a current browser. The work begins at its authored threshold. The operational sequence develops through the messenger and the accumulating poem field.

On mobile, the illuminated fault-latch at the boundary of the poem underfield can be tapped to expand or collapse the reading area and dragged for the expanded reading state.

## Locked system-message core

- Upload failed
- Sending the message failed
- Connection attempt failed
- Reconnecting…
- Failed
- Do you want to report the problem?
- Reporting the problem…
- Reporting failed

`Try again` is an interface action and is excluded from the poem.

## Package

- `index.html` — standalone artwork
- `procedure-text.txt` — locked textual constitution
- `statement.txt` — approved concise statement
- `QA_REPORT.md` — verification record
- `CHANGELOG.md` — release history
- `CITATION.cff` — citation metadata
- `RIGHTS.md` — rights note
- `checksums.sha256` — release hashes
- `docs/FINAL_DESIGN_AND_TECHNICAL_SPEC.md` — implementation specification
- `docs/CHANGE_INTEGRATION.md` — revision record
- `docs/desktop_state_contact_sheet.png` — desktop visual review
- `docs/mobile_state_contact_sheet.png` — mobile visual review
- `tests/qa.py` — browser and structural QA harness
- `tests/render_visuals.py` — visual-state renderer

## Technical profile

- semantic HTML, CSS, and vanilla JavaScript
- deterministic finite-state and loop logic
- self-contained pale image as inline SVG
- one active shell plus a maximum of six ordered historical frames
- unbounded textual procedure
- visible mobile textual-underfield affordance
- reduced-motion, reduced-transparency, forced-colors, print, and no-script handling
- restrictive Content Security Policy
