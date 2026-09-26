# Rise and Fall Agent Instructions

## Project

Rise and Fall is a Crusader Kings III mod. `descriptor.mod` is launcher metadata; this repository has no package build, lint, CI, or automated test suite. Use the game’s generated documentation and working vanilla examples as scripting references. Never edit installed vanilla game files.

## Start here

- Before compatibility or release work, inspect `descriptor.mod` and its version fields.
- Before adding IDs or localization, search for existing keys and collisions.
- Preserve UTF-8 with BOM in CK3 `.txt`, `.yml`, and `.gui` files. Keep IDs stable and prefix new IDs and keys with their feature subsystem.
- For an unfamiliar script token, consult the matching file under `docs/` (`triggers.log`, `effects.log`, `event_scopes.log`, `event_targets.log`, `on_actions.log`). For GUI APIs, consult `docs/data_types*.txt`.
- Static modifiers go in `common/modifiers/`.

## Detailed instructions

Load the reference that matches the task; do not load every guide for unrelated changes.

- [Scripting, scopes, decisions, and AI](ai_instructions/skills/ck3-scripting.md)
- [Titles, succession, court positions, and realm changes](ai_instructions/skills/ck3-realm-systems.md)
- [Events, localization, GUI, and player-facing workflow](ai_instructions/skills/ck3-ui-and-workflow.md)
- [CK3 GUI modding skill](ai_instructions/skills/gui/SKILL.md)

## Project-specific workflow

There is no repository test runner. For behavior or UI changes, static checks are only an initial check: launch CK3 with the mod enabled, reproduce a minimal changed path, and inspect game logs. Add player-facing gameplay/UI changes to `ai_instructions/changelog.txt` using its current version and past-tense format. Documentation-only changes do not need a changelog entry.

When adding behavior or non-obvious implementation logic, add a concise nearby comment explaining its purpose or constraints; do not merely restate the code.

When work uncovers a verified, reusable CK3 rule, engine behavior, implementation pattern, or validation finding, update the matching guide under `ai_instructions/skills/` in the same change. Keep the note scoped, fold it into an existing section when possible, and omit guesses or temporary symptoms.