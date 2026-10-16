"""Timed Anya-entry probe: launch, boot->SPACE, menu, click Anya, then sample
the screen every second for 30s (means + change flags), then CPU sample.
Usage: python timed_anya.py tag
"""
import sys, os, time, ctypes, subprocess
import numpy as np
src = open(r'D:/Steam/steamapps/common/Dead Estate/_loc_work/scripts/nav_anya.py').read()
exec(src.split("# --- main ---")[0])
OUT = r'D:/Steam/steamapps/common/Dead Estate/_loc_work/shots'
tag = sys.argv[1]

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
print('boot mean', round(boot.mean(), 1)); sys.stdout.flush()

key(0x20); time.sleep(3)
menu = capture(f'{tag}_menu.png')
print('menu mean', round(menu.mean(), 1)); sys.stdout.flush()

focus(hwnd)
px, py = int(60 * 2560 / 480), int(80 + 164 * 1440 / 270)
click(px, py)
print('clicked anya', px, py); sys.stdout.flush()

t0 = time.time()
prev = None
for i in range(30):
    lg = capture(f'{tag}_t{i:02d}.png')
    m = lg.mean()
    ch = '' if prev is None else (' CHANGE' if abs(m - prev) > 0.05 else ' same')
    print(f't+{time.time()-t0:5.1f}s mean={m:7.2f}{ch}')
    prev = m
    sys.stdout.flush()
    time.sleep(0.3)

out = subprocess.run(['powershell', '-Command',
  "$p = Get-Process 'Dead Estate'; $c1 = $p.TotalProcessorTime.TotalSeconds; Start-Sleep 2; $p.Refresh(); Write-Output ('cpu2s=' + [math]::Round($p.TotalProcessorTime.TotalSeconds-$c1,2) + ' responding=' + $p.Responding)"],
  capture_output=True, text=True)
print(out.stdout.strip())
