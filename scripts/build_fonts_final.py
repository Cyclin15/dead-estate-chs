# Final font composition: original Latin art preserved at (0,0), CJK appended at an
# oversample factor so the engine can scale it back down sharply.
#
# Oversample choice: the game renders text 1:1 onto a 480x270 surface that is then blown
# up by windowSize (2 by default), so CJK needs >=2x the logical size. Huge display fonts
# stay at 1x to keep the package reasonable.
import os, sys, io, json, math, csv
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image, ImageDraw, ImageFont

W = r"D:\Steam\steamapps\common\Dead Estate\_loc_work"
ORIG = os.path.join(W, "origfonts")
OUT = os.path.join(W, "fontfinal")
CHARSET = os.path.join(W, "charset.txt")
PAD = 2

REG = r"C:\Windows\Fonts\msyh.ttc"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"

# fonts rendered at 2x (body text / UI) vs 1x (rarely-used display faces)
HI = {
    "fntGameFont", "fntGameFontNormal", "fntGameFontBold",
    "fntGameFontNormalBold", "fntGameFontItalics", "fntGameFontNormalItalics",
    "fntGameFontBoldItalics", "fntGameFontNormalBoldItalics",
    "fntSmall", "fntSmallBold", "fntSmallItalics", "fntSmallBoldItalics",
    "fntSmaller", "fntSmallerBold", "fntSmallerItalics", "fntSmallerBoldItalics",
    "fntGameFontBigger", "fntGameFontBiggerBold",
    "fntGameFontBiggerItalics", "fntGameFontBiggerBoldItalics",
    "fntGameFontItalicsBigger",
}

def read_meta(d):
    m = {}
    for line in open(os.path.join(d, "meta.tsv"), encoding="utf-8").read().splitlines()[1:]:
        if "\t" in line:
            k, v = line.split("\t", 1)
            m[k] = v
    return m

def read_glyphs(d):
    rows = []
    for line in open(os.path.join(d, "glyphs.csv"), encoding="utf-8").read().splitlines()[1:]:
        p = line.split(";")
        if len(p) >= 7:
            rows.append([int(x) for x in p[:7]])
    return rows

def pot(v):
    p = 1
    while p < v:
        p *= 2
    return p

def shear(img, amount=0.17):
    w, h = img.size
    return img.transform((w + int(h * amount), h), Image.AFFINE,
                         (1, amount, -h * amount, 0, 1, 0), resample=Image.BICUBIC)

chars = open(CHARSET, encoding="utf-8").read()
cjk = "".join(dict.fromkeys(c for c in chars if ord(c) > 127))
os.makedirs(OUT, exist_ok=True)
print(f"CJK characters: {len(cjk)}")

total_bytes = 0
manifest = []
for name in sorted(os.listdir(ORIG)):
    d = os.path.join(ORIG, name)
    if not os.path.isdir(d):
        continue
    meta = read_meta(d)
    em = int(float(meta["EmSize"]))
    bold = meta["Bold"].lower() == "true"
    italic = meta["Italic"].lower() == "true"
    iw = int(meta["ItemSourceWidth"]); ih = int(meta["ItemSourceHeight"])
    if iw == 0 or ih == 0:
        print(f"  SKIP {name}: no texture")
        continue

    ss = 2 if name in HI else 1
    ttf = BOLD if bold else REG
    px = max(1, em * ss)
    font = ImageFont.truetype(ttf, px)

    boxes = []
    for ch in cjk:
        bb = font.getbbox(ch)
        w = max(1, bb[2] - bb[0]); h = max(1, bb[3] - bb[1])
        adv = int(round(font.getlength(ch)))
        boxes.append((ch, bb, w, h, adv))

    cell_w = max(b[2] for b in boxes) + PAD
    cell_h = max(b[3] for b in boxes) + PAD
    # pack the CJK block into its own canvases so it can sit beside/below the Latin art
    per_row_2048 = max(1, 2048 // cell_w)
    per_sheet = per_row_2048 * max(1, 2048 // cell_h)
    sheets = [boxes[i:i + per_sheet] for i in range(0, len(boxes), per_sheet)]

    # sheet 0 also carries the Latin art at (0,0)
    sheet0_w = max(2048, iw)
    sheet0_rows = math.ceil(len(sheets[0]) / per_row_2048)
    sheet0_h = ih + sheet0_rows * cell_h

    fdir = os.path.join(OUT, name)
    os.makedirs(fdir, exist_ok=True)
    rows_out = []
    for si, sheet in enumerate(sheets):
        base_h = ih if si == 0 else 0
        rows = math.ceil(len(sheet) / per_row_2048)
        cw = max(2048, iw) if si == 0 else per_row_2048 * cell_w
        chh = base_h + rows * cell_h
        canvas = Image.new("RGBA", (pot(cw), pot(chh)), (0, 0, 0, 0))
        if si == 0:
            canvas.paste(Image.open(os.path.join(d, "page.png")).convert("RGBA"), (0, 0))
        dr = ImageDraw.Draw(canvas)
        for k, (c, bb, w, h, adv) in enumerate(sheet):
            col = k % per_row_2048; row = k // per_row_2048
            x = col * cell_w
            y = base_h + row * cell_h
            tile = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
            ImageDraw.Draw(tile).text((-bb[0] + 4, -bb[1] + 4), c, font=font,
                                      fill=(255, 255, 255, 255))
            if italic:
                tile = shear(tile)
            canvas.alpha_composite(tile, (x, y))
            # Shift stays the LOGICAL advance: divide the oversampled advance back down
            logical_adv = max(1, int(round(adv / ss)))
            rows_out.append([ord(c), x, y, w, h, logical_adv, 0, si])
        canvas.save(os.path.join(fdir, f"{name}_{si}.png"))
        total_bytes += os.path.getsize(os.path.join(fdir, f"{name}_{si}.png"))

    # Latin glyphs keep their shipped coordinates; they now live on sheet 0.
    # Column 8 is the sheet index (0 for Latin).
    latin = read_glyphs(d)
    with open(os.path.join(fdir, f"glyphs_{name}.csv"), "w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f, delimiter=";", lineterminator="\n")
        wr.writerow([meta["DisplayName"], em, meta["Bold"], meta["Italic"], 0, 1, ss, ss])
        for r in latin:
            wr.writerow(r + [0])
        for r in rows_out:
            wr.writerow(r)

    manifest.append((name, em, ss, len(latin), len(rows_out), len(sheets)))
    print(f"  {name:32s} em={em:3d} ss={ss}x sheets={len(sheets)} latin={len(latin):3d} cjk={len(rows_out):5d}")

print()
print("fonts:", len(manifest), " PNG bytes: %.1f MB" % (total_bytes / 1048576))
json.dump([{"font": m[0], "em": m[1], "ss": m[2], "latin": m[3], "cjk": m[4], "sheets": m[5]}
           for m in manifest], open(os.path.join(W, "dump", "fontfinal_manifest.json"), "w"), indent=1)
