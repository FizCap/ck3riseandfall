LLM-friendly scope notes for Rise and Fall mod

Purpose
- Short cheatsheet for future LLM edits: scope behaviors, common pitfalls, and quick fixes.

1) Scope basics
- Event scope defaults depend on file location. Many on_action effects start with character scope when run via `every_ruler`/`every_independent_ruler`.
- Common scope types you'll encounter:
  - character: use character-only triggers/effects and variables stored on characters.
  - title/holder: used when manipulating titles, succession, or de jure operations.
  - province: used for spawn locations, province-level effects, and many on-map operations.
  - barony: rarely used directly for spawn_army; prefer province-level locations.

2) Saving & referencing scopes
- save_scope_as = name stores the current scope under `scope:name` for later use in the same unbroken event chain.
- When referencing saved scopes later, ensure you're using the correct target type. Example: `scope:independent_ruler.capital_province` (province) vs `scope:independent_ruler.capital_barony` (barony).
- Use `save_scope_as` only when the saved object will be valid for the later effect's expected event_target.

3) Variables
- set_variable = { name = X value = Y } makes the variable available as `var:X` in the same top scope or `scope` context.
- Avoid direct comparisons using `var:` inside triggers (engine rejects `var:X > 0`). Instead, compute numeric values in the same effect and use `has_variable = X` or use `script_value` triggers.
- Helper sequence: set_variable -> change_variable (multiply/add/max/min) -> clamp_variable -> round_variable -> remove_variable.

4) Iterators & guards
- Always add existence guards before iterating: e.g., `if = { limit = { has_dynasty = yes } dynasty = { every_dynasty_member = { ... } } }`.
- If iterating over rulers or titles, confirm the scope type matches (e.g., `every_independent_ruler` yields character scopes representing rulers).

5) spawn_army tips
- spawn_army location expects a province event target. Prefer `scope:character.capital_province` or `scope:saved_scope_name.capital_province`.
- Provide `levies` or `men_at_arms` and a `name` to avoid engine warnings.
- If an army sometimes fails to spawn (not at war), use `save_scope_as` on the resulting army (save_temporary_scope_as) and guard presence.

6) Quick fix patterns (copyable)
- Guard dynasty:
  if = { limit = { has_dynasty = yes } dynasty = { every_dynasty_member = { ... } } }

- Compute numeric var and use it safely in same scope:
  set_variable = { name = foo value = scope:independent_ruler.max_military_strength }
  change_variable = { name = foo multiply = 0.1 }
  clamp_variable = { name = foo min = 0 max = 5000 }
  round_variable = { name = foo nearest = 1 }

- Spawn at sponsor's capital province:
  spawn_army = { name = foo levies = var:foo location = scope:independent_ruler.capital_province }

7) Where to consult
- docs/triggers.log — valid triggers and compare patterns
- docs/effects.log — effect signatures like spawn_army and variable helpers
- docs/event_scopes.log / docs/event_targets.log — which tokens accept provinces, titles, characters

8) When to ask for help
- When logs show an invalid event target link or invalid comparison with `var:`. Provide the exact log lines and the file/line number mentioned by the engine.

---

Keep this file short and add new patterns as you learn them from future engine logs.

9) Recent issue: title-variable scope gotchas
- Symptom: Script errors like "Failed to fetch variable ... due to not being set" or "Event target link 'var' returned an unset scope" during on_action handlers (for example on_title_gain).
- Root cause: reading/writing `var:` variables across different scopes without saving the source scope. Example: entering a `primary_title = { ... }` block and attempting to read `var:riseandfall_realm_stability_score` directly inside the title scope — the engine looks for that var in the title scope and fails.
- Fix pattern used in this repo:
  1. Reading a title-stored var into a character:
     - save the primary title into a tmp scope and use title-var syntax:
       primary_title = { save_scope_as = tmp_title }
       if = { limit = { scope:tmp_title = { has_variable = riseandfall_realm_stability_score } } set_variable = { name = riseandfall_realm_stability_score value = scope:tmp_title.var:riseandfall_realm_stability_score } }
  2. Writing a character var back to the primary title safely:
     - save the character scope, then set the title var using scope reference:
       save_scope_as = char_scope
       primary_title = { set_variable = { name = riseandfall_realm_stability_score value = scope:char_scope.var:riseandfall_realm_stability_score } }
  3. Guards: check `primary_title.exists = yes` before saving/reading title vars and fall back to computed defaults when missing.
- Why this works: `save_scope_as` captures the necessary object scope so the engine can resolve `scope:tmp_title.var:...` and `scope:char_scope.var:...` correctly instead of looking up an unset var in the wrong event target.

Add this note whenever you persist per-realm or per-title variables in scripts; it's a recurring source of subtle runtime errors.
