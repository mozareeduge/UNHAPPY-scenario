# Core execution model

## Reconcile before changing

Read the mission, requirements, decisions, in/out scope, workmap, and the active task's `read_refs`.
Search before full reads. For a clear local task, implement directly. For unfamiliar or cross-cutting
work, create a bounded repository map and a short implementation sequence, then work in the same run.

## Execute

- Reach a real vertical path early.
- Preserve exact text, data, citations, rights, design invariants, and public/private boundaries named
  by the workload.
- Preserve unrelated changes.
- Use one main agent. Use at most one bounded explorer and one bounded final reviewer when justified.
- Do not rerun an unchanged failure. Diagnose the smallest reproducer, change strategy, then rerun.
- Keep full logs on disk and summarize only bounded tails in conversation.

## Safety

Use the session's existing permission mode. Never modify permission settings or install hooks. Ask
before dependency installation, push/PR/release/deployment, destructive operations, or external
mutations unless the user's current instruction already provides exact authority.

## Completion

Compute the current material fingerprint, run the required named checks, close blocking findings, and
run the finite completion verifier. When it passes, stop. Report exact artifacts, checks, Git/CI/live
identity, limitations, and the single genuine manual action only when unavoidable.
