# H3 Prompt Tool Maintenance Rules

## Required update targets

Unless the user explicitly narrows the scope, every functional or user-visible update to this tool must be synchronized to all three locations:

1. `G:\AI\Faithful-H3-Web` - active local deployment.
2. `D:\AI\Faithful-H3-Web` - local distribution/source copy.
3. GitHub repository `wodeshijie1234/faithful-h3-web` - committed and pushed to `main`.

Before reporting completion, verify the active local service uses the updated G-drive source, run relevant automated tests, and report any blocked synchronization truthfully.
