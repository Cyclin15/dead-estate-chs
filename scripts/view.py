"""Compact ASCII viewer for logical 270x480 npy captures."""
import sys
import numpy as np

def view(g, x0=0, y0=0, x1=480, y1=270, step=3, skip_empty=True):
    out = []
    last_empty = True
    for y in range(y0, y1, step):
        line = ''
        for x in range(x0, x1, step):
            v = g[y:y+step, x:x+step].mean()
            line += ' ' if v < 40 else ('.' if v < 100 else ('+' if v < 180 else '#'))
        if skip_empty and line.strip() == '' and last_empty:
            continue
        last_empty = line.strip() == ''
        out.append(f'{y:3d} {line}')
    return '\n'.join(out)

if __name__ == '__main__':
    g = np.load(sys.argv[1])
    x0, y0, x1, y1, step = 0, 0, 480, 270, 3
    if len(sys.argv) > 2:
        x0, y0, x1, y1 = map(int, sys.argv[2:6])
    if len(sys.argv) > 6:
        step = int(sys.argv[6])
    print(view(g, x0, y0, x1, y1, step))
