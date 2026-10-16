"""Match on-screen text against the CJK frames generated for the Anya sprite
fonts (spritefonts2/<spr>/sheet*.png + cjkframes.tsv). Tries each candidate
draw scale; reports best per-glyph matches."""
import sys, os, glob
import numpy as np
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_frames(spr):
    d = os.path.join(BASE, 'spritefonts2', spr)
    sheet = None
    for p in glob.glob(os.path.join(d, '*.png')):
        sheet = p
    im = np.array(Image.open(sheet).convert('RGBA'))
    alpha = im[:, :, 3] > 40
    frames = {}
    with open(os.path.join(d, 'cjkframes.tsv'), encoding='utf-8') as f:
        for line in f:
            parts = line.rstrip('\n').split('\t')
            if len(parts) < 6 or not parts[0].isdigit():
                continue
            cc, x, y, w, h = map(int, parts[:5])
            frames[chr(cc)] = alpha[y:y+h, x:x+w]
    return frames

def upscale(tpl, factor):
    """Nearest-neighbor upscale by non-integer factor."""
    h, w = tpl.shape
    H, W = int(round(h*factor)), int(round(w*factor))
    yi = np.minimum((np.arange(H)/factor).astype(int), h-1)
    xi = np.minimum((np.arange(W)/factor).astype(int), w-1)
    return tpl[np.ix_(yi, xi)]

def match_region(mask, frames, factor, xrange_, yrange_):
    """Segment mask (bool screen bitmap) into glyphs, match each against templates."""
    H, W = mask.shape
    colp = mask.sum(axis=0)
    segs = []
    x = 0
    while x < W:
        if colp[x] > 0:
            x0 = x
            while x < W and colp[x] > 0:
                x += 1
            # allow small gaps (parts of one glyph)
            while x < W and (colp[x:x+5] > 0).any():
                x += 1
                while x < W and colp[x] > 0:
                    x += 1
            sub = mask[:, x0:x]
            rows = np.where(sub.any(axis=1))[0]
            segs.append((x0 + rows.min()*0, x, rows.min(), rows.max()+1))
        x += 1
    out = []
    for (sx0, sx1, sy0, sy1) in segs:
        seg = mask[sy0:sy1, sx0:sx1]
        best = (0, '?')
        for ch, tpl in frames.items():
            t = upscale(tpl, factor)
            th, tw = t.shape
            gh, gw = seg.shape
            # allow size mismatch +-4px
            if abs(th-gh) > 5 or abs(tw-gw) > 5:
                continue
            ph = max(th, gh) + 4
            pw = max(tw, gw) + 4
            A = np.zeros((ph, pw), bool)
            A[2:2+gh, 2:2+gw] = seg
            for dy in range(0, ph-th+1):
                for dx in range(0, pw-tw+1):
                    B = np.zeros((ph, pw), bool)
                    B[dy:dy+th, dx:dx+tw] = t
                    inter = (A & B).sum()
                    union = (A | B).sum()
                    if union and inter/union > best[0]:
                        best = (inter/union, ch)
        out.append((best[1], round(best[0], 2), sx0, sx1, sy0, sy1))
    return out

if __name__ == '__main__':
    shot = sys.argv[1]
    x0, y0, x1, y1 = map(int, sys.argv[2:6])
    img = Image.open(os.path.join(BASE, 'shots', shot)).convert('RGB')
    a = np.array(img).astype(int)
    r, g, b = a[:,:,0], a[:,:,1], a[:,:,2]
    mask = (r > 170) & (g > 170)  # any bright color (yellow or white)
    mask = mask[y0:y1, x0:x1]
    SCREEN = 1463/480.0
    for spr, scales in [('sprAnyaTypewriterFont', [5, 4, 6, 3]), ('sprAnyaFancyFont', [3, 2, 4])]:
        frames = load_frames(spr)
        for ds in scales:
            factor = ds * SCREEN
            res = match_region(mask, frames, factor, None, None)
            txt = ''.join(x[0] for x in res)
            score = [x[1] for x in res]
            good = sum(1 for s in score if s > 0.8)
            print(f'{spr} scale={ds}: {good}/{len(res)} good -> {txt}')
            if good:
                print('   scores:', score)
