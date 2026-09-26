# CK3 Events, Localization, GUI, and Project Workflow

Read this guide for event chains, localization, UI changes, changelog entries, and verification. For GUI work, load the [GUI skill](gui/SKILL.md), then consult its API and project-pattern references as needed.

## Events and localization

- Every player-facing key must exist under `l_english:`. Verify dynamic localization methods against the actual scope type. For saved event scopes, use the working direct form `[saved_name.GetName]`; script syntax such as `scope:` can break event tooltips.
- For chained player-choice events, guard pending flags and required variables. Save scopes before clearing receiver state; use `root = { ... }` when targeting that receiver. Clear stale saved scopes and trigger a follow-up popup with `delayed = yes` only after checking the next target is still pending.

## GUI entry point

- Read `ai_instructions/skills/gui/SKILL.md` before GUI work. It covers local API references, scope/datacontext matching, real list sources, command validity, localization, vanilla overrides, and in-game checks.
- In brief: a standalone `.gui` file does not register a HUD/game-view key. Place custom HUD panels inside an already-loaded HUD widget, usually behind a `GetVariableSystem` flag. For existing windows, patch the file that owns the window and insert into its actual tab/body while preserving the vanilla structure.

## Review and validation

- Before editing, search for existing IDs, script keys, and localization keys. Verify unfamiliar syntax against generated docs and working vanilla examples.
- After editing, inspect braces/block structure, duplicate IDs, loc coverage, and scope/target types. For CK3 `.txt`, `.yml`, and `.gui` files, preserve UTF-8 BOM.
- There is no repo-local parser or test runner. Use focused static checks, then launch CK3 with the mod enabled and reproduce at least one minimal path per changed behavior or screen. Read game logs as the runtime failure report; report clearly when only source-level checks were possible.
- For a behavior or UI change, add a player-facing entry to `ai_instructions/changelog.txt`, following its current version/header and past-tense bullet style. Documentation-only changes need no entry.
- Before compatibility/release work, check `descriptor.mod` version metadata. Do not add `path=` or edit the installed CK3 `game/` directory.