"""Clean control run: boot -> SPACE -> main menu -> click Anya button -> observe.
Prints compact summaries; full ASCII views saved to /tmp.
"""
import sys, os, time, ctypes, subprocess
import numpy as np
src = open(r'D:/Steam/steamapps/common/Dead Estate/_loc_work/scripts/nav_anya.py').read()
exec(src.split("# --- main ---")[0])
OUT = r'D:/Steam/steamapps/common/Dead Estate/_loc_work/shots'
tag = sys.argv[1] if len(sys.argv) > 1 else 'ctl'

def save_view(lg, path, y0=0, y1=270, x0=0, x1=480, step=2):
    rows = []
    for y in range(y0, y1, step):
        row = ''
        for x in range(x0, x1, 2):
            v = lg[y:y+step, x:x+2].max()
            row += '#' if v > 60 else ('.' if v > 25 else ' ')
        if row.strip():
            rows.append(f'{y:3d} {row}')
    open(path, 'w').write('\n'.join(rows) + ('\n(all dark)\n' if not rows else '\n'))

# launch fresh
subprocess.run(['taskkill', '/IM', 'Dead Estate.exe', '/F'], capture_output=True)
time.sleep(2)
subprocess.Popen([os.path.join(BASE, '..', 'Dead Estate.exe')], cwd=os.path.join(BASE, '..'))
hwnd = None
for _ in range(60):
    time.sleep(1)
    hwnd = find_window()
    if hwnd: break
print('hwnd', hwnd); sys.stdout.flush()
time.sleep(7)
focus(hwnd); time.sleep(1)
boot = capture(f'{tag}_boot.png')
print('boot mean', boot.mean()); sys.stdout.flush()

key(0x20); time.sleep(3)
menu = capture(f'{tag}_menu.png')
print('menu mean', menu.mean())
save_view(menu, os.path.join(os.environ['TEMP'], f'{tag}_menu.txt'), 95, 230, 0, 260)
sys.stdout.flush()

# click Anya button: band y156-172 (documented), left column -> center ~ (60,164)
px, py = int(60 * 2560 / 480), int(80 + 164 * 1440 / 270)
print('clicking anya at', px, py)
focus(hwnd)
click(px, py)
time.sleep(8)
a = capture(f'{tag}_anya_a.png')
print('anya t+8 mean', a.mean())
time.sleep(3)
b = capture(f'{tag}_anya_b.png')
print('anya t+11 mean', b.mean(), 'identical:', np.array_equal(a, b))
save_view(a, os.path.join(os.environ['TEMP'], f'{tag}_anya.txt'))
sys.stdout.flush()

# responsiveness probe
key(0x1B); time.sleep(1.5)
c = capture(f'{tag}_anya_c.png')
print('after ESC mean', c.mean(), 'changed:', not np.array_equal(b, c))
out = subprocess.run(['powershell', '-Command',
  "$p = Get-Process 'Dead Estate'; $c1 = $p.TotalProcessorTime.TotalSeconds; Start-Sleep 2; $p.Refresh(); Write-Output ('cpu2s=' + [math]::Round($p.TotalProcessorTime.TotalSeconds-$c1,2))"],
  capture_output=True, text=True)
print(out.stdout.strip())
