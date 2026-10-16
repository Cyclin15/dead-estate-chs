"""Robust: restore->foreground->capture with retry, then navigate."""
import sys, os, time, ctypes
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gameio import capture, find_window, key
import numpy as np
from view import view

user32 = ctypes.windll.user32

def fg():
    hwnd = find_window()
    assert hwnd, 'no window'
    for _ in range(30):
        user32.ShowWindow(hwnd, 9)
        user32.SetForegroundWindow(hwnd)
        user32.SetFocus(hwnd)
        time.sleep(0.1)
        if user32.GetForegroundWindow() == hwnd and not user32.IsIconic(hwnd):
            return hwnd
    raise RuntimeError('cannot get foreground')

def cap(name, tries=10):
    for i in range(tries):
        try:
            lg = capture(name)
            if lg is not None and lg.size:
                return lg
        except IndexError:
            pass
        fg(); time.sleep(0.2)
    raise RuntimeError('capture failed')

fg()
time.sleep(0.3)
lg = cap('verify_menu.png')
np.save('shots/verify_menu.npy', lg)
print('=== MENU left column ===')
print(view(lg, 0, 80, 170, 240, 2))
