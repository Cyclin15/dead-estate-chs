# v3 font build: compose two NEW regular fonts (fntAnyaFancyCN / fntAnyaTypewriterCN)
# that replace the runtime font_add_sprite_ext fonts (extended charmap = freeze).
#
# Per font:
#   - Latin glyphs: byte-exact crops of the original sprite frames
#     (dump/spritefonts/<spr>/pageN.png via dump/spritefonts_info.txt), placed in a
#     cellH-tall quad at their original tgt offset. Shift = frameW + 1 (prop bbox + sep),
#     Offset = tgtX.
#   - CJK glyphs: tight ink from spritefonts2/<spr>/sheet0.png pasted at ty in a
#     cellH-tall quad, Offset = 0/1, Shift = fixed advance.
# Metric model (same as the 34 proven fontfinal2 fonts): uniform quad height,
# quad top-left = (pen_x + Offset, pen_y), ink bottom = baseline row.
# Output: out/v3fonts/<name>/{sheet0.png, glyphs.csv}  (BuildV2 CSV format).
import os, sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image

W = r"D:\Steam\steamapps\common\Dead Estate\_loc_work"
OUT = os.path.join(W, "out", "v3fonts")
PAD = 2
MAXW = 4096

# sprite -> (new font name, charmap string index, cellH, cjk shift, cjk offset)
FONTS = {
    "sprAnyaFancyFont":     ("fntAnyaFancyCN",     7999, 16, 16, 1),
    "sprAnyaTypewriterFont":("fntAnyaTypewriterCN",8001,  9, 11, 0),
}

# ---- parse sprite frame info
info = {}
for line in open(os.path.join(W, "dump", "spritefonts_info.txt"), encoding="utf-8"):
    m = re.match(r"FRAME\s+(\S+)\s+(\d+)\s+localpage=(\d+)\s+tpi=(\d+)\s+src=\((\d+),(\d+)\)\s+(\d+)x(\d+)\s+tgt=\((\d+),(\d+)\)\s+(\d+)x(\d+)", line)
    if m:
        spr, fi, lp = m.group(1), int(m.group(2)), int(m.group(3))
        info.setdefault(spr, []).append(dict(
            lp=lp, sx=int(m.group(5)), sy=int(m.group(6)), sw=int(m.group(7)), sh=int(m.group(8)),
            tx=int(m.group(9)), ty=int(m.group(10))))

# ---- charmaps from original strings
sj = json.load(open(os.path.join(W, "dump", "strings_indexed.json"), encoding="utf-8"))
strings = sj["Strings"]
def str_at(idx):
    return strings[idx]

import struct
for spr, (name, mapIdx, cellH, cjkShift, cjkOff) in FONTS.items():
    charmap = str_at(mapIdx)
    frames = info[spr]
    assert len(frames) == len(charmap), f"{spr}: {len(frames)} frames vs charmap {len(charmap)}"
    pages = {n: Image.open(os.path.join(W, "dump", "spritefonts", spr, f"page{n}.png")).convert("RGBA")
             for n in sorted({f["lp"] for f in frames})}

    glyphs = []  # (charcode, img(quad), shift, offset)

    # Latin
    for i, ch in enumerate(charmap):
        f = frames[i]
        crop = pages[f["lp"]].crop((f["sx"], f["sy"], f["sx"] + f["sw"], f["sy"] + f["sh"]))
        qw = f["tx"] + f["sw"]
        quad = Image.new("RGBA", (qw, cellH), (0, 0, 0, 0))
        quad.paste(crop, (f["tx"], f["ty"]))
        if crop.getextrema()[3][1] == 0:  # fully transparent frame (space etc.)
            shift = cellH // 3 + 1        # sensible space width
        else:
            shift = f["sw"] + 1           # prop bbox width + sep
        glyphs.append((ord(ch), quad, shift, f["tx"]))

    # CJK — frame rects come from the spritefonts2 manifest (frames[origFrames:] are
    # the CJK additions, in charset order). sheet0.png is proper RGBA (transparent bg),
    # so no ink recovery needed. Glyphs are bottom-aligned in the cell (ty = cellH - h).
    mf = json.load(open(os.path.join(W, "spritefonts2", spr, "manifest.json"), encoding="utf-8"))
    sheet = Image.open(os.path.join(W, "spritefonts2", spr, "sheet0.png")).convert("RGBA")
    assert mf["missing"] == [], f"{spr}: manifest reports missing CJK chars"
    ncjk = 0
    for fr in mf["frames"][mf["origFrames"]:]:
        ch, x, y, w, h = fr["char"], fr["x"], fr["y"], fr["w"], fr["h"]
        crop = sheet.crop((x, y, x + w, y + h))
        ty = cellH - h
        quad = Image.new("RGBA", (max(w + cjkOff, 1), cellH), (0, 0, 0, 0))
        quad.paste(crop, (cjkOff, ty), crop)
        glyphs.append((ord(ch), quad, cjkShift, cjkOff))
        ncjk += 1

    # dedupe (CJK charset may overlap nothing in Latin, but be safe)
    seen = {}
    for g in glyphs:
        seen[g[0]] = g
    glyphs = [seen[c] for c in sorted(seen)]

    # ---- shelf pack
    x = y = rh = 0
    placed = []
    for code, quad, shift, off in glyphs:
        w, h = quad.size
        if x + w + PAD > MAXW:
            x = 0; y += rh + PAD; rh = 0
        placed.append((code, x, y, w, h, shift, off, quad))
        x += w + PAD
        rh = max(rh, h)
    sheetW = 4096
    sheetH = y + rh + PAD
    def pot(v):
        p = 1
        while p < v: p <<= 1
        return p
    sheetH = pot(sheetH)
    out = Image.new("RGBA", (sheetW, sheetH), (0, 0, 0, 0))
    for code, px, py, w, h, shift, off, quad in placed:
        assert px + w <= sheetW
        out.paste(quad, (px, py))

    d = os.path.join(OUT, name)
    os.makedirs(d, exist_ok=True)
    out.save(os.path.join(d, "sheet0.png"))
    with open(os.path.join(d, "glyphs.csv"), "w", encoding="utf-8", newline="") as fh:
        fh.write(f"{name};{cellH};False;False;0;1;1;1\n")
        for code, px, py, w, h, shift, off, quad in placed:
            fh.write(f"{code};{px};{py};{w};{h};{shift};{off}\n")
    lat_n = sum(1 for g in glyphs if g[0] < 128)
    print(f"{name}: {len(glyphs)} glyphs ({lat_n} latin + {ncjk} cjk), cell {cellH}, sheet {sheetW}x{sheetH}")
print("done")
