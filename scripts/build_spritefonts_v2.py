# Compose extended sprite-font frame sheets: original Latin frames (byte-identical crops)
# followed by CJK frames (fusion pixel font, ink tight at top-left like the originals).
# Output: per sprite a PNG sheet + manifest (frames) + new charmap string file.
import os, sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

W = r"D:\Steam\steamapps\common\Dead Estate\_loc_work"
OUT = os.path.join(W, "spritefonts2")
os.makedirs(OUT, exist_ok=True)

FUSION = {
    8:  os.path.join(W, "pixelfonts", "f8",  "fusion-pixel-8px-proportional-zh_hans.ttf"),
    10: os.path.join(W, "pixelfonts", "f10", "fusion-pixel-10px-proportional-zh_hans.ttf"),
    12: os.path.join(W, "pixelfonts", "f12", "fusion-pixel-12px-proportional-zh_hans.ttf"),
}
# sprite -> (render px, base font px)
SPRITES = {
    "sprAnyaTypewriterFont": (10, 10),   # caps are 9 rows; fusion-10 ink is 10x9
    "sprAnyaFancyFont":      (16, 8),    # caps 16 rows; fusion-8 at 16px = 16x14 (2x)
    "sprAnyaReviewFont":     (8, 8),     # caps 6 rows; fusion-8 ink is 8x7 (1 row taller)
}
CHARMAP_IDX = {
    "sprAnyaTypewriterFont": 8001,
    "sprAnyaFancyFont": 7999,
    "sprAnyaReviewFont": 10807,
}

chars = open(os.path.join(W, "charset.txt"), encoding="utf-8").read()
cset = [c for c in dict.fromkeys(c for c in chars if ord(c) > 127)]  # ♦ included: unprocessed effect codes get drawn

# original frame geometry from the dump log
info = open(os.path.join(W, "dump", "spritefonts_info.txt"), encoding="utf-8").read().splitlines()
orig_frames = {}
for l in info:
    p = l.split("\t")
    if p[0] == "FRAME":
        name = p[1]; i = int(p[2]); lp = int(p[3].split("=")[1])
        m = re.search(r"src=\((\d+),(\d+)\)\t(\d+)x(\d+)", l)
        x, y, w, h = map(int, m.groups())
        orig_frames.setdefault(name, []).append((i, lp, x, y, w, h))
# original charmap strings (must match frame order)
orig_charmaps = {}
for l in info:
    p = l.split("\t")
    if p[0] == "CHARMAP":
        idx = int(p[1].strip("[]")); ln = int(p[2].split("=")[1])
        orig_charmaps[idx] = ln
# fetch actual string content from the indexed strings dump (original English data)
_raw = open(os.path.join(W, "dump", "strings_indexed.json"), encoding="utf-8").read()
_raw = re.sub(r",\s*([\]}])", r"\1", _raw)
strings = json.loads(_raw)["Strings"]

manifest = {}
for name, (px, base) in SPRITES.items():
    fs = sorted(orig_frames[name])
    imgs = {}
    for i, lp, x, y, w, h in fs:
        if lp not in imgs:
            imgs[lp] = Image.open(os.path.join(W, "dump", "spritefonts", name, f"page{lp}.png")).convert("RGBA")
    cm_idx = CHARMAP_IDX[name]
    cm = strings[cm_idx]
    assert len(cm) == len(fs), f"{name}: charmap len {len(cm)} vs frames {len(fs)}"
    font = ImageFont.truetype(FUSION[base], px)
    cmap = TTFont(FUSION[base]).getBestCmap()
    font12 = ImageFont.truetype(FUSION[12], px)
    cmap12 = TTFont(FUSION[12]).getBestCmap()

    frames = []  # (char, PIL image)
    for i, lp, x, y, w, h in fs:
        frames.append((cm[i], imgs[lp].crop((x, y, x + w, y + h))))
    missing = []
    for ch in cset:
        f, in_map = font, ord(ch) in cmap
        if not in_map:
            if ord(ch) in cmap12:
                f = font12
            else:
                missing.append(ch); continue
        im = Image.new("L", (px * 3, px * 3), 0)
        ImageDraw.Draw(im).text((px, px), ch, font=f, fill=255)
        im = im.point(lambda v: 255 if v >= 128 else 0)
        bb = im.getbbox()
        if bb is None:
            continue
        frames.append((ch, im.crop(bb).convert("RGBA")))

    # shelf-pack all frames on one 2048-wide sheet
    maxH = max(f.size[1] for _, f in frames)
    xs, ys, rowH = 0, 0, maxH
    placed = []
    for ch, f in frames:
        if xs + f.size[0] > 2048:
            xs = 0; ys += rowH
        placed.append((ch, xs, ys, f.size[0], f.size[1], f))
        xs += f.size[0] + 1
    sheet_h = ys + rowH
    def pot(v):
        p = 1
        while p < v: p *= 2
        return p
    sheet = Image.new("RGBA", (2048, pot(max(1, sheet_h))), (0, 0, 0, 0))
    out_frames = []
    for ch, x, y, w, h, f in placed:
        sheet.paste(f, (x, y))
        out_frames.append({"char": ch, "x": x, "y": y, "w": w, "h": h})
    d = os.path.join(OUT, name)
    os.makedirs(d, exist_ok=True)
    sheet.save(os.path.join(d, "sheet0.png"))
    newmap = cm + "".join(ch for ch in cset if ord(ch) in cmap or ord(ch) in cmap12)
    with open(os.path.join(d, "charmap.txt"), "w", encoding="utf-8") as f:
        f.write(newmap)
    json.dump({"sprite": name, "charmapStringIndex": cm_idx,
               "origFrames": len(fs), "newFrames": len(out_frames), "missing": missing,
               "frames": out_frames},
              open(os.path.join(d, "manifest.json"), "w"), ensure_ascii=False, indent=0)
    manifest[name] = dict(orig=len(fs), total=len(out_frames), missing=len(missing))
    print(f"{name}: orig {len(fs)} + cjk {len(out_frames)-len(fs)} = {len(out_frames)} frames, missing {len(missing)} {''.join(missing[:8])}, sheet 2048x{pot(max(1,sheet_h))}")

json.dump(manifest, open(os.path.join(W, "dump", "spritefonts2_manifest.json"), "w"), indent=1)
