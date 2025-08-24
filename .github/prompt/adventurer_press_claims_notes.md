## Adventurer press-claims — notes, fixes, and test checklist

Summary
- Goal: make landless adventurer leaders more aggressive about pressing their claims (prefer kingdom-tier claims).
- Outcome: implemented a scripted effect called `riseandfall_adventurer_press_claims_se`, registered a yearly on_action, diagnosed and fixed several script/system issues, and validated `start_war` usage so the effect runs without script errors and attempts wars.

Tiny contract (inputs / outputs / success criteria / error modes)
- Inputs: on_action yearly trigger (character scope saved as `independent_adventurer`), the adventurer's claims list.
- Outputs: engine `start_war` call attempting to press a selected claim (casus_belli = `claim_cb`).
- Success: no script-system errors, `start_war` is executed by the adventurer and the engine accepts the war request (or the war is created when engine conditions permit).
- Error modes: unsupported `random_claim` params causing no selection, wrong `start_war` scope leading to "Wrong scope" errors, missing `target_title` leading to "No valid titles found", vacant titles causing skipped attempts.

What we changed (chronological / delta)
- Added `riseandfall_adventurer_press_claims_se` in `common/scripted_effects/riseandfall_adventurer_effects.txt`:
  - Iterates adventurer claims using `random_claim` with a `limit` filter (initially attempted to use unsupported params `explicit = yes` / `pressed = no` — removed).
  - Calls `start_war` from a saved character scope (`scope:independent_adventurer`) so the claimant scope is valid.
  - Initially added debug toasts to observe runtime behavior, later removed after fixes.
- Added/updated on_action `riseandfall_yearly_adventurer_press_claims` in `common/on_action/riseandfall_adventurer_on_actions.txt`:
  - Uses `every_ruler` with `save_scope_as = independent_adventurer` then calls the scripted effect so `scope:independent_adventurer` is available inside the SE.
- Localization changes:
  - Added then removed debug loc entries. No permanent UI loc changes were left behind for the debug keys.

Root causes we found and fixes applied
- Unsupported `random_claim` parameters (explicit/pressed):
  - Symptom: iterator produced no useful results or silent failures. Fix: removed unsupported params and used `random_claim` with a `limit = { ... }` filter instead.
- start_war scope errors (landed_title vs character):
  - Symptom: "Wrong scope for effect: landed_title, expected character" when start_war was run from a non-character scope.
  - Fix: call start_war under `scope:independent_adventurer` (saved character scope in the on_action) so claimant is a character.
- start_war "No valid titles found" error:
  - Symptom: engine log: "start_war effect [ No valid titles found for start_war effect ]".
  - Fix: include `target_title = scope:claim_target_title` when calling `start_war` for claim CBs; this satisfies engine validation that a target title is provided.
  - After adding `target_title` the script stopped producing that specific error.
- Debug toasts not visible or noisy:
  - Symptom: debug toasts didn't appear or cluttered testing.
  - Fix: removed persistent debug toasts; used short-lived debug edits only when necessary, then removed them.

Validation & quality gates performed
- Syntax/scope: validated against `docs/effects.log` and example engine event files. Confirmed `start_war` signature and that `random_claim` exists and supports `limit`.
- Local checks: verified `descriptor.mod` path and that localization file is loaded under `localization/english/`.
- Runtime: after fixes, the script no longer produced the earlier script errors; `start_war` is now called with claimant and a title parameter.

How to test (manual, in-game)
1) Enable the `riseandfall` mod and load a save with landless adventurers.
2) Wait for a yearly tick (the effect is on `yearly_global_pulse`).
3) Confirm no script-system errors in the game's log (look for jomini errors in `error.log` or the console output).
4) Observe whether adventurers attempt wars. If wars aren't created, check logs for start_war acceptance/rejection and the reason.

Quick debugging hints if still not firing
- If scripted effect never runs: ensure adventurer meets `every_ruler` on_action limits (is_adult, not imprisoned, has_realm_law = `camp_purpose_legitimists`, not at war).
- If `random_claim` doesn't pick anything: temporarily relax `limit = { tier >= tier_kingdom }` to `tier >= tier_duchy` or remove the `limit` to confirm whether claim scarcity is the blocker.
- If chosen title is vacant (no holder): consider a fallback to `scope:claim_target_title.de_jure_holder` or skip to another claim.

Next low-risk improvements (recommended)
- Add a small fallback in the SE: if `exists = scope:claim_target_title.holder` is false, try `exists = scope:claim_target_title.de_jure_holder` and use that as `target` (or skip if still invalid).
- Add a missing-loc + duplicate-ID scan script under `tools/` (recommended in repo guidelines). Small scripts exist in the Copilot instructions; consider adding `riseandfall/tools/duplicate-ids.ps1` and `missing-loc.ps1` as low-risk extras.
- Consider adding a short unit test or in-mod event that can be triggered in a save to reliably reproduce the flow during development (for easier iteration).

Files touched (summary)
- common/scripted_effects/riseandfall_adventurer_effects.txt — implemented `riseandfall_adventurer_press_claims_se`, debug iterations, removal of unsupported params, final start_war signature.
- common/on_action/riseandfall_adventurer_on_actions.txt — ensured `save_scope_as = independent_adventurer` and registered `riseandfall_yearly_adventurer_press_claims` on yearly pulse.
- localization/english/riseandfall_adventurer_l_english.yml — temporary debug loc keys added then removed.

Edge cases to be aware of
- Claim scarcity: many adventurers may not have kingdom-tier explicit claims; this will make the SE skip often.
- Vacant titles: if titles are vacant, `start_war` needs a valid holder/target — add fallback logic if you want the adventurer to attack title directly.
- Engine differences: versions of CK3 may differ slightly; always check `docs/` files shipped in the repo and test on the target supported_version.

Completion status
- Implemented: scripted effect + on_action registration — DONE.
- Fixed: invalid `random_claim` parameters — DONE.
- Fixed: start_war scope and missing title validation error — DONE.
- Verified: no script system errors for the start_war call — DONE (per your report).

If you want, I can implement the recommended fallback for vacant titles or add a temporary non-UI debug event to print the chosen title/holder when testing — say which and I'll add it.

---
Generated on: 2025-08-23
