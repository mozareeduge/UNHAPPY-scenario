# Security audit and correction record

## Removed from v4.2

The following mechanisms were removed because they created a hidden or persistent control plane:

- modification of `.git/info/exclude`;
- installation under `.claude/` and `CLAUDE.local.md`;
- rewriting `.claude/settings.local.json`;
- forcing `acceptEdits` or changing bypass-permission settings;
- PreToolUse/PostToolUse hooks and command interception;
- automatic Cloudflare MCP allow/deny hooks;
- hidden HMAC keys and runtime manifests under `.git/relay/`;
- a fixed `READY_FOR_WORKLOAD` compliance token;
- instructions not to inspect the package.

## Retained safely

- explicit authority and scope ordering;
- active workload packages with manifest verification and path-traversal protection;
- bounded repository mapping;
- named deterministic checks;
- material-content fingerprints;
- transparent evidence records and logs;
- finite completion contracts;
- bounded final review;
- explicit external-system authority and rollback requirements.

## Trust boundary

This package can structure work, but it cannot grant itself permissions. Claude Code session settings,
repository permissions, credentials, push/PR authority, and deployment authority remain under user and
platform control. All repository changes must remain visible and reviewable.
