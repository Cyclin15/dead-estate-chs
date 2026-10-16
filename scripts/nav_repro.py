"""Reproduce character select screen: title->menu->Play->charsel->hover difficulty.
Single process: window must stay foreground during input+capture.
Usage: python nav_repro.py"""
import sys, os, time, ctypes
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gameio import capture, find_window, focus, key, click, phys
from view import view
import numpy as np

def fg_loop():
    user32 = ctypes.windll.user32
    hwnd = find_window()
    assert hwnd, 'no window'
    for _ in range(20):
        user32.ShowWindow(hwnd, 9)
        user32.SetForegroundWindow(hwnd)
        user32.SetFocus(hwnd)
        time.sleep(0.15)
        if user32.GetForegroundWindow() == hwnd:
            return hwnd
    raise RuntimeError('cannot get foreground')

h = fg_loop()
print('foreground ok', h)
time.sleep(0.5)

key(0x20)  # SPACE: title -> main menu
time.sleep(2.5)
lg = capture('repro_menu.png')
print('=== MENU (left column) ===')
print(view(lg, 0, 90, 160, 230, 2))
np.save('shots/repro_menu.npy', lg)
