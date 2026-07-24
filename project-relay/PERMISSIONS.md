# Permission policy

This repository layer does not change Claude Code settings or permission mode.

- Respect the permission mode selected by the user in the Claude Code UI.
- Do not create `.claude/settings*.json`, hooks, interceptors, or auto-allow profiles.
- Ask before dependency installation, commits, pushes, PRs, releases, deployment, migrations, cloud
  operations, secret-bearing operations, destructive deletion, or history rewrite unless the current
  user instruction explicitly authorizes the exact class of action.
- Never use `sudo`, force-push, hard reset, destructive `git clean`, or broad deletion without a new
  explicit user instruction.
