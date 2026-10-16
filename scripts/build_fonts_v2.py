# v2 font build: render CJK glyphs at LOGICAL pixel size (no supersampling, Scale=1).
#
# Pipeline facts this is built on:
#  - Game draws text 1:1 either on the 480x270 world surface (then integer-nearest upscaled)
#    or directly in GUI space; global texture interpolation is OFF (GEN8 has no Interpolate).
#  - GM fonts bake vertical alignment into uniform-height glyph bitmaps:
#    all Latin quads share one cell height; ink row = distance from cell top.
#  - Glyph.Offset = horizontal left bearing; Shift = advance.
# So: CJK quads use the SAME cell height as the font's Latin glyphs, ink placed by
# baseline (ink bottom = baseline + 1 when it fits), binary alpha, pixel font source.
import os, sys, io, json, math, csv
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from fontTools.ttLib import TTFont

W = r"D:\Steam\steamapps\common\Dead Estate\_loc_work"
ORIG = os.path.join(W, "origfonts")
OUT = os.path.join(W, "fontfinal2")
CHARSET = os.path.join(W, "charset.txt")
BASELINES = json.load(open(os.path.join(W, "dump", "baselines.json"), encoding="utf-8"))

FUSION = {
    8:  os.path.join(W, "pixelfonts", "f8",  "fusion-pixel-8px-proportional-zh_hans.ttf"),
    10: os.path.join(W, "pixelfonts", "f10", "fusion-pixel-10px-proportional-zh_hans.ttf"),
    12: os.path.join(W, "pixelfonts", "f12", "fusion-pixel-12px-proportional-zh_hans.ttf"),
}
EM_MAP = {5: 8, 8: 8, 10: 10, 12: 12, 15: 15, 16: 16, 20: 20, 30: 30, 39: 39, 50: 50}
BASE = {8: 8, 10: 10, 12: 12, 15: 12, 16: 8, 20: 10, 30: 10, 39: 12, 50: 10}
PAD = 2

chars = open(CHARSET, encoding="utf-8").read()
cset = [c for c in dict.fromkeys(c for c in chars if ord(c) > 127)]  # ♦ (U+2666) included: unprocessed effect codes DO get drawn
print(f"render set: {len(cset)} chars")

# cmap coverage per base font
cmaps = {}
for b, p in FUSION.items():
    cmaps[b] = TTFont(p).getBestCmap()
    missing = [c for c in cset if ord(c) not in cmaps[b]]
    print(f"  fusion-{b}px missing: {len(missing)} {''.join(missing[:10])}")

def shear(img, amount=0.17):
    w, h = img.size
    return img.transform((w + int(h * amount) + 2, h), Image.AFFINE,
                         (1, amount, -h * amount, 0, 1, 0), resample=Image.BICUBIC)

_fontcache = {}
def get_font(base, px):
    f = _fontcache.get((base, px))
    if f is None:
        f = ImageFont.truetype(FUSION[base], px)
        _fontcache[(base, px)] = f
    return f

def render_char(ch, px):
    """Return (binary ink image, advance) for ch rendered at px logical size."""
    base = BASE[px]
    if ord(ch) not in cmaps[base]:
        base = 12  # rare-char fallback (10px set misses a couple)
    f = get_font(base, px)
    adv = int(round(f.getlength(ch)))
    im = Image.new("L", (px * 3, px * 3), 0)
    ImageDraw.Draw(im).text((px, px), ch, font=f, fill=255)
    im = im.point(lambda v: 255 if v >= 128 else 0)
    bb = im.getbbox()
    if bb is None:
        return None, adv
    return im.crop(bb), adv

def read_meta(d):
    m = {}
    for line in open(os.path.join(d, "meta.tsv"), encoding="utf-8").read().splitlines()[1:]:
        if "\t" in line:
            k, v = line.split("\t", 1)
            m[k] = v
    return m

def pot(v):
    p = 1
    while p < v: p *= 2
    return min(p, 8192)

total_png = 0
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
    bl = BASELINES[name]
    cellH = bl["cellH"]; baseline = bl["baseline"]
    px = EM_MAP[em]
    tiny = (em == 5)  # 8px CJK cannot fit the 7px cell: grow the quad, bump line height in csx
    quadH = (max(cellH, 9) if tiny else cellH)

    placed = []  # (char, inkImg, adv, topRow)
    maxInkW = 0
    for ch in cset:
        ink, adv = render_char(ch, px)
        if ink is None:
            continue
        if bold:
            if px >= 16:
                ink = ink.filter(ImageFilter.MaxFilter(3))
            else:
                w, h = ink.size
                fat = Image.new("L", (w + 1, h + 1), 0)
                fat.paste(ink, (0, 0)); fat.paste(ink, (1, 0)); fat.paste(ink, (0, 1))
                ink = fat
            ink = ink.crop(ink.getbbox())
        if italic:
            sh = shear(ink)
            sh = sh.point(lambda v: 255 if v >= 128 else 0)
            ink = sh.crop(sh.getbbox())
        bottomRow = baseline + 1
        if bottomRow >= quadH: bottomRow = quadH - 1
        topRow = bottomRow - ink.size[1] + 1
        if topRow < 0: topRow = 0
        if tiny:
            topRow = 1
        placed.append((ch, ink, adv, topRow))
        maxInkW = max(maxInkW, ink.size[0])

    # pack: latin art at (0,0), CJK below, single texture page
    cell_w = maxInkW + PAD
    page_w = pot(max(2048, iw))
    while page_w < 8192:
        cols = page_w // cell_w
        rows = math.ceil(len(placed) / cols)
        if ih + rows * (quadH + PAD) <= 8192:
            break
        page_w *= 2
    cols = page_w // cell_w
    rows = math.ceil(len(placed) / cols)
    assert ih + rows * (quadH + PAD) <= 8192, f"{name} does not fit"
    page_h = pot(ih + rows * (quadH + PAD) + 8)
    canvas = Image.new("RGBA", (page_w, page_h), (0, 0, 0, 0))
    canvas.paste(Image.open(os.path.join(d, "page.png")).convert("RGBA"), (0, 0))

    fdir = os.path.join(OUT, name)
    os.makedirs(fdir, exist_ok=True)
    out_rows = []
    for k, (ch, ink, adv, topRow) in enumerate(placed):
        col = k % cols; row = k // cols
        x = col * cell_w
        y = ih + row * (quadH + PAD)
        quad = Image.new("L", (ink.size[0], quadH), 0)
        quad.paste(ink, (0, topRow))
        rgba = Image.merge("RGBA", tuple(quad.split() * 3) + (quad.split()[0],))
        canvas.paste(rgba, (x, y))
        out_rows.append([ord(ch), x, y, ink.size[0], quadH, adv, 0])

    latin = [l.split(";") for l in open(os.path.join(d, "glyphs.csv"), encoding="utf-8").read().splitlines()[1:] if l.strip()]
    png = os.path.join(fdir, f"{name}_0.png")
    canvas.save(png)
    total_png += os.path.getsize(png)
    with open(os.path.join(fdir, f"glyphs_{name}.csv"), "w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f, delimiter=";", lineterminator="\n")
        wr.writerow([meta["DisplayName"], em, meta["Bold"], meta["Italic"], 0, 1, 1, 1])  # ScaleX=ScaleY=1
        for r in latin:
            wr.writerow(r[:7] + [0])
        for r in out_rows:
            wr.writerow(r + [0])
    manifest.append({"font": name, "em": em, "px": px, "latin": len(latin), "cjk": len(out_rows),
                     "cellH": cellH, "quadH": quadH, "page": f"{page_w}x{page_h}", "tiny": tiny})
    print(f"  {name:32s} em={em:2d} px={px:2d} latin={len(latin):3d} cjk={len(out_rows):5d} quad={quadH} page={page_w}x{page_h}")

json.dump(manifest, open(os.path.join(W, "dump", "fontfinal2_manifest.json"), "w"), indent=1)
print(f"fonts: {len(manifest)}  PNG bytes: {total_png/1048576:.1f} MB")
