# Pre-translation safety checks for the v3e batch.
import json, re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

p = json.load(open('dump/pristine_strings.json', encoding='utf-8'))
t = json.load(open('dump/translations.json', encoding='utf-8'))
rev = {}
for k, v in p.items():
    rev.setdefault(v, []).append(k)

def show(s, label=None):
    print(f'--- {label or s!r}  idx={rev.get(s)}  cur={ {i: t.get(i) for i in rev.get(s, [])} }')

# A. generic fragments: find ALL usages across CodeEntries
frags = ['A ', ' of ', ' will ', ' which ', 'GOT ', ' enemies.', ' on destruction.',
         'Causes some pots to ', '. Enemies killed with ', ' at once.', ' jabs!',
         ' swings!', ' if you attack on beat.', ' sticker', 'Rumble', 'six',
         ' radioactive', ' bullets', 'burst', 'Fires ', 'Throw ', 'Take', 'Read']
usage = {f: [] for f in frags}
qre = re.compile(r'"((?:[^"\\]|\\.)*)"')
for fn in os.listdir('dump/CodeEntries'):
    path = os.path.join('dump/CodeEntries', fn)
    for i, line in enumerate(open(path, encoding='utf-8'), 1):
        if '"' not in line:
            continue
        for m in qre.finditer(line):
            if m.group(1) in usage:
                usage[m.group(1)].append(f'{fn}:{i}: {line.strip()[:150]}')
for f in frags:
    print(f'===== usages of {f!r} (idx {rev.get(f)}): {len(usage[f])}')
    for u in usage[f][:12]:
        print('   ', u)

# B. painting puzzle: where do allScreens keys come from?
src = open('dump/CodeEntries/gml_Object_oAnyaGalleryPaintingPuzzle_Create_0.gml', encoding='utf-8').read()
print('===== oAnyaGalleryPaintingPuzzle_Create_0 (first 90 lines):')
print('\n'.join(src.splitlines()[:90]))

# E. existing translations for style reference
for s in ['New run', 'Give up', 'Throw in the towel', 'Try again', 'Give it another go',
          'Start over', 'GAME OVER.', 'YOU DIED.', 'Took ', 'Placed ', 'Used ', 'Inserted ',
          "SCOUT'S BADGE", 'Mmm??..', 'Mm mm', 'Mm!!', 'Mmm?', 'Mmm mmm', 'Check inventory',
          'Toggles fullscreen mode on and off.',
          'When enabled, your character will aim directly towards the crosshair even when jumping or falling.']:
    show(s)

# difficulty descriptions current state
print('===== difficulty strings 9078-9089:')
for i in range(9078, 9090):
    print(f'  [{i}] orig={p[str(i)]!r}')
    print(f'        cur ={t.get(i)!r}')

# music player: multi-word track names already translated?
src = open('dump/CodeEntries/gml_Object_musicPlayer_Create_0.gml', encoding='utf-8').read()
print('===== music tracks (name arg translation state):')
for m in re.finditer(r'addTrack\(([^;]+)\);', src):
    parts = [x for x in qre.findall(m.group(1))]
    if parts:
        name = parts[0] if len(parts) >= 2 else '?'
        idx = rev.get(name, ['?'])[0]
        print(f'  {name!r} idx={idx} -> {t.get(idx)!r}')

# credits: segment titles + Cast
src = open('dump/CodeEntries/gml_Object_oAwakeningEndingController_Create_0.gml', encoding='utf-8').read()
segs = set(re.findall(r'CredSegment\("([^"]+)"', src))
print('===== credit segments:')
for s in sorted(segs):
    idx = rev.get(s, ['?'])[0]
    print(f'  {s!r} idx={idx} -> {t.get(idx)!r}')

# F. Choker / Sticker descriptions
src = open('dump/CodeEntries/gml_GlobalScript_scrAnyaItems.gml', encoding='utf-8').read()
for name in ['Choker', 'Sticker', 'Book', 'Plunger', 'Meat']:
    m = re.search(r'function Anya\w*\(\) : AnyaItem\(\) constructor\s*\{(.*?)\n\}', src)
for nm in ['Choker', 'Sticker']:
    m = re.search(rf'self\.name = "{nm}";\s*\n\s*self\.description = "([^"]+)"', src)
    print(f'===== {nm}: {m.group(1) if m else "?"}')

# I. monsterMaker Other_10 context
src = open('dump/CodeEntries/gml_Object_monsterMaker_Other_10.gml', encoding='utf-8').read()
print('===== monsterMaker_Other_10:')
print(src[:800])
