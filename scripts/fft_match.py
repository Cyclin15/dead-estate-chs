"""FFT-based sliding template matcher: for each candidate font/scale and each
expected character, find the best-IoU placement of the glyph template in the
on-screen region. Handles per-char wave offsets since positions are free."""
import sys, os, glob, csv, json
import numpy as np
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LW, LH = 480, 270

def phys_to_logical(img):
    a = np.array(img.convert('RGB')).astype(int)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    bright = (r > 160) & (g > 160)
    H, W = bright.shape
    out = np.zeros((LH, LW), bool)
    for ly in range(LH):
        py = int((ly + 0.5) * H / LH)
        for lx in range(LW):
            px = int((lx + 0.5) * W / LW)
            out[ly, lx] = bright[py, px]
    return out

def upscale_nn(tpl, fx, fy):
    h, w = tpl.shape
    H, W = int(round(h*fy)), int(round(w*fx))
    yi = np.minimum((np.arange(H)/fy).astype(int), h-1)
    xi = np.minimum((np.arange(W)/fx).astype(int), w-1)
    return tpl[np.ix_(yi, xi)]

def load_font_final(name):
    d = os.path.join(BASE, 'fontfinal2', name)
    sheet = Image.open(os.path.join(d, name + '_0.png')).convert('RGBA')
    alpha = np.array(sheet)[:, :, 3] > 40
    glyphs = {}
    with open(os.path.join(d, 'glyphs_%s.csv' % name), encoding='utf-8') as f:
        rows = list(csv.reader(f, delimiter=';'))
    for r in rows[1:]:
        try:
            ch = chr(int(r[0])); x, y, w, h = map(int, r[1:5])
        except Exception:
            continue
        if w and h:
            glyphs[ch] = alpha[y:y+h, x:x+w]
    return glyphs

def load_sprite_frames(spr):
    d = os.path.join(BASE, 'spritefonts2', spr)
    sheet = None
    for p in glob.glob(os.path.join(d, '*.png')):
        sheet = p
    im = np.array(Image.open(sheet).convert('RGBA'))
    # glyphs are WHITE on BLACK (RGB-encoded); alpha is 255 everywhere
    ink = (im[:, :, 0] > 128) & (im[:, :, 1] > 128)
    frames = {}
    with open(os.path.join(d, 'cjkframes.tsv'), encoding='utf-8') as f:
        for line in f:
            parts = line.rstrip('\n').split('\t')
            if len(parts) < 6 or not parts[0].isdigit():
                continue
            cc, x, y, w, h = map(int, parts[:5])
            if w and h:
                frames[chr(cc)] = ink[y:y+h, x:x+w]
    return frames

class Region:
    def __init__(self, mask):
        self.mask = mask.astype(float)
        self.H, self.W = mask.shape
        self.padded = np.zeros((self.H*2, self.W*2))
        self.padded[:self.H, :self.W] = self.mask
        self.F = np.fft.rfft2(self.padded)

    def best_iou(self, tpl, min_ink=15):
        """Slide tpl (bool) over region; return best (iou, y, x)."""
        t = tpl.astype(np.float64)
        th, tw = t.shape
        if th > self.H or tw > self.W:
            return (0, 0, 0)
        tsum = int(round(t.sum()))
        if tsum < min_ink:
            return (0, 0, 0)
        T = np.zeros((self.H*2, self.W*2))
        T[:th, :tw] = t[::-1, ::-1]
        corr = np.fft.irfft2(self.F * np.fft.rfft2(T), s=(self.H*2, self.W*2))
        valid = corr[th-1:self.H, tw-1:self.W]
        # candidate positions with intersection >= 60% of template ink
        # valid[i, j] is the correlation for the template placed at (i, j)
        Y, X = np.nonzero(valid > tsum*0.6)
        best = (0, 0, 0)
        ii = self.ii
        for y, x in zip(Y, X):
            gy, gx = y, x
            sy1, sx1 = min(self.H, gy+th), min(self.W, gx+tw)
            s = int(round(ii[sy1, sx1] - ii[gy, sx1] - ii[sy1, gx] + ii[gy, gx]))
            inter = int(round(valid[y, x]))
            inter = min(inter, tsum, s)
            union = tsum + s - inter
            if union > 0:
                iou = inter / union
                if iou > best[0]:
                    best = (iou, gy, gx)
        return best

def make_ii(mask):
    m = mask.astype(float)
    ii = np.zeros((m.shape[0]+1, m.shape[1]+1))
    ii[1:, 1:] = np.cumsum(np.cumsum(m, 0), 1)
    return ii

def main():
    shot = sys.argv[1]
    img = Image.open(os.path.join(BASE, 'shots', shot))
    log = phys_to_logical(img)
    np.save(os.path.join(BASE, 'shots', 'logical_%s.npy' % shot), log)

    y0, y1 = int(sys.argv[2]), int(sys.argv[3])
    region_mask = log[y0:y1, :]
    reg = Region(region_mask)
    reg.ii = make_ii(region_mask)
    total_ink = region_mask.sum()
    print(f"region y{y0}-{y1} ink={total_ink}")

    string = sys.argv[4] if len(sys.argv) > 4 else '我十分确信，各位都玩过那款游戏——操控那个黄色的家伙吃豆子、躲避鬼魂，对吧？……'
    if string == 'ALL':
        # top chars by frequency across all translations
        d = json.load(open(os.path.join(BASE, 'dump', 'translations.json'), encoding='utf-8'))
        from collections import Counter
        cnt = Counter()
        for v in d.values():
            cnt.update(v)
        string = ''.join(c for c, n in cnt.most_common(400))
    charset = list(dict.fromkeys(string))

    FX, FY = 2560/480.0, 1600/270.0

    candidates = []
    if '--small' in sys.argv:
        fonts = ('fntSmall', 'fntSmallBold', 'fntSmaller', 'fntSmallerBold',
                 'fntCryptic', 'fntGameFont', 'fntGameFontBold', 'fntWeirdo', 'fntTiny',
                 'fntGameFontNormal', 'fntGameFontNormalBold')
        scales = (1, 2)
    else:
        fonts = ('fntGameFontBiggest', 'fntGameFontBiggestBold', 'fntGameFontBiggestBoldItalics',
                 'Font_YoYo_50', 'Font_YoYo_30', 'fnt_gm_30', 'fntGameFontBigger', 'fntGameFontBiggerBold')
        scales = (1, 2)
    for name in fonts:
        g = load_font_final(name)
        for s in scales:
            candidates.append((f'{name} x{s}', g, s, s, False))
            candidates.append((f'{name} x{s} MIRROR', g, s, s, True))
    for ds in (3, 4, 5, 6, 2):
        candidates.append((f'typewriter ds={ds}', load_sprite_frames('sprAnyaTypewriterFont'), ds, ds, False))
        candidates.append((f'typewriter ds={ds} MIRROR', load_sprite_frames('sprAnyaTypewriterFont'), ds, ds, True))
    for ds in (2, 3, 4):
        candidates.append((f'fancy ds={ds}', load_sprite_frames('sprAnyaFancyFont'), ds, ds, False))
        candidates.append((f'fancy ds={ds} MIRROR', load_sprite_frames('sprAnyaFancyFont'), ds, ds, True))
    for ds in (6, 7, 8):
        candidates.append((f'review ds={ds}', load_sprite_frames('sprAnyaReviewFont'), ds, ds, False))

    for name, glyphs, fx, fy, mirror in candidates:
        hits = []
        for ch in charset:
            tpl0 = glyphs.get(ch)
            if tpl0 is None or not tpl0.any():
                continue
            tpl = upscale_nn(tpl0, fx, fy)
            if mirror:
                tpl = tpl[:, ::-1]
            iou, gy, gx = reg.best_iou(tpl)
            if iou > 0.7:
                hits.append((round(iou, 2), ch, gx, gy + y0))
        hits.sort(reverse=True)
        if hits:
            chars = ''.join(h[1] for h in hits)
            print(f"{name}: {len(hits)}/{len(charset)} chars matched: {chars}")
            for h in hits[:40]:
                print(f"   iou={h[0]} '{h[1]}' at x{h[2]} y{h[3]}")
        else:
            print(f"{name}: no matches")


if __name__ == "__main__":
    main()
