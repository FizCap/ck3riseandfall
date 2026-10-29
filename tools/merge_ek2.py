"""Rebuild the focused EK2 overrides, or check them without writing game files."""
from pathlib import Path
import argparse
import difflib
import re
import subprocess
import tempfile

PATCH = Path(__file__).resolve().parents[1]
RF = PATCH.parent / 'development'
EK = Path(r'C:\Program Files (x86)\Steam\steamapps\workshop\content\1158310\2887120253')
VANILLA = Path(r'C:\Program Files (x86)\Steam\steamapps\common\Crusader Kings III\game')


def read(path):
    return path.read_text(encoding='utf-8-sig')


def blocks(text):
    """Return top-level definitions while ignoring quoted braces and comments."""
    tokens = list(re.finditer(r'"(?:\\.|[^"\\])*"|#[^\n]*|[{}]|[^\s{}"#]+', text))
    depth = 0
    result = {}
    for i, token in enumerate(tokens):
        value = token[0]
        if value.startswith(('#', '"')):
            continue
        if value == '{':
            if depth == 0:
                assert i >= 2 and tokens[i-1][0] == '=', 'Unexpected top-level block'
                key, start = tokens[i-2][0], tokens[i-2].start()
                assert key not in result, f'Duplicate definition: {key}'
            depth += 1
        elif value == '}':
            depth -= 1
            assert depth >= 0, 'Unmatched closing brace'
            if depth == 0:
                result[key] = text[start:token.end()]
    assert depth == 0, 'Unclosed block'
    return result


def merge(ours, base, theirs):
    with tempfile.TemporaryDirectory(prefix='rf-ek2-') as directory:
        paths = [Path(directory) / name for name in ('ours', 'base', 'theirs')]
        for path, content in zip(paths, (ours, base, theirs)):
            path.write_text(content, encoding='utf-8')
        process = subprocess.run(['git', 'merge-file', '-p', *map(str, paths)], capture_output=True)
        assert process.returncode == 0, process.stdout.decode('utf-8') + process.stderr.decode('utf-8')
        return process.stdout.decode('utf-8').replace('\r\n', '\n')


def feature_merge(relative):
    base = read(VANILLA / relative).splitlines(True)
    rf = read(RF / relative).splitlines(True)
    feature = []
    count = 0
    # Current RF copies include older vanilla layout differences. Only transplant
    # feature insertions, so EK's own layout and updated vanilla widgets survive.
    for tag, a, b, c, d in difflib.SequenceMatcher(None, base, rf, autojunk=False).get_opcodes():
        inserted = ''.join(rf[c:d])
        keep = tag == 'insert' and ('riseandfall' in inserted.lower() or 'rf_disqualify' in inserted)
        feature.extend(rf[c:d] if keep else base[a:b])
        count += keep
    expected = 2 if relative == 'gui/window_character.gui' else 1
    assert count == expected, f'{relative}: expected {expected} feature insertions, found {count}; review upstream changes'
    return merge(read(EK / relative), ''.join(base), ''.join(feature))


def block_end(text, start):
    depth = 0
    opened = False
    for token in re.finditer(r'"(?:\\.|[^"\\])*"|#[^\n]*|[{}]', text[start:]):
        if token[0] == '{':
            depth += 1
            opened = True
        elif token[0] == '}':
            depth -= 1
            if opened and depth == 0:
                return start + token.end()
    raise AssertionError('Unclosed block')


def build():
    output = {relative: feature_merge(relative) for relative in (
        'gui/window_character.gui', 'gui/window_title.gui', 'gui/shared/mapmodes.gui',
        'common/succession_appointment/admin_emperor.txt',
        'common/succession_appointment/admin_governor.txt',
    )}
    relative = 'common/laws/00_succession_laws.txt'
    base, rf, ek = (read(root / relative) for root in (VANILLA, RF, EK))
    # Preserve all EK law conditions and add the three script-owned RF laws.
    # Also retain RF's explicit theocratic heir pool for spiritual faith heads.
    feature = base
    original = blocks(base)['same_faith_theocratic_succession_law']
    feature = feature.replace(original, blocks(rf)['same_faith_theocratic_succession_law'], 1)
    custom = [body for key, body in blocks(rf).items() if key.startswith('riseandfall_')]
    assert len(custom) == 3
    feature += '\n# Rise and Fall: temporary script-owned succession laws.\n' + '\n\n'.join(custom) + '\n'
    output[relative] = merge(ek, base, feature)

    # EK's current declaration already supports puppets and Writ of War.
    # Swap only the target validator for RF's administrative Warlord exceptions.
    war = blocks(read(EK / 'common/character_interactions/00_war.txt'))['declare_war_interaction']
    old = 'allows_declaring_war_against_target_trigger = { TARGET = scope:recipient }'
    assert war.count(old) == 1
    output['common/character_interactions/riseandfall_war.txt'] = (
        '# EK2 declaration flow, including GCM/Writ of War and native puppet scopes.\n'
        '# Warlords bypass only administrative war-law restrictions through the RF validator.\n'
        + war.replace(old, 'riseandfall_' + old) + '\n'
    )
    category = read(RF / 'common/character_interaction_categories/riseandfall_interaction.txt')
    indices = [int(x) for x in re.findall(r'\bindex\s*=\s*(\d+)', read(EK / 'common/character_interaction_categories/00_character_interaction_categories.txt'))]
    assert sorted(indices) == list(range(max(indices) + 1))
    output['common/character_interaction_categories/riseandfall_interaction.txt'] = (
        '# Keep Rise and Fall after every EK2 category, including Magic.\n'
        + re.sub(r'index\s*=\s*\d+[^\n]*', f'index = {max(indices) + 1}', category)
    )
    # EK replaces the historical map and the Frankokratia story database.
    # Remove inapplicable branches rather than inventing Tamriel equivalents.
    relative = 'common/scripted_effects/riseandfall_ai_title_creation_effects.txt'
    content = read(RF / relative)
    original = blocks(content)['riseandfall_ai_create_france_aquitaine_titles_se']
    output[relative] = content.replace(original, 'riseandfall_ai_create_france_aquitaine_titles_se = {\n'
        '    # EK2 has no France or Aquitaine; retain the shared caller as a no-op.\n}', 1)

    relative = 'common/scripted_effects/riseandfall_ai_title_handout_effects.txt'
    content = read(RF / relative)
    original = ('                # France and Aquitaine are deliberately kept together until\n'
                '                # the holder can take the unification decision.\n'
                '                NOT = { this = title:k_france }\n'
                '                NOT = { this = title:k_aquitaine }\n')
    assert content.count(original) == 1
    output[relative] = content.replace(original, '                # EK2 has no historical France/Aquitaine crown exemption.\n', 1)

    relative = 'common/scripted_effects/riseandfall_realm_split_effects.txt'
    content = read(RF / relative)
    start = content.index('            # Vanilla restricts Princely Elective to e_hre.')
    end = content.index('\n        }\n        else_if', start)
    output[relative] = content[:start] + ('            # EK2 has no HRE; dynamic successors use ordinary elective succession.\n'
        '            add_title_law = feudal_elective_succession_law') + content[end:]

    relative = 'events/riseandfall_war_enhancement_events.txt'
    content = read(RF / relative)
    marker = content.index('name = riseandfall_war_enhancement.1.f')
    start = content.rfind('\t# Option: We should restore the Princely Elective system.', 0, marker)
    assert start >= 0
    end = block_end(content, content.index('\toption = {', start))
    output[relative] = content[:start] + '\t# EK2 has no HRE restoration option.\n' + content[end:]

    relative = 'common/casus_belli_types/riseandfall_warlord_conquest.txt'
    content = read(RF / relative)
    start = content.index('        #Declaring war on the frankokratia leader')
    end = block_end(content, content.index('        if = {', start))
    output[relative] = content[:start] + '        # EK2 has no Frankokratia story to protect from this conquest.\n' + content[end:]

    relative = 'common/casus_belli_types/riseandfall_claim_cb.txt'
    content = read(RF / relative)
    original = 'is_weak_claimant_due_to_gender_trigger = { FAITH = scope:attacker.faith'
    assert content.count(original) == 2
    output[relative] = ('# EK2 gender-based claim strength follows the attacker\'s Rite, not the vanilla Faith argument.\n'
        + content.replace(original, 'is_weak_claimant_due_to_gender_trigger = { RITE = scope:attacker.rite'))
    # Check shared validators as well as same-path overlaps. These currently
    # differ from vanilla only by RF's intended guards; fail if EK changes them.
    for file, keys in (
        ('common/scripted_triggers/00_war_and_peace_triggers.txt', ['allows_declaring_war_against_target_trigger']),
        ('common/scripted_triggers/10_tgp_triggers.txt', ['tgp_can_be_a_minister_trigger', 'tgp_can_be_grand_marshal_trigger']),
    ):
        vanilla, elder = blocks(read(VANILLA / file)), blocks(read(EK / file))
        for key in keys:
            assert vanilla[key] == elder[key], f'EK changed {key}; merge its logic before rebuilding'
    return {relative: '\n'.join(line.rstrip() for line in content.splitlines()) + '\n'
            for relative, content in output.items()}


def validate(output):
    for folder, pattern in (('common', '*.txt'), ('gui', '*.gui'), ('events', '*.txt')):
        for path in (RF / folder).rglob(pattern):
            relative = path.relative_to(RF).as_posix()
            if (EK / relative).is_file():
                assert relative in output, f'Unmerged same-path override: {relative}'
    for relative, content in output.items():
        assert not re.search(r'^(<<<<<<<|=======|>>>>>>>)', content, re.M), relative
        assert not re.search(r'title:(?:e_hre|k_france|k_aquitaine)\b|story_type\s*=\s*frankokratia_story', content), relative
        if relative.endswith('.gui'):
            depth = 0
            for token in re.finditer(r'"(?:\\.|[^"\\])*"|#[^\n]*|[{}]', content):
                if token[0] == '{':
                    depth += 1
                elif token[0] == '}':
                    depth -= 1
                    assert depth >= 0, relative
            assert depth == 0, relative
        else:
            blocks(content)
    # Every EK law survives; custom laws use distinct indices within their group.
    relative = 'common/laws/00_succession_laws.txt'
    laws = blocks(output[relative])
    assert set(blocks(read(EK / relative))) <= set(laws)
    occupied = {}
    for path in (EK / 'common/laws').glob('*.txt'):
        contents = output[relative] if path.name == '00_succession_laws.txt' else read(path)
        for key, body in blocks(contents).items():
            group = re.search(r'\blaw_group_type\s*=\s*(\w+)', body)
            index = re.search(r'\bindex\s*=\s*(\d+)', body)
            if group and index:
                slot = (group[1], index[1])
                assert slot not in occupied, f'Law index collision: {key} / {occupied.get(slot)}'
                occupied[slot] = key


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Write the reviewed merge results; default only checks')
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
