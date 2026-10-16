"""Match a single on-screen glyph against font frames, sweeping a linear
un-shear first (the wave shader shears glyphs approximately linearly).
Usage: python shear_match.py npy y0 y1 x0 x1
"""
import sys, os
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fft_match import load_sprite_frames, load_font_final, Region, make_ii
from verify_decode import exact_iou


def unshear(g, s):
    """Inverse-shear: shift row y left/right by s*(y-c) pixels."""
    h, w = g.shape
    c = (h - 1) / 2.0
    out = np.zeros_like(g)
    for y in range(h):
        d = int(round(s * (y - c)))
        if d == 0:
            out[y] = g[y]
        elif d > 0 and d < w:
            out[y, :w - d] = g[y, d:]
        elif d < 0 and -d < w:
            out[y, -d:] = g[y, :w + d]
    return out


def main():
    npy = sys.argv[1]
    y0, y1, x0, x1 = map(int, sys.argv[2:6])
    mask = np.load(os.path.join(BASE, 'shots', npy))
    g0 = mask[y0:y1, x0:x1]
    gh, gw = g0.shape
    print(f"glyph {gw}x{gh} ink={g0.sum()}")

    frames = {}
    for spr in ('sprAnyaFancyFont', 'sprAnyaTypewriterFont', 'sprAnyaReviewFont'):
        for ch, tpl in load_sprite_frames(spr).items():
            frames[('spr', ch)] = tpl
    for name in ('fntSmall', 'fntSmallBold', 'fntSmaller', 'fntSmallerBold',
                 'fntGameFont', 'fntGameFontBold', 'fntGameFontNormal',
                 'fntCryptic', 'fntWeirdo'):
        for ch, tpl in load_font_final(name).items():
            frames[('ff', name, ch)] = tpl

    results = []
    for s in np.arange(-0.45, 0.46, 0.05):
        g = unshear(g0, s)
        if g.sum() < g0.sum() * 0.9:
            continue
        pad = np.zeros((gh * 2 + 20, gw * 2 + 20), bool)
        pad[10:10 + gh, 10:10 + gw] = g
        reg = Region(pad)
        reg.ii = make_ii(pad)
        for key, tpl in frames.items():
            th, tw = tpl.shape
            for sc in (1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0):
                H, W = int(round(th * sc)), int(round(tw * sc))
                if abs(H - gh) > 3 or abs(W - gw) > 3:
                    continue
                yi = np.minimum((np.arange(H) / sc).astype(int), th - 1)
                xi = np.minimum((np.arange(W) / sc).astype(int), tw - 1)
                t = tpl[np.ix_(yi, xi)]
                iou, py, px = reg.best_iou(t, min_ink=20)
                if iou > 0.55:
                    ei = exact_iou(pad, t, py, px)
                    results.append((round(ei, 2), round(s, 2), key, sc))
    results.sort(reverse=True)
    for r in results[:15]:
        print(r)


if __name__ == '__main__':
    main()
