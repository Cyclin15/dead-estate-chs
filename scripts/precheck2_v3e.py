# Round 2 checks (string keys!).
import json, re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

p = json.load(open('dump/pristine_strings.json', encoding='utf-8'))
t = json.load(open('dump/translations.json', encoding='utf-8'))
rev = {}
for k, v in p.items():
    rev.setdefault(v, []).append(k)

print('===== difficulty current values:')
for i in range(9078, 9090):
    print(f'  [{i}] {t.get(str(i))!r}')

print('===== string 332:', repr(p.get('332')))

# music player first addTrack calls
src = open('dump/CodeEntries/gml_Object_musicPlayer_Create_0.gml', encoding='utf-8').read()
qre = re.compile(r'"((?:[^"\\]|\\.)*)"')
print('===== first 3 addTrack calls:')
for m in list(re.finditer(r'addTrack\([^;]+\);', src))[:3]:
    print('  ', m.group(0)[:200])

# credits segments
segs = set(re.findall(r'CredSegment\("([^"]+)"', src))  # wrong file; do it right:
src2 = open('dump/CodeEntries/gml_Object_oAwakeningEndingController_Create_0.gml', encoding='utf-8').read()
segs = set(re.findall(r'CredSegment\("([^"]+)"', src2))
print('===== credit segments:')
for s in sorted(segs):
    idx = rev.get(s, ['?'])[0]
    print(f'  {s!r} idx={idx} -> {t.get(idx)!r}')

# rumbleTerm usage
src3 = open('dump/CodeEntries/gml_Object_controlSettingsMenu_Create_0.gml', encoding='utf-8').read()
print('===== controlSettingsMenu rumble context:')
for i, line in enumerate(src3.splitlines(), 1):
    if 'rumbleTerm' in line or 'Rumble' in line:
        print(f'  {i}: {line.strip()[:180]}')

# Took/Placed/Used/Inserted/Put away usages in scrAnyaItems
src4 = open('dump/CodeEntries/gml_GlobalScript_scrAnyaItems.gml', encoding='utf-8').read()
print('===== scrAnyaItems prefix usages:')
for i, line in enumerate(src4.splitlines(), 1):
    if re.search(r'concat\("(Took |Placed |Used |Inserted |Put away|Place |GOT )', line):
        print(f'  {i}: {line.strip()[:200]}')

# Anya sticker item names (for the sticker puzzle text)
for s in ['Moon sticker', 'Sticker', 'Place ', 'is needed to unlock the hatch.', 'Silver Coffin Key ']:
    print(f'--- {s!r} idx={rev.get(s)} cur={ {i: t.get(i) for i in rev.get(s, [])} }')

# Anya item descriptions around names (Book/Plunger/Meat/Choker/Sticker)
print('===== Anya item name/desc pairs:')
for m in re.finditer(r'self\.name = "(\w+)";\s*\n\s*self\.description = "([^"]*)"', src4):
    if m.group(1) in ('Book', 'Plunger', 'Meat', 'Choker', 'Sticker'):
        print(f'  {m.group(1)}: {m.group(2)[:150]}')

# Anya typewriter text patterns
print('===== Anya typewriter concat patterns:')
for i, line in enumerate(src4.splitlines(), 1):
    if 'setTypeWriterText' in line and 'concat' in line:
        print(f'  {i}: {line.strip()[:200]}')
