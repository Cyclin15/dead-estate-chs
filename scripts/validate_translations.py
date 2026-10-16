# Validate translation outputs: complete JSON, full coverage, markup integrity intact.
import json, os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

W = r"D:\Steam\steamapps\common\Dead Estate\_loc_work"
TB = os.path.join(W, "dump", "tb")
TR = os.path.join(W, "dump", "tr")
DIAMOND = "\u2666"

tb_files = sorted(f for f in os.listdir(TB) if f.endswith(".json"))
tr_files = set(f for f in os.listdir(TR) if f.endswith(".json"))

missing, bad_json, ok_files = [], [], []
all_tr = {}
problems = []
total_src = 0
out_of_range = []

for tf in tb_files:
    rf = tf.replace("t_", "r_")
    src = json.load(open(os.path.join(TB, tf), encoding="utf-8"))
    total_src += len(src)
    if rf not in tr_files:
        missing.append(rf)
        continue
    try:
        got = json.load(open(os.path.join(TR, rf), encoding="utf-8"))
    except Exception as e:
        bad_json.append((rf, str(e)[:80]))
        continue
    if not isinstance(got, list):
        bad_json.append((rf, "not a list"))
        continue
    ok_files.append(rf)
    smap = {u["idx"]: u["t"] for u in src}
    seen = {}
    for it in got:
        if not isinstance(it, dict) or "idx" not in it or "zh" not in it:
            problems.append(f"{rf}: malformed item")
            continue
        k = it["idx"]
        if k not in smap:
            problems.append(f"{rf}: idx {k} not in source")
            continue
        zh = it["zh"] or ""
        en = smap[k]
        if not zh.strip():
            problems.append(f"{rf}: idx {k} empty")
        de = len(re.findall(r"\u2666.", en)); dz = len(re.findall(r"\u2666.", zh))
        if de != dz:
            problems.append(f"{rf}: idx {k} diamond {dz}!={de}")
        ne = en.count("\\n"); nz = zh.count("\\n")
        if ne != nz:
            problems.append(f"{rf}: idx {k} \\n {nz}!={ne}")
        if len(zh) > max(40, len(en) * 2.2):
            out_of_range.append(f"{rf}: idx {k} len {len(zh)} vs en {len(en)}")
        seen[k] = zh
        all_tr[k] = zh
    for k in smap:
        if k not in seen:
            problems.append(f"{rf}: idx {k} MISSING")

print("batch files      :", len(tb_files))
print("result files     :", len(tr_files))
print("valid result files:", len(ok_files))
print("missing results  :", len(missing), missing[:6])
print("bad json         :", len(bad_json), bad_json[:6])
print("source units     :", total_src)
print("translated units :", len(all_tr))
print("coverage         : %.2f%%" % (100.0 * len(all_tr) / total_src))
print("integrity problems:", len(problems))
for p in problems[:25]:
    print("   ", p)
print("suspiciously long translations:", len(out_of_range))
for p in out_of_range[:10]:
    print("   ", p)

json.dump(all_tr, open(os.path.join(W, "dump", "translations.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0, sort_keys=True)
print()
print("merged ->", os.path.join(W, "dump", "translations.json"))
