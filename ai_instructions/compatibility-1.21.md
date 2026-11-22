# CK3 1.21 compatibility rebase

Compared against installed CK3 1.21.0.3 (Florin) on 2026-11-22. Launcher metadata now targets `1.21.*`.

The trade screen stall came from full-file GUI overrides that still contained the 1.20 interface. Opening trade uses the new province trader pins, trade-post icons, and trade-route endpoints in `gui/map_icon_layer.gui`, plus trade widgets in `gui/window_character.gui` and the trade map modes in `gui/shared/mapmodes.gui`. Replacing those files with the older copies removed that interface.

## Rebased overrides

Each file below is the 1.21 vanilla file plus the existing Rise and Fall additions.

| File | Retained mod behavior |
| --- | --- |
| `gui/map_icon_layer.gui` | Fort-level overlay and icon fade while that overlay is active. |
| `gui/shared/mapmodes.gui` | Fort map-mode toggle in the additional map-mode list. |
| `gui/window_character.gui` | Adventurer chance and realm stability indicator. |
| `gui/window_title.gui` | Title giveaway exclusion toggle. |
| `gui/interaction_menu_window.gui` | Recipient stability and adventurer chance. |
| `gui/window_menatarms.gui` | x10 and x50 regiment size buttons. Kept the 1.21 `MaaProvinceStatAlpha` calls. |
| `common/laws/00_succession_laws.txt` | The three script-only succession laws at indices 100–102. |
| `common/succession_appointment/admin_emperor.txt` | Warlord, Puppet Regency, and admin-nerf score adjustments. |
| `common/succession_appointment/admin_governor.txt` | Warlord and admin-nerf score adjustments. |
| `common/character_interactions/riseandfall_war.txt` | 1.21 Declare War, still routed through the Warlord-aware target trigger. |
| `common/scripted_triggers/riseandfall_war_triggers.txt` | 1.21 target validation, with Warlord exemptions on the administrative and permanent vassal war-law bans. |
| `common/script_values/ai_men_at_arms_chance_landless_ruler.txt` | Legitimist adventurers still ignore the generic landless MaA penalties. |
| `common/scripted_triggers/zz_riseandfall_palace_coup_council_triggers.txt` | 1.21 minister and grand marshal eligibility, with the Palace Coup handoff guard. |

Removed `common/diarchies/diarchy_types/_diarchies.info` and `common/succession_appointment/_succession_appointment.info`. They were stale documentation copies and contained no mod behavior. The interaction category stays at index 16 because 1.21 assigned index 15 to `interaction_debug_gdp`.

On-action files only append mod actions and were left in place. This pass did not launch CK3, so the trade screen, fort overlay, stability indicator, and bulk regiment buttons still need an in-game check.
