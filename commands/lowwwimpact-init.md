# lowwwimpact — Install into this project

Finishes setup after the skill folder has been cloned into the project. Idempotent — safe to
re-run after an update.

Run the **Install Workflow** defined in the skill (single source of truth): `SKILL.md` →
section **Install Workflow**. The summary below is for orientation.

## What to do

### 1. Detect the host

Find where the skill actually lives and derive the destinations from it:

| Skill directory | Host | Commands → | Passive → |
|---|---|---|---|
| `.claude/skills/lowwwimpact-helper/` | Claude Code | `.claude/commands/` | `AGENTS.md`, plus `@AGENTS.md` in `CLAUDE.md` |
| `.opencode/lowwwimpact-helper/` | opencode | `.opencode/commands/` | `AGENTS.md` |
| `.cursor/skills/lowwwimpact-helper/` | Cursor | `.cursor/commands/` | `AGENTS.md` |

If more than one matches, ask which host to install for. If none matches, ask where the skill lives
rather than guessing.

### 2. Copy the commands

Plain-copy every file from `<skill>/commands/*.md` into the host's command directory. Create the
directory if needed; overwrite existing files so updates refresh. This includes
`lowwwimpact-init.md` itself.

**Do not add YAML frontmatter.** These files are plain markdown precisely so the same file works
unchanged in every host.

### 3. Install passive mode into `AGENTS.md`

Ensure `<project>/AGENTS.md` exists, then inject the contents of `<skill>/passive.md` between
marker comments:

```markdown
<!-- lowwwimpact:passive:start -->
…contents of passive.md…
<!-- lowwwimpact:passive:end -->
```

**Idempotent by replacement**: if both markers are already present, replace everything between
them. Only append the block when the markers are absent. Never write it twice.

### 4. Claude Code only — point `CLAUDE.md` at `AGENTS.md`

Ensure `<project>/CLAUDE.md` contains the single line `@AGENTS.md`. Skip if already present.

### 5. Report

State the host detected, list the commands copied, and say whether the passive block was added or
replaced.

## Notes

- Everything installs at the **project** level — nothing is written to `~/.claude` or equivalent.
- Passive content is **injected, not imported**, because `@path` imports are Claude Code syntax and
  the `AGENTS.md` convention has no portable import mechanism. The trade-off: the block goes stale
  when the skill updates. Re-run this command to refresh it, the same way you refresh the commands.
- To update: re-copy the skill folder, then re-run `/lowwwimpact-init`.
