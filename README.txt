Rise and Fall : EK2 Compatibility Patch 1.1.0

Sources reviewed: Rise and Fall 1.4.6, Elder Kings 2 0.21.1.1 (Workshop
2887120253), and installed CK3 1.20 scripting/GUI examples.

Enable all three mods, in this order:
1. Elder Kings 2
2. Rise and Fall
3. Rise and Fall : EK2 Compatibility Patch

This folder is a compatibility patch and requires both base mods. Unique
Rise and Fall content, icons, tooltips, localization, map overlays, and scripted
systems are inherited from Rise and Fall. Do not replace Elder Kings with a
copy of the standalone Rise and Fall mod.

Merged overrides:
- Character window: Elder Kings layout, plus adventurer chance and stability.
- Title window: Elder Kings controls, plus the title giveaway exclusion button.
- Map modes: Elder Kings modes, plus the Rise and Fall fort overlay toggle.
- Succession: all 48 Elder Kings laws in 00_succession_laws.txt, plus three
  script-owned Rise and Fall laws and its explicit theocratic faith-head pool.
- Administrative appointments: Elder Kings scores, including Arcana, plus
  Rise and Fall Warlord-family, Puppet Regency, and assigned score adjustments.
- Declare War: current Elder Kings GCM/Writ of War and puppet-aware flow,
  using Rise and Fall's administrative Warlord war-law exceptions.
- Interaction categories: Rise and Fall follows Magic at index 17.
- Claim CB: gender-based claim strength uses Elder Kings' Rite argument.
- Historical-map exceptions: France/Aquitaine special title handling and the
  HRE restoration option are disabled. Dynamic successors use ordinary elective
  succession in the HRE-specific fallback. The Warlord conquest AI no longer
  checks the absent Frankokratia story. Other branches remain inherited intact.

Maintenance (Python 3 and Git required, from this folder):
  python tools/merge_ek2.py
Checks all 14 generated overrides, block balance, BOMs, law-index collisions,
and shared validators against current installed sources without writing files.
  python tools/merge_ek2.py --write
Rebuilds the reviewed integrations. Review diffs and rerun an in-game check
when either base mod changes. A passing source check does not prove visual fit,
interactive commands, a successful succession, or long-running campaign behavior.

Runtime evidence and remaining checks are recorded in VALIDATION.txt.
