"""Navigate: boot -> ... -> char select -> select character -> hover difficulty.
Captures each step. Single process to keep window foreground."""
import sys, os, time, ctypes, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from gameio import capture, find_window, key, phys
from view import view

user32 = ctypes.windll.user32
subprocess.Popen([r'D:\Steam\steamapps\common\Dead Estate\Dead Estate.exe'],
                 cwd=r'D:\Steam\steamapps\common\Dead Estate')
time.sleep(14)

def fg():
    h = find_window()
    assert h
    for _ in range(20):
        user32.ShowWindow(h, 9); user32.SetForegroundWindow(h); user32.SetFocus(h)
        time.sleep(0.12)
        if user32.GetForegroundWindow() == h:
            return h
    raise RuntimeError('no fg')

def cap(name):
    lg = capture(name + '.png')
    np.save('shots/%s.npy' % name, lg)
    print('==', name, '==')
    print(view(lg, 0, 0, 480, 270, 4)[:1800])
    return lg

h = fg()
cap('cs_s0_boot')
key(0x20); time.sleep(2.5)
cap('cs_s1')
key(0x20); time.sleep(2.5)
cap('cs_s2')
print('DONE steps')
