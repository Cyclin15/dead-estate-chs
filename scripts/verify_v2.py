"""Foreground existing game -> SPACE to menu -> capture -> click Play -> capture char select."""
import sys, os, time, ctypes
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gameio import capture, find_window, key
import numpy as np
from view import view

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
print('foreground ok')
time.sleep(0.5)

key(0x20)  # SPACE: title -> main menu
time.sleep(2.5)
lg = capture('verify_menu.png')
np.save('shots/verify_menu.npy', lg)
print('=== MENU left column ===')
print(view(lg, 0, 80, 170, 240, 2))
