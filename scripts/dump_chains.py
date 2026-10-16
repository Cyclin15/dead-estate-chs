# Dump concat() chains (weapons/items) with per-fragment translation status.
import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

p = json.load(open('dump/pristine_strings.json', encoding='utf-8'))
t = json.load(open('dump/translations.json', encoding='utf-8'))
rev = {}
for k, v in p.items():
    rev.setdefault(v, []).append(k)

Q = re.compile(r'"((?:[^"\\]|\\.)*)"')

for f in ['dump/CodeEntries/gml_GlobalScript_scrWeapons.gml',
          'dump/CodeEntries/gml_GlobalScript_scrItems.gml']:
    print('=' * 20, f.split('/')[-1])
    for line in open(f, encoding='utf-8'):
        if 'concat(' not in line:
            continue
        m = re.search(r'concat\((.*)\);', line)
        if not m:
            continue
        parts = Q.findall(m.group(1))
        idxs = [rev.get(s, ['?']) for s in parts]
        if any(any(i not in t for i in ix) for ix in idxs):
            out = []
            for s, ix in zip(parts, idxs):
                miss = any(i not in t for i in ix)
                if miss:
                    out.append(f'[MISS {ix[0]}]{s!r}')
                else:
                    out.append(f'[ok]{s!r}={t.get(ix[0], "")!r}')
            print('  ' + ' '.join(out))
