"""Decode on-screen text from a screenshot by template-matching against the
rebuilt font sheets (fontfinal2). Usage:
  python read_screen.py shot.png x0 y0 x1 y1 [fontname]
Coordinates are screen pixels; the region is downsampled to logical resolution
(480x270 * 3.0479) and matched greedily left-to-right."""
import sys, csv, os
from PIL import Image
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(BASE, 'fontfinal2')
SCALE = None  # computed from shot size

def load_font(name):
    d = os.path.join(FONTS, name)
    sheet = Image.open(os.path.join(d, name + '_0.png')).convert('RGBA')
    sheet = np.array(sheet)
    alpha = sheet[:, :, 3] > 40
    glyphs = {}
    with open(os.path.join(d, 'glyphs_%s.csv' % name), encoding='utf-8') as f:
        rows = list(csv.reader(f, delimiter=';'))
    for r in rows[1:]:
        ch = chr(int(r[0])); x, y, w, h = map(int, r[1:5])
        glyphs[ch] = alpha[y:y+h, x:x+w]
    return glyphs

def to_logical(img, x0, y0, x1, y1):
    W, H = img.size
    scale = W / 480.0
    g = np.array(img.convert('L')).astype(int)
    region = g[y0:y1, x0:x1] > 150
    # nearest-sample down to logical resolution
    lw = int((x1-x0)/scale); lh = int((y1-y0)/scale)
    out = np.zeros((lh, lw), bool)
    for ly in range(lh):
        sy = int(ly*scale)+int(scale/2)
        for lx in range(lw):
            sx = int(lx*scale)+int(scale/2)
            out[ly, lx] = region[sy, sx]
    return out

def match(line, glyphs):
    """Greedy left-to-right match of a logical bitmap line against glyph templates."""
    lh, lw = line.shape
    result = []
    conf = []
    x = 0
    while x < lw:
        # skip blank columns
        col = line[:, x]
        if not col.any():
            x += 1; continue
        # try each glyph anchored so its first inky column aligns at x
        best = None
        for ch, tpl in glyphs.items():
            th, tw = tpl.shape
            # glyph must fit vertically-ish and start at x
            tplcols = np.where(tpl.any(axis=0))[0]
            if not len(tplcols): continue
            lead = tplcols[0]
            tx = x - lead
            if tx < 0: continue
            # overlap window
            x_end = min(lw, tx + tw)
            w = x_end - tx
            if w < max(2, tw - 2): continue
            sub = line[:, tx:x_end]
            tsub = tpl[:, :w]
            # vertical alignment: try offsets
            for vy in range(0, max(1, lh - th + 1)):
                a = sub[vy:vy+th]
                if a.shape != tsub.shape: continue
                inter = (a & tsub).sum()
                union = (a | tsub).sum()
                if union == 0: continue
                iou = inter / union
                # penalize leftover ink right after (next glyph gap check lenient)
                if best is None or iou > best[0]:
                    best = (iou, ch, tx + tw, vy)
        if best and best[0] > 0.55:
            result.append(best[1]); conf.append(round(best[0],2))
            x = best[2]
        else:
            result.append('?'); conf.append(0)
            x += 1
    return ''.join(result), conf

if __name__ == '__main__':
    shot, x0, y0, x1, y1 = sys.argv[1], *map(int, sys.argv[2:6])
    fontname = sys.argv[6] if len(sys.argv) > 6 else 'fntGameFontBold'
    img = Image.open(os.path.join(BASE, 'shots', shot))
    line = to_logical(img, x0, y0, x1, y1)
    glyphs = load_font(fontname)
    text, conf = match(line, glyphs)
    print('logical size:', line.shape)
    print('TEXT:', text)
    print('conf:', conf)
