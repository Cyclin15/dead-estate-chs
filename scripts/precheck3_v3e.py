# Round 3 checks.
import json, re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

p = json.load(open('dump/pristine_strings.json', encoding='utf-8'))
t = json.load(open('dump/translations.json', encoding='utf-8'))
rev = {}
for k, v in p.items():
    rev.setdefault(v, []).append(k)

def show(s):
    print(f'  {s!r} idx={rev.get(s)} cur={ {i: t.get(i) for i in rev.get(s, [])} }')

print('===== rumble composite parts:'); [show(s) for s in [' intensity', "Adjusts the intensity of the controller's ", ' features.', 'rumble']]
print('===== misc tracks/titles:'); [show(s) for s in ['Milkbar Lads Intro', 'Dead Estate', 'Green thing', 'Blue thing']]

src = open('dump/CodeEntries/gml_Object_levelController_Create_0.gml', encoding='utf-8').read().splitlines()
print('===== levelController 720-735:')
for i in range(719, min(735, len(src))):
    print(f'  {i+1}: {src[i].strip()[:180]}')

# prefixes: Inserted/That/FLOOR/COSTUME/Insert usage
for f in ['Inserted ', 'That ', 'FLOOR ', 'COSTUME ', 'Insert ', 'FLOOR', 'COSTUME']:
    print(f'===== usages of {f!r}:')
    for fn in os.listdir('dump/CodeEntries'):
        path = os.path.join('dump/CodeEntries', fn)
        for i, line in enumerate(open(path, encoding='utf-8'), 1):
            if f'"{f}' in line or (f.endswith(' ') and f'"{f}"' in line):
                print(f'   {fn}:{i}: {line.strip()[:160]}')

src = open('dump/CodeEntries/gml_Object_newCharacterSelect_Create_0.gml', encoding='utf-8').read().splitlines()
print('===== newCharacterSelect 185-205:')
for i in range(184, min(205, len(src))):
    print(f'  {i+1}: {src[i].strip()[:180]}')

# Anya item descriptions for the 5 names
s = open('dump/CodeEntries/gml_GlobalScript_scrAnyaItems.gml', encoding='utf-8').read()
print('===== Anya items context:')
for nm in ['Book', 'Plunger', 'Meat', 'Choker', 'Sticker']:
    m = re.search(rf'self\.name = "{nm}";(.{{0,400}})', s, re.S)
    print(f'  --- {nm}: {m.group(1)[:260]!r}' if m else f'  --- {nm}: NOT FOUND')

# how is oAnyaLevelController name consumed?
s = open('dump/CodeEntries/gml_Object_oAnyaLevelController_Create_0.gml', encoding='utf-8').read()
print('===== oAnyaLevelController name consumption:')
for i, line in enumerate(s.splitlines(), 1):
    if re.search(r'\bname\b', line) and ('draw' in line.lower() or 'areaName' in line or '.name ==' in line or 'find' in line.lower()):
        print(f'  {i}: {line.strip()[:170]}')
# AreaName object
s = open('dump/CodeEntries/gml_Object_oAnyaBallroomAreaName_Create_0.gml', encoding='utf-8').read()
print('===== oAnyaBallroomAreaName full:'); print(s)
# who reads AreaName name?
for fn in os.listdir('dump/CodeEntries'):
    if 'AreaName' in fn: continue
    path = os.path.join('dump/CodeEntries', fn)
    body = open(path, encoding='utf-8').read()
    if 'AreaName' in body and ('name' in body):
        for i, line in enumerate(body.splitlines(), 1):
            if 'AreaName' in line and 'name' in line:
                print(f'  {fn}:{i}: {line.strip()[:170]}')
