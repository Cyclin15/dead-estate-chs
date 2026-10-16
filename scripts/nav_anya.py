"""Navigate: launch game -> boot title SPACE -> main menu -> click Anya button.
Captures at each stage. Usage: python nav_anya.py [tag]
"""
import sys, os, time, ctypes, subprocess
import numpy as np
from PIL import Image

user32 = ctypes.windll.user32
gdi = ctypes.windll.gdi32
user32.SetProcessDPIAware()
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'shots')
tag = sys.argv[1] if len(sys.argv) > 1 else 'orig'

# --- input structs (verified sizes) ---
class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ulong), ("wScan", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.c_void_p)]
class KINPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("ki", KEYBDINPUT), ("pad", ctypes.c_byte * 8)]
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong), ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong), ("dwExtraInfo", ctypes.c_void_p)]
class MINPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("mi", MOUSEINPUT)]

def key(vk, hwnd=None):
    for flags in (0, 2):
        i = KINPUT(); i.type = 1; i.ki.wVk = vk; i.ki.dwFlags = flags
        ctypes.windll.user32.SendInput(1, ctypes.byref(i), ctypes.sizeof(i))
        time.sleep(0.05)

def click(px, py):
    ctypes.windll.user32.SetCursorPos(px, py)
    time.sleep(0.15)
    for flags in (2, 4):
        i = MINPUT(); i.type = 0; i.mi.dwFlags = flags
        ctypes.windll.user32.SendInput(1, ctypes.byref(i), ctypes.sizeof(i))
        time.sleep(0.06)

class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

def find_window():
    res = []
    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def cb(h, _):
        if user32.IsWindowVisible(h):
            ln = user32.GetWindowTextLengthW(h)
            if ln:
                buf = ctypes.create_unicode_buffer(ln + 1)
                user32.GetWindowTextW(h, buf, ln + 1)
                res.append((h, buf.value))
        return True
    user32.EnumWindows(cb, 0)
    for h, t in res:
        if 'Dead Estate' in t or '死亡庄园' in t:
            return int(h)
    return None

def focus(hwnd):
    user32.ShowWindow(hwnd, 6); time.sleep(0.4)
    user32.ShowWindow(hwnd, 9); time.sleep(0.6)

def capture(name):
    hwnd = find_window()
    if not hwnd:
        print('NO WINDOW'); return None
    r = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(r))
    w, h = r.right - r.left, r.bottom - r.top
    hdc = user32.GetWindowDC(hwnd)
    mdc = gdi.CreateCompatibleDC(hdc)
    bmp = gdi.CreateCompatibleBitmap(hdc, w, h)
    gdi.SelectObject(mdc, bmp)
    gdi.BitBlt(mdc, 0, 0, w, h, hdc, 0, 0, 0x00CC0020)
    class BMIH(ctypes.Structure):
        _fields_ = [("biSize", ctypes.c_ulong), ("biWidth", ctypes.c_long),
                    ("biHeight", ctypes.c_long), ("biPlanes", ctypes.c_ushort),
                    ("biBitCount", ctypes.c_ushort), ("biCompression", ctypes.c_ulong),
                    ("biSizeImage", ctypes.c_ulong), ("biXPelsPerMeter", ctypes.c_long),
                    ("biYPelsPerMeter", ctypes.c_long), ("biClrUsed", ctypes.c_ulong),
                    ("biClrImportant", ctypes.c_ulong)]
    class BMI(ctypes.Structure):
        _fields_ = [("bmiHeader", BMIH), ("bmiColors", ctypes.c_ulong * 3)]
    bmi = BMI()
    bmi.bmiHeader = BMIH(ctypes.sizeof(BMIH), w, -h, 1, 32, 0, 0, 0, 0, 0, 0)
    buf = ctypes.create_string_buffer(w * h * 4)
    gdi.GetDIBits(mdc, bmp, 0, h, buf, ctypes.byref(bmi), 0)
    arr = np.frombuffer(buf.raw, dtype=np.uint8).reshape(h, w, 4)
    bgr = arr[:, :, :3]
    rgb = bgr[:, :, ::-1].copy()
    img = Image.fromarray(rgb)
    img.save(os.path.join(OUT, name))
    gdi.DeleteObject(bmp); gdi.DeleteDC(mdc); user32.ReleaseDC(hwnd, hdc)
    # logical view
    g = np.array(img.convert('L'), dtype=np.uint8)
    ys = (np.arange(270) * 1440 / 270).astype(int)
    xs = (np.arange(480) * 2560 / 480).astype(int)
    lg = g[80:1520][ys][:, xs]
    np.save(os.path.join(OUT, name.replace('.png', '.npy')), lg)
    return lg

def ascii_view(lg, thresh=60):
    rows = []
    for y in range(0, 270, 3):
        row = ''
        for x in range(0, 480, 2):
            v = lg[y:y+3, x:x+2].max()
            row += '#' if v > thresh else ('.' if v > 25 else ' ')
        rows.append(row)
    return '\n'.join(rows)

# --- main ---
print('launching game...')
subprocess.Popen([os.path.join(BASE, '..', 'Dead Estate.exe')], cwd=os.path.join(BASE, '..'))
hwnd = None
for _ in range(60):
    time.sleep(1)
    hwnd = find_window()
    if hwnd: break
if not hwnd:
    print('game did not start'); sys.exit(1)
print('hwnd', hwnd)
time.sleep(6)  # boot
focus(hwnd)
capture(f'{tag}_boot.png')
print('== boot ==')
print(ascii_view(capture(f'{tag}_boot2.png')))

key(0x20)  # SPACE -> main menu
time.sleep(1.5)
lg = capture(f'{tag}_menu.png')
print('== menu ==')
print(ascii_view(lg))

# click Anya button: main-menu button at logical (55,110) -> phys (55*2560/480, 80+110*1440/270)
px, py = int(55 * 2560 / 480), int(80 + 110 * 1440 / 270)
print('clicking', px, py)
click(px, py)
time.sleep(5)
lg = capture(f'{tag}_anya1.png')
print('== anya t+5s ==')
print(ascii_view(lg))
time.sleep(5)
lg = capture(f'{tag}_anya2.png')
print('== anya t+10s ==')
print(ascii_view(lg))
