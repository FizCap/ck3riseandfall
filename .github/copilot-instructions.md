```instructions
# Copilot instructions for the Rise and Fall mod — LLM-friendly (CK3)

Purpose
- Make this repository immediately usable by automated agents and human contributors. This file combines repo-specific rules with concrete CK3 modding patterns and an explicit LLM "contract" so an agent knows how to act safely and effectively.

Quick start checklist (high value, do these first)
- Open `descriptor.mod` and confirm: name, path, supported_version.
- Read `docs/triggers.log` and `docs/event_scopes.log` to confirm scope tokens and trigger signatures.
- Search `events/`, `common/`, and `localization/english/` for the IDs you plan to change.
- Never edit the global `game/` folder — place overrides under this repo.

LLM contract (short, strict)
- Always prefer vanilla engine patterns from `game/` and `docs/` logs. Do not invent new engine tokens.
- For any change: produce a 2–4 bullet contract (inputs, outputs, data shape, error modes).
- Run local validation steps after edits: syntax check (brace balance), duplicate-ID scan, and verify localization coverage.
- When editing multiple files, include a concise summary list of changed files and why.
- If a required file or engine log is missing, stop and ask for it instead of guessing.

Repository structure (one-paragraph)
- CK3 mod; data-driven text files. No compile step — the game loads scripts directly. Primary folders: `common/` (defines, scripted_effects, modifiers), `events/`, `localization/english/`, and `docs/` (engine-generated reference logs).

Minimal engineering contract for script changes
- Inputs: file(s) modified (path + brief purpose), expected in-game scope(s), and any new localization keys.
- Outputs: changed game behavior (short description), localization entries, and tests/method to validate.
- Success criteria: files load without engine errors, loc keys present, and behavior reproduces in a minimal in-game test.
- Error modes: missing loc keys (raw keys shown), silent trigger scope mismatches, duplicate IDs causing collisions.

Best-practice checklist for edits
- Use `riseandfall.` as your ID prefix when adding events/effects/modifiers.
- Place permanent modifiers in `common/static_modifiers/`; put temporary or computed modifiers in `common/scripted_modifiers/`.
- Register `on_actions` in `common/on_actions/` and call scripted effects with `effect = { your_effect = yes }`.
- Always add `l_english:` entries for any UI-facing keys.
- Use `docs/` logs to validate valid tokens and scope support before saving changes.

Edge cases & gotchas (short list)
- Mis-scoped trigger: trigger silently does nothing — verify scope via `docs/event_scopes.log`.
- Missing localization: the game displays raw keys — add corresponding `localization/english/*.yml` entries.
- Duplicate IDs: first file wins — run a duplicate-ID scan before committing.
- Infinite modifier loops: always check `has_modifier` before applying a modifier and include removal logic.

Scope patterns & helpers
- Default scope depends on file location. To change scope explicitly use `owner = { ... }`, `ruler = { ... }`, `state = { ... }`, `holder = { ... }`.
- Iteration helpers: `any_` (trigger check), `random_` (effect helper for a single element), `every_` (apply to all matched elements).
- Save dynamic scopes: `save_scope_as = my_scope` then reference `scope:my_scope`.

Small examples (copyable patterns)
- on_action registration
  riseandfall_example_on_action = {
      effect = {
          riseandfall.example_effect = yes
      }
  }

- scripted effect calling create_character
  riseandfall.make_heir = {
    create_character = {
      age = { 0 8 }
      culture = ruler.culture
      religion = ruler.religion
      heir = yes
    }
  }

- defensive modifier application
  riseandfall_safe_apply = {
    if = {
      limit = { NOT = { has_modifier = riseandfall_temp_mod } }
      add_modifier = { name = riseandfall_temp_mod duration = 365 }
    }
  }

Debugging & quality gates (run these before committing)
1) Brace balance & syntax: visually or via editor plugin.
2) Duplicate-ID scan (suggested helper): `riseandfall/tools/duplicate-ids.ps1`.
3) Missing localization scan: `riseandfall/tools/missing-loc.ps1` (find referenced keys without `localization/` entries).
4) Smoke test: load CK3 with the mod enabled and verify the minimal repro (one event or effect triggers as expected).

Developer helper scripts (suggested)
- `riseandfall/tools/duplicate-ids.ps1` — scans repo for duplicate event/effect IDs.
- `riseandfall/tools/missing-loc.ps1` — finds referenced localization keys that are missing in `localization/english/` files.

When to ask for help
- Provide failing engine log lines, the exact file(s) you edited, and a minimal reproduction scenario when asking for troubleshooting.

Files & docs to consult
- `docs/triggers.log`, `docs/event_scopes.log`, `docs/effects.log`, `docs/modifiers.log`, `docs/on_actions.log`, `docs/event_targets.log`.

If something is unclear, provide the exact file paths or engine log lines and I will inspect `docs/` and the target files and suggest fixes.

```
```instructions
# Copilot instructions for the Rise and Fall mod (merged & CK3-adapted)

Purpose
- Short, focused instructions to make AI coding agents immediately productive in this repository. This file combines repo-specific guidance with consolidated lessons, best practices, and patterns for Crusader Kings III modding.

Quick checklist (what to do first)
- Open `descriptor.mod` to confirm mod metadata (name, path, supported_version).
- Read `docs/triggers.log` and `docs/event_scopes.log` for canonical trigger and scope behavior used by the mod.
- Inspect `events/`, `common/`, and `localization/english/` when changing behavior; these are the primary content surfaces.
- Never change `game/` files—create or edit files under this repo's root only.

Big picture (how this project is structured)
- This repository is a Crusader Kings III mod: data-driven, text-based content. There is no compilation step — edits are validated in-game.
- Major components:
  - `common/` — rules, scripted effects, modifiers and definitions (constants live in `common/defines`).
  - `events/` — event scripts using namespaced IDs (use `riseandfall.` prefix).
  - `localization/english/` — `l_english:` YAML files; every referenced loc key must exist here.
  - `docs/` — autogenerated engine reference logs (`triggers.log`, `event_scopes.log`, `effects.log`) — treat these as authoritative when adding triggers or changing scopes.

Data flow
- Events/scripted_effects (in `events/` and `common/scripted_effects/`) reference constants in `common/defines/*` and localization keys in `localization/`. Scope correctness (character/title/province) is critical — see `docs/event_scopes.log`.

Project-specific conventions and patterns
- Namespace everything: use `riseandfall.` prefix for events, scripted effects and decisions. Grep for your ID before committing.
- Keep `descriptor.mod` metadata accurate: path must match your mod folder and `supported_version` should match the tested CK3 build (current repo: `supported_version="1.16.2.3"`).
- Scope-first: consult `docs/event_scopes.log` for scope tokens (char, lt, prov, etc.) — many silent failures are mis-scoped triggers.
- Localization-first: every UI/event key (title/desc/option) must be present under `localization/english/*.yml` using `l_english:` header; missing keys render as raw identifiers in-game.
- Use `docs/*.log` as the primary reference when choosing triggers/effects; they reflect the local engine surface the mod targets.

Critical developer workflows
- Edit → test in-game: no compile step. Reload the mod in CK3 and test minimal repros for events and triggers.
Quick pre-test checklist
- Confirm `descriptor.mod` (name/path/supported_version).
- Ensure text files are UTF-8 without BOM and adhere to CK3 curly-brace format.
- Run quick checks: brace balance, duplicate-ID scan, and loc-key presence before starting the game.
Use `docs/` logs to validate trigger signatures and scope usage before editing events.

Integration points & external dependencies
- Engine integration: files are interpreted directly by CK3; changes take effect when the game loads the mod.
- Cross-file links: events often call scripted_effects, modifiers, add/remove modifiers, and localization keys. Update all referenced files together to avoid runtime errors.

What to avoid / common pitfalls
- Never edit the global `game/` folder. Add overrides inside this repo.
- Missing localization shows raw keys in-game — always add `l_english:` entries for any new loc keys.
- Mis-scoped triggers are silent failures; validate scopes in `docs/event_scopes.log`.
- Duplicate IDs: first-come wins; run a duplicate-ID scan (suggested script location: `riseandfall/tools/duplicate-ids.ps1`).

Merged CK3-specific lessons & best practices
-----------------------------------------

1. Lessons Learned & Common Pitfalls
- Unsupported / non-vanilla syntax: avoid using syntax that isn't present in vanilla CK3 files. When unsure, copy the pattern from `game/` or `docs/` logs. Nonstandard tokens silently fail.
- on_actions and effect blocks: register `on_actions` using an `effect = { ... }` block that calls scripted effects; don't attempt to embed reusable `effect =` blocks inside `scripted_effect` definitions where the engine expects a call.
- Modifiers placement: permanent or recurring country modifiers belong in `common/static_modifiers/` (or the equivalent static modifier file), not as ephemeral scripted modifiers. Use `common/scripted_modifiers/` only for temporary, calculated modifiers.
- Game rules & conditional logic: gate gameplay changes and journal entries with `has_game_rule` in `possible` blocks so they fully disable behavior when the rule is off (putting checks only in `is_shown_when_inactive` will only hide UI, not stop activation).
- Temporary vs permanent modifiers: prefer block syntax for time-limited modifiers (include `days = N` or the temporary block) and omit time fields for permanent modifiers.
- Defensive modifier handling: always check `has_modifier` (or similar) before adding modifiers to avoid stacking/looping issues; add explicit removal logic for temporary modifiers when their window expires (for example, after a historical date or a scripted cutoff).
- Localization coverage: every scripted effect, event, decision, journal entry, and modifier that appears in UI or logs must have localization entries in `localization/english/*.yml` under the `l_english:` header.

2. Best Practices
- Follow vanilla patterns for `on_actions`, `scripted_effects`, `scripted_triggers`, and `scripted_modifiers`—vanilla is the canonical source for supported syntax and scope behavior.
- Keep static game-changing modifiers in static modifier files; use scripted modifiers for computed temporary values only.
- Use `has_game_rule` and proper `possible` checks to fully disable/enable systems controlled by game rules.
- Remove or clean up time-limited state when it is no longer relevant (historical cutoffs, war end, ruler death, etc.).
- Ensure all scripted effects and on_actions are callable and registered; trace from on_action → scripted_effect → localization.

3. Scope Usage & Patterns
- Every effect/trigger/on_action begins in a default scope (character, title, county, province, realm, etc.). Consult `docs/event_scopes.log` for what each token accepts.
- Switch explicit scopes using `owner = { ... }`, `ruler = { ... }`, `state = { ... }`, `holder = { ... }` as appropriate to the action.
- Use `any_`, `every_`, and `random_` where applicable: `any_` is typically a trigger check (do any elements match?), `random_` acts on a single chosen element, and `every_` performs effects for all matching elements.
- Save dynamic scopes with `save_scope_as = X` and reference them as `scope:X` when needed.

4. Directory Structure & File Placement (CK3)
- New `on_actions` live under `common/on_actions/`.
- New scripted effects go in `common/scripted_effects/` (use a repo prefix, e.g., `riseandfall_` or `rf_`).
- New scripted triggers go in `common/scripted_triggers/` (prefix similarly).
- Scripted modifiers belong in `common/scripted_modifiers/`.
- Put permanent modifiers in `common/static_modifiers/` when appropriate.

5. Scripting Keyword Patterns
- any_ is a trigger (checks any element in a collection).
- random_ is an effect helper (acts on one chosen element).
- every_ is an effect helper (acts on all matched elements).

6. Debugging & Validation
- Validate all referenced scripted effects, triggers and modifiers exist before loading the game.
- Check that `on_actions` are registered and correctly scoped in the main file.
- Trace the full flow from trigger → effect and validate scope usage at each step.
- Use the `docs/` logs (provided in this repo) for supported tokens and scopes.
- For quick syntax checks you can use editor search and the engine logs when running the game—watch for missing localization keys and duplicate IDs.

7. Modding Conventions (project-specific)
- Namespace IDs: prefer the `riseandfall.` prefix for events, scripted effects and decisions; do a grep for your ID before committing to avoid duplicates.
- Converter or machine-generated files can use `zzz_` or `99_` prefixes to ensure load order.
- Localization keys for new features should follow the `riseandfall.` or `rf_` naming pattern and live in `localization/english/`.
- Document non-obvious intent with comments, especially for complex scope switches or cross-file interactions.

8. Example Patterns (CK3)
- On_Action registration calling a scripted effect
  riseandfall_harsh_law_on_action = {
      effect = {
          riseandfall.apply_harsh_law = yes
      }
  }

- Creating a character (used in events / scripted effects)
  create_character = {
    age = { 0 8 }
    culture = ruler.culture
    religion = ruler.religion
    heir = yes
  }

- Preventing modifier loops
  riseandfall_heir_storage = {
    trigger = {
      is_monarch = yes
      NOT = { has_modifier = riseandfall_has_an_heir }
      owner = { NOT = { any_scope_character = { is_heir = yes is_character_alive = yes } } }
    }
    effect = {
      riseandfall_heir_storage_effect = yes
    }
  }

9. Useful Documentation Files (already in this repo)
- `docs/effects.log`: list of effects and supported scopes
- `docs/triggers.log`: list of triggers and supported scopes
- `docs/modifiers.log`: list of modifiers and descriptions
- `docs/on_actions.log`: list of on_actions and expected scopes
- `docs/event_targets.log`: list of event targets and input/output scopes

10. Developer Workflow (CK3)
- No compile step: validate changes by launching Crusader Kings III with the mod enabled and test minimal reproductions for events and triggers.
- Update both scripting files in `common/` and matching localization entries in `localization/` for any new mechanics.
- Use `docs/` logs to validate trigger signatures and scope usage before editing events.
- Suggested low-risk extras the AI agent can add: small tests for duplicate IDs or missing loc keys under `riseandfall/tools/`.

If something is unclear, request the exact file(s) or failing engine log lines and I will inspect `docs/` and the target files and suggest fixes.

```
# Copilot instructions for the Rise and Fall mod

Purpose
- Short, focused instructions to make AI coding agents immediately productive in this repository. Merge of repo-specific LLM guidance included.

Quick checklist (what to do first)
- Open `descriptor.mod` to confirm mod metadata (name, path, supported_version).
- Read `docs/triggers.log` and `docs/event_scopes.log` for canonical trigger and scope behavior used by the mod.
- Inspect `events/`, `common/`, and `localization/english/` when changing behavior; these are the primary content surfaces.
- Never change `game/` files—create or edit files under this repo's root only.

Big picture (how this project is structured)
- This repository is a Crusader Kings III mod: data-driven, text-based content. There is no compilation step — edits are validated in-game.
- Major components:
  - `common/` — rules, scripted effects, modifiers and definitions (constants live in `common/defines`).
  - `events/` — event scripts using namespaced IDs (use `riseandfall.` prefix).
  - `localization/english/` — `l_english:` YAML files; every referenced loc key must exist here.
  - `docs/` — autogenerated engine reference logs (`triggers.log`, `event_scopes.log`, `effects.log`) — treat these as authoritative when adding triggers or changing scopes.

Data flow
- Events/scripted_effects (in `events/` and `common/scripted_effects/`) reference constants in `common/defines/*` and localization keys in `localization/`. Scope correctness (character/title/province) is critical — see `docs/event_scopes.log`.

Project-specific conventions and patterns
- Namespace everything: use `riseandfall.` prefix for events, scripted effects and decisions. Grep for your ID before committing.
- Keep `descriptor.mod` metadata accurate: path must match your mod folder and `supported_version` should match the tested CK3 build (current repo: `supported_version="1.16.2.3"`).
- Scope-first: consult `docs/event_scopes.log` for scope tokens (char, lt, prov, etc.) — many silent failures are mis-scoped triggers.
- Localization-first: every UI/event key (title/desc/option) must be present under `localization/english/*.yml` using `l_english:` header; missing keys render as raw identifiers in-game.
- Use `docs/*.log` as the primary reference when choosing triggers/effects; they reflect the local engine surface the mod targets.

Critical developer workflows
- Edit → test in-game: no compile step. Reload the mod in CK3 and test minimal repros for events and triggers.
Quick pre-test checklist
- Confirm `descriptor.mod` (name/path/supported_version).
- Ensure text files are UTF-8 without BOM and adhere to CK3 curly-brace format.
- Run quick checks: brace balance, duplicate-ID scan, and loc-key presence before starting the game.
Use `docs/` logs to validate trigger signatures and scope usage before editing events.

Integration points & external dependencies
- Engine integration: files are interpreted directly by CK3; changes take effect when the game loads the mod.
- Cross-file links: events often call scripted_effects, modifiers, add/remove modifiers, and localization keys. Update all referenced files together to avoid runtime errors.

Examples (concrete patterns)
- `descriptor.mod` (repo uses): name="Rise and Fall", path="mod/riseandfall", supported_version="1.16.2.3".
- Event + loc pattern: `riseandfall.1 = { ... }` with loc keys `riseandfall.1.t`, `.d`, `.a` in `localization/english/*.yml`.
- Use `docs/triggers.log` and `docs/event_scopes.log` as authoritative references.

What to avoid / common pitfalls
- Never edit the global `game/` folder. Add overrides inside this repo.
- Missing localization shows raw keys in-game — always add `l_english:` entries for any new loc keys.
- Mis-scoped triggers are silent failures; validate scopes in `docs/event_scopes.log`.
- Duplicate IDs: first-come wins; run a duplicate-ID scan (suggested script location: `riseandfall/tools/duplicate-ids.ps1`).

If something is unclear
- Request the exact file(s) or the failing in-game log lines; provide the minimal reproducer and I will inspect `docs/` and the target files and suggest one or two fixes.

Quick actionable additions (what this AI agent can do next)
- Add the two PowerShell helpers under `riseandfall/tools/` (`duplicate-ids.ps1`, `missing-loc.ps1`) and run them across the mod.
- Create a small example payload (descriptor, one event, localization, scripted_effect) under `events/` + `localization/` to illustrate best practices.

Feedback
- If anything here is too terse or you want line-level examples from specific event files, tell me which file and I will expand this guidance.
