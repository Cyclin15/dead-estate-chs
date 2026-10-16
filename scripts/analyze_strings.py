# Analyze the Dead Estate data.win string table for localization scope.
import json, re, sys, collections

path = r"D:\Steam\steamapps\common\Dead Estate\_loc_work\dump\strings_indexed.json"
with open(path, encoding="utf-8") as f:
    data = json.load(f)
S = data["Strings"]
print("total string entries:", len(S))

ID_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')          # bare identifier
PATH_RE = re.compile(r'^[A-Za-z0-9_\\/\.\-]+$')           # path-ish / dotted name

def is_identifierish(s):
    if ID_RE.match(s):
        return True
    if PATH_RE.match(s) and len(s) > 0:
        return True
    return False

prose = []          # sentences / display text
ident = []          # identifiers, asset names, code symbols
empty = []
other = []

for i, s in enumerate(S):
    t = s.strip()
    if t == "":
        empty.append(i)
        continue
    if is_identifierish(t):
        ident.append(i)
        continue
    # has spaces or punctuation and a real letter run -> candidate display text
    if re.search(r'[A-Za-z]{2,}', t) and (" " in t or re.search(r'[.,!?\'"\-:;]', t)):
        prose.append(i)
    else:
        other.append(i)

print("empty/whitespace :", len(empty))
print("identifier-ish   :", len(ident))
print("prose candidates :", len(prose))
print("other            :", len(other))

# character-weight of prose candidates
total_chars = sum(len(S[i]) for i in prose)
print("prose total chars:", total_chars)
print("prose avg chars  : %.1f" % (total_chars / max(1, len(prose))))

# length distribution of prose
buckets = collections.Counter()
for i in prose:
    L = len(S[i])
    if L < 20: buckets["<20"] += 1
    elif L < 40: buckets["20-39"] += 1
    elif L < 80: buckets["40-79"] += 1
    elif L < 160: buckets["80-159"] += 1
    elif L < 320: buckets["160-319"] += 1
    else: buckets["320+"] += 1
print("prose length buckets:", dict(buckets))

# how many distinct CJK-unique chars would a translation need? approximate via
# rough English->Chinese ratio of 1 Chinese char per ~1.7 English chars
est_cjk_chars = int(total_chars / 1.7)
print("rough translated size (chars):", est_cjk_chars)
print("rough unique CJK glyphs needed (upper bound ~min(est, 3500)):", min(est_cjk_chars, 3500))

print()
print("=== longest 15 prose strings (dialogue/lore) ===")
for i in sorted(prose, key=lambda x: -len(S[x]))[:15]:
    print(f"[{i}] len={len(S[i])}")
    print("    " + S[i][:400].replace("\n", "\\n"))

print()
print("=== 25 random mid-length prose samples ===")
import random
random.seed(7)
mid = [i for i in prose if 25 <= len(S[i]) <= 90]
for i in random.sample(mid, min(25, len(mid))):
    print(f"  [{i}] {S[i][:150]}")
