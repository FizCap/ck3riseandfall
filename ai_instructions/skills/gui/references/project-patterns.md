# Rise and Fall GUI Patterns and Validation

These examples were verified in the current mod GUI tree. Reopen the target block and surrounding structure before copying a pattern.

## Existing project examples

- `gui/window_title.gui` uses `IsValidCommand( TitleViewWindow.GetDestroyTitle )` to gate `CreateCommandPopup(...)`; follow that pairing for vanilla command actions.
- The title giveaway control in `gui/window_title.gui` uses `GetScriptedGui( 'riseandfall_toggle_giveaway_blocked_gui' )`. Its wrapper in `common/scripted_guis/riseandfall_toggle_giveaway_blocked.txt` declares `scope = title` and calls a scripted effect. Match the scope passed by the GUI to that wrapper scope.
- Fort map mode state is toggled in `gui/shared/mapmodes.gui` using `GetVariableSystem.Toggle( 'riseandfall_fort_map_mode_active' )`; `gui/map_icon_layer.gui` reads the same state to control fort overlays. Keep state key spelling identical across controls and consumers.
- Shared tooltip types live in `gui/shared/rf_stability_tooltip.gui` and `rf_adventurer_tooltip.gui`; both extend `object_tooltip_pop_out`.
- `gui/window_character.gui` is an existing vanilla window override with mod widgets integrated into the owning window. Follow its actual nested context and visibility pattern when adding character-window content.
- Existing vanilla GUI code uses chained contexts (for example title then holder) where a child depends on the preceding context. Preserve the order and verify each resulting type.

## Patterns to adapt from vanilla

### Scripted GUI button

```gui
button_standard = {
    datacontext = "[GetScriptedGui( 'create_head_of_faith' )]"
    enabled = "[ScriptedGui.IsValid( GuiScope.SetRoot( GetPlayer.MakeScope ).AddScope( 'faith', Faith.MakeScope ).End )]"
    onclick = "[ScriptedGui.Execute( GuiScope.SetRoot( GetPlayer.MakeScope ).AddScope( 'faith', Faith.MakeScope ).End )]"
    tooltip = "[ScriptedGui.BuildTooltip( GuiScope.SetRoot( GetPlayer.MakeScope ).AddScope( 'faith', Faith.MakeScope ).End )]"
}
```

Use only after verifying that the wrapper accepts the same root and named scope types.

### Command-object button

```gui
button_round = {
    enabled = "[IsValidCommand( TitleViewWindow.GetDestroyTitle )]"
    onclick = "[CreateCommandPopup( TitleViewWindow.GetDestroyTitle )]"
    tooltip = "[TitleViewWindow.GetDestroyTitleButtonTooltip]"
}
```

### Empty and non-empty model states

```gui
visible = "[DataModelHasItems( TitleViewWindow.GetVassalGroupItems )]"
visible = "[IsDataModelEmpty( TitleViewWindow.GetVassalGroupItems )]"
```

### Chained datacontext

```gui
datacontext = "[TitleViewWindow.GetTitle]"
datacontext = "[Title.GetHolder]"
```

### Scripted GUI wrapper

```txt
riseandfall_example_gui = {
    scope = title

    is_shown = { }
    is_valid = { }

    effect = {
        riseandfall_some_effect = yes
    }
}
```

## HUDs and existing windows

- Main-tab buttons that open vanilla/known views should follow current patterns from vanilla HUD/window files such as `game/gui/hud.gui`, `window_court.gui`, and `window_factions.gui`.
- For a mod HUD panel, add the panel inside a loaded HUD widget and control it with state, for example `Set('my_panel_open', 'true')`, `Clear('my_panel_open')`, and `Exists('my_panel_open')`.
- For content inside an existing window, override the file that owns that window and insert into its real body/tab. A detached companion window is not automatically instantiated by the existing view.
- Full-window vanilla copies drift; keep edits marked and focused, and recheck them after CK3 updates.
- A map-icon override must retain every engine-requested named widget from the current vanilla file. In CK3 1.20, omitting `landless_religious_head_widget` caused a `Failed to create map icon widget` assertion during character selection. Rebase the whole owning file and transplant only the fort overlay; restoring individual obsolete API calls is insufficient.
- In the character stability strip, CK3 1.20 rejected `size` and `margin_left` on a `container`, and `margin_top` on a progressbar. Use a fixed-size `widget` for the icon cell and supported `position` offsets for those elements; containers resize to their contents.

## Localization and data

- Use localization keys for player-facing text and tooltips. `raw_text` / `raw_tooltip` are for debug/dev-only UI.
- Add or verify localization for literal `text` / `tooltip` keys and scripted tooltip paths that return keys or descriptions.
- Do not assume GUI markup can create a controller list. Use a real controller model or a script-filled list; set item context explicitly when unclear.
- For a character value read from a variable on the current Character context, bridge through `Scope` when same-context datacontext resolution fails:

```gui
# Parent row exposes the variable as a Scope context.
datacontext = "[Character.MakeScope.Var('some_character_var')]"

# Child row resolves that Scope back to the Character.
datacontext = "[Scope.Char]"
```

## Focused verification

1. Confirm each expression token in local `docs/data_types*.txt` and locate a working vanilla usage.
2. Check wrapper `scope =` against the GUI `MakeScope` and confirm datacontext hops in order.
3. Check model source, empty state, and item type.
4. Check `IsValidCommand` gates each `CreateCommandPopup` and scripted buttons have correct validity/effect/tooltip paths.
5. Check all visible strings and tooltips have localization.
6. Launch CK3 and test exactly the changed screen or interaction; inspect logs. Source checks alone do not prove the widget instantiated.

If available, GUI editor/log tools can help inspect data types; `dump_data_types` is a type-dump aid, not proof of in-game behavior.
