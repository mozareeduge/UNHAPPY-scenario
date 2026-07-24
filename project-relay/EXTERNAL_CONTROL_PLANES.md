# External control planes

Capability is not authority. A connected API, MCP server, CLI, repository token, or deployment service
may be used only for systems and actions explicitly authorized by the active workload and user.

Before mutation: inventory the selected resource, save a sanitized snapshot, define rollback, and
verify the exact endpoint/command. After mutation: re-read the control plane and verify independent
postconditions. Never commit credentials or raw private account data.
