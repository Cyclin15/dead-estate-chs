"""Decode on-screen text from a PHYSICAL-resolution screenshot (2560x1600) of
the 480x270 game by inverting the nearest-integer-logical upscale via center
sampling, then template-matching glyphs at scale 1 against the rebuilt font
glyphs (fontfinal2) and the sprite-font CJK frames (spritefonts2).

Usage: python match_phys.py shot_phys.png
"""
import sys, csv, os, glob
import numpy as np
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LW, LH = 480, 270

def phys_to_logical(img):
    a = np.array(img.convert('RGB')).astype(int)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    bright = (r > 160) & (g > 160)  # white or yellow text
    H, W = bright.shape
    out = np.zeros((LH, LW), bool)
    for ly in range(LH):
        py = int((ly + 0.5) * H / LH)
        for lx in range(LW):
            px = int((lx + 0.5) * W / LW)
            out[ly, lx] = bright[py, px]
    return out

def load_font_final(name):
    d = os.path.join(BASE, 'fontfinal2', name)
    sheet = Image.open(os.path.join(d, name + '_0.png')).convert('RGBA')
    alpha = np.array(sheet)[:, :, 3] > 40
    glyphs = {}
    with open(os.path.join(d, 'glyphs_%s.csv' % name), encoding='utf-8') as f:
        rows = list(csv.reader(f, delimiter=';'))
    for r in rows[1:]:
        ch = chr(int(r[0])); x, y, w, h = map(int, r[1:5])
        if w and h:
            glyphs[ch] = alpha[y:y+h, x:x+w]
    return glyphs

def load_sprite_frames(spr):
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
            if w and h:
                frames[chr(cc)] = alpha[y:y+h, x:x+w]
    return frames

def match_line(line, glyphs):
    """Greedy left-to-right; returns (text, confs).
    Prunes candidates with a first-ink-column bitmask subset test."""
    lh, lw = line.shape
    res, conf = [], []
    # precompute per-column ink bitmasks
    colmask = []
    for x in range(lw):
        m = 0
        for y in range(lh):
            if line[y, x]:
                m |= 1 << y
        colmask.append(m)
    # precompute template metadata
    meta = []  # (ch, tpl, th, tw, lead, leadmask)
    for ch, tpl in glyphs.items():
        th, tw = tpl.shape
        cols = np.where(tpl.any(axis=0))[0]
        if not len(cols):
            continue
        lead = int(cols[0])
        m = 0
        for y in range(th):
            if tpl[y, lead]:
                m |= 1 << y
        meta.append((ch, tpl, th, tw, lead, m))
    x = 0
    while x < lw:
        if not colmask[x]:
            x += 1; continue
        smask = colmask[x]
        best = None
        for ch, tpl, th, tw, lead, leadmask in meta:
            if leadmask & ~smask:
                continue  # template ink where screen has none -> impossible
            tx = x - lead
            if tx < 0:
                continue
            x_end = min(lw, tx + tw)
            w = x_end - tx
            if w < max(2, tw - 2):
                continue
            sub = line[:, tx:x_end]
            tsub = tpl[:, :w]
            for vy in range(0, max(1, lh - th + 1)):
                a = sub[vy:vy+th]
                if a.shape != tsub.shape:
                    continue
                inter = (a & tsub).sum()
                union = (a | tsub).sum()
                if union == 0:
                    continue
                iou = inter / union
                if best is None or iou > best[0]:
                    best = (iou, ch, tx + tw)
        if best and best[0] > 0.55:
            res.append(best[1]); conf.append(round(best[0], 2))
            x = best[2]
        else:
            res.append('?'); conf.append(0)
            x += 1
    return ''.join(res), conf

def segment_lines(mask, min_gap=3, min_ink=2):
    """Split a bool bitmap into (y0,y1) text lines by row gaps."""
    rows = np.where(mask.any(axis=1) & (mask.sum(axis=1) >= min_ink))[0]
    if not len(rows):
        return []
    breaks = np.nonzero(np.diff(rows) > min_gap)[0]
    return [(g[0], g[-1] + 1) for g in np.split(rows, breaks + 1)]

def main():
    shot = sys.argv[1]
    img = Image.open(os.path.join(BASE, 'shots', shot))
    log = phys_to_logical(img)
    np.save(os.path.join(BASE, 'shots', 'logical_%s.npy' % shot), log)
    # save a visual too
    Image.fromarray((~log * 255).astype('uint8')).save(
        os.path.join(BASE, 'shots', 'logical_%s.png' % shot))

    pools = {
        'typewriter': load_sprite_frames('sprAnyaTypewriterFont'),
        'fancy': load_sprite_frames('sprAnyaFancyFont'),
        'review': load_sprite_frames('sprAnyaReviewFont'),
    }
    for name in ('fntGameFont', 'fntGameFontBold', 'fntGameFontBigger',
                 'fntGameFontBiggerBold', 'fntSmall', 'fntGameFontBiggest'):
        try:
            pools[name] = load_font_final(name)
        except Exception as e:
            print('skip', name, e)

    lines = segment_lines(log)
    print('logical lines:', lines)
    for (y0, y1) in lines:
        band = log[y0:y1, :]
        cols = np.nonzero(band.any(axis=0))[0]
        print(f'--- line y{y0}-{y1} (h={y1-y0}) x{cols[0]}-{cols[-1]}')
        for pname, glyphs in pools.items():
            text, conf = match_line(band, glyphs)
            good = sum(1 for c in conf if c > 0.8)
            if good >= max(1, int(len(conf) * 0.4)):
                print(f'  [{pname}] {good}/{len(conf)} good: {text}')
                print(f'    conf: {conf}')

if __name__ == '__main__':
    main()
