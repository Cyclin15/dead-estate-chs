# Refined localization-scope analysis for Dead Estate data.win.
import json, re, collections, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

path = r"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\strings_indexed.json"
with open(path, encoding="utf-8") as f:
    S = json.load(f)["Strings"]
print("total string entries:", len(S))

SHADER = re.compile(r'#version|gl_FragColor|uniform sampler2D|void main\s*\(', re.I)
IDENT  = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
PATHP  = re.compile(r'^[A-Za-z0-9_\\/\.\-]+$')

prose, ident, shader, other, empty = [], [], [], [], []
for i, s in enumerate(S):
    t = s.strip()
    if not t:
        empty.append(i); continue
    if SHADER.search(t):
        shader.append(i); continue
    if IDENT.match(t) or PATHP.match(t):
        ident.append(i); continue
    if re.search(r'[A-Za-z]{2,}', t) and (" " in t or re.search(r"[.,!?'\"\-:;]", t)):
        prose.append(i)
    else:
        other.append(i)

print("empty            :", len(empty))
print("shader source    :", len(shader))
print("identifier-ish   :", len(ident))
print("prose candidates :", len(prose))
print("other            :", len(other))

chars = sum(len(S[i]) for i in prose)
print("prose chars      :", chars)
print("prose words      :", sum(len(S[i].split()) for i in prose))

# Exclude the credits blobs (>1500 chars) to see in-game wording volume
big = [i for i in prose if len(S[i]) > 1500]
small = [i for i in prose if len(S[i]) <= 1500]
print()
print("credits/large blobs (>1500 chars):", len(big), "chars:", sum(len(S[i]) for i in big))
print("in-game strings (<=1500 chars)  :", len(small), "chars:", sum(len(S[i]) for i in small))
print("  -> words:", sum(len(S[i].split()) for i in small))

b = collections.Counter()
for i in small:
    L = len(S[i])
    k = "<20" if L < 20 else "20-39" if L < 40 else "40-79" if L < 80 else "80-199" if L < 200 else "200+"
    b[k] += 1
print("in-game length buckets:", dict(b))

# Unique Latin letters + punctuation actually used (for subsetting a CJK font)
used = set()
for i in prose:
    used.update(S[i])
print()
print("distinct characters used across prose:", len(used))
nonascii = sorted(c for c in used if ord(c) > 127)
print("non-ASCII chars used:", "".join(nonascii)[:200])
print("their codepoints:", " ".join(f"U+{ord(c):04X}" for c in nonascii[:60]))

print()
print("=== 30 in-game prose samples (item/UI/dialogue flavour) ===")
import random
random.seed(11)
pool = [i for i in small if 20 <= len(S[i]) <= 120]
for i in random.sample(pool, min(30, len(pool))):
    print(f"  [{i}] {S[i][:160]}")
