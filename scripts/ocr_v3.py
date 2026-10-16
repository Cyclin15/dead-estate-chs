"""OCR a logical-res npy region against a v3fonts sheet. Usage:
  python ocr_v3.py shot.npy y0 y1 fontname   (x auto-detected from ink)"""
import sys, csv, os
import numpy as np
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(BASE, 'out', 'v3fonts')

def load_font(name):
    d = os.path.join(FONTS, name)
    sheet = np.array(Image.open(os.path.join(d, 'sheet0.png')).convert('RGBA'))
    alpha = sheet[:, :, 3] > 40
    glyphs = {}
    with open(os.path.join(d, 'glyphs.csv'), encoding='utf-8') as f:
        rows = list(csv.reader(f, delimiter=';'))
    for r in rows[1:]:
        ch = chr(int(r[0])); x, y, w, h = map(int, r[1:5])
        if w > 0 and h > 0:
            glyphs[ch] = alpha[y:y+h, x:x+w]
    return glyphs

def match(line, glyphs):
    lh, lw = line.shape
    result, conf = [], []
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
            result.append(best[1]); conf.append(round(best[0], 2))
            x = best[2]
        else:
            result.append('?'); conf.append(0)
            x += 1
    return ''.join(result), conf

if __name__ == '__main__':
    shot, y0, y1, fontname = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    lg = np.load(os.path.join(BASE, 'shots', shot + '.npy'))
    band = lg[y0-2:y1+3] > 120
    xs = np.where(band.any(axis=0))[0]
    x0, x1 = xs.min(), xs.max() + 1
    text, conf = match(band[:, x0:x1], load_font(fontname))
    print('region y[%d:%d] x[%d:%d]' % (y0, y1, x0, x1))
    print('TEXT:', text)
    print('conf:', conf)
