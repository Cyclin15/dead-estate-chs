# Round 4 checks.
import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

p = json.load(open('dump/pristine_strings.json', encoding='utf-8'))
t = json.load(open('dump/translations.json', encoding='utf-8'))
rev = {}
for k, v in p.items():
    rev.setdefault(v, []).append(k)

def show(s):
    print(f'  {s!r} idx={rev.get(s)} cur={ {i: t.get(i) for i in rev.get(s, [])} }')

src = open('dump/CodeEntries/gml_Object_levelController_Create_0.gml', encoding='utf-8').read().splitlines()
print('===== levelController 726 full + 727:')
print('  ', src[725].strip())
if len(src) > 726: print('  ', src[726].strip())

s = open('dump/CodeEntries/gml_Object_levelIntroHandler_PreCreate_0.gml', encoding='utf-8').read()
print('===== levelIntroHandler_PreCreate full:'); print(s)
s = open('dump/CodeEntries/gml_Object_levelIntroHandler_Create_0.gml', encoding='utf-8').read()
print('===== levelIntroHandler_Create full:'); print(s[:1500])

print('===== fragment status:')
for x in [' into the empty slot.', " was just a sticker! I'm gonna take it off the painting.",
          'Insert 8 Ball', 'Putting together', "Erectin'", ' the ', ' floor', ' floor.',
          'Autumn Emblem', 'Spring Emblem', 'Summer Emblem', 'Winter Emblem']:
    show(x)

# emblemNames array source
s = open('dump/CodeEntries/gml_Object_oAnyaPedestalPuzzle_Step_0.gml', encoding='utf-8').read()
print('===== emblemNames in pedestal puzzle:')
for i, line in enumerate(s.splitlines(), 1):
    if 'emblemNames' in line and ('=' in line or '[' in line):
        print(f'  {i}: {line.strip()[:160]}')

# Anya item name+desc pairs (broader regex)
s = open('dump/CodeEntries/gml_GlobalScript_scrAnyaItems.gml', encoding='utf-8').read()
print('===== Anya item blocks:')
for nm in ['Book', 'Plunger', 'Meat', 'Choker', 'Sticker']:
    m = re.search(rf'self\.name = "{nm}";((?:.|\n){{0,300}})', s)
    if m:
        txt = m.group(1)
        d = re.search(r'self\.description = "([^"]*)"', txt)
        print(f'  {nm}: desc={d.group(1)[:120] if d else "?"}')

# floor text pieces after 726
src2 = open('dump/CodeEntries/gml_Object_levelController_Create_0.gml', encoding='utf-8').read()
m = re.search(r'generatingFloorText = concat\((.*?)\);', src2, re.S)
if m:
    print('===== generatingFloorText parts:')
    for q in re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1)):
        idx = rev.get(q, ['?'])[0]
        print(f'  {q!r} idx={idx} cur={t.get(idx)!r}')
