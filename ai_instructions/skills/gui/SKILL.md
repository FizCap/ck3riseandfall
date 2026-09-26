---
name: ck3-gui-modding
description: Use when creating, editing, or debugging Crusader Kings III GUI files, vanilla window overrides, HUD widgets, scripted GUI wrappers, datamodels, or UI localization.
---

# CK3 GUI Modding

Use this skill for Rise and Fall GUI work. The GUI is declarative and expression-driven: valid syntax can still fail when a widget receives the wrong context, its model has no items, or the owning window never instantiates it.

## Start with local evidence

1. Identify the exact screen and owning GUI file. Search `gui/` and `common/scripted_guis/`; inspect surrounding structure before editing.
2. Check unfamiliar GUI expressions in `docs/data_types_gui.txt`, `data_types_script.txt`, `data_types_common.txt`, and `data_types_uncategorized.txt`. Treat `data_types_internalclausewitzgui.txt` mainly as editor/tooling context.
3. For scripted GUI `is_shown`, `is_valid`, and `effect` blocks, check supported triggers and effects in `docs/triggers.log` and `docs/effects.log`. Some useful supported-token examples or details can also appear in matching vanilla script and `common/scripted_guis` files, so search those as well.
4. Confirm API tokens in local generated type logs and find matching patterns in installed vanilla GUI/scripted GUI files. Use vanilla files as references only; never edit `game/`.
5. Read [API and expression reference](references/api-and-expressions.md) for scope builders, models, state, or command methods. Read [project patterns and validation](references/project-patterns.md) for existing mod examples and screen integration.

## Rules for changes

- Put GUI overrides/widgets in `gui/`, reusable types in `gui/shared/`, scripted GUI bridges in `common/scripted_guis/`, and UI strings in `localization/english/`.
- Preserve UTF-8 with BOM in `.gui`, script `.txt`, and localization `.yml` files. Keep edits consistent with the surrounding vanilla style and ASCII unless the file intentionally uses other characters.
- Match each `datacontext` and `datamodel` to the actual object type consumed by its children. For scripted GUIs, the wrapper's `scope =` must match the scope passed from GUI.
- Use real controller-provided or script-filled lists; GUI markup cannot invent a controller datamodel. Set item context explicitly when its type is otherwise ambiguous, and handle empty models.
- For game-state changes, prefer an existing vanilla command object (`IsValidCommand` before `CreateCommandPopup`) or a scripted GUI wrapper that calls a scripted effect.
- Add localization for visible text and tooltips. Raw text is for debug/dev-only UI.
- Keep vanilla overrides focused, preserve the owning window's structure, and recheck copied overrides against the current game version.
- Add a concise comment for non-obvious additions, explaining purpose or constraints rather than repeating the code.

## Integration rules

- A standalone `.gui` file does not register a HUD panel or a new game-view key. For a custom HUD panel, put the widget inside an already-loaded HUD widget (such as `ingame_topbar`) and gate visibility with `GetVariableSystem` state.
- `ToggleGameView` and `IsGameViewOpen` work with known registered game views. Do not assume a custom top-level `window` declaration registers one.
- For an existing vanilla screen, edit the GUI file that owns that screen and insert into its real tab/body block. A separate top-level window can parse but never appear in the existing view.
- For character values stored on a `Character` variable, bridge through `Scope` where needed: use a `Scope` datacontext and then `[Scope.Char]` for the child context to avoid same-context errors.

## Validation

- Verify API names in generated type logs, scope type at each GUI/wrapper hop, model data and item context, visibility/enabled logic, command validity, and localization coverage.
- Launch CK3 with the mod enabled and inspect the changed screen. A parseable file or source-level check does not prove that a widget instantiated or an action worked.
- If the widget is absent, check registration/owning file, visibility expression, and context validity. If a list is blank, check its source and item context. If a button does nothing, check command validity or the wrapper scope/effect. If an override is ignored, check the owning path and `blockoverride` name.