"""Reconstruct the logical 480x270 bitmap from a DPI-downscaled capture
(1463x914) of the 2560x1600 physical fullscreen game window.

Capture pixel (x,y) samples physical (floor(x*2560/1463), floor(y*1600/914)).
Logical pixel (lx,ly) covers physical [lx*2560/480,(lx+1)*2560/480) x
[ly*1600/270,(ly+1)*1600/270). Each capture pixel votes for the logical pixel
containing its sampled physical pixel; majority vote decides. Untouched
logical pixels get nearest-neighbor fill.
"""
import sys, os
import numpy as np
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LW, LH = 480, 270

def reconstruct(img, mode='bright', color=None, tol=60):
    """mode: 'bright' (>160 R&G) or 'color' (match RGB within tol)."""
    a = np.array(img.convert('RGB')).astype(int)
    Hc, Wc = a.shape[:2]
    PH, PW = 1600, 2560
    if color is not None:
        cr, cg, cb = color
        mask = (np.abs(a[:,:,0]-cr)<tol) & (np.abs(a[:,:,1]-cg)<tol) & (np.abs(a[:,:,2]-cb)<tol)
    else:
        mask = (a[:,:,0] > 160) & (a[:,:,1] > 160)
    votes = np.zeros((LH, LW), int)
    hit = np.zeros((LH, LW), int)
    ys = np.arange(Hc)
    xs = np.arange(Wc)
    py = np.minimum((ys * PH // Hc), PH-1)
    px = np.minimum((xs * PW // Wc), PW-1)
    ly = np.minimum(py * LH // PH, LH-1)
    lx = np.minimum(px * LW // PW, LW-1)
    votes = np.zeros((LH, LW), int)
    hit = np.zeros((LH, LW), int)
    L = ly[:, None]*LW + lx[None, :]
    np.add.at(votes.ravel(), L.ravel(), 1)
    np.add.at(hit.ravel(), L.ravel(), mask.ravel().astype(int))
    out = hit*2 >= votes
    # nearest fill for zero-vote pixels
    from collections import deque
    zero = votes == 0
    if zero.any():
        q = deque()
        seen = zero.copy()
        for y in range(LH):
            for x in range(LW):
                if zero[y, x]:
                    q.append((y, x))
        while q:
            y, x = q.popleft()
            filled = False
            for dy, dx in ((0,1),(0,-1),(1,0),(-1,0)):
                ny, nx = y+dy, x+dx
                if 0 <= ny < LH and 0 <= nx < LW and not zero[ny, nx]:
                    out[y, x] = out[ny, nx]
                    zero[y, x] = False
                    filled = True
                    break
            if not filled:
                q.append((y, x))
    return out

if __name__ == '__main__':
    shot = sys.argv[1]
    img = Image.open(os.path.join(BASE, 'shots', shot))
    # yellow text (255,255,45)
    out = reconstruct(img, color=(255, 255, 45), tol=70)
    np.save(os.path.join(BASE, 'shots', 'recon_yellow_%s.npy' % shot), out)
    Image.fromarray((~out*255).astype('uint8')).save(
        os.path.join(BASE, 'shots', 'recon_yellow_%s.png' % shot))
    ys, xs = np.nonzero(out)
    if len(xs):
        print("yellow logical bbox x", xs.min(), xs.max(), "y", ys.min(), ys.max(), "count", len(xs))
        # ascii art
        for y in range(ys.min(), ys.max()+1):
            print(''.join('#' if out[y, x] else '.' for x in range(xs.min(), xs.max()+1)))
    else:
        print("no yellow")
