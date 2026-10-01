# CK3 1.20 compatibility audit

Compared against installed CK3 1.20.0.2 on 2026-09-30. Mod release metadata is 1.4, targeting `1.20.*`.

## Crash evidence and repairs

The original log ended with a missing `landless_religious_head_widget` in `gui/map_icon_layer.gui`, followed by `Failed to create map icon widget`. It also contained 13,763 invalid-succession messages: the copied succession file still nested individual laws inside law-group definitions, which CK3 1.20 no longer accepts.

| Override or subsystem | Change |
| --- | --- |
| `common/laws/00_succession_laws.txt` | Rebased on all current vanilla laws; converted the three Rise and Fall laws to top-level definitions with `law_group_type` and unique indices 100–102. Vanilla law groups now come from vanilla `common/law_groups/`. |
| `common/succession_appointment/admin_emperor.txt`, `admin_governor.txt` | Rebased on current scoring, including shared appointment values and house aspiration bonuses; retained Warlord, Puppet Regency and administrative nerf adjustments. |
| `common/succession_appointment/riseandfall_warlord.txt` | Replaced removed `allow_same_tier_candidates` with `allowed_candidate_tier = lower_or_equal`. |
| `gui/map_icon_layer.gui` | Restored all current vanilla map widgets, including religious heads, and removed obsolete strait visibility calls; retained the fort overlay. |
| `gui/shared/mapmodes.gui` | Restored current mode controls and `ClearExplored*` APIs; retained the fort toggle. |
| `gui/window_character.gui` | Restored current religious superior, religious subordinate and other vanilla UI changes; retained adventurer and stability indicators. Fixed unsupported fixed-size container and progressbar margin properties found during runtime inspection. |
| `gui/window_title.gui` | Restored the current title view, including clerical regions; retained the giveaway exclusion toggle. |
| `gui/interaction_menu_window.gui` | Restored current puppet filters and menu structure; retained recipient stability and adventurer chance. |
| `gui/window_menatarms.gui` | Audited: existing purchase/sell controls and bulk buttons remained compatible; no behavior change required. |
| `common/character_interactions/riseandfall_war.txt` | Rebased on puppet-aware vanilla Declare War; preserved Warlord exemptions through the focused `riseandfall_allows_declaring_war_against_target_trigger` variant of current vanilla validation. |
| Administrative checks across custom scripts | Replaced removed `government_allows = administrative` with `government_has_mechanic = administrative`; retained valid ordinary rule checks. |
| Interaction category | Moved from index 15 to 16 because vanilla added `interaction_debug_pam` at 15. |
| Recruitment and Puppet Master scripts | Removed invalid `limit` blocks inside six `any_ruler` triggers and repaired two literal backslash-t tokens in title-transfer code. |
| Debug decisions | Added the two missing confirmation localization keys. |

The custom adventurer claim CB has no same-ID definition in current vanilla. Its administrative check was updated without replacing its custom outcomes or war settings. The landless MaA AI value's only upstream compatibility change was the administrative mechanic check. Other custom CBs, diarchy types and scripted effects did not collide with current vanilla definitions. Existing on_action extensions were distinguished from replacement definitions.

## Validation

- Launched CK3 with the existing enabled playset and Rise and Fall loaded.
- The user reproduced character selection and reported that it loaded without crashing. A captured CK3 window showed an active, paused 867 campaign.
- The fresh log no longer contained invalid succession builds, the missing map-widget assertion, old administrative appointment trigger errors, obsolete map-mode calls or the interaction category collision.
- All five refreshed GUI files retained every nonblank vanilla source line, with only feature additions and whitespace normalization.
- Checked braces, UTF-8 BOM, referenced law and appointment IDs, stability placement, and focused `git diff --check` on the edited mod and guide files. The user's freshly generated reference docs contain engine-emitted trailing whitespace and were preserved.
- A subsequent fresh startup also confirmed zero missing debug confirmation keys, retired invite flag warnings, orphan warnings for recruitment events `.0004`–`.0007`, or scope mismatches in Palace Coup claimant consolidation. Recruitment parsing and Puppet Master parsing also produced no Rise and Fall parse errors on that startup. The corrected stability properties still require a fresh character-window rendering check.
- Administrative succession, actual puppet war declarations, bulk MaA purchases and long-running simulations were not exercised.

## Remaining playset issues

- **Architect of Automation** owns `aba_script_values.txt` and `aba_mod_scripted_effect.txt`, which reported removed building-cost values and missing building-requirement triggers.
- **Balance of Power UI** overrides `gui/window_factions.gui` and still calls removed `Faction.GetShowSpecialTitle`.
- **More Interactive Vassals** appeared in conqueror story creation failures through `interactive_on_actions.txt`.
- Other enabled mods reported invalid launcher version strings and an encoding warning for `zz_defines_stop_drifting.txt`.
- Other unused-variable warnings may remain; the retired invite flags and legacy recruitment orphan warnings were repaired in the follow-up pass below.

Installed vanilla files and other mods were not edited. Existing user changes to release metadata and generated documentation were retained.

## Follow-up warning repairs

- Palace Coup claimant consolidation now re-enters `scope:palace_coup_challenger` after saving each kingdom title, before running both vassal iterators. Ranking, regional filtering and player-selected bids were preserved.
- Removed four uncalled toggle-based invitation helpers that were the only references to the retired free/paid invite flags. Current browsers, knight recruitment hooks and yearly guardian automation were retained.
- Preserved events `riseandfall_courtier_automation.0004`–`.0007` and their effects, marking them `orphan = yes` as documented by vanilla for intentionally unreferenced entry points.
- The existing confirmation localization additions loaded successfully on restart. Startup verification does not demonstrate a complete Palace Coup execution.
- A later live log contained 21,686 blocks mentioning Rise and Fall, representing 13 distinct messages. Most were repeated unset-`root` errors in Coalition tracking during the global yearly pulse. Tracking now saves the ruler explicitly before all three callers evaluate neighbor eligibility, preserving the territorial and invitation gates.
- Completed Create Adventurer Camp's disabled AI configuration with `ai_targets = { ai_recipients = self }`, retaining `ai_frequency = 0`, human-only availability and `ai_potential = { always = no }`.
- The Dragonrider compatibility placeholder now uses prefixed standalone name/description keys. Its trait ID, bonuses and tracks remain; the placeholder no longer references AGOT-only text or dragon variables.
- Captured the running observer campaign on 2 January 868, confirming it crossed the yearly pulse. The live log then contained no Coalition tracking scope errors or placeholder localization errors. Its single remaining Rise and Fall entry was the intermediate AI-field warning emitted at startup before the completed interaction configuration was saved; that last correction requires the next restart.
