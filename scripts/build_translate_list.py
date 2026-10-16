# Build the authoritative translate list.
#
# Rationale: the string table holds every literal in the game, including debug text
# from bundled libraries (GifHx, GMLive, ...). We attribute literals to their source
# code file by comparing each code entry's decompiled text to the string table, then
# drop everything whose only owner is a non-player-facing library script.
import json, os, re, sys, io, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
W = r"D:\Steam\steamapps\common\Dead Estate\_loc_work"
CODE = os.path.join(W, "dump", "CodeEntries")
DUMP = os.path.join(W, "dump")

# Suffixes / names that are engine or third-party library code, never player-facing.
LIB_PATTERNS = [
    re.compile(r'gif_std_', re.I), re.compile(r'GifHx', re.I), re.compile(r'^mt_', re.I),
    re.compile(r'haxe_', re.I), re.compile(r'GMLive', re.I),
    re.compile(r'^gml_GlobalScript_Gif', re.I),
    re.compile(r'DevTool', re.I), re.compile(r'devTool', re.I),
    re.compile(r'Debug', re.I), re.compile(r'scrDebug', re.I),
    re.compile(r'achievementTester', re.I), re.compile(r'controllerTest', re.I),
    re.compile(r'Obj_Steam', re.I), re.compile(r'oPSN', re.I), re.compile(r'PSN', re.I),
    re.compile(r'SpriteLoader', re.I), re.compile(r'oSaveDesync', re.I),
    re.compile(r'switchDevTool', re.I), re.compile(r'gamepad', re.I),
    re.compile(r'^gml_Object_Obj_', re.I), re.compile(r'Element', re.I),
]

def owner_is_library(fname):
    stem = fname[:-4] if fname.endswith('.gml') else fname
    body = stem
    for p in LIB_PATTERNS:
        if p.search(body):
            return True
    return False

# ---- load string table ----
S = json.load(open(os.path.join(DUMP, "strings_indexed.json"), encoding="utf-8"))["Strings"]
print("total strings:", len(S))

# ---- load translatable candidates ----
units = json.load(open(os.path.join(DUMP, "units.json"), encoding="utf-8"))
unit_idx = {u["idx"]: u["t"] for u in units}
print("prose candidates:", len(unit_idx))

# ---- scan every code file for quoted literals, recording who owns each ----
lit_owners = collections.defaultdict(set)   # literal text -> set of file stems
lib_stems = set()
game_stems = set()
files = [f for f in os.listdir(CODE) if f.endswith('.gml')]
for f in files:
    stem = f[:-4]
    if owner_is_library(f):
        lib_stems.add(stem)
    else:
        game_stems.add(stem)
print("code files:", len(files), " library-ish:", len(lib_stems), " game:", len(game_stems))

# Use the raw string table entries as the literal universe; attribute by searching the
# decompiled text. That is exact because a literal appears verbatim in its source.
text_cache = {}
for f in files:
    stem = f[:-4]
    with open(os.path.join(CODE, f), encoding="utf-8", errors="replace") as fh:
        text_cache[stem] = fh.read()

# For speed, index only candidate literals (the ~4.8k prose strings).
for idx, t in unit_idx.items():
    # candidate forms: raw, and with \n turned into real newlines, and escaped quotes
    forms = {t, t.replace("\\n", "\n"), t.replace('\\"', '"')}
    for stem in list(game_stems) + list(lib_stems):
        body = text_cache[stem]
        for form in forms:
            if form and form in body:
                lit_owners[idx].add(stem)
                break

only_lib = set()
has_game = set()
unattributed = set()
for idx in unit_idx:
    owners = lit_owners.get(idx, set())
    g = owners & game_stems
    l = owners & lib_stems
    if g:
        has_game.add(idx)
    elif l:
        only_lib.add(idx)
    else:
        unattributed.add(idx)

print()
print("attributed to game code     :", len(has_game))
print("attributed ONLY to library  :", len(only_lib))
print("not found in any code file  :", len(unattributed))

# Keep: game code, plus unattributed-but-plausible (they may live in rooms/objects with
# code names we did not export, or contain characters the decompiler escaped).
def looks_like_debug(t):
    return bool(re.search(r'\b(LZW|Excepted|introducer|constructor|discarded at index|assert|stack trace)\b', t, re.I))

keep = [i for i in unit_idx if i in has_game]
keep += [i for i in unattributed if not looks_like_debug(unit_idx[i])]
keep = sorted(set(keep))
dropped = sorted(set(unit_idx) - set(keep))

print("FINAL translate list:", len(keep), " dropped:", len(dropped))
json.dump(keep, open(os.path.join(DUMP, "translate_indices.json"), "w"), indent=0)
json.dump(dropped, open(os.path.join(DUMP, "dropped_indices.json"), "w"), indent=0)

# show what got dropped
print()
print("=== dropped samples ===")
for i in dropped[:25]:
    print(f"  [{i}] {unit_idx[i][:90]!r}")
