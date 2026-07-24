# Operating safety

Do not install or initialize another agent framework. Do not modify Claude settings, permission mode,
hooks, `.git/info/exclude`, global Git configuration, or files outside the repository. Every change
must remain visible in `git status` and the draft PR. Dependency installation, commit, push, and draft
PR creation are authorized for this task; merge, release, deployment mutation, and repository settings
are not.
