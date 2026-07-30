# UNHAPPY Scenario v2.6.0 — QA Report

## Release conclusion

**Passed.** The v2.4.0 baseline retains its **24 automated test suites**. This candidate adds **9 further suites** covering every objectively testable C01–C09 predicate from the creative implementation contract, for **33 automated test suites** total, followed by manual inspection of desktop, compact-desktop, tablet, mobile, long-loop, and visual-state renders. Automated checks establish objective behavior only; final artistic judgement remains Mohammad Zare's alone (see "Remaining limit").

## Automated verification

| Family | Coverage | Result |
|---|---|---:|
| Static integrity | Exact text, unique IDs, CSP, no external runtime APIs, no storage code | Passed |
| Typography and threshold | Distinct threshold, editorial, operational, state, and poem roles | Passed |
| Initial encounter | Threshold transition, pale image, zero-progress orbit, pending-message state | Passed |
| Procedure — Yes path | Failure → recovery → report → reporting failure → renewed connection failure | Passed |
| Procedure — No path | Refusal returns to renewed connection failure without false reporting lines | Passed |
| Utility routes | About, return, restart, and return to title | Passed |
| Interaction ownership | One active semantic shell, inert background, no shell Close/X | Passed |
| Retry affordance | Rhythmic active call and reduced-motion alternative | Passed |
| Poem inscription | Delayed fade, boundary registration, blood-light residue | Passed |
| Layer archive | Bounded, textless, directionally ordered historical frames | Passed |
| Long duration | 2,000 lines, review scrolling, return-to-latest | Passed |
| Responsive geometry | 320×568 through 1440×900 | Passed |
| Short desktop | 1051×566 question layout retains text, actions, and composer clearance | Passed |
| Mobile underfield | Compact, reading, expanded, tap-to-toggle, drag-ready affordance | Passed |
| Accessibility | Focus, semantics, target size, reduced motion | Passed |
| Visual proportion | State text and actions remain proportionate to shell geometry | Passed |
| C06 decision parity | Yes/No equal semantic and computed treatment, DOM order and focus unchanged | Passed |
| C09 no-branch closure | One nonverbal closure recorded per No, no reporting text, existing 650 ms interval | Passed |
| C05/C08 erosion and exhaustion | Retry credibility and process exhaustion decrease across cycles; locked timing map and hit target unchanged | Passed |
| C02 failed-transmission bridge | Event-bound, noninteractive (`pointer-events: none`), points to a real poem line | Passed |
| C01 poem field annexation | Grows from accumulated lines/cycles without obstructing messenger/composer | Passed |
| C03 historical shell pressure | Measurable, age-derived tonal displacement while remaining textless | Passed |
| C04 line-anchored bloom (desktop, mobile) | Bloom stays vertically anchored near its own line's real geometry | Passed |
| C07 mobile fault seam | Usable and unclipped at 320×568, 390×844, 430×932 | Passed |

The machine-readable record is in `tests/qa-results.json`.

## Layout and composition verification

### Desktop

- The messenger and poem field retain a controlled two-chamber composition.
- The procedural stage reserves the lower conversation region for the surviving message.
- Active shells remain above the composer and outside the poem field.
- Compact-desktop and short-height layouts use bounded minimum shell heights so action rows cannot be clipped.
- Question, process, failure, and reporting shells retain distinct proportions rather than sharing one modal template.

### Historical accumulation

- One active shell remains fully readable and interactive.
- At most six historical shells remain visible.
- Historical shells contain no readable text, controls, spinner, live region, or focus target.
- Retired shells reorganize around the active shell in one controlled direction: older frames move further left and lower, with restrained scale reduction.
- Long sequences remove the oldest visual frame while preserving every poem line.

### Mobile poem underfield

- The underfield remains unframed and cannot be mistaken for a message bubble.
- A visible black-and-rust fault-latch interrupts the boundary line.
- The latch has an illuminated node and directional chevrons reflecting compact versus expanded state.
- Its pointer target is at least 44 CSS pixels.
- A tap toggles compact and reading states; drag supports the expanded state.
- The control is not clipped and remains above the messenger/poem boundary.

## Branch and scenario coverage

- initial zero-progress transmission;
- upload failure and attachment disappearance;
- message failure and message-level retry;
- connection retry;
- reconnecting and terminal failure;
- reporting Yes and No branches;
- reporting failure and renewed loop;
- About pause and return;
- restart, return to title, and Escape;
- repeated shell generation;
- repeated poem accumulation;
- manual poem review and return to latest.

## UI, UX, and visual-layer review

Manual contact sheets cover threshold, sending, upload failure, message failure, connection failure, reconnecting, failure, report question, reporting, reporting failure, renewed connection failure, and About at desktop and mobile sizes.

Additional compact-desktop review verified the complete real route at 1051×566 after the attachment had disappeared. The report question, buttons, surviving message, composer, and poem remained distinct and unobstructed.

The retained visual system remains black-dominant, with bone text, restrained rust/blood energy, textless black shell residue, and slow blood-light accumulation beneath the poem.

## Privacy and integrity

- external runtime requests: **0**;
- external images: **0**;
- external fonts: **0**;
- network, analytics, cookies, and persistent-storage code: absent;
- attachment: embedded SVG;
- duplicate IDs: **0**;
- HTML structural parse: passed.

## Browser disclosure

Automated execution used **Chromium 144 on Linux** through Playwright. Firefox, WebKit, and real-device low-end performance are not claimed as tested in this environment.

## Defects found and corrected in this cycle

1. Compact desktop could compress report shells until their controls were visually clipped.
2. Percentage-based shell placement left too little reserved space above the surviving message at short heights.
3. Historical shells used alternating offsets that could read as scattered rather than accumulated.
4. The mobile poem control was visually too weak and was clipped by its parent overflow.
5. The previous tap cycle required an extra state before returning the underfield; tap now directly expands or collapses while drag retains full expansion.

## Adopted and declined decisions

The full list of adopted (C01–C09, preserved C10) and declined systems for this candidate is
recorded in `CHANGELOG.md` under v2.6.0. Declined: ambient event-driven optical field
modulation, attachment retinal afterimage, reporting-failure depth collapse.

## Remaining limit

The final aesthetic judgement remains artistic rather than fully automatable. Contact sheets and source-level design constraints are included for continued critique.
