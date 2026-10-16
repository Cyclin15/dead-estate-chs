# -*- coding: utf-8 -*-
# v3e-2: policy change — single-token (single word) UI strings stay ENGLISH.
# Revert ALL single-token translations (v3d-era ones AND the v3e batch), except:
#   - sentence fragments used in concat() composition (must stay translated)
#   - identity mappings (translation == pristine, no visual change)
#   - 'Rumble intensity': twin of the composed label "Rumble"+" intensity", which
#     stays English because 'Rumble'/' intensity' are single-token labels -> both
#     twins must show the same English text.
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

p = json.load(open('dump/pristine_strings.json', encoding='utf-8'))
t = json.load(open('dump/translations.json', encoding='utf-8'))

FRAG = {
    'Fires ', 'exploding', ' bullets.', 'burst', ' of ', 'lasers', 'Throw ', 'rapid-fire',
    'heavy', 'Become ', 'Does ', 'Radioactive', 'six', ' radioactive', ' bullets',
    ' enemies.', ' larger', 'explosions', ' will ', ' which ', 'A ', 'mini-Chunks',
    'Triples', 'pinatas', 'radioactive', 'release', 'become ', 'explode', 'GOT ',
    'Took ', 'Placed ', 'Used ', 'Inserted ', 'Insert ', 'Place ', ' sticker', 'That ',
    ' intensity', ' features.', 'the ', 'next ', 'level', 'floor', 'Building', 'Generating',
    'Assembling', 'Constructing', 'FLOOR ', 'COSTUME ', "Erectin'",
}

# multi-word twin-consistency reverts (composed label stays English)
EXTRA_REVERT = {
    'Rumble intensity': '震动强度',
}

deleted = []
kept_identity = []
for k in list(t.keys()):
    orig = p.get(k, '')
    if not orig or any(c.isspace() for c in orig):
        continue
    if orig in FRAG:
        continue
    if t[k] == orig:
        kept_identity.append(orig)
        continue
    deleted.append((int(k), orig, t[k]))
    del t[k]

for orig, cur in EXTRA_REVERT.items():
    hits = [k for k, v in p.items() if v == orig]
    assert len(hits) == 1, (orig, hits)
    if t.get(hits[0]) == cur:
        deleted.append((int(hits[0]), orig, t[hits[0]]))
        del t[hits[0]]

deleted.sort()
json.dump(t, open('dump/translations.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'reverted {len(deleted)} single-token entries (+{len(EXTRA_REVERT)} twin); '
      f'kept {len(kept_identity)} identity mappings; total now {len(t)}')
for i, orig, tr in deleted[:8]:
    print(f'  [{i}] {orig!r} (was {tr!r})')
print('  ...')
