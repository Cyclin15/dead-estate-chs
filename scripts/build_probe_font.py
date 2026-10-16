# Build 2x-oversampled CJK atlases for the probe fonts.
#
# The original Latin region is left completely alone: Latin glyphs keep pointing at the
# vanilla page item. Only the new CJK glyphs go into this atlas, rendered at 2x the
# logical em size so the engine can scale them back down sharply.
import os, sys, io, json, math, csv
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image, ImageDraw, ImageFont

W = r"D:\Steam\steamapps\common\Dead Estate\_loc_work"
ORIG = os.path.join(W, "origfonts")
OUT = os.path.join(W, "probe_fonts")
PAD = 2
SCALE = 2                       # oversample factor

# only the font(s) we are probing
TARGETS = {name: ttf for name, ttf in {
    "fntGameFontNormal": r"C:\Windows\Fonts\msyh.ttc",
    "fntSmall": r"C:\Windows\Fonts\msyh.ttc",
}.items()}

chars = open(os.path.join(W, "charset.txt"), encoding="utf-8").read()
cjk = "".join(dict.fromkeys(c for c in chars if ord(c) > 127))
print(f"CJK glyphs: {len(cjk)}  oversample: {SCALE}x")

def read_meta(d):
    m = {}
    for line in open(os.path.join(d, "meta.tsv"), encoding="utf-8").read().splitlines()[1:]:
        if "\t" in line:
            k, v = line.split("\t", 1)
            m[k] = v
    return m

os.makedirs(OUT, exist_ok=True)
for name, ttf in TARGETS.items():
    d = os.path.join(ORIG, name)
    meta = read_meta(d)
    em = int(meta["EmSize"])
    px = em * SCALE
    font = ImageFont.truetype(ttf, px)

    boxes = []
    for ch in cjk:
        bbox = font.getbbox(ch)
        w = max(1, bbox[2] - bbox[0]); h = max(1, bbox[3] - bbox[1])
        adv = int(round(font.getlength(ch)))
        boxes.append((ch, bbox, w, h, adv))

    cell_w = max(b[2] for b in boxes) + PAD
    cell_h = max(b[3] for b in boxes) + PAD
    per_row = max(1, 2048 // cell_w)
    rows = math.ceil(len(boxes) / per_row)
    cw = per_row * cell_w
    chh = rows * cell_h
    # round up to powers of two, capped at 8192
    def pot(v):
        p = 1
        while p < v:
            p *= 2
        return p
    cw = min(8192, pot(cw)); chh = min(8192, pot(chh))
    print(f"  {name}: em={em} -> {px}px  cell={cell_w}x{cell_h} per_row={per_row} rows={rows} canvas={cw}x{chh}")

    canvas = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
    dr = ImageDraw.Draw(canvas)
    rows_out = []
    for k, (ch, bbox, w, h, adv) in enumerate(boxes):
        col = k % per_row; row = k // per_row
        x = col * cell_w; y = row * cell_h
        dr.text((x - bbox[0], y - bbox[1]), ch, font=font, fill=(255, 255, 255, 255))
        rows_out.append([ord(ch), x, y, w, h, adv, 0])

    fdir = os.path.join(OUT, name)
    os.makedirs(fdir, exist_ok=True)
    canvas.save(os.path.join(fdir, "cjk.png"))
    with open(os.path.join(fdir, "cjk_glyphs.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        for r in rows_out:
            w.writerow(r)
    json.dump({"canvas": [cw, chh], "scale": SCALE, "em": em, "count": len(rows_out)},
              open(os.path.join(fdir, "meta.json"), "w"), indent=1)
print("done")
