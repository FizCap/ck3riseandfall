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
- Interaction `ai_potential` blocks are evaluated with the interaction actor as the root scope only; `scope:actor`, `scope:recipient`, and other interaction event targets are unavailable there. Keep actor-only eligibility in `ai_potential` and put actor/recipient pair checks in `ai_will_do` or another block where both scopes are defined.
- Tooltip-evaluated triggers can read an unset `var:` even when placed beside `has_variable` in an `AND`. For optional object comparisons, use the repository's `var:name ?= scope:target` pattern rather than relying on short-circuiting.
- Income fields such as `yearly_character_income` and `year_character_treasury_variable_income` can supply numeric scripted values even though generated trigger documentation lists their comparison forms. For divided indemnities, calculate positive-clamped gold and treasury amounts in payer-scoped scripted values, then use `pay_short_term_gold` or `pay_short_term_treasury`; income-payment helpers reject negative net income.
- `spawn_army.location` requires a province event target; use `capital_province`, not `capital_barony`, when spawning at a character's capital.
- Keep on_action handlers small and dispatch to scripted effects with `effect = { ... }`. Gate game-rule mechanics with `has_game_rule`; define new rules in `common/game_rules/` with the `riseandfall` category.
- Yearly on-action loops such as `every_ruler` do not provide an implicit `root` scope; save the current character before entering a title or other nested scope when the effect must return to that character.
- When a trigger enters a character iterator but must compare candidates with the original character, save that character before the iterator and use a documented target trigger; direct comparisons such as `this = scope:name` are invalid.
- Character-target triggers documented with `Traits: character target` take the target character directly, such as `target_is_same_character_or_above = scope:saved_character`; do not wrap the target in a `{ target = ... }` block unless the generated trigger documentation explicitly shows that form. A nested scripted trigger may not retain the iterator caller's `root`; keep cross-scope comparisons at the iterator call site or pass an explicitly valid saved scope.
- For mechanics with an explicit title-level active-state marker, treat that marker as authoritative. Succession, trait assignment, and maintenance may preserve marked state but must not recreate a cleared marker from stale character traits.
- Feature-specific scripted-score bonuses must include the feature's current eligibility gate in every copied appointment or score definition; relationship and government checks alone are not sufficient.
- Temporary realm succession laws must be applied to the ruler whose realm enters the relevant state, store the prior law on a persistent primary-title variable, and restore it only after the triggering state is absent.
- Script-only laws must explicitly use `should_start_with = { always = no }`; omitting it can make the law win default-law selection even when `can_have` is false.
- Temporary inheritance succession laws that must exclude landed candidates should use the native `exclude_rulers = yes` rule; a negative candidate score does not make a landed character ineligible.
- Persistent diarchy states must use a dedicated marker and explicit removal effect; court-position synchronization and missing-candidate recovery may repair or defer the office, but must never end the diarchy implicitly.
- Add concise `#` comments for non-obvious scope changes, thresholds, weights, or math. Keep braces and block structure strict.
- When an effect resolves title or vassal changes inside a title/realm iterator, snapshot the target titles or counties into a list first and mutate them in a separate `every_in_list` pass; live collection mutation can invalidate vanilla on-action scopes.
- After using vanilla `depose_effect`, let normal succession distribute the deposed ruler's surviving titles unless the mechanic explicitly requires a different holder; a second manual title-transfer pass can override or duplicate vanilla inheritance.
- When every county held by an administrative sub-vassal is being reassigned, transfer the intact ruler to the destination liege instead of unlanding them; mixed holders can surrender only the offending counties.
- When a Story Mode event causes real realm fragmentation, apply a bounded collapse-pressure relief after title/vassal transfers and resync the primary-title copy; structural weakening should reduce an arc without deleting it.
- For standard realm splits, select successor anchors from the full eligible vassal pool and assign ordinary vassals individually through political/geographic influence; de-jure regions are soft cohesion and fallback aids, not mandatory anchor quotas.

## Localization And GUI
- Every UI-facing key must exist under `l_english:`. Check dynamic localization methods against the actual scope type. For saved event scopes, use the working direct form `[saved_name.GetName]`; `scope:` is script syntax and can break event tooltips when copied into localization.
- Match GUI `datacontext`, `datamodel`, and scripted GUI wrapper scopes exactly. Guard command buttons with `IsValidCommand` before `CreateCommandPopup` and guard list widgets against empty data.
- A standalone custom `.gui` file does not automatically register a HUD or game-view key. Put custom HUD panels inside an already-loaded HUD widget, usually behind a `GetVariableSystem` state flag. Recheck vanilla overrides and block names after CK3 patches.
- For custom content inside an existing vanilla window, override the GUI file that owns that window (often the complete vanilla window file) and insert the widget into its real tab/body block. A separate top-level `window` can parse successfully while never being instantiated by the existing game view. Preserve the vanilla window structure and types, then patch the copied override narrowly; for My Realm this means `gui/window_my_realm.gui`, not a detached companion window.

## Workflow
- Before editing, search for collisions and inspect the relevant reference log. After editing, check braces, duplicate event/script IDs, localization coverage, and scope/target types.
- For chained player-choice events, guard pending flags and required variables; save scopes before clearing receiver state, use `root = { ... }` when targeting that receiver, clear stale saved scopes, and trigger follow-up popups with `delayed = yes` after verifying the next target is still pending.
- Launch CK3 with the mod enabled, reproduce one minimal path per changed mechanic or screen, and use the game logs as the failure report. There is no repo-local parser or test runner.
- For CK3 behavior or UI changes, add a player-facing Steam Workshop entry to `ai_instructions/changelog.txt` using that file's existing version, header, and past-tense bullet format. Documentation-only changes do not need a changelog entry.
- When a fix reveals a reusable CK3 scope, token, ordering, encoding, runtime, or validation rule that is not already documented here, add a concise durable instruction to the relevant section of this file in the same change. Keep these additions general enough to prevent the class of bug from recurring; do not record temporary symptoms or one-off implementation details.
