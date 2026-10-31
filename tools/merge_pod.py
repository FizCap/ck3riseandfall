"""Check or rebuild the reviewed Rise and Fall / Princes of Darkness overrides."""
from pathlib import Path
import argparse
import difflib
import re
import subprocess
import tempfile

PATCH = Path(__file__).resolve().parents[1]
RF = PATCH.parent / 'development'
POD = Path(r'C:\Program Files (x86)\Steam\steamapps\workshop\content\1158310\2216659254')
VANILLA = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Crusader Kings III\game')
TOKEN = r'"(?:\\.|[^"\\])*"|#[^\n]*|[{}]|[^\s{}"#]+'


def read(path):
    return path.read_text(encoding='utf-8-sig')


def blocks(text):
    tokens = list(re.finditer(TOKEN, text))
    depth, result = 0, {}
    for i, token in enumerate(tokens):
        if token[0] == '{':
            if depth == 0:
                assert i >= 2 and tokens[i-1][0] == '=', 'Unexpected top-level block'
                key, start = tokens[i-2][0], tokens[i-2].start()
                assert key not in result, f'Duplicate definition: {key}'
            depth += 1
        elif token[0] == '}':
            depth -= 1
            assert depth >= 0, 'Unmatched closing brace'
            if depth == 0:
                result[key] = text[start:token.end()]
    assert depth == 0, 'Unclosed block'
    return result


def merge(ours, base, theirs):
    with tempfile.TemporaryDirectory(prefix='rf-pod-') as directory:
        paths = [Path(directory) / name for name in ('ours', 'base', 'theirs')]
        for path, content in zip(paths, (ours, base, theirs)):
            path.write_text(content, encoding='utf-8', newline='\n')
        process = subprocess.run(['git', 'merge-file', '-p', *map(str, paths)], capture_output=True)
        assert process.returncode == 0, process.stdout.decode('utf-8') + process.stderr.decode('utf-8')
        return process.stdout.decode('utf-8').replace('\r\n', '\n')


def feature_gui(relative, expected):
    base = read(VANILLA / relative).splitlines(True)
    rf = read(RF / relative).splitlines(True)
    feature, count = [], 0
    # RF copies also contain older vanilla layout changes. Transplant only
    # RF feature additions so current PoD controls and engine widgets survive.
    for tag, a, b, c, d in difflib.SequenceMatcher(None, base, rf, autojunk=False).get_opcodes():
        chunk = ''.join(rf[c:d])
        keep = tag == 'insert' and ('riseandfall' in chunk.lower() or 'rf_disqualify' in chunk)
        feature.extend(rf[c:d] if keep else base[a:b])
        count += keep
    assert count == expected, f'{relative}: expected {expected} feature additions, found {count}; review source changes'
    return merge(read(POD / relative), ''.join(base), ''.join(feature))


def build():
    output = {relative: feature_gui(relative, expected) for relative, expected in (
        ('gui/window_character.gui', 2), ('gui/window_title.gui', 1),
        ('gui/interaction_menu_window.gui', 1), ('gui/map_icon_layer.gui', 2),
        ('gui/shared/mapmodes.gui', 1),
    )}
    relative = 'common/laws/00_succession_laws.txt'
    base, rf, pod = (read(root / relative) for root in (VANILLA, RF, POD))
    feature = base.replace(blocks(base)['same_faith_theocratic_succession_law'],
                           blocks(rf)['same_faith_theocratic_succession_law'], 1)
    custom = [body for key, body in blocks(rf).items() if key.startswith('riseandfall_')]
    assert len(custom) == 3
    feature += '\n# Rise and Fall: temporary script-owned succession laws.\n' + '\n\n'.join(custom) + '\n'
    laws = merge(pod, base, feature)
    # PoD 1.20.1 assigns both clerical and theocratic election index 10.
    # Restore vanilla's unused clerical index 11 within this law group.
    original = blocks(laws)['clerical_appointment_law']
    assert re.search(r'\bindex\s*=\s*10\b', original)
    corrected = re.sub(r'\bindex\s*=\s*10\b',
                       '# Keep clerical appointment distinct from theocratic election (index 10).\n\tindex = 11', original, count=1)
    output[relative] = laws.replace(original, corrected, 1)

    # Retain PoD war blockers, Storyteller/Golconda, Dark Passion and pact effects.
    # RF's target validator changes only administrative Warlord war-law bans.
    war = blocks(read(POD / 'common/character_interactions/00_war.txt'))['declare_war_interaction']
    old = 'allows_declaring_war_against_target_trigger = { TARGET = scope:recipient }'
    assert war.count(old) == 1
    output['common/character_interactions/riseandfall_war.txt'] = (
        '# Preserve PoD declaration restrictions and effects while adding RF Warlord war-law exceptions.\n'
        + war.replace(old, 'riseandfall_' + old) + '\n')
    # A future PoD validator change requires a real merge into RF's validator.
    relative = 'common/scripted_triggers/00_war_and_peace_triggers.txt'
    key = 'allows_declaring_war_against_target_trigger'
    assert blocks(read(POD / relative))[key] == blocks(read(VANILLA / relative))[key], 'PoD changed the shared war validator'

    relative = 'common/character_interaction_categories/riseandfall_interaction.txt'
    pod_categories = read(POD / 'common/character_interaction_categories/00_character_interaction_categories.txt')
    indices = [int(x) for x in re.findall(r'\bindex\s*=\s*(\d+)', pod_categories)]
    assert sorted(indices) == list(range(max(indices) + 1))
    output[relative] = ('# Place Rise and Fall after every PoD interaction category.\n'
        + re.sub(r'index\s*=\s*\d+[^\n]*', f'index = {max(indices)+1}', read(RF / relative)))

    relative = 'common/casus_belli_types/riseandfall_claim_cb.txt'
    claims = read(RF / relative)
    old = 'is_weak_claimant_due_to_gender_trigger = { FAITH = scope:attacker.faith'
    assert claims.count(old) == 2
    claims = claims.replace(old, 'is_weak_claimant_due_to_gender_trigger = { RITE = scope:attacker.rite')
    anchor = '        scope:claimant = {\n            NOT = { has_trait = incapable }\n            is_hostage = no\n'
    assert claims.count(anchor) == 1
    claims = claims.replace(anchor, '''        # Match PoD's claimant availability and Shadow Inquisition restrictions.
        NAND = {
            scope:attacker = {
                faith = faith:shadowinquisition
                is_ai = yes
            }
            scope:defender = { faith = faith:shadowinquisition }
        }
        scope:claimant = {
            NOT = { has_trait = incapable }
            is_hostage = no
            custom_description = {
                text = is_not_a_minister_desc
                tgp_is_any_minister = no
            }
            POD_is_available = yes
            NAND = {
                has_trait = mortal
                can_hold_title_as_mortal_trigger = no
            }
''', 1)
    output[relative] = ('# PoD claim strength follows the attacker\'s Rite; its trigger does not accept FAITH.\n'
        + claims)
    return {relative: '\n'.join(line.rstrip() for line in content.splitlines()) + '\n'
            for relative, content in output.items()}


def validate(output):
    for folder, pattern in (('common', '*.txt'), ('gui', '*.gui'), ('events', '*.txt')):
        for path in (RF / folder).rglob(pattern):
            relative = path.relative_to(RF).as_posix()
            if (POD / relative).is_file():
                assert relative in output, f'Unmerged same-path override: {relative}'
    for relative, content in output.items():
        assert not re.search(r'^(<<<<<<<|=======|>>>>>>>)', content, re.M), relative
        if relative.endswith('.gui'):
            depth = 0
            for token in re.finditer(TOKEN, content):
                if token[0] == '{':
                    depth += 1
                elif token[0] == '}':
                    depth -= 1
                    assert depth >= 0, relative
            assert depth == 0, relative
        else:
            blocks(content)
    relative = 'common/laws/00_succession_laws.txt'
    assert set(blocks(read(POD / relative))) <= set(blocks(output[relative]))
    # Include vanilla law files not overridden by PoD in the effective load.
    files = {path.name: path for path in (VANILLA / 'common/laws').glob('*.txt')}
    files.update({path.name: path for path in (POD / 'common/laws').glob('*.txt')})
    occupied = {}
    for name, path in files.items():
        contents = output[relative] if name == '00_succession_laws.txt' else read(path)
        for key, body in blocks(contents).items():
            group = re.search(r'\blaw_group_type\s*=\s*(\w+)', body)
            index = re.search(r'\bindex\s*=\s*(\d+)', body)
            if group and index:
                slot = (group[1], index[1])
                assert slot not in occupied, f'Law index collision: {key} / {occupied.get(slot)}'
                occupied[slot] = key


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Write merges; default checks without writing game files')
    args = parser.parse_args()
    output = build()
    validate(output)
    for relative, content in output.items():
        path = PATCH / relative
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8-sig', newline='\r\n')
        else:
            assert path.is_file() and read(path) == content, f'Outdated merge: {relative}'
            assert path.read_bytes().startswith(b'\xef\xbb\xbf'), f'Missing BOM: {relative}'
        print(('WROTE ' if args.write else 'PASS ') + relative)
