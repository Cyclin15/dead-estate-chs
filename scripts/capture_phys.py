"""Capture the game window at PHYSICAL resolution (2560x1600).
Usage: python capture_phys.py name.png [--key KEY]
Sends an optional key to the game window first (e.g. --key esc, --key return,
--key down, --key left, --key x, --key 200) then waits 0.6s and captures.
"""
import sys, os, time, ctypes
import numpy as np
from PIL import Image

user32 = ctypes.windll.user32
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'shots')

WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
KEYS = {'return': 0x0D, 'esc': 0x1B, 'left': 0x25, 'up': 0x26, 'right': 0x27,
        'down': 0x28, 'space': 0x20, 'tab': 0x09, 'shift': 0x10, 'ctrl': 0x11,
        'alt': 0x12, 'backspace': 0x08, 'delete': 0x2E, 'end': 0x23, 'home': 0x24}


def find_window():
    hwnd = None
    res = []

    def cb(h, _):
        if user32.IsWindowVisible(h):
            ln = user32.GetWindowTextLengthW(h)
            if ln:
                buf = ctypes.create_unicode_buffer(ln + 1)
                user32.GetWindowTextW(h, buf, ln + 1)
                res.append((h, buf.value))
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    user32.EnumWindows(WNDENUMPROC(cb), 0)
    for h, t in res:
        if 'Dead Estate' in t or '死亡庄园' in t:
            return h
    return None


def main():
    name = sys.argv[1]
    key = None
    delay = 0.6
    args = sys.argv[2:]
    if '--key' in args:
        key = args[args.index('--key') + 1]
    if '--delay' in args:
        delay = float(args[args.index('--delay') + 1])

    user32.SetProcessDPIAware()
    hwnd = find_window()
    if not hwnd:
        print('window not found')
        sys.exit(1)

    import ctypes.wintypes
    rect = ctypes.wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    l, t, r, b = rect.left, rect.top, rect.right, rect.bottom
    w, h = r - l, b - t

    if key:
        # focus the game with a real mouse click at window center, then send a
        # real keyboard event (PostMessage is unreliable for GameMaker games)
        cx, cy = l + w // 2, t + h // 2
        user32.SetCursorPos(cx, cy)
        time.sleep(0.1)
        user32.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
        user32.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP
        time.sleep(0.2)
        vk = KEYS.get(key)
        if vk is None:
            vk = ord(key.upper())
        user32.keybd_event(vk, 0, 0, 0)
        time.sleep(0.08)
        user32.keybd_event(vk, 0, 2, 0)  # KEYEVENTF_KEYUP
        time.sleep(delay)

    from PIL import ImageGrab
    img = ImageGrab.grab(bbox=(l, t, r, b), all_screens=True)
    path = os.path.join(OUT, name)
    img.save(path)
    print(f'saved {path} {img.size} hwnd={hwnd} rect=({l},{t},{r},{b})')


if __name__ == '__main__':
    main()
