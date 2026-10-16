# -*- coding: utf-8 -*-
# v3e: apply difficulty revert + missed-translation batch.
# All entries keyed by EXPECTED PRISTINE TEXT; indices resolved via rev map with
# strict assertions, so any index drift fails loudly instead of corrupting STRG.
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

p = json.load(open('dump/pristine_strings.json', encoding='utf-8'))
t = json.load(open('dump/translations.json', encoding='utf-8'))
rev = {}
for k, v in p.items():
    rev.setdefault(v, []).append(k)

errors = []
def idx_of(text, current=None):
    """Resolve unique string index for pristine text; optionally require current translation state."""
    ix = rev.get(text, [])
    if len(ix) != 1:
        errors.append(f'index resolve failed for {text!r}: {ix}')
        return None
    i = ix[0]
    if current is not None and t.get(i) != current:
        errors.append(f'current-state mismatch for {text!r} [{i}]: {t.get(i)!r} != {current!r}')
    return i

# ---------------- 1. difficulty revert ----------------
DELETE = {
    'TOO YOUNG TO DIE': '年少轻狂',
    'GAME JOURNO': '游戏记者',
    'X MUST DIE': 'X必须死',
}
DIFF_DESC = {
    '♦b♦3Too Young to Die♦r♦/♦2♦iSmaller floors, more red pots and money, Chunks appears later and moves slower.':
        ('♦b♦3年少轻狂♦r♦/♦2♦i楼层更小，红陶罐和钱更多，查克斯出现得更晚、移动更慢。',
         '♦b♦3Too Young to Die♦r♦/♦2♦i楼层更小，红陶罐和钱更多，查克斯出现得更晚、移动更慢。'),
    "♦b♦2Normal♦r♦/♦8Dead Estate's standard difficulty.":
        ('♦b♦2普通♦r♦/♦8《死亡庄园》的标准难度。',
         '♦b♦2Normal♦r♦/♦8《死亡庄园》的标准难度。'),
    '♦b♦2Painful♦r♦/♦0♦iFaster enemies; larger floors; less money; Chunks appears sooner, moves faster, and mutates on death.':
        ('♦b♦2痛苦♦r♦/♦0♦i敌人更快；楼层更大；钱更少；查克斯出现得更早、移动更快，并且死亡时会变异。',
         '♦b♦2Painful♦r♦/♦0♦i敌人更快；楼层更大；钱更少；查克斯出现得更早、移动更快，并且死亡时会变异。'),
    '♦b♦1Nightmare♦r♦/♦0♦iFewer red pots, buffed enemies, more floor effects, item and weapon rooms are hidden, Chunks has more health.':
        ('♦b♦1梦魇♦r♦/♦0♦i红陶罐更少，敌人被强化，楼层效果更多，道具房和武器房被隐藏，查克斯生命值更高。',
         '♦b♦1Nightmare♦r♦/♦0♦i红陶罐更少，敌人被强化，楼层效果更多，道具房和武器房被隐藏，查克斯生命值更高。'),
    '♦b♦s♦0X Must Die♦r♦/♦0♦iEven less money, even fewer red pots, Chunks appears much sooner and spawns with even more health, and your map is hidden.':
        ('♦b♦s♦0X必须死♦r♦/♦0♦i钱更少，红陶罐更少，查克斯出现得早得多、生成时生命值更高，并且你的地图被隐藏。',
         '♦b♦s♦0X Must Die♦r♦/♦0♦i钱更少，红陶罐更少，查克斯出现得早得多、生成时生命值更高，并且你的地图被隐藏。'),
}

# ---------------- 2. edits to EXISTING translations (fragment recomposition) ----------------
# pristine text -> (expected current, new value)
EDITS = {
    ' at once.': (' 同时发射。', '。'),
    ' in opposite directions.': (' 朝相反方向飞出。', '，一前一后。'),
    ' of shotgun shells.': (' 发霰弹。', '。'),
    ' jabs!': (' 连刺！', '刺拳！'),
    ' swings!': (' 挥舞！', '挥击！'),
    ' if you attack on beat.': (' 如果你踩点攻击的话。', '，前提是踩点攻击。'),
    '. Enemies killed with ': ('。被其杀死的敌人', '。被'),
    'Causes some pots to ': ('使某些陶罐 ', '某些陶罐被摧毁时会'),
    ' on destruction.': ('被摧毁时。', '。'),
    'the next ': ('下一个 ', '下一'),
    'your next ': ('你的下一个 ', '你的下一'),
}

# ---------------- 3. new translations ----------------
# pristine text -> Chinese  (verified display-only or same-index-safe)
ADD = {
    # --- main menu / pause / game over ---
    'Continue': '继续',
    'Play': '开始游戏',
    'Challenges': '挑战',
    'Settings': '设置',
    'Quit': '退出',
    'PAUSED': '已暂停',
    'COWARD.': '胆小鬼。',
    'FAILURE.': '失败。',
    'Retry': '再来一次',
    'CLEARED': '已清除',
    'OK': '确定',
    'CURSES': '诅咒',
    # --- extras menu ---
    'Medals': '勋章',
    'Records': '记录',
    'Movies': '影像',
    'Gallery': '画廊',
    'Extras': '附加内容',
    # --- settings menus ---
    'Fullscreen': '全屏',
    'Z-Aiming': 'Z轴瞄准',
    'Rumble': '震动',
    'rumble': '震动',
    ' intensity': '强度',
    ' features.': '功能的强度。',
    'Use gamepad': '使用手柄',
    'Gamepad aim assist': '手柄瞄准辅助',
    'Toggles aiming assistance for gamepads on and off.': '开启或关闭手柄的瞄准辅助。',
    'Gamepad aim speed': '手柄瞄准速度',
    'Adjusts the speed that your crosshair moves with a gamepad.': '调整手柄准星的移动速度。',
    'Thumbstick deadzones': '摇杆死区',
    "Adjusts the sensitivity of a gamepad's thumbsticks.": '调整手柄摇杆的灵敏度。',
    'Rumble intensity': '震动强度',
    "Adjusts the intensity of the gamepad's rumble features.": '调整手柄震动功能的强度。',
    # --- HUD / text effects / timers ---
    'HEALTH': '生命',
    'WEAPON': '武器',
    'MAP': '地图',
    'MONEY': '金币',
    'HEALED': '已治疗',
    'SHIELDED': '获得护盾',
    'HURRY': '快！',
    'BADASS': '帅呆了',
    'WIN': '稳了',
    'NICE': '漂亮',
    'RIP': '安息吧',
    'FLOOR ': '楼层 ',
    'COSTUME ': '皮肤 ',
    'LABORATORY': '实验室',
    # --- save desync menu ---
    'Load local file, update cloud file': '载入本地文件，更新云端文件',
    'Load cloud file, update local file': '载入云端文件，更新本地文件',
    'Save files desynced': '存档文件不一致',
    # --- floor generation text ---
    'Building': '正在建造',
    'Generating': '正在生成',
    'Assembling': '正在装配',
    'Constructing': '正在构筑',
    'the ': '这一',
    'next ': '下一',
    'level': '楼层',
    'floor': '楼层',
    'Loading': '载入中',
    'Loading...': '载入中……',
    # --- witch shop stats ---
    'Health': '生命',
    'Agility': '敏捷',
    'Strength': '力量',
    # --- Anya: items ---
    'Book': '书本',
    'Plunger': '马桶搋',
    'Meat': '肉',
    'Choker': '颈链',
    'Sticker': '贴纸',
    # --- Anya: options / UI ---
    'Cancel': '取消',
    'Use': '使用',
    'Discard': '丢弃',
    'Examine': '查看',
    'Take': '拿取',
    'Inspect': '细看',
    'INVENTORY': '物品栏',
    'SAVE': '保存',
    'BACK': '返回',
    'Resume': '继续',
    'CONTINUE': '继续',
    'QUIT': '退出',
    'EXIT': '离开',
    'HEALTHY': '健康',
    'MODERATE': '一般',
    'INJURED': '受伤',
    # --- Anya: areas ---
    'Ballroom': '舞厅',
    'Bathroom': '浴室',
    'Cemetery': '墓园',
    'Courtyard': '庭院',
    'Greenhouse': '温室',
    'Kitchen': '厨房',
    'Library': '图书馆',
    'Study': '书房',
    'Wardrobe': '衣帽间',
    'Slaughterhouse': '屠宰场',
    'BALLROOM': '舞厅',
    # --- Anya: painting puzzle ---
    'Moon': '月亮',
    'Bat': '蝙蝠',
    'Apple': '苹果',
    'Grapes': '葡萄',
    'Chalice': '圣杯',
    'Ankh': '安卡',
    'Place ': '贴上',
    ' sticker': '贴纸',
    'That ': '那个',
    'Insert ': '插入',
    'Inserted ': '已将',
    'Took ': '拿起了',
    'Placed ': '把',
    'Used ': '用掉了',
    'GOT ': '获得',
    # --- Anya: Digby pickups (same-index string_pos, safe) ---
    'BACKPACK': '背包',
    'BALLCAP': '球帽',
    # --- challenges ---
    'Blackout': '灯火全灭',
    'Hemophiliac': '血友病',
    'Mutants': '突变体',
    'Uselessness': '一无是处',
    'Ununundead': '不不不死族',
    '-Preface-': '-序言-',
    # --- item names ---
    'Lighter': '打火机',
    'Eyedrops': '眼药水',
    'Taser': '电击枪',
    'Bonker': '大棒槌',
    'Gunpowder': '火药',
    'Polisher': '抛光剂',
    'Heartworm': '心丝虫',
    'Gemini': '双子座',
    'Sledgehammer': '大锤',
    'Bait': '诱饵',
    'Stockpile': '囤货',
    'Medkit': '医疗包',
    'Ambrosia': '仙馔',
    'Paycheck': '工资单',
    'Coupon': '优惠券',
    'Roids': '类固醇',
    'Revengeance': '复仇',
    'Backup': '后援',
    'Scope': '瞄准镜',
    'Snowglobe': '雪花玻璃球',
    'Peapod': '豆荚',
    'Mitosis': '细胞分裂',
    'Arrow': '箭矢',
    'Tragedy': '悲剧',
    'Comedy': '喜剧',
    'Bandolier': '子弹带',
    'Slime': '史莱姆',
    'Darts': '飞镖',
    'Breezepods': '清风豆',
    'Witch-B-Gone': '女巫克星',
    'BTGO': '买三赠一',
    'Duplicator': '复制器',
    'Compass': '罗盘',
    'Dumbbell': '哑铃',
    'Bloodthirst': '嗜血',
    'Holster': '枪套',
    'Buzzy': '嗡嗡',
    'X-Ray': 'X光',
    'Flashbangs': '闪光弹',
    'Mutagen': '诱变剂',
    '♦s♦werror': '♦s♦w错误',
    'Globe': '地球仪',
    'IED': '土制炸弹',
    'Au': '金',
    'Eggy': '蛋蛋',
    'Handsaw': '手锯',
    'Heatseeker': '热传播',
    'Dummy': '假人',
    'Combustophile': '爆炸狂',
    'Hourglass': '沙漏',
    'Stethoscope': '听诊器',
    'Flies': '苍蝇',
    'Lead': '铅',
    'Mosquito': '蚊子',
    'Hellfire': '地狱火',
    'Blindfold': '眼罩',
    'Nail': '钉子',
    'Balloon': '气球',
    'Detonator': '起爆器',
    'Sulfur': '硫磺',
    'Horseshoe': '马蹄铁',
    'Aporia': '阿波里亚',
    'Calendar': '日历',
    # --- item quotes ---
    'Lame.': '逊爆了。',
    'Boom.': '轰。',
    'Cool.': '酷。',
    'Gross.': '恶心。',
    'Ew.': '咦。',
    'Cute.': '可爱。',
    'Bopeebosomething.': '啵噼啵什么来着。',
    'Eugh.': '呕。',
    'Fwoosh.': '咻。',
    'Heheh.': '嘿嘿。',
    'Hehe': '嘿嘿',
    'Maggots.': '蛆虫。',
    '...Creepy.': '……真瘆人。',
    'Icky...': '黏糊糊……',
    'Poop.': '便便。',
    'Ominous.': '不祥。',
    'Gross...': '好恶心……',
    'Rotten.': '烂透了。',
    # --- weapon names ---
    'Handgun': '手枪',
    'Magnum': '麦格农',
    'SMG': '冲锋枪',
    'Minigun': '转管机枪',
    'Shotgun': '霰弹枪',
    'Auto-Shotgun': '自动霰弹枪',
    'Mini-Shotgun': '迷你霰弹枪',
    'Flamethrower': '火焰喷射器',
    'Bomb': '炸弹',
    'Paddleball': '弹力球拍',
    'Cannon': '加农炮',
    'Axe': '斧头',
    'Hammer': '锤子',
    'Broadsword': '阔剑',
    'Crossbow': '弩',
    'Quacks': '嘎嘎叫',
    'Quacks.': '嘎。',
    'Chainsaw': '电锯',
    'Shuriken': '手里剑',
    'Boomerang': '回旋镖',
    'Bone': '骨头',
    'Trumpet': '小号',
    'Thumbtacks': '图钉',
    'Record': '唱片',
    'Eliminator': '歼灭者',
    'Knife': '小刀',
    'Jetpack': '喷气背包',
    'Volcano': '火山',
    'WHHRRRRRR': '呜噜噜噜噜噜',
    # --- weapon desc fragments ---
    'Fires ': '一次发射',
    'exploding': '会爆炸的',
    ' bullets.': '子弹。',
    'burst': '霰弹',
    ' of ': '，全部是',
    'lasers': '激光',
    'Throw ': '扔出',
    'rapid-fire': '快速',
    'heavy': '沉重',
    'Become ': '化身',
    'Does ': '造成',
    'Radioactive': '放射性',
    'six': '六发',
    ' radioactive': '放射性',
    ' bullets': '子弹',
    'Eheheheh...': '嘿嘿嘿嘿……',
    'Devastating.': '毁灭性的。',
    'Ssssssss.': '嘶嘶嘶嘶嘶。',
    'Long.': '真长。',
    # --- item desc fragments ---
    ' enemies.': '。',
    ' larger': '变大',
    'explosions': '爆炸',
    ' will ': '杀死的敌人会',
    ' which ': '，',
    'A ': '一把',
    'mini-Chunks': '迷你查克斯',
    'Triples': '三倍延长',
    'pinatas': '皮纳塔',
    'radioactive': '带放射性',
    'release': '松开',
    'become ': '变得',
    'explode': '爆炸',
    # --- medals (display names) ---
    'Butler': '管家',
    'Cultist': '邪教徒',
    'Freako': '怪胎',
    'Groundskeeper': '园丁',
    'Director': '导演',
    'Slayer': '屠戮者',
    'Acolyte': '侍僧',
    'Survivor': '幸存者',
    'Scrambled': '乱作一团',
    'Chargeback': '退款',
    'Challenger': '挑战者',
    'Struggler': '挣扎者',
    'Disarmed': '被缴械',
    'Graduation': '毕业',
    'Troublemaker': '捣蛋鬼',
    'Showdown': '决战',
    'Locksmith': '开锁匠',
    'Exterminator': '灭虫人',
    'Speedrunner': '速通者',
    'Die': '去死',
    'Die.': '去死。',
    'Massacre': '大屠杀',
    'Collector': '收藏家',
    'Hoarder': '囤积狂',
    'Klepto': '偷窃狂',
    'Gigaton': '十亿吨级',
    'Lumberjack': '伐木工',
    'Commencement': '毕业典礼',
    'Midas': '点金手',
    'Rich': '大富豪',
    'Rodent': '鼠辈',
    'Vermin': '害兽',
    'Uh-Oh...': '糟了……',
    'Unbound': '脱缰',
    'Cracked': '碎裂',
    'Globetrotter': '环球客',
    'Triumph': '凯旋',
    'Dreamer': '入梦者',
    'Awakening': '觉醒',
    'Goodnight': '晚安',
    # --- music tracks ---
    'Gauntlet': '试炼场',
    'Polaroid': '拍立得',
    'Hellmart': '地狱超市',
    'Heavenmart': '天堂超市',
    'Safety': '安全屋',
    # --- misc dialogue/quotes ---
    'Groovy.': '带感。',
    'Extinguished.': '熄灭了。',
    'Hmm...': '嗯……',
    '...Alright.': '……好吧。',
    'Strange.': '真奇怪。',
    'Mmmm....': '嗯嗯嗯……',
    'Mmmm...': '嗯嗯……',
    'Whatever.': '随便。',
    'Okay.': '好吧。',
    'Owchie.': '哎哟喂。',
    'Stop.': '住手。',
    'Yowch.': '嗷呜。',
    'Ouch.': '哎唷。',
    'Ow.': '嗷。',
    'Worldender': '灭世者',
    'Doggy': '狗狗',
    'Music': '音乐',
    'Programming': '程序',
    'Cast': '出演',
    'Broke...': '破产了……',
    'Mhm.': '嗯哼。',
    'Cheapskate.': '小气鬼。',
    'Hm...': '唔……',
    'Hmph.': '哼。',
    'You...': '你……',
    'Mmm...': '嗯……',
    'Mmm': '嗯',
    'Guilty.': '心虚。',
    '...Heeeelp...': '……救……救命……',
    'Creepy...': '瘆人……',
    'N-n-n-no...': '不-不-不行……',
    'N-no...': '不-不行……',
    'Seeya.': '回头见。',
    'Yup.': '没错。',
    'Leave.': '走吧。',
    'DUMMY': '笨蛋',
    'IDIOT': '白痴',
    'MORON': '蠢货',
}

# optional: add if missing (gamepad input desc)
OPTIONAL_ADD = {
    "Switches between keyboard & mouse and gamepad as the game's input method.":
        '在键盘鼠标与手柄之间切换游戏的输入方式。',
}

# ================= apply =================
n_del = n_edit = n_add = 0
for text, cur in DELETE.items():
    i = idx_of(text, cur)
    if i is not None:
        del t[i]; n_del += 1
for text, (cur, new) in DIFF_DESC.items():
    i = idx_of(text, cur)
    if i is not None:
        t[i] = new; n_edit += 1
for text, (cur, new) in EDITS.items():
    i = idx_of(text, cur)
    if i is not None:
        t[i] = new; n_edit += 1
for text, new in ADD.items():
    i = idx_of(text)
    if i is None:
        continue
    if t.get(i) is not None:
        errors.append(f'ADD target already translated: {text!r} [{i}] = {t[i]!r}')
        continue
    t[i] = new; n_add += 1
for text, new in OPTIONAL_ADD.items():
    i = idx_of(text)
    if i is not None and t.get(i) is None:
        t[i] = new; n_add += 1

if errors:
    print('!!! ABORT — assertion failures:')
    for e in errors:
        print('   ', e)
    sys.exit(1)

json.dump(t, open('dump/translations.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'OK: deleted {n_del}, edited {n_edit}, added {n_add}; total entries now {len(t)}')

# ---- charset delta ----
have = set(open('charset.txt', encoding='utf-8').read())
need = set()
for v in t.values():
    need.update(c for c in v if ord(c) > 127 and c != '♦')
missing = sorted(need - have)
print(f'charset: have {len(have)}, need {len(need)}, missing {len(missing)}: {"".join(missing)}')
if missing:
    with open('charset.txt', 'a', encoding='utf-8') as f:
        f.write(''.join(missing))
    print('charset.txt: appended missing chars')
