# UNHAPPY Scenario
## Final Design and Technical Specification — v2.6.0

v2.6.0 implements the approved atelier decisions C01–C09 on top of this specification's v2.4.0
baseline, unchanged below. See `CHANGELOG.md` (v2.6.0) for the full adopted/declined system list
and `design/CREATIVE_IMPLEMENTATION_CONTRACT.md` (execution package, external to this repository)
for each system's predicates.

## 1. Artistic proposition

A message attempts to leave through an apparently powerful communications environment. The image cannot begin to upload, language remains suspended, and every mechanism of recovery or accountability becomes another failure. The interface accumulates black procedural frames while the poem receives the system messages.

## 2. Textual constitution

### Locked poem messages

1. Upload failed
2. Sending the message failed
3. Connection attempt failed
4. Reconnecting…
5. Failed
6. Do you want to report the problem?
7. Reporting the problem…
8. Reporting failed

### Interface actions excluded from the poem

Enter · Try again · Yes · No · Return · Restart encounter · Return to title · About

### Carrier texts

UNHAPPY Scenario · An Internet Blackout Poem · by mozare · N. · Here it is.

## 3. Spatial composition

### Wide desktop

The artwork uses two co-present chambers: messenger/failure apparatus and poem field. The poem occupies a narrower inscription region. The active procedural shell is constrained to a dedicated stage inside the conversation, with a lower reservation for the surviving outgoing message.

### Compact desktop and tablet

The two-chamber relation remains, but spacing and poem width contract. Shells use explicit minimum and maximum heights, preventing questions and action rows from collapsing at short viewports.

### Mobile

The messenger and poem become vertically related. The poem is an unframed underfield. A visible fault-latch at the boundary provides the affordance to expand or collapse the reading region; dragging can reach the expanded state.

## 4. Shell family

Each state has a distinct geometry. No procedural shell contains an X or Close control.

The active shell contains the current phrase and only its required actions. Up to six historical shells remain as textless black frames. Their centres align with the active shell and recede in one controlled direction, with bounded offset, scale, and opacity.

State-specific bounds:

- connection and renewed connection: medium horizontal shells;
- reconnecting and reporting: compact process shells;
- Failed: dense terminal shell;
- reporting question: broader shell with protected action height;
- reporting failed: compact institutional failure shell.

## 5. Poem field

Desktop uses an unframed right inscription field. Mobile uses an unframed lower underfield. A boundary registration precedes each line; the line then fades from blur and a small vertical offset. Each inscription creates a restrained blood-light bloom beneath the text.

The poem contains system messages only. `Try again` remains an interface action.

## 6. Mobile fault-latch

The fault-latch is a real button with a 48-pixel high interaction region. Its visible element is a black, faceted interruption in the fault line with:

- a blood-red illuminated node;
- upward and downward chevrons;
- compact-state emphasis on expansion;
- reading/expanded-state emphasis on collapse;
- a low-frequency breath animation removed under reduced motion.

Tap toggles compact and reading states. Drag preserves compact, reading, and expanded snap selection.

## 7. Interaction principles

- Actions become available independently of poem inscription.
- Only the active shell is interactive and semantically current.
- Messenger header, message lane, and composer become inert while a shell owns interaction.
- Historical shells are inert and absent from the accessibility tree.
- About is an artwork-level utility and pauses timed progression.

## 8. Visual system

The dominant field is black. Bone carries language. Rust and blood-red remain local energy rather than dominant panel color. The v2.3 material atmosphere, typography, restrained linework, and blood-light poem field are preserved.

## 9. Accessibility and privacy

Native buttons, clear focus, target sizing, reduced motion, reduced transparency, forced colors, print, and no-script modes are included. No real upload, message, connection check, report, analytics, cookie, storage, or external runtime request occurs.

## 10. Release blockers

The release is blocked if any shell enters the poem field, overlaps the composer, clips its action row, retains historical text, grows beyond six visual residues, hides the mobile underfield affordance, inserts `Try again` into the poem, or produces external runtime activity.
