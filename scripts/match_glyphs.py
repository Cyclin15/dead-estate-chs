"""Segment a band of the reconstructed logical bitmap into glyphs (column
gaps) and match each glyph against ALL CJK frames at fine scales.
Usage: python match_glyphs.py recon_bright_shot19.npy y0 y1 x0 x1 [topn]
"""
import sys, os
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fft_match import load_sprite_frames, Region, make_ii
from verify_decode import exact_iou


def seg_glyphs(band, max_gap=1):
    colp = band.any(axis=0)
    segs = []
    x = 0
    W = band.shape[1]
    while x < W:
        if colp[x]:
            x0 = x
            gap = 0
            x += 1
            while x < W:
                if colp[x]:
                    gap = 0
                    x += 1
                else:
                    gap += 1
                    if gap > max_gap:
                        break
                    x += 1
            x1 = x - gap
            sub = band[:, x0:x1]
            rows = np.nonzero(sub.any(axis=1))[0]
            segs.append((x0, x1, rows.min(), rows.max() + 1))
        else:
            x += 1
    return segs


def main():
    npy = sys.argv[1]
    y0, y1, x0, x1 = map(int, sys.argv[2:6])
    topn = int(sys.argv[6]) if len(sys.argv) > 6 else 3
    mask = np.load(os.path.join(BASE, 'shots', npy))
    band = mask[y0:y1, x0:x1]

    scales = [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0]
    fonts = [('fancy', 'sprAnyaFancyFont'), ('twr', 'sprAnyaTypewriterFont'),
             ('rev', 'sprAnyaReviewFont')]
    frames_all = {tag: load_sprite_frames(spr) for tag, spr in fonts}

    for gx0, gx1, gy0, gy1 in seg_glyphs(band):
        g = band[gy0:gy1, gx0:gx1]
        gh, gw = g.shape
        pad = np.zeros((gh * 2 + 20, gw * 2 + 20), bool)
        pad[10:10 + gh, 10:10 + gw] = g
        reg = Region(pad)
        reg.ii = make_ii(pad)
        results = []
        for tag, frames in frames_all.items():
            for ch, tpl in frames.items():
                th, tw = tpl.shape
                for s in scales:
                    H, W = int(round(th * s)), int(round(tw * s))
                    if abs(H - gh) > 4 or abs(W - gw) > 4:
                        continue
                    yi = np.minimum((np.arange(H) / s).astype(int), th - 1)
                    xi = np.minimum((np.arange(W) / s).astype(int), tw - 1)
                    t = tpl[np.ix_(yi, xi)]
                    iou, py, px = reg.best_iou(t, min_ink=20)
                    if iou > 0.5:
                        ei = exact_iou(pad, t, py, px)
                        results.append((round(ei, 2), tag, ch, s, gx0 + px - 10 + x0,
                                        gy0 + py - 10 + y0))
        results.sort(reverse=True)
        print(f"glyph x{gx0+x0}-{gx1+x0} y{gy0+y0}-{gy1+y0} ({gw}x{gh}) ink={g.sum()}")
        for r in results[:topn]:
            print(f"    {r[0]}  {r[1]} '{r[2]}' scale={r[3]} at ({r[4]},{r[5]})")


if __name__ == '__main__':
    main()
