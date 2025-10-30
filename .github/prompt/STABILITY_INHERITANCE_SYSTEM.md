# Realm Stability Inheritance System

## Overview
This document describes how the Rise and Fall mod implements realm stability score inheritance when a character dies or passes a title to their heir.

## Design Principles

### 1. **Scope Analysis** (from `docs/event_scopes.log` and vanilla death.txt)
- **on_death**: Root scope is the dying character
  - Available targets:
    - `primary_heir` - the character's designated primary heir
    - `player_heir` - specific player heir (often same as primary_heir)
    - All scoped variables attached to the character are accessible
- **on_title_gain** / **on_title_gain_inheritance**: Root scope is the new title holder
  - Available: `scope:previous_holder` (the character who held it before)
  - `scope:transfer_type` indicates inheritance vs. conquest

### 2. **Inheritance Mechanics**

#### Death Transfer (on_death)
When a ruler dies with a realm stability score:
1. The dying character's score is saved and transferred to their primary/player heir
2. 100% of the predecessor's stability transfers (no penalty for death itself)
3. The heir also inherits the predecessor's war multiplier (preserves realm momentum)
4. Related variables (`riseandfall_rs_civil_war_years`, `riseandfall_puppet_regency_years`) are initialized fresh for the heir

**Key Insight**: This prevents sudden stability collapse on succession. A well-managed realm stays stable when the ruler dies, though the new ruler's stats may cause adjustments at the next calculation.

#### Title Transfer (on_title_gain_inheritance)
When a character gains a title via inheritance:
1. If the heir doesn't have a stability score yet, check if the previous holder had one
2. If yes, inherit the score from the previous holder
3. If no, calculate a fresh score based on the heir's stats and realm state

**Key Insight**: This handles title-by-title transfers (e.g., vassal counts inheriting from liege) and ensures newly-landed characters get a reasonable stability baseline.

---

## Implementation

### Files Modified

#### 1. `common/scripted_effects/riseandfall_realm_stability_effects.txt`
**New Effect**: `riseandfall_inherit_stability_score_se`

**Purpose**: Transfer stability from predecessor to heir

**Logic**:
```
Input:  Root scope = heir
        scope:predecessor = character whose stability is being transferred
        Game rule: riseandfall_realm_stability_enabled must be true

Actions:
1. Check if predecessor has riseandfall_realm_stability_score > 0
2. If yes:
   - Copy predecessor's stability to heir
   - Save for tooltip as scope:predecessor_stability_amount
   - Copy war multiplier from predecessor (preserves momentum)
   - Initialize months/civil-war tracking for heir
3. If no:
   - Initialize heir with default (neutral) multiplier values
```

**Transfer Percentage**: **100%** (full transfer, no degradation)

**Additional Transfers**:
- War multiplier (`riseandfall_realm_stability_war_multiplier`)
- All component calculations reset; next `riseandfall_calculate_realm_stability_se` call will recompute components based on heir's stats

---

#### 2. `common/on_action/riseandfall_realm_stability_on_actions.txt`
**New On_action**: `riseandfall_on_death_stability_inheritance`

**Trigger**: 
```
Game rule enabled
Root character is a ruler
Root character has a stability score variable
```

**Effect**:
```
1. Save root (dying character) as scope:predecessor
2. If primary_heir exists and is alive:
   - Call riseandfall_inherit_stability_score_se on primary_heir
3. Else if player_heir exists (and is not primary_heir):
   - Call riseandfall_inherit_stability_score_se on player_heir
```

**Scope Available**: 
- `root` = dying character
- `player_heir` / `primary_heir` = available targets (per vanilla death.txt)
- `scope:killer` (if exists, for future expansion)

---

**Modified On_action**: `riseandfall_on_title_gain_inheritance`

**Old Logic**: Calculate fresh stability if heir doesn't have one yet

**New Logic**:
```
Trigger: Game rule enabled

Effects:
1. If heir has no stability score AND previous holder has one:
   - Save previous_holder as scope:predecessor
   - Call riseandfall_inherit_stability_score_se on heir
   
2. Else if heir has no stability score AND no previous holder data:
   - Calculate fresh stability via riseandfall_calculate_realm_stability_se

3. Else:
   - Do nothing (heir already has a score, or no trigger condition met)
```

**Scope Available**:
- `root` = new title holder (character who just gained the title)
- `scope:previous_holder` = character who held the title before
- `scope:title` = the title being transferred
- `scope:transfer_type` = flag (e.g., flag:inheritance)

---

## Behavior Examples

### Example 1: Experienced King Dies
- King has stability score of **75** (well-managed realm)
- King dies, leaving kingdom to Son (new heir)
- **Inheritance trigger activates**:
  - Son receives stability score of **75**
  - Son inherits war multiplier (e.g., 100%, or higher if father had recent victories)
  - Son's own stats have NOT changed the score yet; next yearly calculation will adjust it based on his lower/higher stats
  - Result: Son starts with momentum from father, but may lose/gain stability next year if his stats differ

### Example 2: Infant Heir
- King dies; Infant inherits
- Same process: Infant receives full stability score
- Infant's regency may trigger puppet regency multiplier decay (already handled by existing logic)
- Result: Infant's regency doesn't automatically tank stability; reputation is preserved

### Example 3: Multiple Title Inheritance
- Liege (King of X) dies with stability 80
- Liege has three landed vassals:
  1. Eldest (holds Duke of Y) — inherits from Liege (on_death triggers)
  2. Second (holds County of Z) — inherits on_title_gain_inheritance (scope:previous_holder = old liege)
  3. Youngest (holds minor vassal count) — similar to Second
- Eldest gets 80 (full transfer)
- Second and Third get checked for inheritance via on_title_gain_inheritance; they'll inherit if they don't already have a score
- Result: All heirs preserve some momentum from predecessor

### Example 4: Non-Inheritance Transfer (e.g., Conquest)
- Lord A conquers Lord B's county
- `scope:transfer_type` is **not** flag:inheritance
- riseandfall_on_title_gain_inheritance **does not trigger** (no inheritance transfer)
- Conqueror calculates fresh stability based on their stats and new realm
- Result: Conquests reset stability baseline (as intended; conqueror has new realm)

---

## Edge Cases & Defensive Checks

### 1. **Predecessor Missing Stability Variable**
- If predecessor has no `riseandfall_realm_stability_score`, inherit effect checks with `has_variable`
- Heir initializes to default multiplier (100%) and gets fresh calculation next year

### 2. **Both primary_heir and player_heir Exist**
- On_death checks `exists = primary_heir` first
- Only calls on player_heir if primary_heir doesn't exist (avoids double-transfer)
- Both targets use the same predecessor scope

### 3. **Heir Dies Before Next Calculation**
- Heir's stability is preserved in variable until next yearly pulse
- If heir dies immediately, death effect triggers again, passing to their heir
- Cascading transfers work (grandchild inherits from child, etc.)

### 4. **Regency / Diarchy Effects**
- Inheritance is separate from diarchy handling (already in death.txt)
- Heir's regency status is respected in next calculation (puppet regency multiplier applied)
- War multiplier is **copied** (not recalculated) to preserve strategic context

---

## Supported Targets Checklist

Based on `docs/event_scopes.log` analysis:

| Scope/Target | Used For | Status |
|---|---|---|
| `root` (on_death) | Dying character | ✓ Checked |
| `primary_heir` | Available in on_death | ✓ Used |
| `player_heir` | Available in on_death | ✓ Used as fallback |
| `scope:previous_holder` (on_title_gain) | Previous title holder | ✓ Used |
| `scope:title` | Title being transferred | ✓ Available (not used yet) |
| `scope:transfer_type` | Type of transfer (inheritance flag) | ✓ Can filter on |
| Character variables (`has_variable`) | Checking stability score | ✓ Used |
| Character variables (`set_variable`) | Setting inherited values | ✓ Used |

---

## Testing Checklist

- [ ] Load mod in CK3 with Realm Stability enabled
- [ ] Create a character with high stability (80+)
- [ ] Kill or retire that character
- [ ] Observe that heir receives stability score
- [ ] Check that heir's score doesn't jump immediately (waits for next calculation)
- [ ] Test with multiple heirs (eldest, vassal brothers)
- [ ] Test with regency (infant heir)
- [ ] Test cascade deaths (heir dies soon after inheriting)
- [ ] Test conquest vs. inheritance (conquest should reset stability)
- [ ] Verify no console errors about missing variables

---

## Future Enhancements

1. **Stability Decay on Death**: Add option to transfer only 75% or 50% (instead of 100%)
   - Config via game rule or define

2. **Realm Scope Transfers**: Currently only character-scope; could extend to dynasty or realm-wide effects

3. **Tooltip Notifications**: Add event or modifier to show heir that they inherited stability from predecessor

4. **Prestige/Piety Inheritance**: Similar pattern could be applied to other character stats

---

## Contract Summary

| Aspect | Details |
|---|---|
| **Inputs** | Dying/transferring character with `riseandfall_realm_stability_score` variable |
| **Outputs** | Heir receives inherited stability score + war multiplier; next calculation adjusts based on heir's stats |
| **Scope Requirements** | on_death (root=dying char), on_title_gain_inheritance (root=heir, scope:previous_holder=old holder) |
| **Validation** | Game rule must be enabled; character must have stability variable |
| **Error Modes** | Missing predecessor score (handled: defaults to neutral); missing heir (handled: trigger skips) |
| **Success Criteria** | Heir has `riseandfall_realm_stability_score` set to predecessor's value; next yearly pulse adjusts it |

