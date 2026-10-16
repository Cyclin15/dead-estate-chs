"""Game I/O helpers: launch, keys, clicks, capture (logical 480x270), OCR.
Reuses nav_anya.py internals by exec'ing its prefix."""
import sys, os, time, ctypes, subprocess
import numpy as np
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'shots')

src = open(os.path.join(BASE, 'scripts', 'nav_anya.py'), encoding='utf-8').read()
exec(src.split("# --- main ---")[0])

# --- OCR (from read_screen.py, adapted to take a logical npy directly) ---
import csv
_FONTS = os.path.join(BASE, 'fontfinal2')

def load_font(name):
    d = os.path.join(_FONTS, name)
    sheet = np.array(Image.open(os.path.join(d, name + '_0.png')).convert('RGBA'))
    alpha = sheet[:, :, 3] > 40
    glyphs = {}
    with open(os.path.join(d, 'glyphs_%s.csv' % name), encoding='utf-8') as f:
        rows = list(csv.reader(f, delimiter=';'))
    for r in rows[1:]:
        ch = chr(int(r[0])); x, y, w, h = map(int, r[1:5])
        if w > 0 and h > 0:
            glyphs[ch] = alpha[y:y+h, x:x+w]
    return glyphs

def ocr_line(line, glyphs):
    lh, lw = line.shape
    result = []
    x = 0
    while x < lw:
        if not line[:, x].any():
            x += 1; continue
        best = None
        for ch, tpl in glyphs.items():
            th, tw = tpl.shape
            tplcols = np.where(tpl.any(axis=0))[0]
            if not len(tplcols): continue
            tx = x - tplcols[0]
            if tx < 0: continue
            x_end = min(lw, tx + tw)
            w = x_end - tx
            if w < max(2, tw - 2): continue
            sub = line[:, tx:x_end]
            tsub = tpl[:, :w]
            for vy in range(0, max(1, lh - th + 1)):
                a = sub[vy:vy+th]
                if a.shape != tsub.shape: continue
                inter = (a & tsub).sum()
                union = (a | tsub).sum()
                if union == 0: continue
                iou = inter / union
                if best is None or iou > best[0]:
                    best = (iou, ch, tx + tw)
        if best and best[0] > 0.55:
            result.append(best[1]); x = best[2]
        else:
            result.append('?'); x += 1
    return ''.join(result)

def ocr_region(lg, x0, y0, x1, y1, fontname='fntSmall'):
    """OCR a logical region: splits into text lines by ink rows."""
    glyphs = load_font(fontname)
    reg = lg[y0:y1, x0:x1] > 150
    rows = reg.any(axis=1)
    lines = []
    y = 0
    while y < len(rows):
        if rows[y]:
            y2 = y
            while y2 < len(rows) and rows[y2]: y2 += 1
            lines.append((y + y0, ocr_line(reg[y:y2], glyphs)))
            y = y2
        else:
            y += 1
    return lines

def phys(lx, ly):
    return int(lx * 2560 / 480), int(80 + ly * 1440 / 270)
