# CK3 GUI Authoring — LLM Prompt (compact)

Purpose (1–2 lines)
- Teach an LLM how to author correct, compatible Crusader Kings III `.gui` UI files and small scripted GUIs using authoritative vanilla patterns and engine logs.

Contract (inputs / outputs / error modes / success criteria)
- Inputs: requested GUI feature (window/widget), target scope (character/title/province/etc.), required datamodels/promotes, localization keys.
- Outputs: a set of `.gui` text files (types/templates + window/widget file), any `scripted_widgets` registration, and `localization/english/*.yml` entries. Files must follow vanilla structure and use `riseandfall.` prefix for new IDs.
- Error modes: missing localization (raw keys show), bad scope/datamodel mismatch (silent no-op), duplicate IDs (first-file wins), illegal layout (100% nested expands → layout collapse).
- Success criteria: files load without syntax/brace errors, referenced loc keys exist, and a minimal in-game check (open window or call ScriptedGui.Execute) shows expected UI.

Short engineering checklist to follow
- Reuse vanilla `types`/`using` templates where possible; customize with `blockoverride` instead of editing core templates.
- Use `datamodel = "[...]"` + `item = { ... }` for lists; ensure `item` expects the returned datamodel type.
- Guard all `visible`/iteration logic with existence checks (e.g., IsValid, IsDataModelEmpty).
- Use `layoutpolicy_*`, `min/max` sizes, and `expand = {}` to control layout; avoid nested 100% expand chains.
- Add localization in `localization/english/` for every UI key.
- Use `-debug_mode -develop`, `gui.debug`, and `dump_data_types` when iterating or debugging.

Common building blocks (tokens & primitives)
- Root: `widget`, `window`, `container`, then layout: `vbox`, `hbox`, `flowcontainer`, `fixedgridbox`, `scrollarea`, `scrollbox`, `item`.
- Layout tokens: `layoutpolicy_horizontal/vertical` (expanding/growing/fixed/preferred), `expand = {}`, `spacer`, `min_width/max_width/minimumsize/maximumsize`.
- Reuse helpers: `using = Window_Background`, `using = Window_Margins`, `using = tooltip_ws`.
- Data-binding: `datacontext = "[...]"` for single-scope widget, `datamodel = "[...]"` + `item` for lists, and `blockoverride` inside `item` to map UI parts to model values.
- Types & templates: `types { type X = Y { ... } }` and `blockoverride "name" { ... }` to change template internals safely.
- Animation & states: `state = { name = _show ... using = Animation_* }`, `delay/duration/next/on_start` to chain animations, `PdxGuiTriggerAllAnimations` or `PdxGuiWidget.FindChild(...).TriggerAnimation(...)` for programmatic triggers.
- Variable UI toggles: `GetVariableSystem` / `VariableSystem.Toggle('key')` for ephemeral UI state.

Delta: Adding conditional widgets to existing stats bars (Stability Box)
- Problem: Need to add mod-specific stats (e.g., stability) as standalone boxes in character window stats bars, with proper visibility guards and no empty spaces.
- Fix: Modify the `blockoverride` for the stats bar (e.g., `hbox_character_view_secondary_stats_bar`) to include a new conditional `widget` with icon, text, tooltip, and size matching other stats. Use `datacontext` for game rules and complex `visible` conditions checking variables and flags.
- Working snippet (copypasta):
  blockoverride "hbox_character_view_secondary_stats_bar"
  {
    # ... existing widgets ...
    divider_light = {
      visible = no  # Hide divider to avoid empty boxes
      layoutpolicy_vertical = expanding
    }
    # Stability
    widget = {
      datacontext = "[AccessGameRules.AccessNamedGameRule( 'riseandfall_enable_realm_stability' ).GetSetting]"
      visible = "[Complex condition checking variables >0, landed titles, etc.]"
      size = { 72 32 }
      tooltip = "REALM_STABILITY_TOOLTIP"
      using = tooltip_es
      hbox = {
        spacing = 3
        expand = {}
        icon = { size = { 30 30 } texture = "gfx/interface/icons/scale_of_power.dds" }
        text_single = { text = "[Character.MakeScope.Var('riseandfall_realm_stability_score').GetValue|0]/[Character.MakeScope.Var('riseandfall_realm_stability_target').GetValue|0]" default_format = "#high" align = center|nobaseline fontsize_min = 12 max_width = 50 }
        expand = {}
      }
    }
  }
- Notes: Place after existing stats like military strength. Ensure visibility checks prevent showing for unlanded or when values are zero. Hide dividers to avoid gaps.

Mini contract for this pattern
- Inputs: stat name, variable names, icon texture, tooltip key, visibility conditions.
- Output: integrated widget in stats bar with proper guards.
- Error modes: empty boxes (hide dividers), wrong visibility (check all conditions), layout issues (match sizes).
- Success: stat appears as a clean box next to vanilla stats when conditions met.

Common patterns & examples (minimal, LLM-ready snippets)
- Minimal window skeleton (concept):
  window = {
    name = "riseandfall_example_window"
    parentanchor = center
    using = Window_Background
    vbox = {
      using = Window_Margins
      header_pattern = { blockoverride "header_text" { text = "riseandfall.example.title" } }
      vbox = { datamodel = "[RiseAndFall.GetItems]" item = { button_list = { datacontext = "[Item.Get]" text_single = { text = "[Item.GetName]" } } } }
    }
  }

- Registering a scripted widget (text description):
  - Add a small `common/scripted_guis/` or `gui/scripted_widgets/` entry that points to your window type.
  - For sguis, call from code: `ScriptedGui.Execute('riseandfall.example', make_scope_value('some_id', id))` (match the engine API tokens used in your engine build).

Datamodel item pattern
- `datamodel = "[SomeView.GetList]"` + `item = { ... datacontext = "[ListItem.Get]" ... }`.
- Use `IsDataModelEmpty` guard for empty states.

Types / blockoverride guidance
- Prefer: define `type <my_type> = <vanilla_type> { blockoverride "foo" { ... } }` so you don't break load order or mod compatibility.
- Use `blockoverride` for small changes (text, onclick, frame) rather than creating incompatible copies of vanilla templates.

Animation and interactive triggers
- Put show/hide and mouse states inside `state` blocks. Example: `_show` uses `Animation_FadeIn_Standard`; `_hide` uses `Animation_FadeOut_Standard`.
- Use `PdxGuiTriggerAllAnimations('anim_name')` after changing data models to refresh animated layouts.

Debugging & iteration commands (developer shortcuts)
- Launch flags: `-debug_mode -develop` to enable widget inspector and logging.
- In-game: enable `gui.debug` (GUI inspector) and the GUI Editor (Ctrl+F8) for live inspection.
- Console: `dump_data_types` to list available promotes/functions; `reload gui` to hot-reload your `.gui` files; `reload texture` for texture changes.

QA gates & validation steps (run before committing)
- 1) Brace balance: quick textual check in editor or script. (Required)
- 2) Duplicate-ID scan: ensure your `riseandfall.` IDs are unique. (Required)
- 3) Localization coverage: grep for `riseandfall.` keys and confirm `localization/english/*.yml` entries. (Required)
- 4) Datamodel type-check: ensure datamodels return the scope expected by `item` contexts (manual check with `dump_data_types`). (Required)
- 5) Smoke test: launch CK3 with mod enabled, open/trigger the window or scripted GUI in-game. (Recommended)

Common pitfalls (short)
- Nested expanding boxes with 100% sizes cause layout collapse. Use `min/max` and `layoutpolicy` carefully.
- Using wrong saved scope types (saving a barony then using it as a province) — verify scopes with `docs/event_scopes.log`.
- Missing loc keys — game shows raw keys.
- Editing vanilla templates directly — prefer `blockoverride` to remain compatible with other mods.

Vanilla idioms worth copying (high-signal)
- Header + close pattern: `header_pattern` + `blockoverride "header_text"` + `blockoverride "button_close"`.
- Outliner / lists: `datamodel` → `item` → `button_list`, with `datacontext` pointing to item functions (e.g., `Character.GetID`, `Army.GetName`).
- Save/load frontend: large `widget` with `types` for `button_saved_games` showing many visibility guards — a good reference for robust UIs.

File conventions for this repo (project rules)
- Place GUI files under `gui/` or `common/scripted_guis/` in the mod root; do not edit `game/`.
- Use `riseandfall.` prefix for new scripted gui IDs and loc keys.
- Add `localization/english/riseandfall_*_l_english.yml` entries for UI strings.

Small troubleshooting checklist (when something goes wrong)
- Check console/engine logs for GUI parse errors.
- Run `dump_data_types` to confirm promote/function names used in `datamodel` and `datacontext` are available.
- Verify blockoverride names match actual fields in the template (typos silently fail).
- If a window doesn't appear, ensure it's registered (scripted widget or called via ScriptedGui.Execute) and data guards (`visible`) evaluate true.

Next-steps suggestions (for the agent)
- Create a minimal example: small window, one `datamodel` list, `scripted_widgets` entry, and a matching `localization/english` file.
- Add a small PowerShell script under `riseandfall/tools/validate-gui.ps1` that checks brace balance, duplicate IDs, and missing localization keys.

References (authoritative sources to consult while editing)
- `docs/event_scopes.log`, `docs/triggers.log`, `docs/effects.log`, `docs/modifiers.log`, `docs/on_actions.log` in this repo for engine surface.
- Vanilla files under the CK3 install `game/gui/*.gui` for canonical templates and idioms.

---

## Delta: Created example stability widget
- Files added under the mod:
  - `gui/riseandfall_character_stability.gui` — small widget showing an icon + numeric promote read from `Character.GetStabilityLevel`.
  - `gui/scripted_widgets/riseandfall_scripted_widgets.txt` — scripted widget registration (anchor heuristics; engine may require different registration fields depending on version).
  - `localization/english/riseandfall_stability_l_english.yml` — tooltip and title.

Testing instructions (quick):
- Launch CK3 with `-debug_mode -develop`.
- Enable `gui.debug` or open the GUI Editor (Ctrl+F8) and inspect `character_window` to find the `riseandfall_character_stability` widget.
- If the value is missing or shows `0`, ensure your mod exposes a promote `Character.GetStabilityLevel` (or change the `text` expression in the `.gui` file to match your promote name).

Assumptions & notes:
- The scripted widgets system differs across engine versions; if the widget doesn't appear, open the character `.gui` in the frontend `game/gui/` and add a `blockoverride` for the header or portrait area instead of scripted registration.
- Placeholder icon uses an existing prestige icon texture; replace with `gfx` in your mod for a unique icon.

Notes for LLM usage
- Prefer vanilla tokens and patterns. When in doubt, copy the smallest vanilla pattern and `blockoverride` it.
- Always include an engineering contract and QA gates for each generated change.
- When suggesting exact promote/function names (e.g., `GetPlayer`, `Character.GetID`), prefer verifying with `dump_data_types` before committing code.

