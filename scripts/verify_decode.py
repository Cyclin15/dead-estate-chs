"""Greedy-decode a reconstructed logical bitmap band against the rebuilt
sprite-font CJK frames (native logical scale), with exact boolean IoU
re-verification of every accepted glyph.
Usage: python verify_decode.py recon_bright_shot19.npy y0 y1 x0 x1 [erode [fontfilter]]
"""
import sys, os, json
from collections import Counter
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fft_match import load_sprite_frames, upscale_nn, Region, make_ii


def erode(mask, n):
    m = mask.copy()
    for _ in range(n):
        p = np.pad(m, 1)
        m = (p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:] & p[1:-1, 1:-1])
    return m


def exact_iou(mask, tpl, gy, gx):
    th, tw = tpl.shape
    H, W = mask.shape
    y1, x1 = min(H, gy + th), min(W, gx + tw)
    sub = mask[gy:y1, gx:x1]
    t = tpl[:y1 - gy, :x1 - gx]
    inter = int((sub & t).sum())
    union = int((sub | t).sum())
    return inter / union if union else 0.0


def main():
    npy = sys.argv[1]
    y0, y1, x0, x1 = map(int, sys.argv[2:6])
    er = int(sys.argv[6]) if len(sys.argv) > 6 else 0
    fontfilter = sys.argv[7] if len(sys.argv) > 7 else None

    mask = np.load(os.path.join(BASE, 'shots', npy))
    band = mask[y0:y1, x0:x1]
    if er:
        band = erode(band, er)
    print(f"band {npy} y{y0}-{y1} x{x0}-{x1} erode={er} ink={band.sum()}")

    d = json.load(open(os.path.join(BASE, 'dump', 'translations.json'), encoding='utf-8'))
    cnt = Counter()
    for v in d.values():
        cnt.update(v)
    charset = set(c for c, n in cnt.most_common(600))

    configs = []
    for spr, scales in [('sprAnyaFancyFont', (1, 2)),
                        ('sprAnyaTypewriterFont', (1, 2, 3)),
                        ('sprAnyaReviewFont', (1, 2))]:
        if fontfilter and fontfilter not in spr:
            continue
        for s in scales:
            configs.append((spr, s))

    for spr, s in configs:
        frames = load_sprite_frames(spr)
        reg = Region(band)
        reg.ii = make_ii(band)
        cands = []
        for ch, tpl0 in frames.items():
            if ch not in charset:
                continue
            tpl = upscale_nn(tpl0, s, s)
            iou, gy, gx = reg.best_iou(tpl, min_ink=30)
            if iou >= 0.70:
                th, tw = tpl.shape
                cands.append((iou, ch, gx, gy, tw, th))
        # greedy accept by descending IoU, allow slight window overlap
        cands.sort(reverse=True)
        acc = []
        occupied = []
        for iou, ch, gx, gy, tw, th in cands:
            ok = True
            for (ox, oy, ow, oh) in occupied:
                ix = max(0, min(gx + tw, ox + ow) - max(gx, ox))
                iy = max(0, min(gy + th, oy + oh) - max(gy, oy))
                if ix * iy > 0.25 * min(tw * th, ow * oh):
                    ok = False
                    break
            if ok:
                acc.append((gx, gy, ch, iou, tw, th))
                occupied.append((gx, gy, tw, th))
        acc.sort()
        # exact boolean re-verification
        good = []
        for gx, gy, ch, iou, tw, th in acc:
            tpl = upscale_nn(frames[ch], s, s)
            ei = exact_iou(band, tpl, gy, gx)
            good.append((gx, gy, ch, iou, ei))
        text = ''.join(g[2] for g in good)
        eious = [round(g[4], 2) for g in good]
        n_ok = sum(1 for g in good if g[4] >= 0.70)
        print(f"\n{spr} scale={s}: accepted={len(good)} exact_ok={n_ok}")
        print(f"  TEXT: {text}")
        print(f"  exact IoU: {eious}")
        if good:
            print(f"  positions: {[(g[0]+x0, g[1]+y0) for g in good]}")


if __name__ == '__main__':
    main()
