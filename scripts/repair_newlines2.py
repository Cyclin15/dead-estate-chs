# Definitive newline repair.
#
# Ground truth (verified against the raw string table): the engine stores REAL newline
# bytes (LF, and CRLF inside the long journal/credits entries). No string contains a
# literal backslash escape. Six entries ended up with a literal "\r\n" and collapsed
# line breaks, so they are rewritten to mirror the English break structure exactly.
import json, os, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

W = r"D:\Steam\steamapps\common\Dead Estate\_loc_work"
TR = os.path.join(W, "dump", "tr")
def rd(p): return json.load(open(p, encoding="utf-8-sig"))
def wr(p, o): json.dump(o, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

S = rd(os.path.join(W, "dump", "strings_indexed.json"))["Strings"]

# Hand-aligned rewrites: same line-break count as the English source.
REWRITE = {
    14560: "点击游戏窗口内\n任意位置开始",
    13191: "发行《死亡庄园》\n",
    13192: "并帮助我们\n",
    14934: "至于那项实验，\r\n过去几十年里，我一直潜心研究\r\n跨维度旅行。\r\n\r\n我相信你早就知道了。",
    14935: ("我最近一年的研究\r\n收获尤其丰硕。\r\n你在房子里见过那些生物\r\n了吧？\r\n它们来自一个我最近才建立起\r\n联系的维度。\r\n\r\n一个被我命名为「3X1T」的领域。\r\n\r\n别问为什么。"),
    14943: ("又及。\r\n罗塞莉亚，请别忘了喂查克斯。\r\n\r\n科迪莉亚，求你了——看在上帝的份上——千万\r\n别从大学退学。\r\n\r\n兰伯特，无论你身在世界的何处，\r\n永远不要放弃对知识的追求。\r\n"),
}
# 14935 needs exactly 9 breaks; verify/pad below.
REWRITE[14935] = "我最近一年的研究\r\n收获尤其丰硕。\r\n你在房子里见过那些生物了吧？\r\n它们来自一个我最近才建立\r\n起联系的维度。\r\n\r\n一个被我命名为「3X1T」的领域。\r\n\r\n别问为什么。\r\n"

def breaks(s): return s.count("\n")

for f in sorted(os.listdir(TR)):
    if not re.match(r"^r_\d{3}\.json$", f):
        continue
    path = os.path.join(TR, f)
    got = rd(path)
    changed = False
    for it in got:
        i = it["idx"]
        zh = it["zh"]
        new = re.sub(r"' ([^']{1,24}?) '", r"'\1'", zh)
        if i in REWRITE:
            new = REWRITE[i]
        if new != zh:
            it["zh"] = new
            changed = True
    if changed:
        wr(path, got)

# merge + report
all_tr = {}
for f in sorted(os.listdir(TR)):
    if re.match(r"^r_\d{3}\.json$", f):
        for it in rd(os.path.join(TR, f)):
            all_tr[it["idx"]] = it["zh"]

keep = json.load(open(os.path.join(W, "dump", "translate_indices.json"), encoding="utf-8"))
bad = []
for i in keep:
    en, zh = S[i], all_tr[i]
    if breaks(en) != breaks(zh):
        bad.append(("nl", i, breaks(en), breaks(zh)))
    if len(re.findall(r"\u2666.", en)) != len(re.findall(r"\u2666.", zh)):
        bad.append(("diamond", i))
    if zh.count("\\r\\n") or zh.count("\\n"):
        bad.append(("literal-escape", i))

print("entries:", len(keep), " problems:", len(bad))
for b in bad[:20]:
    print("   ", b)

json.dump(all_tr, open(os.path.join(W, "dump", "translations.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=0, sort_keys=True)
print("merged translations.json written")
