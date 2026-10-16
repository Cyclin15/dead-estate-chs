# Build CJK font atlases + glyph CSVs in the exact format UTMT's ImportFonts.csx consumes.
#
# Produce, per font, a folder containing:
#   <fontName>.png         - the atlas (Latin + CJK glyphs packed)
#   glyphs_<fontName>.csv  - DisplayName;EmSize;Bold;Italic;Charset;AntiAliasing;ScaleX;ScaleY
#                            then per glyph: Char;SrcX;SrcY;SrcW;SrcH;Shift;Offset
import os, sys, csv, math, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image, ImageDraw, ImageFont

WORK = r"D:\Steam\steamapps\common\Dead Estate\_loc_work"
OUT  = os.path.join(WORK, "fontbuild")

# (font asset name, Windows font file, em size, bold, italic)
FONTS = [
    ("fntGameFontNormal",          r"C:\Windows\Fonts\msyh.ttc",  12, False, False),
    ("fntGameFontNormalBold",      r"C:\Windows\Fonts\msyhbd.ttc", 12, True,  False),
    ("fntGameFontNormalItalics",   r"C:\Windows\Fonts\msyh.ttc",  12, False, True),
    ("fntGameFontNormalBoldItalics",r"C:\Windows\Fonts\msyhbd.ttc",12, True,  True),
    ("fntGameFont",                r"C:\Windows\Fonts\msyhbd.ttc", 12, True,  False),
    ("fntGameFontBold",            r"C:\Windows\Fonts\msyhbd.ttc", 12, True,  False),
    ("fntGameFontItalics",         r"C:\Windows\Fonts\msyhbd.ttc", 12, True,  True),
    ("fntGameFontBoldItalics",     r"C:\Windows\Fonts\msyhbd.ttc", 12, True,  True),
    ("fntSmall",                   r"C:\Windows\Fonts\msyh.ttc",  10, False, False),
    ("fntSmallBold",               r"C:\Windows\Fonts\msyhbd.ttc", 10, True,  False),
    ("fntSmallItalics",            r"C:\Windows\Fonts\msyh.ttc",  10, False, True),
    ("fntSmallBoldItalics",        r"C:\Windows\Fonts\msyhbd.ttc", 10, True,  True),
    ("fntSmaller",                 r"C:\Windows\Fonts\msyh.ttc",   8, False, False),
    ("fntSmallerBold",             r"C:\Windows\Fonts\msyhbd.ttc",  8, True,  False),
    ("fntSmallerItalics",          r"C:\Windows\Fonts\msyh.ttc",   8, False, True),
    ("fntSmallerBoldItalics",      r"C:\Windows\Fonts\msyhbd.ttc",  8, True,  True),
    ("fntGameFontBigger",          r"C:\Windows\Fonts\msyh.ttc",  20, False, False),
    ("fntGameFontBiggerBold",      r"C:\Windows\Fonts\msyhbd.ttc", 20, True,  False),
    ("fntGameFontBiggerItalics",   r"C:\Windows\Fonts\msyh.ttc",  20, False, True),
    ("fntGameFontBiggerBoldItalics",r"C:\Windows\Fonts\msyhbd.ttc",20, True,  True),
    ("fntGameFontBiggest",         r"C:\Windows\Fonts\msyh.ttc",  39, False, False),
    ("fntGameFontBiggestBold",     r"C:\Windows\Fonts\msyhbd.ttc", 39, True,  False),
    ("fntGameFontBiggestItalics",  r"C:\Windows\Fonts\msyh.ttc",  39, False, True),
    ("fntGameFontBiggestBoldItalics",r"C:\Windows\Fonts\msyhbd.ttc",39,True,  True),
]

ATLAS = 2048
BORDER = 2

def build(font_name, ttf, em, bold, italic, chars):
    """chars: iterable of characters to include (in addition to ASCII 32..126)."""
    os.makedirs(OUT, exist_ok=True)
    fdir = os.path.join(OUT, font_name)
    os.makedirs(fdir, exist_ok=True)

    glyphchars = [chr(c) for c in range(32, 127)] + list(chars)
    # de-dup, preserve order
    seen = set(); ordered = []
    for ch in glyphchars:
        if ch not in seen:
            seen.add(ch); ordered.append(ch)
    glyphchars = ordered

    # CJK render box: em square with headroom; Latin uses the natural size
    font = ImageFont.truetype(ttf, em)
    ascent, descent = font.getmetrics()
    # per glyph metrics from PIL
    boxes = []
    maxw = 0; maxh = 0
    for ch in glyphchars:
        try:
            bbox = font.getbbox(ch)
        except Exception:
            bbox = (0, 0, 0, 0)
        w = max(1, bbox[2] - bbox[0])
        h = max(1, bbox[3] - bbox[1])
        # use shift = advance width (GameMaker "Shift"), offset = left bearing
        try:
            adv = int(round(font.getlength(ch)))
        except Exception:
            adv = w
        boxes.append((ch, bbox, w, h, adv, bbox[0]))
        maxw = max(maxw, w); maxh = max(maxh, h)

    # grid cell size = max glyph box + border
    cw = maxw + BORDER
    chh = maxh + BORDER
    per_row = max(1, ATLAS // cw)
    rows = math.ceil(len(glyphchars) / per_row)
    # keep atlas square-ish; if too tall, use multiple sheets
    sheets = []
    per_sheet_rows = max(1, ATLAS // chh)
    per_sheet = per_row * per_sheet_rows
    for s in range(0, len(glyphchars), per_sheet):
        sheets.append(glyphchars[s:s+per_sheet])

    rows_out = []
    for si, sheet in enumerate(sheets):
        img = Image.new("RGBA", (ATLAS, ATLAS), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        for k, ch in enumerate(sheet):
            idx = glyphchars.index(ch)
            _, bbox, w, h, adv, off = boxes[idx]
            col = k % per_row
            row = k // per_row
            x = col * cw
            y = row * chh
            # draw with the glyph's own bearing so it lands at (x,y)
            d.text((x - bbox[0], y - bbox[1]), ch, font=font, fill=(255, 255, 255, 255))
            rows_out.append((ch, si, x, y, w, h, adv, off))
        name = font_name if len(sheets) == 1 else f"{font_name}_{si}"
        img.save(os.path.join(fdir, f"{name}.png"))

    # CSV
    csvp = os.path.join(fdir, f"glyphs_{font_name}.csv")
    with open(csvp, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        # header carries the native metrics so the font keeps working if fully repacked
        w.writerow(["Microsoft YaHei", em, bold, italic, 0, 1, 1, 1])
        for (ch, si, x, y, gw, gh, adv, off) in rows_out:
            w.writerow([ord(ch), x, y, gw, gh, adv, off, si])
    return len(rows_out), len(sheets)

if __name__ == "__main__":
    charset_file = os.path.join(WORK, "charset.txt")
    with open(charset_file, encoding="utf-8") as f:
        chars = f.read()
    chars = "".join(dict.fromkeys(chars))  # dedup
    print(f"charset size: {len(chars)}")
    total = 0
    for (name, ttf, em, b, i) in FONTS:
        n, sheets = build(name, ttf, em, b, i, chars)
        total += n
        print(f"  {name:32s} em={em:3d} bold={int(b)} ital={int(i)} glyphs={n:5d} sheets={sheets}")
    print("total glyph entries:", total)
