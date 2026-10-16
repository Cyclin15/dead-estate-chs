# Compose new font atlases: original Latin region untouched at (0,0), CJK appended.
#
# Why: the game's font textures are sub-rectangles of a shared 8192x8192 page, and glyph
# coordinates are local to that sub-rectangle. Pasting the original region at (0,0) of a
# taller canvas keeps every Latin glyph coordinate and metric pixel-identical, so nothing
# already shipped can shift. CJK glyphs are packed below the original region.
import os, sys, io, json, math, csv
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image, ImageDraw, ImageFont

W = r"D:\Steam\steamapps\common\Dead Estate\_loc_work"
ORIG = os.path.join(W, "origfonts")
OUT = os.path.join(W, "fontbuild2")
CHARSET = os.path.join(W, "charset.txt")
PAD = 1

# font asset name -> TTF used to rasterise the CJK additions
FONT_FILES = {
    "bold": r"C:\Windows\Fonts\msyhbd.ttc",
    "regular": r"C:\Windows\Fonts\msyh.ttc",
}

def read_meta(d):
    m = {}
    with open(os.path.join(d, "meta.tsv"), encoding="utf-8") as f:
        next(f)
        for line in f:
            if "\t" in line:
                k, v = line.rstrip("\n").split("\t", 1)
                m[k] = v
    return m

def read_glyphs(d):
    rows = []
    with open(os.path.join(d, "glyphs.csv"), encoding="utf-8") as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split(";")
            if len(p) < 7:
                continue
            rows.append([int(p[0]), int(p[1]), int(p[2]), int(p[3]), int(p[4]), int(p[5]), int(p[6])])
    return rows

def ttf_for(bold, italic):
    # Italic is synthesised by shearing, matching how the originals look slanted.
    return FONT_FILES["bold"] if bold else FONT_FILES["regular"]

def shear(img, amount=0.18):
    w, h = img.size
    return img.transform((w + int(h * amount), h), Image.AFFINE,
                         (1, amount, -h * amount, 0, 1, 0), resample=Image.BICUBIC)

def main():
    chars = open(CHARSET, encoding="utf-8").read()
    cjk = "".join(dict.fromkeys(c for c in chars if ord(c) > 127))
    print(f"non-ASCII glyphs to add: {len(cjk)}")
    os.makedirs(OUT, exist_ok=True)

    summary = []
    for name in sorted(os.listdir(ORIG)):
        d = os.path.join(ORIG, name)
        if not os.path.isdir(d):
            continue
        meta = read_meta(d)
        em = int(meta["EmSize"])
        bold = meta["Bold"].lower() == "true"
        italic = meta["Italic"].lower() == "true"
        pw = int(meta["PageWidth"]); ph = int(meta["PageHeight"])
        iw = int(meta["ItemSourceWidth"]); ih = int(meta["ItemSourceHeight"])
        page_png = os.path.join(d, "page.png")
        if not os.path.exists(page_png) or iw == 0 or ih == 0:
            print(f"SKIP {name}: no texture")
            continue

        base = Image.open(page_png).convert("RGBA")
        ttf = ttf_for(bold, italic)
        font = ImageFont.truetype(ttf, em)

        # measure glyphs
        boxes = []
        for ch in cjk:
            bbox = font.getbbox(ch)
            w = max(1, bbox[2] - bbox[0]); h = max(1, bbox[3] - bbox[1])
            adv = int(round(font.getlength(ch)))
            boxes.append((ch, bbox, w, h, adv))

        cell_w = max((b[2] for b in boxes), default=1) + PAD
        cell_h = max((b[3] for b in boxes), default=1) + PAD
        # start packing below the original region
        start_y = ih
        per_row = max(1, (max(pw, iw) - 0) // cell_w)
        if per_row < 1:
            per_row = 1
        rows_needed = math.ceil(len(boxes) / per_row)
        canvas_w = max(pw, per_row * cell_w)
        canvas_h = start_y + rows_needed * cell_h
        # round up to a sane texture size
        canvas_w = min(8192, max(64, canvas_w))
        canvas_h = min(8192, max(64, canvas_h))

        canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        canvas.paste(base, (0, 0))      # Latin region keeps identical pixel coordinates

        draw = ImageDraw.Draw(canvas)
        new_rows = []
        for k, (ch, bbox, w, h, adv) in enumerate(boxes):
            col = k % per_row
            row = k // per_row
            x = col * cell_w
            y = start_y + row * cell_h
            if y + h > canvas_h:
                break
            # render into a small tile so italics shear only the glyph
            tile = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
            td = ImageDraw.Draw(tile)
            td.text((-bbox[0] + 4, -bbox[1] + 4), ch, font=font, fill=(255, 255, 255, 255))
            if italic:
                tile = shear(tile)
            canvas.alpha_composite(tile, (x, y))
            new_rows.append([ord(ch), x, y, w, h, adv, 0])

        fdir = os.path.join(OUT, name)
        os.makedirs(fdir, exist_ok=True)
        canvas.save(os.path.join(fdir, f"{name}.png"))

        # CSV: original Latin glyphs (unchanged coordinates) + the new CJK glyphs
        orig_rows = read_glyphs(d)
        with open(os.path.join(fdir, f"glyphs_{name}.csv"), "w", encoding="utf-8", newline="") as f:
            wtr = csv.writer(f, delimiter=";", lineterminator="\n")
            wtr.writerow([meta["DisplayName"], em, meta["Bold"], meta["Italic"], 0, 1, 1, 1])
            for r in orig_rows:
                wtr.writerow(r + [0])
            for r in new_rows:
                wtr.writerow(r + [0])

        with open(os.path.join(fdir, "meta.json"), "w", encoding="utf-8") as f:
            json.dump({"canvas": [canvas_w, canvas_h], "item": [iw, ih],
                       "origPage": [pw, ph], "em": em, "bold": bold, "italic": italic,
                       "origGlyphs": len(orig_rows), "cjkGlyphs": len(new_rows)}, f)

        summary.append((name, em, len(orig_rows), len(new_rows), canvas_w, canvas_h))
        print(f"  {name:32s} em={em:3d} orig={len(orig_rows):3d} cjk={len(new_rows):5d} canvas={canvas_w}x{canvas_h}")

    print()
    print("fonts composed:", len(summary))
    total = sum(s[3] for s in summary)
    print("total CJK glyph entries:", total)

if __name__ == "__main__":
    main()
