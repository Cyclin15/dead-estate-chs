# -*- coding: utf-8 -*-
# List all currently-translated entries whose pristine text is a single token
# (no whitespace) — candidates for the "single words stay English" policy.
import json, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

p = json.load(open('dump/pristine_strings.json', encoding='utf-8'))
t = json.load(open('dump/translations.json', encoding='utf-8'))

# fragments that compose sentences — must stay translated even though single-token
FRAG = {
    'Fires ', 'exploding', ' bullets.', 'burst', ' of ', 'lasers', 'Throw ', 'rapid-fire',
    'heavy', 'Become ', 'Does ', 'Radioactive', 'six', ' radioactive', ' bullets',
    ' enemies.', ' larger', 'explosions', ' will ', ' which ', 'A ', 'mini-Chunks',
    'Triples', 'pinatas', 'radioactive', 'release', 'become ', 'explode', 'GOT ',
    'Took ', 'Placed ', 'Used ', 'Inserted ', 'Insert ', 'Place ', ' sticker', 'That ',
    ' intensity', ' features.', 'the ', 'next ', 'level', 'floor', 'Building', 'Generating',
    'Assembling', 'Constructing', 'FLOOR ', 'COSTUME ', "Erectin'",
}

rows = []
for k, v in t.items():
    orig = p.get(k, '')
    if not orig or any(c.isspace() for c in orig):
        continue          # multi-word or unknown -> out of scope here
    if orig in FRAG:
        continue
    rows.append((int(k), orig, v))

rows.sort()
print(f'{len(rows)} single-token translated entries:')
for i, orig, tr in rows:
    print(f'[{i}] {orig!r} -> {tr!r}')
