# Final normalization + merge.
#
# Discovery: some source strings store the four characters \ r \ n (a literal escape,
# as GameMaker's own \r\n escape) while others store a real newline character. The
# model mirrored whatever it saw, so "%s" patterns are already correct. The only real
# defects are entries whose newline count differs from the source; those get padded or
# trimmed on the escaped form so the engine sees exactly the original break structure.
import json, os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

W = r"D:\Steam\steamapps\common\Dead Estate\_loc_work"
TB = os.path.join(W, "dump", "tb")
TR = os.path.join(W, "dump", "tr")
LIT_RN, LIT_N = "\\r\\n", "\\n"

def rd(p): return json.load(open(p, encoding="utf-8-sig"))
def wr(p, o): json.dump(o, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def breaks(s):
    """Count break tokens, treating a real newline and a literal escape as equivalent."""
    return s.count("\n") + s.count(LIT_RN) + s.count(LIT_N)

fixed, files = 0, []
for f in sorted(os.listdir(TR)):
    if not re.match(r"^r_\d{3}\.json$", f):
        continue
    tbp = os.path.join(TB, f.replace("r_", "t_"))
    if not os.path.exists(tbp):
        continue
    src = {u["idx"]: u["t"] for u in rd(tbp)}
    path = os.path.join(TR, f)
    got = rd(path)
    changed = False
    for it in got:
        i = it["idx"]
        if i not in src:
            continue
        en, zh = src[i], it["zh"]
        want = breaks(en)
        # strip stray spaces the model added inside short quoted terms
        new = re.sub(r"' ([^']{1,24}?) '", r"'\1'", zh)
        if breaks(new) != want:
            # normalize everything to the escaped form the source uses, then fix the count
            n = new.replace("\r\n", LIT_RN).replace("\n", LIT_RN)
            cur = breaks(n)
            if cur < want:
                n = n + LIT_RN * (want - cur)
            elif cur > want:
                for _ in range(cur - want):
                    p = n.rfind(LIT_RN)
                    if p < 0:
                        break
                    n = n[:p] + n[p + len(LIT_RN):]
            new = n
        if new != zh:
            it["zh"] = new
            fixed += 1
            changed = True
    if changed:
        wr(path, got)
        files.append(f)

print(f"normalized entries: {fixed} in {len(files)} files")

# ---- merge every result into the canonical translations map ----
all_tr = {}
for f in sorted(os.listdir(TR)):
    if not re.match(r"^r_\d{3}\.json$", f):
        continue
    for it in rd(os.path.join(TR, f)):
        all_tr[it["idx"]] = it["zh"]

keep = json.load(open(os.path.join(W, "dump", "translate_indices.json"), encoding="utf-8"))
missing = [i for i in keep if i not in all_tr]
print("translate indices:", len(keep), " merged:", len(all_tr), " missing:", len(missing))

json.dump(all_tr, open(os.path.join(W, "dump", "translations.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0, sort_keys=True)

# ---- final integrity report ----
S = rd(os.path.join(W, "dump", "strings_indexed.json"))["Strings"]
bad = []
for i in keep:
    en, zh = S[i], all_tr[i]
    if breaks(en) != breaks(zh):
        bad.append(i)
    if (len(re.findall(r"\u2666.", en))) != (len(re.findall(r"\u2666.", zh))):
        bad.append(("diamond", i))
print("final integrity problems:", len(bad), bad[:10])

chars = set()
for zh in all_tr.values():
    chars.update(zh)
print("distinct characters in translation:", len(chars))
