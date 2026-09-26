# GUI API and Expressions

Use local generated type logs as the source of truth. The signatures below are quick reminders; confirm unfamiliar or changed tokens before use.

## Reference order

1. `docs/data_types_gui.txt`, `data_types_script.txt`, `data_types_common.txt`, and `data_types_uncategorized.txt`.
2. Working vanilla examples in installed `game/gui` and `game/common/scripted_guis` (read-only references).
3. Existing mod patterns under `gui/` and `common/scripted_guis/`.

`docs/data_types_internalclausewitzgui.txt` is primarily editor/tooling context, not runtime gameplay GUI API guidance.

## Scripted GUI expressions

- `GetScriptedGui( 'key' )` returns a `ScriptedGui`.
- `GuiScope` is the `TopScope` builder; `GetPlayer.MakeScope` and object `MakeScope` methods provide scopes.
- `ScriptedGui.Execute( GuiScope... )`
- `ScriptedGui.BuildTooltip( GuiScope... )`
- `ScriptedGui.IsShown( GuiScope... )`
- `ScriptedGui.IsValid( GuiScope... )`
- `ScriptedGui.ExecuteTooltip( GuiScope... )`
- `ScriptedGui.IsShownTooltip( GuiScope... )`
- `ScriptedGui.IsValidTooltip( GuiScope... )`
- `GuiScope.SetRoot( Scope )`, `.AddScope( 'name', Scope )`, `.AddList( 'name', ScopeList )`, `.End`
- `GuiScope.ScriptValue( 'named_script_value' )`, `.GetScriptValueBreakdown( 'named_script_value' )`, `.GetScriptValueDesc( 'named_script_value' )`
- Scope helpers include `.Var( 'var_name' )`, `.VarRemaining( 'var_name' )`, `.GetList( 'list_name' )`, `.ScriptValue( 'named_script_value' )`, and `.IsSet`.

Match every scope hop and child context to the actual object types expected by the scripted GUI and expressions.

## Datamodel helpers

- `DataModelHasItems( Model )`
- `IsDataModelEmpty( Model )`
- `GetDataModelSize( Model )`
- `DataModelFirst( Model, Count )`
- `DataModelSkipFirst( Model, Count )`
- `DataModelSubSpan( Model, Offset, Count )`

Models must come from a real controller getter or an explicitly populated variable list. Guard empty lists and use the correct item `datacontext`.

## Other common expressions

- Comparisons: `GreaterThan_CFixedPoint(...)`, `LessThan_CFixedPoint(...)`, `GreaterThan_int32(...)`, `LessThan_int32(...)`.
- Localization selection: `SelectLocalization( condition, 'KEY_TRUE', 'KEY_FALSE' )`.
- UI state: `GetVariableSystem.Exists( 'key' )`, `.Set( 'key' )`, `.Clear( 'key' )`, `.Toggle( 'key' )`, `.SetOrToggle( 'key', value )`, `.HasValue( 'key', value )`.
- Command object gating: `IsValidCommand( CommandObject )` before `CreateCommandPopup( CommandObject )`.

## Common constructs

Prefer working vanilla patterns for `window`, `widget`, `container`, `vbox`, `hbox`, `flowcontainer`, `scrollbox`, `fixedgridbox`, `item`, and `types`; `using` templates; `block` / `blockoverride`; and properties such as `visible`, `enabled`, `down`, `tooltip`, `tooltip_visible`, `onclick`, `onrightclick`, `oncreate`, and `state`.

`ignoreinvisible = yes` is useful on row/flow containers when hidden children should not leave gaps.