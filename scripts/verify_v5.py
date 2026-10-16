import sys, os, time, ctypes, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gameio import capture, find_window, key, click, phys
import numpy as np
from view import view

user32 = ctypes.windll.user32
GAME = r"D:\Steam\steamapps\common\Dead Estate\Dead Estate.exe"
subprocess.Popen([GAME], cwd=os.path.dirname(GAME))
hwnd = None
for _ in range(60):
    time.sleep(0.5)
    hwnd = find_window()
    if hwnd and not user32.IsIconic(hwnd):
        break
assert hwnd, 'no window'
print('window up', hwnd)
for _ in range(30):
    user32.ShowWindow(hwnd, 9); user32.SetForegroundWindow(hwnd); user32.SetFocus(hwnd)
    time.sleep(0.1)
    if user32.GetForegroundWindow() == hwnd and not user32.IsIconic(hwnd):
        break
else:
    raise RuntimeError('no foreground')
time.sleep(1.0)

def cap(name, tries=10):
    for i in range(tries):
        try:
            lg = capture(name)
            if lg is not None and lg.size:
                return lg
        except IndexError:
            pass
        time.sleep(0.2)
    raise RuntimeError('capture failed')

# title -> menu
key(0x20); time.sleep(2.0)
m = cap('w_menu.png'); np.save('../shots/w_menu.npy', m)
# menu -> ? (confirm)
key(0x20); time.sleep(2.0)
s1 = cap('w_step1.png'); np.save('../shots/w_step1.npy', s1)
print('done')
