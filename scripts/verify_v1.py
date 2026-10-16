"""Launch game -> main menu -> capture. Single process."""
import sys, os, time, subprocess, ctypes
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gameio import capture, find_window

GAME = r"D:\Steam\steamapps\common\Dead Estate\Dead Estate.exe"
p = subprocess.Popen([GAME], cwd=os.path.dirname(GAME))
time.sleep(6)

user32 = ctypes.windll.user32
hwnd = find_window()
assert hwnd, 'no window'
for _ in range(20):
    user32.ShowWindow(hwnd, 9)
    user32.SetForegroundWindow(hwnd)
    user32.SetFocus(hwnd)
    time.sleep(0.15)
    if user32.GetForegroundWindow() == hwnd:
        break
else:
    raise RuntimeError('cannot get foreground')
time.sleep(0.5)

from gameio import key
key(0x20)  # SPACE: title -> menu
time.sleep(2.5)
lg = capture('verify_menu.png')
import numpy as np
np.save('shots/verify_menu.npy', lg)
print('captured menu', lg.shape)
print('pid', p.pid)
