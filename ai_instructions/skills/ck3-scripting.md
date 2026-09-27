# CK3 Scripting, Scopes, Decisions, and AI

Read this guide for script effects/triggers, decisions, interactions, on_actions, armies, and AI logic. For title and court lifecycle rules, also read `ck3-realm-systems.md`.

## Verify syntax and scope

- Check the generated reference logs in `docs/` before using unfamiliar triggers, effects, targets, scopes, or on_actions. Treat prose notes as cheatsheets; generated docs and working vanilla examples take precedence.
- For on_action extensions, verify the hook and expected scope in `docs/on_actions.log`, then inspect the vanilla handler. Some code hooks, including diarchy hooks, provide the affected character as `root` despite generated entries saying `Expected Scope: none`.
- Validate every scope hop. Guard optional scopes with `exists`; guard variables with `has_variable`. A saved scope must retain the expected character/title/province type.
- Character flags use add_character_flag = { flag = flag_name } and 
emove_character_flag = flag_name; set_character_flag is not a valid effect.
- Tooltip triggers may read an unset `var:` even beside `has_variable` in an `AND`; use `var:name ?= scope:target` for optional object comparisons.
- When comparing iterator candidates with the original character, save the original before iterating and use a documented target trigger. Direct comparisons such as `this = scope:name` are invalid. Character-target triggers take their character target directly unless documentation says otherwise; nested scripted triggers may not retain the iterator caller’s `root`.
- Add concise `#` comments for non-obvious scope changes, thresholds, weights, or calculations; keep block structure strict.

## Decisions, interactions, and candidate searches

- Use `is_valid` for cheap availability requirements when a decision should remain visible but disabled. Do not put world-wide candidate searches there: even `any_ruler` with nested court/acceptance checks searches for candidates independently of the event that builds the list. Recruitment browsers should search in the clicked event, handle empty results using their prepared candidate scopes, and retain recruitment eligibility checks. Keep broad visibility requirements such as government/landed status in `is_shown`.
- If a scripted value reads a named saved scope such as `scope:rf_courtier_automation_candidate`, save that candidate before evaluating the value. In candidate iterators, move candidate-dependent affordability checks out of `limit` and into the iterator body after `save_scope_as`; trigger limits cannot create the saved scope the value expects.

- Decision previews evaluate conditional scripted effects against current persistent state. Do not make preview targets or costs depend on a flag set by that same decision; use a mode-specific immediate effect for enable actions. A direct scripted-effect call nested under `hidden_effect` can still expand in previews. Dispatch stateful, non-previewable work through a hidden event when the tooltip builder must not enter it.
- Do not use `ordered_living_character` in a decision effect whose preview is evaluated in the Decisions window. Gather candidates from filtered diplomatic-range rulers and their courts, then use `ordered_in_list` on that reduced set.
- `every_courtier_or_guest` only sees the scoped character’s own court and guests. For diplomatic-range recruitment, iterate documented broader targets (prefer diplomatic-range rulers and their courts), then filter court status and vanilla eligibility.
- For previewable ranked roster upgrades, combine incumbents and candidates in a temporary list, order by score, cap at the roster limit, and apply effects only to candidate entries in the final top set. Do not rely on variables assigned earlier in the same decision effect.
- Manual guardian browsers use iseandfall_guardian_recruitment_score_value and a ten-candidate limit. Keep household demand and existing-teacher checks out of their preparation effects: those gates suppress all results before ranking, even when a stronger teacher is recruitable.
- For manual choices that must improve a capped roster, reuse the combined incumbent/candidate ranking and expose only candidates that survive the roster cap. Rebuild it after each selection so the refreshed choices account for the changed roster.
- Vanilla `invite_to_court_interaction` adds +20 AI acceptance when `cover_travel_expenses` is selected. Since `is_character_interaction_potentially_accepted` has no send-option parameter, use its `ai_accept` threshold of `-20` to check that the candidate reaches acceptance with that option; also require the default threshold to be rejected when separating paid from free invites.
- A free foreign-court invitation must call `is_character_interaction_potentially_accepted` for the vanilla interaction with no send-option scopes; validity alone does not prove acceptance without paid expenses, Influence, or a Hook.
- Interaction `ai_potential` runs with the actor as root only. Keep actor-only checks there; put actor/recipient checks in `ai_will_do` or a block where both scopes exist.
- Feature-specific scripted-score bonuses must repeat the feature’s current eligibility gate in each copied score/appointment definition.

## Hooks, armies, and war callbacks

- Keep on_action handlers small and dispatch through `effect = { ... }`. Gate optional mechanics with `has_game_rule`; define rules under `common/game_rules/` with the `riseandfall` category.
- Yearly loops such as `every_ruler` do not provide an implicit `root`. Save the current character before nested title scopes when code must return to it. Do not call a whole-world `every_ruler` repair from a character-rooted code hook; use a root-specific repair to avoid recursive fan-out.
- `spawn_army.location` needs a province target such as `capital_province`, not `capital_barony`. Its `save_scope_as` may be unset when not at war; guard before using it.
- To maintain owner-wide regiments including unraised event troops, use the character’s `every_maa_regiment` and filter `is_event_maa_regiment`, not `every_army`.
- `create_maa_regiment.size` accepts a literal integer. For a dynamic size, snapshot existing regiments, create at size 1, identify the new regiment by list exclusion, then resize it with `change_maa_regiment_size` using a saved scope value.
- `ai_start_best_war.is_valid`, `on_success`, and `on_failure` receive only documented callback scopes. Persist prepared character/title targets as typed variables on `root`, compare to `scope:target_character` / `scope:target_title` with `?=`, and remove them after the synchronous call returns.
- `is_landed` means holding a county or barony; landless adventurers satisfy `is_landed = no`. Let vanilla `can_declare_war` validate their claim-war CB rather than adding landed-hierarchy restrictions.
- Income values such as `yearly_character_income` and `year_character_treasury_variable_income` can provide numeric scripted values. For divided indemnities, compute positive-clamped gold/treasury in payer-scoped values, then use `pay_short_term_gold` or `pay_short_term_treasury`; income-payment helpers reject negative net income.

## Decision to persist a rule

When adding a reusable rule, document the verified engine behavior and the safe pattern, not a one-off symptom. Keep title/office lifecycle guidance in `ck3-realm-systems.md`.
