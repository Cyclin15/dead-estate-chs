# Repair: the model escaped REAL newlines into literal "\n" / "\r\n" sequences.
# The source strings store real newline characters, so convert them back.
import json, os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

W = r"D:\Steam\steamapps\common\Dead Estate\_loc_work"
TB = os.path.join(W, "dump", "tb")
TR = os.path.join(W, "dump", "tr")
LIT_N = "\\n"
LIT_RN = "\\r\\n"

def rd(p): return json.load(open(p, encoding="utf-8-sig"))
def wr(p, o): json.dump(o, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

fixed_entries = 0
fixed_files = []
still_bad = []

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
        want = en.count("\n")            # real newlines expected
        if zh.count("\n") == want and zh.count(LIT_N) == 0:
            continue
        cand = zh
        if LIT_RN in cand or LIT_N in cand:
            # only convert when the source genuinely uses newlines
            if want > 0:
                cand = cand.replace(LIT_RN, "\r\n").replace(LIT_N, "\n")
        if cand.count("\n") == want:
            if cand != zh:
                it["zh"] = cand
                fixed_entries += 1
                changed = True
        else:
            still_bad.append((f, i, en.count("\n"), cand.count("\n")))
    if changed:
        wr(path, got)
        fixed_files.append(f)

print(f"repaired entries: {fixed_entries} in {len(fixed_files)} files")
print("files:", fixed_files)
print("still mismatched:", len(still_bad))
for r in still_bad[:20]:
    print("   ", r)
