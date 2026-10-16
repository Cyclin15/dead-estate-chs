"""Launch Dead Estate, wait for a 'Code Error' dialog, dump its text via WM_GETTEXT
on child controls, and screenshot it. Usage: python read_code_error.py"""
import ctypes, ctypes.wintypes as wt, os, subprocess, sys, time, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

user32 = ctypes.windll.user32
GAMEDIR = r"D:\Steam\steamapps\common\Dead Estate"
OUT = os.path.join(GAMEDIR, "_loc_work", "shots")

EnumProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

def win_text(h):
    ln = user32.GetWindowTextLengthW(h)
    b = ctypes.create_unicode_buffer(ln + 1)
    user32.GetWindowTextW(h, b, ln + 1)
    return b.value

def find(pred, timeout=60):
    t0 = time.time()
    while time.time() - t0 < timeout:
        res = []
        def cb(h, _):
            if user32.IsWindowVisible(h):
                t = win_text(h)
                if t and pred(t):
                    res.append((h, t))
            return True
        user32.EnumWindows(EnumProc(cb), 0)
        if res:
            return res[0]
        time.sleep(0.5)
    return None

subprocess.Popen([os.path.join(GAMEDIR, "Dead Estate.exe")], cwd=GAMEDIR)
hit = find(lambda t: "Code Error" in t)
if not hit:
    print("no Code Error dialog within 60s — game may be running fine")
    sys.exit(0)
hwnd, title = hit
print("dialog hwnd", hwnd, title)
time.sleep(1.0)  # let the dialog fill in

texts = []
def cb2(h, _):
    cls = ctypes.create_unicode_buffer(64)
    user32.GetClassNameW(h, cls, 64)
    ln = user32.GetWindowTextLengthW(h)
    if ln:
        b = ctypes.create_unicode_buffer(ln + 1)
        user32.SendMessageW(h, 0x000D, ln + 1, b)  # WM_GETTEXT
        texts.append((cls.value, b.value))
    return True
user32.EnumChildWindows(ctypes.c_void_p(hwnd), EnumProc(cb2), 0)
for cls, txt in texts:
    print(f"--- child {cls} ({len(txt)} chars) ---")
    print(txt[:4000])

# screenshot the dialog
rect = wt.RECT()
user32.GetWindowRect(hwnd, ctypes.byref(rect))
w, h = rect.right - rect.left, rect.bottom - rect.top
print("rect", rect.left, rect.top, w, h)
from PIL import Image
gdi = ctypes.windll.gdi32
hdc = user32.GetWindowDC(0)
mdc = gdi.CreateCompatibleDC(hdc)
bmp = gdi.CreateCompatibleBitmap(hdc, w, h)
gdi.SelectObject(mdc, bmp)
gdi.BitBlt(mdc, 0, 0, w, h, hdc, rect.left, rect.top, 0x00CC0020)
class BMI(ctypes.Structure):
    _fields_ = [("biSize", ctypes.c_uint32), ("biWidth", ctypes.c_int32), ("biHeight", ctypes.c_int32),
                ("biPlanes", ctypes.c_uint16), ("biBitCount", ctypes.c_uint16), ("biCompression", ctypes.c_uint32),
                ("biSizeImage", ctypes.c_uint32), ("biXPelsPerMeter", ctypes.c_int32), ("biYPelsPerMeter", ctypes.c_int32),
                ("biClrUsed", ctypes.c_uint32), ("biClrImportant", ctypes.c_uint32)]
bmi = BMI(ctypes.sizeof(BMI), w, -h, 1, 32, 0, 0, 0, 0, 0, 0)
buf = ctypes.create_string_buffer(w * h * 4)
gdi.GetDIBits(mdc, bmp, 0, h, buf, ctypes.byref(bmi), 0)
img = Image.frombytes("RGBA", (w, h), buf.raw)
img.save(os.path.join(OUT, "code_error.png"))
print("saved code_error.png", img.size)
