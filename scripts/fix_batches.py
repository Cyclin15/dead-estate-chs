# Fill the one missing batch and repair the 24 literal-newline defects.
import json, os, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

W = r"D:\Steam\steamapps\common\Dead Estate\_loc_work"
TB = os.path.join(W, "dump", "tb")
TR = os.path.join(W, "dump", "tr")
NL = "\\n"

def rd(p): return json.load(open(p, encoding="utf-8-sig"))
def wr(p, o): json.dump(o, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---------- 1. batch 126 translations ----------
credit_lines = [
    ("Developed by Milkbar Lads", "由 Milkbar Lads 开发"),
    ("Published by 2 Left Thumbs", "由 2 Left Thumbs 发行"),
    ("Milkbar Lads is...", "Milkbar Lads 成员是……"),
    ("Lead programmer", "主程序"),
    ("Environmental art", "场景美术"),
    ("Weapon art", "武器美术"),
    ("Animation", "动画"),
    ("Lead artist", "主美"),
    ("Boss & enemy art", "Boss 与敌人美术"),
    ("Cutscene art", "过场美术"),
    ("Character select art", "选人界面美术"),
    ("Title art", "标题美术"),
    ("Character designer", "角色设计"),
    ("Credits art", "制作人员名单美术"),
    ("Cordelia shop art", "科迪莉亚商店美术"),
    ("Lead musician", "主音乐"),
    ("Voice acting", "配音"),
    ("Menu art", "菜单美术"),
    ("Cutscene art asst.", "过场美术助理"),
    ("Character select art asst.", "选人界面美术助理"),
    ("Item art", "道具美术"),
    ("Background art", "背景美术"),
    ("Thank you to GRAEME", "感谢 GRAEME"),
    ("from 2 Left Thumbs", "来自 2 Left Thumbs"),
    ("for publishing Dead Estate", "发行了《死亡庄园》"),
    ("and helping us", "并帮助我们"),
    ("make this happen!", "让这一切成真！"),
    ("Voice acting by:", "配音："),
]

src126 = rd(os.path.join(TB, "t_126.json"))
src_map = {u["idx"]: u["t"] for u in src126}

manual = {
 14436: "常驻者",
 14475: "created blackfade",
 14478: "献祭之地",
 14479: "剧终",
 14509: "答对了！",
 14510: "正确答案：",
 14512: "Milkbar Lads\\n\\n在 C:\\Users\\...\\AppData\\Local\\Dead_Estate\\ 下发现外部 .ini 文件\\n\\n",
 14513: "「祝你好运。」",
 14514: "在尸体旁发现了一把刀刃，与先前描述的那把相符，还插在树上。树干上潦草地刻着这样一句话：",
 14515: "XXXXXX 与 XXXXXXXX 两位警员发现了尸体。在搜查现场后，卡特在一棵树上发现了一条刻痕留言",
 14516: "位于 Ridgewood 路旁。他立即呼叫支援，并循着脚印进入树林。15 分钟后，梅尔菲副警长与",
 14517: "根据梅尔菲的报告，他发现两串一模一样的泥泞脚印，从汽车尾部延伸进树林",
 14518: "已被完全击碎。汽车前轮被一把约 3/16 英寸厚的锯齿刀刃割破。据副警长",
 14519: "XXXXXXXXX 路，就在 XXXXXXX 与 Ridgewood 交叉口之前、道路对面远离 XXXXXXXXXXX 的一侧。梅尔菲报告称",
 14520: "他在死前数小时遭到严重殴打。受害者的尸体由 XXXXXX 副警长发现，他找到了托马斯的车，停在",
 14521: "XXXXXXXXX —— 鼻梁骨折，缺失三颗牙齿，脸上有多处巨大的肿胀瘀伤，那鲜艳的红色说明",
 14522: "位于森林深处，距离 XXXXXXXXX 路约 2.5 英里处。受害者被立即确认为 XXXXX XXXX —— 一位 XX 岁的居民",
 14523: "1978 年 6 月 21 日 —— 受害者被发现时被狗链捆绑并遭勒死，弃于一个看似匆忙挖出的浅坑中，位于",
 14535: "我没时间管这个。",
 14536: "我空手就能把这武器掰成两半。",
 14537: "我在做史上最大的煎蛋卷。顾不上每个鸡蛋了。",
 14546: "画面设置",
 14549: "返回暂停菜单",
 14560: "点击游戏窗口内任意位置开始",
 14614: "等一下……",
 14617: "你为啥这么可疑",
 14638: "卡车司机杰夫",
 14639: "+能承受更多伤害\\n-移动稍慢\\n+初始携带手枪",
 14640: "真结局成就：",
 14656: "剧终。",
 14663: "\u2666w用 \u2666r\u2666kinputUp\u2666r \u2666kinputLeft\u2666r \u2666kinputDown\u2666r \u2666kinputRight\u2666r\u2666w 移动。",
 14664: "\u2666w用 \u2666r\u2666kgpLeftStick\u2666r\u2666w 移动。",
 14665: "\u2666w用 \u2666r\u2666kinputFire\u2666r\u2666w 开火。",
 14666: "\u2666w用 \u2666r\u2666kinputFire\u2666r\u2666w 开火，用 \u2666r\u2666kgpRightStick\u2666r\u2666w 瞄准。",
}

# Build 14641 (credits) by translating the known role lines, preserving structure.
cr = src_map[14641]
for en, zh in credit_lines:
    cr = cr.replace(en, zh)
manual[14641] = cr

out126 = []
for u in src126:
    i = u["idx"]
    zh = manual.get(i)
    if zh is None:
        raise SystemExit(f"batch126: no translation for idx {i}: {u['t'][:60]!r}")
    out126.append({"idx": i, "zh": zh})
wr(os.path.join(TR, "r_126.json"), out126)
print(f"batch 126: wrote {len(out126)} entries")

# ---------- 2. repair literal-newline defects ----------
fixed_entries = 0
fixed_files = 0
for f in sorted(os.listdir(TR)):
    if not re.match(r"^r_\d{3}\.json$", f):
        continue
    tbn = f.replace("r_", "t_")
    tbp = os.path.join(TB, tbn)
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
        want, have = en.count(NL), zh.count(NL)
        if want == have:
            continue
        # the model emitted real newlines (or CRLF) where the game uses the \n escape
        cand = zh.replace("\r\n", NL).replace("\r", NL).replace("\n", NL)
        if cand.count(NL) == want:
            it["zh"] = cand
            fixed_entries += 1
            changed = True
    if changed:
        wr(path, got)
        fixed_files += 1

print(f"newline repairs: {fixed_entries} entries in {fixed_files} files")
