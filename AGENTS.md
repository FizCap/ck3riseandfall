# Rise and Fall (CK3) Agent Instructions

## Repository
- This is a Crusader Kings III mod source tree, not a package project. `descriptor.mod` is the launcher metadata; check its `version`, `supported_version`, and `remote_file_id` before compatibility or release work. Do not add a `path=` entry or edit the installed CK3 `game/` directory.
- There is no package manifest, build/lint/typecheck configuration, CI workflow, or automated test suite in this repository. Do not invent package commands; static checks plus an in-game smoke test are the verification path.
- Preserve UTF-8 with BOM for CK3 `.txt`, `.yml`, and `.gui` files. Keep IDs stable and prefix new IDs and keys by their feature subsystem.

## Layout
- `common/` contains definitions: `on_action/` hooks vanilla pulses and events, `scripted_effects/` and `scripted_triggers/` hold reusable logic, `script_values/` holds formulas, `game_rules/` holds toggles, and `decisions/` and `character_interactions/` are player/AI entry points.
- `events/` contains event chains; `localization/english/` contains all UI-facing keys.
- `gui/` contains vanilla overrides and widgets; `common/scripted_guis/` bridges GUI actions to scripted effects. Read `ai_instructions/ck3-gui-modding-instructions.txt` before GUI work.
- Static modifiers belong in `common/modifiers/`; do not create or use a `common/static_modifiers/` folder.

## Source Of Truth
- Before using an unfamiliar CK3 token, check `docs/triggers.log`, `effects.log`, `event_scopes.log`, `event_targets.log`, or `on_actions.log`; GUI API tokens are in `docs/data_types*.txt`.
- Treat `.github/prompt` notes and other prose as cheatsheets; when they conflict with generated docs or working vanilla examples, trust the latter. Use installed vanilla files for examples only, never edit them.
- Search existing event IDs, script keys, and localization keys before adding new ones. Multiple files intentionally extend the same vanilla on_action; verify the hook name and expected scope in `docs/on_actions.log`.

## CK3 Scripting
- Validate every scope hop. Guard optional scopes with `exists` and optional variables with `has_variable`; saved scopes must retain the character, title, or province type expected by later code.
- Tooltip-evaluated triggers can read an unset `var:` even when placed beside `has_variable` in an `AND`. For optional object comparisons, use the repository's `var:name ?= scope:target` pattern rather than relying on short-circuiting.
- `spawn_army.location` requires a province event target; use `capital_province`, not `capital_barony`, when spawning at a character's capital.
- Keep on_action handlers small and dispatch to scripted effects with `effect = { ... }`. Gate game-rule mechanics with `has_game_rule`; define new rules in `common/game_rules/` with the `riseandfall` category.
- Add concise `#` comments for non-obvious scope changes, thresholds, weights, or math. Keep braces and block structure strict.

## Localization And GUI
- Every UI-facing key must exist under `l_english:`. Check dynamic localization methods against the actual scope type. For saved event scopes, use the working direct form `[saved_name.GetName]`; `scope:` is script syntax and can break event tooltips when copied into localization.
- Match GUI `datacontext`, `datamodel`, and scripted GUI wrapper scopes exactly. Guard command buttons with `IsValidCommand` before `CreateCommandPopup` and guard list widgets against empty data.
- A standalone custom `.gui` file does not automatically register a HUD or game-view key. Put custom HUD panels inside an already-loaded HUD widget, usually behind a `GetVariableSystem` state flag. Recheck vanilla overrides and block names after CK3 patches.

## Workflow
- Before editing, search for collisions and inspect the relevant reference log. After editing, check braces, duplicate event/script IDs, localization coverage, and scope/target types.
- For chained player-choice events, guard pending flags and required variables; save scopes before clearing receiver state, use `root = { ... }` when targeting that receiver, clear stale saved scopes, and trigger follow-up popups with `delayed = yes` after verifying the next target is still pending.
- Launch CK3 with the mod enabled, reproduce one minimal path per changed mechanic or screen, and use the game logs as the failure report. There is no repo-local parser or test runner.
- For CK3 behavior or UI changes, add a player-facing Steam Workshop entry to `ai_instructions/changelog.txt` using that file's existing version, header, and past-tense bullet format. Documentation-only changes do not need a changelog entry.
