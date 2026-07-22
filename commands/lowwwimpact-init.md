# lowwwimpact — Initialize project

Wire the lowwwimpact-helper skill into the current project with the fewest manual steps. This
finishes the setup after the skill folder has been cloned into
`<project>/.claude/skills/lowwwimpact-helper/`.

Run the **Init Workflow** defined in the skill (single source of truth):
`.claude/skills/lowwwimpact-helper/SKILL.md` → section **Init Workflow (Mode 0)**.

## What to do

1. **Resolve the skill directory.** Expect it at `<project>/.claude/skills/lowwwimpact-helper/`.
   If it is not there, stop and tell the user to clone it first.

2. **Copy the fix commands to the project.** Plain-copy every file from
   `<skill>/commands/*.md` into `<project>/.claude/commands/` (create the directory if needed;
   overwrite existing files so updates refresh). This includes `lowwwimpact-init.md` itself.

3. **Wire the companion block into `CLAUDE.md`.** Ensure `<project>/CLAUDE.md` exists (create it
   if missing). If it does not already contain the import line, append this block:

   ```markdown
   ## Sustainable-by-default (lowwwimpact companion)

   @.claude/skills/lowwwimpact-helper/companion.md
   ```

   **Idempotent** — if `@.claude/skills/lowwwimpact-helper/companion.md` is already present, do
   not add it again.

4. **Report.** List the commands copied and whether the companion import was added or already
   present.

## Notes

- Everything installs at the **project** level — nothing is written to `~/.claude`.
- To update later: re-copy the skill folder, then re-run this command to refresh the copied
  commands. `companion.md` updates automatically through the `@import` — no re-paste needed.
